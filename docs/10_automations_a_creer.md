# Automations à créer

Backlog d'automations identifiées le 2026-05-24 en croisant toutes les entités disponibles avec les automations existantes. Chaque entrée indique les entités clés, la logique attendue et la priorité.

---

## Priorité 🔴 Urgent / Sécurité

### Watchdog Evohome en erreur

**Problème actuel :** `sensor.evohome_schedule_status` = `error` (actif au moment du diagnostic).

| Champ | Valeur |
|---|---|
| Trigger | `sensor.evohome_schedule_status` change vers `error` |
| Action | Notification mobile Fabien |
| Pattern | Identique aux watchdogs `automation.watchdog_integration_vicare`, `automation.watchdog_p1_meter` |

---

### Alerte stockage iPhone Gillian

**Problème actuel :** `sensor.iphone_13_pro_de_gillian_storage` = 5.9% (critique au moment du diagnostic).

| Champ | Valeur |
|---|---|
| Trigger | `sensor.iphone_13_pro_de_gillian_storage` passe sous 10% |
| Action | Notification mobile Fabien et/ou Gillian |
| Condition | Une seule notification par jour max |

---

### Coupure automatique du fer à repasser

**Risque :** `switch.buanderie_fer_a_repasser_262` peut rester allumé si oublié.

| Champ | Valeur |
|---|---|
| Trigger | `sensor.buanderie_fer_a_repasser_power` < 10 W pendant 30 min (fer en veille = oublié) |
| Action | Éteindre `switch.buanderie_fer_a_repasser_262` + notification mobile |
| Condition | `switch.buanderie_fer_a_repasser_262` = on |

---

## Priorité 🟠 Confort quotidien

### Pompe à eau jardin — arrêt si pluie imminente

| Champ | Valeur |
|---|---|
| Trigger | `binary_sensor.pluie_imminente_2h` passe à `on` |
| Action | Éteindre `switch.jardin_pompe_a_eau` + notification |
| Condition | `switch.jardin_pompe_a_eau` = on |
| Note | Pas de reprise automatique — l'utilisateur rallume manuellement |

---

### Notification fin de machine à laver

| Champ | Valeur |
|---|---|
| Trigger | `sensor.bosch_wav28gh0fg_68a40e728c79_bsh_common_status_operationstate` change vers `BSH.Common.EnumType.OperationState.Finished` |
| Alternative trigger | `binary_sensor.machine_a_laver_en_cours` passe à `off` (template basé sur puissance) |
| Action | Notification mobile |
| Condition | Quelqu'un est à la maison (`input_boolean.presence_toggle` = on) |

---

### Notification fin de sèche-linge

| Champ | Valeur |
|---|---|
| Trigger | `binary_sensor.sechoir_en_cours` passe à `off` |
| Action | Notification mobile |
| Condition | Quelqu'un est à la maison |

---

### Notification fin de lave-vaisselle

| Champ | Valeur |
|---|---|
| Trigger | `sensor.dishwasher_program_phase` change vers `not_running` (depuis un état actif) |
| Action | Notification mobile |
| Condition | Quelqu'un est à la maison |
| Note | L'Awtrix gère déjà l'affichage via `automation.awtrix_dishwasher` — cette automation ajoute uniquement la notification téléphone |

---

### Radiateurs salle de bain et salle de douche — extinction automatique

**Problème :** `switch.salle_de_bain_radiateur` et `switch.salle_de_douche_radiateur` sont toujours ON sans schedule visible.

| Champ | Valeur |
|---|---|
| Trigger (nuit) | 22h30 |
| Action nuit | Éteindre les deux switches |
| Trigger (matin) | 6h30 |
| Action matin | Allumer les deux switches |
| Condition absent | Si `input_boolean.presence_toggle` = off → rester éteints |
| Note | À affiner avec les horaires réels d'utilisation |

---

### Machine à café — extinction automatique

| Champ | Valeur |
|---|---|
| Trigger | `sensor.cuisine_machine_a_cafe_power` < 5 W pendant 2h |
| Action | Éteindre `switch.cuisine_machine_a_cafe` |
| Condition | `switch.cuisine_machine_a_cafe` = on |

---

## Priorité 🟡 Confort / Sécurité maison

### Caméras Surveillance Station liées à la présence

**Logique :** La Diskstation Surveillance Station doit être en mode "away" (enregistrement actif) quand la maison est vide.

| Champ | Valeur |
|---|---|
| Trigger | `input_boolean.presence_toggle` change |
| Action si vide | `switch.diskstation_surveillance_station_home_mode` = off (away = caméras ON) |
| Action si occupé | `switch.diskstation_surveillance_station_home_mode` = on (home mode = caméras réduites) |
| Note | Actuellement `home_mode` = off en permanence — aucun lien avec la présence |

---

### Éclairage extérieur au coucher/lever du soleil

Lumières extérieures allumées au coucher du soleil, éteintes à une heure fixe.

| Entité | Zone |
|---|---|
| `light.jardin_passage` | Passage jardin côté porte cuisine |
| `light.terasse` | Terrasse principale |
| `light.salon_exterieur` | Extérieur salon |
| `light.salle_a_manger_exterieur` | Extérieur salle à manger |
| `light.terasse_bois` | Terrasse bois |

| Champ | Valeur |
|---|---|
| Trigger allumage | Coucher du soleil (offset +15 min) |
| Trigger extinction | 23h30 (ou minuit) |
| Condition allumage | `input_boolean.presence_toggle` = on OU sonnette détecte quelqu'un |
| Note | À séparer en 2 automations : sunset ON et heure fixe OFF |

---

### Climatisation chambre — démarrage automatique en été

| Champ | Valeur |
|---|---|
| Entité climate | `climate.chambre` (Panasonic) |
| Trigger | `sensor.chambre_inside_temperature` > 26°C après 20h |
| Action | Passer en mode `cool`, consigne 22°C |
| Condition | Quelqu'un est à la maison, `climate.chambre` = off |
| Arrêt | `sensor.chambre_inside_temperature` < 22°C ou lever du soleil |

---

### Notification Tesla — autonomie faible au départ

| Champ | Valeur |
|---|---|
| Trigger | `person.fabien` quitte la maison |
| Condition | `sensor.f_r_i_d_a_y_niveau_de_batterie` < 30% OU `sensor.f_r_i_d_a_y_autonomie_de_batterie` < 100 km |
| Action | Notification mobile avec autonomie restante et état de charge |

---

### Lave-vaisselle — démarrage recommandé sur surplus solaire

Extension de la logique Tesla Smart Charge : notifier quand lancer le lave-vaisselle est optimal.

| Champ | Valeur |
|---|---|
| Trigger | `sensor.solar_production` > 2000 W ET `sensor.p1_meter_3c39e7284d28_active_power` < -1000 W (export) pendant 15 min |
| Condition | `sensor.dishwasher_status` = off (lave-vaisselle non en cours) |
| Action | Notification "Surplus solaire : bon moment pour lancer le lave-vaisselle" |
| Note | Pas de démarrage automatique (nécessite chargement manuel du lave-vaisselle) |

---

## Ouverture volets le matin (existante mais désactivée)

`automation.ouverture_volets_matin` existe mais est **désactivée** (state: off).

| Champ | Valeur |
|---|---|
| Status | Désactivée intentionnellement ou oubliée ? |
| Pendant ce temps | `automation.fermeture_volets` est active |
| Action recommandée | Vérifier et réactiver si souhaité, ou supprimer |

---

## Résumé

| Priorité | Automation | Entités clés |
|---|---|---|
| 🔴 | Watchdog Evohome | `sensor.evohome_schedule_status` |
| 🔴 | Alerte stockage iPhone Gillian | `sensor.iphone_13_pro_de_gillian_storage` |
| 🔴 | Coupure fer à repasser | `switch.buanderie_fer_a_repasser_262` |
| 🟠 | Pompe à eau + pluie | `switch.jardin_pompe_a_eau`, `binary_sensor.pluie_imminente_2h` |
| 🟠 | Fin machine à laver | `binary_sensor.machine_a_laver_en_cours` |
| 🟠 | Fin sèche-linge | `binary_sensor.sechoir_en_cours` |
| 🟠 | Fin lave-vaisselle | `sensor.dishwasher_program_phase` |
| 🟠 | Radiateurs SdB/SdD schedule | `switch.salle_de_bain_radiateur`, `switch.salle_de_douche_radiateur` |
| 🟠 | Machine à café extinction | `switch.cuisine_machine_a_cafe` |
| 🟡 | Caméras vs présence | `switch.diskstation_surveillance_station_home_mode` |
| 🟡 | Éclairage extérieur sunset | `light.jardin_passage`, `light.terasse`, … |
| 🟡 | Climatisation chambre été | `climate.chambre`, `sensor.chambre_inside_temperature` |
| 🟡 | Tesla autonomie faible départ | `person.fabien`, `sensor.f_r_i_d_a_y_niveau_de_batterie` |
| 🟡 | Lave-vaisselle surplus solaire | `sensor.solar_production`, `sensor.dishwasher_status` |
