from util.helpers import Safe_Datetime_Converter


class Cancelled_Order_GU():

    def __init__(self, order_id, user, token_id, status, type, timestamp, updated_timestamp):
        self.order_id = order_id
        self.user = user
        self.token_id = token_id

        self.status = status
        self.type = type

        self.timestamp = timestamp
        self.updated_timestamp = updated_timestamp

    ### To Write ################################################################################################

    def to_print_dic(self):

        print_dic = {}
        print_dic["order_id"] = self.order_id
        print_dic["user"] = self.user
        print_dic["token_id"] = self.token_id

        print_dic["status"] = self.status
        print_dic["type"] = self.type

        print_dic["timestamp"] = Safe_Datetime_Converter.datetime_to_string(self.timestamp)
        print_dic["updated_timestamp"] = Safe_Datetime_Converter.datetime_to_string(self.updated_timestamp)

        return print_dic