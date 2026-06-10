from PyQt5.QtWidgets import QMainWindow


class COMMONCLASS(QMainWindow):
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