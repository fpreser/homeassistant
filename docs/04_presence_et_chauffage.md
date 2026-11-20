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
| **Welcome Home** (`WelcomeHome.yaml`) | N'importe quel `person.*` arrive a la maison | Allume `light.jardin_exterieur_porte` 2 min (apres coucher du soleil uniquement) ; allume aussi `light.garage` pendant 2 min s'il etait eteint a l'arrivee (garage gauche/droite suivent deja via "Éclairage automatique") |
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

> **Note (2026-11-15)** : en pratique les cles de jours des attributs `schedule` des sensors `sensor.evohome_sched_*` sont en **anglais minuscules** (`monday` … `sunday`), pas en francais : `_normalise_schedule` ne traduit que les cles `Monday`… capitalisees, alors que evohome-async 3.x renvoie `monday`… Le service `evohome_set_zone_schedule` accepte les deux formes, donc le contenu d'un sensor peut etre renvoye tel quel.

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
| `pyscript.evohome_set_zone_schedule` | Remplace la planification complete d'une zone (`zone_name`, `schedule` requis) — 7 jours obligatoires, voir ci-dessous |
| `pyscript.evohome_update_heat_demand` | Rafraichit manuellement les sensors de deficit thermique |
| `pyscript.evohome_deficit_history_stats` | Analyse historique des deficits — voir section ci-dessous |

#### Service `pyscript.evohome_set_zone_schedule` (ecriture d'un planning)

```yaml
action: pyscript.evohome_set_zone_schedule
data:
  zone_name: "Salon"          # nom exact de la zone (ex: "Salle à manger", "Hall Entree")
  schedule:
    monday:    [{time: "05:30", temp: 20}, {time: "08:00", temp: 16}]
    tuesday:   [...]
    # ... les 7 jours sont obligatoires
```

- **Jours acceptes** : francais minuscules ou capitalises (accents toleres : `lundi`, `Lundi`, `LUNDI`) ou anglais minuscules (`monday`). Les **7 jours** sont requis, sans doublon.
- **Validation** : 1 a 6 creneaux par jour, heure `HH:MM` par **pas de 10 minutes**, consigne entre 5 et 35 °C, pas deux creneaux a la meme heure. Message d'erreur explicite sinon (ex : `Jours manquants dans le planning (les 7 sont requis) : Jeudi`).
- **Apres le PUT** : Honeywell accepte la requete puis execute une « comm task » vers la passerelle ; le script **attend son succes** (interrogation toutes les 3 s, 90 s max) avant de relire les plannings (`evohome_fetch_schedules`).
- **En cas d'echec** : log d'erreur (`Planning Evohome '<zone>' NON applique : ...`), **notification persistante** `evohome_set_schedule_<zone>` et exception propagee. Il n'y a plus de « success » silencieux.
- **Piege pyscript** : ne pas nommer une variable `task` ni `state` dans un service (masque les objets pyscript `task.sleep` / `state.set`), et ne pas passer `task.wait()` a `asyncio.wait_for` (pyscript attend deja les coroutines natives a l'appel).

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

#### Correction `evohome_set_zone_schedule` (2026-11-15, evohome-async 3.1.0)

Le service repondait « success » mais Honeywell refusait la mise a jour. Trois causes, verifiees dans le code de `evohome-async==3.1.0` (version imposee par HA 2026.11.1) :

| Symptome | Cause | Correctif |
|---|---|---|
| `400 DayOfWeekMissing` avec `lundi` ou `monday` | Le script ne cherchait que les cles `Lundi`… capitalisees : les autres jours etaient ignores, la liste envoyee etait vide | Alias FR/EN normalises (minuscules, sans accents) + exigence des 7 jours |
| `'0' is not a valid DayOfWeek` avec `Lundi` | Le script envoyait `day_of_week: 0` (entier) ; la lib attend l'enum `DayOfWeek` (`"monday"`…, convertie en `"Monday"` pour Honeywell) | Envoi de `"monday"`…`"sunday"` |
| « success » malgre l'echec | (1) `auth.put()` ne fait que logger un payload invalide et l'envoie quand meme ; (2) `set_schedule()` renvoie une `CommTask` jamais attendue ; (3) pyscript avale les exceptions d'un service | Validation stricte avant envoi, attente de la comm task, log + notification + exception |

Sauvegarde de l'ancien script : `pyscript/apps/evohome_schedule/__init__.py.bak_20261115`.

---

## Optimisation des plannings Evohome (novembre 2026)

Mise en oeuvre le 2026-11-15 sur 7 zones (Cuisine, Salon, Salle à manger, Hall Entree, Salle de Bain, Ch Emma, Ch Louis). **Non modifiees** : WC Bas, Hall Nuit, Polyvalent, Bureau Fabien, Ch Amis.

### Nouveaux plannings (heure/consigne °C)

| Zone | Lun, mar, jeu, ven | Mercredi | Sam, dim |
|---|---|---|---|
| Cuisine | 05:30/20, 07:30/18, 17:00/20, 23:00/19 | 05:30/20, 07:30/18, 11:30/20, 14:00/16, 17:00/20, 23:00/18 | 07:00/20, 23:00/18 |
| Salon | 05:30/20, 08:00/16, **19:00**/20, 23:00/19 | 05:30/20, 08:00/16, 12:00/20, 14:00/16, **19:00**/20, 23:00/19 | 07:00/20, 23:00/18 |
| Salle à manger | 00:00/16, 22:30/18 | 00:00/16, 12:00/20, 22:30/18 | 07:00/19, 23:00/18 |
| Hall Entree | lun-ven : 05:30/18, 07:00/16, 17:00/18, **22:00/16** | idem | **08:00/18, 22:00/16** |
| Salle de Bain | lun-ven : 05:30/21, 07:40/17 | idem | 07:00/18, 20:00/17 |
| Ch Emma, Ch Louis | 05:30/19, 07:00/16, 17:00/19, 20:00/18 | 05:30/19, 07:00/16, 12:00/19, 20:00/18 | 07:00/19, 20:00/18 |

La Cuisine etait deja a ce planning avant l'intervention (modifie depuis l'application Honeywell) : l'ecriture n'a rien change.

### D'ou vient l'optimisation : ce que disent les donnees

Ces plannings ont ete **suggeres par Claude via l'interface web claude.ai** (pas de trace ecrite dans le depot), dans la ligne du plan d'analyse de mai 2026 (inertie par piece, zones sous consigne, revision des plannings). Les donnees historiques ci-dessous ont ete utilisees *a posteriori* pour verifier chaque changement ; une 2e analyse (gaz, presence, hydraulique) figure en fin de section.

**Base** : statistiques horaires HA du 25/10 au 14/11/2026 (21 jours, 501 h par zone, chauffage en continu depuis ~le 25/10, gaz chauffage 1,8 a 5,1 par jour, moyenne 3,6). Les plannings en vigueur pendant cette periode sont les **anciens** (dernier export : `evohome_backups/evohome_schedules_20261115_1815.json`).

**Classement des deficits (consigne − reel)**

| Zone | Deficit moyen | % du temps > 0,3 °C | Deficit max | T moyenne | Modifiee |
|---|---|---|---|---|---|
| Salle à manger | 0,37 °C | 33 % | 3,8 | 18,9 | oui |
| Hall Entree | 0,10 | 15 % | 1,4 | 18,7 | oui |
| Cuisine | 0,07 | 9 % | 1,1 | 19,6 | oui |
| Salle de Bain | 0,06 | 5 % | 2,4 | 19,5 | oui |
| Salon / Ch Emma / Ch Louis | 0,01 | 1-2 % | 0,5-1,5 | 20,1-20,6 | oui |
| WC Bas, Hall Nuit, Polyvalent, Bureau Fabien, Ch Amis | 0,00 | 0 % | 0 | 18,6-20,9 | non |

Les 4 zones qui tirent le plus le bruleur sont exactement celles dont le planning a ete retouche en priorite ; les 5 zones sans aucun deficit n'ont pas ete touchees.

**Constats** (jours lun/mar/jeu/ven, derniers jours de la periode)

- **Les consignes basses (16-17 °C) ne sont jamais atteintes** : a midi les pieces restent a 17,5 (Hall) – 19,3 (Salon) – 18,0 (Salle à manger) – 18,9 (Salle de Bain) – 19,5 (Ch Louis). Les pieces sont chauffees « en passif » par les voisines (inertie du batiment) : baisser ou supprimer un creneau de jour ne degrade pas le confort.
- **Salle à manger** : de 06:00 a 08:00 la temperature ne bouge pas (18,4-18,6 °C) pendant le boost a 20 °C ; le deficit y est chronique (0,3-0,7 °C de 06:00 a 22:00). Le boost de 90 min n'atteint jamais sa cible et consomme du gaz pour rien.
- **Hall Entree** : ne descend jamais sous 17,4 °C meme avec 16 °C de consigne ; a 16:00 il est a 17,5 et met ~1-2 h pour atteindre 18,5-18,9 (deficit 0,4-0,5 a 16-17 h). Une cible de 19 °C est donc rarement tenue.
- **Salle de Bain** : montee mesuree ≈ **1 °C/h** (19,9 °C a 05:00 → 20,7 a 06:00 → 22,1 a 07:00, soit 0,1 °C au-dessus de la consigne de 22) puis refroidissement passif jusqu'a ~19 °C vers 12:00-14:00.
- **Ch Emma / Ch Louis** : 20,3-21,2 °C a 04:00-07:00, bien au-dessus de la consigne de 19 °C ; deficit ≈ 0 toute la journee.

**Verdict par modification**

| Zone | Modification | Appui des donnees |
|---|---|---|
| Salle à manger | Boost 06:00-07:30 a 20 °C supprime ; week-end 20 → 19 °C | **Fort** : boost sans effet mesurable, zone chroniquement sous sa cible |
| Hall Entree | 19 → 18 °C, matin +30 min, soir 16:00 → 17:00, week-end 12:00/19 → 18 | **Fort a moyen** : cible 19 rarement atteinte, la piece tient deja ~18 °C passivement |
| Salle de Bain | 22 → 21 °C, depart 05:00 → 05:30 | **Moyen** : a ~1 °C/h, 21 °C est atteint vers 06:45-07:00 ; depend de l'heure reelle d'utilisation, a surveiller |
| Ch Emma, Ch Louis | Depart 06:00 → 05:30 (semaine), week-end 06:00 → 07:00, creneau 16:00 week-end supprime | **Neutre** : temperature deja > consigne, aucun appel de chaleur, pas d'effet sur le gaz |
| Salon | Depart 06:00 → 05:30, soir 19:00 → 17:00 | **Non justifie par les deficits** (≈ 0 partout) : choix de confort qui ajoutait ~2 h/jour a 20 °C. **Soir remis a 19:00 le 2026-11-15** (matin 05:30 conserve) |
| Cuisine | deja au planning cible | Coherent : 9 % du temps en deficit |

**Limites de l'analyse** : la consigne moyenne par heure melange jours de presence et d'absence (mode « Chauffage Auto »), elle n'a pas ete utilisee pour les chiffres fins ; les statistiques horaires lissent les pics (deficits max souvent plus eleves). Pas de mesure de la conso gaz par zone.

**Suivi propose** : relancer `pyscript.evohome_deficit_history_stats` (`hours: 336`) apres 2 semaines avec les nouveaux plannings et comparer deficit moyen et gaz/jour a temperature exterieure comparable ; verifier en priorite Salle de Bain (deficit entre 05:30 et 07:00) et l'effet du Salon sur la conso.

### Ajustements du 2026-11-15 (soir) et architecture chaudiere

**Architecture** : la chaudiere Viessmann est **pilotee par Evohome** via un module : des qu'une zone demande de la chaleur, la chaudiere passe en « normal » (23 °C, courbe de chauffe pente 1,4 / decalage 0) ; sinon elle reste en « reduit » (3 °C). Il n'y a pas de programme horaire Viessmann a regler : ce sont les consignes Evohome qui decident de tout le temps de bruleur.

**Constat** : la nuit (21:00-05:00), le bruleur tourne ~2,5 h/nuit (28 h en 11 nuits, 68 cycles/jour de 6 min en moyenne sur 24 h) alors qu'aucune zone n'est sous sa consigne. Le **Hall Entree**, a 19 °C de 16:00 a 07:00 (et 19 °C en continu le week-end) pour une temperature de 19,0 °C, etait le suspect principal : 59 % du temps de bruleur nocturne a lieu avec le Hall a 0-0,2 °C de sa consigne, alors que le Hall se stabilise seul vers 17,4-17,5 °C quand il n'est pas chauffe. Cause **non demontree** (le bruleur tourne aussi 31-38 % de la nuit quand le Hall est > 0,5 °C au-dessus de sa consigne) ; la demande de chaleur reelle d'Evohome n'est pas exposee par evohomeasync2.

**Actions** :
- Salon : soir 17:00 → **19:00** (le Salon etait deja a 19,2-19,5 °C a 17:00-19:00).
- Hall Entree : consigne de nuit **16 °C** (22:00 → 05:30 semaine, 22:00 → 08:00 week-end) au lieu de 18-19 °C ; plus de consigne continue le week-end.
- **A mesurer** : heures de bruleur de nuit (reference ~2,5 h/nuit) sur 2-3 nuits ; si la baisse est nette, la cause est bien le Hall ; sinon chercher ailleurs.
- **Pile faible intermittente** sur la Salle de Bain (zone 2328068, capteur + actionneur) : le log HA a enregistre un defaut « low battery » a 11:22, 16:35 et 17:22 le 2026-11-15, mais `activeFaults` est vide a 19:11 (non permanent). Les piles sont changees quand l'ecran du controleur Honeywell remonte un defaut (aucun a ce jour). **Alerte automatique** : `automation/EvohomeDefauts.yaml` (« Evohome — Alerte défauts zones ») notifie dans HA et sur l'iPhone de Fabien quand une zone ou le systeme a un `activeFaults` non vide pendant 30 min ; la notification persistante est supprimee 5 min apres le retablissement. La zone Salle de Bain est en direct sur la chaudiere.
- **Test Bureau Fabien** (15/11 18:47 → 16/11 07:32) : consigne forcee a 5 °C pour savoir si la chaleur du premier etage depend de sa vanne. A interpreter avec prudence : le Hall a ete modifie la meme nuit (le bruleur peut aussi baisser).
- **Premier etage** (Hall Nuit, Bureau Fabien, Polyvalent, Ch Emma, Ch Louis, Ch Amis) : tuyaux partages ; Hall Nuit et Bureau Fabien restent ~+4 °C au-dessus de leur consigne, leur temperature suit la consigne maximale du groupe.
- **Chaine absence cassee** : l'automation « Change statut chauffage » (`automation.appliquer_mode_evohome_depuis_liste_deroulante`) est **desactivee depuis 2025-11-18**, donc `input_select.evohome_select` = Away ne change jamais le mode Evohome. A reactiver avant une longue absence (decision a prendre).

### Alignement Salon / Salle à manger / Cuisine et plannings du matin (2026-11-17)

Les 3 pieces forment **un seul volume ouvert** (pas de porte). Une **cassette a bois** dans le Salon souffle aussi dans le Hall d'entree (allumee souvent le week-end, pas tous les jours) : ces jours-la Salon/Hall/Cuisine depassent leur consigne et ne demandent plus de chaleur (ex. 15/11 soir : Salon 22,3 °C a minuit, Hall 18,1 °C) ; a exclure des comparaisons (voir plus bas).

**Suivi du test du 15/11** : brule de nuit ~40 min (nuit 15→16, avec cassette) puis ~35 min (nuit 16→17, sans cassette, ext. 10-12 °C) contre ~2,5 h avant. La 2e nuit, sans cassette et Bureau revenu a son planning, reste basse : le Hall a 16 °C la nuit est tres probablement la cause principale (pas de nuit de reference a meme temperature : base HA recreee le 15/11).

**Audit chaudiere 16-17/11** : 94 % des minutes de bruleur en chauffage ont une zone sous sa consigne (Cuisine 62 %, Salle à manger 19 %, Salle de Bain 16 %, Hall 2 %) ; 45 cycles, mediane 2 min (cycles du relais), depart median 39 °C, modulation max mediane 17 % : condensation OK. Etage 1 jamais sous consigne.

**Capteurs de presence** (mouvement Hall, lumieres, `person.*`) sur 2 matins de semaine : activite des 06:07-06:25, lumiere de la **Salle de douche** 06:45-07:16 (piece distincte de la Salle de bain, sans zone Evohome, seulement un radiateur electrique ; aucune lumiere « Salle de bain » dans HA : son usage se lit au radiateur booster 06:18-06:55 et au volet qui s'ouvre vers 07:15), departs 07:01-07:17 (Gillian) puis 07:27-07:30 (Fabien, Louis, Emma) : maison vide a 07:30.

**Plannings appliques le 2026-11-17** (lun/mar/jeu/ven ; mercredi = meme avec plage 12:00-14:00) :

| Zone | Semaine | Mercredi (en plus) | Sam, dim |
|---|---|---|---|
| Salon | 05:00/20, 07:30/16, 17:00/20, 23:00/19 | 12:00/20 puis 23:00/19 (sans creux, modifie fin de soiree) | 07:00/20, 23:00/18 |
| Cuisine | 05:00/20, 07:30/16, 17:00/19, 23:00/18,5 | 12:00/**19**, 14:00/16 | 07:00/19, 23:00/18 |
| Salle à manger | 05:00/19, 07:30/16, 17:00/18, 23:00/16 | 12:00/18, 14:00/16 | 07:00/18, 23:00/16 |
| Salle de Bain | 04:30/22, 07:30/17 | idem | 07:00/18, 20:00/17 |

- Horaires identiques pour Salon, Cuisine et Salle à manger ; les **valeurs** different : le Salon pilote (20/19 °C), la Salle à manger se stabilise seule vers 18 °C grace au Salon (elle n'a jamais atteint 20 °C) et la Cuisine flottait pres de sa consigne (60-76 % du temps sous 20 °C le matin et le soir) donc appelait la chaudiere en continu.
- Depart du matin avance de 05:30 a 05:00 et fin de chauffe a **07:30** au lieu de 08:00 : meme duree (2 h 30), sans gaz en plus. Montee mesuree ≈ 0,6 °C/h (salon, cuisine) : a 06:30 le 17/11 : Salon 19,8, Cuisine 18,8, Salle à manger 17,9, Salle de Bain 19,6 °C.
- Mercredi : les enfants sont au Salon l'apres-midi, d'ou le 20 °C de 12:00 a 14:00 (la Cuisine reste a 19).
- La Salle à manger etait a 19:00 pour le soir sans que ce soit une modification de Claude (origine inconnue) ; remise a 17:00.
- **Complements du 2026-11-17 (fin de soiree)** :
  - **Hall Entree 18 → 17 °C** (lun-ven 05:30/17, 07:00/16, 17:00/17, 22:00/16 ; sam-dim 08:00/17, 22:00/16) : sans cassette a bois il plafonne a 17,5-17,8 °C et n'atteint jamais 18 ; il etait sous sa consigne pendant 107 des 125 minutes de bruleur du soir (17h-23h). Sauvegarde de l'ancien planning : `evohome_hall_20261117_avant17.json`.
  - **Salon, mercredi** : plage 12:00-14:00 etendue a toute l'apres-midi (12:00/20 puis 23:00/19, plus de creux a 14:00). Appui : la prise TV du salon (`sensor.salon_prise_tv_power`, veille ~50 W, allumee > 90 W) montre la TV en marche les mercredis 28/10, 04/11 et 11/11 d'environ 12:00-13:00 jusqu'a 16:00-17:00 (3 mercredis sur 3 ; stats long terme de l'ancienne base). Cuisine et Salle à manger gardent leur plage 12:00-14:00. Les jeudis 29/10, 05/11 et 12/11 montrent aussi la TV l'apres-midi (a confirmer avec Fabien : quelqu'un est-il a la maison le jeudi apres-midi ?). Ancien planning du Salon : `evohome_schedules_20261117_2330.json`.
- Non modifies : chambres, Hall Nuit, Polyvalent, Bureau Fabien, WC Bas, Ch Amis (etage 1 jamais sous consigne).
- **Mesures de reference et comparaison future** : `config/evohome_backups/baseline_avant_matin_20261117.md` (T a 05:30-07:30, bruleur, kWh radiateurs). A refaire dans 2-3 matins ; si la Cuisine reste sous 19 °C a 06:30, avancer son depart a 04:30.
- Piege MCP : avec l'agent `ha-agent`, `ha_call_service` prend `service_data` (chaine JSON), pas `data` ; apres une ecriture, lancer `pyscript.evohome_fetch_schedules` puis relire `sensor.evohome_sched_*`.

**Radiateurs electriques d'appoint** (voir plus bas) : le radiateur de la Salle de bain tourne le matin vers 06:18-06:55 (~1,3 kW, 0,3-0,6 kWh) et le soir 12-60 min : il complete le chauffage central quand la piece est froide (19,6 °C a 06:30 le 17/11). Le demarrage a 04:30 devrait le faire moins tourner le matin (a verifier).

### Sauvegarde et restauration

- **Plannings d'apres le 2026-11-17 (12 zones)** : `config/evohome_backups/evohome_schedules_20261117_2330.json` ; **avant** les plannings matin/cuisine : `config/evohome_backups/evohome_matin_20261117_2340.json` (Salon, Cuisine, Salle à manger, Salle de Bain) et `evohome_sam_20261117_2310.json` (Salle à manger, planning 17:00/20 + nuit 19).
- **Plannings d'avant (12 zones)** : `config/evohome_backups/evohome_schedules_20261115_1815.json` (verifie par empreinte md5 contre les capteurs).
- **Restaurer une zone** : pour chaque zone, appeler `pyscript.evohome_set_zone_schedule` avec `zone_name` = `zones.<capteur>.zone_name` et `schedule` = `zones.<capteur>.schedule` du fichier (jours en anglais acceptes), puis `pyscript.evohome_fetch_schedules`. Zones a restaurer : Cuisine, Salon, Salle à manger, Hall Entree, Salle de Bain, Ch Emma, Ch Louis.
- **Restaurer l'ancien script** : copier `__init__.py.bak_20261115` sur `__init__.py` puis `pyscript.reload` (l'ancien script ne sait pas ecrire un planning).

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

**Situation des pieces** : la Salle de bain est une zone Evohome (`climate.salle_de_bain`, en direct sur la chaudiere) ; la **Salle de douche**, la **Chambre grenier** et le **Bureau Gillian** sont au **2e etage**, hors Evohome et hors chaudiere : Salle de douche = radiateur booster ci-dessus, Chambre grenier = climatisation Panasonic (`climate.chambre`), Bureau Gillian = autre climatisation (`climate.bureau_gillian`, peu utilise). Ils sont exclus des comparaisons gaz/Evohome.

**Usage constate (15-17/11/2026)** : le radiateur « booster » de la Salle de bain demarre vers 06:18-06:37 (~1,3 kW) pendant 12-21 min, et le soir 12-60 min (le 16/11 il a ete coupe par l'automation apres 1 h : switch resté OFF jusqu'a 06:37 le lendemain). Le radiateur de la Salle de douche (piece distincte de la Salle de bain) tourne a ~150-1150 W vers 06:57-07:53. Energie du SdB : 0,3-0,8 kWh par periode. Mesures de reference dans `config/evohome_backups/baseline_avant_matin_20261117.md`.

---

## Climatisation Panasonic

- Integration **panasonic_cc** (Panasonic Comfort Cloud)
- **`climate.chambre`** : unite de climatisation chambre grenier
- **`sensor.chambre_grenier_climatisation_power`** : puissance consommee instantanee (W) — inclus dans `sensor.power_heating`
- **`sensor.chambre_grenier_climatisation_daily_energy`** : energie journaliere (kWh) — inclus dans l'energy dashboard
- Sensors complementaires : `sensor.chambre_inside_temperature`, `sensor.chambre_outside_temperature`, `sensor.chambre_cooling_power`, `sensor.chambre_heating_power`

### Script sieste chambre grenier (`script/sieste_chambre_grenier.yaml`)

Sequence automatisee pour une sieste :
1. Ferme le volet (`cover.volet_chambre`, `speed: slow`)
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
| `automation/WelcomeHome.yaml` | Lumiere porte entree + garage 2 min a l'arrivee (apres sunset) |
| `script/sieste_chambre_grenier.yaml` | Sequence sieste : volets + clim avec timer |
| `template_sensors/temperature_rooms.yaml` | 12 sensors temperature Evohome + temperature chauffe-eau |
| `template_sensors/trajet_matin.yaml` | Temps trajet matin Fabien (3 segments) et Gillian |
| `template_sensors/household_applicances.yaml` | `sensor.connection_iphone_fabien` (localisation WiFi BSSID) |
| `pyscript/apps/evohome_schedule/__init__.py` | Fetch planifications 12 zones Evohome → JSON + sensors HA (cron 4h, service manuel) + ecriture de planning (`evohome_set_zone_schedule`, valide et attend la comm task) |
| `automation/EvohomeDefauts.yaml` | Alerte (notification persistante + push iPhone) quand une zone/le systeme Evohome a un defaut actif (piles, communication) pendant 30 min |
| `evohome_backups/evohome_schedules_20261117_2330.json`, `evohome_matin_20261117_2340.json`, `evohome_sam_20261117_2310.json`, `baseline_avant_matin_20261117.md` | Plannings apres/avant l'alignement et les plannings du matin du 2026-11-17, et mesures de reference pour comparer plus tard |
| `evohome_backups/evohome_schedules_20261115_1815.json` | Sauvegarde des 12 plannings avant l'optimisation du 2026-11-15 (procedure de restauration dans la section « Optimisation des plannings Evohome ») |
