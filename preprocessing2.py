import csv
import matplotlib.pyplot as plt
import pandas as pd
import ast

with open('signal_raw_bruite.csv') as f:
    r = csv.reader(f)  # ',' est le séparateur
    for l in r:
        print(l)  # chaque ligne est une liste de valeurs      
        




# Charger le fichier CSV
df = pd.read_csv("signal_raw_bruite.csv")

# Convertir la colonne "samples" en liste Python
samples = ast.literal_eval(df.loc[0, "samples"])

# Afficher le signal
plt.figure(figsize=(10, 4))
plt.plot(samples)

# Titres et axes
plt.title("Signal audio bruité")
plt.xlabel("Échantillons")
plt.ylabel("Amplitude")

# Grille
plt.grid(True)

# Affichage
plt.show()