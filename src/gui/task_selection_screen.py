from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QWidget, QRadioButton, \
    QCheckBox, QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QButtonGroup
from PyQt5 import QtCore
from PyQt5 import QtGui

from objects.enums.tasks import Download_Task, Processing_Task, High_Level_Task


class Task_Selection_Screen(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()
        self.observer = None

    def initUI(self):

        self.grid = QGridLayout()

        task_selection_label = QLabel("Task Selection Screen")
        task_selection_label.setAlignment(QtCore.Qt.AlignCenter)
        self.grid.addWidget(task_selection_label, 0, 0, 1, 2)

        download_column_position = 0
        download_row_position = 1

        download_tasks_label = QLabel("Download Download_Task")
        download_tasks_label.setAlignment(QtCore.Qt.AlignCenter)
        self.grid.addWidget(download_tasks_label, download_row_position, download_column_position)
        download_row_position = download_row_position + 1


        download_get_type_label = QLabel("Which get_types do you want to download?")
        download_get_type_label.setAlignment(QtCore.Qt.AlignCenter)
        self.grid.addWidget(download_get_type_label, download_row_position, download_column_position)
        download_row_position = download_row_position + 1

        self.download_sell_get_type_checkbox = QCheckBox("Sell Orders")
        self.grid.addWidget(self.download_sell_get_type_checkbox, download_row_position, download_column_position)
        download_row_position = download_row_position + 1

        self.download_buy_get_type_checkbox = QCheckBox("Buy Orders")
        self.grid.addWidget(self.download_buy_get_type_checkbox, download_row_position, download_column_position)
        download_row_position = download_row_position + 1


        download_status_label = QLabel("Which statuses do you want to download?")
        download_status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.grid.addWidget(download_status_label, download_row_position, download_column_position)
        download_row_position = download_row_position + 1

        self.download_active_orders_checkbox = QCheckBox("Active Orders")
        self.grid.addWidget(self.download_active_orders_checkbox, download_row_position, download_column_position)
        download_row_position = download_row_position + 1

        self.download_filled_orders_checkbox = QCheckBox("Filled Orders")
        self.grid.addWidget(self.download_filled_orders_checkbox, download_row_position, download_column_position)
        download_row_position = download_row_position + 1

        self.download_cancelled_orders_checkbox = QCheckBox("Cancelled Orders")
        self.grid.addWidget(self.download_cancelled_orders_checkbox, download_row_position, download_column_position)
        download_row_position = download_row_position + 1


        download_win_rate_label = QLabel("Do you want to download the Win Rate?")
        download_win_rate_label.setAlignment(QtCore.Qt.AlignCenter)
        self.grid.addWidget(download_win_rate_label, download_row_position, download_column_position)
        download_row_position = download_row_position + 1

        self.download_win_rate_checkbox = QCheckBox("Download Win Rate")
        self.grid.addWidget(self.download_win_rate_checkbox, download_row_position, download_column_position)
        download_row_position = download_row_position + 1


        quality_check_label = QLabel("Which quality check methods do you want to run?")
        quality_check_label.setAlignment(QtCore.Qt.AlignCenter)
        self.grid.addWidget(quality_check_label, download_row_position, download_column_position)
        download_row_position = download_row_position + 1

        self.download_double_checking_orders_checkbox = QCheckBox("Double Checking Orders")
        self.grid.addWidget(self.download_double_checking_orders_checkbox, download_row_position, download_column_position)
        download_row_position = download_row_position + 1



        process_column_position = 1
        process_row_position = 1

        processing_tasks_label = QLabel("Processing Download_Task")
        processing_tasks_label.setAlignment(QtCore.Qt.AlignCenter)
        self.grid.addWidget(processing_tasks_label, process_row_position, process_column_position)
        process_row_position = process_row_position + 1

        process_get_type_label = QLabel("Which get_types do you want to process?")
        process_get_type_label.setAlignment(QtCore.Qt.AlignCenter)
        self.grid.addWidget(process_get_type_label, process_row_position, process_column_position)
        process_row_position = process_row_position + 1

        self.process_sell_get_type_checkbox = QCheckBox("Sell Orders")
        self.grid.addWidget(self.process_sell_get_type_checkbox, process_row_position, process_column_position)
        process_row_position = process_row_position + 1


        max_row_position = download_row_position + 1 if download_row_position > process_row_position else process_row_position + 1
        self.task_start_button = QPushButton("Start the tasks")
        self.task_start_button.clicked.connect(self.start_tasks)
        self.grid.addWidget(self.task_start_button, max_row_position, 0, 1, 2)


        self.setLayout(self.grid)


    def start_tasks(self):
        no_error = self.sanity_check()

        if no_error:
            download_task_list = []
            process_task_list = []

            if self.download_sell_get_type_checkbox.isChecked():
                if self.download_active_orders_checkbox.isChecked():
                    download_task_list.append(Download_Task.DOWN_ACTIVE_SELL_ORDERS)
                if self.download_filled_orders_checkbox.isChecked():
                    download_task_list.append(Download_Task.DOWN_FILLED_SELL_ORDERS)
                if self.download_cancelled_orders_checkbox.isChecked():
                    download_task_list.append(Download_Task.DOWN_CANCELLED_SELL_ORDERS)

            if self.download_buy_get_type_checkbox.isChecked():
                if self.download_active_orders_checkbox.isChecked():
                    download_task_list.append(Download_Task.DOWN_ACTIVE_BUY_ORDERS)
                if self.download_filled_orders_checkbox.isChecked():
                    download_task_list.append(Download_Task.DOWN_FILLED_BUY_ORDERS)
                if self.download_cancelled_orders_checkbox.isChecked():
                    download_task_list.append(Download_Task.DOWN_CANCELLED_BUY_ORDERS)

            if self.download_double_checking_orders_checkbox.isChecked():
                download_task_list.append(Download_Task.DOWN_DOUBLE_CHECKING)

            if self.download_win_rate_checkbox.isChecked():
                download_task_list.append(Download_Task.DOWN_WIN_RATE)

            if self.process_sell_get_type_checkbox.isChecked():
                process_task_list.append(Processing_Task.PROCESSING_NEW_DATA)

            high_level_task_list = []
            if len(download_task_list) > 0:
                high_level_task_list.append((High_Level_Task.DOWNLOAD_TASK, download_task_list))
            if len(process_task_list) > 0:
                high_level_task_list.append((High_Level_Task.PROCESS_TASK, process_task_list))

            if len(high_level_task_list) > 0:
                self.notify_observer(high_level_task_list)

    def sanity_check(self):

        messages = []

        if self.download_sell_get_type_checkbox.isChecked() or self.download_buy_get_type_checkbox.isChecked():
            if (self.download_cancelled_orders_checkbox.isChecked() == False) and (self.download_active_orders_checkbox.isChecked() == False) and (self.download_filled_orders_checkbox.isChecked() == False):
                messages.append(f"At least one status has to be checked for downloading.")

        if self.download_cancelled_orders_checkbox.isChecked() or self.download_active_orders_checkbox.isChecked() or self.download_filled_orders_checkbox.isChecked() :
            if (self.download_sell_get_type_checkbox.isChecked() == False) and (self.download_buy_get_type_checkbox.isChecked() == False):
                messages.append(f"At least one get_type has to be checked for downloading.")

        if len(messages) > 0:
            error_text = "\n".join(messages)
            error_message_box = QMessageBox()
            error_message_box.setText(error_text)
            error_message_box.setWindowTitle("Input Error")
            error_message_box.setIcon(QMessageBox.Warning)
            error_message_box.exec_()
            return False

        else:
            return True

    def notify_observer(self, par1=None):

        self.observer.update("task_selection_screen", par1)
