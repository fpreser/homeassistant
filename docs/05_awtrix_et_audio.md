# Awtrix et Systeme Audio

## Awtrix Light (afficheur LED)

### Materiel et communication

- **Appareil** : Awtrix Light — matrice LED 8x32
- **Communication** : MQTT, topic base `awtrix_dd33c0/`
- **Topics principaux** :
  - `awtrix_dd33c0/notify` — notification temporaire (texte + icone)
  - `awtrix_dd33c0/custom/<app>` — app persistante
  - `awtrix_dd33c0/switch` — on/off
- **Surveillance** : automation **"Awtrix Availability or Unavailability"** notifie si l'afficheur devient indisponible

### Script d'envoi de notification

**`script.awtrix_notification`** (`script/awtrix_notification.yaml`) :

Parametres :
- `notification_text` : texte a afficher
- `my_icon` : identifiant icone
- `text_case` : casse du texte
- `show_rainbow` : effet arc-en-ciel (bool)
- `hold_notification` : notification persistante (bool)
- `my_duration` : duree d'affichage

### Apps et toggles

Chaque app est controlee par un `input_boolean` et une automation associee. L'automation publie sur le topic MQTT correspondant quand le toggle change ou quand la donnee est mise a jour.

| App | Input Boolean | Automation | Contenu affiche |
|---|---|---|---|
| Heure | `input_boolean.awtrix_toggle_time` | Awtrix Toggle Time App | Heure courante |
| Date | `input_boolean.awtrix_toggle_date` | Awtrix Toggle Date App | Date du jour |
| Batterie | `input_boolean.awtrix_toggle_battery` | Awtrix Toggle Battery | Niveau batterie HA |
| Humidite | `input_boolean.awtrix_toggle_humidity` | Awtrix Toggle Humidity | Humidite interieure |
| Temperature | `input_boolean.awtrix_toggle_temperature` | Awtrix toggle Temperature | Temperature interieure |
| Conso nette | `input_boolean.awtrix_toggle_consommation_nette` | Awtrix Consommation Nette | `sensor.p1_meter_*_active_power` (W) |
| Temp. exterieure | `input_boolean.awtrix_toggle_temperature_exterieure` | Awtrix Temperature Exterieure | Temperature exterieure |
| Tesla (batterie) | `input_boolean.awtrix_toggle_tesla` | Awtrix Tesla | Niveau batterie Tesla % |
| Tesla (charge) | `input_boolean.awtrix_toggle_tesla_charge` | Awtrix Tesla Charging | Amperage + barre progression |
| Lave-vaisselle | `input_boolean.awtrix_toggle_dishwasher` | Awtrix Dishwasher | Etat lave-vaisselle |
| Machine a laver | `input_boolean.awtrix_toggle_machine_a_laver` | Awtrix App Machine a laver | Etat + temps restant |
| Tondeuse Tony | `input_boolean.awtrix_toggle_tony` | Awtrix Tony | Statut tondeuse |
| Mercedes | `input_boolean.awtrix_toggle_mercedes` | Awtrix Mercedes | Niveau carburant |
| Citerne gaz | `input_boolean.awtrix_toggle_tank` | Awtrix Tank | Niveau citerne Antargaz % |
| Trajet Fabien | `input_boolean.awtrix_toggle_trajet_matin_fabien` | Awtrix Trajet Fabien | Temps trajet matin (min) |
| Trajet Gillian | `input_boolean.awtrix_toggle_trajet_matin_gillian` | Awtrix Trajet Gillian | Temps trajet matin (min) |

### Duree d'affichage par app

- **`input_number.awtrix_app_time_display_duration`** : duree en ms par app (configurable via UI)
- Automation **"Awtrix Set App Display Duration"** : applique la valeur a toutes les apps

### Activation automatique des trajets

- Automation **"Activer Awtrix trajets matin"** : active les deux apps trajet le matin en semaine
- Automation **"Desactiver Awtrix trajets matin"** : les desactive apres le depart

---

## Systeme audio (Google Home / Cast)

### Enceintes configurees

| Media player | Zone |
|---|---|
| `media_player.cuisine` | Cuisine |
| `media_player.ampli_salon` | Ampli salon (Onkyo TX-RZ710) |
| `media_player.chambre_emma` | Chambre Emma |
| `media_player.chambre_louis` | Chambre Louis |
| `media_player.salle_de_bain` | Salle de bain |
| `media_player.bureau_fabien` | Bureau Fabien |
| `media_player.chambre_amis` | Chambre amis |
| `media_player.bureau_gillian` | Bureau Gillian |
| `media_player.reveil_chambre_grenier` | Reveil chambre grenier |
| `media_player.sdd` | Salle de douche |

### Groupes d'enceintes (package google_home_resume)

Definis dans `packages/google_home_resume.yaml` :

| Groupe | Enceintes |
|---|---|
| `media_player.maison` | Toutes les enceintes (10) |
| `media_player.rez` | Ampli salon + Cuisine |
| `media_player.premier` | Emma + Louis + SdB + Bureau Fabien + Chambre amis |
| `media_player.deuxieme` | Bureau Gillian + Reveil grenier + SdD |

### Scripts audio

**`script.amp_settings`** : regle le volume d'un media player selon l'heure (0.3 matin/soir, 0.5 apres-midi). Parametre : `media_player`, `volume_level`.

**`script.ready_cast` / `ready_cast_with_set_volume`** : prepare une enceinte Google Home avant lecture (evite le bip de reveil). Sequence : mute → allume → attend idle → demute → dit "Bonjour" (voix YvetteNeural).

**`script.google_home_resume`** (`packages/google_home_resume.yaml`) : script communautaire pour reprendre la lecture Spotify/radio apres une annonce TTS. Gere la pause/reprise proprement.

---

## TTS (Text-to-Speech)

- **Integration** : `tts.cloud_say` (Nabu Casa) — voix par defaut "Lea" (fr-FR)
- **`script.TTS_Speech` (alias `call_tts`)** : evite le bip avant un message TTS. Parametre : `player`, `texte`, `voix`.
  - Mute → allume → attend idle → demute → lecture TTS

**`script.speech_engine_simplified`** : moteur TTS simplifie pour les annonces via google_home_resume.

---

## Spotify (Spotcast)

Integration **spotcast** avec 4 comptes configures dans `configuration.yaml` :

| Compte | Identifiant spotcast |
|---|---|
| Fabien (principal) | `fabien_preser` |
| Gillian | `gillie` |
| Louis | `lou_p` |
| Emma | `emma_preser` |

Utilise par `script.google_home_resume` pour reprendre la lecture apres TTS.

### Stations radio configurees (google_home_resume)

| Station | |
|---|---|
| NPO Radio 2 | |
| Radio Veronica | |
| Willy | |
| KINK | |

---

## Horloges (automations audio)

### GrandFatherClock (`automation/GrandFatherClock.yaml`)

Joue un carillon toutes les 15 minutes sur `media_player.bureau_fabien` entre 09h30 et 21h30 :
- :15 → 1 coup (Toll-1Quarter.mp3)
- :30 → 2 coups (Toll-2Quarter.mp3)
- :45 → 3 coups (Toll-3Quarter.mp3)
- :00 → N coups correspondant a l'heure (ex. 15h → Toll-3.mp3)

Utilise `script.ready_cast_with_set_volume` (volume 40%).

### Cuckoo Clock (`automation/CucKoo_Clock.yaml`)

Joue un coucou sur `media_player.cuisine` a chaque heure et demi-heure entre 09h30 et 21h30 :
- :30 → 1 coucou (cuckoo-clock-01.wav)
- :00 → N coucous correspondant a l'heure (cuckoo-clock-HH.wav)

### Rappel heure matin

Automation **"Rappel heure matin"** : annonce vocale periodique le matin pour rappeler l'heure.

---

## Rapport journalier

**`script.rapport_journalier`** : lit le briefing journalier (`templates/speech/daily_briefing.yaml`) via TTS sur les enceintes. Utilise `script.google_home_voice` avec `use_resume: true`.

---

## Fichiers

| Fichier | Contenu |
|---|---|
| `automation/GrandFatherClock.yaml` | Carillon quart-horaire (bureau Fabien) |
| `automation/CucKoo_Clock.yaml` | Coucou horaire (cuisine) |
| `script/awtrix_notification.yaml` | Envoi notification MQTT vers Awtrix |
| `script/amp_settings.yaml` | Volume adaptatif selon l'heure |
| `script/ready_cast.yaml` | Preparation enceinte avant lecture |
| `script/TTS_Speech.yaml` | TTS sans bip de demarrage |
| `script/speech_engine_simplified.yaml` | Moteur TTS simplifie |
| `script/rapport_journalier.yaml` | Briefing journalier vocal |
| `packages/google_home_resume.yaml` | Groupes enceintes + reprise Spotify apres TTS |
