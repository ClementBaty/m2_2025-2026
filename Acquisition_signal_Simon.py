

filename = "U:\\Projet_prog\\Test\\m2_2025-2026\\Fichier_entree.csv" # nom du fichier a lire

t = [] # vecteur temps
x = [] # vecteur données

# --- ÉTAPE 1 : EXTRACTION DES DONNÉES ---
with open(filename, "r") as f:
    next(f)  # saute la première ligne (les en-têtes)
    for ligne in f:
        ligne = ligne.strip()  # enlever les espaces et retours à la ligne
        if not ligne: # Sécurité : ignorer les lignes vides
            continue
        valeurs = ligne.split(",")  # utiliser la virgule comme séparateur
        t.append(float(valeurs[0]))
        x.append(float(valeurs[1]))

print("t =", t)
print("x =", x)