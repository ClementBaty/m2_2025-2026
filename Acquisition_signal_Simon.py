import datetime # Import nécessaire pour le timestamp

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

# --- ÉTAPE 2 : CALCUL DES PROPRIÉTÉS DU SIGNAL ---

# 1. Liste des échantillons (données)
samples = x

# On s'assure qu'il y a au moins 2 points pour pouvoir faire des calculs
if len(t) >= 2:
    # 2. Taux d'échantillonnage (en Hz)
    dt = t[1] - t[0] # Période d'échantillonnage
    samplerate = round(1.0 / dt) # 1 / dt donne la fréquence. "round()" permet d'arrondir à un entier (ex: 8192)

    # 3. Durée du signal (en secondes)
    duration = t[-1] - t[0] # t[-1] permet de récupérer le dernier élément de la liste t
else:
    samplerate = 0
    duration = 0

# 4. Timestamp (Horodatage de l'extraction)
# datetime.now() récupère la date/heure de ton PC
# .replace(microsecond=0) permet de ne pas afficher les microsecondes
# .isoformat() la formate comme tu le souhaites (ex: 2026-05-13T15:55:00)
timestamp = datetime.datetime.now().replace(microsecond=0).isoformat()


# --- AFFICHAGE POUR VÉRIFIER QUE TOUT FONCTIONNE ---
print(f"Taux d'échantillonnage (samplerate) : {samplerate} Hz")
print(f"Durée du signal (duration) : {duration} s")
print(f"Timestamp : {timestamp}")
print(f"Nombre d'échantillons : {len(samples)}")
print(f"Aperçu des 5 premiers samples : {samples[:5]}")