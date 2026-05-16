# AV Salon — Unfolded Circle Remote 3

## Materiel

| Appareil | Controle |
|---|---|
| Sony Bravia 8 (Google TV) | Integration native Android TV (UC Remote 3) |
| Onkyo TX-RZ710 | Harmony Hub → HA → scripts |
| VOO Evasion | Harmony Hub → HA → scripts |
| Decodeur TNT Fujionkyo | Harmony Hub → HA → scripts |
| Plex | Integration custom UC (JackJPowell/uc-intg-plex) |

## Infrastructure

- **Harmony Hub** : `remote.salon` (id hub : 6921036) — contient tous les codes IR
- **Unfolded Circle Remote 3** : Web Configurator sur `http://192.168.1.35` (PIN : 9998)
- **Integrations UC configurees** : Android TV (Sony), Home Assistant

## Scripts Harmony (config/script/harmony_av.yaml)

Tous les scripts suivent le meme pattern :

```yaml
remote.send_command → remote.salon
  device: "<nom du device dans Harmony>"
  command: "<commande>"
```

### VOO Evasion (`device: "VOO Enregistreur numerique"`, id: 82218657)

| Script | Alias | Commande Harmony |
|---|---|---|
| `script.voo_power` | VOO - Power | PowerToggle |
| `script.voo_haut/bas/gauche/droite` | VOO - Navigation | DirectionUp/Down/Left/Right |
| `script.voo_ok` | VOO - OK | OK |
| `script.voo_retour` | VOO - Retour | Back |
| `script.voo_quitter` | VOO - Quitter | Exit |
| `script.voo_menu` | VOO - Menu | Menu |
| `script.voo_guide` | VOO - Guide | Guide |
| `script.voo_info` | VOO - Info | Info |
| `script.voo_home` | VOO - Home | Home |
| `script.voo_chaine_suivante` | VOO - Chaine suivante | ChannelUp |
| `script.voo_chaine_precedente` | VOO - Chaine precedente | ChannelDown |
| `script.voo_lecture/pause/stop` | VOO - Transport | Play/Pause/Stop |
| `script.voo_rembobiner` | VOO - Rembobiner | Rewind |
| `script.voo_avance_rapide` | VOO - Avance rapide | FastForward |
| `script.voo_enregistrer` | VOO - Enregistrer | Record |
| `script.voo_saut_arriere/avant` | VOO - Saut | SkipBack/SkipForward |
| `script.voo_rouge` | VOO - Rouge | Red |
| `script.voo_vod` | VOO - VOD | VOD |
| `script.voo_betv` | VOO - BeTV | BeTv |
| `script.voo_tv` | VOO - TV | TV |
| `script.voo_0` … `script.voo_9` | VOO - 0…9 | 0…9 |

### Decodeur TNT Fujionkyo (`device: "Decodeur Fujionkyo"`, id: 51302938)

| Script | Alias | Commande Harmony |
|---|---|---|
| `script.tnt_power` | TNT - Power | PowerToggle |
| `script.tnt_haut/bas/gauche/droite` | TNT - Navigation | DirectionUp/Down/Left/Right |
| `script.tnt_select` | TNT - Select | Select |
| `script.tnt_quitter` | TNT - Quitter | Exit |
| `script.tnt_menu` | TNT - Menu | Menu |
| `script.tnt_guide` | TNT - Guide | Guide |
| `script.tnt_info` | TNT - Info | Info |
| `script.tnt_teletext` | TNT - Teletexte | Teletext |
| `script.tnt_chaine_suivante` | TNT - Chaine suivante | ChannelUp |
| `script.tnt_chaine_precedente` | TNT - Chaine precedente | ChannelDown |
| `script.tnt_chaine_prec` | TNT - Chaine prec (memoire) | ChannelPrev |
| `script.tnt_rouge/vert/bleu/jaune` | TNT - Couleurs | Red/Green/Blue/Yellow |
| `script.tnt_0` … `script.tnt_9` | TNT - 0…9 | 0…9 |

### Onkyo TX-RZ710 (`device: "Recepteur AV Onkyo"`, id: 39530143)

| Script | Alias | Commande Harmony |
|---|---|---|
| `script.onkyo_allumer` | Onkyo - Allumer | PowerOn |
| `script.onkyo_eteindre` | Onkyo - Eteindre | PowerOff |
| `script.onkyo_power` | Onkyo - Power toggle | PowerToggle |
| `script.onkyo_volume_plus/moins` | Onkyo - Volume +/- | VolumeUp/VolumeDown |
| `script.onkyo_mute` | Onkyo - Mute | Mute |
| `script.onkyo_entree_tv` | Onkyo - Entree TV | InputTv |
| `script.onkyo_entree_cbl` | Onkyo - Entree CBL/SAT | InputCbl/Sat |
| `script.onkyo_entree_bd` | Onkyo - Entree BD/DVD | InputBd/Dvd |
| `script.onkyo_entree_game` | Onkyo - Entree Game | InputGame |
| `script.onkyo_entree_net` | Onkyo - Entree Net | InputNet |
| `script.onkyo_entree_bluetooth` | Onkyo - Entree Bluetooth | InputBluetooth |
| `script.onkyo_entree_aux` | Onkyo - Entree AUX | InputAux |
| `script.onkyo_entree_strm` | Onkyo - Entree Streaming Box | InputStrmBox |
| `script.onkyo_mode_cinema` | Onkyo - Mode Cinema/TV | ModeMovie/Tv |
| `script.onkyo_mode_musique` | Onkyo - Mode Musique | ModeMusic |
| `script.onkyo_mode_jeu` | Onkyo - Mode Jeu | ModeGame |
| `script.onkyo_haut/bas/gauche/droite` | Onkyo - Navigation | DirectionUp/Down/Left/Right |
| `script.onkyo_entrer` | Onkyo - Enter | Enter |
| `script.onkyo_retour` | Onkyo - Retour | Return |
| `script.onkyo_lecture/pause` | Onkyo - Transport | Play/Pause |

## Activites Harmony configurees

| ID | Activite |
|---|---|
| -1 | PowerOff |
| 31148298 | Regarder la TNT |
| 53334474 | Regarder Netflix |
| 53334718 | Regarder Smart TV |
| 53336572 | Regarder Voo |

Accessibles via `select.salon_activities` ou les switches d'activite (desactives par defaut dans HA).

## Lancement d'apps Sony Bravia 8 (Android TV)

Via Input Source dans le Web Configurator UC, taper le package :

| App | Package |
|---|---|
| Netflix | `com.netflix.ninja` |
| YouTube | `com.google.android.youtube.tv` |
| Disney+ | `com.disney.disneyplus` |
| Prime Video | `com.amazon.amazonvideo.livingroom` |
| Plex | `com.plexapp.android` |
| Spotify | `com.spotify.tv.android` |
| Apple TV | `com.apple.atve.sony.appletv` |
| Max (HBO) | `com.wbd.stream` |
| Kodi | `market://launch?id=org.xbmc.kodi` |

## Automations AV

### BraviaAVSync (config/automation/BraviaAVSync.yaml)

Synchronisation automatique des appareils AV avec la Sony Bravia (trigger : intégration braviatv, entité `media_player.bravia_8_3`).

| Automation | Trigger | Actions |
|---|---|---|
| `bravia_av_allumage` | Bravia passe de `off` → `on/idle/playing/paused` | Onkyo ON → VOO toggle → TNT toggle |
| `bravia_av_extinction` | Bravia passe de `on/idle/playing/paused` → `off` | VOO toggle → TNT toggle → Onkyo OFF |

**Notes :**
- Délai de 5 s sur le trigger pour éviter les faux positifs
- Onkyo contrôlé via `media_player.turn_on/off` (intégration ISCP native, plus fiable que IR)
- VOO et TNT contrôlés via `script.voo_power` / `script.tnt_power` (toggle IR Harmony) — suppose les appareils dans l'état attendu (éteints au démarrage, allumés à l'extinction)
- Délais entre actions : 3 s après Onkyo, 2 s entre VOO et TNT

## Ressources

- Icones UC : unfolded.tools
- Codes IR communautaires : github.com/mattgruter/unfoldedcircle-ircodes
- Integrations custom UC : installer via Web Configurator → Integrations → Install custom (.tar.gz)
