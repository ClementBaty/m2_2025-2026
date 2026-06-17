# Module d’Extraction de Caractéristiques Avancées 
Projet Groupe C – Interface + Analyse de Signaux

---

##  1. Rôle du module

Ce module fournit un outil complet permettant :

- de charger un fichier CSV ou JSON contenant un signal temporel ou spectral,
- d’extraire automatiquement des caractéristiques avancées (FFT, pics, centroïde spectral, statistiques temporelles),
- d’afficher les résultats dans une interface graphique,
- d’exporter les résultats en CSV et/ou JSON.

Il combine une interface PyQt5 ergonomique et un moteur d’analyse basé sur NumPy, SciPy et Pandas.

---

##  2. Entrées attendues

### Fichier CSV/JSON
Le module accepte deux formats :

- **Signal temporel** : colonne temps + colonne amplitude  
- **Signal spectral** : colonne fréquence + colonne amplitude  

Le type de signal est détecté automatiquement.

### Paramètres utilisateur
- Fréquence d’échantillonnage `fs` (vous pouvez decider de l'indiquer manuellement ou quéelle soit calculée automatiquement en fonction des données du signal filtré)
- Dossier de sortie
- Options d’export : CSV / JSON

---

##  3. Sorties générées

### Affichage dans l’interface
- 3 plus grands pics FFT (amplitude + fréquence)
- Centroïde spectral
- Moyenne, écart-type, kurtosis, skewness, RMS (si signal temporel)

### Fichiers exportés
- `features_output.csv`
- `features_output.json`

Ces fichiers contiennent toutes les caractéristiques extraites.

---

##  4. Comment tester le module

1. Lancer l’interface :
   ```bash
   python main_interface.py

2. Charger un fichier
    ```bash
    Cliquer sur Choisir fichier
    Sélectionner un fichier .csv ou .json

3. Définir les paramètres
    ```bash
    Cocher/décocher l’utilisation d’une fréquence manuelle
    Saisir fs si nécessaire
    Choisir un dossier de sortie

4. Lancer l’extraction
Cliquer sur :
   ```bash
   Lancer l'extraction
6. Vérifier les résultats
Les caractéristiques s’affichent dans la zone Résultats

**Les fichiers features_output.csv et features_output.json sont créés dans le dossier choisi**

---

## 5. Répartition des tâches dans le groupe
Notre groupe a travaillé de manière collaborative. Voici la répartition réelle des tâches :

 ### 1. Analyse des besoins et choix techniques 
Nous avons défini ensemble :
- les fonctionnalités nécessaires,
- le choix du code de référence issu de nos anciens cours,
- la structure générale du projet.

### 2. Développement du moteur d’extraction 
Nous avons :
- vérifier la cohérence du code d’extraction existant,
- corriger les erreurs,
- améliorer la robustesse,
- intégrer l’IA pour optimiser certaines fonctions,
- valider les résultats.

### 3. Conception de l’interface graphique 
Nous avons travaillé sur :

- la réflexion ergonomique,
- la conception visuelle,
- la création de l’interface dans Qt Designer,
- la conversion du .ui en .py,
- l’intégration avec le code principal.

### 4. Intégration finale avec l’IA 
En se basant de notre code et de l'interface fait l’IA nous a aidés à :

- générer le fichier main_interface.py,
- connecter les boutons,
- intégrer le moteur d’extraction,
- corriger les erreurs,
- finaliser l’application.

---
