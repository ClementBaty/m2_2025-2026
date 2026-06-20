"""
Lanceur principal — Groupe D.

Szymon, Mame, Sokhna, Ouail — M2 T3I ALTERNANCE 2026

Point d'entrée du classificateur de type de fichier. Ce fichier se contente
de fixer l'identité applicative Windows (pour l'icône de la barre des tâches)
puis de démarrer l'interface définie dans :mod:`gui`. Toute la logique métier
se trouve dans :mod:`classification_backend`.

Lancement : ``python traitements.py``
"""

import ctypes

import gui


def main() -> None:
    """
    Configure l'application puis lance l'interface graphique.

    :returns: ``None``.
    """
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "groupeD.filetypeclassifier"
        )
    except (AttributeError, OSError):
        # Hors Windows, cet appel n'existe pas : on l'ignore proprement.
        pass

    gui.launch()


if __name__ == "__main__":
    main()
