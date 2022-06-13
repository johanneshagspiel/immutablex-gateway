
class Sales_History_Entry():

    def __init__(self, card_name, token_id, card_quality,
                 purchase_order_id, currency_purchase_price, purchase_currency, purchase_price_euro, purchase_timestamp,
                 sale_order_id, currency_sale_price, sale_currency, currency_price_euro_at_sale, sale_timestamp,
                 minutes_needed_to_sell, profit, roi):

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
