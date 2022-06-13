import glob
import json
import os
import shutil
import time
from datetime import datetime
from objects.orders.gods_unchained.order_administrator_gu import Order_Administrator_GU
from util.files.file_handler import File_Handler
from util.helpers import Safe_Datetime_Converter


class Processing_File_Helper():


    @staticmethod
    def get_order_list_for_type_order_processing(get_type_string, status_string):

        last_updated_timestamp_folder = File_Handler.get_base_path("last_updated_timestamp_folder")
        processing_data_folder_path = File_Handler.get_base_path("processing_data_folder")

        last_active_order_updated_timestamp_file_path = str(last_updated_timestamp_folder) + "\\" + "last_update_timestamp_active_" + get_type_string.lower() + ".json"

        if os.path.isfile(last_active_order_updated_timestamp_file_path):
            with open(last_active_order_updated_timestamp_file_path, 'r', encoding='utf-8') as last_active_order_updated_timestamp_file:
                last_active_order_updated_timestamp_str = json.load(last_active_order_updated_timestamp_file)
            last_active_order_updated_timestamp_file.close()

            last_active_order_updated_timestamp = Safe_Datetime_Converter.string_to_datetime(last_active_order_updated_timestamp_str)

        else:
            last_active_order_updated_timestamp = datetime.strptime("2021-06-01T00:00:00.00Z", "%Y-%m-%dT%H:%M:%S.%fZ")


        to_be_processed_file_path_list = Processing_File_Helper.get_path_list_for_type_order_processing(get_type_string=get_type_string, status_string=status_string)
        to_be_processed_order_list = Order_Administrator_GU.create_order_list_from_path_list(to_be_processed_file_path_list)

        if status_string.lower() == "active":
            update_timestamp_list = [order.updated_timestamp for order in to_be_processed_order_list]

            if len(update_timestamp_list) > 0:
                max_timestamp = max(update_timestamp_list)

                max_timestamp_str = Safe_Datetime_Converter.datetime_to_string(max_timestamp)
                with open(last_active_order_updated_timestamp_file_path, 'w', encoding='utf-8') as last_active_order_updated_timestamp_file:
                    json.dump(max_timestamp_str, last_active_order_updated_timestamp_file, ensure_ascii=False, indent=4)
                last_active_order_updated_timestamp_file.close()

            final_order_list = to_be_processed_order_list

        else:
            before_last_active_update_timestamp_list = [order for order in to_be_processed_order_list if order.updated_timestamp <= last_active_order_updated_timestamp]
            remainder_file_path = str(processing_data_folder_path) + "\\" + status_string.lower() + "_" + get_type_string.lower() + "_orders_remainder_to_be_processed.json"

            if len(before_last_active_update_timestamp_list) < len(to_be_processed_order_list):
                after_last_active_update_timestamp_list = [order for order in to_be_processed_order_list if order.updated_timestamp > last_active_order_updated_timestamp]

                with open(remainder_file_path, 'w', encoding='utf-8') as remainder_file:
                    for order_object in after_last_active_update_timestamp_list:
                        if order_object != None:
                            json.dump(json.dumps(order_object.to_print_dic()), remainder_file, ensure_ascii=False, indent=4)
                            remainder_file.write("\n")
                remainder_file.close()

            else:
                if os.path.isfile(remainder_file_path):
                    os.remove(remainder_file_path)

            final_order_list = before_last_active_update_timestamp_list

        return final_order_list


    @staticmethod
    def get_path_list_for_type_order_processing(get_type_string, status_string):

        processing_data_folder_path = str(File_Handler.get_base_path("processing_data_folder"))

        to_be_processed_path = processing_data_folder_path + "\\" + status_string.lower() + "_" + get_type_string.lower() + "_orders_to_be_processed.json"
        double_checked_to_be_processed_path = processing_data_folder_path + "\\" + status_string.lower() + "_" + get_type_string.lower() + "_orders_double_checked_to_be_processed.json"
        remainder_to_be_processed_path = processing_data_folder_path + "\\" + status_string.lower() + "_" + get_type_string.lower() + "_orders_remainder_to_be_processed.json"
        purchase_error_to_be_processed_path = processing_data_folder_path + "\\" + status_string.lower() + "_" + get_type_string.lower() + "_orders_purchase_error_to_be_processed.json"
        #missed_to_be_processed_path = processing_data_folder_path + "\\" + status_string.lower() + "_" + get_type_string.lower() + "_orders_missed_to_be_processed.json"

        to_be_checked_list = [to_be_processed_path, double_checked_to_be_processed_path, remainder_to_be_processed_path, purchase_error_to_be_processed_path]
        path_list = [path for path in to_be_checked_list if os.path.isfile(path)]

        return path_list


    @staticmethod
    def delete_to_be_processed_orders(get_type_string, status_string):

        processing_data_folder_path = str(File_Handler.get_base_path("processing_data_folder"))

        to_be_processed_path = processing_data_folder_path + "\\" + status_string.lower() + "_" + get_type_string.lower() + "_orders_to_be_processed.json"
        double_checked_to_be_processed_path = processing_data_folder_path + "\\" + status_string.lower() + "_" + get_type_string.lower() + "_orders_double_checked_to_be_processed.json"
        purchase_error_to_be_processed_path = processing_data_folder_path + "\\" + status_string.lower() + "_" + get_type_string.lower() + "_orders_purchase_error_to_be_processed.json"
        #remainder_to_be_processed_path = processing_data_folder_path + "\\" + status_string.lower() + "_" + get_type_string.lower() + "_orders_remainder_to_be_processed.json"
        #missed_to_be_processed_path = processing_data_folder_path + "\\" + status_string.lower() + "_" + get_type_string.lower() + "_orders_missed_to_be_processed.json"

        to_be_checked_list = [to_be_processed_path, double_checked_to_be_processed_path, purchase_error_to_be_processed_path]
        path_list = [path for path in to_be_checked_list if os.path.isfile(path)]

        for path in path_list:
            os.remove(path)

class File_Mover_Helper():

    @staticmethod
    def move_to_be_processed_files_for_processing(get_type_str):

        processing_data_folder_path = str(File_Handler.get_base_path("processing_data_folder"))

        to_be_processed_path_name_list = []
        status_list = ["active", "cancelled", "filled", "inactive", "expired"]

        for status in status_list:
            to_be_processed_path = status.lower() + "_" + get_type_str.lower() + "_orders_to_be_processed"
            #missed_to_be_processed_path = status.lower() + "_" + get_type_str.lower() + "_orders_missed_to_be_processed"
            double_checked_to_be_processed_path = status.lower() + "_" + get_type_str.lower() + "_orders_double_checked_to_be_processed"
            purchase_error_to_be_processed_path = status.lower() + "_" + get_type_str.lower() + "_orders_purchase_error_to_be_processed"

            to_be_processed_path_name_list.extend([to_be_processed_path, double_checked_to_be_processed_path, purchase_error_to_be_processed_path])

        to_be_processed_path_list = [File_Handler.get_base_path(name) for name in to_be_processed_path_name_list]
        existing_file_path_list = [path for path in to_be_processed_path_list if os.path.isfile(path)]
        number_of_potentially_to_be_moved_files = len(existing_file_path_list)

        search_string_files = str(processing_data_folder_path) + "\\*.json"
        json_files = glob.glob(search_string_files)
        number_already_existing_files = len(json_files)
        number_of_to_be_processed_files = number_of_potentially_to_be_moved_files + number_already_existing_files

        File_Mover_Helper._move_to_be_processed_files(existing_file_path_list)

        return number_of_to_be_processed_files


    @staticmethod
    def _move_to_be_processed_files(to_be_processed_file_path_list):

        processing_data_folder_path = str(File_Handler.get_base_path("processing_data_folder"))

        for from_path in to_be_processed_file_path_list:
            base_name = os.path.basename(from_path)
            to_path = processing_data_folder_path + "\\" + base_name

            if os.path.isfile(to_path):
                print(f"File {to_path} already exists")

            else:
                not_yet_moved = True

                while not_yet_moved:
                    try:
                        shutil.move(from_path, to_path)
                        not_yet_moved = False

                    except PermissionError:
                        print(f"File {from_path} currently in use - we will wait for 2 seconds")
                        time.sleep(2)
