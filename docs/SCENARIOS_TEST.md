# Scénarios de test

Exercice académique — vérifier pour chaque cas : **5 questions**, **recommandation intermédiaire**, **revue médecin**, **rapport final**.

## Cas 1 — Syndrome respiratoire simple

**Cas initial :**
> Patient de 28 ans, toux sèche depuis 4 jours, fatigue légère, pas de fièvre au thermomètre maison, pas de douleur thoracique.

**Réponses suggérées (5) :**
1. 4 jours
2. Non
3. Au repos c'est supportable
4. Aucun médicament, pas d'allergie
5. Aucun antécédent notable

**Revue médecin :** surveillance, paracétamol si besoin, consultation si fièvre ou essoufflement.

## Cas 2 — Red flags

**Cas initial :**
> Homme 55 ans, douleur thoracique depuis 1 heure, essoufflement au repos.

**Réponses suggérées :**
1. 1 heure
2. Non fièvre
3. S'aggrave au repos
4. Aspirine occasionnelle
5. Hypertension traitée

**Revue médecin :** orientation urgences / SAMU selon protocole local (exercice : documenter la conduite).

## Cas 3 — Cas bénin

**Cas initial :**
> Femme 22 ans, mal de gorge léger depuis 2 jours, alimentation normale.

**Réponses :** 2 jours / pas de fièvre / stable / pas de traitement / pas d'antécédent.

**Revue médecin :** hydratation, repos vocal, consultation si aggravation après 5 jours.

## LangGraph Studio

1. `cd backend` puis `langgraph dev` (depuis la racine avec `PYTHONPATH=..`).
2. Observer les transitions : supervisor → diagnostic_agent → … → physician_review → report_agent.
3. Utiliser les interrupts pour simuler réponses patient et médecin.
