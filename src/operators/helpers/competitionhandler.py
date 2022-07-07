import os
from src.parallel_workers.parallellistdownloader import ParallelListDownloader
from src.scrappers.godsunchainedpoller import GodsUnchainedPoller
from src.util.files.filehandler import FileHandler
from src.util.files.fileiohelper import FileIoHelper
from src.util.numberconverter import NumberConverter


class CompetitionHandler:
    """
    A helper class to handle the information associated with offers made by the competition
    """

    def __init__(self):
        """
        The constructor of the CompetitionHandler
        """
        pass

    @staticmethod
    def check_competition_file(inventory_list):
        """
        A method to check whether for every card in the inventory the corresponding offers by the competitors have been
        downloaded. If not, all offers by the competitors are downloaded and stored in a file. The reason for this is
        to minimize the amount of requests made
        :param inventory_list: a list of all cards in the inventory of the user
        :return: the list of all information about offers made by competitors
        """

        print(f"Checking Competition")

        competition_folder = FileHandler.get_base_path("competition_folder")

        currencies = ["GODS", "ETH"]

        gp = GodsUnchainedPoller()
        pld = ParallelListDownloader()

        combined_info_list = []

        for inventory_entry in inventory_list:

            for currency in currencies:

                file_name = inventory_entry.card_name + "_" + inventory_entry.token_id + "_" + str(currency) + ".json"
                file_path = str(competition_folder) + "\\" + file_name

                if not os.path.isfile(file_path):

                    all_card_available = gp._get_all_active_sell_jsons_for_a_currency(
                        asset_name=inventory_entry.card_name, currency_string=inventory_entry.sale_currency)

                    all_order_ids_competition = [json["order_id"] for json in all_card_available
                                                 if json["sell"]["data"]["token_id"] != inventory_entry.token_id]

                    all_order_competition = pld.parallel_download_list(all_order_ids_competition, 250,
                                                                       "get_jsons_of_competition_by_order_id")

                    competition_price_dic = {}
                    for entry in all_order_competition:
                        token_id = entry["sell"]["data"]["token_id"]
                        base_price = NumberConverter.get_float_from_quantity_decimal(entry["buy"]["data"]["quantity"],
                                                                                     entry["buy"]["data"]["decimals"])
                        if "fees" in entry:
                            fee_quantity = entry["fees"][0]["amount"]
                            fee_decimals = entry["fees"][0]["token"]["data"]["decimals"]
                            fee = NumberConverter.get_float_from_quantity_decimal(quantity=fee_quantity,
                                                                                  decimals=fee_decimals)
                        else:
                            if inventory_entry.sale_currency == "ETH":
                                fee = base_price * 0.00990099009900991
                            elif inventory_entry.sale_currency == "GODS":
                                fee = base_price * 0.01

                        combined_price = base_price + fee

                        competition_price_dic[token_id] = (base_price, combined_price)

                    FileIoHelper.write_competition_price_file(file_path, competition_price_dic)

                else:
                    competition_price_dic = FileIoHelper.read_competition_price_file(file_path)

                if currency == inventory_entry.sale_currency:
                    combined_info_list.append((inventory_entry, competition_price_dic))

        return combined_info_list

    @staticmethod
    def check_competition_file_of_inventory_entry(inventory_entry):
        """
        Check if for one card all offers by the competitors have been downloaded
        :param inventory_entry: the inventory entry of the card to check
        :return: the information of the offers made by the competitors
        """

        competition_folder = FileHandler.get_base_path("competition_folder")

        gp = GodsUnchainedPoller()
        pld = ParallelListDownloader()

        currency = inventory_entry.sale_currency

        file_name = inventory_entry.card_name + "_" + inventory_entry.token_id + "_" + str(currency) + ".json"
        file_path = str(competition_folder) + "\\" + file_name

        if not os.path.isfile(file_path):

            all_card_available = gp._get_all_active_sell_jsons_for_a_currency(asset_name=inventory_entry.card_name,
                                                                              currency_string=currency)

            all_order_ids_competition = [json["order_id"] for json in all_card_available
                                         if json["sell"]["data"]["token_id"] != inventory_entry.token_id]

            all_order_competition = pld.parallel_download_list(all_order_ids_competition, 250,
                                                               "get_jsons_of_competition_by_order_id")

            competition_price_dic = {}
            for entry in all_order_competition:
                token_id = entry["sell"]["data"]["token_id"]
                base_price = NumberConverter.get_float_from_quantity_decimal(entry["buy"]["data"]["quantity"],
                                                                             entry["buy"]["data"]["decimals"])
                if "fees" in entry:
                    fee_quantity = entry["fees"][0]["amount"]
                    fee_decimals = entry["fees"][0]["token"]["data"]["decimals"]
                    fee = NumberConverter.get_float_from_quantity_decimal(quantity=fee_quantity, decimals=fee_decimals)

                else:
                    if currency == "ETH":
                        fee = base_price * 0.00990099009900991
                    elif currency == "GODS":
                        fee = base_price * 0.01

                combined_price = base_price + fee

                competition_price_dic[token_id] = (base_price, combined_price)

            FileIoHelper.write_competition_price_file(file_path, competition_price_dic)

        else:
            competition_price_dic = FileIoHelper.read_competition_price_file(file_path)

        result_tuple = (inventory_entry, competition_price_dic)

        return result_tuple

    @staticmethod
    def add_missing_orders_to_competition_file(missing_active_orders_list, prev_competition_price_dic, inventory_entry):
        """
        Add a list of missed offers by competitors to the competitor's information file
        :param missing_active_orders_list: a list of orders by competitors found
        :param prev_competition_price_dic: the previous competitor's information file
        :param inventory_entry: the inventory entry associated with a card
        :return: the updated competitor information file
        """

        competition_folder = FileHandler.get_base_path("competition_folder")
        file_name = inventory_entry.card_name + "_" + inventory_entry.token_id + "_" \
                    + inventory_entry.sale_currency + ".json"
        file_path = str(competition_folder) + "\\" + file_name

        pld = ParallelListDownloader()

        missed_jsons = pld.parallel_download_list(missing_active_orders_list, 250,
                                                  "get_jsons_of_competition_by_order_id")

        additional_info_list = []

        for entry in missed_jsons:

            if "sell" in entry:

                token_id = entry["sell"]["data"]["token_id"]

                base_price = NumberConverter.get_float_from_quantity_decimal(entry["buy"]["data"]["quantity"],
                                                                             entry["buy"]["data"]["decimals"])
                if "fees" in entry:

                    fee_quantity = entry["fees"][0]["amount"]
                    fee_decimals = entry["fees"][0]["token"]["data"]["decimals"]
                    fee = NumberConverter.get_float_from_quantity_decimal(quantity=fee_quantity, decimals=fee_decimals)
                else:

                    if inventory_entry.sale_currency == "ETH":
                        fee = base_price * 0.00990099009900991
                    elif inventory_entry.sale_currency == "GODS":
                        fee = base_price * 0.01
                    # fee = base_price * 0.01

                combined_price = base_price + fee

                prev_competition_price_dic[token_id] = (base_price, combined_price)
                additional_info_list.append((token_id, combined_price))

        FileIoHelper.write_competition_price_file(file_path, prev_competition_price_dic)

        return prev_competition_price_dic, additional_info_list

    @staticmethod
    def delete_competition_file_after_sale(sold_order):
        """
        Method to delete the competitor's information file associated with a card
        :param sold_order: the filled order of the card sale
        :return: None
        """

        competition_folder = FileHandler.get_base_path("competition_folder")
        currencies = ["GODS", "ETH"]

        for currency in currencies:
            file_name = sold_order.card_name + "_" + sold_order.token_id + "_" + str(currency) + ".json"
            file_path = str(competition_folder) + "\\" + file_name

            os.remove(file_path)

    @staticmethod
    def delete_competition_file_after_multiple_sales(sold_order_list):
        """
        A method to delete competitor files after multiple sales happened
        :param sold_order_list: a list of the filled orders associated with the sales
        :return: None
        """

        competition_folder = FileHandler.get_base_path("competition_folder")
        currencies = ["GODS", "ETH"]

        for sold_order, inventory_entry in sold_order_list:
            for currency in currencies:
                file_name = sold_order.card_name + "_" + sold_order.token_id + "_" + str(currency) + ".json"
                file_path = str(competition_folder) + "\\" + file_name

                os.remove(file_path)
