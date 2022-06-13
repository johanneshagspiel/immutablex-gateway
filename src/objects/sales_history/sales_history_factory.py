from objects.sales_history.sales_history_entry import Sales_History_Entry
from scrappers.coinapi_scrapper import CoinAPI_Scrapper
from util.helpers import Safe_Datetime_Converter
from util.number_converter import Number_Converter


class Sales_History_Factory():

    def __init__(self):
        None

    @staticmethod
    def convert_inventory_entry_and_order_to_sales_history(inventory_entry, sale_order):

        currency_sale_price = Number_Converter.get_float_from_quantity_decimal(sale_order.quantity, sale_order.decimals)
        price_at_sale_moment = CoinAPI_Scrapper.get_price_at_point_in_past(Safe_Datetime_Converter.datetime_to_string(sale_order.updated_timestamp), inventory_entry.sale_currency)
        currency_price_euro_at_sale = price_at_sale_moment * currency_sale_price

        card_name = inventory_entry.card_name
        token_id = inventory_entry.token_id
        card_quality = inventory_entry.card_quality

        purchase_order_id = inventory_entry.order_id
        currency_purchase_price = inventory_entry.purchase_price_currency
        purchase_currency = inventory_entry.purchase_currency
        purchase_price_euro = inventory_entry.purchase_price_euro
        purchase_timestamp = Safe_Datetime_Converter.datetime_to_string(inventory_entry.purchase_timestamp)

        sale_order_id = sale_order.order_id
        currency_sale_price = currency_sale_price
        sale_currency = inventory_entry.sale_currency
        currency_price_euro_at_sale = currency_price_euro_at_sale
        sale_timestamp = Safe_Datetime_Converter.datetime_to_string(sale_order.updated_timestamp)

        minutes_needed_to_sell = int((Safe_Datetime_Converter.string_to_datetime(sale_timestamp) - Safe_Datetime_Converter.string_to_datetime(purchase_timestamp)).total_seconds() / 60)
        profit = float(currency_price_euro_at_sale) - float(purchase_price_euro)
        roi = profit / float(purchase_price_euro)

        new_sales_history_entry = Sales_History_Entry(card_name, token_id, card_quality,
                 purchase_order_id, currency_purchase_price, purchase_currency, purchase_price_euro, purchase_timestamp,
                 sale_order_id, currency_sale_price, sale_currency, currency_price_euro_at_sale, sale_timestamp,
                 minutes_needed_to_sell, profit, roi)

        return new_sales_history_entry


    @staticmethod
    def convert_purchase_and_sale_order_to_sales_history(purchase_order, sale_order):


        card_name = sale_order.card_name
        token_id = sale_order.token_id
        card_quality = sale_order.card_quality


        purchase_price_cur = Number_Converter.get_float_from_quantity_decimal(purchase_order.quantity, purchase_order.decimals)
        price_at_purchase_moment = CoinAPI_Scrapper.get_price_at_point_in_past(Safe_Datetime_Converter.datetime_to_string(purchase_order.updated_timestamp), purchase_order.currency)
        purchase_price_euro = price_at_purchase_moment * purchase_price_cur

        purchase_order_id = purchase_order.order_id
        purchase_price_cur = purchase_price_cur
        purchase_currency = purchase_order.currency
        purchase_price_euro = purchase_price_euro
        purchase_timestamp = Safe_Datetime_Converter.datetime_to_string(purchase_order.updated_timestamp)


        sale_price_cur = Number_Converter.get_float_from_quantity_decimal(sale_order.quantity, sale_order.decimals)
        price_at_sale_moment = CoinAPI_Scrapper.get_price_at_point_in_past(Safe_Datetime_Converter.datetime_to_string(sale_order.updated_timestamp), sale_order.currency)
        sale_price_euro = price_at_sale_moment * sale_price_cur

        sale_order_id = sale_order.order_id
        sale_price_cur = sale_price_cur
        sale_currency = sale_order.currency
        sale_price_euro = sale_price_euro
        sale_timestamp = Safe_Datetime_Converter.datetime_to_string(sale_order.updated_timestamp)


        minutes_needed_to_sell = int((Safe_Datetime_Converter.string_to_datetime(sale_timestamp) - Safe_Datetime_Converter.string_to_datetime(purchase_timestamp)).total_seconds() / 60)
        profit = float(sale_price_euro) - float(purchase_price_euro)
        roi = profit / float(purchase_price_euro)

        new_sales_history_entry = Sales_History_Entry(card_name, token_id, card_quality,
                 purchase_order_id, purchase_price_cur, purchase_currency, purchase_price_euro, purchase_timestamp,
                 sale_order_id, sale_price_cur, sale_currency, sale_price_euro, sale_timestamp,
                 minutes_needed_to_sell, profit, roi)

        return new_sales_history_entry
