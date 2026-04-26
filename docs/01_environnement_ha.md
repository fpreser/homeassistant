# Environnement Home Assistant

## Vue d'ensemble

- **Version HA** : 2026.2.3
- **Localisation** : Belgique
- **Langue** : Français
- **Port** : 8123
- **Reseau electrique** : Triphase sans neutre, 40A, ~15 930W max theorique
- **Limite compteur configuree** : 14 000W (`input_number.tesla_grid_limit`)

## Matrice des integrations

### Integrations natives / core

| Integration | Usage | Entites cles |
|---|---|---|
| **Evohome** (Honeywell) | Chauffage central, 12 zones | `climate.hall_entree`, `climate.salon`, `climate.cuisine`, `climate.salle_a_manger`, `climate.hall_nuit`, `climate.polyvalent`, `climate.ch_emma`, `climate.ch_louis`, `climate.bureau_fabien`, `climate.chambre_amis`, `climate.salle_de_bain`, `climate.wc_bas` |
| **HomeKit** | Pont vers Apple Home (lights, switches, climate, covers) — exclude sensors/binary_sensors | -- |
| **Prometheus** | Export metriques (lights, sensors, binary_sensors) — namespace `hass` | -- |
| **Tesla Fleet API** | Voiture Tesla Model Y "F.R.I.D.A.Y" | `switch.f_r_i_d_a_y_charge`, `number.f_r_i_d_a_y_charge_current`, `sensor.f_r_i_d_a_y_charger_current`, `sensor.f_r_i_d_a_y_niveau_de_batterie`, `number.f_r_i_d_a_y_charge_limit`, `device_tracker.f_r_i_d_a_y_location` |
| **SMA (Solar)** | 2 onduleurs photovoltaiques SB 5.0 | `sensor.sb5_0_1av_41_208_grid_power`, `sensor.sb5_0_1av_41_345_grid_power`, `sensor.sb5_0_1av_41_208_voltage_l1`, `sensor.sb5_0_1av_41_345_voltage_l1` |
| **P1 Meter** (HomeWizard) | Compteur electrique reseau bi-directionnel (T1/T2) + tarif actif | `sensor.p1_meter_3c39e7284d28_active_power`, imports/exports T1 (HP) et T2 (HC), `sensor.p1_meter_3c39e7284d28_active_tariff` |
| **ViCare** (Viessmann) | Chaudiere Vitodens (chauffage + eau chaude) | `water_heater.vicare_water`, `climate.vicare_heating`, conso gaz jour (kWh) |
| **Waze** | Temps de trajet (3 segments matin Fabien + direct Gillian) | `sensor.trajet_maison_ecole_emma`, `sensor.trajet_ecole_emma_ecole_louis`, `sensor.trajet_ecole_louis_travail_fabien`, `sensor.trajet_maison_travail_gillian` |
| **TTS Google Translate** | Annonces vocales en francais (voix Lea) | -- |
| **Google Home / Cast** | 10 enceintes (salons, chambres, bureaux, SdB) | `media_player.cuisine`, `media_player.ampli_salon`, `media_player.bureau_fabien`, etc. |
| **Emulated Roku** | Telecommande Harmony Hub | port 8060 |
| **MQTT** | Communication Awtrix Light (afficheur LED) | topic `awtrix_dd33c0/...` |
| **Husqvarna Automower** | Tondeuse robot "Tony" | `lawn_mower.tony`, `camera.tony_map` |
| **Forecast.Solar** | Previsions production solaire | `sensor.energy_production_tomorrow` |
| **Withings** | Sante / suivi personnel | -- |
| **Onkyo TX-RZ710** | Amplificateur AV salon | `media_player.ampli_salon` |
| **Plex** | Serveur media | -- |

### Integrations HACS (custom_components)

| Integration | Usage |
|---|---|
| **HACS** | Gestionnaire d'integrations custom |
| **battery_sim** | Simulation batterie domestique type Tesla Powerwall (entites `tesla_powerwall.*`) |
| **dreo** | Ventilateurs Dreo |
| **grok_conversation** | Agent conversationnel xAI Grok |
| **home_connect_alt** | Electromenager Bosch/Siemens (lave-linge WAV28G, lave-vaisselle) |
| **mbapi2020** | Mercedes-Benz (voiture Mercedes) |
| **miele** | Electromenager Miele |
| **panasonic_cc** | Climatisation Panasonic Comfort Cloud chambre grenier (`climate.chambre`, `sensor.chambre_grenier_climatisation_power`) |
| **remote_homeassistant** | Connexion a une instance HA distante |
| **resmed_myair** | Suivi CPAP ResMed |
| **spotcast** | Diffusion Spotify sur Chromecast/Google Home (4 comptes : Fabien, Gillian, Louis, Emma) |
| **tesla_pubkey** | Serveur cle publique pour Tesla Fleet API |

## Equipements domotiques

### Eclairage (Zigbee/Z-Wave via prises connectees)

Toutes les lumieres sont monitorees en puissance (W). Zones :
- **RDC** : Jardin passage, Terrasse, Terrasse bois, Salon (table, exterieur, prises), Salle a manger (table, exterieur), Cuisine (passage, ilot, evier), Hall d'entree (porte, escalier, principal)
- **Etage** : Hall de nuit (veilleuses, principal), Salle de douche
- **Grenier** : Grenier, Chambre grenier (entree, principal), Escalier palier 2eme

### Prises connectees monitorees

| Prise | Entite |
|---|---|
| VMC Grenier | `sensor.grenier_vmc_power` |
| PC Bureau Fabien | `sensor.bureau_fabien_pc_power` |
| UPS | `sensor.prise_ups_power` |
| TV Salon | `sensor.salon_prise_tv_power` |
| Pompe a eau jardin | `sensor.jardin_pompe_a_eau_power` |
| Seche-linge | `sensor.buanderie_seche_linge_power` |
| Machine a laver | `sensor.buanderie_machine_a_laver_power` |
| Radiateur SdB | `sensor.salle_de_bain_radiateur_power` |
| Radiateur SdD | `sensor.salle_de_douche_radiateur_power` |

### Autres equipements

- **Tony** : Robot tondeuse (`lawn_mower.tony`)
- **Velux** : Ouvrants motorises
- **Sonnette** : Sonnette connectee avec notification
- **Awtrix Light** : Afficheur LED matriciel (apps Tesla, conso nette, temperature, humidite, batterie, poubelles, Mercedes, lave-vaisselle, machine a laver, trajet matin)
- **Harmony Hub** : Telecommande universelle (emulated_roku)
- **Fibaro Button** : Bouton cuisine ilot
- **Chauffe-eau** : Viessmann Vitodens (`water_heater.vicare_water`)

## Membres du foyer

| Membre | Notifications | Details |
|---|---|---|
| **Fabien** | `script.notify_fabien` | iPhone 16 Pro, suivi WiFi BSSID |
| **Gillian** | `script.notify_gillian` | -- |
| **Emma** | `script.notify_emma` | Ecole (trajet Waze) |
| **Louis** | `script.notify_louis` | Ecole (trajet Waze) |

## Chauffage

- **Systeme principal** : Honeywell Evohome, 12 zones avec thermostats individuels
- **Chaudiere** : Viessmann Vitodens (eau chaude sanitaire)
- **Climatisation** : Panasonic Comfort Cloud
- **Radiateurs electriques d'appoint** : Salle de bain + Salle de douche (coupure auto apres 1h/40min)
- **Citerne gaz** : Antargaz, niveau scrape via Python toutes les 24h

## Structure des fichiers de config

```
config/
  configuration.yaml          # Config principale
  automations.yaml            # Automations UI (hors smart charge)
  automation/                 # Automations YAML manuelles
    TeslaSmartCharge.yaml     #   Smart charge solaire (10 automations)
    TeslaNightCharge.yaml     #   Charge nocturne HC via tarif P1 Meter (5 automations)
    AwtrixTeslaCharge.yaml    #   Affichage charge sur Awtrix
    ...
  script/                     # Scripts YAML manuels
  template_sensors/           # Sensors template (format 2025.12+)
    tesla_smart_charge.yaml   #   Calcul surplus solaire / amperage optimal
    tesla_night_charge.yaml   #   Decision charge nocturne / heures creuses
    ...
  python_scripts/             # Scripts Python (Antargaz, poubelles, photos)
  custom_components/          # Integrations HACS
  packages/                   # Package google_home_resume
```
