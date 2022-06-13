import json

from objects.orders.gods_unchained.cancelled_order_gu import Cancelled_Order_GU
from objects.orders.gods_unchained.order_gu import Order_GU
from util.custom_exceptions import Start_New_Day_Error
from util.helpers import Safe_Datetime_Converter
from util.number_converter import Number_Converter


class Order_Factory_GU():


    def __init__(self):
        None

    @staticmethod
    def order_json_to_object(order_json, historical_prices_dic):

        mythic_card_number_list = [100000, 100002, 65000, 65001, 65002, 65003, 65004]

        order_id = order_json["order_id"]
        user = order_json["user"]

        status = order_json["status"]

        # timestamp = order_json["timestamp"]
        # updated_timestamp = order_json["updated_timestamp"]

        timestamp = Safe_Datetime_Converter.string_to_datetime(order_json["timestamp"])
        updated_timestamp = Safe_Datetime_Converter.string_to_datetime(order_json["updated_timestamp"])

        updated_timestamp_day = order_json["updated_timestamp"].split('T')[0]


        if updated_timestamp_day not in historical_prices_dic:
            print("#")
            print(updated_timestamp_day)
            print(order_json)
            print("#")
            raise Start_New_Day_Error()


        # check if it is a sell order
        if "decimals" in order_json["buy"]["data"]:

            type = "sell"

            card_name = order_json["sell"]["data"]["properties"]["name"]

            token_id = order_json["sell"]["data"]["token_id"]
            token_address = order_json["sell"]["data"]["id"]

            if int(token_id) in mythic_card_number_list:
                card_quality = "Mythic"
            else:
                if order_json["sell"]["data"]["properties"]["image_url"]:
                    card_quality_number = int(order_json["sell"]["data"]["properties"]["image_url"].split("q=")[1])

                    if card_quality_number == 1:
                        card_quality = "Diamond"
                    elif card_quality_number == 2:
                        card_quality = "Gold"
                    elif card_quality_number == 3:
                        card_quality = "Shadow"
                    elif card_quality_number == 4:
                        card_quality = "Meteorite"
                    elif card_quality_number == 5:
                        card_quality = "Plain"
                    else:
                        card_quality = None
                else:
                    card_quality = None

            quantity = order_json["buy"]["data"]["quantity"]
            decimals = order_json["buy"]["data"]["decimals"]

            price_crypto_as_float = Number_Converter.get_float_from_quantity_decimal(decimals=decimals, quantity=quantity)

            if order_json["buy"]["type"] == "ETH":
                currency = "ETH"
                dic_entry = historical_prices_dic[updated_timestamp_day]["ETH"]
            else:
                if order_json["buy"]["data"]["token_address"] == "0xccc8cb5229b0ac8069c51fd58367fd1e622afd97":
                    currency = "GODS"
                    dic_entry = historical_prices_dic[updated_timestamp_day]["GODS"]
                elif order_json["buy"]["data"]["token_address"] == "0xf57e7e7c23978c3caec3c3548e3d615c346e79ff":
                    currency = "IMX"
                    dic_entry = historical_prices_dic[updated_timestamp_day]["IMX"]
                elif order_json["buy"]["data"]["token_address"] == "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48":
                    currency = "USDC"
                    dic_entry = historical_prices_dic[updated_timestamp_day]["USDC"]
                elif order_json["buy"]["data"]["token_address"] == "0x9ab7bb7fdc60f4357ecfef43986818a2a3569c62":
                    currency = "GOG"
                    dic_entry = historical_prices_dic[updated_timestamp_day]["GOG"]
                elif order_json["buy"]["data"]["token_address"] == "0xed35af169af46a02ee13b9d79eb57d6d68c1749e":
                    currency = "OMI"
                    dic_entry = historical_prices_dic[updated_timestamp_day]["OMI"]
                else:
                    print(order_json["buy"]["data"]["token_address"])
                    print(json.dumps(order_json, indent = 4))
                    dic_entry = None
                    raise Exception("This currency is not yet implemented")

            if dic_entry != None:
                price_euro_at_updated_timestamp_day = dic_entry * price_crypto_as_float
            else:
                price_euro_at_updated_timestamp_day = None

            if status == "cancelled":
                new_order_object = Cancelled_Order_GU(order_id, user, token_id, status, type, timestamp, updated_timestamp)
            else:
                new_order_object = Order_GU(order_id, user, token_id, token_address, status, type, card_name,
                                            card_quality, quantity, decimals, currency, price_euro_at_updated_timestamp_day,
                                            timestamp, updated_timestamp)
            return new_order_object

        #buy order
        elif "decimals" in order_json["sell"]["data"]:

            type = "buy"

            card_name = order_json["buy"]["data"]["properties"]["name"]

            token_id = order_json["buy"]["data"]["token_id"]
            token_address = order_json["buy"]["data"]["id"]

            if int(token_id) in mythic_card_number_list:
                card_quality = "Mythic"
            else:
                if order_json["buy"]["data"]["properties"]["image_url"]:
                    card_quality_number = int(order_json["buy"]["data"]["properties"]["image_url"].split("q=")[1])

                    if card_quality_number == 1:
                        card_quality = "Diamond"
                    elif card_quality_number == 2:
                        card_quality = "Gold"
                    elif card_quality_number == 3:
                        card_quality = "Shadow"
                    elif card_quality_number == 4:
                        card_quality = "Meteorite"
                    elif card_quality_number == 5:
                        card_quality = "Plain"
                    else:
                        card_quality = None
                else:
                    card_quality = None

            quantity = order_json["sell"]["data"]["quantity"]
            decimals = order_json["sell"]["data"]["decimals"]

            price_crypto_as_float = Number_Converter.get_float_from_quantity_decimal(quantity=quantity, decimals=decimals)

            if order_json["sell"]["type"] == "ETH":
                currency = "ETH"
                dic_entry = historical_prices_dic[updated_timestamp_day]["ETH"]
            else:
                if order_json["sell"]["data"]["token_address"] == "0xccc8cb5229b0ac8069c51fd58367fd1e622afd97":
                    currency = "GODS"
                    dic_entry = historical_prices_dic[updated_timestamp_day]["GODS"]
                elif order_json["sell"]["data"]["token_address"] == "0xf57e7e7c23978c3caec3c3548e3d615c346e79ff":
                    currency = "IMX"
                    dic_entry = historical_prices_dic[updated_timestamp_day]["IMX"]
                elif order_json["sell"]["data"]["token_address"] == "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48":
                    currency = "USDC"
                    dic_entry = historical_prices_dic[updated_timestamp_day]["USDC"]
                elif order_json["sell"]["data"]["token_address"] == "0x9ab7bb7fdc60f4357ecfef43986818a2a3569c62":
                    currency = "GOG"
                    dic_entry = historical_prices_dic[updated_timestamp_day]["GOG"]
                elif order_json["sell"]["data"]["token_address"] == "0xed35af169af46a02ee13b9d79eb57d6d68c1749e":
                    currency = "OMI"
                    dic_entry = historical_prices_dic[updated_timestamp_day]["OMI"]
                else:
                    print(order_json["sell"]["data"]["token_address"])
                    print(json.dumps(order_json, indent=4))
                    dic_entry = None
                    raise Exception("This currency is not yet implemented")

            if dic_entry != None:
                price_euro_at_updated_timestamp_day = dic_entry * price_crypto_as_float
            else:
                price_euro_at_updated_timestamp_day = None


            if status == "cancelled":
                new_order_object = Cancelled_Order_GU(order_id, user, token_id, status, type, timestamp, updated_timestamp)
            else:
                new_order_object = Order_GU(order_id, user, token_id, token_address, status, type, card_name,
                                            card_quality, quantity, decimals, currency, price_euro_at_updated_timestamp_day,
                                            timestamp, updated_timestamp)
            return new_order_object

        else:
            #this means it was a trade of two cards
            None


    @staticmethod
    def string_to_object(order_string):

        try:
            if "order_id" in order_string:
                order_as_json = order_string
        except Exception as e:
            try:
                order_as_json = json.loads(order_string)
            except Exception as e:
                print(e)
                raise

        status = order_as_json["status"]

        if status == "cancelled":
            order_id = order_as_json["order_id"]
            user = order_as_json["user"]
            token_id = order_as_json["token_id"]
            type = order_as_json["type"]

            timestamp = Safe_Datetime_Converter.string_to_datetime(order_as_json["timestamp"])
            updated_timestamp = Safe_Datetime_Converter.string_to_datetime(order_as_json["updated_timestamp"])

            new_order_object = Cancelled_Order_GU(order_id, user, token_id, status, type, timestamp, updated_timestamp)

        else:
            order_id = order_as_json["order_id"]
            user = order_as_json["user"]
            token_id = order_as_json["token_id"]
            token_address = order_as_json["token_address"]

            status = order_as_json["status"]
            type = order_as_json["type"]

            card_name = order_as_json["card_name"]
            card_quality = order_as_json["card_quality"]

            quantity = order_as_json["quantity"]
            decimals = order_as_json["decimals"]
            currency = order_as_json["currency"]
            price_euro_at_updated_timestamp_day = order_as_json["price_euro_at_updated_timestamp_day"]

            timestamp = Safe_Datetime_Converter.string_to_datetime(order_as_json["timestamp"])
            updated_timestamp = Safe_Datetime_Converter.string_to_datetime(order_as_json["updated_timestamp"])

            new_order_object = Order_GU(order_id, user, token_id, token_address, status, type, card_name,
                                             card_quality, quantity, decimals, currency, price_euro_at_updated_timestamp_day, timestamp,
                                             updated_timestamp)

        return new_order_object


    ###

    @staticmethod
    def convert_list_of_order_json_to_list_of_order(order_json_list, historical_prices_dic):

        order_list = []
        for order_json in order_json_list:
            new_order = Order_Factory_GU.order_json_to_object(order_json, historical_prices_dic)
            order_list.append(new_order)

        return order_list


    @staticmethod
    def create_order_list_from_path_list(path_list):

        combined_order_list = []

        for path in path_list:
            order_object_list = Order_Factory_GU.create_order_list_from_path(path)
            combined_order_list.extend(order_object_list)

        return combined_order_list


    @staticmethod
    def create_order_list_from_path(path_to_load):

        order_json_list = []
        with open(path_to_load, 'r', encoding='utf-8') as orders_in_string_file:
            for line_index, line in enumerate(orders_in_string_file):
                try:
                    line_json = json.loads(json.loads(line))
                    order_json_list.append(line_json)
                except:
                    try:
                        line_json = json.loads(line)
                        order_json_list.append(line_json)
                    except:
                        print(f"Line Index: {line_index}")
                        print(line)
        orders_in_string_file.close()

        order_object_list = []
        for order_json in order_json_list:
            new_order_object = Order_Factory_GU.string_to_object(order_json)
            order_object_list.append(new_order_object)

        return order_object_list
