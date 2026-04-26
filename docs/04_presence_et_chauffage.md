# Presence, Chauffage et Confort

## Presence et geolocalisation

### Membres du foyer suivis

| Entite | Membre | Methode |
|---|---|---|
| `person.fabien` | Fabien | GPS app HA + WiFi BSSID |
| `person.gillian` | Gillian | GPS app HA |
| `person.louis` | Louis | GPS app HA |
| `person.emma` | Emma | GPS app HA |

### Detection presence globale

- **`input_boolean.presence_toggle`** (note : typo intentionnel dans le nom) : flag global maison vide / occupee. Gere par l'automation "Presence Toggle"
- L'automation **"Presence Toggle"** surveille les 4 `person.*` et bascule le flag selon la presence d'au moins un membre a la maison

### Localisation fine de Fabien (WiFi BSSID)

Le sensor **`sensor.connection_iphone_fabien`** (`template_sensors/household_applicances.yaml`) mappe le BSSID du WiFi de l'iPhone 16 Pro de Fabien vers une zone de la maison :

| BSSID | Zone |
|---|---|
| `ca:9e:43:da:09:6e` | Routeur 6 GHz |
| `94:18:65:3a:22:75` | Routeur 5 GHz |
| `ca:9e:43:d9:c9:39` | Bureau 6 GHz |
| `c8:9e:43:d9:c9:37` | Bureau 5 GHz |
| `36:98:b5:45:db:8c` | Grenier 6 GHz |
| `3a:98:b5:45:db:89` | Grenier 5 GHz |
| `94:18:65:3a:00:xx` | Garage |

### Automations presence

| Automation | Trigger | Action |
|---|---|---|
| **Presence Toggle** | Changement etat `person.*` | Met a jour `input_boolean.presence_toggle` |
| **Chauffage Auto** | `input_boolean.presence_toggle` change | Passe Evohome en mode absent/present |
| **Welcome Home** (`WelcomeHome.yaml`) | N'importe quel `person.*` arrive a la maison | Allume `light.jardin_exterieur_porte` 2 min (apres coucher du soleil uniquement) |
| **Gillian arrive** | `person.gillian` arrive | Notification |

---

## Chauffage central (Evohome)

### Architecture

- **Systeme** : Honeywell Evohome, 12 zones independantes
- **Integration HA** : `evohome` (scan interval 180s, credentials dans `secrets.yaml`)
- **Mode systeme** : `sensor.honeywell_mode_systeme` (lit `climate.home` attribut `system_mode_status.mode`)

### Zones configurees

| Zone | Entite climate | Sensor temperature |
|---|---|---|
| Hall d'entree | `climate.hall_entree` | `sensor.honeywell_1` |
| WC Bas | `climate.wc_bas` | `sensor.honeywell_2` |
| Salon | `climate.salon` | `sensor.honeywell_3` |
| Salle a manger | `climate.salle_a_manger` | `sensor.honeywell_4` |
| Cuisine | `climate.cuisine` | `sensor.honeywell_5` |
| Hall de nuit | `climate.hall_nuit` | `sensor.honeywell_6` |
| Polyvalent | `climate.polyvalent` | `sensor.honeywell_7` |
| Chambre Emma | `climate.ch_emma` | `sensor.honeywell_8` |
| Chambre Louis | `climate.ch_louis` | `sensor.honeywell_9` |
| Bureau Fabien | `climate.bureau_fabien` | `sensor.honeywell_10` |
| Chambre Amis | `climate.chambre_amis` | `sensor.honeywell_11` |
| Salle de bain | `climate.salle_de_bain` | `sensor.honeywell_12` |

Les sensors temperature (`template_sensors/temperature_rooms.yaml`) extraient `current_temperature` des attributs Evohome.

### Automation chauffage

- **"Chauffage Auto"** : bascule le mode Evohome global (present/absent) en fonction de `input_boolean.presence_toggle`
- **"Change statut chauffage"** : permet de changer manuellement le mode systeme Evohome via `input_select.evohome_select`

---

## Chaudiere (Viessmann Vitodens)

- Integration **ViCare** dans HA
- **`water_heater.vicare_water`** : chauffe-eau (temperature actuelle, consigne)
- **`sensor.temperature_chauffe_eau`** : template sensor extrayant `current_temperature` depuis `water_heater.vicare_water`
- **`climate.vicare_heating`** : controle de la chaudiere
- Consommation gaz integree dans l'energy dashboard (kWh/jour, chauffage + eau chaude separes)

---

## Radiateurs electriques d'appoint

Deux radiateurs electriques surveilles en puissance et coupes automatiquement :

| Radiateur | Switch | Sensor puissance | Delai coupure |
|---|---|---|---|
| Salle de bain | `switch.salle_de_bain_radiateur` | `sensor.salle_de_bain_radiateur_power` | 1 heure |
| Salle de douche | `switch.salle_de_douche_radiateur` | `sensor.salle_de_douche_radiateur_power` | 40 minutes |

### Automation PowerRadiateurs (`automation/PowerRadiateurs.yaml`)

**"Controle Radiateurs"** : si un radiateur reste allume plus de 1h (SdB) ou 40min (SdD) au-dessus de 100W → coupe le switch + notification Fabien. Protection contre l'oubli.

---

## Climatisation Panasonic

- Integration **panasonic_cc** (Panasonic Comfort Cloud)
- **`climate.chambre`** : unite de climatisation chambre grenier
- **`sensor.chambre_grenier_climatisation_power`** : puissance consommee instantanee (W) — inclus dans `sensor.power_heating`
- **`sensor.chambre_grenier_climatisation_daily_energy`** : energie journaliere (kWh) — inclus dans l'energy dashboard
- Sensors complementaires : `sensor.chambre_inside_temperature`, `sensor.chambre_outside_temperature`, `sensor.chambre_cooling_power`, `sensor.chambre_heating_power`

### Script sieste chambre grenier (`script/sieste_chambre_grenier.yaml`)

Sequence automatisee pour une sieste :
1. Ferme le volet (`cover.volet_chambre_low_speed`)
2. Ferme le velux chambre (`cover.volet_velux_chambre`)
3. Allume la clim (`climate.chambre`)
4. Attend la duree `input_datetime.ac_timer`
5. Eteint la clim

---

## Trajets matin (Waze)

Calcules dans `template_sensors/trajet_matin.yaml` :

| Sensor | Calcul | Attributs |
|---|---|---|
| `sensor.temps_trajet_matin_fabien` | Maison → Ecole Emma → Ecole Louis → Travail Fabien (3 segments) | duree par segment |
| `sensor.temps_trajet_matin_gillian` | Maison → Travail Gillian (direct) | -- |

Sources Waze : `sensor.trajet_maison_ecole_emma`, `sensor.trajet_ecole_emma_ecole_louis`, `sensor.trajet_ecole_louis_travail_fabien`, `sensor.trajet_maison_travail_gillian`

Rafraichissement : automation **"Update Waze toutes les 5 mins"**

---

## Velux et volets

- Integration **Somfy TaHoma** pour les ouvrants motorises
- Automation **"Aeration Velux"** : ouvre/ferme les velux selon un timer (`input_datetime.velux_aeration_duration`)
- Automation **"Fermeture Volets"** : ferme les volets au coucher du soleil

---

## Fichiers

| Fichier | Contenu |
|---|---|
| `automation/PowerRadiateurs.yaml` | Coupure auto radiateurs SdB (1h) et SdD (40min) |
| `automation/WelcomeHome.yaml` | Lumiere porte entree 2 min a l'arrivee (apres sunset) |
| `script/sieste_chambre_grenier.yaml` | Sequence sieste : volets + clim avec timer |
| `template_sensors/temperature_rooms.yaml` | 12 sensors temperature Evohome + temperature chauffe-eau |
| `template_sensors/trajet_matin.yaml` | Temps trajet matin Fabien (3 segments) et Gillian |
| `template_sensors/household_applicances.yaml` | `sensor.connection_iphone_fabien` (localisation WiFi BSSID) |
