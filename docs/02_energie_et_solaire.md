# Energie et Solaire

## Architecture energetique

```
                     Reseau (P1 Meter)
                          |
                     [Compteur bi-directionnel]
                          |
            +-------------+-------------+
            |                           |
     Consommation maison         Injection reseau
            |                           |
     +------+------+              Surplus solaire
     | Maison      |
     | Tesla       |         [Onduleur 1: SB5.0 #208]
     | Electro     |         [Onduleur 2: SB5.0 #345]
     | Lumieres    |                |
     | Prises      |          Panneaux PV
     +-------------+
```

## Compteur reseau - P1 Meter (HomeWizard)

Le compteur P1 mesure la puissance active et les totaux d'energie en tarif bi-horaire (Belgique).

| Sensor | Description |
|---|---|
| `sensor.p1_meter_3c39e7284d28_active_power` | Puissance active instantanee (W). **Positif = soutirage, Negatif = injection** |
| `sensor.p1_meter_3c39e7284d28_total_power_import_t1` | Total prelevement Heures Pleines (kWh) |
| `sensor.p1_meter_3c39e7284d28_total_power_import_t2` | Total prelevement Heures Creuses (kWh) |
| `sensor.p1_meter_3c39e7284d28_total_power_export_t1` | Total injection Heures Pleines (kWh) |
| `sensor.p1_meter_3c39e7284d28_total_power_export_t2` | Total injection Heures Creuses (kWh) |

**Convention tarif belge** : T1 = Heures Pleines (jour), T2 = Heures Creuses (nuit/WE).

## Production solaire - SMA

2 onduleurs SMA SB 5.0 (total ~10 kWc installe).

| Sensor | Description | state_class |
|---|---|---|
| `sensor.sb5_0_1av_41_208_grid_power` | Puissance onduleur 1 (W) | `measurement` |
| `sensor.sb5_0_1av_41_345_grid_power` | Puissance onduleur 2 (W) | `measurement` |
| `sensor.sb5_0_1av_41_208_total_yield` | Production cumul vie onduleur 1 (kWh) — 31 922 kWh | `total_increasing` |
| `sensor.sb5_0_1av_41_345_total_yield` | Production cumul vie onduleur 2 (kWh) — 32 294 kWh | `total_increasing` |
| `sensor.sb5_0_1av_41_208_daily_yield` | Production aujourd'hui onduleur 1 (Wh) | `total_increasing` |
| `sensor.sb5_0_1av_41_345_daily_yield` | Production aujourd'hui onduleur 2 (Wh) | `total_increasing` |
| `sensor.sb5_0_1av_41_208_voltage_l1` | Tension onduleur 1 (V) — exclu recorder |
| `sensor.sb5_0_1av_41_345_voltage_l1` | Tension onduleur 2 (V) — exclu recorder |

### Sensor calcule

- **`sensor.solar_total`** : Somme des 2 onduleurs (W) — unique_id `sensor.solar_total_power` mais entity_id derive du nom "Solar Total"

## Sensors de puissance calcules

### Par categorie

| Sensor | Formule | Description |
|---|---|---|
| `sensor.power_home` | P1 active + solaire onduleur 1 + solaire onduleur 2 | Consommation totale maison (W) |
| `sensor.power_lights` | Somme de ~20 sensors lumieres | Puissance eclairage (W) |
| `sensor.power_plugs` | VMC + PC + UPS + TV + Pompe eau | Puissance prises (W) |
| `sensor.power_tesla` | `sensor.f_r_i_d_a_y_charger_power` × 1000 (kW → W) | Puissance charge Tesla (W) |
| `sensor.power_heating` | Radiateur SdB + Radiateur SdD + Climatisation Panasonic | Puissance chauffage/clim (W) |
| `sensor.power_electro` | Seche-linge + Machine a laver | Puissance electromenager suivi (W) |
| `sensor.power_unmanaged` | home - lights - heating - electro - plugs - tesla | Puissance non suivie (W) |

### Energie nette

- **`sensor.net_energy`** : Consommation nette depuis le dernier releve officiel (01/01/2025)
  - Formule : `(import_HP - off_HP) + (import_HC - off_HC) - (export_HP - off_HP) - (export_HC - off_HC)`
  - Permet de suivre la consommation nette facturee

### Releve officiel (reference)

| Sensor | Valeur (kWh) |
|---|---|
| `sensor.officiel_heures_pleines_injection` | 27 308 |
| `sensor.officiel_heures_creuses_injection` | 9 545 |
| `sensor.officiel_heures_pleines_prelevement` | 16 049 |
| `sensor.officiel_heures_creuses_prelevement` | 22 066 |
| `sensor.date_dernier_releve_officiel` | 2025-01-01 |

## Surveillance onduleurs

- **Automation "Surveillance surtension Onduleurs"** : Detecte les decrochages onduleurs (surtension reseau)
- **Compteurs journaliers** : `counter.decrochage_onduleur_1`, `counter.decrochage_onduleur_2` (reset a minuit)

## Automations liees a l'energie

| Automation | Description |
|---|---|
| Compte Cycles Pompe A Eau | Incremente un compteur quand la pompe demarre (>50W) |
| Controle Radiateurs | Coupe les radiateurs SdB (1h) et SdD (40min) + notification |
| Surveillance surtension Onduleurs | Compte les decrochages onduleurs |
| Awtrix Consommation Nette | Affiche la conso nette sur l'afficheur LED |
| Min Max Consommation Nette | Suivi min/max de la consommation nette |

## Simulation batterie

L'integration **battery_sim** (HACS) est installee, probablement pour simuler l'interet d'une batterie domestique virtuelle par rapport a la production/consommation reelle.

## Statistiques long-terme

Tous les sensors P1 et SMA ont `state_class` natif depuis leur integration HA. Les sensors template (power_home, solar_total, etc.) ont `state_class: measurement` depuis `power_and_energy.yaml`.

### Recap state_class par type

| Type | state_class | Sensors |
|---|---|---|
| Energie cumulative (P1 import/export) | `total_increasing` | `total_power_import_t1/t2`, `total_power_export_t1/t2` |
| Energie cumulative (SMA yield) | `total_increasing` | `total_yield` x2, `daily_yield` x2 |
| Puissances instantanees | `measurement` | `active_power`, `grid_power`, tous les sensors calcules |
| Energie nette calculee | `total` | `sensor.net_energy`, sensors releves officiels |

### Analyse possible avec l'agent MCP

- **Taux d'autoconsommation** : (production - export) / production sur la periode
- **Taux d'autosuffisance** : (production - export) / consommation totale
- **Production solaire par periode** : via `total_yield` (increment entre deux dates)
- **Correlation production/meteo** : `daily_yield` vs `vicare_outside_temperature`
- **Pic de consommation** : `peak_demand_current_month` = tarif capacitaire belge

Exemples de questions a poser a l'agent :
> "Quel est mon taux d'autoconsommation solaire ce mois vs le mois dernier ?"
> "Est-ce que ma production solaire couvre ma recharge Tesla sur la semaine ?"
> "Quelles heures de la journee ai-je le plus de surplus solaire ?"

## Points cles pour les futures automatisations energie

1. **Le P1 meter est la source de verite** pour savoir si on soutire ou injecte
2. **Tarif bi-horaire** : HP (jour) vs HC (nuit/WE) - important pour optimiser les periodes de charge
3. **~10 kWc solaire** : production significative, surplus frequents en journee
4. **Toute la chaine de mesure est en place** : production, consommation, injection, prelevement
5. **La tension est mesuree** en temps reel (utile pour calculer la puissance Tesla a partir de l'amperage)
6. **Production cumulee** : onduleur 1 = 31 922 kWh, onduleur 2 = 32 294 kWh (total ~64 216 kWh vie)
