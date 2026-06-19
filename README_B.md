## ***RAPPORT DE PROJET : PRÉTRAITEMENT DES SIGNAUX \& EXTRACTION DE CARACTÉRISTIQUES***





Branche B —> Groupe de Programmation

&#x20;



Membres de l'équipe : ALI Elian, BACAR Nadjilat, OUATTARA Nadien, KABASELE TSHIANDA Deogracias



&#x20;

Environnement : Python (NumPy, SciPy, Matplotlib) \& Interface Graphique (GUI)



&#x20;

1\. Contexte du Projet et Rôle de la Branche B



Notre projet s’intègre dans un workflow global de traitement de signal divisé en 6 étapes successives. L’idée générale est de prendre un signal brut qui sort d'un capteur (souvent très bruité) et de le transformer en données propres et exploitables pour faire de l'analyse prédictive.



Dans cette chaîne de travail, les tâches sont réparties entre trois grands groupes :



·       En entrée (Groupe A) : Ils s'occupent de la récupération et de l'envoi des signaux bruts.



·       Notre rôle (Branche B) : On récupère le signal du Groupe A, on le nettoie (suppression du bruit), on extrait les caractéristiques clés et on standardise le tout.



·       En sortie (Groupe C) : Ils récupèrent nos données propres pour faire tourner les modèles de prédiction finaux.



&#x20;



2\. Objectifs de la Partie B



Pour valider le cahier des charges, notre groupe s'est fixé trois gros objectifs :



1\.  Le Nettoyage : Supprimer le bruit de fond parasite sur le signal brut et normaliser les amplitudes pour qu'elles soient exploitables.



2\.  L'Extraction de caractéristiques : Trouver automatiquement l'amplitude maximale et la fréquence dominante du signal après filtrage.



3\.  La Standardisation : Exporter proprement toutes ces données dans un format universel pour que le Groupe C puisse les lire directement sans bug.



&#x20;



3\. Choix Technologiques et Répartition des Tâches



On a choisi de coder l'ensemble de l'application en Python, car c'est le langage le plus adapté pour le traitement de données et la création rapide d'interfaces graphiques.



Pour avancer efficacement, on s'est réparti le travail comme suit :



·       ALI Elian : S'est occupé de la partie traitement pur, du choix des filtres de nettoyage.



·       BACAR Nadjilat : A géré toute la partie gestion du signal (chargement des fichiers d'entrée), l'affichage des courbes et la documentation du code. Ainsi que de la création de la routine d'exportation en CSV.



·       OUATTARA Nadien : A conçu l'architecture de l'interface graphique et s'est chargée de lier l'interface aux fonctions de calcul et s'est assuré que la liaison entre les codes de tout le monde fonctionnait sans erreur.



·       KABASELE Deogracias : A travaillé en binôme sur l'interface graphique et s'est assuré de la gestion de la branche B sur git en supprimant les programmes avant le pull request.



&#x20;



4\. Structure de notre Programme (Pipeline)



L'application fonctionne comme une chaîne de traitement séquentielle divisée en 4 blocs principaux, tous gérés par notre script principal (main.py) :



·       Prog Chargement signal : Module qui importe le fichier brut et vérifie que les données ne sont pas corrompues.



·       Prog Filtre : C'est le cœur mathématique du projet. Il applique les filtres numériques pour enlever les fréquences parasites et lisser la courbe.



·       Prog Interface graphique : Une interface interactive qui permet à l'utilisateur de charger son fichier et de voir directement le résultat sur un écran.



·       Prog Combiné (main) : Il rassemble tous les modules, calcule l'amplitude max et la fréquence dominante, et gère l'affichage final.



&#x20;



Le Fichier de Sortie : En fin de traitement, le programme génère automatiquement un fichier nommé signal\_filtered.csv. Ce fichier contient le signal propre (les données de l'amplitude filtrée en fonction du temps) ainsi que les deux caractéristiques extraites : l'amplitude max et la fréquence dominante.



&#x20;



5\. Déroulement du Projet et Évolution (Versions 1 à 3)



Pour éviter de tout coder d'un coup et de se retrouver bloqués, on a fonctionné par itérations avec trois versions successives :



·       Version 1 : On a d'abord codé les algorithmes de filtrage bruts et les calculs de caractéristiques en ligne de commande. Le but était juste de vérifier que les maths derrière le code étaient justes.



·       Version 2 (Intégration GUI) : On a greffé l'interface graphique sur nos scripts de la V1. À ce stade, on pouvait charger un signal, cliquer sur un bouton et afficher la visualisation finale (courbe propre).



&#x20;



·       Version 3/4 (Optimisation et Livraison) : C'est la version finale. On a peaufiné les filtres pour qu'ils soient plus précis et on a sécurisé l'export CSV pour qu'il s'intègre parfaitement avec les outils du Groupe C.



&#x20;



&#x20;

###### **Résultat final** : On arrive à sortir un signal parfaitement propre, sans parasites, prêt à être envoyé pour l'analyse prédictive. Le code est commenté, stable et répond aux attentes du sujet.

