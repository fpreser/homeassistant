# Dashboard — Volets et Vélux

**Vue :** `volets-et-velux` (subview, icône `mdi:window-shutter`)

---

## Structure générale

```
┌─────────────────────────────────────────────┐
│  Ligne 1 : Gestion thermique                │
├─────────────────────────────────────────────┤
│  Ligne 2 : Aération vélux                   │
├─────────────────────────────────────────────┤
│  Tabs par étage                             │
│   🏠0  │  🏠1  │  🏠2                       │
│  ──────────────────────────────────────────  │
│  [contenu tab actif]                        │
└─────────────────────────────────────────────┘
```

---

## Ligne 1 — Gestion thermique estivale

| Widget | Type | Entité | Action |
|---|---|---|---|
| Gestion thermique | `mushroom-entity-card` | `input_boolean.gestion_thermique` | Tap = toggle |
| Seuil (°C) | `mushroom-number-card` | `input_number.seuil_chaleur` | Boutons +/− |
| T ext | `mushroom-entity-card` | `sensor.vicare_outside_temperature` | Affichage seul |

Active/désactive le système de fermeture automatique des volets et d'ouverture nocturne des vélux.
Voir [docs/07_volets.md](07_volets.md) pour la logique complète.

---

## Ligne 2 — Aération vélux manuelle

| Widget | Type | Entité | Action |
|---|---|---|---|
| Durée | `mushroom-entity-card` | `input_datetime.velux_aeration_duration` | Réglage durée |
| Démarrage | `mushroom-entity-card` | `timer.velux` | Tap = `script.start_aeration` |
| Pluie 2h | `mushroom-entity-card` | `binary_sensor.pluie_imminente_2h` | Affichage seul |

Lance `script.start_aeration` → ouvre `velux_sdd_droite`, `velux_sdd_gauche`, `velux_escalier` pendant la durée configurée. `velux_chambre` **exclu** (géré séparément par GestionThermique).

---

## Tabs par étage

### Tab 0 — Rez-de-chaussée (`mdi:home-floor-0`)

| Ligne | Volet gauche | Volet droit |
|---|---|---|
| 1 | `volet_tv_low_speed` — TV | `volet_canape_low_speed` — Canapé |
| 2 | `volet_salle_a_manger_low_speed` — S-M | `volet_cuisine_low_speed` — Cuisine |

### Tab 1 — 1er étage (`mdi:home-floor-1`)

| Ligne | Volet gauche | Volet droit |
|---|---|---|
| 1 | `volet_poly_pelouse_low_speed` — Poly Pelouse | `volet_poly_route_low_speed` — Poly Route |
| 2 | `volet_emma_route_low_speed` — Emma Route | `volet_emma_gauche_low_speed` — Emma Gauche |
| 3 | `volet_louis_low_speed` — Louis | `volet_salle_de_bain_low_speed` — Sdb |
| 4 | `volet_bureau_fabien` — Bureau | `volet_bureau_gillian_low_speed` — Ch Amis |

### Tab 2 — Grenier (`mdi:home-floor-2`)

| Ligne | Carte gauche | Carte droite |
|---|---|---|
| 1 | `volet_velux_chambre` — Occultant | `volet_chambre_low_speed` — Fenêtre Est |
| 2 | `velux_escalier` — Escalier | `velux_chambre` — Vélux Chambre |
| 3 | `velux_sdd_gauche` — SDD Gauche | `velux_sdd_droite` — SDD Droite |

---

## Notes

- `cover.volet_bureau_fabien` (tab 1er, ligne 4) n'a pas de variante `_low_speed` — c'est intentionnel, le volet ne dispose pas de cette entité.
