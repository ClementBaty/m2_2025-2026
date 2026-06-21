# Fichier README du GROUPE F

Le groupe de travail est composé de 4 personnes :

* Quentin ROUX
* Romain FORNER
* Nathan BAUDET
* Xavier LATORRE

Nous avons réparti le travail en différentes tâches :

* 2 personnes se sont occupées des interfaces ;
* 2 personnes se sont occupées du code reliant les interfaces entre elles.

Réalisation de l’interface 1 : récupération du fichier, choix des données à afficher, paramétrage de l’affichage (bouton Échap, exécution, etc.) et vérification visuelle des données.

Réalisation de l’interface 2 : réalisation de l’affichage des graphiques.

Gestion des interactions entre les différents modules.

Nous utilisons la convention « F_ » afin d’identifier nos fichiers par rapport à ceux des autres groupes.

# Explication du programme

## Architecture du programme

Comme indiqué précédemment, nous avons nommé tous nos fichiers avec le préfixe `F_`.

Vous retrouverez 3 dossiers :

* `F_Code` : dossier contenant le code ;
* `F_Ui` : dossier contenant les interfaces au format `.ui` ;
* `F_plots_test` : dossier contenant les images et documents de test.

### Dans le dossier `F_Code`

`F_0` correspond aux fichiers communs aux différentes interfaces (structures de variables et fonctions communes).

`F_1` correspond à l’interface 1, `F_2` à l’interface 2, etc.

Pour les fichiers du type `F_1_A_...`, la numérotation par lettre est utilisée :

* `A` correspond toujours au fichier contenant la déclaration de la classe de l’interface ;
* les lettres suivantes correspondent aux fonctions ou classes annexes utilisées dans cette interface.

### Dans le dossier `F_Ui`

L’organisation est identique à celle du dossier `F_Code` :

* `F_Interface_1_Selection.ui` : interface 1 (sélection des données) ;
* `F_Interface_2_Affichage.ui` : interface 2 (affichage des courbes).

Si vous souhaitez faire des tests, nous vous laissons les deux fichiers `F_analysis_test.csv` et `F_analysis_test.json`.

Il vous suffira d’en sélectionner un dans le bandeau de sélection.

