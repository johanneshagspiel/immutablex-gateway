import json

from src.objects.orders.gods_unchained.cancelledordergu import CancelledOrderGU
from src.objects.orders.gods_unchained.order_gu import OrderGU
from src.util.custom_exceptions import StartNewDayError
from src.util.helpers import SafeDatetimeConverter
from src.util.numberconverter import NumberConverter


class OrderFactoryGU:
    """
    A Factory class to create an Order for Gods Unchained
    """

    def __init__(self):
        """
        The constructor of the OrderFactoryGU class
        """
        pass

    @staticmethod
    def order_json_to_object(order_json, historical_prices_dic):
        """
        A method to convert one downloaded order from a JSON dictionary to an instance of the class Order
        :param order_json: one downloaded order in the form of a dictionary
        :param historical_prices_dic: a dictionary from the CoinAIPScrapper representing the historical cryptocurrency
        prices
        :return: a new OrderGU instance
        """

        mythic_card_number_list = [100000, 100002, 65000, 65001, 65002, 65003, 65004]

        order_id = order_json["order_id"]
        user = order_json["user"]

        status = order_json["status"]

        timestamp = SafeDatetimeConverter.string_to_datetime(order_json["timestamp"])
        updated_timestamp = SafeDatetimeConverter.string_to_datetime(order_json["updated_timestamp"])

        updated_timestamp_day = order_json["updated_timestamp"].split('T')[0]

        if updated_timestamp_day not in historical_prices_dic:
            print("#")
            print(updated_timestamp_day)
            print(order_json)
            print("#")
            raise StartNewDayError()

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

            price_crypto_as_float = NumberConverter.get_float_from_quantity_decimal(decimals=decimals,
                                                                                    quantity=quantity)

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
                elif order_json["buy"]["data"]["token_address"] == "0x4d224452801aced8b2f0aebe155379bb5d594381":
                    currency = "APE"
                    dic_entry = historical_prices_dic[updated_timestamp_day]["APE"]

                elif order_json["buy"]["data"]["token_address"] == "0xe910c2a090516fb7a7be07f96a464785f2d5dc18":
                    currency = "CMT"
                    if "CMT" in historical_prices_dic[updated_timestamp_day]:
                        dic_entry = historical_prices_dic[updated_timestamp_day]["CMT"]
                    else:
                        dic_entry = None
                elif order_json["buy"]["data"]["token_address"] == "0x2caa4021e580b07d92adf8a40ec53b33a215d620":
                    currency = "VCO"
                    if "VCO" in historical_prices_dic[updated_timestamp_day]:
                        dic_entry = historical_prices_dic[updated_timestamp_day]["VCO"]
                    else:
                        dic_entry = None
                elif order_json["buy"]["data"]["token_address"] == "0x733b5056a0697e7a4357305fe452999a0c409feb":
                    currency = "VCORE"
                    if "VCORE" in historical_prices_dic[updated_timestamp_day]:
                        dic_entry = historical_prices_dic[updated_timestamp_day]["VCORE"]
                    else:
                        dic_entry = None

                else:
                    print(order_json["buy"]["data"]["token_address"])
                    print(json.dumps(order_json, indent=4))
                    raise Exception("This currency is not yet implemented")

            if dic_entry is not None:
                price_euro_at_updated_timestamp_day = dic_entry * price_crypto_as_float
            else:
                price_euro_at_updated_timestamp_day = None

            if status == "cancelled":
                new_order_object = CancelledOrderGU(order_id, user, token_id, status, type, timestamp,
                                                    updated_timestamp)
            else:
                new_order_object = OrderGU(order_id, user, token_id, token_address, status, type,
                                           card_name, card_quality, quantity, decimals, currency,
                                           price_euro_at_updated_timestamp_day, timestamp, updated_timestamp)
            return new_order_object

        # buy order
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

            price_crypto_as_float = NumberConverter.get_float_from_quantity_decimal(quantity=quantity,
                                                                                    decimals=decimals)

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
                elif order_json["buy"]["data"]["token_address"] == "0x4d224452801aced8b2f0aebe155379bb5d594381":
                    currency = "APE"
                    dic_entry = historical_prices_dic[updated_timestamp_day]["APE"]

                elif order_json["buy"]["data"]["token_address"] == "0xe910c2a090516fb7a7be07f96a464785f2d5dc18":
                    currency = "CMT"
                    if "CMT" in historical_prices_dic[updated_timestamp_day]:
                        dic_entry = historical_prices_dic[updated_timestamp_day]["CMT"]
                    else:
                        dic_entry = None
                elif order_json["buy"]["data"]["token_address"] == "0x2caa4021e580b07d92adf8a40ec53b33a215d620":
                    currency = "VCO"
                    if "VCO" in historical_prices_dic[updated_timestamp_day]:
                        dic_entry = historical_prices_dic[updated_timestamp_day]["VCO"]
                    else:
                        dic_entry = None
                elif order_json["buy"]["data"]["token_address"] == "0x733b5056a0697e7a4357305fe452999a0c409feb":
                    currency = "VCORE"
                    if "VCORE" in historical_prices_dic[updated_timestamp_day]:
                        dic_entry = historical_prices_dic[updated_timestamp_day]["VCORE"]
                    else:
                        dic_entry = None

                else:
                    print(order_json["sell"]["data"]["token_address"])
                    print(json.dumps(order_json, indent=4))
                    raise Exception("This currency is not yet implemented")

            if dic_entry is not None:
                price_euro_at_updated_timestamp_day = dic_entry * price_crypto_as_float
            else:
                price_euro_at_updated_timestamp_day = None

            if status == "cancelled":
                new_order_object = CancelledOrderGU(order_id, user, token_id, status, type, timestamp,
                                                    updated_timestamp)
            else:
                new_order_object = OrderGU(order_id, user, token_id, token_address, status, type, card_name,
                                           card_quality, quantity, decimals, currency,
                                           price_euro_at_updated_timestamp_day, timestamp, updated_timestamp)
            return new_order_object

        else:
            # this means it was a trade of two cards
            pass

    @staticmethod
    def string_to_object(order_string):
        """
        A method to convert an order in the form of a string into an OrderGu instance
        :param order_string: the order as a string (typically from reading a file)
        :return: an instance of OrderGU
        """

        try:
            if "order_id" in order_string:
                order_as_json = order_string
        except Exception:
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

            timestamp = SafeDatetimeConverter.string_to_datetime(order_as_json["timestamp"])
            updated_timestamp = SafeDatetimeConverter.string_to_datetime(order_as_json["updated_timestamp"])

            new_order_object = CancelledOrderGU(order_id, user, token_id, status, type, timestamp, updated_timestamp)

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

            timestamp = SafeDatetimeConverter.string_to_datetime(order_as_json["timestamp"])
            updated_timestamp = SafeDatetimeConverter.string_to_datetime(order_as_json["updated_timestamp"])

            new_order_object = OrderGU(order_id, user, token_id, token_address, status, type, card_name,
                                       card_quality, quantity, decimals, currency,
                                       price_euro_at_updated_timestamp_day, timestamp, updated_timestamp)

        return new_order_object

    @staticmethod
    def convert_list_of_order_json_to_list_of_order(order_json_list, historical_prices_dic):
        """
        Method to convert list of dictionaries to a list of OrderGUs
        :param order_json_list: list of dictionaries
        :param historical_prices_dic: a dictionary from the CoinAIPScrapper representing the historical cryptocurrency
        prices
        :return: a list of OrderGU instances
        """

        order_list = []
        for order_json in order_json_list:
            new_order = OrderFactoryGU.order_json_to_object(order_json, historical_prices_dic)
            order_list.append(new_order)

        return order_list

    @staticmethod
    def create_order_list_from_path_list(path_list):
        """
        Method to convert a list of files into a list of OrderGUs
        :param path_list: a list of paths to files that are read
        :return: a list of OrderGUs
        """

        combined_order_list = []

        for path in path_list:
            order_object_list = OrderFactoryGU.create_order_list_from_path(path)
            combined_order_list.extend(order_object_list)

        return combined_order_list

    @staticmethod
    def create_order_list_from_path(path_to_load):
        """
        A method to create a list of OrderGUs based on a file
        :param path_to_load: the path to the file to be read
        :return: a list of OrderGUs
        """

        order_json_list = []
        with open(path_to_load, 'r', encoding='utf-8') as orders_in_string_file:
            for line_index, line in enumerate(orders_in_string_file):
                try:
                    line_json = json.loads(json.loads(line))
                    order_json_list.append(line_json)
                except Exception:
                    try:
                        line_json = json.loads(line)
                        order_json_list.append(line_json)
                    except Exception:
                        print(f"Line Index: {line_index}")
                        print(line)
        orders_in_string_file.close()

        order_object_list = []
        for order_json in order_json_list:
            new_order_object = OrderFactoryGU.string_to_object(order_json)
            order_object_list.append(new_order_object)

        return order_object_list
