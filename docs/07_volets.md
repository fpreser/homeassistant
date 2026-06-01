# Volets et Vélux

## Orientation de la maison

**Adresse :** 45 Rue Jacques, 6782 Habergy, Belgique
**Coordonnées OSM :** 49.6120229°N, 5.7602536°E (bâtiment way 771717487, vérifié 2026-05-23)

La rue Jacques longe la maison côté **ouest** (axe N-NNE, 10.6° depuis le nord). La maison mesure **12.1 m** de façade nord/sud × **9.1 m** de profondeur est/ouest.

```
              NORD
               │
   ┌───────────┼───────────┐
   │           │           │
Façade EST     │      Façade OUEST
(jardin)       │      = Rue Jacques
soleil 6h-10h  │      soleil 14h-20h
   │           │           │
   └───────────┼───────────┘
               │
              SUD  ← façade la plus exposée en été
         soleil 10h-16h, plein midi
         façade 12.1 m (long côté)
```

---

## Entités covers

### Volets — façade SUD (soleil 10h-16h, priorité 1 en été)

| Entité | Emplacement |
|---|---|
| `cover.volet_poly_pelouse` / `_low_speed` | Polyvalent côté jardin |
| `cover.volet_bureau_fabien` / `_low_speed` | Bureau Fabien |
| `cover.volet_bureau_gillian` / `_low_speed` | Bureau Gillian (chambre amis) |
| `cover.volet_cuisine` / `_low_speed` | Cuisine |
| `cover.volet_velux_chambre` | Volet occultant du vélux chambre grenier |

### Volets — façade OUEST (soleil 14h-20h, priorité 2 en été)

| Entité | Emplacement |
|---|---|
| `cover.volet_tv` / `_low_speed` | Salon côté TV |
| `cover.volet_poly_route` / `_low_speed` | Polyvalent côté rue |
| `cover.volet_emma_route` / `_low_speed` | Chambre Emma (fenêtre rue) |

### Volets — façade EST (soleil 6h-10h, impact faible)

| Entité | Emplacement |
|---|---|
| `cover.volet_chambre` / `_low_speed` | Chambre grenier |

### Volets — façade NORD (pas d'exposition directe)

| Entité | Emplacement |
|---|---|
| `cover.volet_salle_de_bain` / `_low_speed` | Salle de bain |
| `cover.volet_salle_a_manger` / `_low_speed` | Salle à manger |
| `cover.volet_louis` / `_low_speed` | Chambre Louis |
| `cover.volet_canape` / `_low_speed` | Salon côté canapé |
| `cover.volet_emma_gauche` / `_low_speed` | Chambre Emma (fenêtre gauche) |

### Vélux (fenêtres de toit)

| Entité | Emplacement | Orientation toiture |
|---|---|---|
| `cover.velux_chambre` | Chambre grenier | **SUD** |
| `cover.velux_escalier` | Escalier | **SUD** |
| `cover.velux_sdd_gauche` | Salle de douche gauche | **NORD** |
| `cover.velux_sdd_droite` | Salle de douche droite | **NORD** |

### Groupe global

| Entité | Rôle |
|---|---|
| `cover.my_shutters` | Groupe global de tous les volets (Overkiz) |
| `scene.ouverture_volets` | Ouvre tous les volets |
| `scene.fermeture_volets` | Ferme tous les volets |

### Helpers position personnalisée (Overkiz)

Chaque volet expose aussi un `number.volet_*_my_position` (position mémorisée) et un `button.volet_*_my_position` (rappel position). Utilisés pour des presets fixes, non utilisés par les automations actuelles.

---

## Capteurs de température intérieure

Utilisés par les automations de gestion thermique :

| Capteur | Pièce |
|---|---|
| `sensor.temp_salon` | Salon |
| `sensor.temp_salle_a_manger` | Salle à manger |
| `sensor.temp_cuisine` | Cuisine |
| `sensor.temp_hall_nuit` | Hall de nuit |
| `sensor.temp_polyvalent` | Polyvalent |
| `sensor.temp_chambre_emma` | Chambre Emma |
| `sensor.temp_chambre_louis` | Chambre Louis |
| `sensor.temp_bureau_fabien` | Bureau Fabien |
| `sensor.temp_chambre_amis` | Chambre d'Amis |
| `sensor.temp_salle_de_bain` | Salle de bain |
| `sensor.temp_hall_entree` | Hall d'entrée |
| `sensor.chambre_inside_temperature` | Chambre grenier |
| `sensor.vicare_outside_temperature` | Extérieur (sonde chaudière Viessmann) |

---

## Automations existantes

### Ouverture Volets Matin (id: 1746094800000)

Fichier : `config/automations.yaml`

Ouvre tous les volets via `scene.ouverture_volets` selon le type de jour, uniquement si le soleil est levé.

| Trigger | Conditions | Action |
|---|---|---|
| ⏰ 7h00 | Lundi–vendredi + soleil levé | Ouvre volets |
| ⏰ 9h00 | Samedi–dimanche + soleil levé | Ouvre volets |
| 🌅 Lever du soleil | (Semaine ET heure >= 7h) OU (week-end ET heure >= 9h) | Ouvre volets |

Le trigger sunrise couvre le cas hivernal : si le soleil se lève à 8h30 un mercredi, le trigger 7h ne passe pas (soleil pas levé), mais le trigger sunrise se déclenche car 8h30 > 7h.

### Fermeture Volets (id: 1730209049725)

Fichier : `config/automations.yaml`

| Trigger | Action |
|---|---|
| Coucher du soleil + 20 min | Active `scene.fermeture_volets` |

### Harmony Home — volets salon (id: 1722360860567)

Fichier : `config/automations.yaml`

Contrôle manuel via télécommande Harmony Hub (Emulated Roku) :

| Bouton | Action |
|---|---|
| `Up` | Ouvre `volet_tv_low_speed` + `volet_canape` |
| `Down` | Ferme `volet_canape` + `volet_tv` |
| `Left` | Toggle `volet_canape_low_speed` + `volet_tv_low_speed` |
| `Right` | Toggle `volet_salle_a_manger_low_speed` |

### Aération Vélux (id: 1681121951553)

Fichier : `config/automations.yaml`

Déclenché par `timer.velux` (durée configurable via `input_datetime.velux_aeration_duration`, défaut 30 min) :

- Timer actif → ouvre 3 vélux + notification "Début aération"
- Timer terminé → ferme 3 vélux + notification "Fin aération"

Vélux contrôlés : `velux_sdd_droite`, `velux_sdd_gauche`, `velux_escalier`.

**`velux_chambre` exclu de ce groupe** — il est géré séparément par la ventilation nocturne avec ses propres conditions (voir section Gestion thermique été).

---

## Scripts

### Sieste chambre grenier

| Script | Fichier | Action |
|---|---|---|
| `script.sieste_chambre_grenier` | `script/sieste_chambre_grenier.yaml` | Ferme `volet_chambre_low_speed` + `volet_velux_chambre`, lance la clim |
| `script.fin_sieste_chambre_grenier` | `script/fin_sieste_chambre_grenier.yaml` | Ouvre `volet_chambre_low_speed` + `volet_velux_chambre`, éteint la clim |

---

## Gestion thermique été

### Contexte

En été, la façade **sud** (12.1 m, plein midi) est la plus critique. La façade **ouest** (rue Jacques) prend le relais en après-midi. Sans occultation diurne, les pièces montent rapidement au-dessus de 25°C (chambre grenier à 26°C mesurée le 2026-05-23 avec 28.5°C extérieur).

### Helpers

| Helper | Entity ID | Plage | Rôle |
|---|---|---|---|
| Maître on/off | `input_boolean.gestion_thermique` | — | Active/désactive toute la gestion thermique |
| Seuil T_ext | `input_number.seuil_chaleur` | 18–35°C, step 1 | T_ext de déclenchement de la protection solaire |
| Seuil T_int froid | `input_number.seuil_froid` | 15–25°C, step 1 | T_int_max minimale : en dessous, les vélux ne s'ouvrent pas / se ferment |

Aucun `initial:` sur ces helpers — HA restaure la dernière valeur réglée après redémarrage.

### Template sensor

**Fichier :** `template_sensors/gestion_thermique.yaml`

| Entité | Rôle |
|---|---|
| `binary_sensor.pluie_imminente_2h` | ON si précipitations > 0.1 mm dans les 2 prochains slots horaires. Rafraîchi toutes les 30 min via `weather.get_forecasts` (Met.no). |

### Automations

**Fichier :** `automation/GestionThermique.yaml`

| Automation | Entity ID | Déclencheur | Action |
|---|---|---|---|
| Fermeture solaire | `automation.gestion_thermique_fermeture_solaire` | T_ext > seuil + checks 9h/13h | Sud → 15% ; Ouest → 15% dès 13h |
| Réouverture diurne | `automation.gestion_thermique_reouverture_volets` | T_ext < seuil − 2°C (hysteresis) | Sud + Ouest → 100% |
| Ouverture vélux nuit | `automation.gestion_thermique_ouverture_velux_nuit` | Nuit + T_ext < T_int_max − 2°C + T_int_max > 20°C + pas de pluie | SDD + escalier ouverts ; chambre si clim off + volet > 90% |
| Fermeture vélux matin | `automation.gestion_thermique_fermeture_velux_matin` | Sunrise + 30 min | Tous les vélux → fermés |
| Surveillance pluie | `automation.gestion_thermique_surveillance_pluie_nocturne` | `pluie_imminente_2h` → on (nuit) | Tous les vélux → fermés + notif |
| Fermeture vélux trop frais | `automation.gestion_thermique_velux_trop_frais` | T_int_max < 20°C (nuit) | Tous les vélux → fermés + notif |

**T_int_max** = max(`temp_hall_nuit`, `temp_chambre_emma`, `temp_chambre_louis`)

**`velux_chambre` (grenier) — conditions supplémentaires :**
- `climate.chambre = off` — ne pas contrecarrer la clim
- `cover.volet_velux_chambre.current_position > 90` — volet partiellement ou totalement fermé = intention de blocage, ne pas ouvrir

**Cohabitation avec les automations existantes :**
- `ouverture_volets_matin` (7h/9h) → rouvre tout à 100% chaque matin → la protection reprend si T_ext > seuil
- `fermeture_volets` (coucher soleil) → ferme tout → prend le relais en fin de soirée
- `aeration_velux` (timer manuel) → contrôle SDD + escalier uniquement (velux_chambre exclu)

**Pourquoi T_ext et non un mapping T_int par pièce ?**
La protection solaire est préventive — fermer avant que la chaleur entre, pas après.
T_ext > seuil est le bon signal. Les capteurs intérieurs servent uniquement à décider
quand purger la chaleur la nuit (T_int_max).

### Ce qui n'est pas géré automatiquement

| Entité | Raison |
|---|---|
| `volet_chambre` (est) | Soleil matin seulement, peu impactant, risque de gêner si chambre occupée |
| `volet_salle_de_bain` (nord) | Pas d'exposition directe en été |
| `volet_salle_a_manger` (nord) | Pas d'exposition directe en été |
| `volet_louis` (nord) | Pas d'exposition directe en été |
| `volet_canape` (nord) | Pas d'exposition directe en été |
| `volet_emma_gauche` (nord) | Pas d'exposition directe en été |
| `cover.my_shutters` | Groupe global réservé aux scènes ouverture/fermeture existantes |
| `timer.velux` / `aeration_velux` | Garde son fonctionnement manuel indépendant |
