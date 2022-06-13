import glob
import json
import os.path
from datetime import datetime, timedelta
from dateutil import relativedelta
from util.files.file_handler import File_Handler
from util.files.file_io_helper import File_IO_Helper
from util.helpers import Safe_Datetime_Converter


class Double_Checking_Helper():

    def __init__(self):
        None

    @staticmethod
    def find_incorrect_orders_list(combined_list):

        log_list = []
        missed_order_json_list = []

        for result_list, comparison_dic in combined_list:
            from_timestamp_str = comparison_dic["from"]
            to_timestamp_str = comparison_dic["to"]
            comparison_list_dic = comparison_dic["comparison_list"]

            new_log_dic = {}
            new_log_dic["from"] = from_timestamp_str
            new_log_dic["to"] = to_timestamp_str

            status_missed_orders = {}

            for download_timestamp_str, order_json_list in result_list:
                for order_json in order_json_list:
                    status = order_json["status"].upper()
                    order_id = order_json["order_id"]

                    if status not in comparison_list_dic:

                        if status in status_missed_orders:
                            status_order_entry = status_missed_orders[status]
                        else:
                            status_order_entry = (download_timestamp_str, [])

                        order_id_list = status_order_entry[1]
                        order_id_list.append(order_id)

                        status_missed_orders[status] = (status_order_entry[0], order_id_list)
                        missed_order_json_list.append(order_json)


                    else:
                        comparison_status_list = comparison_list_dic[status]

                        if order_id not in comparison_status_list:

                            if status in status_missed_orders:
                                status_order_entry = status_missed_orders[status]
                            else:
                                status_order_entry = (download_timestamp_str, [])

                            order_id_list = status_order_entry[1]
                            order_id_list.append(order_id)

                            status_missed_orders[status] = (status_order_entry[0], order_id_list)
                            missed_order_json_list.append(order_json)

            new_log_dic["status_missed_orders_dic"] = status_missed_orders
            log_list.append(new_log_dic)

        log_list.sort(key = lambda x: x["from"], reverse=True)

        return log_list, missed_order_json_list


    @staticmethod
    def check_if_double_checking_going_on():
        double_checking_month_overview_folder = File_Handler.get_base_path("double_checking_month_overview_folder")

        search_string_files = str(double_checking_month_overview_folder) + "\\*_double_checking.json"
        json_files = glob.glob(search_string_files)

        check_boolean = len(json_files) > 0

        return check_boolean

    @staticmethod
    def get_double_checking_file_paths():
        double_checking_month_overview_folder = File_Handler.get_base_path("double_checking_month_overview_folder")

        search_string_files = str(double_checking_month_overview_folder) + "\\*_double_checking.json"
        json_files = glob.glob(search_string_files)

        json_files.sort(key= lambda x: int(os.path.basename(x).split("_")[0]))

        return json_files


    @staticmethod
    def create_double_checking_list(get_type_string):

        print(f"Determining To Be Double Checked Orders")

        double_checking_month_overview_folder = File_Handler.get_base_path("double_checking_month_overview_folder")

        start_time_stamp = datetime.strptime("2021-06", "%Y-%m")
        start_time_year = start_time_stamp.year
        start_time_month = start_time_stamp.month
        first_key = str(start_time_year) + "_" + str(start_time_month)

        current_utc = datetime.utcnow()
        current_year = current_utc.year
        current_month = current_utc.month
        current_day = current_utc.day
        final_key = str(current_year) + "_" + str(current_month)

        not_caught_up = True

        overall_year_month_dic = {}
        overall_year_month_dic[first_key] = {}

        while not_caught_up:
            timestamp_plus_month = start_time_stamp + relativedelta.relativedelta(months=1)

            next_timestamp_year = timestamp_plus_month.year
            next_timestamp_month = timestamp_plus_month.month

            next_key = str(next_timestamp_year) + "_" + str(next_timestamp_month)
            overall_year_month_dic[next_key] = {}

            start_time_stamp = timestamp_plus_month

            if final_key == next_key:
                not_caught_up = False


        path_to_timestamp_folder = File_Handler.get_base_path("timestamps_folder")
        timestamp_path_list = []

        statuses = ["ACTIVE", "FILLED", "CANCELLED", "EXPIRED", "INACTIVE"]

        for status_string in statuses:
            timestamp_file_name = status_string.lower() + "_" + get_type_string.lower() + "_orders.json"
            path_to_timestamp_file = str(path_to_timestamp_folder) + "\\" + timestamp_file_name
            if os.path.isfile(path_to_timestamp_file):
                timestamp_path_list.append((status_string, path_to_timestamp_file))


        for status_string, timestamp_path in timestamp_path_list:

            timestamp_log_list = File_IO_Helper.read_timestamp_log_from_path(timestamp_path)

            alignment_boolean = False
            alignment_from_timestamp = None
            alignment_download_info_list = []

            for timestamp_dic in timestamp_log_list:

                from_timestamp = Safe_Datetime_Converter.string_to_datetime(timestamp_dic["from"])

                from_timestamp_year = from_timestamp.year
                from_timestamp_month = from_timestamp.month
                from_timestamp_day = from_timestamp.day

                from_timestamp_seconds = from_timestamp.second
                from_timestamp_microseconds = from_timestamp.microsecond

                to_timestamp = Safe_Datetime_Converter.string_to_datetime(timestamp_dic["to"])
                to_timestamp_seconds = to_timestamp.second
                to_timestamp_microseconds = to_timestamp.microsecond

                if not ((current_year == from_timestamp_year) and (current_month == from_timestamp_month) and (current_day == from_timestamp_day)):

                    if alignment_boolean:

                        if (to_timestamp_seconds != 0) or (to_timestamp_microseconds != 0):
                            alignment_download_info_list.extend(timestamp_dic["download_info_list"])

                        else:
                            alignment_from_timestamp_year = alignment_from_timestamp.year
                            alignment_from_timestamp_month = alignment_from_timestamp.month

                            alignment_download_info_list.extend(timestamp_dic["download_info_list"])

                            check_key = str(alignment_from_timestamp_year) + "_" + str(alignment_from_timestamp_month)
                            year_month_dic = overall_year_month_dic[check_key]

                            key = Safe_Datetime_Converter.datetime_to_string(alignment_from_timestamp) + "_" + timestamp_dic["to"]

                            if key in year_month_dic:
                                current_entry = year_month_dic[key]
                            else:
                                current_entry = {}

                            combined_order_id_list = []

                            for timestamp, order_id_list in alignment_download_info_list:
                                combined_order_id_list.extend(order_id_list)

                            current_entry[status_string] = combined_order_id_list
                            year_month_dic[key] = current_entry
                            overall_year_month_dic[check_key] = year_month_dic

                            alignment_boolean = False
                            alignment_from_timestamp = None
                            alignment_download_info_list = []

                    elif (to_timestamp_seconds != 0) or (to_timestamp_microseconds != 0):
                        alignment_boolean = True
                        alignment_from_timestamp = from_timestamp
                        alignment_download_info_list.extend(timestamp_dic["download_info_list"])

                    else:
                        check_key = str(from_timestamp_year) + "_" + str(from_timestamp_month)
                        year_month_dic = overall_year_month_dic[check_key]


                        key = timestamp_dic["from"] + "_" + timestamp_dic["to"]

                        if key in year_month_dic:
                            current_entry = year_month_dic[key]
                        else:
                            current_entry = {}


                        combined_order_id_list = []
                        for timestamp, order_id_list in timestamp_dic["download_info_list"]:
                            combined_order_id_list.extend(order_id_list)


                        current_entry[status_string] = combined_order_id_list
                        year_month_dic[key] = current_entry
                        overall_year_month_dic[check_key] = year_month_dic


        double_checking_file_path_list = []

        file_count = 0

        for year_month_key, year_month_dic in overall_year_month_dic.items():

            to_download_list = [(key.split("_")[0], key.split("_")[1], value) for key, value in year_month_dic.items()]

            dic_list = []
            for from_timestamp_str, to_timestamp_str, order_id_list in to_download_list:
                dic_entry = {}
                dic_entry["from"] = from_timestamp_str
                dic_entry["to"] = to_timestamp_str
                dic_entry["comparison_list"] = order_id_list
                dic_list.append(dic_entry)


            sorted_logs = sorted(dic_list, key=lambda x: x["from"], reverse=True)

            month_overview_file_path = str(double_checking_month_overview_folder) + "\\" + str(file_count) + "_" + year_month_key + "_double_checking.json"

            File_IO_Helper.write_still_to_be_double_checked_file_to_path(sorted_logs, month_overview_file_path)

            file_count = file_count + 1

            double_checking_file_path_list.append(month_overview_file_path)


        double_checking_file_path_list.sort(key=lambda x: int(os.path.basename(x).split("_")[0]))

        return double_checking_file_path_list
