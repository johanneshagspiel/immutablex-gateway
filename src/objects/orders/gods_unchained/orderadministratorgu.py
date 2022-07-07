import json
import os

import pandas as pd
import numpy as np
import pytz

from datetime import datetime, timedelta

from src.objects.enums.gettype import GetType
from src.objects.enums.status import Status
from src.objects.orders.gods_unchained.orderfactorygu import OrderFactoryGU
from src.operators.helpers.missedordershelper import MissedOrdersHelper
from src.scrappers.coinmarketcapscrapper import CoinMarketCapScrapper
from src.util.custom_exceptions import StartNewDayError
from src.util.files.filehandler import FileHandler
from src.util.files.fileiohelper import FileIoHelper
from src.util.helpers import ResultCollectionFilter, SafeDatetimeConverter
from src.util.numberconverter import NumberConverter


class OrderAdministratorGU:
    """
    The class that converts downloaded information into Orders and stores them appropriately
    """

    def __init__(self):
        """
        The constructor of the OrderAdministratorGU
        """
        pass

    @staticmethod
    def receive_orders_with_timestamp(get_type_string, status_string, result_list, start_time_stamp_str,
                                      next_start_time_stamp_str, historical_prices_file_dic, timestamp_before_download):
        """
        The method to convert the orders downloaded based on a from and to timestamp into Orders
        :param get_type_string: the type of the downloaded orders such as buy or sell
        :param status_string: the status of the downloaded order such as active
        :param result_list: a list of (from_timestamp_str, to_timestamp_str, json_list) tuple where
        the from_timestamp_str and the to_timestamp_str represent the time-period downloaded
        :param start_time_stamp_str: the first-time stamp downloaded
        :param next_start_time_stamp_str: the next start_time_stamp
        :param historical_prices_file_dic: the dictionary containing the historical prices
        :param timestamp_before_download: the timestamp before the download process started
        :return: None
        """

        get_type = GetType[get_type_string]
        status = Status[status_string]

        current_time_utc = datetime.utcnow()
        next_day_now = current_time_utc + timedelta(days=1) - timedelta(hours=current_time_utc.hour) \
                       - timedelta(minutes=current_time_utc.minute) - timedelta(seconds=current_time_utc.second) \
                       - timedelta(microseconds=current_time_utc.microsecond)
        seconds_to_next_day = (next_day_now - current_time_utc).total_seconds()

        day_at_download = timestamp_before_download - timedelta(hours=timestamp_before_download.hour) \
                          - timedelta(minutes=timestamp_before_download.minute) \
                          - timedelta(seconds=timestamp_before_download.second) \
                          - timedelta(microseconds=timestamp_before_download.microsecond)
        seconds_between_next_day_and_download_day = (next_day_now - day_at_download).total_seconds()

        if seconds_between_next_day_and_download_day > 86400:
            raise StartNewDayError()
        else:
            if seconds_to_next_day < 10:
                raise StartNewDayError()

        log_list = []
        order_object_list = []
        for from_timestamp_str, to_time_stamp_str, entry in result_list:
            download_info_dic = []
            for download_timestamp_str, order_json_list in entry:
                new_order_list = OrderFactoryGU.convert_list_of_order_json_to_list_of_order(order_json_list,
                                                                                            historical_prices_file_dic)
                new_order_list = list(filter(lambda x: x is not None, new_order_list))
                order_object_list.extend(new_order_list)
                order_id_list = [order.order_id for order in new_order_list]
                download_info_dic.append((download_timestamp_str, order_id_list))
            log_list.append((from_timestamp_str, to_time_stamp_str, download_info_dic))

        log_list = sorted(log_list, key=lambda x: x[0], reverse=False)

        order_object_list = list(filter(lambda x: x is not None, order_object_list))

        order_object_list = sorted(order_object_list, key=lambda x: x.updated_timestamp, reverse=False)

        restart_info_path = FileHandler.get_restart_info_path(get_type, status, "ROLLING")

        if os.path.isfile(restart_info_path):

            with open(restart_info_path, 'r', encoding='utf-8') as restart_info_file:
                previous_restart_dic = json.load(restart_info_file)
            restart_info_file.close()

            restart_info_dic = {}
            restart_info_dic["start_time_stamp"] = start_time_stamp_str
            restart_info_dic["next_start_time_stamp"] = next_start_time_stamp_str

            latest_split_file_number = previous_restart_dic["latest_split_file_number"]
            latest_new_file_dic = previous_restart_dic["new_file_dic"]

            if len(order_object_list) > 0:

                last_seen_order_object = order_object_list[-1]

                last_seen_updated_timestamp = SafeDatetimeConverter.datetime_to_string(
                    timestamp=last_seen_order_object.updated_timestamp)
                last_seen_order_id = last_seen_order_object.order_id

                restart_info_dic["last_seen_order_id"] = last_seen_order_id
                restart_info_dic["last_seen_updated_timestamp"] = last_seen_updated_timestamp
            else:
                restart_info_dic["last_seen_order_id"] = previous_restart_dic["last_seen_order_id"]
                restart_info_dic["last_seen_updated_timestamp"] = previous_restart_dic["last_seen_updated_timestamp"]

                restart_info_dic["latest_split_file_number"] = previous_restart_dic["latest_split_file_number"]
                restart_info_dic["new_file_dic"] = previous_restart_dic["new_file_dic"]

        else:
            restart_info_dic = {}
            restart_info_dic["start_time_stamp"] = start_time_stamp_str
            restart_info_dic["next_start_time_stamp"] = next_start_time_stamp_str

            latest_split_file_number = 0

            if len(order_object_list) > 0:

                last_seen_order_object = order_object_list[-1]
                last_seen_updated_timestamp = SafeDatetimeConverter.datetime_to_string(
                    timestamp=last_seen_order_object.updated_timestamp)
                last_seen_order_id = last_seen_order_object.order_id

                first_seen_order_object = order_object_list[0]
                first_seen_updated_timestamp = SafeDatetimeConverter.datetime_to_string(
                    timestamp=first_seen_order_object.updated_timestamp)
                first_seen_order_id = first_seen_order_object.order_id

                restart_info_dic["last_seen_order_id"] = last_seen_order_id
                restart_info_dic["last_seen_updated_timestamp"] = last_seen_updated_timestamp
                restart_info_dic["latest_split_file_number"] = 0
                restart_info_dic["new_file_dic"] = {}

                new_file_dic_entry = {}
                new_file_dic_entry["first_order_id"] = first_seen_order_id
                new_file_dic_entry["first_order_updated_timestamp"] = first_seen_updated_timestamp
                new_file_dic_entry["last_order_id"] = None
                new_file_dic_entry["last_order_updated_timestamp"] = None
                new_file_dic_entry["number_lines"] = 0

                restart_info_dic["new_file_dic"]['0'] = new_file_dic_entry
                latest_new_file_dic = restart_info_dic["new_file_dic"]

            else:
                restart_info_dic["last_seen_order_id"] = None
                restart_info_dic["last_seen_updated_timestamp"] = None
                restart_info_dic["latest_split_file_number"] = 0
                restart_info_dic["new_file_dic"] = {}

                new_file_dic_entry = {}
                new_file_dic_entry["first_order_id"] = None
                new_file_dic_entry["first_order_updated_timestamp"] = None
                new_file_dic_entry["last_order_id"] = None
                new_file_dic_entry["last_order_updated_timestamp"] = None
                new_file_dic_entry["number_lines"] = 0

                restart_info_dic["new_file_dic"]['0'] = new_file_dic_entry
                latest_new_file_dic = restart_info_dic["new_file_dic"]

        if len(order_object_list) > 0:

            base_path = FileHandler.get_store_path(get_type, status, "ROLLING")
            start_file_name = status_string.lower() + "_" + get_type_string.lower() + "_orders_rolling"

            latest_split_file_number_str = str(latest_split_file_number)

            if latest_split_file_number_str in latest_new_file_dic:
                previous_number_lines = latest_new_file_dic[latest_split_file_number_str]["number_lines"]
            else:
                previous_number_lines = 0

            previous_latest_split_file_number = latest_split_file_number
            current_new_file_list_index = previous_latest_split_file_number

            total_new_file_list = []
            total_new_file_list.append((current_new_file_list_index, []))
            list_index = 0

            for line_index, new_order in enumerate(order_object_list):

                updated_line_index = line_index + previous_number_lines

                if (updated_line_index  % 500000 == 0) and (updated_line_index != 0):
                    current_new_file_list_index = current_new_file_list_index + 1
                    total_new_file_list.append((current_new_file_list_index, []))
                    list_index = list_index + 1

                total_new_file_list[list_index][1].append(new_order)

            file_name_list = []
            for current_new_file_list_index, new_file_list in total_new_file_list:
                new_file_name = start_file_name + "_" + str(current_new_file_list_index) + ".json"
                file_name_list.append(new_file_name)
                new_file_store_path = str(base_path) + '\\' + new_file_name

                first_order_as_json = new_file_list[0]
                first_order_id = first_order_as_json.order_id
                first_order_updated_timestamp = SafeDatetimeConverter.datetime_to_string(
                    timestamp=first_order_as_json.updated_timestamp)

                last_order_as_json = new_file_list[-1]
                last_order_id = last_order_as_json.order_id
                last_order_updated_timestamp = SafeDatetimeConverter.datetime_to_string(
                    timestamp=last_order_as_json.updated_timestamp)

                latest_split_file_number = current_new_file_list_index
                current_new_file_list_index_str = str(current_new_file_list_index)

                if current_new_file_list_index == previous_latest_split_file_number:
                    latest_new_file_dic[current_new_file_list_index_str]["number_lines"] = \
                        len(new_file_list) + latest_new_file_dic[current_new_file_list_index_str]["number_lines"]
                else:
                    latest_new_file_dic[current_new_file_list_index_str] = {}
                    latest_new_file_dic[current_new_file_list_index_str]["first_order_id"] = first_order_id
                    latest_new_file_dic[current_new_file_list_index_str]["first_order_updated_timestamp"] = first_order_updated_timestamp
                    latest_new_file_dic[current_new_file_list_index_str]["number_lines"] = len(new_file_list)

                latest_new_file_dic[current_new_file_list_index_str]["last_order_id"] = last_order_id
                latest_new_file_dic[current_new_file_list_index_str]["last_order_updated_timestamp"] = last_order_updated_timestamp

                with open(new_file_store_path, 'a', encoding='utf-8') as new_file:
                    for order_object in new_file_list:
                        if order_object != None:
                            json.dump(json.dumps(order_object.to_print_dic()), new_file, ensure_ascii=False, indent=4)
                            new_file.write("\n")
                new_file.close()

            restart_info_dic["latest_split_file_number"] = latest_split_file_number
            restart_info_dic["new_file_dic"] = latest_new_file_dic

            with open(restart_info_path, 'w', encoding='utf-8') as restart_info_file:
                json.dump(restart_info_dic, restart_info_file, ensure_ascii=False, indent=4)
            restart_info_file.close()

            order_id_base_path = FileHandler.get_base_path("to_be_processed_downloaded_order_id_folder")
            to_be_processed_downloaded_order_id_path = str(order_id_base_path) + "\\to_be_processed_" + status_string.lower() + "_" + get_type_string.lower() + "_order_ids.json"

            order_id_list = [x.order_id for x in order_object_list]

            FileIoHelper.write_timestamp_log(get_type_string, status_string, log_list, file_name_list)
            FileIoHelper.write_to_be_processed_order_ids(order_id_list, to_be_processed_downloaded_order_id_path)

            to_be_processed_path = FileHandler.get_store_path(get_type, status, "TO_BE_PROCESSED")

            with open(to_be_processed_path, 'a', encoding='utf-8') as to_be_processed_file:
                for order_object in order_object_list:
                    if order_object != None:
                        json.dump(json.dumps(order_object.to_print_dic()), to_be_processed_file, ensure_ascii=False, indent=4)
                        to_be_processed_file.write("\n")
            to_be_processed_file.close()

        else:
            with open(restart_info_path, 'w', encoding='utf-8') as restart_info_file:
                json.dump(restart_info_dic, restart_info_file, ensure_ascii=False, indent=4)
            restart_info_file.close()

            FileIoHelper.write_timestamp_log(get_type_string, status_string, log_list)


    @staticmethod
    def received_double_checked_orders(missed_orders_list, get_type_str):
        """
        A method to deal with orders that have been downloaded for double checking.
        :param missed_orders_list: a list of OrderGUs
        :param get_type_str: the type of Order downloaded i.e. buy
        :return: None
        """

        #start_time = datetime.utcnow()

        get_type = get_type_str.upper()

        cancelled_orders_list = [entry for entry in missed_orders_list if entry.status == "cancelled"]
        filled_orders_list = [entry for entry in missed_orders_list if entry.status == "filled"]
        active_orders_list = [entry for entry in missed_orders_list if entry.status == "active"]
        inactive_orders_list = [entry for entry in missed_orders_list if entry.status == "inactive"]
        expired_orders_list = [entry for entry in missed_orders_list if entry.status == "expired"]


        combination_list = [("CANCELLED", get_type, cancelled_orders_list), ("FILLED", get_type, filled_orders_list),
                            ("ACTIVE", get_type, active_orders_list), ("INACTIVE", get_type, inactive_orders_list),
                            ("EXPIRED", get_type, expired_orders_list)]


        for status_string, get_type_string, order_object_list in combination_list:

            if len(order_object_list) > 0:

                status = Status[status_string]
                get_type = GetType[get_type_string]


                store_path = FileHandler.get_store_path(get_type, status, "DOUBLE_CHECKED")

                with open(store_path, 'a', encoding='utf-8') as new_file:
                    for order_object in order_object_list:
                        if order_object != None:
                            json.dump(json.dumps(order_object.to_print_dic()), new_file, ensure_ascii=False, indent=4)
                            new_file.write("\n")
                new_file.close()


                to_be_processed_path = FileHandler.get_store_path(get_type, status, "DOUBLE_CHECKED_TO_BE_PROCESSED")

                with open(to_be_processed_path, 'a', encoding='utf-8') as to_be_processed_file:
                    for order_object in order_object_list:
                        if order_object != None:
                            json.dump(json.dumps(order_object.to_print_dic()), to_be_processed_file, ensure_ascii=False, indent=4)
                            to_be_processed_file.write("\n")
                to_be_processed_file.close()


                order_id_base_path = FileHandler.get_base_path("to_be_processed_downloaded_order_id_folder")
                to_be_processed_downloaded_order_id_path = str(order_id_base_path) + "\\to_be_processed_" + status_string.lower() + "_" + get_type_string.lower() + "_order_ids.json"

                order_id_list = [x.order_id for x in order_object_list]
                FileIoHelper.write_to_be_processed_order_ids(order_id_list, to_be_processed_downloaded_order_id_path)


        #print(f"Double Checking Orders 1: {(datetime.utcnow() - start_time).total_seconds()}")


    @staticmethod
    def receive_missing_orders(missing_orders_list, historical_prices_file_dic, timestamp_before_download):
        """
        A method to deal with the Orders that have been missed in the initial download process
        :param missing_orders_list: a list of OrderGus
        :param historical_prices_file_dic: a dictionary of the historical prices
        :param timestamp_before_download: the timestamp before the download process has started. Needed to check if
        a new day has started during the download process
        :return: None
        """

        #start_time = datetime.utcnow()

        current_time_local = datetime.now()
        current_time_utc = current_time_local.astimezone(pytz.utc)
        next_day_now = current_time_utc + timedelta(days=1) - timedelta(hours=current_time_utc.hour) - timedelta(minutes=current_time_utc.minute) - timedelta(seconds=current_time_utc.second) - timedelta(microseconds=current_time_utc.microsecond)
        seconds_to_next_day = (next_day_now - current_time_utc).total_seconds()

        day_at_download = timestamp_before_download - timedelta(hours=timestamp_before_download.hour) - timedelta(minutes=timestamp_before_download.minute) - timedelta(seconds=timestamp_before_download.second) - timedelta(microseconds=timestamp_before_download.microsecond)
        seconds_between_next_day_and_download_day = (next_day_now - day_at_download).total_seconds()

        if seconds_between_next_day_and_download_day > 86400:
            raise StartNewDayError()
        else:
            if seconds_to_next_day < 10:
                raise StartNewDayError()


        does_not_exist_list = [{"order_id" : entry[1], "status" : "does_not_exist", "type" : entry[0]["code"]} for entry in missing_orders_list if "code" in entry[0]]

        existing_json_list = [entry for entry in missing_orders_list if "code" not in entry[0]]

        trade_list = [{"order_id" : entry[1], "status" : "trade", "type" : ResultCollectionFilter.get_trade_addresses(entry[0])} for entry in existing_json_list if ResultCollectionFilter.is_trade(entry[0])]
        not_trade_list = [entry for entry in existing_json_list if ResultCollectionFilter.is_trade(entry[0]) == False]

        other_collection_list = [x for x in not_trade_list if ResultCollectionFilter.belongs_to_gu(x[0]) == False]

        other_collection_id_list = [{"order_id": entry[1], "status" : "other_collection", "type": MissedOrdersHelper.get_collection_name(entry[0])} for entry in other_collection_list]
        other_collection_store_list = [(x[0], MissedOrdersHelper.get_collection_name(x[0])) for x in other_collection_list]

        gods_unchained_list = [x for x in not_trade_list if ResultCollectionFilter.belongs_to_gu(x[0])]
        order_object_list = [(entry[1], OrderFactoryGU.order_json_to_object(entry[0], historical_prices_file_dic)) for entry in gods_unchained_list]

        other_order_id_list = [{"order_id" : order_id, "status" : "other", "type" : "other"} for (order_id, order) in order_object_list if order == None]
        filtered_order_object_list = [(order_id, order) for (order_id, order) in order_object_list if order != None]

        buy_order_id_list = [(order_id, order) for (order_id, order) in filtered_order_object_list if order.type == "buy"]
        sell_order_id_list = [(order_id, order) for (order_id, order) in filtered_order_object_list if order.type == "sell"]

        cancelled_sell_orders_list = [(order_id, order) for (order_id, order) in sell_order_id_list if order.status == "cancelled"]
        filled_orders_sell_list = [(order_id, order) for (order_id, order) in sell_order_id_list if order.status == "filled"]
        active_orders_sell_list = [(order_id, order) for (order_id, order) in sell_order_id_list if order.status == "active"]
        inactive_orders_sell_list = [(order_id, order) for (order_id, order) in sell_order_id_list if order.status == "inactive"]
        expired_orders_sell_list = [(order_id, order) for (order_id, order) in sell_order_id_list if order.status == "expired"]

        cancelled_sell_order_ids = [{"order_id" : order_id, "status" : "cancelled", "type" : "sell"} for (order_id, order) in cancelled_sell_orders_list]
        filled_sell_order_ids = [{"order_id": order_id, "status": "filled", "type" : "sell"} for (order_id, order) in filled_orders_sell_list]
        active_sell_order_ids = [{"order_id": order_id, "status": "active", "type" : "sell"} for (order_id, order) in active_orders_sell_list]
        inactive_sell_order_ids = [{"order_id": order_id, "status": "inactive", "type": "sell"} for (order_id, order) in inactive_orders_sell_list]
        expired_sell_order_ids = [{"order_id": order_id, "status": "expired", "type": "sell"} for (order_id, order) in expired_orders_sell_list]


        cancelled_buy_orders_list = [(order_id, order) for (order_id, order) in buy_order_id_list if order.status == "cancelled"]
        filled_orders_buy_list = [(order_id, order) for (order_id, order) in buy_order_id_list if order.status == "filled"]
        active_orders_buy_list = [(order_id, order) for (order_id, order) in buy_order_id_list if order.status == "active"]
        inactive_orders_buy_list = [(order_id, order) for (order_id, order) in buy_order_id_list if order.status == "inactive"]
        expired_orders_buy_list = [(order_id, order) for (order_id, order) in buy_order_id_list if order.status == "expired"]

        cancelled_buy_order_ids = [{"order_id" : order_id, "status" : "cancelled", "type" : "buy"} for (order_id, order) in cancelled_buy_orders_list]
        filled_buy_order_ids = [{"order_id": order_id, "status": "filled", "type" : "buy"} for (order_id, order) in filled_orders_buy_list]
        active_buy_order_ids = [{"order_id": order_id, "status": "active", "type" : "buy"} for (order_id, order) in active_orders_buy_list]
        inactive_buy_order_ids = [{"order_id": order_id, "status": "inactive", "type": "buy"} for (order_id, order) in inactive_orders_buy_list]
        expired_buy_order_ids = [{"order_id": order_id, "status": "expired", "type": "buy"} for (order_id, order) in expired_orders_buy_list]


        combination_list = [("CANCELLED", "SELL", cancelled_sell_orders_list), ("FILLED", "SELL", filled_orders_sell_list), ("ACTIVE", "SELL", active_orders_sell_list), ("INACTIVE", "SELL", inactive_orders_sell_list), ("EXPIRED", "SELL", expired_orders_sell_list),
                            ("CANCELLED", "BUY", cancelled_buy_orders_list), ("FILLED", "BUY", filled_orders_buy_list), ("ACTIVE", "BUY", active_orders_buy_list), ("INACTIVE", "BUY", inactive_orders_buy_list), ("EXPIRED", "BUY", expired_orders_buy_list)]

        for status_string, get_type_string, order_list in combination_list:

            if len(order_list) > 0:

                order_object_list = [x[1] for x in order_list]

                status = Status[status_string]
                get_type = GetType[get_type_string]


                store_path = FileHandler.get_store_path(get_type, status, "MISSED")

                with open(store_path, 'a', encoding='utf-8') as new_file:
                    for order_object in order_object_list:
                        if order_object != None:
                            json.dump(json.dumps(order_object.to_print_dic()), new_file, ensure_ascii=False, indent=4)
                            new_file.write("\n")
                new_file.close()


                # to_be_processed_path = File_Handler.get_store_path(get_type, status, "MISSED_TO_BE_PROCESSED")
                #
                # with open(to_be_processed_path, 'a', encoding='utf-8') as to_be_processed_file:
                #     for order_object in order_object_list:
                #         if order_object != None:
                #             json.dump(json.dumps(order_object.to_print_dic()), to_be_processed_file, ensure_ascii=False, indent=4)
                #             to_be_processed_file.write("\n")
                # to_be_processed_file.close()


        order_id_list = []
        order_id_list.extend(does_not_exist_list)
        order_id_list.extend(other_order_id_list)
        order_id_list.extend(trade_list)

        order_id_list.extend(other_collection_id_list)

        order_id_list.extend(cancelled_sell_order_ids)
        order_id_list.extend(filled_sell_order_ids)
        order_id_list.extend(active_sell_order_ids)
        order_id_list.extend(inactive_sell_order_ids)
        order_id_list.extend(expired_sell_order_ids)

        order_id_list.extend(cancelled_buy_order_ids)
        order_id_list.extend(filled_buy_order_ids)
        order_id_list.extend(active_buy_order_ids)
        order_id_list.extend(inactive_buy_order_ids)
        order_id_list.extend(expired_buy_order_ids)

        order_id_list = sorted(order_id_list, key= lambda x: x["order_id"])

        MissedOrdersHelper.write_other_collections_list(other_collection_store_list)

        FileIoHelper.write_missed_order_id_list_to_file(order_id_list)

        #print(f"Missed Orders 1: {(datetime.utcnow() - start_time).total_seconds()}")


    @staticmethod
    def receive_purchase_error_order(purchase_error_order):
        """
        Method to deal with purchase error orders
        :param purchase_error_order: the purchase error order
        :return: None
        """

        store_file_path = FileHandler.get_store_path(get_type=str(purchase_error_order.type), status=str(purchase_error_order.status), file_type="purchase_error")
        with open(store_file_path, 'a', encoding='utf-8') as store_file:
            json.dump(json.dumps(purchase_error_order.to_print_dic()), store_file, ensure_ascii=False, indent=4)
            store_file.write("\n")
        store_file.close()

        to_be_processed_store_file_path = FileHandler.get_store_path(get_type=str(purchase_error_order.type), status=str(purchase_error_order.status), file_type="purchase_error_to_be_processed")
        with open(to_be_processed_store_file_path, 'a', encoding='utf-8') as to_be_processed_store_file:
            json.dump(json.dumps(purchase_error_order.to_print_dic()), to_be_processed_store_file, ensure_ascii=False, indent=4)
            to_be_processed_store_file.write("\n")
        to_be_processed_store_file.close()

        order_id_base_path = FileHandler.get_base_path("to_be_processed_downloaded_order_id_folder")
        to_be_processed_downloaded_order_id_path = str(order_id_base_path) + "\\purchase_error_to_be_processed_" \
                                                   + str(purchase_error_order.status).lower() + "_" \
                                                   + str(purchase_error_order.type).lower() + "_order_ids.json"
        order_id_list = [purchase_error_order.order_id]
        FileIoHelper.write_to_be_processed_order_ids(order_id_list, to_be_processed_downloaded_order_id_path)

    @staticmethod
    def write_updated_active_sell_order_list_to_file(active_updated_orders_list):
        """
        Method to write updated active sell orders to file
        :param active_updated_orders_list: the list of the active updated sell ordres
        :return: None
        """

        active_updated_sell_orders_file_path = FileHandler.get_base_path("active_sell_orders_updated")

        order_list = [order for order in active_updated_orders_list if order != None]
        order_dic_list = [json.dumps(order.to_print_dic()) for order in order_list]

        with open(active_updated_sell_orders_file_path, 'w', encoding='utf-8') as active_updated_sell_orders_file:
            active_updated_sell_orders_file.write('\n'.join(order_dic_list))
        active_updated_sell_orders_file.close()


    @staticmethod
    def write_updated_active_sell_order_df_to_file(active_order_df):
        """
        Method to write an updated active sell order DataFrame to file
        :param active_order_df: the updated active sell order DataFrame
        :return: None
        """

        active_order_df = active_order_df.reset_index()

        active_order_df = active_order_df[["order_id", "user", "token_id", "token_address", "status", "type",
                                           "card_name", "card_quality", "quantity", "decimals", "currency", "price_euro_at_updated_timestamp_day",
                                           "timestamp", "updated_timestamp"]]

        active_updated_sell_orders_file_path = FileHandler.get_base_path("active_sell_orders_updated")
        active_order_df.to_csv(active_updated_sell_orders_file_path)

    @staticmethod
    def convert_df_to_order_list(input_df):
        """
        Method to convert an Order DataFrame to list
        :param input_df: an Order DataFrame
        :return: a list of OrderGUs
        """

        input_df = input_df[["order_id", "user", "token_id", "token_address", "status", "type",
                                           "card_name", "card_quality", "quantity", "decimals", "currency", "price_euro_at_updated_timestamp_day",
                                           "timestamp", "updated_timestamp"]]

        input_df['updated_timestamp'] = input_df.updated_timestamp.dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        input_df['timestamp'] = input_df.timestamp.dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        input_df['json'] = input_df.apply(lambda x: x.to_json(), axis=1)
        json_list = input_df['json'].to_list()

        order_list = []

        for line_index, line in enumerate(json_list):
            try:
                line_json = json.loads(line)
                order_object = OrderFactoryGU.string_to_object(line_json)
                order_list.append(order_object)
            except:
                try:
                    line_json = json.loads(json.loads(line))
                    order_object = OrderFactoryGU.string_to_object(line_json)
                    order_list.append(order_object)
                except Exception as e:
                    print(e)
                    print(f"Line Index: {line_index}")
                    print(line)

        return order_list

    @staticmethod
    def create_active_updated_orders_df(get_type_string):
        """
        A method to create an active update order DataFrame
        :param get_type_string: the type of active updated Order i.e. Sell or buy
        :return: the active update order DataFrame
        """

        active_sell_orders_updated_file_path = FileHandler.get_base_path("active_sell_orders_updated")

        #df = OrderAdministratorGU.create_df_from_path(active_sell_orders_updated_file_path)
        df = pd.read_csv(active_sell_orders_updated_file_path, index_col=0)

        df = df.astype({'order_id': 'int64'})
        df = df.astype({'decimals': 'int64'})

        df = df.astype({'updated_timestamp': 'datetime64[ns, UTC]'})
        df = df.astype({'timestamp': 'datetime64[ns, UTC]'})

        # update the price to new price
        currency_prices_dic = CoinMarketCapScrapper.get_latest_currency_price()

        df["price_crypto"] = np.vectorize(lambda x, y: NumberConverter.get_float_from_quantity_decimal(x, y))(df["quantity"], df["decimals"])
        df["price_euro"] = np.vectorize(lambda x, y: currency_prices_dic[x] * y)(df["currency"], df["price_crypto"])

        return df

    @staticmethod
    def create_df_for_orders(get_type_str, status_str, file_type_str):
        """
        Create a DataFrame for a kind of order
        :param get_type_str: the type of the Order such as i.e. buy or sell
        :param status_str: the status of the order i.e. active or filled
        :param file_type_str: the file_type i.e. double_checked or missed
        :return: the created DataFrame
        """

        file_path_list = FileHandler.get_all_paths_of_type_of_orders(get_type_str=get_type_str, status_str=status_str, file_type=file_type_str)

        active_order_df = OrderAdministratorGU.create_df_from_path_list(file_path_list)

        return active_order_df


    @staticmethod
    def create_df_from_path_list(file_path_list):
        """
        A method to create a DataFrame from a files at a path_list
        :param file_path_list: a list of paths to files
        :return: a DataFrame of OrderGUs
        """

        df_list = []
        for index, file_path in enumerate(file_path_list):

            df = OrderAdministratorGU.create_df_from_path(file_path)
            df_list.append(df)

        df = pd.concat(df_list)

        df = df.reset_index()
        df = df.drop(columns=["index"])

        return df


    @staticmethod
    def create_df_from_path(file_path):
        """
        A method to create a DataFrame from Orders stored at a file at a path
        :param file_path: path to the file
        :return: a DataFrame of Order GUs
        """

        temp_list = []
        with open(file_path, 'r', encoding='utf-8') as orders_in_string_file:
            for line_index, line in enumerate(orders_in_string_file):
                try:
                    line_json = json.loads(json.loads(line))
                    temp_list.append(line_json)
                except:
                    try:
                        line_json = json.loads(line)
                        temp_list.append(line_json)
                    except:
                        print(f"Line Index: {line_index}")
                        print(line)
        orders_in_string_file.close()


        json_list = json.dumps(temp_list)
        df = pd.read_json(json_list)

        df = df.astype({'order_id': 'int64'})
        #df = df.astype({'decimals': 'int64'})

        df = df.astype({'updated_timestamp': 'datetime64[ns, UTC]'})
        df = df.astype({'timestamp': 'datetime64[ns, UTC]'})

        return df

    @staticmethod
    def create_df_from_order_list(order_list):
        """
        A method to create a DataFrame from a list of Orders
        :param order_list: the list of orders to be converted
        :return: a DataFrame of Orders
        """

        temp_list = []
        for order in order_list:
            order_dic = order.to_print_dic()
            temp_list.append(order_dic)

        json_list = json.dumps(temp_list)
        df = pd.read_json(json_list)

        df = df.astype({'order_id': 'int64'})
        #df = df.astype({'decimals': 'int64'})

        df = df.astype({'updated_timestamp': 'datetime64[ns, UTC]'})
        df = df.astype({'timestamp': 'datetime64[ns, UTC]'})

        return df

    @staticmethod
    def create_active_updated_orders_df_from_order_list(order_list):
        """
        A method to create a DataFrame of active updated orders from a list of OrderGUs
        :param order_list: a list of OrderGUs
        :return: a DataFrame of active updated orders
        """

        df = OrderAdministratorGU.create_df_from_order_list(order_list)

        # update the price to new price
        currency_prices_dic = CoinMarketCapScrapper.get_latest_currency_price()

        df["price_crypto"] = np.vectorize(lambda x, y: NumberConverter.get_float_from_quantity_decimal(x, y))(df["quantity"], df["decimals"])
        df["price_euro"] = np.vectorize(lambda x, y: currency_prices_dic[x] * y)(df["currency"], df["price_crypto"])

        return df

    @staticmethod
    def create_updated_active_sell_order_list():
        """
        A method to create a list of active updated sell OrderGUs
        :return: a list of OrderGUs
        """

        active_sell_orders_updated_file_path = FileHandler.get_base_path("active_sell_orders_updated")

        order_list = OrderAdministratorGU.create_order_list_from_path(active_sell_orders_updated_file_path)

        return order_list

    @staticmethod
    def create_order_list_from_path_list(file_path_list):
        """
        A method to create a list of OrderGUs from a list of path
        :param file_path_list: a list of path to files
        :return: a list of OrderGUs
        """

        combined_order_list = []

        for path in file_path_list:
            start_time = datetime.now()

            order_list = OrderAdministratorGU.create_order_list_from_path(path)
            combined_order_list.extend(order_list)

        return combined_order_list

    @staticmethod
    def create_order_list_from_path(file_path):
        """
        A method to create a list of OrderGUs from a path
        :param file_path: the path to a file
        :return: a list of OrderGUs
        """

        order_list = []
        with open(file_path, 'r', encoding='utf-8') as orders_in_string_file:
            for line_index, line in enumerate(orders_in_string_file):
                try:
                    line_json = json.loads(line)
                    order_object = OrderFactoryGU.string_to_object(line_json)
                    order_list.append(order_object)
                except:
                    try:
                        line_json = json.loads(json.loads(line))
                        order_object = OrderFactoryGU.string_to_object(line_json)
                        order_list.append(order_object)
                    except Exception as e:
                        print(e)
                        print(f"Line Index: {line_index}")
                        print(line)
        orders_in_string_file.close()

        return order_list

    @staticmethod
    def get_all_order_id_for_type_order(path_list):
        """
        A method to get all order ids from a file
        :param path_list: a path to a file
        :return: a list of Order IDs
        """

        order_id_list = []

        for index, path in enumerate(path_list):
            last_line_index = 0
            with open(path, 'r', encoding='utf-8') as orders_in_string_file:
                for line_index, line in enumerate(orders_in_string_file):
                    try:
                        line_json = json.loads(json.loads(line))
                        temp_order_id = line_json["order_id"]
                        order_id_list.append(temp_order_id)
                    except:
                        try:
                            line_json = json.loads(line)
                            temp_order_id = line_json["order_id"]
                            order_id_list.append(temp_order_id)
                        except:
                            print(f"Line Index: {line_index}")
                            print(line)

                    if line_index > last_line_index:
                        last_line_index = line_index

            orders_in_string_file.close()

        return order_id_list

    @staticmethod
    def get_all_order_id_for_type_order(path_list):
        """
        A method to get all order ids from a file
        :param path_list: a path to a file
        :return: a list of Order IDs
        """

        order_id_list = []

        for index, path in enumerate(path_list):
            last_line_index = 0
            with open(path, 'r', encoding='utf-8') as orders_in_string_file:
                for line_index, line in enumerate(orders_in_string_file):
                    try:
                        line_json = json.loads(json.loads(line))
                        temp_order_id = line_json["order_id"]
                        order_id_list.append(temp_order_id)
                    except:
                        try:
                            line_json = json.loads(line)
                            temp_order_id = line_json["order_id"]
                            order_id_list.append(temp_order_id)
                        except:
                            print(f"Line Index: {line_index}")
                            print(line)

                    if line_index > last_line_index:
                        last_line_index = line_index

            orders_in_string_file.close()

        return order_id_list
