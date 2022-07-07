
class SalesHistoryEntry:
    """
    A class representing one sale that occurred
    """

    def __init__(self, card_name, token_id, card_quality,
                 purchase_order_id, currency_purchase_price, purchase_currency, purchase_price_euro, purchase_timestamp,
                 sale_order_id, currency_sale_price, sale_currency, currency_price_euro_at_sale, sale_timestamp,
                 minutes_needed_to_sell, profit, roi):
        """
        The constructor of the SalesHistoryEntry class
        :param card_name: the name of the sold card
        :param token_id: the id of the sold card
        :param card_quality: the quality of the sold card
        :param purchase_order_id: the id of the order where the card has been purchased
        :param currency_purchase_price: the purchase price of the card in the cryptocurrency used
        :param purchase_currency: the cryptocurrency used to purchase a card
        :param purchase_price_euro: the purchase price of the card in euro
        :param purchase_timestamp: the timestamp when the card was purchased
        :param sale_order_id: the id of the sales order
        :param currency_sale_price: the sale price of the card in the cryptocurrency used
        :param sale_currency: the cryptocurrency used in the sale of the card
        :param currency_price_euro_at_sale: the sale price of the card in euro
        :param sale_timestamp: the timestamp of the sale
        :param minutes_needed_to_sell: minutes between the purchase and the sale of the card
        :param profit: profit in euro made
        :param roi: return on investment
        """

        self.card_name = card_name
        self.token_id = token_id
        self.card_quality = card_quality

        self.pur_order_id = purchase_order_id
        self.pur_currency = purchase_currency
        self.pur_price_cur = currency_purchase_price
        self.pur_price_euro = purchase_price_euro
        self.pur_timestamp = purchase_timestamp

        self.sale_order_id = sale_order_id
        self.sale_currency = sale_currency
        self.sale_price_cur = currency_sale_price
        self.sale_price_euro = currency_price_euro_at_sale
        self.sale_timestamp = sale_timestamp

        self.minutes_to_sale = minutes_needed_to_sell
        self.profit = profit
        self.roi = roi
