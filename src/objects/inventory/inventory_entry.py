from src.util.helpers import SafeDatetimeConverter


class InventoryEntry:
    """
    This class represents one card in the inventory of a user.
    """

    def __init__(self, card_name, token_id, order_id, purchase_price_currency, purchase_currency, purchase_price_euro,
                 purchase_timestamp, sale_currency, sale_price_currency, card_quality):
        """
        The constructor for the InventoryEntry class
        :param card_name: the name of the card
        :param token_id: the id of the token of the card
        :param order_id: the order_id of the purchase order
        :param purchase_price_currency: the price of the card in the currency used to buy the card
        :param purchase_currency: the currency used to purchase the card
        :param purchase_price_euro: the purchase price in euro
        :param purchase_timestamp: the timestamp of the purchase
        :param sale_currency: the currency in which the card should be sold
        :param sale_price_currency: the price at which the card should be sold
        :param card_quality: the quality of the card (particular to Gods Unchained Cards)
        """

        self.card_name = card_name
        self.token_id = token_id
        self.order_id = order_id

        self.purchase_price_currency = purchase_price_currency
        self.purchase_currency = purchase_currency
        self.purchase_price_euro = purchase_price_euro
        self.purchase_timestamp = purchase_timestamp

        self.sale_currency = sale_currency
        self.sale_price_currency = sale_price_currency

        self.card_quality = card_quality

    def to_print_dic(self):
        """
        Method to turn one InventoryEntry instance into a dictionary that can be written to file.
        :return: the InventoryEntry instance as a dictionary
        """

        print_dic = {"card_name": self.card_name, "token_id": self.token_id, "order_id": self.order_id,
                     "purchase_price_currency": self.purchase_price_currency,
                     "purchase_currency": self.purchase_currency, "purchase_price_euro": self.purchase_price_euro,
                     "purchase_timestamp": SafeDatetimeConverter.datetime_to_string(self.purchase_timestamp),
                     "sale_currency":  self.sale_currency, "sale_price_currency": self.sale_price_currency,
                     "card_quality": self.card_quality}

        return print_dic
