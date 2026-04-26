# Appareils, Surveillance et Divers

## Electromenager

### Machine a laver (Bosch WAV28G)

- Integration **home_connect_alt**
- **`binary_sensor.machine_a_laver_en_cours`** : true si `sensor.buanderie_machine_a_laver_power` > 5W
- **`sensor.washing_machine_time_to_complete`** : temps restant en secondes (`device_class: duration`) lu depuis l'attribut `bsh.common.option.remainingprogramtime` de l'integration Bosch
- **`sensor.buanderie_machine_a_laver_201_energy`** : energie journaliere (kWh) — dans l'energy dashboard
- Automation **"Awtrix On Off Machine a laver"** : affiche/masque l'app Awtrix quand la machine demarre/s'arrete

### Seche-linge

- **`binary_sensor.sechoir_en_cours`** : true si `sensor.buanderie_seche_linge_power` > 10W
- **`sensor.buanderie_seche_linge_191_energy`** : energie journaliere (kWh) — dans l'energy dashboard

### Lave-vaisselle (Bosch/Siemens)

- Integration **home_connect_alt**
- **`sensor.dishwasher_energy_consumption`** : energie journaliere (kWh) — dans l'energy dashboard
- Automation **"Awtrix Dishwasher"** : affiche l'etat sur Awtrix
- Automation **"Awtrix on off Lave Vaiselle"** : active/desactive l'app selon l'etat

### Frigo buanderie

- **`sensor.buanderie_frigos_buanderie_249_energy`** : energie journaliere (kWh) — dans l'energy dashboard

### Autres appareils cuisine

| Appareil | Sensor energie |
|---|---|
| Machine a cafe | `sensor.cuisine_machine_a_cafe_energy` |
| Bouilloire | `sensor.cuisine_bouilloire_energy` |
| Grille-pain | `sensor.cuisine_grille_pain_energy` |

---

## Tondeuse robot (Tony)

- Integration **Husqvarna Automower**
- **`lawn_mower.tony`** : entite principale (demarrer, arreter, mettre en dock)
- **`camera.tony_map`** : carte de tonte (exclu de HomeKit)
- **`sensor.tony_status`** (`template_sensors/household_applicances.yaml`) : traduction des etats en francais

| Etat HA | Affichage |
|---|---|
| `off` | Eteint |
| `idle` | Au repos |
| `mowing` | Tonte |
| `charging` | En charge |
| `docked` | A la base |
| `returning` | Retourne a la base |
| `paused` | Pause |
| `error` | Necessite une attention |

- Automation **"Awtrix Tony"** : affiche le statut Tony sur l'afficheur LED

---

## Surveillance et securite

### Sonnette

- Automation **"Sonnette appuyee"** : au declenchement de la sonnette connectee
  - Capture une photo (snapshot camera)
  - Diffuse une alerte audio
  - Notifie Fabien et Gillian avec la photo

### UPS (onduleur electrique)

- Automation **"Monitor UPS"** : surveille le niveau de batterie UPS (`sensor.prise_ups_power`)
  - Notifie quand la batterie descend sous un seuil critique
  - Prise UPS : `sensor.prise_ups_power` (W)

### Hall d'entree (detection + luminosite)

- Automation **"Hall entree detection avec luminosite"** : detecte la presence dans le hall et allume la lumiere si la luminosite est insuffisante

### Bouton rouge hall entree

- Automation **"Bouton rouge Hall Entree"** : action programmee sur le bouton physique du hall d'entree

### Bouton cuisine ilot (Fibaro)

- Automation **"Fibaro-Button-Ilot-Cuisine"** : gere les evenements du bouton Fibaro de l'ilot cuisine (webhook HA)

---

## Collecte des dechets (poubelles)

### Script Python (`python_scripts/collecte_poubelles.py`)

Scrape le site de la commune de Messancy (`messancy.be`) pour recuperer les prochaines dates de collecte par type :

| Type | Attribut JSON |
|---|---|
| Dechets organiques | `organiques` |
| Ordures menageres | `ordures` |
| PMC | `pmc` |
| Papier/carton | `papier` |

Utilise Selenium via hub distant (`192.168.1.10:4444`). Sauvegarde dans `/config/poubelles_data.json`.

### Sensor HA (`sensor.prochaines_poubelles`)

Defini dans `configuration.yaml` (command_line) :
- Commande : `python3 /config/python_scripts/collecte_poubelles.py`
- Rafraichissement : toutes les 24h
- **Etat** : prochaine date de collecte (minimum de tous les types)
- **Attributs** : `organiques`, `ordures`, `pmc`, `papier`, `timestamp`

Automation **"Monitor Citerne"** : surveillance du niveau de la citerne Antargaz et notification quand le niveau descend.

---

## Citerne gaz (Antargaz)

### Script Python (`python_scripts/poll_antargazremote.py`)

Scrape `my.antargaz.be` (Selenium Hub `192.168.1.10:4444`, credentials dans `secrets.yaml`) et renvoie un JSON avec :
- `niveau` : pourcentage rempli
- `date_lecture` : date du dernier releve
- `date_derniere_livraison`
- `volume_citerne`, `type_gaz`, `timestamp`, etc.

Variante locale : `poll_antargazlocal.py` (sans Selenium distant).

### Sensors HA

| Sensor | Source | Description |
|---|---|---|
| `sensor.antargaz` | command_line (24h) | Sensor brut avec tous les attributs JSON |
| `sensor.gaz_tank_level` | template | Niveau citerne en % (`device_class: battery`) |
| `sensor.gaz_tank_level_date` | template | Date du dernier releve |
| `sensor.gaz_scrape_timestamp` | template | Horodatage du dernier scraping |

Rafraichissement manuel : automation **"Update Antargaz"** (7h, 14h, 22h).

---

## Photos Synology

### Script Python (`python_scripts/random_synology_photo.py`)

Selectionne une photo aleatoire depuis un NAS Synology pour affichage (ecran, dashboard, etc.).

---

## Eclairage automatique

### Spot garage (`automation/SpotGarage.yaml`)

**"Spot Garage Auto"** : synchronise le spot de garage (`light.spot_garage`) avec la lumiere de passage jardin (`light.jardin_passage`) — s'allume et s'eteint ensemble.

---

## Surveillance reseau

### Redemarrage WiFi

- Automation **"Restart Wifi on Saturday Morning"** : redemarrage preventif du WiFi tous les samedis matin (maintenance).

### Compteurs de decrochage onduleurs

- `counter.decrochache_onduleur_208` : nombre de decrochages onduleur 1 dans la journee
- `counter.decrochage_onduleur_2` : nombre de decrochages onduleur 2 dans la journee
- Reset automatique a minuit
- Incremente par l'automation **"Decrochage des onduleurs"** (trigger : surtension reseau pendant la journee)

---

## Suivi consommation min/max

- **`input_number.min_consommation_nette`** + **`input_datetime.min_consommation_nette_timestamp`** : minimum de `sensor.p1_meter_*_active_power` avec horodatage
- **`input_number.max_consommation_nette`** + **`input_datetime.max_consommation_nette_timestamp`** : maximum avec horodatage
- Gere par l'automation **"Min Max Consommation Nette"**
- Affiche sur Awtrix via `input_boolean.awtrix_toggle_consommation_nette`

---

## Fichiers

| Fichier | Contenu |
|---|---|
| `python_scripts/collecte_poubelles.py` | Scraping dates collecte dechets (Messancy) |
| `python_scripts/poll_antargazremote.py` | Scraping niveau citerne Antargaz (remote Selenium) |
| `python_scripts/poll_antargazlocal.py` | Variante locale sans Selenium Hub |
| `python_scripts/random_synology_photo.py` | Selection photo aleatoire NAS Synology |
| `automation/SpotGarage.yaml` | Spot garage synchro avec passage jardin |
| `template_sensors/household_applicances.yaml` | binary_sensor machine/sechoir, sensor tony_status, washing_machine_time_to_complete |
