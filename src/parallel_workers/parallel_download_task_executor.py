import concurrent.futures
#logging.basicConfig(level=logging.DEBUG)
import time
import traceback

from objects.orders.gods_unchained.order_administrator_gu import Order_Administrator_GU
from objects.enums.tasks import Download_Task
from operators.download_manager import Download_Manager
from operators.helpers.double_checking_helper import Double_Checking_Helper
from operators.helpers.missed_orders_helper import Missed_Orders_Helper
from scrappers.coinapi_scrapper import CoinAPI_Scrapper
from scrappers.gods_unchained_poller import Gods_Unchained_Poller
from scrappers.gods_unchained_winrate_poller import Gods_Unchained_Winrate_Poller
from util.files.file_handler import File_Handler
from util.files.file_io_helper import File_IO_Helper
from util.custom_exceptions import TooManyAPICalls, Response_Error, Start_New_Day_Error, Request_Error, Internal_Server_Error, Download_Log_Error
from multiprocessing import Pipe

from util.helpers import Future_Helper


class Parallel_Download_Task_Executor():

    def __init__(self):
        self.observer = None

        self._guwp = Gods_Unchained_Winrate_Poller()
        self._download_manager = Download_Manager()
        self._download_manager.observer = self

        self._status_dic = {}

        self.message_to_be_passed_on = None
        self.no_message_sent = True


    def parallel_execute_download_task(self, task_list):
        amount_tasks = len(task_list)

        input_list = []

        download_logs_dic = {}
        for task in task_list:


            if task == Download_Task.DOWN_ACTIVE_SELL_ORDERS:
                entry = "download_sell_active"
                input_list.append((task, None))

            if task == Download_Task.DOWN_FILLED_SELL_ORDERS:
                entry = "download_sell_filled"
                input_list.append((task, None))

            if task == Download_Task.DOWN_CANCELLED_SELL_ORDERS:
                entry = "download_sell_cancelled"
                input_list.append((task, None))

            if task == Download_Task.DOWN_ACTIVE_BUY_ORDERS:
                entry = "download_buy_active"
                input_list.append((task, None))

            if task == Download_Task.DOWN_FILLED_BUY_ORDERS:
                entry = "download_buy_filled"
                input_list.append((task, None))

            if task == Download_Task.DOWN_CANCELLED_BUY_ORDERS:
                entry = "download_buy_cancelled"
                input_list.append((task, None))

            if task == Download_Task.DOWN_WIN_RATE:
                entry = "download_win_rate"
                input_list.append((task, None))


            if task == Download_Task.DOWN_MISSING_ORDERS:
                entry = "download_missing_orders"

                current_still_to_be_downloaded_order_ids_list = File_IO_Helper.read_still_to_be_downloaded_order_ids()

                if current_still_to_be_downloaded_order_ids_list == None or len(current_still_to_be_downloaded_order_ids_list) == 0:
                    #still_to_be_downloaded_order_ids_list = Missed_Orders_Helper.create_still_to_be_downloaded_order_ids_list()
                    raise Exception("Implement case of missing orders after one pass")

                else:
                    still_to_be_downloaded_order_ids_list = current_still_to_be_downloaded_order_ids_list

                input_entry = {"still_to_be_downloaded_order_ids_list" : still_to_be_downloaded_order_ids_list}
                input_list.append((task, input_entry))


            if task == Download_Task.DOWN_DOUBLE_CHECKING:
                entry = "download_double_checking_orders"

                double_checking_underway = Double_Checking_Helper.check_if_double_checking_going_on()

                if double_checking_underway:
                    double_checking_files_path_list = Double_Checking_Helper.get_double_checking_file_paths()
                else:
                    raise Exception("Implement how to deal when everything has been double checked once")
                    #double_checking_files_path_list = Double_Checking_Helper.create_double_checking_list(get_type_string="SELL")

                input_entry = {"double_checking_files_path_list" : double_checking_files_path_list}
                input_list.append((task, input_entry))

            download_logs_dic[entry] = "started"
            self._status_dic[entry] = "started"

        File_IO_Helper.write_download_progress_logs(download_logs_dic)

        historical_prices_file_dic = CoinAPI_Scrapper.get_historical_prices()

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=amount_tasks)
        future_list = []
        for task, additional_information_dic in input_list:
            temp_future = executor.submit(self._execute_task, task, additional_information_dic, historical_prices_file_dic)
            future_list.append(temp_future)

        while Future_Helper.at_least_one_future_not_done(future_list):
            time.sleep(1)


        finished_download_task_dic = {}
        for task in download_logs_dic.keys():
            finished_download_task_dic[task] = "finished"
        File_IO_Helper.write_download_progress_logs(finished_download_task_dic)


    def _execute_task(self, task, additional_information_dic, historical_prices_file_dic):

        if task == Download_Task.DOWN_ACTIVE_SELL_ORDERS:
            self._download_manager.download_order(get_type_string="SELL", status_string="ACTIVE", historical_prices_file_dic=historical_prices_file_dic)

        elif task == Download_Task.DOWN_FILLED_SELL_ORDERS:
            self._download_manager.download_order(get_type_string="SELL", status_string="FILLED", historical_prices_file_dic=historical_prices_file_dic)

        elif task == Download_Task.DOWN_CANCELLED_SELL_ORDERS:
            self._download_manager.download_order(get_type_string="SELL", status_string="CANCELLED", historical_prices_file_dic=historical_prices_file_dic)


        if task == Download_Task.DOWN_ACTIVE_BUY_ORDERS:
            self._download_manager.download_order(get_type_string="BUY", status_string="ACTIVE", historical_prices_file_dic=historical_prices_file_dic)

        elif task == Download_Task.DOWN_FILLED_BUY_ORDERS:
            self._download_manager.download_order(get_type_string="BUY", status_string="FILLED", historical_prices_file_dic=historical_prices_file_dic)

        elif task == Download_Task.DOWN_CANCELLED_BUY_ORDERS:
            self._download_manager.download_order(get_type_string="BUY", status_string="CANCELLED", historical_prices_file_dic=historical_prices_file_dic)


        elif task == Download_Task.DOWN_WIN_RATE:
            try:
                self._download_manager.download_winrate()
            except Exception as e:
                traceback.print_exc()

        elif task == Download_Task.DOWN_MISSING_ORDERS:
            self._download_manager.download_missing_orders(only_task=False, still_to_be_downloaded_order_ids_list=additional_information_dic["still_to_be_downloaded_order_ids_list"], historical_prices_file_dic=historical_prices_file_dic)

        elif task == Download_Task.DOWN_DOUBLE_CHECKING:
            self._download_manager.download_orders_to_be_double_checked(only_task=False, double_checking_files_path_list=additional_information_dic["double_checking_files_path_list"], historical_prices_file_dic=historical_prices_file_dic)



    def restart(self):
        new_status_dic = {}
        for process_name, status in self._status_dic.items():
            new_status_dic[process_name] = "started"
        self._status_dic = new_status_dic

        self.message_to_be_passed_on = None
        self.no_message_sent = True

        self._download_manager.restart()



    def shutdown(self):
        self._download_manager.shutdown()


    def inform(self, information, sender):

        if isinstance(information, (Response_Error, Request_Error, TooManyAPICalls, Internal_Server_Error, Start_New_Day_Error)):

            print(f"Received {information} from {sender}")

            self.message_to_be_passed_on = information


        elif isinstance(information, str):

            print(f"Received {information} from {sender}")

            if information == "waiting":
                self._status_dic[sender] = "waiting"

                if self.message_to_be_passed_on:

                    all_processes_down = True
                    for process_name, status in self._status_dic.items():
                        if status != "waiting":
                            all_processes_down = False
                    if all_processes_down:
                        if self.no_message_sent:
                            self.no_message_sent = False
                            self.notify_observer(self.message_to_be_passed_on, "parallel_download_task_executor")


            elif information == "shut_down":
                self._status_dic[sender] = "shut_down"

                all_processes_down = True
                for process_name, status in self._status_dic.items():
                    if status != "shut_down":
                        all_processes_down = False
                if all_processes_down:
                    if self.no_message_sent:
                        self.no_message_sent = False
                        self.notify_observer("shut_down_completed", "parallel_download_task_executor")


    def notify_observer(self, information, sender):

        self.observer.inform(information, sender)
