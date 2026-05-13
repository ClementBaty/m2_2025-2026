**Groupe A : Silvestre SIMON, Tom BOTTAZZINI,BETTAOUI Manal , GRAPIN Alex**

**Groupe B : ALI Elian, BACAR Nadjilat, KABASELE TSHIANDA Deogracias, OUATTARA Hassan Nadien**  

**Groupe C : HAOUCHE El Aline, THAMMAVONG Aliyadeth, FODING MASSAOUOP Alexandra Laure, TEP Noelly**

**Groupe D : SIDORKIEWICZ Szymon, DIONG Mame, THIAM Sokhna, Ouail Kassa BAGHDOUCHE**

**Groupe E : Mizeb Abdelmouncif, Ulrich MEYEHOU , Samia FASSOULI, Hania KOULACHE (ABS), Zakaria BOUZIANE**

**Groupe F : LATORRE Xavier, ROUX Quentin, BAUDET Nathan, FORNER Romain**



# **GROUPE D:**

## Entrées

Exemple d'entrée : features.json/csv: 

&#x09;\*Spectre de fréquence (liste de valeurs).

&#x09;\*Statistiques calculées.

&#x09;\*Motifs détectés (ex : "peaks": \[100, 200, 300]).





Le but est d'en déduire la nature du signal avec un dégré de certitude à partir des caractéristiques avancés fournis par le **GROUPE C : Noelly, Amine, Alexandra, Ali.**



## Sorties:

###### Fichiers livrables pour **GROUPE E: Moncef, Ulrisch, Samia, Zakaria**: 

&#x09;\*Code Python extract\_from\_signal.py pour le traitement avancé

&#x09;\*Fichier features.csv/json

&#x09;\*Fichier expliquant les outils et calculs utilisés



###### Fichiers à ajouter dans le projet final pour le groupe:

**\***Code source commenté et documenté (plusieurs fichiers coordonnés par le document noté dans la description de chaque modules).

**\***Fichiers de sortie normalisés (JSON/CSV).

**\***Scripts de validation OU document d’explication selon groupes.

**\***Un README\_X.md expliquant :

&#x09;Le rôle du module.

&#x09;Les entrées/sorties attendues.

&#x09;Comment tester le module.

&#x09;La répartition des tâches effectuée (pas le détail les grandes lignes)

**\***Tout autre document permettant de mieux comprendre le travail fourni



###### Fichiers livrables par personne:

**\***Historique GIT personnel (pas seulement les commits sur la branche D)

**\***Historique des interactions IA (cf détails dans le cours)

**\***Choix technologiques, difficultés et points d’appui

**\***Avis critique sur son travail

→ Le format est libre pour cette partie.



## Règles internes au groupe

### Entêtes COMMIT:

A mettre impérativement dans chaque commit



\[CREATE] : Ajout d’un nouveau fichier, module ou fonctionnalité

\[ADD]    : Ajout d’un élément dans un fichier existant

\[MODIF]  : Modification d’un fichier existant

\[FIX]    : Correction d’un bug

\[WIP]    : Travail en cours, commit temporaire

\[DEL]    : Suppression d’un fichier, d’une fonction ou d’un bloc de code

\[RENAME] : Renommage d’un fichier, dossier, variable ou fonction

\[MOVE]   : Déplacement d’un fichier ou dossier

\[MERGE]  : Fusion de branches

\[REFACTOR] : Réorganisation du code sans changer son comportement

\[DOC]    : Ajout ou modification de documentation

\[TEST]   : Ajout ou modification de tests

\[CONFIG] : Modification de configuration

\[INIT]   : Initialisation du projet

\[UPDATE] : Mise à jour de dépendances, librairies ou ressources

\[HOTFIX] : Correction urgente

\[CLEAN]  : Nettoyage du code, suppression de commentaires inutiles, fichiers temporaires

\[OPTIM]  : Optimisation des performances



### Réglés de code à respecter (noté):

#### Utiliser PEPs 8 "Orthographe du code":

* Une ligne sautée ne contient pas de caractères (espaces ou autres)
* La dernière ligne du fichier python est une ligne vide
* Les indentations sont des multiples de 4 espaces (pas de tabulations)
* Il faut 1 espace autour de chaque opérateur mathématiques
* Les : sont collés (def clement() :)
* Deux lignes sont sautées après la définition d’une classe
* La documentation utilise les """
* CONSTANTES, MaClasse, fonction

Dans Spyder, activez l’analyseur de syntaxe dans :

Outils->Préférences->Complétion et Linting->Onglet « Style du code »

Cochez « Activez le linting de style de code » 



#### Documenter le code:

Il est important de documenter une fonction pour expliquer :

ce que fait cette fonction

ce qu’elle renvoie

ce qu’elle attend

La documentation se fait à l’aide des triples guillemets « """ »



def cube(x):

&#x09;"""

&#x09;prend un nombre entier et renvoie son cube

&#x09;"""

&#x09;return x\*\*3



Il existe des outils pour générer des documentation complètes.

* Sphinx : extraction, mise en page et génération de pages HTML
* PyCharm : pré-remplissage du bloc de documentation



