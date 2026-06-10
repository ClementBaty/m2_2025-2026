from PyQt5.QtWidgets import QMainWindow


class COMMONCLASS(QMainWindow):
    def go_to(self, nom_fenetre):
        self.fenetres[nom_fenetre].show()
        self.hide()
    def init_voyant(self, widget, taille=20, forme="carre", couleur="red"):
        widget.setFixedSize(taille, taille)

        radius = 0
        if forme == "rond":
            radius = taille // 2

        widget.setStyleSheet(f"""
            background-color: {couleur};
            border: 2px solid black;
            border-radius: {radius}px;
        """)
    def set_voyant_color(self, widget, couleur):
        widget.setStyleSheet(f"""
            background-color: {couleur};
            border: 2px solid black;
            border-radius: 0px;
        """)
class COMONVAR:
    def __init__(self):
        self.chemin = "analysis.csv"