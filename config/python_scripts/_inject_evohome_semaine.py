"""
Injecte la vue 'Planning Semaine' dans le dashboard Lovelace principal.
Usage: python3 config/python_scripts/_inject_evohome_semaine.py

Prérequis : pyscript.evohome_fetch_schedules doit avoir tourné au moins une fois
pour créer les sensors sensor.evohome_sched_*.
"""
import json
import re
import unicodedata

STORAGE_FILE = "config/.storage/lovelace.lovelace_fabien"
VIEW_PATH = "planning-semaine"

# Noms exacts des zones Honeywell (correspondant aux friendly_name HA)
ZONES_RDC = [
    ("Hall Entree",    "climate.hall_entree"),
    ("WC Bas",         "climate.wc_bas"),
    ("Salon",          "climate.salon"),
    ("Salle a manger", "climate.salle_a_manger"),
    ("Cuisine",        "climate.cuisine"),
]
ZONES_1ER = [
    ("Hall Nuit",      "climate.hall_nuit"),
    ("Polyvalent",     "climate.polyvalent"),
    ("Ch Emma",        "climate.ch_emma"),
    ("Ch Louis",       "climate.ch_louis"),
]
ZONES_TOP = [
    ("Bureau Fabien",  "climate.bureau_fabien"),
    ("Ch Amis",        "climate.chambre_amis"),
    ("Salle de Bain",  "climate.salle_de_bain"),
]

# Noms d'affichage plus lisibles pour les cartes
DISPLAY_NAMES = {
    "Hall Entree":    "Hall d'Entrée",
    "Salle a manger": "Salle à Manger",
}

# Template Jinja2 pour la carte de planning d'une zone
SCHEDULE_TEMPLATE = """\
{{% set s = state_attr('__SENSOR__', 'schedule') %}}
#### __DISPLAY__
{{% if s %}}
{{% set days = [['Lundi','Lun'],['Mardi','Mar'],['Mercredi','Mer'],['Jeudi','Jeu'],['Vendredi','Ven'],['Samedi','Sam'],['Dimanche','Dim']] %}}
{{% for d in days %}}**{{{{ d[1] }}}}** {{% set slots = s.get(d[0], []) %}}{{% for sl in slots %}}{{{{ sl.time }}}}→{{{{ sl.temp }}}}°{{% if not loop.last %}} · {{% endif %}}{{% endfor %}}
{{% endfor %}}{{% else %}}
_Sync requis_
{{% endif %}}"""


def _zone_slug(name: str) -> str:
    n = unicodedata.normalize("NFKD", name)
    n = "".join(c for c in n if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_")


def schedule_card(zone_name):
    sensor_id = f"sensor.evohome_sched_{_zone_slug(zone_name)}"
    display = DISPLAY_NAMES.get(zone_name, zone_name)
    content = SCHEDULE_TEMPLATE.replace("__SENSOR__", sensor_id).replace("__DISPLAY__", display)
    return {"type": "markdown", "content": content}


def floor_grid(zones):
    return {
        "type": "custom:layout-card",
        "layout_type": "custom:grid-layout",
        "layout": {
            "grid-template-columns": "repeat(auto-fill, minmax(220px, 1fr))",
            "grid-gap": "8px",
        },
        "cards": [schedule_card(name) for name, _ in zones],
    }


def build_view():
    return {
        "type": "custom:vertical-layout",
        "title": "Planning Semaine",
        "path": VIEW_PATH,
        "icon": "mdi:calendar-week",
        "subview": True,
        "badges": [],
        "cards": [
            # En-tête
            {
                "type": "custom:mushroom-entity-card",
                "entity": "sensor.evohome_schedule_status",
                "name": "Dernière synchronisation",
                "tap_action": {"action": "more-info"},
            },
            # RDC
            {"type": "markdown", "content": "### 🏠 Rez-de-chaussée"},
            floor_grid(ZONES_RDC),
            # 1er étage
            {"type": "markdown", "content": "### 🛏️ 1er Étage"},
            floor_grid(ZONES_1ER),
            # Bureau & divers
            {"type": "markdown", "content": "### 🏢 Bureau & Divers"},
            floor_grid(ZONES_TOP),
        ],
    }


# ── Injection ────────────────────────────────────────────────────────────────
with open(STORAGE_FILE, encoding="utf-8") as f:
    data = json.load(f)

views = data["data"]["config"]["views"]
views = [v for v in views if v.get("path") != VIEW_PATH]

insert_before = next(
    (i for i, v in enumerate(views) if v.get("path") == "chauffage"),
    len(views),
)
views.insert(insert_before, build_view())
data["data"]["config"]["views"] = views

with open(STORAGE_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)

print(f"Vue '{VIEW_PATH}' injectee en position {insert_before} ({len(views)} vues)")
