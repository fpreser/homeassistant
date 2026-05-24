"""
Planification Evohome — synchronisation API Honeywell → HA
===========================================================

Récupère les planifications hebdomadaires de chaque zone Evohome
et les stocke dans /config/evohome_schedules.json.

Services exposés :
  pyscript.evohome_fetch_schedules  — synchronisation manuelle ou via dashboard
  pyscript.evohome_reset_zone       — annule l'override d'une zone (entity_id requis)

Sensor mis à jour :
  sensor.evohome_schedule_status   — "ok" / "error" + attributs (zones, fetched_at)

Déclenchements automatiques :
  - 90s après le démarrage HA
  - Chaque nuit à 4h00

Config requise dans configuration.yaml :
  pyscript:
    allow_all_imports: true
    apps:
      evohome_schedule:
        username: !secret evohome_username
        password: !secret evohome_password
"""

import json
from datetime import datetime

SCHEDULE_FILE = "/config/evohome_schedules.json"
STATUS_SENSOR = "sensor.evohome_schedule_status"

_DAYS_EN_FR = {
    "Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi",
    "Thursday": "Jeudi", "Friday": "Vendredi",
    "Saturday": "Samedi", "Sunday": "Dimanche",
}
_DAYS_NUM_FR = {
    0: "Lundi", 1: "Mardi", 2: "Mercredi", 3: "Jeudi",
    4: "Vendredi", 5: "Samedi", 6: "Dimanche",
}
_DAYS_FR_NUM = {v: k for k, v in _DAYS_NUM_FR.items()}


def _normalise_schedule(raw) -> dict:
    """Convertit le schedule Honeywell en {jour_fr: [{time: HH:MM, temp: float}]}.

    Supporte les deux formats :
    - evohomeasync2 2.x : list directe, clés snake_case (day_of_week, heat_setpoint, time_of_day)
    - evohomeasync2 0.x/1.x : dict avec dailySchedules, clés camelCase
    """
    result = {}
    # Nouveau format 2.x : liste directe ; ancien format : dict avec dailySchedules
    if isinstance(raw, list):
        daily = raw
    else:
        daily = raw.get("dailySchedules") or raw.get("DailySchedules") or []

    for day_entry in daily:
        day_raw = (
            day_entry.get("day_of_week")
            or day_entry.get("dayOfWeek")
            or day_entry.get("DayOfWeek", 0)
        )
        if isinstance(day_raw, int):
            day_fr = _DAYS_NUM_FR.get(day_raw, str(day_raw))
        else:
            day_fr = _DAYS_EN_FR.get(str(day_raw), str(day_raw))

        switchpoints = day_entry.get("switchpoints") or day_entry.get("Switchpoints") or []
        slots = []
        for sp in switchpoints:
            t = (
                sp.get("time_of_day")
                or sp.get("timeOfDay")
                or sp.get("TimeOfDay", "00:00:00")
            )
            temp = (
                sp.get("heat_setpoint")
                or sp.get("heatSetpoint")
                or sp.get("HeatSetpoint")
                or sp.get("temperature", 0.0)
            )
            slots.append({"time": str(t)[:5], "temp": float(temp)})

        result[day_fr] = sorted(slots, key=lambda s: s["time"])
    return result


async def _get_zone(zone_name: str):
    """Trouve l'objet zone evohomeasync2 par son nom.

    Essaie d'abord le broker HA (session existante), puis crée un nouveau client
    en fallback. Supporte evohomeasync2 0.x (cancel_temp_override) et 1.x+ (reset_mode).
    """
    # Broker HA — réutilise la session authentifiée de l'intégration evohome
    broker = hass.data.get("evohome")
    if broker:
        try:
            tcs = broker.tcs
            zones_iter = tcs.zones.values() if isinstance(tcs.zones, dict) else iter(tcs.zones)
            for zone in zones_iter:
                name = getattr(zone, "name", "") or getattr(zone, "Name", "")
                if name == zone_name:
                    log.info(f"evohome: zone '{name}' trouvée via broker HA")
                    return zone
        except Exception as e:
            raise RuntimeError(f"evohome: broker inaccessible ({e})")

    raise ValueError(f"Zone '{zone_name}' introuvable — broker evohome non disponible")


async def _iter_zones():
    """Retourne la liste des zones via le broker HA (session existante).

    pyscript ne supporte pas yield dans les async generators — on retourne une liste.
    evohomeasync2 2.x requiert un AbstractTokenManager pour créer un nouveau client,
    donc le fallback direct n'est plus possible : on s'appuie exclusivement sur le broker HA.
    """
    broker = hass.data.get("evohome")
    if broker:
        try:
            tcs = broker.tcs
            zones = tcs.zones.values() if isinstance(tcs.zones, dict) else list(tcs.zones)
            return list(zones)
        except Exception as e:
            log.warning(f"evohome_schedule: broker inaccessible ({e})")

    raise RuntimeError(
        "Broker evohome HA non disponible — intégration evohome démarrée ?"
    )


async def _do_fetch() -> int:
    """Cœur du fetch — retourne le nombre de zones récupérées."""
    zones_data = {}

    for zone in await _iter_zones():
        name = getattr(zone, "name", None) or getattr(zone, "Name", str(zone))
        zone_id = str(
            getattr(zone, "id", None)
            or getattr(zone, "zoneId", None)
            or getattr(zone, "zone_id", "?")
        )
        try:
            getter = getattr(zone, "get_schedule", None)
            raw = await getter() if callable(getter) else getattr(zone, "schedule", {})
            parsed = _normalise_schedule(raw)
            zones_data[name] = {"zone_id": zone_id, "name": name, "schedule": parsed}
            log.info(f"evohome_schedule: '{name}' — {len(parsed)} jours")
        except Exception as e:
            log.warning(f"evohome_schedule: zone '{name}' — {e}")

    payload = {
        "fetched_at": datetime.now().isoformat(),
        "zones_count": len(zones_data),
        "zones": zones_data,
    }
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    _create_schedule_sensors(zones_data)
    return len(zones_data)


def _zone_slug(name: str) -> str:
    """Convertit un nom de zone Honeywell en slug HA (ex: 'Salle à manger' → 'salle_a_manger')."""
    import re
    import unicodedata
    n = unicodedata.normalize("NFKD", name)
    n = "".join([c for c in n if not unicodedata.combining(c)])
    return re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_")


def _create_schedule_sensors(zones_data: dict) -> None:
    """Crée un sensor HA par zone avec le planning hebdomadaire en attribut."""
    ts = datetime.now().isoformat()
    for name, zone_data in zones_data.items():
        sensor_id = f"sensor.evohome_sched_{_zone_slug(name)}"
        state.set(
            sensor_id,
            value="ok",
            new_attributes={
                "schedule": zone_data["schedule"],
                "zone_name": name,
                "fetched_at": ts,
                "friendly_name": f"Planning {name}",
                "icon": "mdi:calendar-week",
            },
        )


@service
async def evohome_fetch_schedules():
    """Synchronise les planifications Evohome depuis l'API Honeywell."""
    try:
        n = await _do_fetch()
        state.set(
            STATUS_SENSOR,
            value="ok",
            new_attributes={
                "fetched_at": datetime.now().isoformat(),
                "zones_count": n,
                "friendly_name": "Evohome Planification",
                "icon": "mdi:calendar-check",
            },
        )
        log.info(f"evohome_schedule: {n} zones sauvegardées dans {SCHEDULE_FILE}")
    except Exception as exc:
        log.error(f"evohome_schedule: {exc}")
        state.set(
            STATUS_SENSOR,
            value="error",
            new_attributes={
                "error": str(exc),
                "friendly_name": "Evohome Planification",
                "icon": "mdi:calendar-alert",
            },
        )


@service
async def evohome_reset_zone(entity_id=None):
    """Annule l'override d'une zone Evohome et retourne au planning."""
    if not entity_id:
        raise ValueError("entity_id requis (ex: climate.salon)")

    # Nom de zone depuis l'état HA — gère les décalages entity_id/nom (ex: chambre_amis → Ch Amis)
    attrs = state.getattr(entity_id) or {}
    zone_name = attrs.get("friendly_name") or entity_id.split(".", 1)[-1].replace("_", " ").title()

    try:
        zone = await _get_zone(zone_name)
        # evohomeasync2 2.x : reset() / 1.x : reset_mode() / 0.x : cancel_temp_override()
        reset_fn = (
            getattr(zone, "reset", None)
            or getattr(zone, "reset_mode", None)
            or getattr(zone, "cancel_temp_override", None)
        )
        if not reset_fn:
            raise ValueError(f"Aucune méthode reset sur la zone '{zone_name}' (attrs: {[a for a in dir(zone) if not a.startswith('_')]})")
        await reset_fn()
        log.info(f"evohome: zone '{zone_name}' réinitialisée au planning")
    except Exception as exc:
        log.error(f"evohome_reset_zone: {exc}")
        raise


@time_trigger("startup")
async def _startup_fetch():
    """Récupère les planifications 90s après le démarrage HA."""
    await task.sleep(90)
    await evohome_fetch_schedules()


@time_trigger("cron(0 4 * * *)")
async def _daily_fetch():
    """Mise à jour automatique chaque nuit à 4h."""
    await evohome_fetch_schedules()


def _schedule_to_api(schedule: dict) -> list:
    """Convertit {jour_fr: [{time, temp}]} → format API evohomeasync2 2.x."""
    result = []
    for day_fr, num in _DAYS_FR_NUM.items():
        slots = schedule.get(day_fr, [])
        switchpoints = []
        for sp in sorted(slots, key=lambda s: s["time"]):
            switchpoints.append({
                "time_of_day": sp["time"] + ":00",
                "heat_setpoint": float(sp["temp"]),
            })
        if switchpoints:
            result.append({"day_of_week": num, "switchpoints": switchpoints})
    return result


@service
async def evohome_set_zone_schedule(zone_name=None, schedule=None):
    """Met à jour la planification complète d'une zone Evohome.

    zone_name : nom de la zone tel qu'affiché dans l'app Evohome (ex: 'Ch Amis')
    schedule  : dict {jour_fr: [{time: 'HH:MM', temp: float}]}
    """
    if not zone_name or schedule is None:
        raise ValueError("zone_name et schedule requis")

    zone = await _get_zone(zone_name)
    api_schedule = _schedule_to_api(schedule)

    set_fn = getattr(zone, "set_schedule", None)
    if not set_fn:
        raise ValueError(
            f"Pas de méthode set_schedule sur '{zone_name}' "
            f"(attrs: {[a for a in dir(zone) if not a.startswith('_')]})"
        )

    await set_fn(api_schedule)
    log.info(f"evohome: schedule '{zone_name}' mis à jour ({len(api_schedule)} jours)")
    await evohome_fetch_schedules()


@service
async def evohome_update_heat_demand():
    """Crée/met à jour sensor.evohome_deficit_<zone> : déficit thermique (consigne − réel).

    heat_demand n'est pas exposé par evohomeasync2 2.x — on utilise le déficit thermique
    comme proxy : valeur positive = zone en retard sur sa consigne = demande de chaleur.
    Valeur 0 = zone satisfaite ou système éteint.
    """
    ts = datetime.now().isoformat()
    zones = await _iter_zones()
    n_active = 0

    for zone in zones:
        name = getattr(zone, "name", None) or getattr(zone, "Name", str(zone))
        slug = _zone_slug(name)
        sensor_id = f"sensor.evohome_deficit_{slug}"

        try:
            status_dict = zone.status if isinstance(zone.status, dict) else {}
            t_real = (status_dict.get("temperature_status") or {}).get("temperature")
            t_set = (status_dict.get("setpoint_status") or {}).get("target_heat_temperature")

            if t_real is not None and t_set is not None:
                deficit = round(max(0.0, float(t_set) - float(t_real)), 1)
                calling = deficit > 0.3
                if calling:
                    n_active += 1
                state.set(
                    sensor_id,
                    value=deficit,
                    new_attributes={
                        "unit_of_measurement": "°C",
                        "state_class": "measurement",
                        "zone_name": name,
                        "friendly_name": f"Déficit {name}",
                        "icon": "mdi:thermometer-alert" if calling else "mdi:thermometer-check",
                        "calling_for_heat": calling,
                        "current_temperature": t_real,
                        "target_temperature": t_set,
                        "updated_at": ts,
                    },
                )
            else:
                state.set(sensor_id, value="unavailable",
                          new_attributes={"zone_name": name,
                                          "friendly_name": f"Déficit {name}"})
        except Exception as e:
            log.warning(f"evohome_deficit: zone '{name}' — {e}")

    log.info(f"evohome_deficit: {n_active}/{len(zones)} zones en demande de chaleur")


@time_trigger("period(now, 3min)")
async def _demand_poll():
    """Rafraîchit les déficits thermiques toutes les 3 minutes."""
    await evohome_update_heat_demand()


