"""
Moteur de classification — Groupe D.

Szymon, Mame, Sokhna, Ouail — M2 T3I ALTERNANCE 2026

Ce module regroupe toute la logique « back-end » du classificateur de type de
fichier : gestion de la base de données de référence, sélection automatique des
indicateurs les plus pertinents (Fisher Score + SBS), classification par les
plus proches voisins (KNN) et classification algorithmique par seuils, ainsi
que l'export du résultat pour le Groupe E.

Aucune dépendance à l'interface graphique : ce fichier peut être testé seul.
"""

import os
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from mlxtend.feature_selection import SequentialFeatureSelector as SFS

# ---------------------------------------------------------------------------
# Constantes configurables
# ---------------------------------------------------------------------------

MAX_CATEGORIES = 7

#: Nombre minimal de catégories pour considérer la base comme complète.
MIN_CATEGORIES = 3

#: Nombre minimal d'échantillons (lignes) par catégorie dans la référence.
MIN_SAMPLES_PER_CATEGORY = 5

FEATURE_COLUMNS = [
    "fft_magnitude_0", "fft_magnitude_1", "fft_magnitude_2",
    "fft_frequency_0", "fft_frequency_1", "fft_frequency_2",
    "spectral_centroid", "mean", "std_dev", "kurtosis",
    "skewness", "rms",
    "peak_index_0", "peak_index_1", "peak_index_2",
    "peak_amplitude_0", "peak_amplitude_1", "peak_amplitude_2",
]

# ---------------------------------------------------------------------------
# Constantes de chemins
# ---------------------------------------------------------------------------

ROOT_DIR = Path(__file__).parent
SAMPLE_DIR = ROOT_DIR / "SAMPLE"
DATABASE_DIR = ROOT_DIR / "DATABASE"
REFERENCE_FILE = DATABASE_DIR / "reference.csv"
DEFAULT_SAMPLE = SAMPLE_DIR / "features.csv"
EXPORT_FILE = ROOT_DIR / "processed_data.csv"
ICON_FILE = ROOT_DIR / "icon.png"
LOADING_FILE = ROOT_DIR / "loading.png"

# ---------------------------------------------------------------------------
# Journal applicatif
# ---------------------------------------------------------------------------

_journal_callbacks = []


def register_journal(callback) -> None:
    """
    Enregistre une fonction de rappel appelée à chaque message de journal.

    :param callback: fonction prenant une chaîne de caractères en argument.
        Typiquement, l'onglet Journal de l'interface y branche l'ajout d'une
        ligne dans sa zone de texte.
    :returns: ``None``.
    """
    if callback not in _journal_callbacks:
        _journal_callbacks.append(callback)


def journal(message: str) -> None:
    """
    Émet un message vers la console et vers tous les abonnés du journal.

    :param message: texte à journaliser (information de traitement, mise à
        jour de la base, indicateurs retenus, message de débogage…).
    :returns: ``None``.
    """
    print(message)
    for callback in list(_journal_callbacks):
        try:
            callback(message)
        except Exception as exc:  # un abonné défaillant ne doit pas tout casser
            print(f"Journal callback error: {exc}")


# ---------------------------------------------------------------------------
# Gestion de la base de données de référence
# ---------------------------------------------------------------------------


def get_category_folders() -> list:
    """
    Liste les catégories de la base, c'est-à-dire les sous-dossiers de DATABASE.

    :returns: liste triée des noms de sous-dossiers présents dans
        ``DATABASE_DIR``. Liste vide si le dossier n'existe pas.
    """
    if not DATABASE_DIR.exists():
        return []
    return sorted(
        entry.name
        for entry in DATABASE_DIR.iterdir()
        if entry.is_dir()
    )


def build_reference() -> None:
    """
    Reconstruit le fichier ``DATABASE/reference.csv`` à partir des sous-dossiers.

    Parcourt chaque catégorie, lit tous les fichiers ``*features.csv`` qu'elle
    contient, leur ajoute la colonne ``label`` (nom de la catégorie en
    majuscules) puis concatène le tout dans le fichier de référence.

    :returns: ``None``. Écrit le fichier ``REFERENCE_FILE`` sur le disque.
    """
    frames = []
    for category in get_category_folders():
        cat_dir = DATABASE_DIR / category
        for csv_file in sorted(cat_dir.glob("*features.csv")):
            try:
                df = pd.read_csv(csv_file)
                df["label"] = category.upper()
                frames.append(df)
            except Exception as exc:
                journal(f"Avertissement : lecture impossible de {csv_file} : {exc}")

    if frames:
        combined = pd.concat(frames, ignore_index=True)
    else:
        combined = pd.DataFrame(columns=["label"] + FEATURE_COLUMNS)

    combined.to_csv(REFERENCE_FILE, index=False)
    journal(
        f"Base de référence actualisée : {len(combined)} échantillon(s), "
        f"{len(get_category_folders())} catégorie(s)."
    )
    # On invalide le cache de sélection : la base a changé.
    _SELECTION_CACHE["mtime"] = None


def add_category(name: str) -> str:
    """
    Crée une nouvelle catégorie (sous-dossier) dans la base de données.

    :param name: nom de la catégorie souhaitée (espaces et casse normalisés).
    :returns: le nom normalisé (majuscules) effectivement créé.
    :raises ValueError: si le nom est vide, dépasse 10 caractères, ou si le
        nombre maximal de catégories est déjà atteint.
    """
    name = name.strip().upper()
    if not name:
        raise ValueError("Le nom de la catégorie est vide.")
    if len(name) > 10:
        raise ValueError("Le nom est limité à 10 caractères.")
    if len(get_category_folders()) >= MAX_CATEGORIES and name not in get_category_folders():
        raise ValueError(f"Limite de {MAX_CATEGORIES} catégories atteinte.")
    os.makedirs(DATABASE_DIR / name, exist_ok=True)
    journal(f"Catégorie « {name} » ajoutée à la base.")
    return name


def add_reference_file(source_path: str, category: str) -> Path:
    """
    Copie un fichier features.csv dans une catégorie puis reconstruit la référence.

    :param source_path: chemin du fichier CSV à importer.
    :param category: nom de la catégorie de destination.
    :returns: le chemin de destination du fichier copié.
    :raises ValueError: si la catégorie n'existe pas.
    """
    cat_dir = DATABASE_DIR / category
    if not cat_dir.exists():
        raise ValueError(f"La catégorie « {category} » n'existe pas.")
    existing = list(cat_dir.glob("*features.csv"))
    index = len(existing) + 1
    dest = cat_dir / f"{index}features.csv"
    shutil.copy2(source_path, dest)
    journal(f"Fichier importé dans « {category} » : {dest.name}")
    build_reference()
    return dest


def count_samples_per_category() -> dict:
    """
    Compte le nombre d'échantillons (lignes) par catégorie dans la référence.

    :returns: dictionnaire ``{catégorie: nombre_de_lignes}``. Les catégories
        sans fichier de référence apparaissent avec la valeur 0.
    """
    counts = {cat.upper(): 0 for cat in get_category_folders()}
    if REFERENCE_FILE.exists():
        ref_df = pd.read_csv(REFERENCE_FILE)
        if "label" in ref_df.columns:
            for label, group in ref_df.groupby("label"):
                counts[str(label).upper()] = len(group)
    return counts


def database_status() -> dict:
    """
    Évalue la complétude de la base de données de référence.

    Une base est jugée « complète » si elle contient au moins
    ``MIN_CATEGORIES`` catégories et au moins ``MIN_SAMPLES_PER_CATEGORY``
    échantillons dans chacune d'elles.

    :returns: dictionnaire contenant :
        ``complete`` (bool), ``n_categories`` (int),
        ``counts`` (dict catégorie -> nb lignes),
        ``deficient`` (liste des catégories sous le seuil),
        ``deficient_path`` (chemin à ouvrir si la base est incomplète).
    """
    counts = count_samples_per_category()
    n_categories = len(counts)
    deficient = [c for c, n in counts.items() if n < MIN_SAMPLES_PER_CATEGORY]

    complete = n_categories >= MIN_CATEGORIES and not deficient

    # Chemin à proposer si la base est incomplète : dossier de la première
    # catégorie déficiente, sinon le dossier DATABASE lui-même.
    if deficient:
        deficient_path = DATABASE_DIR / deficient[0]
    else:
        deficient_path = DATABASE_DIR

    return {
        "complete": complete,
        "n_categories": n_categories,
        "counts": counts,
        "deficient": deficient,
        "deficient_path": deficient_path,
    }


# ---------------------------------------------------------------------------
# Sélection automatique des indicateurs (Fisher Score + SBS)
# ---------------------------------------------------------------------------

#: Cache de sélection, invalidé dès que la référence change.
_SELECTION_CACHE = {"mtime": None, "columns": None, "info": None}


def fisher_score(features: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """
    Calcule le Fisher Score de chaque indicateur (méthode de filtrage).

    Le Fisher Score favorise les indicateurs dont les moyennes inter-classes
    sont très écartées et dont la variance intra-classe est faible :
    ``score = somme(n_c * (m_c - m)^2) / somme(n_c * var_c)``.

    :param features: tableau ``(n_échantillons, n_indicateurs)`` déjà normalisé.
    :param labels: tableau ``(n_échantillons,)`` des étiquettes de classe.
    :returns: tableau ``(n_indicateurs,)`` des scores de Fisher.
    """
    scores = []
    global_mean = features.mean(axis=0)
    for j in range(features.shape[1]):
        numerator = 0.0
        denominator = 0.0
        for cls in np.unique(labels):
            column = features[labels == cls, j]
            numerator += len(column) * (column.mean() - global_mean[j]) ** 2
            denominator += len(column) * column.var()
        scores.append(numerator / denominator if denominator > 0 else 0.0)
    return np.array(scores)


def select_features(ref_df: pd.DataFrame, available_cols: list) -> tuple:
    """
    Détermine les indicateurs les plus pertinents de la base courante.

    La sélection combine deux approches demandées :
    1. **Fisher Score** : pré-classement des indicateurs par pouvoir
       discriminant (filtrage).
    2. **SBS** (Sequential Backward Selection) enveloppant un KNN : élagage
       descendant qui retient automatiquement, par validation croisée, le plus
       petit sous-ensemble proche du meilleur score (mode « parsimonious »).

    Le résultat est mis en cache tant que ``reference.csv`` n'est pas modifié.

    :param ref_df: DataFrame de la base de référence (avec colonne ``label``).
    :param available_cols: indicateurs réellement disponibles dans la base.
    :returns: couple ``(colonnes_retenues, info)`` où ``info`` est un
        dictionnaire décrivant la sélection (score, classement de Fisher…).
    """
    labels = ref_df["label"].values
    features = StandardScaler().fit_transform(ref_df[available_cols].fillna(0).values)

    # Classement par Fisher Score (utilisé en repli et pour le journal).
    f_scores = fisher_score(features, labels)
    ranking = [available_cols[i] for i in np.argsort(f_scores)[::-1]]

    n_samples = len(ref_df)
    n_classes = len(np.unique(labels))

    # SBS exige assez d'échantillons par classe pour la validation croisée.
    if n_samples < 8 or n_classes < 2:
        info = {
            "method": "Fisher Score seul (base trop petite pour le SBS)",
            "selected": ranking[:min(5, len(ranking))],
            "fisher_ranking": ranking,
            "cv_score": None,
        }
        return info["selected"], info

    cv = min(4, n_samples // n_classes)
    cv = max(2, cv)
    knn = KNeighborsClassifier(n_neighbors=min(3, n_samples - 1))
    sfs = SFS(
        knn,
        k_features="parsimonious",
        forward=False,
        floating=False,
        scoring="accuracy",
        cv=cv,
    )
    sfs.fit(features, labels)
    selected = [available_cols[i] for i in sfs.k_feature_idx_]

    info = {
        "method": f"Fisher Score + SBS (validation croisée {cv} plis)",
        "selected": selected,
        "fisher_ranking": ranking,
        "cv_score": round(float(sfs.k_score_), 3),
    }
    return selected, info


def get_selected_features(ref_df: pd.DataFrame, available_cols: list) -> tuple:
    """
    Retourne la sélection d'indicateurs, en s'appuyant sur un cache.

    :param ref_df: DataFrame de la base de référence.
    :param available_cols: indicateurs disponibles dans la base.
    :returns: couple ``(colonnes_retenues, info)`` (voir :func:`select_features`).
    """
    mtime = REFERENCE_FILE.stat().st_mtime if REFERENCE_FILE.exists() else None
    if _SELECTION_CACHE["mtime"] == mtime and _SELECTION_CACHE["columns"]:
        return _SELECTION_CACHE["columns"], _SELECTION_CACHE["info"]

    columns, info = select_features(ref_df, available_cols)
    _SELECTION_CACHE.update({"mtime": mtime, "columns": columns, "info": info})
    journal(
        f"Indicateurs retenus ({info['method']}) : {', '.join(columns)}"
        + (f" — score VC : {info['cv_score']}" if info["cv_score"] is not None else "")
    )
    return columns, info


# ---------------------------------------------------------------------------
# Classification par base de données (KNN)
# ---------------------------------------------------------------------------


def _read_first_row(filepath: str) -> pd.DataFrame:
    """
    Lit un fichier CSV et renvoie uniquement sa première ligne sous forme de DataFrame.

    :param filepath: chemin du fichier à analyser.
    :returns: DataFrame d'une seule ligne.
    :raises ValueError: si le fichier ne contient aucune ligne de données.
    """
    df = pd.read_csv(filepath)
    if df.empty:
        raise ValueError("Le fichier sélectionné ne contient aucune donnée.")
    if len(df) > 1:
        journal(f"Avertissement : {filepath} contient {len(df)} lignes ; "
                "seule la première est utilisée.")
    return df.iloc[[0]]


def classify_with_database(filepath: str) -> dict:
    """
    Classe la première ligne d'un fichier par KNN sur la base de référence.

    Le sous-ensemble d'indicateurs est d'abord choisi automatiquement
    (:func:`get_selected_features`), les données sont normalisées, puis un
    KNN attribue une classe et un degré de confiance par classe.

    :param filepath: chemin du fichier features.csv à tester.
    :returns: dictionnaire contenant ``label`` (str), ``confidence`` (float
        dans [0, 1]), ``scores`` (dict classe -> pourcentage), ``features``
        (indicateurs utilisés) et ``row`` (la ligne testée).
    :raises ValueError: si la base de référence est vide ou absente.
    """
    sample_row = _read_first_row(filepath)

    if not REFERENCE_FILE.exists():
        raise ValueError("La base est vide. Chargez d'abord des fichiers de référence.")
    ref_df = pd.read_csv(REFERENCE_FILE)
    if ref_df.empty or "label" not in ref_df.columns:
        raise ValueError("La base est vide. Chargez d'abord des fichiers de référence.")

    ref_labels = ref_df["label"].values

    available_in_ref = [c for c in FEATURE_COLUMNS if c in ref_df.columns]
    for col in available_in_ref:
        if col not in sample_row.columns:
            sample_row = sample_row.copy()
            sample_row[col] = 0.0

    # Sélection automatique des indicateurs sur la base courante.
    selected_cols, _info = get_selected_features(ref_df, available_in_ref)

    ref_features = ref_df[selected_cols].fillna(0).values
    sample_features = sample_row[selected_cols].fillna(0).values

    scaler = StandardScaler()
    ref_scaled = scaler.fit_transform(ref_features)
    sample_scaled = scaler.transform(sample_features)

    total = len(ref_scaled)
    k = max(1, 5 + total // 10)
    k = min(k, total)

    knn = KNeighborsClassifier(n_neighbors=k, metric="euclidean")
    knn.fit(ref_scaled, ref_labels)

    probabilities = knn.predict_proba(sample_scaled)[0]
    classes = knn.classes_
    scores = {
        str(cls): round(float(prob) * 100)
        for cls, prob in zip(classes, probabilities)
    }
    predicted_label = str(classes[int(np.argmax(probabilities))])
    confidence = round(float(np.max(probabilities)), 2)

    journal(f"[KNN] Type détecté : {predicted_label} "
            f"(confiance {int(confidence * 100)} %, k={k}).")

    return {
        "label": predicted_label,
        "confidence": confidence,
        "scores": scores,
        "features": selected_cols,
        "row": sample_row.iloc[0],
    }


# ---------------------------------------------------------------------------
# Classification algorithmique (par seuils, sans base de données)
# ---------------------------------------------------------------------------


def _get(row, col, default=0.0):
    """
    Lit une valeur numérique dans une ligne, avec valeur par défaut.

    :param row: ligne pandas (Series).
    :param col: nom de la colonne recherchée.
    :param default: valeur renvoyée si la colonne est absente ou illisible.
    :returns: la valeur en flottant, ou ``default``.
    """
    try:
        return float(row[col]) if col in row.index else default
    except (TypeError, ValueError):
        return default


def classify_by_rules(filepath: str) -> dict:
    """
    Classe la première ligne d'un fichier par un système de seuils fiabilisé.

    L'algorithme attribue un score continu à chacun des quatre types
    physiquement détectables (AUDIO, IMAGE, NOISE, TEXT), à partir des plages
    de valeurs observées dans la base de référence (centroïde spectral,
    écart-type, kurtosis, asymétrie, énergie RMS, amplitudes FFT). Les scores
    sont ensuite normalisés en pourcentages.

    :param filepath: chemin du fichier features.csv à tester.
    :returns: dictionnaire contenant ``label`` (str), ``confidence`` (float
        dans [0, 1]), ``scores`` (dict type -> pourcentage) et ``row``.
    :raises ValueError: si le fichier ne contient aucune ligne de données.
    """
    df = pd.read_csv(filepath)
    if df.empty:
        raise ValueError("Le fichier sélectionné ne contient aucune donnée.")
    if len(df) > 1:
        journal(f"Avertissement : {filepath} contient {len(df)} lignes ; "
                "seule la première est utilisée.")
    row = df.iloc[0]

    centroid = _get(row, "spectral_centroid")
    std_dev = _get(row, "std_dev")
    kurtosis = _get(row, "kurtosis")
    skewness = _get(row, "skewness")
    rms = _get(row, "rms")
    mag0 = _get(row, "fft_magnitude_0")

    scores = {"AUDIO": 0.0, "IMAGE": 0.0, "NOISE": 0.0, "TEXT": 0.0}

    # --- TEXT : centroïde et énergie faibles, forte asymétrie, kurtosis élevé.
    if centroid < 1300:
        scores["TEXT"] += 0.4
    if std_dev < 0.10:
        scores["TEXT"] += 0.3
    if skewness > 0.7:
        scores["TEXT"] += 0.2
    if mag0 < 150:
        scores["TEXT"] += 0.1

    # --- AUDIO : centroïde médian, écart-type modéré, magnitude FFT forte.
    if 1300 <= centroid < 3000:
        scores["AUDIO"] += 0.4
    if 0.10 <= std_dev < 0.20:
        scores["AUDIO"] += 0.3
    if mag0 > 300:
        scores["AUDIO"] += 0.2
    if skewness < 0.7:
        scores["AUDIO"] += 0.1

    # --- IMAGE : centroïde élevé, écart-type marqué, kurtosis élevé.
    if 3000 <= centroid < 5500:
        scores["IMAGE"] += 0.4
    if 0.18 <= std_dev < 0.27:
        scores["IMAGE"] += 0.3
    if kurtosis > 4.5:
        scores["IMAGE"] += 0.2
    if rms < 0.30:
        scores["IMAGE"] += 0.1

    # --- NOISE : centroïde et écart-type très élevés, kurtosis proche de 3.
    if centroid >= 3500:
        scores["NOISE"] += 0.3
    if std_dev >= 0.27:
        scores["NOISE"] += 0.4
    if 2.3 < kurtosis < 3.6:
        scores["NOISE"] += 0.2
    if rms >= 0.27:
        scores["NOISE"] += 0.1

    total = sum(scores.values()) or 1.0
    scores = {cls: round(value / total * 100) for cls, value in scores.items()}

    predicted_label = max(scores, key=scores.get)
    confidence = round(scores[predicted_label] / 100, 2)

    journal(f"[Algorithmique] Type détecté : {predicted_label} "
            f"(confiance {scores[predicted_label]} %).")

    return {
        "label": predicted_label,
        "confidence": confidence,
        "scores": scores,
        "row": row,
    }


# ---------------------------------------------------------------------------
# Export du résultat pour le Groupe E
# ---------------------------------------------------------------------------


def export_results(row, label: str, confidence: float) -> Path:
    """
    Écrit le résultat de classification dans ``processed_data.csv``.

    :param row: ligne pandas du fichier testé (contenant les indicateurs).
    :param label: type détecté.
    :param confidence: degré de confiance dans [0, 1].
    :returns: le chemin du fichier exporté.
    """
    def get_col(col):
        return row[col] if col in row.index else float("nan")

    sample_id = row["sample_id"] if "sample_id" in row.index else "sample"

    mag_cols = [c for c in ["fft_magnitude_0", "fft_magnitude_1", "fft_magnitude_2"]
                if c in row.index]
    freq_cols = [c for c in ["fft_frequency_0", "fft_frequency_1", "fft_frequency_2"]
                 if c in row.index]
    if mag_cols and freq_cols and len(mag_cols) == len(freq_cols):
        mags = [float(row[c]) for c in mag_cols]
        best_idx = int(np.argmax(mags))
        dominant_frequency_hz = float(row[freq_cols[best_idx]])
    else:
        dominant_frequency_hz = float("nan")

    energy = sum(float(row[c]) ** 2 for c in mag_cols) if mag_cols else float("nan")

    result_df = pd.DataFrame([{
        "sample_id": sample_id,
        "label": label,
        "confidence": confidence,
        "mean": get_col("mean"),
        "std_dev": get_col("std_dev"),
        "kurtosis": get_col("kurtosis"),
        "skewness": get_col("skewness"),
        "rms": get_col("rms"),
        "dominant_frequency_hz": dominant_frequency_hz,
        "energy": energy,
    }])
    result_df.to_csv(EXPORT_FILE, index=False)
    journal(f"Export réussi : {EXPORT_FILE.name}")
    return EXPORT_FILE


def ensure_directories() -> None:
    """
    Crée les dossiers SAMPLE et DATABASE s'ils n'existent pas.

    :returns: ``None``.
    """
    for directory in (SAMPLE_DIR, DATABASE_DIR):
        directory.mkdir(parents=True, exist_ok=True)
