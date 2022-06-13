import os

from parallel_workers.parallel_list_downloader import Parallel_List_Downloader
from scrappers.gods_unchained_poller import Gods_Unchained_Poller
from util.files.file_handler import File_Handler
from util.files.file_io_helper import File_IO_Helper
from util.number_converter import Number_Converter


class Competition_Handler():

    def __init__(self):
        None


    @staticmethod
    def check_competition_file(inventory_list):

        print(f"Checking Competition")

        competition_folder = File_Handler.get_base_path("competition_folder")

        currencies = ["GODS", "ETH"]

        gp = Gods_Unchained_Poller()
        pld = Parallel_List_Downloader()

        combined_info_list = []

        for inventory_entry in inventory_list:

            for currency in currencies:

                file_name = inventory_entry.card_name + "_" + inventory_entry.token_id + "_" + str(currency) + ".json"
                file_path = str(competition_folder) + "\\" + file_name

                if not os.path.isfile(file_path):

                    all_card_available = gp._get_all_active_sell_jsons_for_a_currency(asset_name=inventory_entry.card_name, currency_string=inventory_entry.sale_currency)

                    all_order_ids_competition = [json["order_id"] for json in all_card_available if json["sell"]["data"]["token_id"] != inventory_entry.token_id]

                    all_order_competition = pld.parallel_download_list(all_order_ids_competition, 250, "get_jsons_of_competition_by_order_id")

                    competition_price_dic = {}
                    for entry in all_order_competition:
                        token_id = entry["sell"]["data"]["token_id"]
                        base_price = Number_Converter.get_float_from_quantity_decimal(entry["buy"]["data"]["quantity"], entry["buy"]["data"]["decimals"])
                        if "fees" in entry:
                            fee_quantity = entry["fees"][0]["amount"]
                            fee_decimals = entry["fees"][0]["token"]["data"]["decimals"]
                            fee = Number_Converter.get_float_from_quantity_decimal(quantity=fee_quantity, decimals=fee_decimals)
                        else:
                            if inventory_entry.sale_currency == "ETH":
                                fee = base_price * 0.00990099009900991
                            elif inventory_entry.sale_currency == "GODS":
                                fee = base_price * 0.01


                        combined_price = base_price + fee

                        competition_price_dic[token_id] = (base_price, combined_price)


                    File_IO_Helper.write_competition_price_file(file_path, competition_price_dic)

                else:
                    competition_price_dic = File_IO_Helper.read_competition_price_file(file_path)

                if currency == inventory_entry.sale_currency:
                    combined_info_list.append((inventory_entry, competition_price_dic))

        return combined_info_list


    @staticmethod
    def check_competition_file_of_inventory_entry(inventory_entry):

        competition_folder = File_Handler.get_base_path("competition_folder")

        gp = Gods_Unchained_Poller()
        pld = Parallel_List_Downloader()

        currency = inventory_entry.sale_currency

        file_name = inventory_entry.card_name + "_" + inventory_entry.token_id + "_" + str(currency) + ".json"
        file_path = str(competition_folder) + "\\" + file_name

        if not os.path.isfile(file_path):

            all_card_available = gp._get_all_active_sell_jsons_for_a_currency(asset_name=inventory_entry.card_name, currency_string=currency)

            all_order_ids_competition = [json["order_id"] for json in all_card_available if json["sell"]["data"]["token_id"] != inventory_entry.token_id]

            all_order_competition = pld.parallel_download_list(all_order_ids_competition, 250, "get_jsons_of_competition_by_order_id")

            competition_price_dic = {}
            for entry in all_order_competition:
                token_id = entry["sell"]["data"]["token_id"]
                base_price = Number_Converter.get_float_from_quantity_decimal(entry["buy"]["data"]["quantity"], entry["buy"]["data"]["decimals"])
                if "fees" in entry:
                    fee_quantity = entry["fees"][0]["amount"]
                    fee_decimals = entry["fees"][0]["token"]["data"]["decimals"]
                    fee = Number_Converter.get_float_from_quantity_decimal(quantity=fee_quantity, decimals=fee_decimals)

                else:
                    if currency == "ETH":
                        fee = base_price * 0.00990099009900991
                    elif currency == "GODS":
                        fee = base_price * 0.01

                combined_price = base_price + fee

                competition_price_dic[token_id] = (base_price, combined_price)

            File_IO_Helper.write_competition_price_file(file_path, competition_price_dic)

        else:
            competition_price_dic = File_IO_Helper.read_competition_price_file(file_path)

        result_tuple = (inventory_entry, competition_price_dic)

        return result_tuple


    @staticmethod
    def add_missing_orders_to_competition_file(missing_active_orders_list, prev_competition_price_dic, inventory_entry):

        competition_folder = File_Handler.get_base_path("competition_folder")
        file_name = inventory_entry.card_name + "_" + inventory_entry.token_id + "_" + inventory_entry.sale_currency + ".json"
        file_path = str(competition_folder) + "\\" + file_name

        pld = Parallel_List_Downloader()

        missed_jsons = pld.parallel_download_list(missing_active_orders_list, 250, "get_jsons_of_competition_by_order_id")

        additional_info_list = []

        for entry in missed_jsons:

            if "sell" in entry:

                token_id = entry["sell"]["data"]["token_id"]

                base_price = Number_Converter.get_float_from_quantity_decimal(entry["buy"]["data"]["quantity"], entry["buy"]["data"]["decimals"])
                if "fees" in entry:

                    fee_quantity = entry["fees"][0]["amount"]
                    fee_decimals = entry["fees"][0]["token"]["data"]["decimals"]
                    fee = Number_Converter.get_float_from_quantity_decimal(quantity=fee_quantity, decimals=fee_decimals)
                else:

                    if inventory_entry.sale_currency == "ETH":
                        fee = base_price * 0.00990099009900991
                    elif inventory_entry.sale_currency == "GODS":
                        fee = base_price * 0.01
                    #fee = base_price * 0.01

                combined_price = base_price + fee

                prev_competition_price_dic[token_id] = (base_price, combined_price)
                additional_info_list.append((token_id, combined_price))


        File_IO_Helper.write_competition_price_file(file_path, prev_competition_price_dic)

        return prev_competition_price_dic, additional_info_list


    @staticmethod
    def delete_competition_file_after_sale(sold_order):

        competition_folder = File_Handler.get_base_path("competition_folder")
        currencies = ["GODS", "ETH"]

        for currency in currencies:
            file_name = sold_order.card_name + "_" + sold_order.token_id + "_" + str(currency) + ".json"
            file_path = str(competition_folder) + "\\" + file_name

            os.remove(file_path)

    @staticmethod
    def delete_competition_file_after_multiple_sales(sold_order_list):

        competition_folder = File_Handler.get_base_path("competition_folder")
        currencies = ["GODS", "ETH"]

        for sold_order, inventory_entry in sold_order_list:
            for currency in currencies:
                file_name = sold_order.card_name + "_" + sold_order.token_id + "_" + str(currency) + ".json"
                file_path = str(competition_folder) + "\\" + file_name

                os.remove(file_path)