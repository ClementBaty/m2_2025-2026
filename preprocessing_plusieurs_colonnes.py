import pandas as pd
import matplotlib.pyplot as plt
import ast

# Charger le fichier CSV
df = pd.read_csv("signal_raw_bruite.csv")

print("Colonnes trouvées :", df.columns.tolist())

# Cas 1 : colonne "samples" contenant une liste
if "samples" in df.columns:
    samples = ast.literal_eval(str(df.loc[0, "samples"]))

# Cas 2 : une seule colonne numérique
elif len(df.columns) == 1:
    samples = df.iloc[:, 0].dropna().tolist()

# Cas 3 : plusieurs colonnes -> prend la première colonne
else:
    samples = df.iloc[:, 0].dropna().tolist()

# Affichage du signal
plt.figure(figsize=(10, 4))
plt.plot(samples)

plt.title("Signal")
plt.xlabel("Échantillons")
plt.ylabel("Amplitude")
plt.grid(True)

plt.show()

