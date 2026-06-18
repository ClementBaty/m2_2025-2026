import pandas as pd
import matplotlib.pyplot as plt
import ast



def load_signal_csv(file_path):
    """
    Charge un signal depuis un CSV de manière robuste.

    Recherche automatiquement :
    - une colonne nommée samples
    - une colonne nommée signal
    - sinon la première colonne disponible

    Retour :
        list[float] ou None
    """

    try:
        df = pd.read_csv(file_path)
        print(df.head())
        print(df.columns)
        print(df.shape)
        print("\nColonnes détectées :")
        print(list(df.columns))

        print("\nPremières lignes :")
        print(df.head())
    except FileNotFoundError:
        print(f"Erreur : fichier introuvable -> {file_path}")
        return None

    except Exception as e:
        print(f"Erreur de lecture CSV : {e}")
        return None

    if df.empty:
        print("Erreur : le fichier est vide.")
        return None

    # -----------------------------
    # Recherche automatique colonne
    # -----------------------------

    signal_column = None

    candidate_names = [
        "samples",
        "signal",
        "data",
        "audio",
        "values"
    ]

    for col in df.columns:
        if col.lower() in candidate_names:
            signal_column = col
            break

    # Si aucune colonne reconnue,
    # prendre la première colonne
    if signal_column is None:
        signal_column = df.columns[0]

    print(f"Colonne détectée : {signal_column}")

    # -----------------------------
    # Recherche première ligne valide
    # -----------------------------

    signal = None

    for value in df[signal_column]:

        if pd.isna(value):
            continue

        # Cas 1 : liste Python stockée en texte
        try:
            signal = ast.literal_eval(str(value))

            if isinstance(signal, list):
                break

        except (ValueError, SyntaxError):
            pass

        # Cas 2 : valeurs séparées par des virgules
        try:
            signal = [
                float(x.strip())
                for x in str(value).split(",")
            ]

            break

        except ValueError:
            pass

    # -----------------------------
    # Vérification finale
    # -----------------------------

    if signal is None:
        print("Aucun signal valide trouvé.")
        return None

    try:
        signal = [float(x) for x in signal]
    except Exception:
        print("Le signal trouvé n'est pas numérique.")
        return None

    print(f"Signal chargé : {len(signal)} échantillons")

    return signal

signal = load_signal_csv("signal_raw(1).csv")

if signal is not None:

    plt.figure(figsize=(10, 4))

    plt.plot(signal)

    plt.title("Signal chargé depuis Groupe A")
    plt.xlabel("Échantillons")
    plt.ylabel("Amplitude")

    plt.grid(True)

    plt.show()
    
