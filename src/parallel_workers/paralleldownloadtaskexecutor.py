import concurrent.futures
import time
import traceback
from src.objects.enums.tasks import DownloadTask
from src.operators.downloadmanager import DownloadManager
from src.operators.helpers.doublecheckinghelper import DoubleCheckingHelper
from src.operators.requestscheduler import RequestScheduler
from src.scrappers.coinapiscrapper import CoinAPIScrapper
from src.scrappers.gods_unchained_winrate_poller import Gods_Unchained_Winrate_Poller
from src.util.files.fileiohelper import FileIoHelper
from src.util.custom_exceptions import TooManyAPICalls, ResponseError, StartNewDayError, RequestError, \
    InternalServerError
from src.util.helpers import FutureHelper


class ParallelDownloadTaskExecutor:
    """
    A class to parallel execute download tasks
    """

    def __init__(self):
        """
        The constructor of the ParallelDownloadTaskExecutor class
        """
        self.observer = None

        self._guwp = Gods_Unchained_Winrate_Poller()

        self._DownloadManager = DownloadManager()

        self._DownloadManager.observer = self

        self._status_dic = {}

        self.message_to_be_passed_on = None
        self.no_message_sent = True


    def parallel_execute_download_task(self, task_list):
        """
        A method to parallel execute a list of download task
        :param task_list: a list of download tasks to be executed
        :return: None
        """
        amount_tasks = len(task_list)

        input_list = []

        download_logs_dic = {}
        for task in task_list:

            if task == DownloadTask.DOWN_REQUEST_SCHEDULER:
                entry = "download_request_scheduler"
                input_list.append((task, None))

            if task == DownloadTask.DOWN_ACTIVE_SELL_ORDERS:
                entry = "download_sell_active"
                input_list.append((task, None))

            if task == DownloadTask.DOWN_FILLED_SELL_ORDERS:
                entry = "download_sell_filled"
                input_list.append((task, None))

            if task == DownloadTask.DOWN_CANCELLED_SELL_ORDERS:
                entry = "download_sell_cancelled"
                input_list.append((task, None))

            if task == DownloadTask.DOWN_ACTIVE_BUY_ORDERS:
                entry = "download_buy_active"
                input_list.append((task, None))

            if task == DownloadTask.DOWN_FILLED_BUY_ORDERS:
                entry = "download_buy_filled"
                input_list.append((task, None))

            if task == DownloadTask.DOWN_CANCELLED_BUY_ORDERS:
                entry = "download_buy_cancelled"
                input_list.append((task, None))

            if task == DownloadTask.DOWN_WIN_RATE:
                entry = "download_win_rate"
                input_list.append((task, None))

            if task == DownloadTask.DOWN_MISSING_ORDERS:
                entry = "download_missing_orders"

                current_still_to_be_downloaded_order_ids_list = FileIoHelper.read_still_to_be_downloaded_order_ids()

                if current_still_to_be_downloaded_order_ids_list == None or len(current_still_to_be_downloaded_order_ids_list) == 0:
                    #still_to_be_downloaded_order_ids_list = MissedOrdersHelper.create_still_to_be_downloaded_order_ids_list()
                    raise Exception("Implement case of missing orders after one pass")

                else:
                    still_to_be_downloaded_order_ids_list = current_still_to_be_downloaded_order_ids_list

                input_entry = {"still_to_be_downloaded_order_ids_list" : still_to_be_downloaded_order_ids_list}
                input_list.append((task, input_entry))

            if task == DownloadTask.DOWN_DOUBLE_CHECKING:
                entry = "download_double_checking_orders"

                double_checking_underway = DoubleCheckingHelper.check_if_double_checking_going_on()

                if double_checking_underway:
                    double_checking_files_path_list = DoubleCheckingHelper.get_double_checking_file_paths()
                else:
                    raise Exception("Implement how to deal when everything has been double checked once")
                    #double_checking_files_path_list = DoubleCheckingHelper.create_double_checking_list(get_type_string="SELL")

                input_entry = {"double_checking_files_path_list" : double_checking_files_path_list}
                input_list.append((task, input_entry))

            download_logs_dic[entry] = "started"
            self._status_dic[entry] = "started"

        FileIoHelper.write_download_progress_logs(download_logs_dic)

        historical_prices_file_dic = CoinAPIScrapper.get_historical_prices()

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=amount_tasks)
        future_list = []
        for task, additional_information_dic in input_list:
            temp_future = executor.submit(self._execute_task, task, additional_information_dic, historical_prices_file_dic)
            future_list.append(temp_future)

        while FutureHelper.at_least_one_future_not_done(future_list):
            time.sleep(1)

        finished_DownloadTask_dic = {}
        for task in download_logs_dic.keys():
            finished_DownloadTask_dic[task] = "finished"
        FileIoHelper.write_download_progress_logs(finished_DownloadTask_dic)

    def _execute_task(self, task, additional_information_dic, historical_prices_file_dic):
        """
        A method to execute one task
        :param task: the download task
        :param additional_information_dic: additional information for the task as a dictionary
        :param historical_prices_file_dic: a historical price overview as a dictionary
        :return: None
        """

        if task == DownloadTask.DOWN_REQUEST_SCHEDULER:
            self._request_manager.run()

        if task == DownloadTask.DOWN_ACTIVE_SELL_ORDERS:
            self._DownloadManager.download_order(get_type_string="SELL", status_string="ACTIVE", mode= "un_scheduled", historical_prices_file_dic=historical_prices_file_dic)

        elif task == DownloadTask.DOWN_FILLED_SELL_ORDERS:
            self._DownloadManager.download_order(get_type_string="SELL", status_string="FILLED", mode= "un_scheduled", historical_prices_file_dic=historical_prices_file_dic)

        elif task == DownloadTask.DOWN_CANCELLED_SELL_ORDERS:
            self._DownloadManager.download_order(get_type_string="SELL", status_string="CANCELLED", mode= "un_scheduled", historical_prices_file_dic=historical_prices_file_dic)


        if task == DownloadTask.DOWN_ACTIVE_BUY_ORDERS:
            self._DownloadManager.download_order(get_type_string="BUY", status_string="ACTIVE", mode= "un_scheduled", historical_prices_file_dic=historical_prices_file_dic)

        elif task == DownloadTask.DOWN_FILLED_BUY_ORDERS:
            self._DownloadManager.download_order(get_type_string="BUY", status_string="FILLED", mode= "un_scheduled", historical_prices_file_dic=historical_prices_file_dic)

        elif task == DownloadTask.DOWN_CANCELLED_BUY_ORDERS:
            self._DownloadManager.download_order(get_type_string="BUY", status_string="CANCELLED", mode= "un_scheduled", historical_prices_file_dic=historical_prices_file_dic)

        elif task == DownloadTask.DOWN_WIN_RATE:
            try:
                self._DownloadManager.download_winrate()
            except Exception as e:
                traceback.print_exc()

        elif task == DownloadTask.DOWN_MISSING_ORDERS:
            self._DownloadManager.download_missing_orders(only_task=False, still_to_be_downloaded_order_ids_list=additional_information_dic["still_to_be_downloaded_order_ids_list"], historical_prices_file_dic=historical_prices_file_dic)

        elif task == DownloadTask.DOWN_DOUBLE_CHECKING:
            self._DownloadManager.download_orders_to_be_double_checked(only_task=False, double_checking_files_path_list=additional_information_dic["double_checking_files_path_list"], historical_prices_file_dic=historical_prices_file_dic)

    def restart(self):
        """
        A method to restart the parallel download task execution process
        :return: None
        """
        new_status_dic = {}
        for process_name, status in self._status_dic.items():
            new_status_dic[process_name] = "started"
        self._status_dic = new_status_dic

        self.message_to_be_passed_on = None
        self.no_message_sent = True

        self._DownloadManager.restart()

    def shutdown(self):
        """
        A method to shut down the parallel download task execution process
        :return: None
        """
        self._DownloadManager.shutdown()

    def inform(self, information, sender):
        """
        A method to handle received information
        :param information: the received information
        :param sender: the sender of the information
        :return: None
        """

        if isinstance(information, (ResponseError, RequestError, TooManyAPICalls, InternalServerError, StartNewDayError)):

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
                            self.notify_observer(self.message_to_be_passed_on, "ParallelDownloadTaskExecutor")

            elif information == "shut_down":
                self._status_dic[sender] = "shut_down"

                all_processes_down = True
                for process_name, status in self._status_dic.items():
                    if status != "shut_down":
                        all_processes_down = False
                if all_processes_down:
                    if self.no_message_sent:
                        self.no_message_sent = False
                        self.notify_observer("shut_down_completed", "ParallelDownloadTaskExecutor")

    def notify_observer(self, information, sender):
        """
        A method to pass information along
        :param information: the information to be passed along
        :param sender: the sender of the information
        :return: NOne
        """

        self.observer.inform(information, sender)
