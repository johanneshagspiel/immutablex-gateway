import json
import time
from datetime import datetime

from objects.inventory.inventory_entry import Inventory_Entry
from objects.inventory.inventory_entry_factory import Inventory_Entry_Factory
from objects.orders.gods_unchained.order_factory_gu import Order_Factory_GU
from objects.sales_history.sales_history_factory import Sales_History_Factory
from operators.helpers.competition_handler import Competition_Handler
from scrappers.coinapi_scrapper import CoinAPI_Scrapper
from scrappers.coinmarketcap_scrapper import CoinMarketCap_Scrapper
from scrappers.gods_unchained_poller import Gods_Unchained_Poller
from util.files.file_handler import File_Handler
from util.files.file_io_helper import File_IO_Helper
from util.helpers import Safe_Datetime_Converter
from util.number_converter import Number_Converter
from util.custom_exceptions import Response_Error, Request_Error, TooManyAPICalls, Internal_Server_Error


class Inventory_Manager():

    pk_info_file_path = File_Handler.get_base_path("pk_info_file")
    with open(pk_info_file_path, 'r', encoding='utf-8') as pk_info_file:
        pk_info_dic = json.load(pk_info_file)
    pk_info_file.close()
    _user_wallet = pk_info_dic["sender"]
    _gp = Gods_Unchained_Poller()


    def __init__(self):
        None

    @staticmethod
    def get_inventory_list():
        inventory_text_list = File_IO_Helper.read_inventory_list()

        inventory_entry_list = []
        for line in inventory_text_list:
            inventory_entry = Inventory_Entry_Factory.create_entry_from_text(line)
            inventory_entry_list.append(inventory_entry)

        return inventory_entry_list

    ### Inventory_Entry creation based on order #########################################################

    @staticmethod
    def create_new_inventory_entry_purchased_now(order_object, currency_to_sell_in):

        currency = order_object.currency
        current_currency_dic = CoinMarketCap_Scrapper.get_now_currency_price()
        current_price_currency = current_currency_dic[currency]

        purchase_price_float = Number_Converter.get_float_from_quantity_decimal(order_object.quantity, order_object.decimals)
        purchase_price_euro = current_price_currency * purchase_price_float

        purchase_timestamp = datetime.utcnow()

        new_inventory_entry = Inventory_Manager._create_new_inventory_entry(order_object, purchase_timestamp, purchase_price_euro, currency_to_sell_in)
        return new_inventory_entry

    @staticmethod
    def create_new_inventory_entry_purchased_from_filled_order(filled_order_object, currency_to_sell_in):

        currency_rate_day_purchase = CoinAPI_Scrapper.get_price_at_point_in_past(timestamp_str=Safe_Datetime_Converter.datetime_to_string(filled_order_object.updated_timestamp), currency=filled_order_object.currency)
        price_currency_float = Number_Converter.get_float_from_quantity_decimal(filled_order_object.quantity, filled_order_object.decimals)

        purchase_price_euro = price_currency_float * currency_rate_day_purchase

        new_inventory_entry = Inventory_Manager._create_new_inventory_entry(filled_order_object, filled_order_object.updated_timestamp, purchase_price_euro, currency_to_sell_in)
        return new_inventory_entry


    @staticmethod
    def _create_new_inventory_entry(order_object, purchase_timestamp, purchase_price_euro, currency_to_sell_in):

        card_name = order_object.card_name
        token_id = order_object.token_id
        order_id = order_object.order_id

        purchase_price_currency = Number_Converter.get_float_str_from_quantity_decimal(order_object.quantity, order_object.decimals)
        purchase_currency = order_object.currency
        purchase_price_euro = purchase_price_euro
        purchase_timestamp = purchase_timestamp

        sale_currency = currency_to_sell_in
        sale_price_currency = ""

        card_quality = order_object.card_quality

        new_inventory_entry = Inventory_Entry(card_name, token_id, order_id, purchase_price_currency, purchase_currency,
                                              purchase_price_euro, purchase_timestamp, sale_currency, sale_price_currency,
                                              card_quality)

        return new_inventory_entry


    @staticmethod
    def add_new_inventory_entry_to_file(new_inventory_entry):
        existing_inventory_list = Inventory_Manager.get_inventory_list()
        existing_inventory_list.append(new_inventory_entry)
        File_IO_Helper.write_inventory_list(existing_inventory_list)

    ### Inventory Entry Check ###################################################################################

    @staticmethod
    def update_inventory_list_based_on_sold_order(sold_order, current_inventory_entry, current_inventory_entry_list):

        new_sales_history_list = []

        new_sales_history_entry = Sales_History_Factory.convert_inventory_entry_and_order_to_sales_history(inventory_entry=current_inventory_entry, sale_order=sold_order)
        new_sales_history_list.append(new_sales_history_entry)

        new_inventory_entry_list = []
        for inventory_entry in current_inventory_entry_list:
            if inventory_entry.token_id != current_inventory_entry.token_id:
                new_inventory_entry_list.append(inventory_entry)

        File_IO_Helper.write_new_sales_history_list_to_file(new_sales_history_list)
        Competition_Handler.delete_competition_file_after_sale(sold_order)

        File_IO_Helper.write_inventory_list(new_inventory_entry_list)

        return new_inventory_entry_list


    @staticmethod
    def update_inventory_list_based_on_sold_orders(sold_order_list, current_inventory_entry_list):

        new_sales_history_list = []
        sold_token_id_dic = {}
        for sold_order, inventory_entry in sold_order_list:
            new_sales_history_entry = Sales_History_Factory.convert_inventory_entry_and_order_to_sales_history(inventory_entry=inventory_entry, sale_order=sold_order)
            new_sales_history_list.append(new_sales_history_entry)
            sold_token_id_dic[inventory_entry.token_id] = True

        new_inventory_entry_list = []
        for inventory_entry in current_inventory_entry_list:
            if inventory_entry.token_id not in sold_token_id_dic:
                new_inventory_entry_list.append(inventory_entry)

        if len(new_sales_history_list) > 0:
            File_IO_Helper.write_new_sales_history_list_to_file(new_sales_history_list)
            Competition_Handler.delete_competition_file_after_multiple_sales(sold_order_list)

        File_IO_Helper.write_inventory_list(new_inventory_entry_list)

        return new_inventory_entry_list


    @classmethod
    def check_inventory_list(cls, inventory_list):

        print(f"Checking Inventory List")

        new_inventory_list = []
        sold_order_list = []

        new_sales_history_list = []

        historical_price_dic = CoinAPI_Scrapper.get_historical_prices()

        for inventory_entry in inventory_list:

            try:
                inventory_entry_is_sold, potential_latest_filled_order = Inventory_Manager.check_if_inventory_entry_is_sold(inventory_entry, historical_price_dic)

                if inventory_entry_is_sold:
                    new_sales_history_entry = Sales_History_Factory.convert_inventory_entry_and_order_to_sales_history( inventory_entry=inventory_entry, sale_order=potential_latest_filled_order)
                    new_sales_history_list.append(new_sales_history_entry)
                    sold_order_list.append((potential_latest_filled_order, inventory_entry_is_sold))

                    currency_price_euro_at_sale = potential_latest_filled_order.price_euro_at_updated_timestamp_day
                    currency_sale_price = Number_Converter.get_float_from_quantity_decimal(potential_latest_filled_order.quantity, potential_latest_filled_order.decimals)
                    print(f"\"{potential_latest_filled_order.card_name}\" was sold for {currency_sale_price} {potential_latest_filled_order.currency} or {currency_price_euro_at_sale:.3f} EUR")


                else:
                    new_inventory_list.append(inventory_entry)

            except (Response_Error, Request_Error, TooManyAPICalls, Internal_Server_Error) as custom_errors:
                time.sleep(10)
                return Inventory_Manager.check_inventory_list(inventory_list)

        if len(new_sales_history_list) > 0:
            File_IO_Helper.write_new_sales_history_list_to_file(new_sales_history_list)
            File_IO_Helper.write_inventory_list(new_inventory_list)
            Competition_Handler.delete_competition_file_after_multiple_sales(sold_order_list)

        return new_inventory_list


    @classmethod
    def check_if_inventory_entry_is_sold(cls, inventory_entry, historical_price_dic):

        try:

            filled_jsons = Inventory_Manager._gp.get_jsons_by_user_status_sell_token_id(user_str=cls._user_wallet, status_str="filled", sell_token_id_str=inventory_entry.token_id)

            if len(filled_jsons) > 0:

                if len(filled_jsons) > 1:
                    raise Exception(f"Did I sell the token with this id {inventory_entry.token_id} twice?")

                filled_json = filled_jsons[0]
                latest_filled_order = Order_Factory_GU.order_json_to_object(filled_json, historical_prices_dic=historical_price_dic)
                return True, latest_filled_order

            else:
                return False, None

        except (Response_Error, Request_Error, TooManyAPICalls, Internal_Server_Error) as custom_errors:
            time.sleep(2)
            return Inventory_Manager.check_if_inventory_entry_is_sold(inventory_entry, historical_price_dic)
