import ctypes
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QMainWindow

from gui.task_progress_screen import Task_Progress_Screen
from gui.task_selection_screen import Task_Selection_Screen
from src_1.gui.customization.load_font import load_font

class Main_Screen(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        # Create program name
        program_name = "Immutable X Bot "
        program_version = "0.1"

        # Set Name Of Program
        self.setWindowTitle(program_name + program_version)

        # change program icon
        #self.setWindowIcon(QIcon(str(self.file_handler.icon_png_path)))

        # change Font
        # load_font(self.file_handler.used_font_path)
        # self.setFont(QFont("Eurostile LT Std", 18))
        # heading_font = QFont("Eurostile LT Std", 18, weight=QFont.Bold)

        # change taskbar icon
        myappid = program_name + program_version  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # Set name of Window (Starting x, starting y, width, height
        self.setGeometry(180, 180, 720, 720)

        # Add Central Widget
        task_selection_screen = Task_Selection_Screen()
        self.setCentralWidget(task_selection_screen)
        task_selection_screen.observer = self


    def update(self, type, par1):

        if type == "task_selection_screen":
            task_progress_screen = Task_Progress_Screen()
            task_progress_screen.observer = self
            self.setCentralWidget(task_progress_screen)
            task_progress_screen.initUI(par1)

        elif type == "task_progress_screen":
            task_selection_screen = Task_Selection_Screen()
            self.setCentralWidget(task_selection_screen)
            task_selection_screen.observer = self
