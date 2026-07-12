# SEPI — Suivi de l'État des Poubelles par Image

> Détection automatique de l'état des points de collecte (**Vide** / **Pleine**) à partir d'une simple photo, par **extraction de caractéristiques d'image** et **classification par règles** — **sans machine learning**.

SEPI est une application web pensée pour aider les collectivités à **prévenir les dépôts sauvages**. Plutôt que de nettoyer une fois le problème visible, SEPI permet de repérer en amont les points de collecte qui débordent, à partir d'images prises sur le terrain.

**Application en ligne : [https://sepi-visio.streamlit.app](https://sepi-visio.streamlit.app)**

---

## Sommaire

- [Le principe](#le-principe)
- [Une approche IA, sans deep learning](#une-approche-ia-sans-deep-learning)
- [Fonctionnalités : les 6 onglets](#fonctionnalités--les-6-onglets)
- [Architecture du projet](#architecture-du-projet)
- [Installation et lancement](#installation-et-lancement)
- [Hébergement](#hébergement)
- [Stack technique](#stack-technique)
- [Limites connues](#limites-connues)

---

## Le principe

Le pipeline de SEPI suit quatre étapes :

**Image → Extraction de caractéristiques → Classification par règles → Visualisation**

À chaque image uploadée, l'application :

1. **calcule 23 caractéristiques** de l'image (couleur, luminosité, contours, texture, désordre au sol, etc.) ;
2. applique un **ensemble de règles conditionnelles** (`if / else`) sur les caractéristiques les plus discriminantes ;
3. en déduit un **verdict** — *Vide* ou *Pleine* — accompagné d'un **score de confiance** ;
4. stocke le tout en base de données et l'affiche dans des **tableaux de bord** et une **cartographie**.

---

## Une approche IA, sans deep learning

SEPI est un projet d'**intelligence artificielle**, mais **pas de machine learning**. Il est important de bien comprendre la différence, car elle est au cœur de notre démarche.

**Ce que fait un modèle de deep learning classique :** il est entraîné sur des milliers d'images, et « apprend » tout seul à reconnaître une poubelle pleine. Le problème : sa décision est une **boîte noire** — on ne sait pas *pourquoi* il a tranché dans un sens ou dans l'autre.

**Ce que fait SEPI :** il n'y a **aucun modèle entraîné**. La décision vient de **règles écrites à la main**, à partir de mesures objectives calculées sur l'image. Chaque verdict est donc **entièrement explicable** : on peut dire exactement quelles caractéristiques ont fait pencher la décision vers *Vide* ou *Pleine*.

Là où le deep learning fournit une probabilité opaque, SEPI fournit une décision **auditable, lisible et ajustable**. C'est un choix assumé : sur un sujet public comme la gestion des déchets, pouvoir justifier chaque décision devant un élu ou un citoyen est un vrai atout.

Le **score de confiance** affiché joue un rôle comparable à la probabilité d'un réseau de neurones, mais il repose sur une logique transparente : il correspond au **nombre de règles déclenchées** sur le total. Plus il y a de règles qui pointent vers « Pleine », plus la confiance est élevée.

---

## Fonctionnalités : les 6 onglets

L'application est organisée en six onglets, accessibles depuis le menu latéral.

### 1. Accueil — Upload d'une image

L'onglet principal. L'utilisateur **dépose une image** d'un point de collecte, et l'application affiche :

- le **résultat de l'analyse** : *Vide* ou *Pleine* ;
- le **score de confiance** de la décision ;
- les **caractéristiques les plus importantes** ayant conduit à ce résultat (les « facteurs » qui ont fait pencher la décision) ;
- une possibilité d'**annotation manuelle** : l'utilisateur peut confirmer ou corriger le verdict de l'IA.

L'annotation manuelle est essentielle : elle constitue la **vérité terrain** qui permet, dans l'onglet Visualisations, de mesurer la performance réelle du système en comparant les décisions de l'IA aux annotations humaines.

### 2. Multi-Upload — Traitement par lot

Même principe que l'onglet Accueil, mais pour **plusieurs images à la fois**. L'utilisateur dépose un lot d'images, puis les traite **une par une** : pour chaque image, l'application affiche le résultat de l'IA et son score de confiance, et l'utilisateur annote manuellement avant de passer automatiquement à l'image suivante. Idéal pour constituer rapidement un jeu d'images annotées.

### 3. Gallery — Visualisation des images

La galerie affiche les **images collectées** sous forme de vignettes. Elle sert notamment à **repérer visuellement les images mal prédites** et à comprendre *pourquoi* elles échouent, afin d'améliorer les règles et les caractéristiques.

Des **filtres** permettent d'explorer les images selon :

- le **nom** de l'image ;
- l'**annotation manuelle** (Vide / Pleine) ;
- l'**annotation IA** ;
- le **niveau de confiance** de l'IA ;
- une **plage de dates**.

C'est l'outil de travail pour l'amélioration continue : en croisant annotation manuelle et prédiction IA, on identifie les cas d'échec et on ajuste la logique de classification.

### 4. Historique — La base de données

L'historique joue un rôle proche de la galerie, mais **sans les photos** : il affiche directement le **contenu de la base de données**, c'est-à-dire, pour chaque image :

- toutes les **caractéristiques calculées** (les 23 features) ;
- le **chemin** vers le fichier image ;
- les annotations manuelle et IA, la confiance, la date, etc.

C'est la vue « données brutes », utile pour l'analyse détaillée et l'export. Des **filtres** (état IA, annotation manuelle, recherche, confiance, tri) et un **export CSV** y sont disponibles.

### 5. Statistiques — Visualisations et performances du modèle

L'onglet analytique. Il regroupe les **visualisations** du projet et mesure les **performances** de la classification :

- **répartition** des états détectés (Vide / Pleine) ;
- **distribution des caractéristiques** selon l'état — pour voir lesquelles séparent le mieux les deux classes ;
- **corrélations** entre caractéristiques ;
- **importance des caractéristiques** (pouvoir de séparation de chacune) ;
- **performance de la classification** : accuracy, précision, recall, spécificité, F1-score, et **matrice de confusion** (IA vs annotation manuelle).

### 6. À propos

Une présentation de l'application : son objectif, son fonctionnement, l'équipe et la démarche du projet.

---

## Architecture du projet

```
SEPI/
├── app/
│   └── core/
│       ├── features.py      # Extraction des 23 caractéristiques d'image
│       ├── rules.py         # Classification par règles (Vide / Pleine)
│       └── metrics.py       # Calcul des métriques de performance
│
├── views/
│   ├── accueil.py           # Onglet 1 — upload + résultat
│   ├── multi_upload.py      # Onglet 2 — traitement par lot
│   ├── gallery.py           # Onglet 3 — galerie + filtres
│   ├── historique.py        # Onglet 4 — base de données
│   ├── statistiques.py      # Onglet 5 — visualisations & performances
│   └── a_propos.py          # Onglet 6 — à propos
│
├── classifier.py            # Pont entre le moteur et l'interface
├── database.py              # Accès à la base SQLite
├── web_app.py               # Point d'entrée Streamlit
├── Data/
│   └── web_app/             # Images uploadées via l'application
├── requirements.txt
└── README.md
```

---

## Installation et lancement

### Prérequis

- **Python 3.11+**
- **Git**

### Étapes

**1. Cloner le dépôt :**

```bash
git clone https://github.com/VOTRE-COMPTE/SEPI-visio.git
cd SEPI-visio
```

**2. Créer et activer un environnement virtuel :**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

**3. Installer les dépendances :**

```bash
pip install -r requirements.txt
```

**4. Lancer l'application :**

```bash
streamlit run web_app.py
```

L'application s'ouvre automatiquement dans le navigateur à l'adresse `http://localhost:8501`.

> **Note :** la base de données SQLite se **crée automatiquement** au premier lancement si elle n'existe pas. De même, le dossier de stockage des images (`Data/web_app`) est créé au besoin.

---

## Hébergement

L'application est **déployée et hébergée sur Streamlit Community Cloud**, à l'adresse :

**[https://sepi-visio.streamlit.app](https://sepi-visio.streamlit.app)**

Le déploiement est directement connecté au dépôt GitHub : chaque mise à jour poussée sur la branche suivie est automatiquement reprise par la plateforme, qui reconstruit et redéploie l'application.

> **À savoir :** l'application se met en veille après une période d'inactivité et met quelques secondes à se réveiller au premier accès. Le stockage étant éphémère sur ce type d'hébergement gratuit, les images uploadées et la base peuvent être réinitialisées lors d'un redémarrage — ce qui convient à une démonstration, mais nécessiterait un stockage externe (type S3) pour une mise en production.

---

## Stack technique

| Couche | Technologies |
|---|---|
| Langage | Python 3.11 |
| Interface web | Streamlit |
| Traitement d'image | Pillow, NumPy, OpenCV |
| Base de données | SQLite |
| Visualisations | Matplotlib, Seaborn |
| Hébergement | Streamlit Community Cloud |

---

## Limites connues

Par honnêteté et rigueur, nous documentons les cas où le système est mis en difficulté :

- **déchets clairs et épars** au sol, visuellement proches d'un trottoir ou de pavés ;
- **images floues** (prises de loin ou en mouvement) ;
- **très faibles résolutions**, où les caractéristiques locales perdent leur sens ;
- **végétation** naturelle parfois confondue avec un dépôt de déchets verts.

Ces cas constituent la limite intrinsèque d'une approche par règles sans apprentissage profond : le système mesure des indices visuels, mais ne *comprend* pas le contenu de l'image. C'est un choix assumé, au service de la transparence et de l'explicabilité.

---

*Projet réalisé dans le cadre de la Solution Factory — Efrei.*
