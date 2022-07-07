import json
import time
from datetime import datetime

from src.objects.inventory.inventory_entry import InventoryEntry
from src.objects.inventory.inventory_entry_factory import InventoryEntryFactory
from src.objects.orders.gods_unchained.orderfactorygu import OrderFactoryGU
from src.objects.sales_history.saleshistoryfactory import SalesHistoryFactory
from src.operators.helpers.competitionhandler import CompetitionHandler
from src.scrappers.coinapiscrapper import CoinAPIScrapper
from src.scrappers.coinmarketcapscrapper import CoinMarketCapScrapper
from src.scrappers.godsunchainedpoller import GodsUnchainedPoller
from src.util.files.filehandler import FileHandler
from src.util.files.fileiohelper import FileIoHelper
from src.util.helpers import SafeDatetimeConverter
from src.util.numberconverter import NumberConverter
from src.util.custom_exceptions import ResponseError, RequestError, TooManyAPICalls, InternalServerError


class InventoryManager:
    """
    The class that manages the inventory of a User.
    """

    pk_info_file_path = FileHandler.get_base_path("pk_info_file")
    with open(pk_info_file_path, 'r', encoding='utf-8') as pk_info_file:
        pk_info_dic = json.load(pk_info_file)
    pk_info_file.close()
    _user_wallet = pk_info_dic["sender"]
    _gp = GodsUnchainedPoller()

    def __init__(self):
        """
        The constructor of the InventoryManager class.
        """
        pass

    @staticmethod
    def get_inventory_list():
        """
        A method to get a list of the inventory.
        :return: a list of InventoryEntries
        """
        inventory_text_list = FileIoHelper.read_inventory_list()

        inventory_entry_list = []
        for line in inventory_text_list:
            inventory_entry = InventoryEntryFactory.create_entry_from_text(line)
            inventory_entry_list.append(inventory_entry)

        return inventory_entry_list

    @staticmethod
    def create_new_inventory_entry_purchased_now(order_object, currency_to_sell_in):
        """
        A method to create a new InventoryEntry based on a purchase that happened at this moment
        :param order_object: the Order object representing the purchase
        :param currency_to_sell_in: the Currency to sell the card in
        :return: the new InventoryEntry
        """

        currency = order_object.currency
        current_currency_dic = CoinMarketCapScrapper.get_now_currency_price()
        current_price_currency = current_currency_dic[currency]

        purchase_price_float = NumberConverter.get_float_from_quantity_decimal(order_object.quantity,
                                                                               order_object.decimals)
        purchase_price_euro = current_price_currency * purchase_price_float

        purchase_timestamp = datetime.utcnow()

        new_inventory_entry = InventoryManager._create_new_inventory_entry(order_object, purchase_timestamp,
                                                                           purchase_price_euro, currency_to_sell_in)
        return new_inventory_entry

    @staticmethod
    def create_new_inventory_entry_purchased_from_filled_order(filled_order_object, currency_to_sell_in):
        """
        A method to create an InventoryEntry based on a purchase that happened in the past
        :param filled_order_object: the Order instance of the purchase that has happened in the past
        :param currency_to_sell_in: the Currency to sell the card in
        :return: the new InventoryEntry
        """

        currency_rate_day_purchase = CoinAPIScrapper.get_price_at_point_in_past(
            timestamp_str=SafeDatetimeConverter.datetime_to_string(filled_order_object.updated_timestamp),
            currency=filled_order_object.currency)
        price_currency_float = NumberConverter.get_float_from_quantity_decimal(filled_order_object.quantity,
                                                                               filled_order_object.decimals)

        purchase_price_euro = price_currency_float * currency_rate_day_purchase

        new_inventory_entry = InventoryManager._create_new_inventory_entry(filled_order_object,
                                                                           filled_order_object.updated_timestamp,
                                                                           purchase_price_euro, currency_to_sell_in)
        return new_inventory_entry

    @staticmethod
    def _create_new_inventory_entry(order_object, purchase_timestamp, purchase_price_euro, currency_to_sell_in):
        """
        A method to create a new InventoryEntry based on a purchase timestamp and purchase price
        :param order_object: the Order of the purchase
        :param purchase_timestamp: the purchase moment
        :param purchase_price_euro: the purchase price in Euro
        :param currency_to_sell_in: the currency to sell the card in
        :return: the new InventoryEntry
        """

        card_name = order_object.card_name
        token_id = order_object.token_id
        order_id = order_object.order_id

        purchase_price_currency = NumberConverter.get_float_str_from_quantity_decimal(order_object.quantity,
                                                                                      order_object.decimals)
        purchase_currency = order_object.currency
        purchase_price_euro = purchase_price_euro
        purchase_timestamp = purchase_timestamp

        sale_currency = currency_to_sell_in
        sale_price_currency = ""

        card_quality = order_object.card_quality

        new_inventory_entry = InventoryEntry(card_name, token_id, order_id, purchase_price_currency, purchase_currency,
                                             purchase_price_euro, purchase_timestamp, sale_currency,
                                             sale_price_currency, card_quality)

        return new_inventory_entry

    @staticmethod
    def add_new_inventory_entry_to_file(new_inventory_entry):
        """
        Method to write a new InventoryEntry to file
        :param new_inventory_entry: the InventoryEntry to write to file
        :return: None
        """
        existing_inventory_list = InventoryManager.get_inventory_list()
        existing_inventory_list.append(new_inventory_entry)
        FileIoHelper.write_inventory_list(existing_inventory_list)

    @staticmethod
    def update_inventory_list_based_on_sold_order(sold_order, current_inventory_entry, current_inventory_entry_list):
        """
        A method to update the inventory list based on a sold order
        :param sold_order: the Order representing the sale of a card
        :param current_inventory_entry: the InventoryEntry of the card that has been sold
        :param current_inventory_entry_list: the list of all the InventoryEntries of a user
        :return: the inventory list without the sold order
        """

        new_sales_history_list = []

        new_sales_history_entry = SalesHistoryFactory.convert_inventory_entry_and_order_to_sales_history(
            inventory_entry=current_inventory_entry, sale_order=sold_order)
        new_sales_history_list.append(new_sales_history_entry)

        new_inventory_entry_list = []
        for inventory_entry in current_inventory_entry_list:
            if inventory_entry.token_id != current_inventory_entry.token_id:
                new_inventory_entry_list.append(inventory_entry)

        FileIoHelper.write_new_sales_history_list_to_file(new_sales_history_list)
        CompetitionHandler.delete_competition_file_after_sale(sold_order)

        FileIoHelper.write_inventory_list(new_inventory_entry_list)

        return new_inventory_entry_list

    @staticmethod
    def update_inventory_list_based_on_sold_orders(sold_order_list, current_inventory_entry_list):
        """
        A method to update a list of InventoryEntries based on a list of sold Orders
        :param sold_order_list: a list of the Orders of all the cards that has been sold
        :param current_inventory_entry_list: the current InventoryEntry list
        :return: the inventory list without all the sold cards
        """

        new_sales_history_list = []
        sold_token_id_dic = {}
        for sold_order, inventory_entry in sold_order_list:
            new_sales_history_entry = SalesHistoryFactory.convert_inventory_entry_and_order_to_sales_history(
                inventory_entry=inventory_entry, sale_order=sold_order)
            new_sales_history_list.append(new_sales_history_entry)
            sold_token_id_dic[inventory_entry.token_id] = True

        new_inventory_entry_list = []
        for inventory_entry in current_inventory_entry_list:
            if inventory_entry.token_id not in sold_token_id_dic:
                new_inventory_entry_list.append(inventory_entry)

        if len(new_sales_history_list) > 0:
            FileIoHelper.write_new_sales_history_list_to_file(new_sales_history_list)
            CompetitionHandler.delete_competition_file_after_multiple_sales(sold_order_list)

        FileIoHelper.write_inventory_list(new_inventory_entry_list)

        return new_inventory_entry_list

    @classmethod
    def check_inventory_list(cls, inventory_list):
        """
        A method to check whether a card in the inventory list has been sold in the meantime
        :param inventory_list: the current inventory list
        :return: the new inventory list without all the cards that has been sold
        """

        print(f"Checking Inventory List")

        new_inventory_list = []
        sold_order_list = []

        new_sales_history_list = []

        historical_price_dic = CoinAPIScrapper.get_historical_prices()

        for inventory_entry in inventory_list:

            try:
                inventory_entry_is_sold, potential_latest_filled_order = \
                    InventoryManager.check_if_inventory_entry_is_sold(inventory_entry, historical_price_dic)

                if inventory_entry_is_sold:
                    new_sales_history_entry = SalesHistoryFactory.convert_inventory_entry_and_order_to_sales_history(
                        inventory_entry=inventory_entry, sale_order=potential_latest_filled_order)
                    new_sales_history_list.append(new_sales_history_entry)
                    sold_order_list.append((potential_latest_filled_order, inventory_entry_is_sold))

                    currency_price_euro_at_sale = potential_latest_filled_order.price_euro_at_updated_timestamp_day
                    currency_sale_price = NumberConverter.get_float_from_quantity_decimal(
                        potential_latest_filled_order.quantity, potential_latest_filled_order.decimals)
                    print(f"\"{potential_latest_filled_order.card_name}\" was sold for {currency_sale_price} "
                          f"{potential_latest_filled_order.currency} or {currency_price_euro_at_sale:.3f} EUR")

                else:
                    new_inventory_list.append(inventory_entry)

            except (ResponseError, RequestError, TooManyAPICalls, InternalServerError):
                time.sleep(10)
                return InventoryManager.check_inventory_list(inventory_list)

        if len(new_sales_history_list) > 0:
            FileIoHelper.write_new_sales_history_list_to_file(new_sales_history_list)
            FileIoHelper.write_inventory_list(new_inventory_list)
            CompetitionHandler.delete_competition_file_after_multiple_sales(sold_order_list)

        return new_inventory_list

    @classmethod
    def check_if_inventory_entry_is_sold(cls, inventory_entry, historical_price_dic):
        """
        A method to check whether a card in the inventory has been sold
        :param inventory_entry: the inventory entry of the card to be checked
        :param historical_price_dic: the price overview
        :return: True, Filled_Order if the card has been sold otherwise False, None
        """

        try:

            filled_jsons = InventoryManager.\
                _gp.get_jsons_by_user_status_sell_token_id(user_str=cls._user_wallet, status_str="filled",
                                                           sell_token_id_str=inventory_entry.token_id)

            if len(filled_jsons) > 0:

                if len(filled_jsons) > 1:
                    raise Exception(f"Did I sell the token with this id {inventory_entry.token_id} twice?")

                filled_json = filled_jsons[0]
                latest_filled_order = OrderFactoryGU.order_json_to_object(order_json=filled_json,
                                                                          historical_prices_dic=historical_price_dic)
                return True, latest_filled_order

            else:
                return False, None

        except (ResponseError, RequestError, TooManyAPICalls, InternalServerError):
            time.sleep(2)
            return InventoryManager.check_if_inventory_entry_is_sold(inventory_entry, historical_price_dic)
