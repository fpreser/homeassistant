"""
Injecte la vue 'Planification Chauffage' dans le dashboard Lovelace principal.
Usage: python3 config/python_scripts/_inject_evohome_dashboard.py
"""
import json, copy, sys

STORAGE_FILE = "config/.storage/lovelace.lovelace_fabien"
VIEW_PATH = "planification"

ZONES_RDC = [
    ("Hall d'Entrée",   "climate.hall_entree"),
    ("WC Bas",          "climate.wc_bas"),
    ("Salon",           "climate.salon"),
    ("Salle à Manger",  "climate.salle_a_manger"),
    ("Cuisine",         "climate.cuisine"),
]
ZONES_1ER = [
    ("Hall de Nuit",    "climate.hall_nuit"),
    ("Polyvalent",      "climate.polyvalent"),
    ("Ch. Emma",        "climate.ch_emma"),
    ("Ch. Louis",       "climate.ch_louis"),
]
ZONES_TOP = [
    ("Bureau Fabien",   "climate.bureau_fabien"),
    ("Ch. Amis",        "climate.chambre_amis"),
    ("Salle de Bain",   "climate.salle_de_bain"),
]


def zone_card(name, entity):
    sp = f"state_attr('{entity}', 'status')"
    return {
        "type": "vertical-stack",
        "cards": [
            {
                "type": "custom:mushroom-climate-card",
                "entity": entity,
                "name": name,
                "collapsible_controls": False,
                "fill_container": True,
                "hvac_modes": ["heat", "off"],
            },
            {
                "type": "custom:mushroom-template-card",
                "primary": (
                    f"{{% set s = {sp} %}}"
                    "{% if s %}"
                    "{% set mode = s.setpoint_status.setpoint_mode %}"
                    "{% if mode == 'FollowSchedule' %}"
                    "{{ s.setpoints.this_sp_temp }}°C → {{ s.setpoints.next_sp_temp }}°C "
                    "à {{ s.setpoints.next_sp_from | as_datetime | as_local | strftime('%H:%M') }}"
                    "{% elif mode == 'TemporaryOverride' %}"
                    "⚡ Override → {{ s.setpoints.next_sp_from | as_datetime | as_local | strftime('%H:%M') }}"
                    "{% else %}🔒 Override permanent{% endif %}"
                    "{% else %}—{% endif %}"
                ),
                "secondary": (
                    f"{{% set s = {sp} %}}"
                    "{% if s %}"
                    "{% set m = {'FollowSchedule':'📅 Planning',"
                    "'TemporaryOverride':'⚡ Override temp.',"
                    "'PermanentOverride':'🔒 Override perm.'} %}"
                    "{{ m.get(s.setpoint_status.setpoint_mode, s.setpoint_status.setpoint_mode) }}"
                    "{% else %}—{% endif %}"
                ),
                "icon": (
                    f"{{% set s = {sp} %}}"
                    "{% if s and s.setpoint_status.setpoint_mode != 'FollowSchedule' %}"
                    "mdi:calendar-edit{% else %}mdi:calendar-check{% endif %}"
                ),
                "icon_color": (
                    f"{{% set s = {sp} %}}"
                    "{% if s and s.setpoint_status.setpoint_mode != 'FollowSchedule' %}"
                    "orange{% else %}green{% endif %}"
                ),
                "tap_action": {"action": "none"},
            },
            {
                "type": "custom:mushroom-chips-card",
                "chips": [
                    {
                        "type": "action",
                        "icon": "mdi:thermometer-chevron-up",
                        "content": "Boost",
                        "tap_action": {
                            "action": "perform-action",
                            "perform_action": "script.evohome_apply_boost",
                            "data": {"entity_id": entity},
                        },
                    },
                    {
                        "type": "action",
                        "icon": "mdi:calendar-refresh",
                        "content": "Reset",
                        "tap_action": {
                            "action": "perform-action",
                            "perform_action": "script.evohome_reset_zone",
                            "data": {"entity_id": entity},
                        },
                    },
                ],
            },
        ],
    }


def floor_grid(zones):
    return {
        "type": "custom:layout-card",
        "layout_type": "custom:grid-layout",
        "layout": {
            "grid-template-columns": "repeat(auto-fill, minmax(185px, 1fr))",
            "grid-gap": "8px",
        },
        "cards": [zone_card(n, e) for n, e in zones],
    }


def build_view():
    return {
        "type": "custom:vertical-layout",
        "title": "Planification",
        "path": VIEW_PATH,
        "icon": "mdi:calendar-clock",
        "subview": True,
        "badges": [],
        "cards": [
            # ── En-tête système ──────────────────────────────────────
            {
                "type": "horizontal-stack",
                "cards": [
                    {
                        "type": "custom:mushroom-entity-card",
                        "entity": "climate.home",
                        "name": "Mode Système",
                        "icon": "mdi:thermostat-box",
                        "tap_action": {"action": "more-info"},
                    },
                    {
                        "type": "custom:mushroom-entity-card",
                        "entity": "sensor.evohome_schedule_status",
                        "name": "Planification",
                        "tap_action": {"action": "more-info"},
                    },
                    {
                        "type": "custom:mushroom-entity-card",
                        "entity": "sensor.vicare_outside_temperature",
                        "name": "Extérieur",
                        "tap_action": {"action": "more-info"},
                    },
                ],
            },
            # ── Panneau boost ────────────────────────────────────────
            {
                "type": "entities",
                "title": "Contrôle Override",
                "show_header_toggle": False,
                "entities": [
                    {
                        "entity": "input_number.evohome_boost_temp",
                        "name": "Température cible",
                    },
                    {
                        "entity": "input_select.evohome_boost_duration",
                        "name": "Durée",
                    },
                ],
                "footer": {
                    "type": "buttons",
                    "entities": [
                        {
                            "entity": "script.evohome_fetch_schedules",
                            "name": "Sync planifications",
                            "icon": "mdi:sync",
                            "tap_action": {
                                "action": "perform-action",
                                "perform_action": "pyscript.evohome_fetch_schedules",
                            },
                        },
                    ],
                },
            },
            # ── Rez-de-chaussée ──────────────────────────────────────
            {"type": "markdown", "content": "### 🏠 Rez-de-chaussée"},
            floor_grid(ZONES_RDC),
            # ── 1er étage ────────────────────────────────────────────
            {"type": "markdown", "content": "### 🛏️ 1er Étage"},
            floor_grid(ZONES_1ER),
            # ── Bureau & divers ──────────────────────────────────────
            {"type": "markdown", "content": "### 🏢 Bureau & Divers"},
            floor_grid(ZONES_TOP),
        ],
    }


# ── Injection ────────────────────────────────────────────────────────────────
with open(STORAGE_FILE, encoding="utf-8") as f:
    data = json.load(f)

views = data["data"]["config"]["views"]

# Supprimer l'ancienne version si elle existe
views = [v for v in views if v.get("path") != VIEW_PATH]

# Insérer avant la vue "chauffage" (ou en fin si absente)
insert_before = next(
    (i for i, v in enumerate(views) if v.get("path") == "chauffage"),
    len(views),
)
views.insert(insert_before, build_view())
data["data"]["config"]["views"] = views

with open(STORAGE_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)

print(f"✓ Vue '{VIEW_PATH}' injectée en position {insert_before} ({len(views)} vues au total)")
