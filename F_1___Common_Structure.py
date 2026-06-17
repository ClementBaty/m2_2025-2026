from PyQt5.QtWidgets import QMainWindow


class COMMONCLASS(QMainWindow):
    def go_to(self, nom_fenetre):
        self.fenetres[nom_fenetre].show()
        self.hide()

    def init_voyant(self, widget, taille=20, forme="rond", couleur="red"):
        widget.setFixedSize(taille, taille)

        radius = taille // 2 if forme == "rond" else 0
        widget.setProperty("radius", radius)

        widget.setStyleSheet(f"""
            background-color: {couleur};
            border: 2px solid black;
            border-radius: {radius}px;
        """)

    def set_voyant_color(self, widget, couleur):
        radius = widget.property("radius")

        widget.setStyleSheet(f"""
            background-color: {couleur};
            border: 2px solid black;
            border-radius: {radius}px;
        """)
class COMONVAR:
    def __init__(self):
        self.chemin = "analysis.csv"

        self.analysis_init()

    def analysis_init(self):
        """
        Valeur initial pour les variables extraite du fichier analysis
        """
        self.sample_id = None
        self.label = ""
        self.confidence = 0
        self.fft_plot_path = ""
        self.time_series_plot_path = ""
        self.is_anomaly = None
        self.anomaly_reason = ""