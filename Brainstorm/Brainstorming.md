# Idées projet



Nous allons créer une simple base des données pour que notre modèle puisse s'entrainer "à vide" sur nos fichiers d'essai.

Une fois les groupes A, B et C finiront leur partie, on pourra repasser nos fichiers par leur algorithmes pour avoir un apprentissage plus propre, sur des signaux déjà traités.



On doit savoir à quelle fréquence le groupe C va échantillonner le signal pour pouvoir bien interpreter la FFT

On leur demande de nous livrer que la FFT réelle, partie sans alias **(Jusqu'à Fech/2)?**



Au début, on va classifier les fichier par 3 types: audio, image et video. Facilement deductible à partir de la FFT:

* 0-20kHz --> Fichier audio
* Pics de fréquence à 24Hz, 25Hz, 30Hz ou 60Hz --> Fichier vidéo correspondance aux FPS d'une vidéo (Frames Per Second / Images Par Seconde)
* à regarder la "fréquence spatiale", ex si on a un gradient de noir vers le blanc, on aura probablement un signal en dent de scie. Une image statique --> beaucoup des fréquences diverses mais la FFT ne resemble pas au bruit blanc (pas d'entropie proche de 1, la FFT != 1 sur tout le spectre)

**Cf. Le tableau Excel avec les fréquences caractéristiques pour les 3 fichiers**

