# Mesures de reference AVANT les plannings « matin » du 2026-11-17 (23:16)

Source : base HA recreee le 2026-11-15 17:36 (pas d'historique avant). Jours de semaine 16/11 et 17/11 uniquement. Ext. 7-14 °C.
Plannings en vigueur pendant ces mesures : voir `evohome_sam_20261117_2310.json` (SAM), `evohome_matin_20261117_2340.json` (Salon, Cuisine, SAM, SdB avant changement). Plannings apres : `evohome_schedules_20261117_2330.json`.

## Temperatures reelles de la maison (T °C), 17/11 (lundi 16/11 entre parentheses)

| Zone | 05:30 | 06:30 | 07:00 | 07:30 |
|---|---|---|---|---|
| Salon (cons. 20 des 05:30) | 19,2 (21,4) | 19,8 (21,2) | 20,6 (21,2) | 20,6 (21,2) |
| Cuisine (cons. 20 des 05:30) | 18,4 (19,6) | 18,8 (19,5) | 19,4 (19,4) | 19,6 (19,4) |
| Salle a manger (cons. 16 puis 20 le 16/11 : planning different) | 17,9 (20,3) | 17,9 (19,9) | 17,9 (19,9) | 18,1 (19,9) |
| Salle de bain (cons. 22 des 05:00) | 18,6 | 19,6 | 21,4 | 21,4 |
| Hall Entree (cons. 18 des 05:30) | 16,5 (17,4) | 16,4 (17,4) | 17,2 (17,4) | 17,5 (17,6) |

Objectif demande : maison « bien a temperature » au lever (~06:15-06:30), departs ~07:30.

## Presence (capteurs mouvement hall, lumieres, person.*)

- Premiere activite 05:26 (16/11, brief) puis 05:55-06:25 ; 17/11 : 06:07 (hall de nuit), 06:12 (chambre Emma), 06:24 (cuisine).
- Cuisine/salon : lumieres ~06:24-07:28. Lumiere de la Salle de DOUCHE (piece distincte de la Salle de BAIN, sans zone Evohome) 06:45-07:16. Aucune lumiere Salle de bain dans HA : son usage se lit au radiateur booster (06:18-06:55) et au volet (~07:15).
- Departs : Gillian 07:01 (16/11) / 07:17 (17/11) ; Fabien + Louis 07:27 / 07:30 ; Emma ~07:19-07:26. Maison vide a 07:30.

## Chaudiere (16-17/11)

- Chauffage : 177 min de bruleur sur 2 jours (62 min le 16, 115 min le 17) ; ECS 113 min. 45 cycles chauffage, mediane 2 min (29 < 3 min), depart mediane 38,8 °C, modulation max mediane 17 %.
- 94 % des minutes de chauffage ont au moins une zone sous sa consigne : Cuisine 62 %, Salle a manger 19 %, Salle de bain 16 %, Hall 2 %.
- Nuit 15->16/11 : ~40 min de bruleur (ext 7-8 °C, **cassette a bois allumee** le dimanche soir : Salon 22,3 °C a minuit, Hall 18,1) ; nuit 16->17/11 : ~35 min (ext 10-12 °C, pas de cassette). Reference d'avant le 15/11 : ~2,5 h/nuit.

## Radiateurs electriques (energie integree depuis la puissance)

| | SdB radiateur | Salle de douche radiateur |
|---|---|---|
| 15/11 soir | 0,34 kWh (19:56-20:09) | - |
| 16/11 matin | 0,57 kWh (06:18-06:39 puis 06:45-06:57) | 0,78 kWh (06:58-07:53) |
| 16/11 soir | 0,83 kWh (19:45-20:45, coupe par l'automation apres 1 h) | 0 |
| 17/11 matin | 0,33 kWh (06:37-06:55) | 0,37 kWh (06:57-07:12) |
| 17/11 soir | 0,29 kWh (19:58-20:10) | 0 |

A comparer dans 2-3 matins : minutes/kWh du radiateur SdB avant 07:00 (le depart SdB passe de 05:00 a 04:30).

## Changements posterieurs a ces mesures (2026-11-17, ~23:35)

- Hall Entree 18 → 17 °C (matin 05:30-07:00, soir 17:00-22:00, week-end 08:00-22:00). Mesure avant : T 16,4-17,8 sans cassette, sous consigne pendant 107 des 125 min de bruleur du soir (17h-23h).
- Salon mercredi : creux 14:00-17:00 a 16 °C supprime (20 °C de 12:00 a 23:00). TV salon allumee les mercredis ~12-13h a 16-17h (prise `sensor.salon_prise_tv_power`).
- Repartition du bruleur chauffage 16-17/11 : 125 min entre 17h et 23h, 32 min le matin (05:00-07:30 environ), 17 la nuit, 3 le jour : le soir pese plus que le matin.

## A comparer plus tard

1. T a 06:30 des 5 zones ci-dessus (cible : Salon >= 20, Cuisine >= 19, SAM >= 18, SdB >= 21, a ext comparable).
2. Minutes de bruleur chauffage 05:00-07:30 et sur 24 h ; part Cuisine/SAM/SdB.
3. kWh radiateur SdB le matin.
4. Noter les jours de cassette a bois (Salon > 21,5 °C le soir, Hall > 18,5 la nuit) pour les exclure.
