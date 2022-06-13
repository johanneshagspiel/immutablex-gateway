from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QWidget, QRadioButton, \
    QCheckBox, QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QButtonGroup
from PyQt5 import QtCore
from PyQt5 import QtGui

from objects.enums.tasks import Download_Task, Processing_Task, High_Level_Task

class Task_Preparation_Screen():

    def __init__(self):
        super().__init__()

        self.initUI()
        self.observer = None

    def initUI(self):

        self.grid = QGridLayout()

