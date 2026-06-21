Le groupe de travail est composé de 4 personnes.
- Quentin ROUX
- Romain FORNER
- Nathan BAUDET
- Xavier LATORRE

Nous avons réparti le travail en différentes tâches :
- 2 personnes se sont occuper des interfaces
- 2 personnes se sont occuper du codes en qui relie les interfaces entre elle.

Réalisation de l’interface 1 : récupération du fichier, choix des données à afficher, paramétrage de l’affichage (bouton échap, exécution, etc.) et vérification visuelle des données.

Réalisation de l’interface 2 : réalisation de l’affichage des graphiques.

Gestion des interactions entre les différents modules.

Nous utiliserons la convention « F_ » afin d’identifier nos fichiers par rapport à ceux des autres groupes.

# Explication du programme

## l'architecture du programme

Comme dit précédemment, nous avons nommé tous nos fichiers F_... 

vous retrouverez 3 dossier :
- F_Code : dossier contenant les codes
- F_Ui : dossier contenant les interface au format .ui
- F_plots_test : dossier contenant les images  et document de test

### dans le dossier F_Code :

F_0 correspond aux fichiers commun aux différente interfaces. (structure de variables et structure de fonction)

F_1 correspond à l'interfaces 1, F_2 à l'inteface 2...

F_1_A_  viens enssuite la numerotation par lettre,

- A = correspont toujour au fichier contenant la déclaration de la class interface 
- ... = les lettres suivante corresponde au fonction ou class annex utiliser dans cette interface.
### dans le dossier F_Ui :
l'organisation est identique a celle de F_Code;
- F_Interface_1_Selection.ui = Interface 1 (selection des données)
- FF_Interface_2_Affichage.ui = interface 2 (affichage des coubes)
## extraction du fichier