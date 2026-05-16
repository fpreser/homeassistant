"""
Planification Evohome — synchronisation API Honeywell → HA
===========================================================

Récupère les planifications hebdomadaires de chaque zone Evohome
et les stocke dans /config/evohome_schedules.json.

Services exposés :
  pyscript.evohome_fetch_schedules  — synchronisation manuelle ou via dashboard

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

    return len(zones_data)


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


@time_trigger("startup")
async def _startup_fetch():
    """Récupère les planifications 90s après le démarrage HA."""
    await task.sleep(90)
    await evohome_fetch_schedules()


@time_trigger("cron(0 4 * * *)")
async def _daily_fetch():
    """Mise à jour automatique chaque nuit à 4h."""
    await evohome_fetch_schedules()
