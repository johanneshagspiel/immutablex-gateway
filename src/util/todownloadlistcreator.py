import json
import os
from datetime import timedelta
from src.util.files.filehandler import FileHandler
from src.util.files.fileiohelper import FileIoHelper
from src.util.helpers import SafeDatetimeConverter


class ToDownloadListCreator:
    """
    A class to determine what to download next
    """

    def __init__(self):
        """
        The constructor of the ToDownloadListCreator class
        """
        pass

    @staticmethod
    def create_timestamp_list(start_time_stamp, current_time_stamp, max_to_be_downloaded_amount):
        """
        A method to create a list of timestamps to be downloaded
        :param start_time_stamp: the timestamp from which to determine the other timestamps
        :param current_time_stamp: the current time
        :param max_to_be_downloaded_amount: how many timestamps to download at once
        :return: a list of timestamps to be downloaded
        """

        time_difference = (current_time_stamp - start_time_stamp).total_seconds()

        time_stamp_str_list = []
        from_time_stamp = start_time_stamp

        balanced_simultaneous_downloads = max_to_be_downloaded_amount * 60

        if time_difference >= balanced_simultaneous_downloads:
            to_be_downloaded = max_to_be_downloaded_amount
        else:
            to_be_downloaded = int(time_difference / 60)


        if to_be_downloaded == 0:

            raise Exception(f"How ? {start_time_stamp}, {current_time_stamp}, {max_to_be_downloaded_amount}")

        for increase in range(to_be_downloaded):
            to_time_stamp = from_time_stamp + timedelta(minutes=1) - timedelta(seconds=from_time_stamp.second) - timedelta(microseconds=from_time_stamp.microsecond)

            if to_time_stamp > current_time_stamp:
                raise Exception(f"The increase is {increase} out of {to_be_downloaded}  - start_time is {start_time_stamp}, to_time_stamp is {to_time_stamp} and current_time is {current_time_stamp}")

            from_time_stamp_str = SafeDatetimeConverter.datetime_to_string(from_time_stamp)
            to_time_stamp_str = SafeDatetimeConverter.datetime_to_string(to_time_stamp)

            time_stamp_str_list.append((from_time_stamp_str, to_time_stamp_str))
            from_time_stamp = to_time_stamp + timedelta(microseconds=1)

        next_start_time_stamp = SafeDatetimeConverter.string_to_datetime(time_stamp_str_list[-1][1]) + timedelta(microseconds=1)
        if to_be_downloaded == max_to_be_downloaded_amount:
            not_caught_up_with_now = True
        else:
            not_caught_up_with_now = False

        next_start_time_stamp_str = SafeDatetimeConverter.datetime_to_string(next_start_time_stamp)

        return (time_stamp_str_list, next_start_time_stamp_str, not_caught_up_with_now)

    @staticmethod
    def create_missing_order_id_list():
        """
        A method to determine which order ids were missed
        :return: a list of missing order ids
        """

        combination_list = [("active", "sell"), ("filled", "sell"), ("cancelled", "sell"), ("active", "buy"), ("filled", "buy"), ("cancelled", "buy")]

        to_be_processed_downloaded_order_id_folder_path = FileHandler.get_base_path("to_be_processed_downloaded_order_id_folder")
        last_downloaded_missing_order_id_file_path = FileHandler.get_base_path("last_downloaded_missing_order_id_file")

        total_order_id_list = []

        for file_index, (status_string, get_type_string) in enumerate(combination_list):

            path_to_order_id_list = str(to_be_processed_downloaded_order_id_folder_path) + "\\to_be_processed_" + status_string.lower() + "_" + get_type_string.lower() + "_order_ids.json"
            path_to_double_checked_order_id_list = str(to_be_processed_downloaded_order_id_folder_path) + "\\to_be_processed_double_checked_" + status_string.lower() + "_" + get_type_string.lower() + "_order_ids.json"

            path_list = [path_to_order_id_list, path_to_double_checked_order_id_list]

            for path in path_list:
                if os.path.isfile(path):

                    with open(path, 'r', encoding='utf-8') as order_id_file:
                        missing_order_id_list = [line.strip() for line in order_id_file if line != None]
                    order_id_file.close()

                    missing_order_id_list = [int(x) for x in missing_order_id_list]
                    total_order_id_list.extend(missing_order_id_list)

        if os.path.isfile(last_downloaded_missing_order_id_file_path):
            last_downloaded_missing_order_id = FileIoHelper.read_last_downloaded_missing_order_id()
            total_order_id_list.append(int(last_downloaded_missing_order_id))
        else:
            total_order_id_list.append(1)

        sorted_order_id_list = sorted(total_order_id_list)

        min_order_id = sorted_order_id_list[0]
        max_order_id = sorted_order_id_list[-1]
        sorted_order_id_dic = {order_id: True for order_id in sorted_order_id_list}

        missing_order_id_list = []

        for order_id in range(min_order_id, max_order_id):
            if order_id not in sorted_order_id_dic:
                missing_order_id_list.append(order_id)

        return missing_order_id_list

    @staticmethod
    def create_timestamp_list_missing_values(get_type_string, status_string):
        """
        A method to determine which timestamps are missed
        :param get_type_string: the type of orders
        :param status_string: the status of the orders
        :return: a list of timestamps
        """

        to_check_timestamp_folders_path = FileHandler.get_base_path("to_check_timestamp_folders")
        path_to_check_logs = str(to_check_timestamp_folders_path) + "\\to_check_" + status_string.lower() + "_" + get_type_string.lower() + "_orders.json"

        with open(path_to_check_logs, 'r', encoding='utf-8') as logs_file:
            stripped_lines = [line.strip() for line in logs_file if line != None]
        logs_file.close()

        max_amount_checked = 0
        for line_index, line in enumerate(stripped_lines):

            json_object = json.loads(line)
            timestamp_list = json_object["timestamp_list"]
            number_times_checked = len(timestamp_list)

            if number_times_checked > max_amount_checked:
                max_amount_checked = number_times_checked

        first_to_check_list = []
        second_to_check_list = []
        third_to_check_list = []

        for line_index, line in enumerate(stripped_lines):

            json_object = json.loads(line)
            order_id_list = json_object["order_id_list"]
            number_downloaded = len(order_id_list)

            new_entry = (json_object["from"], json_object["to"], order_id_list)

            if max_amount_checked == 1:
                if number_downloaded == 0:
                    first_to_check_list.append(new_entry)
                else:
                    second_to_check_list.append(new_entry)

            else:
                if number_downloaded < max_amount_checked:
                    if number_downloaded == 0:
                        first_to_check_list.append(new_entry)
                    else:
                        second_to_check_list.append(new_entry)
                else:
                        third_to_check_list.append(new_entry)

        first_to_check_list.extend(second_to_check_list)
        first_to_check_list.extend(third_to_check_list)

        return first_to_check_list
