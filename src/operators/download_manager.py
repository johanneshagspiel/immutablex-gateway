import sys
import time
import traceback
from datetime import datetime, timedelta
import json
import os
import pytz
import gc
from objects.enums.get_type import Get_Type
from objects.enums.status import Status
from objects.orders.gods_unchained.order_administrator_gu import Order_Administrator_GU
from objects.orders.gods_unchained.order_factory_gu import Order_Factory_GU
from objects.win_rate.win_rate_administrator import Win_Rate_Administrator
from operators.helpers.double_checking_helper import Double_Checking_Helper
from parallel_workers.parallel_list_downloader import Parallel_List_Downloader
from parallel_workers.parallel_order_id_downloader import Parallel_Order_ID_Downloader
from parallel_workers.parallel_order_downloader import Parallel_Order_Downloader
from parallel_workers.parallel_orders_in_section_downloader import Parallel_Orders_In_Section_Downloader
from parallel_workers.parallel_rank_downloader import Parallel_Rank_Downloader
from parallel_workers.parallel_win_rate_start_time_downloader import Parallel_Win_Rate_Start_Time_Downloader
from util.files.file_handler import File_Handler
from util.files.file_io_helper import File_IO_Helper
from util.helpers import Task_To_Console_Printer, Safe_Datetime_Converter
from util.to_download_list_creator import To_Download_List_Creator
from util.custom_exceptions import TooManyAPICalls, Response_Error, Start_New_Day_Error, Request_Error, \
    Internal_Server_Error, Download_Log_Error


class Download_Manager():

    def __init__(self):
        self._wait_until_restart = False
        self._keep_going = True
        self.observer = None


    def restart(self):
        self._wait_until_restart = False

    def shutdown(self):
        self._keep_going = False

    def notify_observers(self, message, sender):
        self.observer.inform(message, sender)



    def download_order(self, get_type_string, status_string, historical_prices_file_dic):

        order_max_download_amount = 30

        not_yet_waiting_message_printed = True

        get_type = Get_Type[get_type_string]
        status = Status[status_string]

        restart_info_path = File_Handler.get_restart_info_path(get_type, status, "ROLLING")
        sender_name = "download_" + get_type_string.lower() + "_" + status_string.lower()

        parallel_order_downloader = Parallel_Order_Downloader()

        if os.path.isfile(restart_info_path):
            with open(restart_info_path, 'r', encoding='utf-8') as restart_info_file:
                temp_restart_info_file = json.load(restart_info_file)
            restart_info_file.close()

            next_start_time_stamp_str = temp_restart_info_file["next_start_time_stamp"]
            start_time_stamp = datetime.strptime(next_start_time_stamp_str, "%Y-%m-%dT%H:%M:%S.%fZ")

        else:
            start_time_stamp = datetime.strptime("2021-06-01T00:00:00.00Z", "%Y-%m-%dT%H:%M:%S.%fZ")


        print(f"Downloading {status_string} {get_type_string} Orders")

        while self._keep_going:

            if self._wait_until_restart:
                self.notify_observers("waiting", sender_name)
                while self._wait_until_restart:
                    time.sleep(1)
                parallel_order_downloader._shut_down = False

            current_time_stamp = datetime.utcnow()

            difference = (current_time_stamp - start_time_stamp).total_seconds()
            if difference > 60:

                not_yet_waiting_message_printed = True

                time_stamp_str_list, next_start_time_stamp_str, not_caught_up_with_now_new = To_Download_List_Creator.create_timestamp_list(start_time_stamp, current_time_stamp, order_max_download_amount)

                start_time_stamp_str = Safe_Datetime_Converter.datetime_to_string(start_time_stamp)


                try:
                    Task_To_Console_Printer.print_downloading_task_info(status_string=status_string, get_type_string=get_type_string, from_str=start_time_stamp_str, to_str=time_stamp_str_list[-1][1])

                    result = parallel_order_downloader.parallel_download_timestamp_orders(get_type_str=get_type_string, status_str=status_string, time_stamp_str_list=time_stamp_str_list)
                    current_time_stamp = datetime.utcnow()

                    Task_To_Console_Printer.print_writing_warning(status_str=status_string, get_type_string=get_type_string)

                    Order_Administrator_GU.receive_orders_with_timestamp(get_type_string, status_string, result, start_time_stamp_str, next_start_time_stamp_str, historical_prices_file_dic, current_time_stamp)

                    error_encountered = False


                except (Response_Error, Request_Error, TooManyAPICalls, Internal_Server_Error, Start_New_Day_Error) as custom_errors:
                    self.notify_observers(custom_errors, sender_name)

                    parallel_order_downloader._shut_down = True
                    self._wait_until_restart = True
                    error_encountered = True

                except Exception as e:
                    print("#")
                    print(type(e))
                    print(e)
                    print(f"{sender_name}")
                    self._keep_going = False
                    traceback.print_exc()
                    print("#")


                if error_encountered:
                    pass

                else:
                    start_time_stamp = Safe_Datetime_Converter.string_to_datetime(next_start_time_stamp_str)

            else:
                if not_yet_waiting_message_printed:
                    Task_To_Console_Printer.print_waiting_task_info(status_string=status_string, get_type_string=get_type_string)
                    not_yet_waiting_message_printed = False

        self.notify_observers("shut_down", sender_name)



    def download_winrate(self):

        max_time_period_download_amount = 15
        max_rank_download_amount = 100

        start_time_stamp_str = File_IO_Helper.get_winrate_restart_info()

        if start_time_stamp_str:
            start_time_stamp = Safe_Datetime_Converter.string_to_datetime(start_time_stamp_str)
        else:
            current_time_utc = datetime.utcnow()
            start_time_stamp = current_time_utc - timedelta(days=31) - timedelta(hours=current_time_utc.hour) - timedelta(minutes=current_time_utc.minute) - timedelta(seconds=current_time_utc.second) - timedelta(microseconds=current_time_utc.microsecond)

        sender_name = "download_win_rate"
        not_yet_waiting_message_printed = True
        error_encountered = False

        pwrstd = Parallel_Win_Rate_Start_Time_Downloader()
        pld = Parallel_List_Downloader()

        print(f"Downloading WIN_RATE")

        while self._keep_going:

            if self._wait_until_restart:
                print(f"{sender_name}: Waiting")
                self.notify_observers("waiting", sender_name)
                while self._wait_until_restart:
                    time.sleep(1)
                pwrstd._shut_down = False

            current_time_stamp = datetime.utcnow()

            difference = (current_time_stamp - start_time_stamp).total_seconds()

            if difference > 60:

                still_more_win_rates_to_download = True

                while still_more_win_rates_to_download and self._keep_going:

                    if self._wait_until_restart:
                        self.notify_observers("waiting", sender_name)
                        while self._wait_until_restart:
                            time.sleep(1)
                        pwrstd._shut_down = False


                    not_yet_waiting_message_printed = True

                    current_time_stamp = datetime.utcnow()
                    time_stamp_str_list, next_start_time_stamp_str, new_still_more_to_download = To_Download_List_Creator.create_timestamp_list(start_time_stamp, current_time_stamp, max_time_period_download_amount)

                    start_time_stamp_str = Safe_Datetime_Converter.datetime_to_string(start_time_stamp)

                    try:
                        Task_To_Console_Printer.print_downloading_task_info(status_string="WIN_RATE", get_type_string=None, from_str=start_time_stamp_str, to_str=time_stamp_str_list[-1][1])

                        win_rate_list = pwrstd.parallel_download_win_rate(time_stamp_str_list)

                        user_id_list = list({win_rate.user_id : True for win_rate in win_rate_list}.keys())

                        if len(user_id_list) > 0:
                            result_list = pld.parallel_download_list(list_to_download=user_id_list, max_download_amount=max_rank_download_amount, task="download_rank_by_user_id")

                            if len(result_list) > 0:

                                rank_dic = result_list.pop()

                                final_win_rate_list = []
                                for win_rate in win_rate_list:
                                    rank = rank_dic[win_rate.user_id]
                                    win_rate.user_rank = rank
                                    final_win_rate_list.append(win_rate)

                                final_win_rate_list = sorted(final_win_rate_list, key= lambda x: x.unix_time_finished, reverse=False)

                                Task_To_Console_Printer.print_writing_warning("WIN_RATE", get_type_string=None)

                                Win_Rate_Administrator.receive_winrate_list(final_win_rate_list, next_start_time_stamp_str)

                        still_more_win_rates_to_download = new_still_more_to_download

                        error_encountered = False


                    except (Response_Error, Request_Error, TooManyAPICalls, Internal_Server_Error, Start_New_Day_Error) as custom_errors:
                        self.notify_observers(custom_errors, sender_name)

                        pwrstd._shut_down = True
                        pld.shut_down()
                        self._wait_until_restart = True
                        error_encountered = True
                        still_more_win_rates_to_download = True

                    except Exception as e:
                        print("#")
                        print(type(e))
                        print(e)
                        print(f"{sender_name}")
                        self._keep_going = False
                        traceback.print_exc()
                        print("#")


                    if error_encountered:
                        pass

                    else:
                        start_time_stamp = Safe_Datetime_Converter.string_to_datetime(next_start_time_stamp_str)

            else:

                if not_yet_waiting_message_printed:
                    Task_To_Console_Printer.print_waiting_task_info(status_string="WIN_RATE", get_type_string=None)
                    not_yet_waiting_message_printed = False

        self.notify_observers("shut_down", sender_name)



    def download_orders_to_be_double_checked(self, only_task, double_checking_files_path_list, historical_prices_file_dic):

        if only_task:
            download_amount = 60
        else:
            download_amount = 30

        get_type_str = "SELL"


        to_be_double_checked_file_path = double_checking_files_path_list.pop()
        to_be_double_checked_list = File_IO_Helper.read_to_be_double_checked_file_path(to_be_double_checked_file_path)

        still_files_to_double_check = True
        error_encountered = False
        sender_name = "download_double_checking_orders"

        poisd = Parallel_Orders_In_Section_Downloader()


        while still_files_to_double_check and self._keep_going:

            print(f"Downloading DOUBLE_CHECKED Orders")

            start_position = 0
            last_time_stamp = to_be_double_checked_list[-1]["from"]

            if len(to_be_double_checked_list) > download_amount:
                end_position = download_amount
            else:
                end_position = len(to_be_double_checked_list)

            not_caught_up = True


            while not_caught_up and self._keep_going:

                if self._wait_until_restart:
                    self.notify_observers("waiting", sender_name)
                    while self._wait_until_restart:
                        time.sleep(1)
                    poisd._shut_down = False


                if end_position == len(to_be_double_checked_list):
                    not_caught_up = False

                next_to_check_portion = to_be_double_checked_list[start_position:end_position]
                remaining_portion = to_be_double_checked_list[end_position:]

                try:
                    start_timestamp_str = next_to_check_portion[0]["to"]
                    end_timestamp_str = next_to_check_portion[-1]["from"]

                    Task_To_Console_Printer.print_downloading_task_info(status_string="DOUBLE_CHECKED", get_type_string=None, from_str=start_timestamp_str, to_str=end_timestamp_str, additional_info=last_time_stamp)

                    result_list = poisd.parallel_download_orders_in_sections(get_type_str=get_type_str, section_to_download_list=next_to_check_portion)

                    combined_log_list, missed_order_json_list = Double_Checking_Helper.find_incorrect_orders_list( result_list)

                    order_object_list = [Order_Factory_GU.order_json_to_object(missed_order_json, historical_prices_file_dic) for missed_order_json in missed_order_json_list]
                    order_object_list = [order for order in order_object_list if order]

                    Task_To_Console_Printer.print_writing_warning(status_str="DOUBLE_CHECKED", get_type_string=None)

                    if len(order_object_list) > 0:

                        Order_Administrator_GU.received_double_checked_orders(order_object_list, get_type_str)

                    File_IO_Helper.write_temp_timestamps_from_combined_log_list(combined_log_list, get_type_str)

                    File_IO_Helper.write_still_to_be_double_checked_file_to_path(remaining_portion, to_be_double_checked_file_path)

                    error_encountered = False


                except (Response_Error, Request_Error, TooManyAPICalls, Internal_Server_Error, Start_New_Day_Error) as custom_errors:
                    self.notify_observers(custom_errors, sender_name)

                    poisd._shut_down = True
                    self._wait_until_restart = True
                    error_encountered = True
                    not_caught_up = True

                except Exception as e:
                    print("#")
                    print(type(e))
                    print(e)
                    print(f"{sender_name}")
                    self._keep_going = False
                    traceback.print_exc()
                    print("#")


                if error_encountered:
                    pass

                else:
                    start_position = end_position

                    if len(to_be_double_checked_list) < (end_position + download_amount):
                        end_position = len(to_be_double_checked_list)
                    else:
                        end_position = end_position + download_amount


            if len(double_checking_files_path_list) == 0:
                still_files_to_double_check = False
            else:
                os.remove(to_be_double_checked_file_path)
                to_be_double_checked_file_path = double_checking_files_path_list.pop()
                to_be_double_checked_list = File_IO_Helper.read_to_be_double_checked_file_path(to_be_double_checked_file_path)

        self.notify_observers("shut_down", sender_name)



    def download_missing_orders(self, only_task, still_to_be_downloaded_order_ids_list, historical_prices_file_dic):

        if only_task:
            download_amount = 500
        else:
            download_amount = 250

        start_position = 0
        total_number_missing_order_ids = len(still_to_be_downloaded_order_ids_list)

        if len(still_to_be_downloaded_order_ids_list) > download_amount:
            end_position = download_amount
        else:
            end_position = len(still_to_be_downloaded_order_ids_list)

        sender_name = "download_missing_orders"

        error_encountered = False
        not_caught_up = True
        parallel_order_id_downloader = Parallel_Order_ID_Downloader()

        print(f"Downloading MISSED Orders")

        while not_caught_up and self._keep_going:

            if self._wait_until_restart:
                self.notify_observers("waiting", sender_name)
                while self._wait_until_restart:
                    time.sleep(1)
                parallel_order_id_downloader._shut_down = False

            if end_position == len(still_to_be_downloaded_order_ids_list):
                not_caught_up = False

            next_to_check_portion = still_to_be_downloaded_order_ids_list[start_position:end_position]
            remaining_portion = still_to_be_downloaded_order_ids_list[end_position:]

            try:

                Task_To_Console_Printer.print_downloading_task_info(status_string="MISSED", get_type_string=None, from_str=start_position, to_str=end_position, additional_info=str(total_number_missing_order_ids))

                missing_orders_list = parallel_order_id_downloader.parallel_download_orders_by_id(missing_order_id_list=next_to_check_portion, version="json")

                Task_To_Console_Printer.print_writing_warning(status_str="MISSED", get_type_string=None)

                current_time_local = datetime.now()
                current_time_utc = current_time_local.astimezone(pytz.utc)

                Order_Administrator_GU.receive_missing_orders(missing_orders_list, historical_prices_file_dic, current_time_utc)

                File_IO_Helper.write_still_to_be_downloaded_order_ids_to_file(remaining_portion)

                error_encountered = False


            except (Response_Error, Request_Error, TooManyAPICalls, Internal_Server_Error, Start_New_Day_Error) as custom_errors:
                self.notify_observers(custom_errors, sender_name)

                parallel_order_id_downloader._shut_down = True
                self._wait_until_restart = True
                error_encountered = True
                not_caught_up = True

            except Exception as e:
                print("#")
                print(type(e))
                print(e)
                print(f"{sender_name}")
                self._keep_going = False
                traceback.print_exc()
                print("#")


            if error_encountered:
                pass

            else:
                start_position = end_position

                if len(still_to_be_downloaded_order_ids_list) < (end_position + download_amount):
                    end_position = len(still_to_be_downloaded_order_ids_list)
                else:
                    end_position = end_position + download_amount

        self.notify_observers("shut_down", sender_name)
