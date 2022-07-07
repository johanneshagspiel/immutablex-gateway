from src.util.helpers import SafeDatetimeConverter


class OrderGU:
    """
    A class representing one Order
    """

    def __init__(self, order_id, user, token_id, token_address, status, type, card_name, card_quality, quantity,
                 decimals, currency, price_euro_at_updated_timestamp_day, timestamp, updated_timestamp):
        """
        The constructor of the Order class
        :param order_id: the id of the order
        :param user: the user wallet address
        :param token_id: the token_id of the card
        :param token_address: the token_address of the card
        :param status: the status of the Order i.e. active or filled
        :param type: what type of Order it is i.e. Buy or Sell
        :param card_name: the name of the card
        :param card_quality: the quality of the card (specific to Gods Unchained)
        :param quantity: the purchase quantity
        :param decimals: how many decimals the purchase quantity has
        :param currency: the currency in which the card is listed
        :param price_euro_at_updated_timestamp_day: the price of the card in euro at the updated_timestamp
        :param timestamp: the timestamp at which the Order was created
        :param updated_timestamp: the timestamp of the last time the Order was changed i.e. from active to filled
        """
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

    def to_print_dic(self):
        """
        Method to convert one Instance of an Order to a dictionary so that it can be written to file
        :return: the instance of the Order as a dictionary
        """

        print_dic = {"order_id": self.order_id, "user": self.user, "token_id": self.token_id,
                     "token_address": self.token_address, "status": self.status, "type": self.type,
                     "card_name": self.card_name, "card_quality": self.card_quality, "quantity": self.quantity,
                     "decimals": self.decimals, "currency": self.currency,
                     "price_euro_at_updated_timestamp_day": self.price_euro_at_updated_timestamp_day,
                     "timestamp": SafeDatetimeConverter.datetime_to_string(self.timestamp),
                     "updated_timestamp":  SafeDatetimeConverter.datetime_to_string(self.updated_timestamp)}

        return print_dic

    def to_string(self):
        """
        Method to convert one instance of an Order to a string to print to console
        :return: an Order as a string
        """
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
