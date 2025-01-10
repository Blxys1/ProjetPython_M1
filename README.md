# ProjetPython Search Engine

Projet de 1ère année de Master Informatique, Université Lumière Lyon 2

## Description

Ce projet consiste en la création d'un moteur de recherche en Python capable de :

- **Scraper des documents** depuis des sources en ligne telles que NewsAPI et Arxiv.
- **Gérer un corpus de documents** via une classe `Corpus`, incluant l'ajout, la suppression et la sauvegarde de documents.
- **Fournir des fonctionnalités avancées** comme la recherche par mot-clé, la génération de statistiques (fréquence des mots, auteurs prolifiques, etc.) et une concordance contextuelle.
- **Offrir une interface utilisateur minimaliste** simple pour effectuer des recherches, visualiser des statistiques et gérer le corpus.

## Fonctionnalités

- **Scraping de données** : Récupération de documents depuis NewsAPI et Arxiv.
- **Gestion du corpus** : Ajout, suppression, sauvegarde et chargement de documents.
- **Recherche** : Recherche par mot-clé avec affichage des résultats pertinents.
- **Statistiques** : Génération de statistiques sur le corpus, y compris la fréquence des mots et les auteurs les plus prolifiques.
- **Interface utilisateur** : Interface graphique développée avec Tkinter pour une interaction conviviale.

## Prérequis

- Python 3.12
- Bibliothèques Python suivantes :
  - `urllib`
  - `xmltodict`
  - `NewsApiClient`
  - `pandas`
  - `scipy`
  - `sklearn`
  - `tkinter`

## Installation

1. **Cloner le dépôt** :

   ```bash
   git clone https://github.com/Blxys1/ProjetPython_M1.git
   cd ProjetPython_M1

2. **Install dependencies :**
      ```bash
   pip install pandas scipy scikit-learn tk

  

