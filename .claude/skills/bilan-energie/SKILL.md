---
name: bilan-energie
description: Produit un bilan énergie de la maison (jour, semaine ou mois) - production solaire, soutirage T1/T2, injection, autoconsommation, Tesla. Utiliser quand l'utilisateur demande un bilan, un résumé ou une comparaison de consommation/production.
---

Délègue à l'agent `energie` avec la période demandée (défaut : 7 derniers jours).

Format de sortie attendu :
1. Tableau : production, soutirage T1, soutirage T2, injection, autoconsommation (kWh) + taux d'autoconsommation.
2. Part Tesla si disponible.
3. Comparaison avec la période précédente équivalente.
4. Anomalies détectées et 1 à 3 recommandations.

Si l'utilisateur donne les tarifs (€/kWh), ajouter le coût net estimé.
