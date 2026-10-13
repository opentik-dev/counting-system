# Warehouse Vision Counting System

**Langues :** [العربية](../README.md) · [English](README.en.md) · [Français](README.fr.md) · [Español](README.es.md) · [Türkçe](README.tr.md) · [中文](README.zh-CN.md)

Un noyau local et auditable pour compter les cartons et palettes qui franchissent
une ligne dans un entrepôt. Le MVP transforme des observations suivies en
événements directionnels `IN/OUT`, évite les doublons et conserve les métadonnées
de preuve dans SQLite.

## Démarrage rapide

```bash
python3 -m pytest -q
PYTHONPATH=src python3 -m warehouse_counting.demo
```

Le cœur fonctionne avec Python 3.11+ et la bibliothèque standard. Les outils
d’entraînement CPU sont optionnels. Voir [`README.en.md`](README.en.md) pour la
documentation technique détaillée.

## Périmètre actuel

Une ligne de comptage, les objets `carton` et `pallet`, le filtrage par confiance,
la prévention des doublons, la persistance SQLite et les règles explicites de
capacité des palettes. Les caméras en direct, tableaux de bord et l’évaluation
de précision en production restent sur la feuille de route.

## Rejoindre la communauté

Les contributions des développeurs, chercheurs, spécialistes d’entrepôts et
traducteurs sont les bienvenues. Consultez [`CONTRIBUTING.md`](../CONTRIBUTING.md),
ouvrez une Issue et proposez des Pull Requests ciblées et testées.

## Licence

MIT — voir [`LICENSE`](../LICENSE).
