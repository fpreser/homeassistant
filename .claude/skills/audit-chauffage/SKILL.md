---
name: audit-chauffage
description: Audit du chauffage de la maison - capteurs Evohome (12 zones), brûleur, circulateur, ECS, départ chaudière - avec constats, bizarreries à clarifier et optimisations proposées. À utiliser quand l'utilisateur demande d'analyser/optimiser le chauffage, Evohome, le brûleur ou le circulateur, ou de refaire l'audit.
---

Analyse en lecture seule : ne modifier AUCUN planning, consigne ou réglage sans accord explicite de l'utilisateur.

1. **Mesures** : `python -I .claude/skills/audit-chauffage/audit_chauffage.py 15` (avec `PYTHONIOENCODING=utf-8`). Source : Prometheus (15 jours, 1 point/min). Il sort : jour par jour, cycles et intervalles de départ, départ/modulation, charges ECS, profil horaire, nuits (dont runs continus et minutes sans zone en déficit), zones, matins de semaine.
2. **Consignes actuelles** : lire les plannings avec `ha_render_template` sur `state_attr('sensor.evohome_sched_<zone>','schedule')` et l'état des `climate.<zone>` (T, consigne). Vérifier que les plannings voulus ont tenu (un écrasement a déjà eu lieu le 17→20/11). Contrôler aussi, pour chaque `climate.<zone>`, `attributes.status` : `activeFaults`, `temperature_status.is_available`, `setpoint_status.setpoint_mode` (FollowSchedule attendu), et l'âge de `last_updated` (zone figée si > quelques heures) ; et `climate.home.attributes.status` (défauts système, mode Auto).
3. **Comparer** avec la dernière référence : mémoire de l'agent `energie` (`chauffage_audit_*.md` et `chauffage_maison.md`) et la mémoire du projet. Citer la température extérieure à chaque comparaison.
4. **Rapport** en 3 blocs : constats chiffrés ; bizarreries (questions à poser à l'utilisateur) ; optimisations proposées classées par gain/risque, chacune avec ce qu'il faut changer et où (contrôleur Evohome, app ViCare, planning).
5. **Mémoriser** : écrire le nouvel audit dans la mémoire locale de l'agent `energie` (jamais dans le dépôt, qui est public : pas de données de présence ni d'horaires du foyer dans les fichiers commités).

**Pièges connus**
- Le capteur `binary_sensor.vicare_dhw_pump_active` reste à 0 : l'ECS est détectée par un départ chaudière >= 60 °C.
- Prometheus n'exporte pas les `climate.*` ni les plannings : consigne = lue dans HA ; `sensor.evohome_deficit_*` vaut 0 dès que la zone est à sa consigne (déficit tronqué à 0).
- Un « samedi » n'a pas les mêmes plannings que la semaine : ne pas juger les matins de week-end contre les cibles de semaine.
- `ch_amis` n'a pas de `sensor.temp_*` (le script ne montre donc pas sa température), mais `climate.chambre_amis` fonctionne : son déficit à 0 est normal quand elle est au-dessus de sa consigne (16 °C).
- Les 4 caractères accentués s'affichent mal sous la console Windows sans `PYTHONIOENCODING=utf-8`.
- Les puissances de la chaudière ne sont pas exposées ; le gaz est du propane en citerne (1 m³ ViCare ≈ 1,6 L).
- Le programme actif de la chaudière (`active_vicare_program` de `climate.vicare_heating` : normal / reducedEnergySaving / reduced) n'est PAS dans Prometheus mais dans la base HA (états + attributs) : il montre quand le contact Evohome (module Viessmann EM-EA1) est fermé ; une période continue en « normal » > 90 min la nuit sans zone en déficit est à signaler.
- Les réglages de courbe (pente, décalage), consignes normal/réduit/confort et température ECS sont des `number.e3_vitodens_200_0419_*` modifiables depuis HA : ne les changer qu'avec l'accord de l'utilisateur.
- Le brûleur est piloté par Evohome via un relais (tout/rien, cycle de 10 min) : les impulsions de 2 min toutes les 10 min viennent du relais, pas de la chaudière.
