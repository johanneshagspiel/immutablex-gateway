from src.objects.orders.gods_unchained.order_factory_gu import Order_Factory_GU
from src.scrappers.coinapi_scrapper import CoinAPI_Scrapper
from src.scrappers.immutable_x_scrapper import Immutable_X_Scrapper
from src.util.url.url_creator import URL_Creator


class Gods_Unchained_Poller():

    def __init__(self):

        self._url_creator = URL_Creator()

        self._collection_address = "0xacb3c6a43d15b907e8433077b6d38ae40936fe2c"

        self.immutable_x_scrapper = Immutable_X_Scrapper()


    ### Helper Methods ##########################################################################################

    def _convert_json_list_to_order_list(self, json_list):
        historical_currency_prices_dic = CoinAPI_Scrapper.get_historical_prices()
        order_list = [Order_Factory_GU.order_json_to_object(order_json, historical_currency_prices_dic) for order_json in json_list]
        return order_list

    def _convert_json_to_order(self, json):
        historical_currency_prices_dic = CoinAPI_Scrapper.get_historical_prices()
        order = Order_Factory_GU.order_json_to_object(json, historical_currency_prices_dic)
        return order

    ### Order by Type Methods ############################################################################################

    def _get_json_of_type_order(self, status_str, token_address_dic, one_time, meta_data_dic=None, time_tuple=None):

        url = self._url_creator.create_url_by_order_type(input_status_str=status_str, token_address_dic=token_address_dic, time_tuple=time_tuple, meta_data_dic=meta_data_dic)

        if one_time:
            json_list = self.immutable_x_scrapper.make_get_request(url=url)
        else:
            json_list = self.immutable_x_scrapper.make_get_request(url=url, checking_for_internal_errors=True, add_download_time_info=True, write_errors=True, timeout_duration=120)

        return json_list



    def _get_all_active_buy_jsons(self):
        token_address_dic = {}
        token_address_dic["buy_address"] = "NFT_" + str(self._collection_address)
        json_list = self._get_json_of_type_order(status_str="active", token_address_dic=token_address_dic, one_time=True)
        return json_list

    def get_all_active_buy_orders(self):
        json_list = self._get_all_active_buy_jsons()
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list


    def _get_all_active_buy_jsons_of_a_card(self, asset_name):
        token_address_dic = {}
        token_address_dic["buy_address"] = "NFT_" + str(self._collection_address)
        meta_data_dic = {}
        meta_data_dic["buy"] = {}
        meta_data_dic["buy"]["name"] = asset_name
        json_list = self._get_json_of_type_order(status_str="active", token_address_dic=token_address_dic, meta_data_dic=meta_data_dic, one_time=True)
        return json_list

    def get_all_active_buy_orders_of_a_card(self, asset_name):
        json_list = self._get_all_active_buy_jsons_of_a_card(asset_name)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list


    def _get_all_active_buy_jsons_for_a_currency(self, asset_name, currency_string):
        token_address_dic = {}
        token_address_dic["sell_address"] = currency_string
        token_address_dic["buy_address"] ="NFT_" + str(self._collection_address)
        meta_data_dic = {}
        meta_data_dic["buy"] = {}
        meta_data_dic["buy"]["name"] = asset_name
        json_list = self._get_json_of_type_order(status_str="active", token_address_dic=token_address_dic, meta_data_dic=meta_data_dic, one_time=True)
        return json_list

    def get_all_active_buy_orders_of_a_card_for_a_currency(self, asset_name, currency_string):
        json_list = self._get_all_active_buy_jsons_for_a_currency(asset_name, currency_string)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list


    def _get_all_active_buy_jsons_for_a_currency_and_quality(self, asset_name, currency_string, quality):
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
        json_list = self._get_all_active_buy_jsons_for_a_currency_and_quality(asset_name, currency_string, quality)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list


    def _get_all_active_sell_jsons(self):
        token_address_dic = {}
        token_address_dic["sell_address"] = "NFT_" + str(self._collection_address)
        json_list = self._get_json_of_type_order(status_str="active", token_address_dic=token_address_dic, one_time=True)
        return json_list

    def get_all_active_sell_orders(self):
        json_list = self._get_all_active_sell_jsons()
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list


    def _get_all_active_sell_jsons_of_a_card(self, asset_name):
        token_address_dic = {}
        token_address_dic["sell_address"] = "NFT_" + str(self._collection_address)
        meta_data_dic = {}
        meta_data_dic["sell"] = {}
        meta_data_dic["sell"]["name"] = asset_name
        json_list = self._get_json_of_type_order(status_str="active", token_address_dic=token_address_dic, meta_data_dic=meta_data_dic, one_time=True)
        return json_list

    def get_all_active_sell_orders_of_a_card(self, asset_name):
        json_list = self._get_all_active_sell_jsons_of_a_card(asset_name)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list


    def _get_all_active_sell_jsons_for_a_currency(self, asset_name, currency_string):
        token_address_dic = {}
        token_address_dic["sell_address"] = "NFT_" + str(self._collection_address)
        token_address_dic["buy_address"] = currency_string
        meta_data_dic = {}
        meta_data_dic["sell"] = {}
        meta_data_dic["sell"]["name"] = asset_name
        json_list = self._get_json_of_type_order(status_str="active", token_address_dic=token_address_dic, meta_data_dic=meta_data_dic, one_time=True)
        return json_list

    def get_all_active_sell_orders_for_a_currency(self, asset_name, currency_string):
        json_list = self._get_all_active_sell_jsons_for_a_currency(asset_name, currency_string)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list


    def _get_all_active_sell_jsons_for_a_currency_and_quality(self, asset_name, currency_string, quality):
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
        json_list = self._get_all_active_sell_jsons_for_a_currency_and_quality(asset_name, currency_string, quality)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list


    def _get_all_active_sell_jsons_for_a_currency_and_quality_and_min_buy_quantity(self, asset_name, currency_string, quality, buy_min_quantity_str):
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
        json_list = self._get_all_active_sell_jsons_for_a_currency_and_quality_and_min_buy_quantity(asset_name, currency_string, quality, buy_min_quantity_str)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list



    def _get_all_sell_jsons_in_time_period_of_status(self, status_str, from_time_stamp_str, to_time_stamp_str, one_time):
        time_tuple = (from_time_stamp_str, to_time_stamp_str)
        token_address_dic = {}
        token_address_dic["sell_address"] = "NFT_" + str(self._collection_address)
        json_list = self._get_json_of_type_order(status_str=status_str, token_address_dic=token_address_dic, meta_data_dic=None, one_time=one_time, time_tuple=time_tuple)
        return json_list

    def get_all_sell_orders_in_time_period_of_status(self, status_str, from_time_stamp_str, to_time_stamp_str):
        json_list = self._get_all_sell_jsons_in_time_period_of_status(status_str, from_time_stamp_str, to_time_stamp_str)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list


    def _get_all_buy_jsons_in_time_period_of_status(self, status_str, from_time_stamp_str, to_time_stamp_str, one_time):
        time_tuple = (from_time_stamp_str, to_time_stamp_str)
        token_address_dic = {}
        token_address_dic["buy_address"] = "NFT_" + str(self._collection_address)
        json_list = self._get_json_of_type_order(status_str=status_str, token_address_dic=token_address_dic, meta_data_dic=None, one_time=one_time, time_tuple=time_tuple)
        return json_list

    def get_all_buy_orders_in_time_period_of_status(self, status_str, from_time_stamp_str, to_time_stamp_str):
        json_list = self._get_all_buy_jsons_in_time_period_of_status(status_str, from_time_stamp_str, to_time_stamp_str)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list


    def _get_all_sell_jsons_in_time_period(self, from_time_stamp_str, to_time_stamp_str):
        time_tuple = (from_time_stamp_str, to_time_stamp_str)
        token_address_dic = {}
        token_address_dic["sell_address"] = "NFT_" + str(self._collection_address)
        json_list = self._get_json_of_type_order(status_str=None, token_address_dic=token_address_dic, meta_data_dic=None, one_time=True, time_tuple=time_tuple)
        return json_list

    def get_all_sell_orders_in_time_period(self, from_time_stamp_str, to_time_stamp_str):
        json_list = self._get_all_sell_jsons_in_time_period(from_time_stamp_str, to_time_stamp_str)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list


    def _get_all_buy_jsons_in_time_period(self, from_time_stamp_str, to_time_stamp_str):
        time_tuple = (from_time_stamp_str, to_time_stamp_str)
        token_address_dic = {}
        token_address_dic["buy_address"] = "NFT_" + str(self._collection_address)
        json_list = self._get_json_of_type_order(status_str=None, token_address_dic=token_address_dic, meta_data_dic=None, one_time=True, time_tuple=time_tuple)
        return json_list

    def get_all_buy_orders_in_time_period(self, from_time_stamp_str, to_time_stamp_str):
        json_list = self._get_all_buy_jsons_in_time_period(from_time_stamp_str, to_time_stamp_str)
        order_list = self._convert_json_list_to_order_list(json_list)
        return order_list


    def get_orders_based_on_timestamp(self, get_type_str, status_str, from_time_stamp_str, to_time_stamp_str):

        if get_type_str.lower() == "sell":
            return self._get_all_sell_jsons_in_time_period_of_status(status_str=status_str, from_time_stamp_str=from_time_stamp_str, to_time_stamp_str=to_time_stamp_str, one_time=False)

        elif get_type_str.lower() == "buy":
            return self._get_all_buy_jsons_in_time_period_of_status(status_str=status_str, from_time_stamp_str=from_time_stamp_str, to_time_stamp_str=to_time_stamp_str, one_time=False)


    ### Order by ID ###############################################################################################


    def _get_json_by_order_id(self, order_id):
        url = self._url_creator.create_url_by_order_id(order_id)
        json_list = self.immutable_x_scrapper.make_get_request(url, checking_for_internal_errors=False, add_download_time_info=False, write_errors=False, timeout_duration=60)
        return json_list[0]

    def get_order_by_order_id(self, order_id):
        json = self._get_json_by_order_id(order_id)
        order = self._convert_json_to_order(json)
        return order


    def _get_jsons_by_sell_token_id(self, sell_token_id):
        url = self._url_creator.create_url_by_sell_token_id(sell_token_id)
        json_list = self.immutable_x_scrapper.make_get_request(url, checking_for_internal_errors=True, add_download_time_info=False, write_errors=False, timeout_duration=None)
        return json_list

    def get_jsons_by_user_status_sell_token_id(self, user_str, status_str, sell_token_id_str):
        url = self._url_creator.create_url_of_order_by_user_status_sell_token_id(user_str, status_str, sell_token_id_str)
        json_list = self.immutable_x_scrapper.make_get_request(url=url)
        return json_list


    def get_jsons_by_user_status_buy_token_id(self, user_str, status_str, buy_token_id_str):
        url = self._url_creator.create_url_of_order_by_user_status_buy_token_id(user_str, status_str, buy_token_id_str)
        json_list = self.immutable_x_scrapper.make_get_request(url=url)
        return json_list



    ### Collection Methods ######################################################################################

    def get_collection_name(self, collection_address):
        url = self._url_creator.create_url_by_collection_address(collection_address)
        result = self.immutable_x_scrapper.make_get_request(url, checking_for_internal_errors=False, add_download_time_info=False, write_errors=False, timeout_duration=None)
        collection_name = result[0]["name"]
        return collection_name


    def _get_all_collection_info(self):
        url = self._url_creator.create_url_by_collection_address(collection_address="")
        json_list = self.immutable_x_scrapper.make_get_request(url, checking_for_internal_errors=False, add_download_time_info=False, write_errors=False, timeout_duration=None)
        return json_list

    def get_collection_address_of_collection_name(self, collection_name):
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
