import json
import os
from src.util.files.filehandler import FileHandler
from src.util.files.fileiohelper import FileIoHelper
from src.util.helpers import WindowsPathHelper
from src.util.todownloadlistcreator import ToDownloadListCreator


class MissedOrdersHelper:
    """
    A helper class to deal with missed orders
    """

    def __init__(self):
        """
        The constructor
        """
        pass

    @staticmethod
    def create_still_to_be_downloaded_order_ids_list():
        """
        A method to determine the id of the still-to-be-downloaded orders
        :return: a list of the missing order ids
        """

        print(f"Determining Missed Order IDs")

        missing_order_id_list = ToDownloadListCreator.create_missing_order_id_list()
        last_missing_order_id = missing_order_id_list[-1]

        FileIoHelper.write_still_to_be_downloaded_order_ids_to_file(missing_order_id_list)
        FileIoHelper.write_last_downloaded_missing_order_id_to_file(last_missing_order_id)
        # File_IO_Helper.delete_to_be_processed_order_ids()

        return missing_order_id_list

    @staticmethod
    def write_other_collections_list(other_collection_list):
        """
        A method to write missed orders that do not belong to the Gods Unchained collection to file
        :param other_collection_list: a list of orders that do not belong to Gods Unchained
        :return: None
        """

        other_collections_folder_path = FileHandler.get_base_path("other_collections_folder")

        for json_string, collection_name in other_collection_list:

            cleaned_collection_name = WindowsPathHelper.convert_string_to_legal_windows_path(collection_name)

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
        """
        A method to get the collection address associated with an order
        :param order_json: the order as a dictionary
        :return: the collection address
        """

        if "decimals" in order_json["buy"]["data"]:
            collection_address = order_json["sell"]["data"]["token_address"]

        elif "decimals" in order_json["sell"]["data"]:
            collection_address = order_json["buy"]["data"]["token_address"]

        else:
            print("#")
            print(order_json)
            print("#")
            raise Exception("Collection Filter - information_dic - where is the collection address")

        return str(collection_address)

    @staticmethod
    def get_collection_name(order_json):
        """
        A method to get the collection name associated with an order
        :param order_json: the order as a dictionary
        :return: the collection nam
        """

        if "decimals" in order_json["buy"]["data"]:
            collection_name = order_json["sell"]["data"]["properties"]["collection"]["name"]

        elif "decimals" in order_json["sell"]["data"]:
            collection_name = order_json["buy"]["data"]["properties"]["collection"]["name"]

        else:
            print("#")
            print(order_json)
            print("#")
            raise Exception("Collection Filter - information_dic - where is the collection address")

        return str(collection_name)
