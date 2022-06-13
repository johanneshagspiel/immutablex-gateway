from util.helpers import Safe_Datetime_Converter


class Inventory_Entry():

    def __init__(self, card_name, token_id, order_id, purchase_price_currency, purchase_currency, purchase_price_euro, purchase_timestamp, sale_currency, sale_price_currency, card_quality):

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

    ### To Write ################################################################################################

    def to_print_dic(self):

        print_dic = {}
        print_dic["card_name"] = self.card_name
        print_dic["token_id"] = self.token_id
        print_dic["order_id"] = self.order_id

        print_dic["purchase_price_currency"] = self.purchase_price_currency
        print_dic["purchase_currency"] = self.purchase_currency
        print_dic["purchase_price_euro"] = self.purchase_price_euro
        print_dic["purchase_timestamp"] = Safe_Datetime_Converter.datetime_to_string(self.purchase_timestamp)

        print_dic["sale_currency"] = self.sale_currency
        print_dic["sale_price_currency"] = self.sale_price_currency

        print_dic["card_quality"] = self.card_quality

        return print_dic
