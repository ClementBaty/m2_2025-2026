import pandas as pd
import matplotlib.pyplot as plt
import ast

df = pd.read_csv("signal_raw_bruite.csv")

print("Colonnes trouvées :", df.columns.tolist())

if "samples" in df.columns:
    y = ast.literal_eval(str(df.loc[0, "samples"]))
    x = range(len(y))

elif len(df.columns) >= 2:
    x = df.iloc[:, 0]
    y = df.iloc[:, 1]

else:
    y = df.iloc[:, 0]
    x = range(len(y))

plt.figure(figsize=(10, 4))
plt.plot(x, y)

plt.title("Signal")
plt.xlabel("Temps / Échantillons")
plt.ylabel("Amplitude")
plt.grid(True)

plt.show()