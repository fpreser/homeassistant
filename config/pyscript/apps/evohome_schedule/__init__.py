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


def _normalise_schedule(raw: dict) -> dict:
    """Convertit le schedule Honeywell en {jour_fr: [{time: HH:MM, temp: float}]}."""
    result = {}
    daily = raw.get("dailySchedules") or raw.get("DailySchedules") or []
    for day_entry in daily:
        day_raw = day_entry.get("dayOfWeek") or day_entry.get("DayOfWeek", 0)
        if isinstance(day_raw, int):
            day_fr = _DAYS_NUM_FR.get(day_raw, str(day_raw))
        else:
            day_fr = _DAYS_EN_FR.get(str(day_raw), str(day_raw))

        switchpoints = day_entry.get("switchpoints") or day_entry.get("Switchpoints") or []
        slots = []
        for sp in switchpoints:
            t = sp.get("timeOfDay") or sp.get("TimeOfDay", "00:00:00")
            temp = (
                sp.get("heatSetpoint")
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
    # Priorité : broker HA — réutilise la session authentifiée
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
            log.warning(f"evohome: broker inaccessible ({e}), fallback client")

    # Fallback : nouveau client API
    cfg = pyscript.app_config
    username = cfg.get("username", "")
    password = cfg.get("password", "")
    import evohomeasync2
    client = evohomeasync2.EvohomeClient(username, password)
    await client.login()
    for location in client.locations:
        gateways = getattr(location, "gateways", getattr(location, "_gateways", []))
        for gw in gateways:
            systems = getattr(gw, "systems", getattr(gw, "_systems", []))
            for sys_ in systems:
                for zone in sys_.zones:
                    name = getattr(zone, "name", "") or getattr(zone, "Name", "")
                    if name == zone_name:
                        return zone

    raise ValueError(f"Zone '{zone_name}' introuvable dans Evohome")


async def _do_fetch() -> int:
    """Cœur du fetch — retourne le nombre de zones récupérées."""
    cfg = pyscript.app_config
    username = cfg.get("username", "")
    password = cfg.get("password", "")

    if not username or not password:
        raise ValueError(
            "credentials manquants — vérifier pyscript.apps.evohome_schedule dans configuration.yaml"
        )

    import evohomeasync2

    client = evohomeasync2.EvohomeClient(username, password)
    await client.login()

    zones_data = {}

    for location in client.locations:
        gateways = getattr(location, "gateways", getattr(location, "_gateways", []))
        for gw in gateways:
            systems = getattr(gw, "systems", getattr(gw, "_systems", []))
            for sys_ in systems:
                for zone in sys_.zones:
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
                        zones_data[name] = {
                            "zone_id": zone_id,
                            "name": name,
                            "schedule": parsed,
                        }
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
    n = "".join(c for c in n if not unicodedata.combining(c))
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
        # evohomeasync2 1.x+ : reset_mode() / 0.x : cancel_temp_override()
        reset_fn = getattr(zone, "reset_mode", None) or getattr(zone, "cancel_temp_override", None)
        if not reset_fn:
            raise ValueError(f"Aucune méthode reset sur la zone '{zone_name}'")
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
