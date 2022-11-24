from src.util.helpers import SafeDatetimeConverter


class CancelledOrderGU:
    """
    A space optimized class representing a cancelled order. It is separate from the other statuses because cancelled
     orders are very common.
    """

    def __init__(self, order_id, user, token_id, status, type, timestamp, updated_timestamp):
        """
        The constructor of the CancelledOrderGUs class
        :param order_id: the id of the cancelled order
        :param user: the wallet address of the order
        :param token_id: the id of the card
        :param status: the status of the order
        :param type: the type of the order i.e. buy
        :param timestamp: the timestamp when the order was created
        :param updated_timestamp: the last time the order was changed
        """
        self.order_id = order_id
        self.user = user
        self.token_id = token_id

        self.status = status
        self.type = type

        self.timestamp = timestamp
        self.updated_timestamp = updated_timestamp


    def to_tuple(self):
        """
        Method to convert on instance of a cancelled Order to a tuple so that it can be inserted into an MYSQL database
        :return: the instance of the Order as a tuple
        """

        return (self.order_id, self.user, self.token_id, None, self.status, self.type, None, None, None, None, None,
                 None, SafeDatetimeConverter.datetime_to_string(self.timestamp),
                 SafeDatetimeConverter.datetime_to_string(self.updated_timestamp))


    def to_print_dic(self):
        """
        A method to convert a cancelled order into a string to be printed
        :return: a string
        """

        print_dic = {}
        print_dic["order_id"] = self.order_id
        print_dic["user"] = self.user
        print_dic["token_id"] = self.token_id

        print_dic["status"] = self.status
        print_dic["type"] = self.type

        print_dic["timestamp"] = SafeDatetimeConverter.datetime_to_string(self.timestamp)
        print_dic["updated_timestamp"] = SafeDatetimeConverter.datetime_to_string(self.updated_timestamp)

        return print_dic
