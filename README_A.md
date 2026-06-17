\# Projet M2 — Groupe A



Nous sommes le groupe A.

Notre objectif est d’acquérir et d'extraire les paramètres d'un signal d’entrée en format CSV.

Et de générer un fichier de sortie qui sera transmis au groupe B.





\# Fichier d’entrée

&#x09;Le fichier d'entrée est de Type CSV.

&#x09;La première colonne le temps, l'instant ou la donnée a étais enregistrais.

&#x09;La deuxième colonne la donnée



&#x09;La Première ligne est une en tête.



&#x09;EXEMPLE:

&#x09;t,x

&#x09;0.0,4.366025403784439

&#x09;0.0001220703125,3.6760321842572776

&#x09;0.000244140625,2.693626153693505



\# Fichier de sortie

&#x09;Le fichier de sortie est un fichier au format CSV généré automatiquement par l'application.

&#x09;La première ligne correspond à l'en-tête.

&#x09;Les colonnes, dans l'ordre, sont :

&#x20;   		timestamp

&#x20;   		signal\_type

&#x20;   		signal\_source

&#x20;   		sample\_rate

&#x20;   		duration

&#x20;   		sample\_index

&#x20;   		time

&#x20;   		samples



&#x09;Exemple :



&#x09;	timestamp           signal\_type  signal\_source  sample\_rate  duration  sample\_index  time    samples

&#x09;	2026-06-16T14:24:46 CSV          micro          8192         0.4999    0             0.0     4.366

&#x09;	2026-06-16T14:24:46 CSV          micro          8192         0.4999    1             0.0001  3.676

&#x09;	2026-06-16T14:24:46 CSV          micro          8192         0.4999    2             0.0002  2.6936







\## Utilisation du projet

&#x09;1. Exécuter le fichier "main.py".



&#x09;2. Ajouter un fichier d'entrée :

&#x20;  		- Cliquer sur le bouton "...".

&#x20;  		- Sélectionner le fichier CSV à analyser.

&#x20; 		- Le chemin du fichier apparaît alors dans la zone "Lien".



&#x09;3. Compléter les informations relatives au fichier :

&#x20; 		- "Type de signal"

&#x20;  		- "Source"



&#x09;4. Cliquer sur le bouton "Générer".



&#x09;5. Résultats :

&#x20;  		- Les paramètres extraits du fichier sont affichés dans l'interface.

&#x20;  		- Le fichier de sortie est généré automatiquement sous le nom "Output\_GroupeA.csv".





\# Auteurs

&#x09;- Manal BETTAOUI 	Responsable de l'interface

&#x09;- Alex GRAPIN		Responsable de la génération du fichier de sortie

&#x09;- Simon SILVESTRE	Responsable de l'extraction des informations

&#x09;- Tom BOTTAZZINI	Responsable de l'interconnexion et support





\# Technologies utilisées

&#x09;Python 3

&#x09;PyQt5

&#x09;NumPy

&#x09;SciPy

&#x09;Pandas





\# Contraintes du projet

&#x09;Architecture modulaire

&#x09;Programmation orientée objet (POO)

&#x09;Documentation du code

&#x09;Respect des conventions PEP8 et PEP257

&#x09;Utilisation de Git pour le versionnement

&#x09;Utilisation raisonnée de l’IA (Vibe Coding interdit)

