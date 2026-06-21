from PyQt5.QtWidgets import QMainWindow


class COMMONCLASS(QMainWindow):
    """Class contenant les fonction comunes aux interfaces,
    chaque inteface erite de cette class."""
    def go_to(self, nom_fenetre):
        """fonctin de changement d'interface, toutes les interface sont créé au lancement de l'application
        puis on affiche l'interface desirer et on cache l'ancienne"""

        self.fenetres[nom_fenetre].show()
        self.hide()

    def init_voyant(self, widget, taille=20, forme="rond", couleur="red"):
        """Premet d'initiliser les widjet de type voyant (indicateur) en procedent de cette façon,
        on a des voyant qui on tous le meme style graphique."""
        widget.setFixedSize(taille, taille)

        radius = taille // 2 if forme == "rond" else 0
        widget.setProperty("radius", radius)

        widget.setStyleSheet(f"""
            background-color: {couleur};
            border: 2px solid black;
            border-radius: {radius}px;
        """)

    def set_voyant_color(self, widget, couleur):
        """permet de changer la couleur des voyants
        entréé : voyant et couleur voulue
        sortie : modification de la couleur du voyant voulue"""
        radius = widget.property("radius")

        widget.setStyleSheet(f"""
            background-color: {couleur};
            border: 2px solid black;
            border-radius: {radius}px;
        """)


class COMONVAR:
    """Classe contenant les variables comunes aux interfaces,
    permet de memoriser et de comuniquer des donné entre les interfaces"""
    def __init__(self):
        self.chemin = "analysis.csv"

        self.analysis_init()

    def analysis_init(self):
        """
        Valeur initial pour les variables extraite du fichier analysis
        permet de renitialiser facilemment les donners par un simple appel de la fonction.
        """
        self.sample_id = None
        self.label = ""
        self.confidence = 0
        self.fft_plot_path = ""
        self.time_series_plot_path = ""
        self.is_anomaly = None
        self.anomaly_reason = ""
