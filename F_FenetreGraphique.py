from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow
from PyQt5.uic import loadUi
import sys

class Fenetregraphique(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi(r"F_Ui\F_graph_window.ui", self)

        self.F_quit_button.clicked.connect(self.close)