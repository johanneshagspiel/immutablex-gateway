import json
import os
from util.files.file_handler import File_Handler
from util.files.file_io_helper import File_IO_Helper
from util.helpers import Windows_Path_Helper
from util.to_download_list_creator import To_Download_List_Creator


class Missed_Orders_Helper:

    def __init__(self):
        None

    @staticmethod
    def check_if_missed_orders_going_on():
        None

    @staticmethod
    def create_still_to_be_downloaded_order_ids_list():

        print(f"Determining Missed Order IDs")

        missing_order_id_list = To_Download_List_Creator.create_missing_order_id_list()
        last_missing_order_id = missing_order_id_list[-1]

        File_IO_Helper.write_still_to_be_downloaded_order_ids_to_file(missing_order_id_list)
        File_IO_Helper.write_last_downloaded_missing_order_id_to_file(last_missing_order_id)
        # File_IO_Helper.delete_to_be_processed_order_ids()

        return missing_order_id_list


    @staticmethod
    def write_other_collections_list(other_collection_list):

        other_collections_folder_path = File_Handler.get_base_path("other_collections_folder")

        for json_string, collection_name in other_collection_list:

            cleaned_collection_name = Windows_Path_Helper.convert_string_to_legal_windows_path(collection_name)

            store_path = str(other_collections_folder_path) + "\\" + str(cleaned_collection_name)

            if not os.path.isdir(store_path):
                os.mkdir(store_path)

            file_store_path = str(store_path) + "\\raw_missed_orders_" + str(cleaned_collection_name) + ".json"

            with open(file_store_path, 'a', encoding='utf-8') as store_file:
                json.dump(json_string, store_file, ensure_ascii=False)
                store_file.write("\n")
            store_file.close()


    @staticmethod
    def get_collection_address(order_json):

        if "decimals" in order_json["buy"]["data"]:
            collection_address = order_json["sell"]["data"]["token_address"]

        elif "decimals" in order_json["sell"]["data"]:
            collection_address = order_json["buy"]["data"]["token_address"]

        else:
            print("#")
            print(order_json)
            print("#")
            raise Exception("Collection Filter - get - where is the collection address")

        return str(collection_address)


    @staticmethod
    def get_collection_name(order_json):

        if "decimals" in order_json["buy"]["data"]:
            collection_name = order_json["sell"]["data"]["properties"]["collection"]["name"]

        elif "decimals" in order_json["sell"]["data"]:
            collection_name = order_json["buy"]["data"]["properties"]["collection"]["name"]

        else:
            print("#")
            print(order_json)
            print("#")
            raise Exception("Collection Filter - get - where is the collection address")

        return str(collection_name)
