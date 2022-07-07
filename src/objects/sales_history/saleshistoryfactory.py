from src.objects.sales_history.saleshistoryentry import SalesHistoryEntry
from src.scrappers.coinapiscrapper import CoinAPIScrapper
from src.util.helpers import SafeDatetimeConverter
from src.util.numberconverter import NumberConverter


class SalesHistoryFactory:
    """
    A Factory class to create a SalesHistoryEntry
    """

    def __init__(self):
        """
        The constructor for the SalesHistoryFactory
        """
        pass

    @staticmethod
    def convert_inventory_entry_and_order_to_sales_history(inventory_entry, sale_order):
        """
        A method to create a SaleHistoryEntry based on an InventoryEntry and the filled Order
        :param inventory_entry: the InventoryEntry of the sold card
        :param sale_order: the filled Order associated with the sale
        :return: a SaleHistoryEntry
        """

        currency_sale_price = NumberConverter.get_float_from_quantity_decimal(sale_order.quantity, sale_order.decimals)
        price_at_sale_moment = CoinAPIScrapper.get_price_at_point_in_past(SafeDatetimeConverter.datetime_to_string(
            sale_order.updated_timestamp), inventory_entry.sale_currency)
        currency_price_euro_at_sale = price_at_sale_moment * currency_sale_price

        card_name = inventory_entry.card_name
        token_id = inventory_entry.token_id
        card_quality = inventory_entry.card_quality

        purchase_order_id = inventory_entry.order_id
        currency_purchase_price = inventory_entry.purchase_price_currency
        purchase_currency = inventory_entry.purchase_currency
        purchase_price_euro = inventory_entry.purchase_price_euro
        purchase_timestamp = SafeDatetimeConverter.datetime_to_string(inventory_entry.purchase_timestamp)

        sale_order_id = sale_order.order_id
        currency_sale_price = currency_sale_price
        sale_currency = inventory_entry.sale_currency
        currency_price_euro_at_sale = currency_price_euro_at_sale
        sale_timestamp = SafeDatetimeConverter.datetime_to_string(sale_order.updated_timestamp)

        minutes_needed_to_sell = int((SafeDatetimeConverter.string_to_datetime(sale_timestamp) -
                                      SafeDatetimeConverter.string_to_datetime(purchase_timestamp)).total_seconds() / 60)
        profit = float(currency_price_euro_at_sale) - float(purchase_price_euro)
        roi = profit / float(purchase_price_euro)

        new_sales_history_entry = SalesHistoryEntry(card_name, token_id, card_quality,
                 purchase_order_id, currency_purchase_price, purchase_currency, purchase_price_euro, purchase_timestamp,
                 sale_order_id, currency_sale_price, sale_currency, currency_price_euro_at_sale, sale_timestamp,
                 minutes_needed_to_sell, profit, roi)

        return new_sales_history_entry

    @staticmethod
    def convert_purchase_and_sale_order_to_sales_history(purchase_order, sale_order):
        """
        A method to convert both a purchase and a sale order into a SaleHistoryEntry
        :param purchase_order: the purchase order
        :param sale_order: the sale order
        :return: the associated SaleHistoryEntry
        """

        card_name = sale_order.card_name
        token_id = sale_order.token_id
        card_quality = sale_order.card_quality

        purchase_price_cur = NumberConverter.get_float_from_quantity_decimal(purchase_order.quantity,
                                                                             purchase_order.decimals)
        price_at_purchase_moment = CoinAPIScrapper.get_price_at_point_in_past(
            SafeDatetimeConverter.datetime_to_string(purchase_order.updated_timestamp), purchase_order.currency)
        purchase_price_euro = price_at_purchase_moment * purchase_price_cur

        purchase_order_id = purchase_order.order_id
        purchase_price_cur = purchase_price_cur
        purchase_currency = purchase_order.currency
        purchase_price_euro = purchase_price_euro
        purchase_timestamp = SafeDatetimeConverter.datetime_to_string(purchase_order.updated_timestamp)

        sale_price_cur = NumberConverter.get_float_from_quantity_decimal(sale_order.quantity, sale_order.decimals)
        price_at_sale_moment = CoinAPIScrapper.get_price_at_point_in_past(SafeDatetimeConverter.datetime_to_string(
            sale_order.updated_timestamp), sale_order.currency)
        sale_price_euro = price_at_sale_moment * sale_price_cur

        sale_order_id = sale_order.order_id
        sale_price_cur = sale_price_cur
        sale_currency = sale_order.currency
        sale_price_euro = sale_price_euro
        sale_timestamp = SafeDatetimeConverter.datetime_to_string(sale_order.updated_timestamp)

        minutes_needed_to_sell = int((SafeDatetimeConverter.string_to_datetime(sale_timestamp) -
                                      SafeDatetimeConverter.string_to_datetime(purchase_timestamp)).total_seconds() / 60)
        profit = float(sale_price_euro) - float(purchase_price_euro)
        roi = profit / float(purchase_price_euro)

        new_sales_history_entry = SalesHistoryEntry(card_name, token_id, card_quality,
                 purchase_order_id, purchase_price_cur, purchase_currency, purchase_price_euro, purchase_timestamp,
                 sale_order_id, sale_price_cur, sale_currency, sale_price_euro, sale_timestamp,
                 minutes_needed_to_sell, profit, roi)

        return new_sales_history_entry
