from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QWidget, QRadioButton, \
    QCheckBox, QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QButtonGroup
from PyQt5 import QtCore
from PyQt5 import QtGui

from parallel_workers.parallel_proccessing_HighLevelTask_executor import Parallel_Processing_HighLevelTask_Executor
from util.files.file_io_helper import File_IO_Helper


class Task_Progress_Screen(QWidget):

    def __init__(self):
        super().__init__()
        self.observer = None

    def initUI(self, HighLevelTask_list):

        File_IO_Helper.write_stop_parallel_processing_boolean(False)
        self.pphlte = Parallel_Processing_HighLevelTask_Executor()

        self.text_box_list = []

        self.grid = QGridLayout()

        task_progress_label = QLabel("Task Progress Screen")
        task_progress_label.setAlignment(QtCore.Qt.AlignCenter)
        self.grid.addWidget(task_progress_label, 0, 0, 1, 2)

        high_level_column_position = 0
        task_row_position = 1
        max_row_position = 1

        combined_task_list = []

        for HighLevelTask, task_list in HighLevelTask_list:
            HighLevelTask_label = QLabel(f"{HighLevelTask.name.capitalize()} Progress")
            HighLevelTask_label.setAlignment(QtCore.Qt.AlignCenter)
            self.grid.addWidget(HighLevelTask_label, task_row_position, high_level_column_position)
            task_row_position = task_row_position + 1

            new_HighLevelTask_list = []

            for task in task_list:
                task_label = QLabel(f"{task.name.capitalize()} Progress")
                task_label.setAlignment(QtCore.Qt.AlignCenter)
                self.grid.addWidget(task_label, task_row_position, high_level_column_position)
                task_row_position = task_row_position + 1

                task_text_box = QLineEdit()
                task_text_box.setReadOnly(True)
                self.grid.addWidget(task_text_box, task_row_position, high_level_column_position)
                task_row_position = task_row_position + 1

                self.text_box_list.append(task_text_box)

                new_HighLevelTask_list.append((task, task_text_box))

            combined_task_list.append((HighLevelTask, new_HighLevelTask_list))

            high_level_column_position = high_level_column_position + 1

            if task_row_position > max_row_position:
                max_row_position = task_row_position

            task_row_position = 1

        self.task_start_button = QPushButton("Start the tasks")
        self.task_start_button.clicked.connect(self.test)
        self.grid.addWidget(self.task_start_button, max_row_position, 0, 1, 2)
        max_row_position = max_row_position + 1

        self.task_stop_button = QPushButton("Stop the tasks")
        self.task_stop_button.clicked.connect(self.stop_tasks)
        self.grid.addWidget(self.task_stop_button, max_row_position, 0, 1, 2)

        self.setLayout(self.grid)

        self.combined_task_list = combined_task_list

    def test(self):
        #self.pphlte.parallel_execute_HighLevelTask(get_type="SELL", task_list=self.combined_task_list)
        for high_leveltask, task_information_list in self.combined_task_list:
            for task, line_entry in task_information_list:
                line_entry.setText("Test")


    def stop_tasks(self):
        self.notify_observer()

    def notify_observer(self, par1=None):

        File_IO_Helper.write_stop_parallel_processing_boolean(True)

        self.observer.update("task_progress_screen", par1)
