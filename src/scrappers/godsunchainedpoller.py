from src.objects.orders.gods_unchained.orderfactorygu import OrderFactoryGU
from src.scrappers.coinapiscrapper import CoinAPIScrapper
from src.scrappers.immutablexscrapper import ImmutableXScrapper
from src.util.url.urlcreator import UrlCreator


class GodsUnchainedPoller:
    """
    A class to interact with the IMX api to download information about Gods Unchained cards
    """

    def __init__(self):
        """
        The constructor of the GodsUnchainedPoller
        """

        self._url_creator = UrlCreator()

        self._collection_address = "0xacb3c6a43d15b907e8433077b6d38ae40936fe2c"

        self.immutable_x_scrapper = ImmutableXScrapper()

    def _convert_json_list_to_order_list(self, json_list):
        """
        A helper method to convert a list of dictionaries into OrderGU objects
        :param json_list: a list of dictionaries
        :return: a list of OrderGU objects
        """
        historical_currency_prices_dic = CoinAPIScrapper.get_historical_prices()
        order_list = [OrderFactoryGU.order_json_to_object(order_json, historical_currency_prices_dic) for order_json in json_list]
        return order_list

    def _convert_json_to_order(self, json):
        """
        A helper method to convert one dictionary into a OrderGU object
        :param json: the dictionary to convert
        :return: an OrderGu object
        """
        historical_currency_prices_dic = CoinAPIScrapper.get_historical_prices()
        order = OrderFactoryGU.order_json_to_object(json, historical_currency_prices_dic)
        return order

    def _get_json_of_type_order(self, status_str, token_address_dic, one_time, meta_data_dic=None, time_tuple=None):
        """
        A method to download information about a kind of order in json form
        :param status_str: the status of the orders i.e. active
        :param token_address_dic: the token_addresses of the orders i.e. buyer token address
        :param one_time: whether this is a one_time download and thus should not keep track of any errors encountered
        :param meta_data_dic: a dictionary with information about the request for the error detection
        :param time_tuple: the to and from timestamp to be considered
        :return: a list of orders in dictionary form
        """

        url = self._url_creator.create_url_by_order_type(input_status_str=status_str, token_address_dic=token_address_dic, time_tuple=time_tuple, meta_data_dic=meta_data_dic)

        if one_time:
            json_list = self.immutable_x_scrapper.make_get_request(url=url)
        else:
            json_list = self.immutable_x_scrapper.make_get_request(url=url, checking_for_internal_errors=True, add_download_time_info=True, write_errors=True, timeout_duration=120)

        return json_list

    def _get_all_active_buy_jsons(self):
        """
        A method to get all active buy orders in dictionary form
        :return: all active buy orders in dictionary form
        """
        token_address_dic = {}
        token_address_dic["buy_address"] = "NFT_" + str(self._collection_address)
        json_list = self._get_json_of_type_order(status_str="active", token_address_dic=token_address_dic, one_time=True)
        return json_list

    def get_all_active_buy_orders(self):
        """
        A method to get all active buy orders in OrderGU form
        :return: all active buy orders in OrderGU form
        """
        json_list = self._get_all_active_buy_jsons()
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list

    def _get_all_active_buy_jsons_of_a_card(self, asset_name):
        """
        A method to get all active buy orders of a card in dictionary form
        :param asset_name: the card name
        :return: all active buy orders of a card in dictionary form
        """

        token_address_dic = {}
        token_address_dic["buy_address"] = "NFT_" + str(self._collection_address)
        meta_data_dic = {}
        meta_data_dic["buy"] = {}
        meta_data_dic["buy"]["name"] = asset_name
        json_list = self._get_json_of_type_order(status_str="active", token_address_dic=token_address_dic, meta_data_dic=meta_data_dic, one_time=True)
        return json_list

    def get_all_active_buy_orders_of_a_card(self, asset_name):
        """
        A method to get all active buy orders of a card in OrderGU form
        :param asset_name: the card name
        :return: all active buy orders of a card in OrderGU form
        """
        json_list = self._get_all_active_buy_jsons_of_a_card(asset_name)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list

    def _get_all_active_buy_jsons_for_a_currency(self, asset_name, currency_string):
        """
        A method to get all active buy orders of a card offered in a currency in dictionary form
        :param asset_name: the card name
        :param currency_string: the currency in which the card should be offered in
        :return: all active buy orders of a card offered in a currency in dictionary form
        """
        token_address_dic = {}
        token_address_dic["sell_address"] = currency_string
        token_address_dic["buy_address"] ="NFT_" + str(self._collection_address)
        meta_data_dic = {}
        meta_data_dic["buy"] = {}
        meta_data_dic["buy"]["name"] = asset_name
        json_list = self._get_json_of_type_order(status_str="active", token_address_dic=token_address_dic, meta_data_dic=meta_data_dic, one_time=True)
        return json_list

    def get_all_active_buy_orders_of_a_card_for_a_currency(self, asset_name, currency_string):
        """
        A method to get all active buy orders of a card offered in a currency in OrderGU form
        :param asset_name: the card name
        :param currency_string: the currency in which the card should be offered in
        :return: all active buy orders of a card offered in a currency in OrderGU form
        """
        json_list = self._get_all_active_buy_jsons_for_a_currency(asset_name, currency_string)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list

    def _get_all_active_buy_jsons_for_a_currency_and_quality(self, asset_name, currency_string, quality):
        """
        A method to get all active buy orders of a card offered in a currency and in a quality in dictionary form
        :param asset_name: the card name
        :param currency_string: the currency in which the card should be offered in
        :param quality: the quality of the card
        :return: all active buy orders of a card offered in a currency and in a quality in dictionary form
        """
        token_address_dic = {}
        token_address_dic["sell_address"] = currency_string
        token_address_dic["buy_address"] ="NFT_" + str(self._collection_address)
        meta_data_dic = {}
        meta_data_dic["buy"] = {}
        meta_data_dic["buy"]["name"] = asset_name
        meta_data_dic["buy"]["quality"] = quality
        json_list = self._get_json_of_type_order(status_str="active", token_address_dic=token_address_dic, meta_data_dic=meta_data_dic, one_time=True)
        return json_list

    def get_all_active_buy_orders_of_a_card_for_a_currency_and_quality(self, asset_name, currency_string, quality):
        """
        A method to get all active buy orders of a card offered in a currency and in a quality in OrderGU form
        :param asset_name: the card name
        :param currency_string: the currency in which the card should be offered in
        :param quality: the quality of the card
        :return: all active buy orders of a card offered in a currency and in a quality in dictionary form
        """
        json_list = self._get_all_active_buy_jsons_for_a_currency_and_quality(asset_name, currency_string, quality)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list

    def _get_all_active_sell_jsons(self):
        """
        A method to get all active sell orders in dictionary form
        :return: all active sell orders in dictionary form
        """
        token_address_dic = {}
        token_address_dic["sell_address"] = "NFT_" + str(self._collection_address)
        json_list = self._get_json_of_type_order(status_str="active", token_address_dic=token_address_dic, one_time=True)
        return json_list

    def get_all_active_sell_orders(self):
        """
        A method to get all active sell orders in OrderGU form
        :return: all active sell orders in OrderGu form
        """
        json_list = self._get_all_active_sell_jsons()
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list

    def _get_all_active_sell_jsons_of_a_card(self, asset_name):
        """
        A method to get all active sell orders of a card in dictionary form
        :param asset_name: the card name
        :return: all active sell orders of a card in dictionary form
        """
        token_address_dic = {}
        token_address_dic["sell_address"] = "NFT_" + str(self._collection_address)
        meta_data_dic = {}
        meta_data_dic["sell"] = {}
        meta_data_dic["sell"]["name"] = asset_name
        json_list = self._get_json_of_type_order(status_str="active", token_address_dic=token_address_dic, meta_data_dic=meta_data_dic, one_time=True)
        return json_list

    def get_all_active_sell_orders_of_a_card(self, asset_name):
        """
        A method to get all active sell orders of a card in OrderGU form
        :param asset_name: the card name
        :return: all active sell orders of a card in OrderGU form
        """
        json_list = self._get_all_active_sell_jsons_of_a_card(asset_name)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list

    def _get_all_active_sell_jsons_for_a_currency(self, asset_name, currency_string):
        """
        A method to get all active sell orders of a card in a currency in dictionary form
        :param asset_name: the card name
        :param currency_string:
        :return: all active sell orders of a card in a currency in dictionary form
        """
        token_address_dic = {}
        token_address_dic["sell_address"] = "NFT_" + str(self._collection_address)
        token_address_dic["buy_address"] = currency_string
        meta_data_dic = {}
        meta_data_dic["sell"] = {}
        meta_data_dic["sell"]["name"] = asset_name
        json_list = self._get_json_of_type_order(status_str="active", token_address_dic=token_address_dic, meta_data_dic=meta_data_dic, one_time=True)
        return json_list

    def get_all_active_sell_orders_for_a_currency(self, asset_name, currency_string):
        """
        A method to get all active sell orders of a card in a currency in OrderGU form
        :param asset_name: the card name
        :param currency_string: the currency in which the card is offered
        :return: all active sell orders of a card in a currency in OrderGU form
        """
        json_list = self._get_all_active_sell_jsons_for_a_currency(asset_name, currency_string)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list

    def _get_all_active_sell_jsons_for_a_currency_and_quality(self, asset_name, currency_string, quality):
        """
        A method to get all active sell orders of a card in a currency and a quality in dictionary form
        :param asset_name: the card name
        :param currency_string: the currency in which the card is offered
        :param quality: the quality of the card
        :return: all active sell orders of a card in a currency and quality in dictionary form
        """
        token_address_dic = {}
        token_address_dic["sell_address"] = "NFT_" + str(self._collection_address)
        token_address_dic["buy_address"] = currency_string
        meta_data_dic = {}
        meta_data_dic["sell"] = {}
        meta_data_dic["sell"]["name"] = asset_name
        meta_data_dic["sell"]["quality"] = quality
        json_list = self._get_json_of_type_order(status_str="active", token_address_dic=token_address_dic, meta_data_dic=meta_data_dic, one_time=True)
        return json_list

    def get_all_active_sell_orders_for_a_currency_and_quality(self, asset_name, currency_string, quality):
        """
        A method to get all active sell orders of a card in a currency and a quality in OrderGU form
        :param asset_name: the card name
        :param currency_string: the currency in which the card is offered
        :param quality: the quality of the card
        :return: all active sell orders of a card in a currency and quality in OrderGU form
        """
        json_list = self._get_all_active_sell_jsons_for_a_currency_and_quality(asset_name, currency_string, quality)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list

    def _get_all_active_sell_jsons_for_a_currency_and_quality_and_min_buy_quantity(self, asset_name, currency_string, quality, buy_min_quantity_str):
        """
        A method to get all active sell orders of a card in a currency, quality and minimum buy quantity in dictionary
        form
        :param asset_name: the card name
        :param currency_string: the currency in which the card is offered
        :param quality: the quality of the card
        :param buy_min_quantity_str: the minimum purchase quantity
        :return: all active sell orders of a card in a currency, quality and minimum buy quantity in dictionary form
        """
        token_address_dic = {}
        token_address_dic["sell_address"] = "NFT_" + str(self._collection_address)
        token_address_dic["buy_address"] = currency_string
        token_address_dic["buy_min_quantity"] = buy_min_quantity_str
        meta_data_dic = {}
        meta_data_dic["sell"] = {}
        meta_data_dic["sell"]["name"] = asset_name
        meta_data_dic["sell"]["quality"] = quality
        json_list = self._get_json_of_type_order(status_str="active", token_address_dic=token_address_dic, meta_data_dic=meta_data_dic, one_time=True)
        return json_list

    def get_all_active_sell_orders_for_a_currency_and_quality_and_min_buy_quantity(self, asset_name, currency_string, quality, buy_min_quantity_str):
        """
        A method to get all active sell orders of a card in a currency, quality and minimum buy quantity in OrderGU
        form
        :param asset_name: the card name
        :param currency_string: the currency in which the card is offered
        :param quality: the quality of the card
        :param buy_min_quantity_str: the minimum purchase quantity
        :return: all active sell orders of a card in a currency, quality and minimum buy quantity in OrderGU form
        """
        json_list = self._get_all_active_sell_jsons_for_a_currency_and_quality_and_min_buy_quantity(asset_name, currency_string, quality, buy_min_quantity_str)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list

    def _get_all_sell_jsons_in_time_period_of_status(self, status_str, from_time_stamp_str, to_time_stamp_str, one_time):
        """
        A method to get all sell orders in a time period of a certain status in dictionary form
        :param status_str: the status of the orders i.e. active
        :param from_time_stamp_str: the start of the time period to be considered
        :param to_time_stamp_str: the end of the time period to be considered
        :param one_time: whether this is a one time call of this method
        :return: all sell orders in a time period of a certain status in dictionary form
        """
        time_tuple = (from_time_stamp_str, to_time_stamp_str)
        token_address_dic = {}
        token_address_dic["sell_address"] = "NFT_" + str(self._collection_address)
        json_list = self._get_json_of_type_order(status_str=status_str, token_address_dic=token_address_dic, meta_data_dic=None, one_time=one_time, time_tuple=time_tuple)
        return json_list

    def get_all_sell_orders_in_time_period_of_status(self, status_str, from_time_stamp_str, to_time_stamp_str):
        """
        A method to get all sell orders in a time period of a certain status in OrderGu form
        :param status_str: the status of the orders i.e. active
        :param from_time_stamp_str: the start of the time period to be considered
        :param to_time_stamp_str: the end of the time period to be considered
        :param one_time: whether this is a one time call of this method
        :return: all sell orders in a time period of a certain status in OrderGu form
        """
        json_list = self._get_all_sell_jsons_in_time_period_of_status(status_str, from_time_stamp_str, to_time_stamp_str)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list

    def _get_all_buy_jsons_in_time_period_of_status(self, status_str, from_time_stamp_str, to_time_stamp_str, one_time):
        """
        A method to get all buy orders in a time period of a certain status in dictionary form
        :param status_str: the status of the orders i.e. active
        :param from_time_stamp_str: the start of the time period to be considered
        :param to_time_stamp_str: the end of the time period to be considered
        :param one_time: whether this is a one time call of this method
        :return: all sell orders in a time period of a certain status in dictionary form
        """
        time_tuple = (from_time_stamp_str, to_time_stamp_str)
        token_address_dic = {}
        token_address_dic["buy_address"] = "NFT_" + str(self._collection_address)
        json_list = self._get_json_of_type_order(status_str=status_str, token_address_dic=token_address_dic, meta_data_dic=None, one_time=one_time, time_tuple=time_tuple)
        return json_list

    def get_all_buy_orders_in_time_period_of_status(self, status_str, from_time_stamp_str, to_time_stamp_str):
        """
        A method to get all buy orders in a time period of a certain status in OrderGu form
        :param status_str: the status of the orders i.e. active
        :param from_time_stamp_str: the start of the time period to be considered
        :param to_time_stamp_str: the end of the time period to be considered
        :param one_time: whether this is a one time call of this method
        :return: all sell orders in a time period of a certain status in OrderGu form
        """
        json_list = self._get_all_buy_jsons_in_time_period_of_status(status_str, from_time_stamp_str, to_time_stamp_str)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list

    def _get_all_sell_jsons_in_time_period(self, from_time_stamp_str, to_time_stamp_str):
        """
        A method to get all sell orders in a time period of a certain status in dictionary form
        :param from_time_stamp_str: the start of the time period to be considered
        :param to_time_stamp_str: the end of the time period to be considered
        :return: all sell orders in a time period of a certain status in dictionary form
        """
        time_tuple = (from_time_stamp_str, to_time_stamp_str)
        token_address_dic = {}
        token_address_dic["sell_address"] = "NFT_" + str(self._collection_address)
        json_list = self._get_json_of_type_order(status_str=None, token_address_dic=token_address_dic, meta_data_dic=None, one_time=True, time_tuple=time_tuple)
        return json_list

    def get_all_sell_orders_in_time_period(self, from_time_stamp_str, to_time_stamp_str):
        """
        A method to get all sell orders in a time period of a certain status in OrderGU form
        :param from_time_stamp_str: the start of the time period to be considered
        :param to_time_stamp_str: the end of the time period to be considered
        :return: all sell orders in a time period of a certain status in OrderGU form
        """
        json_list = self._get_all_sell_jsons_in_time_period(from_time_stamp_str, to_time_stamp_str)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list

    def _get_all_buy_jsons_in_time_period(self, from_time_stamp_str, to_time_stamp_str):
        """
        A method to get all buy orders in a time period of a certain status in dictionary form
        :param from_time_stamp_str: the start of the time period to be considered
        :param to_time_stamp_str: the end of the time period to be considered
        :return: all buy orders in a time period of a certain status in dictionary form
        """
        time_tuple = (from_time_stamp_str, to_time_stamp_str)
        token_address_dic = {}
        token_address_dic["buy_address"] = "NFT_" + str(self._collection_address)
        json_list = self._get_json_of_type_order(status_str=None, token_address_dic=token_address_dic, meta_data_dic=None, one_time=True, time_tuple=time_tuple)
        return json_list

    def get_all_buy_orders_in_time_period(self, from_time_stamp_str, to_time_stamp_str):
        """
        A method to get all buy orders in a time period of a certain status in OrderGU form
        :param from_time_stamp_str: the start of the time period to be considered
        :param to_time_stamp_str: the end of the time period to be considered
        :return: all buy orders in a time period of a certain status in OrderGU form
        """
        json_list = self._get_all_buy_jsons_in_time_period(from_time_stamp_str, to_time_stamp_str)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list

    def get_orders_based_on_timestamp(self, get_type_str, status_str, from_time_stamp_str, to_time_stamp_str):
        """
        A method to all orders based on characteristics and time period
        :param get_type_str: the type of the order i.e. buy
        :param status_str: the status of the order i.e. active
        :param from_time_stamp_str: the start of the time period
        :param to_time_stamp_str: the end of the time period
        :return: a list of orders
        """
        if get_type_str.lower() == "sell":
            return self._get_all_sell_jsons_in_time_period_of_status(status_str=status_str, from_time_stamp_str=from_time_stamp_str, to_time_stamp_str=to_time_stamp_str, one_time=False)

        elif get_type_str.lower() == "buy":
            return self._get_all_buy_jsons_in_time_period_of_status(status_str=status_str, from_time_stamp_str=from_time_stamp_str, to_time_stamp_str=to_time_stamp_str, one_time=False)

    def _get_json_by_order_id(self, order_id):
        """
        A method to get an order by id in dictionary form
        :param order_id: the id of the order
        :return: an order in dictionary form
        """
        url = self._url_creator.create_url_by_order_id(order_id)
        json_list = self.immutable_x_scrapper.make_get_request(url, checking_for_internal_errors=False, add_download_time_info=False, write_errors=False, timeout_duration=60)
        return json_list[0]

    def get_order_by_order_id(self, order_id):
        """
        A method to get an order by id in OrderGU form
        :param order_id: the id of the order
        :return: an order in OrderGU form
        """
        json = self._get_json_by_order_id(order_id)
        order = self._convert_json_to_order(json)
        return order

    def _get_jsons_by_sell_token_id(self, sell_token_id):
        """
        A method to get all orders by sell token id in dictionary form
        :param sell_token_id: the token_id of the orders considered
        :return: all orders in dictionary form
        """
        url = self._url_creator.create_url_by_sell_token_id(sell_token_id)
        json_list = self.immutable_x_scrapper.make_get_request(url, checking_for_internal_errors=True, add_download_time_info=False, write_errors=False, timeout_duration=None)
        return json_list

    def get_jsons_by_user_status_sell_token_id(self, user_str, status_str, sell_token_id_str):
        """
        A method to get all orders by status, username and sell token id
        :param user_str: the wallet address of the owner
        :param status_str: the status of the order
        :param sell_token_id_str: the sell token id of a card
        :return: all orders in dictionary form
        """
        url = self._url_creator.create_url_of_order_by_user_status_sell_token_id(user_str, status_str, sell_token_id_str)
        json_list = self.immutable_x_scrapper.make_get_request(url=url)
        return json_list

    def get_jsons_by_user_status_buy_token_id(self, user_str, status_str, buy_token_id_str):
        """
        A method to get all orders by status, username and buy token id
        :param user_str: the wallet address of the owner
        :param status_str: the status of the order
        :param buy_token_id_str: the buy token id of a card
        :return: all orders in dictionary form
        """
        url = self._url_creator.create_url_of_order_by_user_status_buy_token_id(user_str, status_str, buy_token_id_str)
        json_list = self.immutable_x_scrapper.make_get_request(url=url)
        return json_list

    def get_collection_name(self, collection_address):
        """
        A method to get a collection's name based on its address
        :param collection_address: the collection address
        :return: the colleciont's name
        """
        url = self._url_creator.create_url_by_collection_address(collection_address)
        result = self.immutable_x_scrapper.make_get_request(url, checking_for_internal_errors=False, add_download_time_info=False, write_errors=False, timeout_duration=None)
        collection_name = result[0]["name"]
        return collection_name

    def _get_all_collection_info(self):
        """
        A method to get the name of all collections
        :return: a list of dictionaries
        """
        url = self._url_creator.create_url_by_collection_address(collection_address="")
        json_list = self.immutable_x_scrapper.make_get_request(url, checking_for_internal_errors=False, add_download_time_info=False, write_errors=False, timeout_duration=None)
        return json_list

    def get_collection_address_of_collection_name(self, collection_name):
        """
        A method to get a collection's address based on its name
        :param collection_name: a collection's name
        :return: a collection's address
        """
        all_collection_json_list = self._get_all_collection_info()
        potential_collection_name_list = [entry for entry in all_collection_json_list if entry["name"] == collection_name]

        if len(potential_collection_name_list) > 0:
            if len(potential_collection_name_list) > 1:
                raise Exception(f"Somehow there are two collections with this name {collection_name}")
            else:
                collection_name_dic = potential_collection_name_list[0]
                collection_address = collection_name_dic["address"]
                return collection_address
        else:
            return f"The collection with the name {collection_name} does not exist."
