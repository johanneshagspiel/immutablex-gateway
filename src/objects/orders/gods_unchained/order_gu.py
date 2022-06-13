from util.helpers import Safe_Datetime_Converter


class Order_GU():

    def __init__(self, order_id, user, token_id, token_address, status, type, card_name, card_quality, quantity, decimals, currency, price_euro_at_updated_timestamp_day, timestamp, updated_timestamp):
        self.order_id = order_id
        self.user = user
        self.token_id = token_id
        self.token_address = token_address

        self.status = status
        self.type = type

        self.card_name = card_name
        self.card_quality = card_quality

        self.quantity = quantity
        self.decimals = decimals
        self.currency = currency
        self.price_euro_at_updated_timestamp_day = price_euro_at_updated_timestamp_day

        self.timestamp = timestamp
        self.updated_timestamp = updated_timestamp

    ### To Write ################################################################################################

    def to_print_dic(self):

        print_dic = {}
        print_dic["order_id"] = self.order_id
        print_dic["user"] = self.user
        print_dic["token_id"] = self.token_id
        print_dic["token_address"] = self.token_address

        print_dic["status"] = self.status
        print_dic["type"] = self.type

        print_dic["card_name"] = self.card_name
        print_dic["card_quality"] = self.card_quality

        print_dic["quantity"] = self.quantity
        print_dic["decimals"] = self.decimals
        print_dic["currency"] = self.currency
        print_dic["price_euro_at_updated_timestamp_day"] = self.price_euro_at_updated_timestamp_day

        print_dic["timestamp"] = Safe_Datetime_Converter.datetime_to_string(self.timestamp)
        print_dic["updated_timestamp"] = Safe_Datetime_Converter.datetime_to_string(self.updated_timestamp)

        return print_dic


    def to_string(self):
        return '{' + f"""
        "order_id": {self.order_id}
        "user": {self.user}
        "token_id": {self.token_id} 
        "token_address": {self.token_address}
        
        "status": {self.status}
        "type": {self.type}
        
        "card_name": {self.card_name}
        "card_quality": {self.card_quality}
        
        "quantity": {self.quantity}
        "decimals": {self.decimals}
        "currency": {self.currency}
        "price_euro_at_updated_timestamp_day": {self.price_euro_at_updated_timestamp_day}
        
        "timestamp": {self.timestamp}
        "updated_timestamp": {self.updated_timestamp}
        """ + '}'
