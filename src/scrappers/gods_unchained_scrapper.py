import os

import requests
import json

from src.scrappers.immutable_x_scrapper import Immutable_X_Scrapper
from src.util.files import file_handler
from src.util.files.file_handler import File_Handler


class Gods_Unchained_Scrapper():
    _file_handler = file_handler.File_Handler()
    _gods_unchained_api = "https://api.godsunchained.com/v0/"

    _url = "https://api.x.immutable.com/v1"
    _gods_unchained_collection_token_address = "0xacb3c6a43d15b907e8433077b6d38ae40936fe2c"
    _x_immutable_scrapper = Immutable_X_Scrapper()

    def __init__(self):
        None

    @classmethod
    def download_all_prototypes(cls):

        print("Downloading all Gods Unchained Card Information")

        url = cls._gods_unchained_api + "/proto"

        headers = {"Accept": "application/json"}
        response = requests.request("GET", url, headers=headers)

        parsed = json.loads(response.text)

        total_number_of_pages = int(int(parsed['total']) / int(parsed["perPage"])) + 2
        resource_list = parsed["records"]

        print(f"Page 1/{total_number_of_pages - 1}")

        for next_page in range(2, total_number_of_pages):

            print(f"Page {next_page}/{total_number_of_pages - 1}")

            next_url = url + "?page=" + str(next_page)

            next_response = requests.request("GET", next_url, headers=headers)
            next_parsed = json.loads(next_response.text)

            next_resource_list = next_parsed["records"]
            resource_list.extend(next_resource_list)

        name_entry_dic = {entry.pop("name") : entry for entry in resource_list}

        path_to_original_assets = File_Handler.get_base_path("gods_unchained_original_assets")
        with open(path_to_original_assets, 'r', encoding='utf-8') as gods_unchained_original_assets_file:
            gods_unchained_original_assets_dic = json.load(gods_unchained_original_assets_file)
        gods_unchained_original_assets_file.close()

        for name, info in name_entry_dic.items():
            gods_unchained_original_assets_dic[name] = info

        with open(path_to_original_assets, 'w', encoding='utf-8') as gods_unchained_assets_file:
            json.dump(gods_unchained_original_assets_dic, gods_unchained_assets_file, ensure_ascii=False, indent=4)

    @classmethod
    def get_info_about_unknown_asset_id(cls, asset_id):
        result_json = cls._x_immutable_scrapper.get_info_of_one_asset(asset_id)

        additional_info_dic = {}
        additional_info_dic["card_god"] = result_json["metadata"]["god"]
        additional_info_dic["card_rarity"] = result_json["metadata"]["rarity"]
        additional_info_dic["card_tribe"] = None
        additional_info_dic["card_set"] = result_json["metadata"]["set"]
        additional_info_dic["card_collectable"] = None
        additional_info_dic["card_live"] = None
        additional_info_dic["card_quality"] = result_json["metadata"]["quality"]

        path_to_unknown_assets = File_Handler.get_base_path("gods_unchained_unknown_assets")

        if os.path.isfile(path_to_unknown_assets):
            with open(path_to_unknown_assets, 'r', encoding='utf-8') as gods_unchained_updated_assets_file:
                gods_unchained_updated_assets_dic = json.load(gods_unchained_updated_assets_file)
            gods_unchained_updated_assets_file.close()
        else:
            gods_unchained_updated_assets_dic = {}

        new_entry = {}
        new_entry["id"] = result_json["metadata"]["proto"]
        new_entry["effect"] = result_json["metadata"]["effect"]
        new_entry["god"] = result_json["metadata"]["god"]
        new_entry["rarity"] = result_json["metadata"]["rarity"]

        new_entry["tribe"] = {}
        new_entry["tribe"]["String"] = None
        new_entry["tribe"]["Valid"] = None

        new_entry["mana"] = result_json["metadata"]["mana"]

        new_entry["attack"] = {}
        new_entry["attack"]["Int64"] = result_json["metadata"]["attack"]
        new_entry["attack"]["Valid"] = True

        new_entry["health"] = {}
        new_entry["health"]["Int64"] = result_json["metadata"]["health"]
        new_entry["health"]["Valid"] = True

        new_entry["type"] = result_json["metadata"]["type"]
        new_entry["set"] = result_json["metadata"]["set"]
        new_entry["collectable"] = True
        new_entry["live"] = True
        new_entry["art_id"] = None
        new_entry["lib_id"] = None

        gods_unchained_updated_assets_dic[result_json["metadata"]["name"]] = new_entry

        with open(path_to_unknown_assets, 'w', encoding='utf-8') as gods_unchained_updated_assets_file:
            json.dump(gods_unchained_updated_assets_dic, gods_unchained_updated_assets_file, ensure_ascii=False, indent=4)

        card_name = result_json["metadata"]["name"]
        print(f"Name found card: {card_name}")

        return additional_info_dic


    @classmethod
    def get_all_gods_unchained_assets(cls):

        path_to_original_assets = File_Handler.get_base_path("gods_unchained_original_assets")

        if os.path.isfile(path_to_original_assets) == False:
            Gods_Unchained_Scrapper.download_all_prototypes()

        with open(path_to_original_assets, 'r', encoding='utf-8') as gods_unchained_original_assets_file:
            gods_unchained_original_assets_dic = json.load(gods_unchained_original_assets_file)
        gods_unchained_original_assets_file.close()

        path_to_unknown_assets = File_Handler.get_base_path("gods_unchained_unknown_assets")
        if os.path.isfile(path_to_unknown_assets):
            with open(path_to_unknown_assets, 'r', encoding='utf-8') as gods_unchained_updated_assets_file:
                gods_unchained_updated_assets_dic = json.load(gods_unchained_updated_assets_file)
            gods_unchained_updated_assets_file.close()

            for card_name, info in gods_unchained_updated_assets_dic.items():
                gods_unchained_original_assets_dic[card_name] = info

        return gods_unchained_original_assets_dic
