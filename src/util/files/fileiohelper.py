import csv
import json
import os
from src.util.files.filehandler import FileHandler


class FileIoHelper:
    """
    A class to help with file io operations
    """

    def __init__(self):
        """
        The constructor of the FileIoHelper class
        """
        pass

    @staticmethod
    def get_winrate_restart_info():
        """
        A method to get info about from which timestamp to restart the win_rate download process
        :return: the timestamp to restart the win_rate download process
        """

        winrate_info_raw_restart_path = FileHandler.get_base_path("card_win_rate_restart_info")

        if os.path.isfile(winrate_info_raw_restart_path):

            with open(winrate_info_raw_restart_path, 'r', encoding='utf-8') as winrate_info_raw_restart_file:
                start_time_stamp_str = winrate_info_raw_restart_file.readline()
            winrate_info_raw_restart_file.close()

            return start_time_stamp_str

        else:
            return None

    @staticmethod
    def load_filled_order_timeline_dic(year_month_list):
        """
        A method to load filled order timelines dictionary
        :param year_month_list: for which months to load the filled order timelines dictionary
        :return: a filled order timeline dictionary
        """

        filled_order_timeline_path = FileHandler.get_base_path("filled_orders_timeline")
        previous_filled_orders_dic = {}

        for year_month in year_month_list:
            filled_orders_dic_path = str(filled_order_timeline_path) + "\\" + str(year_month) + ".json"

            if os.path.isfile(filled_orders_dic_path):

                with open(filled_orders_dic_path, 'r', encoding='utf-8') as filled_order_timeline_file:
                    filled_order_timeline_dic = json.load(filled_order_timeline_file)
                filled_order_timeline_file.close()

                previous_filled_orders_dic[year_month] = filled_order_timeline_dic
            else:
                previous_filled_orders_dic[year_month] = {}

        return previous_filled_orders_dic

    @staticmethod
    def writing_filled_order_timeline_path_to_file(new_filled_orders_dic):
        """
        A method to write a filled order timeline dictionary to file
        :param new_filled_orders_dic: the filled order timeline dictionary to write to file
        :return: None
        """

        filled_order_timeline_path = FileHandler.get_base_path("filled_orders_timeline")

        for year_month, filled_orders_dic in new_filled_orders_dic.items():

            filled_orders_dic_path = str(filled_order_timeline_path) + "\\" + str(year_month) + ".json"

            with open(filled_orders_dic_path, 'w', encoding='utf-8') as filled_order_timeline_file:
                json.dump(filled_orders_dic, filled_order_timeline_file, ensure_ascii=False, indent=4)
            filled_order_timeline_file.close()

    @staticmethod
    def load_today_filled_order_timeline_dic():
        """
        A method to load today's filled order timeline dictionary
        :return: today's filled order timeline dictionary
        """

        today_filled_order_timeline_path = FileHandler.get_base_path("today_filled_orders_timeline")

        if os.path.isfile(today_filled_order_timeline_path):
            with open(today_filled_order_timeline_path, 'r', encoding='utf-8') as today_filled_order_timeline_file:
                today_filled_order_timeline_dic = json.load(today_filled_order_timeline_file)
            today_filled_order_timeline_file.close()
        else:
            today_filled_order_timeline_dic = {}

        return today_filled_order_timeline_dic

    @staticmethod
    def writing_today_filled_order_timeline_dic_to_file(today_filled_order_timeline_dic):
        """
        A method to write today's filled order timeline dictionary to file
        :param today_filled_order_timeline_dic: the timeline dictionary to write to file
        :return: None
        """

        today_filled_order_timeline_path = FileHandler.get_base_path("today_filled_orders_timeline")

        with open(today_filled_order_timeline_path, 'w', encoding='utf-8') as today_filled_order_timeline_file:
            json.dump(today_filled_order_timeline_dic, today_filled_order_timeline_file, ensure_ascii=False, indent=4)
        today_filled_order_timeline_file.close()

    @staticmethod
    def load_processing_logs():
        """
        A method to read the processing log file
        :return: the processing log file as a dictionary
        """

        processing_logs_path = FileHandler.get_base_path("processing_progress_log_file")

        if os.path.isfile(processing_logs_path):
            with open(processing_logs_path, 'r', encoding='utf-8') as processing_logs_file:
                processing_logs_dic = json.load(processing_logs_file)
            processing_logs_file.close()
        else:
            processing_logs_dic = {}

            processing_logs_dic["processing_updated_active_orders"] = None

            processing_logs_dic["processing_today_timeline"] = None
            processing_logs_dic["processing_baseline_timeline"] = None

            processing_logs_dic["card_win_rate_to_be_processed"] = None

            processing_logs_dic["creating_info_active_orders"] = None

            processing_logs_dic["active_to_be_processed"] = None
            processing_logs_dic["filled_to_be_processed"] = None
            processing_logs_dic["cancelled_to_be_processed"] = None

        return processing_logs_dic

    @staticmethod
    def write_processing_logs(processing_logs_dic):
        """
        A method to write the processing log dictionary to file
        :param processing_logs_dic: the processing log dictionary to write to file
        :return: None
        """

        processing_logs_path = FileHandler.get_base_path("processing_progress_log_file")

        with open(processing_logs_path, 'w', encoding='utf-8') as processing_logs_file:
            json.dump(processing_logs_dic, processing_logs_file, ensure_ascii=False, indent=4)
        processing_logs_file.close()

    @staticmethod
    def load_download_logs():
        """
        A method to read the download logs from file
        :return: the download logs as dictionary
        """

        download_logs_path = FileHandler.get_base_path("download_progress_log_file")

        if os.path.isfile(download_logs_path):
            with open(download_logs_path, 'r', encoding='utf-8') as download_logs_file:
                download_logs_dic = json.load(download_logs_file)
            download_logs_file.close()
        else:
            download_logs_dic = {}

        return download_logs_dic

    @staticmethod
    def write_download_progress_logs(download_logs_dic):
        """
        A method to write a download logs dictionary to file
        :param download_logs_dic: the download logs dictionary to write to file
        :return: None
        """

        download_logs_path = FileHandler.get_base_path("download_progress_log_file")

        with open(download_logs_path, 'w', encoding='utf-8') as download_logs_file:
            json.dump(download_logs_dic, download_logs_file, ensure_ascii=False, indent=4)
        download_logs_file.close()

    @staticmethod
    def write_timestamp_log(get_type_string, status_string, log_list, file_name_list=[]):
        """
        A method to write the timestamp logs to file
        :param get_type_string: the type of the downloaded orders
        :param status_string: the status of the downloaded orders
        :param log_list: the timestamp and download information log
        :param file_name_list: the name of the files to which the downloaded orders were written to
        :return: None
        """

        time_stamp_list = []
        for from_timestamp_str, to_time_stamp_str, download_info_list in log_list:
            time_stamp_dic = {}
            time_stamp_dic["from"] = from_timestamp_str
            time_stamp_dic["to"] = to_time_stamp_str
            time_stamp_dic["file_name_list"] = file_name_list
            time_stamp_dic["download_info_list"] = download_info_list

            time_stamp_list.append(time_stamp_dic)

        download_timestamp_logs_folder_path = FileHandler.get_base_path("timestamps_folder")
        download_log_file_path = str(download_timestamp_logs_folder_path) + "\\" + status_string.lower() + "_" + get_type_string.lower() + "_orders.json"

        with open(download_log_file_path, 'a', encoding='utf-8') as download_log_file:
            for time_stamp_dic in time_stamp_list:
                json.dump(time_stamp_dic, download_log_file)
                download_log_file.write("\n")
        download_log_file.close()

    @staticmethod
    def read_timestamp_log_from_path(timestamp_log_file_path):
        """
        A method to read the timestamp log file from a path
        :param timestamp_log_file_path: the path to read the timestamp log from
        :return: the timestamp log
        """

        with open(timestamp_log_file_path, 'r', encoding='utf-8') as timestamp_log_file:
            stripped_lines = [line.strip() for line in timestamp_log_file if line != None]
        timestamp_log_file.close()

        timestamp_log_list = []
        for line in stripped_lines:
            json_object = json.loads(line)
            timestamp_log_list.append(json_object)

        return timestamp_log_list

    @staticmethod
    def write_missed_order_id_list_to_file(missed_order_id_list):
        """
        A method to write the missed order ids to file
        :param missed_order_id_list: a list of missed order ids to write to file
        :return: None
        """

        missed_order_ids_file_path = FileHandler.get_base_path("missed_order_ids_file")

        with open(missed_order_ids_file_path, 'a', encoding='utf-8') as missed_order_ids_file:

            for missed_order_id_dic in missed_order_id_list:
                json.dump(missed_order_id_dic, missed_order_ids_file)
                missed_order_ids_file.write("\n")

        missed_order_ids_file.close()

    @staticmethod
    def write_to_be_processed_order_ids(to_be_processed_order_id_list, to_processed_order_ids_path):
        """
        A method to write to-be-processed order ids to file
        :param to_be_processed_order_id_list: a list of to-be-processed order id's
        :param to_processed_order_ids_path: the path to write to
        :return: None
        """

        with open(to_processed_order_ids_path, 'a', encoding='utf-8') as to_processed_order_ids_file:
            for to_be_processed_order_id in to_be_processed_order_id_list:
                to_processed_order_ids_file.write(str(to_be_processed_order_id))
                to_processed_order_ids_file.write("\n")
        to_processed_order_ids_file.close()

    @staticmethod
    def delete_to_be_processed_order_ids():
        """
        A method to delete the to be processed order_ids
        :return: None
        """

        combination_list = [("active", "sell"), ("filled", "sell"), ("cancelled", "sell")]

        to_be_processed_downloaded_order_id_folder_path = FileHandler.get_base_path("to_be_processed_downloaded_order_id_folder")

        for status_string, get_type_string in combination_list:

            path_to_be_processed_order_id_list = str(to_be_processed_downloaded_order_id_folder_path) + "\\to_be_processed_" + status_string.lower() + "_" + get_type_string.lower() + "_order_ids.json"

            if os.path.isfile(path_to_be_processed_order_id_list):
                os.remove(path_to_be_processed_order_id_list)

    @staticmethod
    def write_still_to_be_downloaded_order_ids_to_file(still_to_be_downloaded_order_id_list):
        """
        A method to write the still_to_be_downloaded order ids to file
        :param still_to_be_downloaded_order_id_list: the still_to_be_downloaded order ids
        :return: None
        """

        #start_time = datetime.utcnow()

        still_to_be_downloaded_order_ids_file_path = FileHandler.get_base_path("still_to_be_downloaded_order_ids_file")

        with open(still_to_be_downloaded_order_ids_file_path, 'w', encoding='utf-8') as still_to_be_downloaded_order_ids_file:
            json.dump(still_to_be_downloaded_order_id_list, still_to_be_downloaded_order_ids_file, ensure_ascii=False, indent=4)
        still_to_be_downloaded_order_ids_file.close()

        #print(f"Missed Orders 2: {(datetime.utcnow() - start_time).total_seconds()}")

    @staticmethod
    def read_still_to_be_downloaded_order_ids():
        """
        A method to read the still-to-be-downloaded order ids from file
        :return: a list of still-to-be-downloaded order ids
        """

        still_to_be_downloaded_order_ids_file_path = FileHandler.get_base_path("still_to_be_downloaded_order_ids_file")

        if os.path.isfile(still_to_be_downloaded_order_ids_file_path):

            with open(still_to_be_downloaded_order_ids_file_path, 'r', encoding='utf-8') as still_to_be_downloaded_order_ids_file:
                missing_order_id_list = json.load(still_to_be_downloaded_order_ids_file)
            still_to_be_downloaded_order_ids_file.close()

        else:
            missing_order_id_list = None

        return missing_order_id_list

    @staticmethod
    def write_updated_active_sell_orders_timestamp(updated_active_sell_orders_timestamp_str):
        """
        A method to write the still-to-be-updated active sell orders timestamps to file the
        :param updated_active_sell_orders_timestamp_str: the still-to-be-updated active sell orders
        :return: None
        """

        updated_active_sell_orders_timestamps_file_path = FileHandler.get_base_path("updated_active_sell_orders_timestamps_file")

        with open(updated_active_sell_orders_timestamps_file_path, 'w', encoding='utf-8') as updated_active_sell_orders_timestamps_file:
            json.dump(updated_active_sell_orders_timestamp_str, updated_active_sell_orders_timestamps_file, ensure_ascii=False, indent=4)
        updated_active_sell_orders_timestamps_file.close()

    @staticmethod
    def read_updated_active_sell_orders_timestamp():
        """
        A method to read the still-to-be-updated active sell orders timestamps
        :return: the still-to-be-updated active sell orders timestamps
        """

        updated_active_sell_orders_timestamps_file_path = FileHandler.get_base_path("updated_active_sell_orders_timestamps_file")

        with open(updated_active_sell_orders_timestamps_file_path, 'r', encoding='utf-8') as updated_active_sell_orders_timestamps_file:
            updated_active_sell_orders_timestamp_str = json.load(updated_active_sell_orders_timestamps_file)
        updated_active_sell_orders_timestamps_file.close()

        return updated_active_sell_orders_timestamp_str

    @staticmethod
    def load_to_be_processed_user_rank_dic():
       """
       A method to load the processed user rank dictionary
       :return: the processed user rank dictionary
       """

       to_be_processed_user_ranking_dic_file_path = FileHandler.get_base_path("to_be_processed_user_ranking_dic")

       if os.path.isfile(to_be_processed_user_ranking_dic_file_path):

           with open(to_be_processed_user_ranking_dic_file_path, 'r', encoding='utf-8') as to_be_processed_user_ranking_dic_file:
               to_be_processed_user_ranking_dic = json.load(to_be_processed_user_ranking_dic_file)
           to_be_processed_user_ranking_dic_file.close()

       else:
           to_be_processed_user_ranking_dic = {}

       return to_be_processed_user_ranking_dic

    @staticmethod
    def write_to_be_processed_user_rank_dic_to_file(to_be_processed_user_ranking_dic):
        """
        A method to write the processed user rank dictionary to file
        :param to_be_processed_user_ranking_dic: the processed user rank dictionary
        :return: None
        """

        to_be_processed_user_ranking_dic_file_path = FileHandler.get_base_path("to_be_processed_user_ranking_dic")

        with open(to_be_processed_user_ranking_dic_file_path, 'w', encoding='utf-8') as to_be_processed_user_ranking_dic_file:
            json.dump(to_be_processed_user_ranking_dic, to_be_processed_user_ranking_dic_file, ensure_ascii=False, indent=4)
        to_be_processed_user_ranking_dic_file.close()

    @staticmethod
    def load_user_rank_dic():
       """
       A method to load the user rank dictionary
       :return: the user rank dictionary
       """

       user_dic_path = FileHandler.get_base_path("user_ranking_dic")

       if os.path.isfile(user_dic_path):

           with open(user_dic_path, 'r', encoding='utf-8') as user_dic_file:
               user_dic = json.load(user_dic_file)
           user_dic_file.close()

       else:
           user_dic = {}

       return user_dic


    @staticmethod
    def write_user_rank_dic_to_file(user_dic):
        """
        A method to write user rank dictionary to file
        :param user_dic: the user rank dictionary
        :return: None
        """

        user_dic_path = FileHandler.get_base_path("user_ranking_dic")

        with open(user_dic_path, 'w', encoding='utf-8') as user_dic_file:
            json.dump(user_dic, user_dic_file, ensure_ascii=False, indent=4)
        user_dic_file.close()

    @staticmethod
    def write_stop_parallel_processing_boolean(stop_parallel_processing_boolean):
        """
        A method to write the boolean to stop the parallel processing process to file
        :param stop_parallel_processing_boolean: the boolean to stop the parallel processing process to file
        :return: None
        """

        stop_parallel_processing_file_path = FileHandler.get_base_path("stop_parallel_processing_file")

        with open(stop_parallel_processing_file_path, 'w', encoding='utf-8') as stop_parallel_processing_file:
            json.dump(stop_parallel_processing_boolean, stop_parallel_processing_file, ensure_ascii=False, indent=4)
        stop_parallel_processing_file.close()

    @staticmethod
    def read_stop_parallel_processing_boolean():
        """
        A method to read the boolean to stop the parallel processing process from file
        :return:
        """

        stop_parallel_processing_file_path = FileHandler.get_base_path("stop_parallel_processing_file")

        with open(stop_parallel_processing_file_path, 'r', encoding='utf-8') as stop_parallel_processing_file:
            stop_parallel_processing_boolean = json.load(stop_parallel_processing_file)
        stop_parallel_processing_file.close()

        return stop_parallel_processing_boolean

    @staticmethod
    def write_last_downloaded_missing_order_id_to_file(last_downloaded_missing_order_id):
        """
        A method to write the last downloaded missing order id to file
        :param last_downloaded_missing_order_id: the last downloaded missing order id
        :return: None
        """

        last_downloaded_missing_order_id_dic = {}
        last_downloaded_missing_order_id_dic["last_downloaded_missing_order_id"] = last_downloaded_missing_order_id

        last_downloaded_missing_order_id_file_path = FileHandler.get_base_path("last_downloaded_missing_order_id_file")

        with open(last_downloaded_missing_order_id_file_path, 'w', encoding='utf-8') as last_downloaded_missing_order_id_file:
            json.dump(last_downloaded_missing_order_id_dic, last_downloaded_missing_order_id_file, ensure_ascii=False, indent=4)
        last_downloaded_missing_order_id_file.close()

    @staticmethod
    def read_last_downloaded_missing_order_id():
        """
        A method to read the last downloaded missing order id from file
        :return: the last downloaded missing order id
        """

        last_downloaded_missing_order_id_file_path = FileHandler.get_base_path("last_downloaded_missing_order_id_file")

        with open(last_downloaded_missing_order_id_file_path, 'r', encoding='utf-8') as last_downloaded_missing_order_id_file:
            last_downloaded_missing_order_id_dic = json.load(last_downloaded_missing_order_id_file)
        last_downloaded_missing_order_id_file.close()

        last_missing_order_id = int(last_downloaded_missing_order_id_dic["last_downloaded_missing_order_id"])

        return last_missing_order_id

    @staticmethod
    def write_response_error(response_error_dic):
        """
        A method to write a response error to file
        :param response_error_dic: the response error dictionary
        :return: None
        """

        store_path = FileHandler.get_base_path("response_error")

        with open(store_path, 'a', encoding='utf-8') as response_error_file:
            json.dump(response_error_dic, response_error_file, ensure_ascii=False)
            response_error_file.write("\n")
        response_error_file.close()

    @staticmethod
    def write_request_error(request_error_dic):
        """
        A method to write a request error to file
        :param request_error_dic: the request error dictionary
        :return: None
        """

        store_path = FileHandler.get_base_path("request_error")

        with open(store_path, 'a', encoding='utf-8') as request_error_file:
            json.dump(request_error_dic, request_error_file, ensure_ascii=False)
            request_error_file.write("\n")
        request_error_file.close()

    @staticmethod
    def write_too_many_api_calls(too_many_api_calls_dic):
        """
        A method to write a too many api call error to file
        :param too_many_api_calls_dic: the too many api call error dictionary
        :return: None
        """

        store_path = FileHandler.get_base_path("too_many_api_calls")

        with open(store_path, 'a', encoding='utf-8') as too_many_api_calls_file:
            json.dump(too_many_api_calls_dic, too_many_api_calls_file, ensure_ascii=False)
            too_many_api_calls_file.write("\n")
        too_many_api_calls_file.close()

    @staticmethod
    def write_internal_server_error(internal_server_error_dic):
        """
        A method to write an internal server error dictionary to file
        :param internal_server_error_dic: an internal server error dictionary
        :return: None
        """

        store_path = FileHandler.get_base_path("internal_server_error")

        with open(store_path, 'a', encoding='utf-8') as internal_server_error_file:
            json.dump(internal_server_error_dic, internal_server_error_file, ensure_ascii=False)
            internal_server_error_file.write("\n")
        internal_server_error_file.close()

    @staticmethod
    def read_historical_prices_dic():
        """
        A method to read the historical prices dictionary
        :return: the historical prices dictionary
        """

        historical_prices_path = FileHandler.get_base_path("historical_currency_prices")

        with open(historical_prices_path, 'r', encoding='utf-8') as historical_prices_file:
            historical_prices_file_dic = json.load(historical_prices_file)
        historical_prices_file.close()

        return historical_prices_file_dic

    @staticmethod
    def read_to_be_double_checked_file_path(to_be_double_checked_file_path):
        """
        A method to read a to-be-double-checked file from a path
        :param to_be_double_checked_file_path: the path to be read from
        :return: to-be-double-checked list
        """

        with open(to_be_double_checked_file_path, 'r', encoding='utf-8') as to_be_double_checked_file:
            stripped_lines = [line.strip() for line in to_be_double_checked_file if line != None]
        to_be_double_checked_file.close()

        still_to_be_double_checked_list = []
        for line in stripped_lines:
            json_object = json.loads(line)
            still_to_be_double_checked_list.append(json_object)

        return still_to_be_double_checked_list

    @staticmethod
    def write_still_to_be_double_checked_file_to_path(month_log_list, month_overview_file_path):
        """
        A method to write still-to-be-double-checked log to file
        :param month_log_list: the log to write to file
        :param month_overview_file_path: the path to write to
        :return: None
        """

        #start_time = datetime.utcnow()

        with open(month_overview_file_path, 'w', encoding='utf-8') as month_overview_file:
            for dic_entry in month_log_list:
                month_overview_file.write(json.dumps(dic_entry))
                month_overview_file.write("\n")
        month_overview_file.close()

        #print(f"Double Checking Orders 3: {(datetime.utcnow() - start_time).total_seconds()}")

    @staticmethod
    def write_temp_timestamps_from_combined_log_list(combined_log_list, get_type_str):
        """
        A method to write timestamps to the combined log file
        :param combined_log_list: the combined log list
        :param get_type_str: the status of the orders
        :return: None
        """

        #start_time = datetime.utcnow()

        double_checking_temp_timestamp_folder_path = FileHandler.get_base_path("double_checking_temp_timestamp_folder")

        statuses = ["ACTIVE", "FILLED", "CANCELLED", "EXPIRED", "INACTIVE"]

        for entry in combined_log_list:
            dic_entry = {}
            dic_entry["from"] = entry["from"]
            dic_entry["to"] = entry["to"]

            for status in statuses:
                if status in entry["status_missed_orders_dic"]:
                    dic_entry["download_info_list"] = entry["status_missed_orders_dic"][status]
                else:
                    dic_entry["download_info_list"] = []

                path_to_file = str(double_checking_temp_timestamp_folder_path) + "\\" + status.lower() + "_" + get_type_str.lower() + "_double_checked_orders.json"
                with open(path_to_file, 'a', encoding='utf-8') as file:
                    file.write(json.dumps(dic_entry))
                    file.write("\n")
                file.close()

        #print(f"Double Checking Orders 2: {(datetime.utcnow() - start_time).total_seconds()}")

    @staticmethod
    def write_inventory_list(new_inventory_list):
        """
        A method to write the new inventory list to file
        :param new_inventory_list: the new inventory list
        :return: None
        """

        inventory_list_path = FileHandler.get_base_path("inventory_list")

        with open(inventory_list_path, 'w', encoding='utf-8') as inventory_list_file:
            for inventory_entry in new_inventory_list:
                inventory_list_file.write(json.dumps(inventory_entry.to_print_dic()))
                inventory_list_file.write("\n")
        inventory_list_file.close()

    @staticmethod
    def read_inventory_list():
        """
        A method to read the inventory list from file
        :return: the inventory list
        """

        inventory_list_path = FileHandler.get_base_path("inventory_list")

        inventory_text_list = []

        with open(inventory_list_path, 'r', encoding='utf-8') as inventory_list_file:
            for line_index, line in enumerate(inventory_list_file):
                inventory_text_list.append(line)
        inventory_list_file.close()

        return inventory_text_list

    @staticmethod
    def add_testing_info_dic(testing_info_dic):
        """
        A method to write testing information to file
        :param testing_info_dic: the testing dictionary
        :return: None
        """

        testing_info_file_path = FileHandler.get_base_path("testing_info_file")

        with open(testing_info_file_path, 'a', encoding='utf-8') as testing_info_file:
            testing_info_file.write(json.dumps(testing_info_dic))
            testing_info_file.write("\n")
        testing_info_file.close()

    @staticmethod
    def write_new_sales_history_list_to_file(new_sales_history_list):
        """
        A method to write the new sales history list to file
        :param new_sales_history_list: the new sales history list
        :return: None
        """

        new_to_write_list = [x.__dict__ for x in new_sales_history_list]

        csv_columns = list(new_to_write_list[0].keys())

        sales_history_path = FileHandler.get_base_path("sales_history")

        if os.path.isfile(sales_history_path):
            to_write_list = []
            with open(sales_history_path, mode='r') as previous_price_history:
                csv_reader = csv.reader(previous_price_history)

                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        key = row
                    else:
                        values = row
                        entry_combination = list(zip(key, values))
                        dic_entry = {x[0]: x[1] for x in entry_combination}
                        to_write_list.append(dic_entry)
                    line_count += 1
            to_write_list.extend(new_to_write_list)
        else:
            to_write_list = new_to_write_list

        temp_dic = {x["token_id"]:x for x in to_write_list}
        final_write_list = temp_dic.values()

        with open(sales_history_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for line in final_write_list:
                writer.writerow(line)

    @staticmethod
    def write_competition_price_file(competition_price_file_path, competition_price_dic):
        """
        A method to write the competition price dictionary to file
        :param competition_price_file_path: the path to write to
        :param competition_price_dic: the competition price dictionary
        :return: None
        """

        with open(competition_price_file_path, 'w', encoding='utf-8') as competition_price_file:
            json.dump(competition_price_dic, competition_price_file, ensure_ascii=False, indent=4)
        competition_price_file.close()

    @staticmethod
    def read_competition_price_file(competition_price_file_path):
        """
        A method to read a competition price dictionary from file
        :param competition_price_file_path: the path to read the dictionary from
        :return: the competition price dictionary
        """

        with open(competition_price_file_path, 'r', encoding='utf-8') as competition_price_file:
            combined_price_dic = json.load(competition_price_file)
        competition_price_file.close()

        return combined_price_dic

    @staticmethod
    def get_lines_in_file(path_to_file):
        """
        A method to determine how many lines there are in a file
        :param path_to_file: the path to the file
        :return: the number of lines
        """

        max_line_index = 0

        with open(path_to_file, 'r', encoding='utf-8') as file_to_be_read:
            for line_index, line in enumerate(file_to_be_read):
                max_line_index = line_index
        file_to_be_read.close()

        return max_line_index
