# Volets et Velux

## Architecture

Les volets sont pilotes via l'integration **Overkiz** (Somfy TaHoma). Deux scenes globales sont exposees par la plateforme :

| Scene | Entite | Role |
|---|---|---|
| Ouverture globale | `scene.ouverture_volets` | Ouvre tous les volets |
| Fermeture globale | `scene.fermeture_volets` | Ferme tous les volets |

Les Velux (fenetres de toit) sont des entites `cover.*` independantes, controlees directement par leurs services HA.

---

## Entites covers

### Volets (Overkiz / Somfy)

| Entite | Emplacement |
|---|---|
| `cover.volet_tv` | Salon cote TV |
| `cover.volet_tv_low_speed` | Salon cote TV (vitesse lente) |
| `cover.volet_canape` | Salon cote canape |
| `cover.volet_canape_low_speed` | Salon cote canape (vitesse lente) |
| `cover.volet_salle_a_manger_low_speed` | Salle a manger (vitesse lente) |
| `cover.volet_chambre_low_speed` | Chambre grenier (vitesse lente) |

### Velux (fenetres de toit)

| Entite | Emplacement |
|---|---|
| `cover.velux_sdd_droite` | Salle de douche droite |
| `cover.velux_sdd_gauche` | Salle de douche gauche |
| `cover.velux_escalier` | Escalier |
| `cover.velux_chambre` | Chambre |
| `cover.volet_velux_chambre` | Volet Velux chambre |

---

## Automatisations

### Ouverture Volets Matin (id: 1746094800000)

Fichier : `config/automations.yaml`

Ouvre tous les volets via `scene.ouverture_volets` selon le type de jour, uniquement si le soleil est leve.

**Logique a 3 triggers :**

| Trigger | Conditions | Action |
|---|---|---|
| ⏰ 7h00 | Jour = lundi–vendredi + soleil leve | Ouvre volets |
| ⏰ 9h00 | Jour = samedi–dimanche + soleil leve | Ouvre volets |
| 🌅 Lever du soleil | (Semaine ET heure >= 7h) OU (week-end ET heure >= 9h) | Ouvre volets |

Le trigger sunrise couvre le cas hivernal : si le soleil se leve a 8h30 un mercredi, le trigger 7h ne passe pas (soleil pas leve), mais le trigger sunrise se declenche car 8h30 > 7h.

### Fermeture Volets (id: 1730209049725)

Fichier : `config/automations.yaml`

| Trigger | Action |
|---|---|
| Coucher du soleil + 20 min | Active `scene.fermeture_volets` |

### Harmony Home — volets salon (id: 1722360860567)

Fichier : `config/automations.yaml`

Controle manuel via telecommande Harmony Hub (Emulated Roku) :

| Bouton | Action |
|---|---|
| `Up` | Ouvre `volet_tv_low_speed` + `volet_canape` |
| `Down` | Ferme `volet_canape` + `volet_tv` |
| `Left` | Toggle `volet_canape_low_speed` + `volet_tv_low_speed` |
| `Right` | Toggle `volet_salle_a_manger_low_speed` |

### Aeration Velux (id: 1681121951553)

Fichier : `config/automations.yaml`

Declenche par `timer.velux` (timer a lancer manuellement) :

- Timer actif → ouvre les 4 Velux + notification "Debut aeration"
- Timer termine → ferme les 4 Velux + notification "Fin aeration"

Velux controles : `velux_sdd_droite`, `velux_sdd_gauche`, `velux_escalier`, `velux_chambre`.

---

## Scripts

### Sieste chambre grenier

| Script | Fichier | Action |
|---|---|---|
| `script.sieste_chambre_grenier` | `script/sieste_chambre_grenier.yaml` | Ferme `volet_chambre_low_speed` + `volet_velux_chambre`, lance la clim |
| `script.fin_sieste_chambre_grenier` | `script/fin_sieste_chambre_grenier.yaml` | Ouvre `volet_chambre_low_speed` + `volet_velux_chambre`, eteint la clim |
