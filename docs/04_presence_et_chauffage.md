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

### Pyscript evohome_schedule — synchronisation des planifications

**Fichier** : `pyscript/apps/evohome_schedule/__init__.py`

Ce script recupere les planifications hebdomadaires des 12 zones Evohome depuis l'API Honeywell et les met a disposition dans HA.

#### Pourquoi ce script existe

L'integration HA native `evohome` expose les entites `climate.*` pour controler les zones, mais **ne stocke pas les planifications hebdomadaires** (les plages horaires/temperatures programmees dans le thermostat). Ce script les recupere via `evohomeasync2` et les injecte dans HA pour qu'un dashboard ou une automation puisse les lire.

#### Comment il fonctionne

Il utilise en priorite le **broker de l'integration HA evohome** (`hass.data["evohome"]`) qui est deja authentifie — pas besoin de creer une nouvelle connexion. Il accede directement a `broker.tcs.zones` (liste des 12 objets `evohomeasync2.zone.Zone`) et appelle `get_schedule()` sur chacun.

```
hass.data["evohome"]          → EvoData
  .tcs                        → ControlSystem (evohomeasync2)
    .zones                    → list[Zone] (12 zones)
      [i].get_schedule()      → list[{day_of_week, switchpoints}]  (API 2.x)
```

Le resultat est normalise en `{jour_fr: [{time: HH:MM, temp: float}]}` et sauvegarde dans `/config/evohome_schedules.json`.

#### Donnees produites

**Fichier JSON** : `/config/evohome_schedules.json`
```json
{
  "fetched_at": "2026-05-24T20:07:07",
  "zones_count": 12,
  "zones": {
    "Cuisine": {
      "zone_id": "...",
      "schedule": {
        "Lundi": [{"time": "06:00", "temp": 20.0}, ...],
        ...
      }
    }
  }
}
```

**Sensors HA crees** :

| Sensor | Description |
|---|---|
| `sensor.evohome_schedule_status` | `ok` ou `error` — etat du dernier fetch (attribut `zones_count`, `fetched_at`) |
| `sensor.evohome_sched_cuisine` | Planning semaine zone Cuisine (schedule en attribut) |
| `sensor.evohome_sched_salon` | Planning semaine zone Salon |
| *(un sensor par zone)* | Nommage : `sensor.evohome_sched_<slug_zone>` |

#### Declenchements automatiques

| Moment | Action |
|---|---|
| 90s apres demarrage HA | Fetch initial (attend que le broker soit pret) |
| Chaque nuit a 4h00 | Mise a jour quotidienne |

#### Services exposes

| Service | Utilisation |
|---|---|
| `pyscript.evohome_fetch_schedules` | Synchronisation manuelle ou depuis le dashboard |
| `pyscript.evohome_reset_zone` | Annule l'override d'une zone et retourne au planning (`entity_id` requis) |
| `pyscript.evohome_set_zone_schedule` | Modifie la planification complete d'une zone (`zone_name`, `schedule` requis) |
| `pyscript.evohome_update_heat_demand` | Rafraichit manuellement les sensors de deficit thermique |
| `pyscript.evohome_deficit_history_stats` | Analyse historique des deficits — voir section ci-dessous |

#### Sensors de deficit thermique (analyse chauffage)

Crees le 2026-05-24 pour analyser l'inertie et les besoins de chaleur par zone.

| Sensor | Contenu | Frequence |
|---|---|---|
| `sensor.evohome_deficit_<slug>` | Deficit en °C par zone (consigne − reel, min 0) | 3 min |
| `sensor.evohome_deficit_ranking` | Zone la plus froide + classement temps reel | 3 min |
| `sensor.evohome_deficit_history` | Resultat analyse historique (apres appel service) | manuel |

**`sensor.evohome_deficit_ranking` attributs :**
- `top_zone` : zone avec le plus grand deficit actuel
- `ranking` : ex `"Bureau Fabien:3.2°C, Ch Emma:1.5°C"`
- `zones_in_deficit` : nombre de zones appelant le bruleur

**Tous les sensors ont `state_class: measurement`** → statistiques long-terme HA activees automatiquement.

#### Analyse historique (a faire en automne 2026)

Apres 2 semaines de chauffage, appeler depuis les outils developpeur HA :

```
Service : pyscript.evohome_deficit_history_stats
Donnees : hours: 336
```

Resultat dans `sensor.evohome_deficit_history` :
- `top_duration` : zones classees par **heures passees en deficit** (inertie / zone chroniquement froide)
- `top_intensity` : zones classees par **deficit moyen** (besoin de chaleur le plus fort)

Utilisation : ajuster les heures de demarrage des planifications (ex: avancer de 30 min si la zone met
trop longtemps a atteindre sa consigne) ou identifier une zone mal equilibree hydrauliquement.

**Note technique :** `heat_demand` (signal natif Evohome) non disponible via evohomeasync2 2.x —
deliberement exclu du schema de validation de la lib. Le deficit thermique est le meilleur proxy
sans appel REST direct a l'API Honeywell.

#### Configuration requise (`configuration.yaml`)

```yaml
pyscript:
  allow_all_imports: true
  apps:
    evohome_schedule:
      username: !secret evohome_username
      password: !secret evohome_password
```

#### Compatibilite evohomeasync2 2.x (correction 2026-05-24)

La version 2.x de la lib a introduit trois changements qui cassaient le script :

| Probleme | Cause | Solution appliquee |
|---|---|---|
| `EvohomeClient() unexpected keyword argument 'password'` | API 2.x : `EvohomeClient(token_manager)` uniquement, pas de creation directe username/password | Suppression du fallback client — broker HA toujours utilise |
| `not implemented ast ast_yield` | pyscript ne supporte pas `yield` dans les async generators | `_iter_zones` reecrite en `async def` retournant une `list` |
| `'list' object has no attribute 'get'` | `get_schedule()` retourne une `list` directe (plus un dict avec `dailySchedules`) avec cles snake_case | `_normalise_schedule` adapte aux deux formats + `"".join([...])` pour les generator expressions |

---

## Chaudiere (Viessmann Vitodens)

- Integration **ViCare** dans HA
- **`water_heater.vicare_water`** : chauffe-eau (temperature actuelle, consigne)
- **`sensor.temperature_chauffe_eau`** : template sensor extrayant `current_temperature` depuis `water_heater.vicare_water`
- **`climate.vicare_heating`** : controle de la chaudiere (mode auto/standby, courbe de chauffe slope=1.4 shift=0)
- Consommation gaz integree dans l'energy dashboard (kWh/jour, chauffage + eau chaude separes)

### Sensors Vicare cles

| Sensor | Description | state_class |
|---|---|---|
| `sensor.vicare_outside_temperature` | Temperature exterieure (source chaudiere) | `measurement` |
| `sensor.vicare_supply_temperature` | Temperature depart circuit (~35-40°C optimal condensation) | natif |
| `sensor.vicare_burner_modulation` | Modulation bruleur (%) | `measurement` |
| `sensor.vicare_burner_active` | Bruleur ON/OFF | binary_sensor |
| `sensor.vicare_heating_gas_consumption_today` | Conso gaz chauffage aujourd'hui (m³) | `total_increasing` |
| `sensor.vicare_heating_gas_consumption_this_week` | Conso gaz chauffage cette semaine (m³) | `total_increasing` |
| `sensor.vicare_heating_gas_consumption_this_month` | Conso gaz chauffage ce mois (m³) | `total_increasing` |
| `sensor.vicare_heating_gas_consumption_this_year` | Conso gaz chauffage cette annee (m³) | `total_increasing` |
| `sensor.vicare_hot_water_gas_consumption_today` | Conso gaz ECS aujourd'hui (m³) | `total_increasing` |
| `sensor.vicare_burner_hours` | Heures totales bruleur (14 000h) | `total_increasing` |
| `sensor.vicare_burner_starts` | Demarrages totaux bruleur (118 000) | `total_increasing` |

---

## Statistiques long-terme pour l'analyse

Depuis le 16/05/2026, **tous les sensors de temperature de pieces ont `state_class: measurement`** (`template_sensors/temperature_rooms.yaml`). Cela active les statistiques long-terme HA (agregats horaires indefiniment conserves).

Les sensors Vicare ont `state_class` natif depuis le debut.

### Ce que l'agent MCP peut analyser

- **Correlation meteo/chauffage** : temperature exterieure vs conso gaz hebdomadaire
- **Confort par piece** : temperature reelle vs consigne Evohome dans le temps
- **Rendement chaudiere** : modulation bruleur, demarrages/heure, supply temp vs ext temp
- **Repartition gaz** : chauffage vs ECS (sensors separes Vicare)
- **Tendances saisonnieres** : accumulation automatique des statistiques horaires

Exemples de questions a poser a l'agent :
> "Correle la conso gaz hebdomadaire avec la temperature exterieure ces 3 derniers mois"
> "Quelle piece est chroniquement sous sa consigne ?"
> "La courbe de chauffe (slope=1.4, shift=0) est-elle adaptee ?"

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
| `pyscript/apps/evohome_schedule/__init__.py` | Fetch planifications 12 zones Evohome → JSON + sensors HA (cron 4h, service manuel) |
