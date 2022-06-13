import sys

from PyQt5.QtWidgets import QApplication

from gui.main_screen import Main_Screen


class Application():

    def __init__(self):
        app = QApplication(sys.argv)
        main_screen = Main_Screen()
        main_screen.show()
        sys.exit(app.exec_())
