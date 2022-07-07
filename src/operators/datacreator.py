import copy
import glob
import json
import statistics
from datetime import datetime, timedelta
import os
from time import mktime
import pytz
from sklearn.linear_model import LinearRegression
from src.objects.orders.gods_unchained.orderadministratorgu import OrderAdministratorGU
from src.objects.orders.gods_unchained.orderfactorygu import OrderFactoryGU
from src.objects.win_rate.winrateadministrator import WinRateAdministrator
from src.operators.helpers.file_helpers import Processing_File_Helper
from src.scrappers.godsunchainedscrapper import GodsUnchainedScrapper
from src.scrappers.gods_unchained_winrate_poller import Gods_Unchained_Winrate_Poller
from src.util.custom_exceptions import ResponseError, RequestError, TooManyAPICalls, InternalServerError
from src.util.files.filehandler import FileHandler
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src.util.files.fileiohelper import FileIoHelper
from src.util.helpers import PandaHelper
from src.util.helpers import SafeDatetimeConverter

pd.set_option("display.precision", 3)
pd.set_option('display.max_columns', 800)
pd.set_option('display.width', 10000)



class DataCreator:
    """
    A method to create information based on downloaded orders
    """

    def __init__(self):
        """
        The constructor of the DataCreator
        """
        pass

    @staticmethod
    def parallel_process_downloaded_info(get_type_string, active_updated_orders_df):
        """
        A method to update information based on the current active updated orders DataFrame in parallel to downloading
        new information
        :param get_type_string: the type of order i.e. buy
        :param active_updated_orders_df: the current active updated orders DataFrame
        :return: None
        """

        print("\nProcessing Downloaded Info\n")
        total_start_time = datetime.now()

        processing_logs_dic = {}

        processing_logs_dic["processing_updated_active_orders"] = "initialized"

        processing_logs_dic["processing_today_timeline"] = "initialized"
        processing_logs_dic["processing_baseline_timeline"] = "initialized"

        #processing_logs_dic["card_win_rate_to_be_processed"] = "initialized"

        processing_logs_dic["creating_info_active_orders"] = "initialized"

        processing_logs_dic["active_to_be_processed"] = "initialized"
        processing_logs_dic["filled_to_be_processed"] = "initialized"
        processing_logs_dic["cancelled_to_be_processed"] = "initialized"
        processing_logs_dic["inactive_to_be_processed"] = "initialized"
        processing_logs_dic["expired_to_be_processed"] = "initialized"

        print("Creating Active Orders To Be Processed List")
        start_time = datetime.now()
        active_orders_to_be_processed_order_path_list = Processing_File_Helper.get_path_list_for_type_order_processing(
            get_type_string=get_type_string, status_string="active")
        active_orders_to_be_processed_exist = len(active_orders_to_be_processed_order_path_list) > 0

        if active_orders_to_be_processed_exist:
            additional_active_orders_df = \
                OrderAdministratorGU.create_df_from_path_list(active_orders_to_be_processed_order_path_list)

            processing_logs_dic["active_to_be_processed"] = "started"
            processing_logs_dic["processing_updated_active_orders"] = "started"
            processing_logs_dic["creating_info_active_orders"] = "started"
            FileIoHelper.write_processing_logs(processing_logs_dic)

        print(f"t: {(datetime.now() - start_time).total_seconds()}")

        print("Determining Filled Orders ID")
        start_time = datetime.now()
        filled_orders_to_be_processed_order_path_list = Processing_File_Helper.get_path_list_for_type_order_processing(
            get_type_string=get_type_string, status_string="filled")

        filled_orders_to_be_processed_exist = len(filled_orders_to_be_processed_order_path_list) > 0
        if filled_orders_to_be_processed_exist:
            filled_orders_to_be_processed_order_list = \
                OrderAdministratorGU.create_order_list_from_path_list(filled_orders_to_be_processed_order_path_list)
            filled_orders_to_be_processed_id = [order.order_id for order in filled_orders_to_be_processed_order_list]

            processing_logs_dic["processing_today_timeline"] = "started"
            processing_logs_dic["processing_baseline_timeline"] = "started"

            processing_logs_dic["filled_to_be_processed"] = "started"
            processing_logs_dic["processing_updated_active_orders"] = "started"
            processing_logs_dic["creating_info_active_orders"] = "started"
            FileIoHelper.write_processing_logs(processing_logs_dic)

        print(f"t: {(datetime.now() - start_time).total_seconds()}")

        print("Determining Cancelled Orders ID")
        start_time = datetime.now()
        cancelled_orders_to_be_processed_order_path_list = \
            Processing_File_Helper.get_path_list_for_type_order_processing(get_type_string=get_type_string,
                                                                           status_string="cancelled")

        cancelled_orders_to_be_processed_exist = len(cancelled_orders_to_be_processed_order_path_list) > 0
        if cancelled_orders_to_be_processed_exist:
            cancelled_orders_to_be_processed_order_list = OrderAdministratorGU.create_order_list_from_path_list(
                cancelled_orders_to_be_processed_order_path_list)
            cancelled_orders_to_be_processed_id = [order.order_id for order in cancelled_orders_to_be_processed_order_list]

            processing_logs_dic["cancelled_to_be_processed"] = "started"
            processing_logs_dic["processing_updated_active_orders"] = "started"
            processing_logs_dic["creating_info_active_orders"] = "started"
            FileIoHelper.write_processing_logs(processing_logs_dic)

        print(f"t: {(datetime.now() - start_time).total_seconds()}")

        print("Determining Inactive Orders ID")
        start_time = datetime.now()
        inactive_orders_to_be_processed_order_path_list =\
            Processing_File_Helper.get_path_list_for_type_order_processing(get_type_string=get_type_string,
                                                                           status_string="inactive")
        inactive_orders_to_be_processed_exist = len(inactive_orders_to_be_processed_order_path_list) > 0

        if inactive_orders_to_be_processed_exist:
            inactive_orders_to_be_processed_order_list = OrderAdministratorGU.create_order_list_from_path_list(
                inactive_orders_to_be_processed_order_path_list)
            inactive_orders_to_be_processed_id = [order.order_id for order in inactive_orders_to_be_processed_order_list]

            processing_logs_dic["inactive_to_be_processed"] = "started"
            processing_logs_dic["processing_updated_active_orders"] = "started"
            processing_logs_dic["creating_info_active_orders"] = "started"
            FileIoHelper.write_processing_logs(processing_logs_dic)

        print(f"t: {(datetime.now() - start_time).total_seconds()}")

        print("Determining Expired Orders ID")
        start_time = datetime.now()
        expired_orders_to_be_processed_order_path_list = \
            Processing_File_Helper.get_path_list_for_type_order_processing(get_type_string=get_type_string,
                                                                           status_string="expired")
        expired_orders_to_be_processed_exist = len(expired_orders_to_be_processed_order_path_list) > 0

        if expired_orders_to_be_processed_exist:
            expired_orders_to_be_processed_order_list = OrderAdministratorGU.create_order_list_from_path_list(
                expired_orders_to_be_processed_order_path_list)
            expired_orders_to_be_processed_id = [order.order_id for order in expired_orders_to_be_processed_order_list]

            processing_logs_dic["expired_to_be_processed"] = "started"
            processing_logs_dic["processing_updated_active_orders"] = "started"
            processing_logs_dic["creating_info_active_orders"] = "started"
            FileIoHelper.write_processing_logs(processing_logs_dic)

        print(f"t: {(datetime.now() - start_time).total_seconds()}")


        # card_win_rate_to_be_processed_file_path = File_Handler.get_base_path("card_win_rate_to_be_processed")
        # card_win_rate_to_be_processed_exist = os.path.isfile(card_win_rate_to_be_processed_file_path)
        # if card_win_rate_to_be_processed_exist:
        #     print("Creating To-Be-Processed Win Rate List")
        #     start_time = datetime.now()
        #     processing_logs_dic["card_win_rate_to_be_processed"] = "started"
        #     File_IO_Helper.write_processing_logs(processing_logs_dic)
        #     win_rate_to_be_processed_list = WinRateAdministrator.create_win_rate_to_be_processed_list()
        #     print(f"t: {(datetime.now() - start_time).total_seconds()}")

        if active_orders_to_be_processed_exist or cancelled_orders_to_be_processed_exist \
                or filled_orders_to_be_processed_exist \
                or inactive_orders_to_be_processed_exist \
                or expired_orders_to_be_processed_exist:

            if active_orders_to_be_processed_exist:
                print("Adding new Active Orders")
                start_time = datetime.now()
                active_updated_orders_df = pd.concat([active_updated_orders_df, additional_active_orders_df])

                print(f"t: {(datetime.now() - start_time).total_seconds()}")

            print("Determining IDs to be filtered")
            start_time = datetime.now()
            combined_id_list = []
            if cancelled_orders_to_be_processed_exist:
                combined_id_list.extend(cancelled_orders_to_be_processed_id)

            if filled_orders_to_be_processed_exist:
                combined_id_list.extend(filled_orders_to_be_processed_id)

            if inactive_orders_to_be_processed_exist:
                combined_id_list.extend(inactive_orders_to_be_processed_id)

            if expired_orders_to_be_processed_exist:
                combined_id_list.extend(expired_orders_to_be_processed_id)

            print(f"t: {(datetime.now() - start_time).total_seconds()}")

            print("Filtering Out Unwanted IDs")
            start_time = datetime.now()
            active_updated_orders_df = active_updated_orders_df[~active_updated_orders_df["order_id"]
            .isin(combined_id_list)]

            print(f"t: {(datetime.now() - start_time).total_seconds()}")


            print("Filtering Out Duplicate Active Orders")
            start_time = datetime.now()
            active_updated_orders_df.sort_values(by=["token_id", "updated_timestamp"], ascending=False)
            active_updated_orders_df.drop_duplicates(subset=["token_id"], keep="first")

            print(f"t: {(datetime.now() - start_time).total_seconds()}")

            print("Writing Updated Orders DF to File")
            start_time = datetime.now()
            OrderAdministratorGU.write_updated_active_sell_order_df_to_file(active_updated_orders_df)

            now_timestamp_str = SafeDatetimeConverter.datetime_to_string(datetime.utcnow())
            FileIoHelper.write_updated_active_sell_orders_timestamp(now_timestamp_str)

            processing_logs_dic["processing_updated_active_orders"] = "finished"
            FileIoHelper.write_processing_logs(processing_logs_dic)

            print(f"t: {(datetime.now() - start_time).total_seconds()}")

        if filled_orders_to_be_processed_exist:

            print("Determining Covered Month - Year")
            start_time = datetime.now()
            year_month_list =\
                DataCreator.determine_year_month_orders_downloaded(filled_orders_to_be_processed_order_list)
            print(f"t: {(datetime.now() - start_time).total_seconds()}")

            print("Loading Previous Filled Order Timeline Dic")
            start_time = datetime.now()
            previous_filled_orders_dic = FileIoHelper.load_filled_order_timeline_dic(year_month_list)
            print(f"t: {(datetime.now() - start_time).total_seconds()}")

            print("Updating Base Line Filled Orders Timeline")
            start_time = datetime.now()
            new_filled_order_timeline_dic = \
                DataCreator.update_base_line_filled_order_timeline(filled_orders_to_be_processed_order_list,
                                                                   previous_filled_orders_dic)
            print(f"t: {(datetime.now() - start_time).total_seconds()}")

            print("Creating Filled Orders Timeline")
            start_time = datetime.now()
            DataCreator.create_filled_orders_sales_timeline(new_filled_order_timeline_dic)
            print(f"t: {(datetime.now() - start_time).total_seconds()}")

            print("Writing Filled Order Timeline Dic To File")
            start_time = datetime.now()
            FileIoHelper.writing_filled_order_timeline_path_to_file(new_filled_order_timeline_dic)

            processing_logs_dic["processing_baseline_timeline"] = "finished"
            FileIoHelper.write_processing_logs(processing_logs_dic)

            print(f"t: {(datetime.now() - start_time).total_seconds()}")


            print("Loading Today Filled Order Timeline Dic")
            start_time = datetime.now()
            today_filled_order_timeline_dic = FileIoHelper.load_today_filled_order_timeline_dic()
            print(f"t: {(datetime.now() - start_time).total_seconds()}")

            print("Updating Today Filled Orders Timeline")
            start_time = datetime.now()
            new_today_filled_order_timeline_dic =\
                DataCreator.update_today_filled_sales(filled_orders_to_be_processed_order_list,
                                                      today_filled_order_timeline_dic)
            print(f"t: {(datetime.now() - start_time).total_seconds()}")

            print("Creating Last 24 Hours Timeline")
            start_time = datetime.now()
            DataCreator.create_last_24_hours_filled_orders_sales_timeline(new_today_filled_order_timeline_dic)
            print(f"t: {(datetime.now() - start_time).total_seconds()}")

            print("Writing Today Filled Orders Timeline To File")
            start_time = datetime.now()
            FileIoHelper.writing_today_filled_order_timeline_dic_to_file(new_today_filled_order_timeline_dic)

            processing_logs_dic["processing_today_timeline"] = "finished"
            FileIoHelper.write_processing_logs(processing_logs_dic)

            print(f"t: {(datetime.now() - start_time).total_seconds()}")

        # if card_win_rate_to_be_processed_exist:
        #     print("Updating Card Win Rate")
        #     start_time = datetime.now()
        #
        #     DataCreator.update_win_rate_month_overview(win_rate_to_be_processed_list)
        #     DataCreator.create_win_rate_info()
        #
        #     print(f"t: {(datetime.now() - start_time).total_seconds()}")


        if active_orders_to_be_processed_exist or cancelled_orders_to_be_processed_exist \
                or filled_orders_to_be_processed_exist \
                or inactive_orders_to_be_processed_exist \
                or expired_orders_to_be_processed_exist:

            print("Creating Updated Orders Info")
            start_time = datetime.now()
            DataCreator.create_info_for_active_orders(active_updated_orders_df, "ETH", "GODS", 1)

            processing_logs_dic["creating_info_active_orders"] = "finished"
            FileIoHelper.write_processing_logs(processing_logs_dic)

            print(f"t: {(datetime.now() - start_time).total_seconds()}")

        if active_orders_to_be_processed_exist:
            for path in active_orders_to_be_processed_order_path_list:
                os.remove(path)
            processing_logs_dic["active_to_be_processed"] = "finished"
            FileIoHelper.write_processing_logs(processing_logs_dic)

        if filled_orders_to_be_processed_exist:
            for path in filled_orders_to_be_processed_order_path_list:
                os.remove(path)
            processing_logs_dic["filled_to_be_processed"] = "finished"
            FileIoHelper.write_processing_logs(processing_logs_dic)

        if cancelled_orders_to_be_processed_exist:
            for path in cancelled_orders_to_be_processed_order_path_list:
                os.remove(path)
            processing_logs_dic["cancelled_to_be_processed"] = "finished"
            FileIoHelper.write_processing_logs(processing_logs_dic)

        if inactive_orders_to_be_processed_exist:
            for path in inactive_orders_to_be_processed_order_path_list:
                os.remove(path)
            processing_logs_dic["inactive_to_be_processed"] = "finished"
            FileIoHelper.write_processing_logs(processing_logs_dic)

        if expired_orders_to_be_processed_exist:
            for path in expired_orders_to_be_processed_order_path_list:
                os.remove(path)
            processing_logs_dic["expired_to_be_processed"] = "finished"
            FileIoHelper.write_processing_logs(processing_logs_dic)

        # if card_win_rate_to_be_processed_exist:
        #     os.remove(card_win_rate_to_be_processed_file_path)
        #     processing_logs_dic["card_win_rate_to_be_processed"] = "finished"
        #     File_IO_Helper.write_processing_logs(processing_logs_dic)

        print(f"\nTotal t: {(datetime.now() - total_start_time).total_seconds()}\n")

        return active_updated_orders_df

    @staticmethod
    def create_info_for_active_orders(sell_order_df, currency_1_str, currency_2_str, number_same_cards):
        """
        A method to create a .csv file that is an overview over all available orders
        :param sell_order_df: the DataFrame containing information about all current sell orders
        :param currency_1_str: the currency to purchase the card in
        :param currency_2_str: the currency to sell the card in
        :param number_same_cards: how many offers of the same card to consider
        :return: None
        """

        storage_path = FileHandler.get_base_path("potential_purchases")

        last_24_hours_sales_path = FileHandler.get_base_path("last_24_hours_sales")
        last_7_days_sales_path = FileHandler.get_base_path("last_7_days_sales")
        last_30_days_sales_path = FileHandler.get_base_path("last_30_days_sales")

        last_24_hours_price_path = FileHandler.get_base_path("last_24_hours_price")
        last_7_days_price_path = FileHandler.get_base_path("last_7_days_price")
        last_30_days_price_path = FileHandler.get_base_path("last_30_days_price")

        last_24_hours_price_change_path = FileHandler.get_base_path("last_24_hours_price_change")
        last_7_days_price_change_path = FileHandler.get_base_path("last_7_days_price_change")
        last_30_days_price_change_path = FileHandler.get_base_path("last_30_days_price_change")

        last_30_days_total_win_rate_path = FileHandler.get_base_path("last_30_days_total_win_rate_file")
        last_30_days_mythic_win_rate_path = FileHandler.get_base_path("last_30_days_mythic_win_rate_file")
        last_4_weekend_rank_total_win_rate_path = FileHandler.get_base_path("last_4_weekend_rank_total_win_rate_file")
        last_4_weekend_rank_mythic_win_rate_path = FileHandler.get_base_path("last_4_weekend_rank_mythic_win_rate_file")

        bot_info_path = FileHandler.get_base_path("bot_info_dic")
        with open(bot_info_path, 'r', encoding='utf-8') as bot_info_file:
            bot_info_dic = json.load(bot_info_file)
        bot_info_file.close()

        quality_list = ["Gold", "Shadow", "Meteorite", "DIAMOND"]
        currency_combination_list = [(currency_1_str, currency_2_str), (currency_2_str, currency_1_str)]

        for currency_combination in currency_combination_list:
            currency_1 = currency_combination[0]
            currency_2 = currency_combination[1]

            currency_1_name = str(currency_1)
            currency_1_token_id = currency_1_name + "_token_id"
            currency_1_order_id = currency_1_name + "_order_id"
            currency_1_cheapest = "cheapest_" + currency_1_name
            currency_1_cheapest_euro = "cheapest_" + currency_1_name + "_euro"

            currency_2_name = str(currency_2)
            currency_2_token_id = currency_2_name + "_token_id"
            currency_2_order_id = currency_2_name + "_order_id"
            currency_2_cheapest = "cheapest_" + currency_2_name
            currency_2_cheapest_euro = "cheapest_" + currency_2_name + "_euro"

            last_24_hours_sales = currency_2_name + "_24h_n"
            last_7_days_sales = currency_2_name + "_7d_n"
            last_7_days_at_least_one_sale = currency_2_name + "7d_min_1n"
            last_30_days_sales = currency_2_name + "_30d_n"
            last_30_days_at_least_one_sale = currency_2_name + "_30d_min_1n"

            last_24_hours_price = currency_2_name + "_24h_p"
            last_7_days_price = currency_2_name + "_7d_p"
            last_30_days_price = currency_2_name + "_30d_p"

            last_24_hours_price_change = currency_2_name + "_24h_p%"
            last_7_days_price_change = currency_2_name + "_7d_p%"
            last_30_days_price_change = currency_2_name + "_30d_p%"

            currency_1_card_quality_list = []

            for card_quality in quality_list:
                one_card_quality_df = sell_order_df[sell_order_df["card_quality"] == card_quality]

                currency_1_df = one_card_quality_df[one_card_quality_df["currency"] == currency_1_name]
                index_min_currency_1_list = currency_1_df.groupby("card_name")["price_euro"].\
                    nsmallest(number_same_cards).index.to_list()
                index_min_currency_1_list = [entry[1] for entry in index_min_currency_1_list]

                min_currency_1_df = currency_1_df[currency_1_df.index.isin(index_min_currency_1_list)]
                min_currency_1_df = min_currency_1_df[["card_name", "price_euro", "price_crypto",
                                                       "token_id", "order_id"]]
                min_currency_1_df = min_currency_1_df.rename(columns={"price_euro": currency_1_cheapest_euro,
                                                                      "price_crypto" : currency_1_cheapest,
                                                                      "token_id": currency_1_token_id,
                                                                      "order_id": currency_1_order_id})

                min_currency_1_df = min_currency_1_df.set_index("card_name")

                currency_2_df = one_card_quality_df[one_card_quality_df["currency"] == currency_2_name]
                index_currency_2_list = currency_2_df.groupby("card_name")["price_euro"].nsmallest(1).index.to_list()
                index_currency_2_list = [entry[1] for entry in index_currency_2_list]
                min_currency_2_df = currency_2_df[currency_2_df.index.isin(index_currency_2_list)]

                min_currency_2_df = min_currency_2_df[["card_name", "price_euro", "price_crypto",
                                                       "token_id", "order_id"]]
                min_currency_2_df = min_currency_2_df.rename(columns={"price_euro": currency_2_cheapest_euro,
                                                                      "price_crypto" : currency_2_cheapest,
                                                                      "token_id": currency_2_token_id,
                                                                      "order_id" : currency_2_order_id})
                min_currency_2_df = min_currency_2_df.set_index("card_name")

                bot_df = currency_2_df.groupby("card_name")["user"]\
                    .apply(lambda x: PandaHelper.filtering_bot_user_series(x, bot_info_dic)).to_frame()
                bot_df["bots"] = bot_df["user"].str.split(pat="to").str[0]
                bot_df["offers"] = bot_df["user"].str.split(pat="to").str[1]
                bot_df = bot_df.drop(columns=["user"])

                combined_df_currency = min_currency_1_df.join(min_currency_2_df)
                combined_df_currency_1 = combined_df_currency.join(bot_df).reset_index()

                combined_df_currency_1["t_dif"] = combined_df_currency_1[currency_2_cheapest_euro] - \
                                                  combined_df_currency_1[currency_1_cheapest_euro]
                combined_df_currency_1["rel_dif"] = (combined_df_currency_1["t_dif"] /
                                                     combined_df_currency_1[currency_1_cheapest_euro]) * 100
                combined_df_currency_1["quality"] = card_quality

                combined_df_currency_1 = \
                    combined_df_currency_1.dropna(subset=[currency_2_cheapest_euro, currency_1_cheapest_euro])
                combined_df_currency_1["card_name"] = combined_df_currency_1["card_name"]\
                    .replace({"Oddi, Valka’s Herald" : "Oddi, Valka's Herald"})

                currency_specific_24_hours_sales_path = str(last_24_hours_sales_path) + "\last_24_hours_sales_"\
                                                        + currency_2_name + "_" + card_quality + ".json"

                with open(currency_specific_24_hours_sales_path, 'r', encoding='utf-8') \
                        as currency_specific_24_hours_sales_file:

                    last_24_hours_sale_dic = json.load(currency_specific_24_hours_sales_file)
                currency_specific_24_hours_sales_file.close()

                currency_specific_7_days_sales_path = str(last_7_days_sales_path) + "\last_7_days_sales_" \
                                                      + currency_2_name + "_" + card_quality + ".json"

                with open(currency_specific_7_days_sales_path, 'r', encoding='utf-8')\
                        as currency_specific_7_days_sales_file:

                    last_7_days_sale_dic = json.load(currency_specific_7_days_sales_file)
                currency_specific_7_days_sales_file.close()

                currency_specific_30_days_sales_path = str(last_30_days_sales_path) + "\last_30_days_sales_"\
                                                       + currency_2_name + "_" + card_quality + ".json"

                with open(currency_specific_30_days_sales_path, 'r', encoding='utf-8')\
                        as currency_specific_30_days_sales_file:
                    last_30_days_sale_dic = json.load(currency_specific_30_days_sales_file)
                currency_specific_30_days_sales_file.close()


                currency_specific_24_hours_price_path = str(last_24_hours_price_path) + "\last_24_hours_price_"\
                                                        + currency_2_name + "_" + card_quality + ".json"

                with open(currency_specific_24_hours_price_path, 'r', encoding='utf-8') as currency_specific_24_hours_price_file:
                    last_24_hours_price_dic = json.load(currency_specific_24_hours_price_file)
                currency_specific_24_hours_price_file.close()

                currency_specific_7_days_price_path = str(last_7_days_price_path) + "\last_7_days_price_"\
                                                      + currency_2_name + "_" + card_quality + ".json"

                with open(currency_specific_7_days_price_path, 'r', encoding='utf-8')\
                        as currency_specific_7_days_price_file:
                    last_7_days_price_dic = json.load(currency_specific_7_days_price_file)
                currency_specific_7_days_price_file.close()

                currency_specific_30_days_price_path = str(last_30_days_price_path) + "\last_30_days_price_"\
                                                       + currency_2_name + "_" + card_quality + ".json"

                with open(currency_specific_30_days_price_path, 'r', encoding='utf-8')\
                        as currency_specific_30_days_price_file:
                    last_30_days_price_dic = json.load(currency_specific_30_days_price_file)
                currency_specific_30_days_price_file.close()


                currency_specific_24_hours_price_change_path = str(last_24_hours_price_change_path)\
                                                               + "\last_24_hours_price_change_" + currency_2_name\
                                                               + "_" + card_quality + ".json"

                with open(currency_specific_24_hours_price_change_path, 'r', encoding='utf-8') as currency_specific_24_hours_price_change_file:
                    last_24_hours_price_change_dic = json.load(currency_specific_24_hours_price_change_file)
                currency_specific_24_hours_price_change_file.close()

                currency_specific_7_days_price_change_path = str(last_7_days_price_change_path) + "\last_7_days_price_change_" + currency_2_name + "_" + card_quality + ".json"
                with open(currency_specific_7_days_price_change_path, 'r', encoding='utf-8') as currency_specific_7_days_price_change_file:
                    last_7_days_price_change_dic = json.load(currency_specific_7_days_price_change_file)
                currency_specific_7_days_price_change_file.close()

                currency_specific_30_days_price_change_path = str(last_30_days_price_change_path) + "\last_30_days_price_change_" + currency_2_name + "_" + card_quality + ".json"
                with open(currency_specific_30_days_price_change_path, 'r', encoding='utf-8') as currency_specific_30_days_price_change_file:
                    last_30_days_price_change_dic = json.load(currency_specific_30_days_price_change_file)
                currency_specific_30_days_price_change_file.close()


                combined_df_currency_1[last_24_hours_sales] = np.vectorize(lambda x: last_24_hours_sale_dic[x], otypes=[np.float64])(combined_df_currency_1["card_name"])

                combined_df_currency_1[last_7_days_sales] = combined_df_currency_1["card_name"].apply(lambda x: last_7_days_sale_dic[x])
                combined_df_currency_1[last_7_days_at_least_one_sale] = combined_df_currency_1[last_7_days_sales].apply(lambda x: PandaHelper.days_in_last_x_with_at_least_y_sales(x, 8, 1))
                combined_df_currency_1[last_7_days_sales] = combined_df_currency_1[last_7_days_sales].apply(lambda x: PandaHelper.total_sales_in_the_past(x))

                combined_df_currency_1[last_30_days_sales] = combined_df_currency_1["card_name"].apply(lambda x: last_30_days_sale_dic[x])
                combined_df_currency_1[last_30_days_at_least_one_sale] = combined_df_currency_1[last_30_days_sales].apply(lambda x: PandaHelper.days_in_last_x_with_at_least_y_sales(x, 31, 1))
                combined_df_currency_1[last_30_days_sales] = combined_df_currency_1[last_30_days_sales].apply(lambda x: PandaHelper.total_sales_in_the_past(x))


                combined_df_currency_1[last_24_hours_price] = combined_df_currency_1["card_name"].apply(lambda x: last_24_hours_price_dic[x])

                combined_df_currency_1["24h_t_dif"] = combined_df_currency_1[last_24_hours_price] - combined_df_currency_1[currency_1_cheapest_euro]
                combined_df_currency_1["24h_rel_dif"] = (combined_df_currency_1["24h_t_dif"] / combined_df_currency_1[currency_1_cheapest_euro]) * 100


                combined_df_currency_1[last_7_days_price] = combined_df_currency_1["card_name"].apply(lambda x: last_7_days_price_dic[x])

                combined_df_currency_1["7d_t_dif"] = combined_df_currency_1[last_7_days_price] - combined_df_currency_1[currency_1_cheapest_euro]
                combined_df_currency_1["7d_rel_dif"] = (combined_df_currency_1["7d_t_dif"] / combined_df_currency_1[currency_1_cheapest_euro]) * 100


                combined_df_currency_1[last_30_days_price] = combined_df_currency_1["card_name"].apply(lambda x: last_30_days_price_dic[x])

                combined_df_currency_1["30d_t_dif"] = combined_df_currency_1[last_30_days_price] - combined_df_currency_1[currency_1_cheapest_euro]
                combined_df_currency_1["30_rel_dif"] = (combined_df_currency_1["30d_t_dif"] / combined_df_currency_1[currency_1_cheapest_euro]) * 100


                combined_df_currency_1[last_24_hours_price_change] = combined_df_currency_1["card_name"].apply(lambda x: last_24_hours_price_change_dic[x])

                combined_df_currency_1[last_7_days_price_change] = combined_df_currency_1["card_name"].apply(lambda x: last_7_days_price_change_dic[x])

                combined_df_currency_1[last_30_days_price_change] = combined_df_currency_1["card_name"].apply(lambda x: last_30_days_price_change_dic[x])


                with open(last_30_days_total_win_rate_path, 'r', encoding='utf-8') as last_30_days_total_win_rate_file:
                    last_30_days_total_win_rate_dic = json.load(last_30_days_total_win_rate_file)
                last_30_days_total_win_rate_file.close()

                with open(last_30_days_mythic_win_rate_path, 'r', encoding='utf-8') as last_30_days_mythic_win_rate_file:
                    last_30_days_mythic_win_rate_dic = json.load(last_30_days_mythic_win_rate_file)
                last_30_days_mythic_win_rate_file.close()

                with open(last_4_weekend_rank_total_win_rate_path, 'r', encoding='utf-8') as last_4_weekend_rank_total_win_rate_file:
                    last_4_weekend_rank_total_win_rate_dic = json.load(last_4_weekend_rank_total_win_rate_file)
                last_4_weekend_rank_total_win_rate_file.close()

                with open(last_4_weekend_rank_mythic_win_rate_path, 'r', encoding='utf-8') as last_4_weekend_rank_mythic_win_rate_file:
                    last_4_weekend_rank_mythic_win_rate_dic = json.load(last_4_weekend_rank_mythic_win_rate_file)
                last_4_weekend_rank_mythic_win_rate_file.close()


                combined_df_currency_1["win_30_d"] = combined_df_currency_1["card_name"].apply(lambda x: last_30_days_total_win_rate_dic[x])

                combined_df_currency_1["win_m_30_d"] = combined_df_currency_1["card_name"].apply(lambda x: last_30_days_mythic_win_rate_dic[x])

                combined_df_currency_1["win_4_w"] = combined_df_currency_1["card_name"].apply(lambda x: last_4_weekend_rank_total_win_rate_dic[x])

                combined_df_currency_1["win_m_4_w"] = combined_df_currency_1["card_name"].apply(lambda x: last_4_weekend_rank_mythic_win_rate_dic[x])

                currency_1_card_quality_list.append(combined_df_currency_1)


            currency_1_to_2_df = pd.concat(currency_1_card_quality_list)

            path_file_1 = str(storage_path) + '\\' + str(currency_1) + "_TO_" + str(currency_2) + ".csv"
            currency_1_to_2_df.to_csv(path_file_1, index=False)

    @staticmethod
    def create_list_of_bot_accounts():
        """
        A method to create a list of account names that potentially could be bots based on outlier analysis
        :return: None
        """

        json_files = FileHandler.get_all_paths_of_type_of_orders("SELL", "CANCELLED", "ROLLING")
        amount_files_to_read = len(json_files)

        bot_account_dic = {}

        for index, path in enumerate(json_files):
            print(f"Reading {index + 1} / {amount_files_to_read}")
            with open(path, 'r', encoding='utf-8') as orders_in_string_file:
                for line_index, line in enumerate(orders_in_string_file):
                    try:
                        line_json = json.loads(json.loads(line))
                        temp_order = OrderFactoryGU.string_to_object(line_json)
                    except Exception as e1:
                        try:
                            line_json = json.loads(line)
                            temp_order = OrderFactoryGU.string_to_object(line_json)
                        except Exception as e2:
                            print(f"Line Index: {line_index}")
                            print(line)
                    finally:
                        if temp_order.user in bot_account_dic:
                            user_dic = bot_account_dic[temp_order.user]
                        else:
                            user_dic = {}

                        if temp_order.token_id in user_dic:
                            new_entry = user_dic[temp_order.token_id]
                            new_entry.append(temp_order.updated_timestamp)
                            user_dic[temp_order.token_id] = new_entry
                        else:
                            new_entry = [temp_order.updated_timestamp]
                            user_dic[temp_order.token_id] = new_entry

                        bot_account_dic[temp_order.user] = user_dic

        updated_info_dic = {}
        for user_name, cancellation_info in bot_account_dic.items():

            amount_cancellation_lists = []
            average_time_difference_list = []
            total_amount_cancellation = 0

            for token_id, cancellation_dates in cancellation_info.items():
                amount_cancellations = len(cancellation_dates)
                amount_cancellation_lists.append(amount_cancellations)
                total_amount_cancellation = total_amount_cancellation + len(cancellation_dates)

                timestamp_list = [ts for ts in cancellation_dates]
                timestamp_list.sort(reverse=False)
                time_difference_list = []

                for index in range(1, len(timestamp_list)):
                    time_difference = (timestamp_list[index] - timestamp_list[index - 1]).total_seconds()
                    time_difference_list.append(time_difference)

                if len(time_difference_list) > 0:
                    average_time_difference = statistics.mean(time_difference_list)
                    average_time_difference_list.append(average_time_difference)

            average_cancellation_amount_final = statistics.mean(amount_cancellation_lists)

            if len(average_time_difference_list) > 0:
                average_time_difference_final = statistics.mean(average_time_difference_list)
            else:
                average_time_difference_final = None
            updated_info_dic[user_name] = (total_amount_cancellation, average_cancellation_amount_final, average_time_difference_final)

        user_info_dic = {k: v for k, v in updated_info_dic.items() if (v[0] != None) and (v[1] != None) and (v[2] != None) and (v[2] != 0)}

        user_info_path = FileHandler.get_base_path("user_info_dic")
        with open(user_info_path, 'w', encoding='utf-8') as user_info_file:
            json.dump(user_info_dic, user_info_file, ensure_ascii=False, indent=4)
        user_info_file.close()

        total_amount_cancellation_list = [value[0] for (key, value) in user_info_dic.items()]
        average_cancellation_list = [value[1] for (key, value) in user_info_dic.items()]
        average_time_difference_list = [value[2] for (key, value) in user_info_dic.items()]

        Q1 = np.percentile(total_amount_cancellation_list, 25, method='midpoint')
        Q3 = np.percentile(total_amount_cancellation_list, 75, method='midpoint')
        IQR = Q3 - Q1
        upper_bound_total_cancellation = Q3 + 1.5 * IQR

        Q1 = np.percentile(average_cancellation_list, 25, method='midpoint')
        Q3 = np.percentile(average_cancellation_list, 75, method='midpoint')
        IQR = Q3 - Q1
        upper_bound_average_cancellation = Q3 + 1.5 * IQR

        bot_info_dic = {k: v for k, v in user_info_dic.items() if (v[0] >= upper_bound_total_cancellation) and (v[1] >= upper_bound_average_cancellation)}

        bot_info_path = FileHandler.get_base_path("bot_info_dic")
        with open(bot_info_path, 'w', encoding='utf-8') as bot_info_file:
            json.dump(bot_info_dic, bot_info_file, ensure_ascii=False, indent=4)
        bot_info_file.close()

        bot_info_avg_time_difference = statistics.mean([v[2] for k, v in bot_info_dic.items()])
        overall_avg_time_difference = statistics.mean(average_time_difference_list)
        print(f"Overall Average Time Difference {overall_avg_time_difference}")
        print(f"Bots Average Time Difference {bot_info_avg_time_difference}")

        total_amount_sellers = len(user_info_dic)
        amount_bots = len(bot_info_dic)
        print(f"Total Amounts Sellers {total_amount_sellers}")
        print(f"Amount Bots {amount_bots}")
        print(f"Bot Percentage {amount_bots / total_amount_sellers}")

    @staticmethod
    def update_today_filled_sales(order_list, today_filled_order_timeline_dic):
        """
        A method to update the timeline of all cards sold today
        :param order_list: the list of orders of newly sold cards
        :param today_filled_order_timeline_dic: the current sale timeline
        :return: the updated current sale timeline
        """

        current_time_local = datetime.now()
        current_time_utc = current_time_local.astimezone(pytz.utc)
        twentyfour_hours_ago_timestamp = current_time_utc - timedelta(days=1)
        twentyfour_hours_ago_timestamp = twentyfour_hours_ago_timestamp.replace(tzinfo=None)

        temp_today_timeline_dic = {}
        for key, value in today_filled_order_timeline_dic.items():
            key_as_timestamp = datetime.strptime(key, "%Y-%m-%dT%H:%M:%S")

            if key_as_timestamp > twentyfour_hours_ago_timestamp:
                temp_today_timeline_dic[key] = value

        today_filled_order_timeline_dic = temp_today_timeline_dic

        for order in order_list:
            card_str = order.card_name

            updated_timestamp_str = SafeDatetimeConverter.datetime_to_string(order.updated_timestamp)
            updated_timestamp_without_microseconds_str = updated_timestamp_str.split('.')[0]

            if order.updated_timestamp > twentyfour_hours_ago_timestamp:

                if updated_timestamp_without_microseconds_str in today_filled_order_timeline_dic:
                    date_entry = today_filled_order_timeline_dic[updated_timestamp_without_microseconds_str]
                else:
                    date_entry = {}

                if card_str in date_entry:
                    card_entry = date_entry[card_str]
                else:
                    card_entry = {}

                new_info_entry = {"token_id": order.token_id,
                              "quantity": order.quantity, "decimals": order.decimals,
                              "currency": order.currency, "price_euro_at_updated_timestamp_day": order.price_euro_at_updated_timestamp_day,
                              "card_quality": order.card_quality}

                if str(order.order_id) not in date_entry:
                    card_entry[order.order_id] = new_info_entry

                date_entry[card_str] = card_entry
                today_filled_order_timeline_dic[updated_timestamp_without_microseconds_str] = date_entry

        return today_filled_order_timeline_dic

    @staticmethod
    def update_base_line_filled_order_timeline(order_list, previous_filled_orders_dic):
        """
        A method to update the overall sale timeline based on newly sold orders
        :param order_list: the newly sold orders
        :param previous_filled_orders_dic: the previous overall sale timeline
        :return: the updated overall sale timeline
        """

        for order in order_list:

            year_month_str = str(order.updated_timestamp.year) + "-" + str(order.updated_timestamp.month)

            filled_order_timeline_dic = previous_filled_orders_dic[year_month_str]

            card_str = order.card_name

            if card_str in filled_order_timeline_dic:
                entry_name = filled_order_timeline_dic[card_str]
            else:
                entry_name = {}

            timestamp_str = SafeDatetimeConverter.datetime_to_string(order.updated_timestamp)
            date_str = timestamp_str.split("T")[0]

            if date_str in entry_name:
                date_entry = entry_name[date_str]
            else:
                date_entry = {}


            new_info_entry = {"token_id": order.token_id,
                              "quantity": order.quantity, "decimals": order.decimals,
                              "currency": order.currency, "price_euro_at_updated_timestamp_day": order.price_euro_at_updated_timestamp_day,
                              "card_quality": order.card_quality}

            if str(order.order_id) not in date_entry:
                date_entry[order.order_id] = new_info_entry

            entry_name[date_str] = date_entry
            filled_order_timeline_dic[card_str] = entry_name

            previous_filled_orders_dic[year_month_str] = filled_order_timeline_dic

        return previous_filled_orders_dic

    @staticmethod
    def determine_year_month_orders_downloaded(order_list):
        """
        A method to determine in which years and months the orders were created
        :param order_list: a list of orders
        :return: a list of all years and months in which the orders were created
        """

        year_month_dic = {}

        for order in order_list:
            year_month_str = str(order.updated_timestamp.year) + "-" + str(order.updated_timestamp.month)
            year_month_dic[year_month_str] = True

        year_month_list = [key for key in year_month_dic.keys()]

        return year_month_list

    @staticmethod
    def update_win_rate_month_overview(win_rate_list):
        """
        A method to update the monthly win rate overview
        :param win_rate_list: a list of new win rate information
        :return: None
        """

        gods_unchained_updated_assets_dic = GodsUnchainedScrapper.get_all_gods_unchained_assets()

        collectable_assets_dic = {key.replace("\u2019", "'"): value["id"] for (key, value) in gods_unchained_updated_assets_dic.items() if value["collectable"] == True}

        id_to_name_dic = {value: key for key, value in collectable_assets_dic.items()}

        user_ranking_dic = FileIoHelper.load_user_rank_dic()

        #for user_name, ranking_dic in file_user_ranking_dic.items():

        last_friday = DataCreator.determine_last_friday()
        new_win_rate_list = []
        year_month_to_load_dic = {}

        for WinRateEntry in win_rate_list:
            user_str = str(WinRateEntry.user_id)

            if last_friday in user_ranking_dic[user_str]:
                user_rank = user_ranking_dic[user_str][last_friday]
            else:
                user_rank = user_ranking_dic[user_str]["new"]

            WinRateEntry.user_rank = user_rank
            new_win_rate_list.append(WinRateEntry)

            year_month = "-".join(WinRateEntry.day_finished.split("-")[0:2])
            year_month_to_load_dic[year_month] = True

        year_month_dic = {}
        months_overview_folder_path = FileHandler.get_base_path("months_overview_folder")
        for year_month in year_month_to_load_dic.keys():
            path_to_current_month_overview = str(months_overview_folder_path) + "\\" + "winrate_" + year_month + ".json"

            if os.path.isfile(path_to_current_month_overview):
                with open(path_to_current_month_overview, 'r', encoding='utf-8') as file_to_current_month_overview:
                    win_rate_dic = json.load(file_to_current_month_overview)
                file_to_current_month_overview.close()

                for key in collectable_assets_dic.keys():
                    if key not in win_rate_dic:
                        win_rate_dic[key] = {}

            else:
                win_rate_dic = {key: {} for key, value in collectable_assets_dic.items()}

            year_month_dic[year_month] = win_rate_dic

        for WinRateEntry in new_win_rate_list:
            for card_id in WinRateEntry.card_list:
                name = id_to_name_dic[card_id]

                year_month = "-".join(WinRateEntry.day_finished.split("-")[0:2])
                win_rate_dic = year_month_dic[year_month]
                WinRateEntry_dic = win_rate_dic[name]

                if WinRateEntry.day_finished in WinRateEntry_dic:
                    day_entry = WinRateEntry_dic[WinRateEntry.day_finished]
                else:
                    day_entry = {}
                    day_entry["wins_overall"] = 0
                    day_entry["losses_overall"] = 0
                    day_entry["wins_mythic"] = 0
                    day_entry["losses_mythic"] = 0

                    day_entry["unique_wins_overall"] = 0
                    day_entry["unique_losses_overall"] = 0
                    day_entry["unique_wins_mythic"] = 0
                    day_entry["unique_losses_mythic"] = 0

                if WinRateEntry.status == "winner":
                    prev_wins_overall = day_entry["wins_overall"]
                    day_entry["wins_overall"] = prev_wins_overall + 1
                    if WinRateEntry.user_rank == 12:
                        prev_wins_mythic = day_entry["wins_mythic"]
                        day_entry["wins_mythic"] = prev_wins_mythic + 1

                elif WinRateEntry.status == "loser":
                    prev_losses_overall = day_entry["losses_overall"]
                    day_entry["losses_overall"] = prev_losses_overall + 1
                    if WinRateEntry.user_rank == 12:
                        prev_losses_mythic = day_entry["losses_mythic"]
                        day_entry["losses_mythic"] = prev_losses_mythic + 1

                WinRateEntry_dic[WinRateEntry.day_finished] = day_entry
                win_rate_dic[name] = WinRateEntry_dic
                year_month_dic[year_month] = win_rate_dic

            unique_card_dic = {card_id: True for card_id in WinRateEntry.card_list}
            unique_card_list = [key for key in unique_card_dic.keys()]

            for unique_card_id in unique_card_list:
                name = id_to_name_dic[unique_card_id]

                year_month = "-".join(WinRateEntry.day_finished.split("-")[0:2])
                win_rate_dic = year_month_dic[year_month]
                WinRateEntry_dic = win_rate_dic[name]

                day_entry = WinRateEntry_dic[WinRateEntry.day_finished]

                if WinRateEntry.status == "winner":
                    prev_wins_overall = day_entry["unique_wins_overall"]
                    day_entry["unique_wins_overall"] = prev_wins_overall + 1
                    if WinRateEntry.user_rank == 12:
                        prev_wins_mythic = day_entry["unique_wins_mythic"]
                        day_entry["unique_wins_mythic"] = prev_wins_mythic + 1

                elif WinRateEntry.status == "loser":
                    prev_losses_overall = day_entry["unique_losses_overall"]
                    day_entry["unique_losses_overall"] = prev_losses_overall + 1
                    if WinRateEntry.user_rank == 12:
                        prev_losses_mythic = day_entry["unique_losses_mythic"]
                        day_entry["unique_losses_mythic"] = prev_losses_mythic + 1

                WinRateEntry_dic[WinRateEntry.day_finished] = day_entry
                win_rate_dic[name] = WinRateEntry_dic
                year_month_dic[year_month] = win_rate_dic

        for year_month, win_rate_dic in year_month_dic.items():
            path_to_current_month_overview = str(months_overview_folder_path) + "\\" + "winrate_" + year_month + ".json"
            with open(path_to_current_month_overview, 'w', encoding='utf-8') as file_to_current_month_overview:
                json.dump(win_rate_dic, file_to_current_month_overview, ensure_ascii=False, indent=4)
            file_to_current_month_overview.close()

    @staticmethod
    def determine_last_friday():
        """
        A method to determine the date of the last friday
        :return: the date of the last friday
        """
        current_time_local = datetime.now()
        current_time_utc = current_time_local.astimezone(pytz.utc)
        current_weekday = current_time_utc.weekday()

        if current_weekday == 4:
            last_friday = current_time_utc.isoformat().split('T')[0]
        else:
            friday_not_found = True

            while friday_not_found:
                new_day = current_time_utc - timedelta(days=1)
                new_weekday = new_day.weekday()

                if new_weekday == 4:
                    last_friday = new_day.isoformat().split('T')[0]
                    friday_not_found = False
                else:
                    current_time_utc = new_day

        return last_friday

    @staticmethod
    def create_win_rate_info():
        """
        A method to create an overview over the win rate of each card
        :return: None
        """

        current_time_local = datetime.now()
        today_utc = current_time_local.astimezone(pytz.utc)

        gods_unchained_updated_assets_dic = GodsUnchainedScrapper.get_all_gods_unchained_assets()
        collectable_assets_dic = {key.replace("\u2019", "'"): 0 for (key, value) in gods_unchained_updated_assets_dic.items() if value["collectable"] == True}

        total_win_rate_dic = copy.deepcopy(collectable_assets_dic)
        mythic_win_rate_dic = copy.deepcopy(collectable_assets_dic)

        asset_name_list = [key for key in collectable_assets_dic.keys()]

        months_overview_folder_path = FileHandler.get_base_path("months_overview_folder")

        iteration_information_list = []

        year_month_last_30_days_dic = {}
        days_in_last_30_days = []
        for day in range(1, 31):
            new_day_time_stamp = today_utc - timedelta(days=day)
            new_day_str = new_day_time_stamp.isoformat().split('T')[0]
            days_in_last_30_days.append(new_day_str)

            year_month = "-".join(new_day_str.split("-")[0:2])
            year_month_last_30_days_dic[year_month] = True
        year_month_30_days_list = [key for key in year_month_last_30_days_dic.keys()]

        overall_months_overview_30_days_dic = {}
        for year_month in year_month_30_days_list:
            month_overview_path = str(months_overview_folder_path) + "\\winrate_" + str(year_month) + ".json"

            with open(month_overview_path, 'r', encoding='utf-8') as month_overview_file:
                temp_dic = json.load(month_overview_file)
            month_overview_file.close()

            for asset_name in asset_name_list:
                if asset_name not in temp_dic:
                    temp_dic[asset_name] = {}

            overall_months_overview_30_days_dic[year_month] = temp_dic

        total_win_last_30_rate_path = FileHandler.get_base_path("last_30_days_total_win_rate_file")
        mythic_win_rate_last_30_path = FileHandler.get_base_path("last_30_days_mythic_win_rate_file")

        iteration_information_list.append((overall_months_overview_30_days_dic, days_in_last_30_days, total_win_last_30_rate_path, mythic_win_rate_last_30_path))

        year_month_4_weekend_dic = {}
        days_in_last_4_weekend_rank = DataCreator.determine_days_in_last_4_weekend_rank()
        for day in days_in_last_4_weekend_rank:
            year_month = "-".join(day.split("-")[0:2])
            year_month_4_weekend_dic[year_month] = True
        year_month_4_weekend_list = [key for key in year_month_4_weekend_dic.keys()]

        overall_months_overview_4_weekend_dic = {}
        for year_month in year_month_4_weekend_list:
            month_overview_path = str(months_overview_folder_path) + "\\winrate_" + str(year_month) + ".json"

            with open(month_overview_path, 'r', encoding='utf-8') as month_overview_file:
                temp_dic = json.load(month_overview_file)
            month_overview_file.close()

            for asset_name in asset_name_list:
                if asset_name not in temp_dic:
                    temp_dic[asset_name] = {}

            overall_months_overview_4_weekend_dic[year_month] = temp_dic

        total_win_rate_4_weekend_path = FileHandler.get_base_path("last_4_weekend_rank_total_win_rate_file")
        mythic_win_rate_4_weekend_path = FileHandler.get_base_path("last_4_weekend_rank_mythic_win_rate_file")

        iteration_information_list.append((overall_months_overview_4_weekend_dic, days_in_last_4_weekend_rank, total_win_rate_4_weekend_path, mythic_win_rate_4_weekend_path))

        for iteration in iteration_information_list:

            overall_months_overview_dic = iteration[0]
            day_list = iteration[1]
            total_store_path = iteration[2]
            mythic_store_path = iteration[3]

            for card_name in asset_name_list:
                total_wins = 0
                total_losses = 0
                total_wins_mythic = 0
                total_losses_mythic = 0

                for to_get_day in day_list:
                    to_get_year_month = "-".join(to_get_day.split("-")[0:2])
                    months_overview_dic = overall_months_overview_dic[to_get_year_month]
                    card_entry = months_overview_dic[card_name]

                    if to_get_day in card_entry:
                        day_entry = card_entry[to_get_day]
                        total_wins = total_wins + day_entry["wins_overall"]
                        total_losses = total_losses + day_entry["losses_overall"]
                        total_wins_mythic = total_wins_mythic + day_entry["wins_mythic"]
                        total_losses_mythic = total_losses_mythic + day_entry["losses_mythic"]

                if total_wins != 0 and total_losses != 0:
                    total_win_rate = total_wins / (total_wins + total_losses)
                else:
                    total_win_rate = None
                total_win_rate_dic[card_name] = total_win_rate

                if total_wins_mythic != 0 and total_losses_mythic != 0:
                    total_mythic_win_rate = total_wins_mythic / (total_wins_mythic + total_losses_mythic)
                else:
                    total_mythic_win_rate = None
                mythic_win_rate_dic[card_name] = total_mythic_win_rate

            with open(total_store_path, 'w', encoding='utf-8') as total_win_rate_file:
                json.dump(total_win_rate_dic, total_win_rate_file, ensure_ascii=False, indent=4)
            total_win_rate_file.close()

            with open(mythic_store_path, 'w', encoding='utf-8') as mythic_win_rate_file:
                json.dump(mythic_win_rate_dic, mythic_win_rate_file, ensure_ascii=False, indent=4)
            mythic_win_rate_file.close()

    @staticmethod
    def determine_days_in_last_4_weekend_rank():
        """
        A method to determine which the date of days in the last 4 weekends
        :return: a list of dates of the last 4 weekends
        """
        current_time_local = datetime.now()
        current_time = current_time_local.astimezone(pytz.utc)
        current_weekday = current_time.weekday()

        weekend_rank_counter = 0
        days_in_last_4_weekend_rank_list = []

        if current_weekday == 5 or current_weekday == 6:
            skip_one_weekend = True
        else:
            skip_one_weekend = False

        while weekend_rank_counter < 4:

            new_day = current_time - timedelta(days=1)
            new_day_str = new_day.isoformat().split('T')[0]
            new_weekday = new_day.weekday()

            if skip_one_weekend == False:
                if new_weekday == 5 or new_weekday == 6:
                    days_in_last_4_weekend_rank_list.append(new_day_str)
                if new_weekday == 4:
                    days_in_last_4_weekend_rank_list.append(new_day_str)
                    weekend_rank_counter = weekend_rank_counter + 1

            if new_weekday == 4 and skip_one_weekend == True:
                skip_one_weekend = False

            current_time = new_day

        return days_in_last_4_weekend_rank_list

    @staticmethod
    def create_last_24_hours_filled_orders_sales_timeline(today_filled_order_timeline_dic):
        """
        A method to create information about the sales that happened in the last 24 hours
        :param today_filled_order_timeline_dic: the last 24 hours timeline
        :return: None
        """

        gods_unchained_updated_assets_dic = GodsUnchainedScrapper.get_all_gods_unchained_assets()

        collectable_assets_list = [key.replace("\u2019", "'") for (key, value) in gods_unchained_updated_assets_dic.items() if value["collectable"] == True and value["set"] != "welcome"]
        #collectable_assets_dic = {key.replace("\u2019", "'"): 0 for (key, value) in gods_unchained_updated_assets_dic.items() if value["collectable"] == True}

        currencies_list = ["ETH", "GODS", "IMX", "USDC", "GOG", "OMI"]
        quality_list = ["Gold", "Shadow", "Meteorite", "DIAMOND"]

        collectable_assets_sales_dic = {key: 0 for key in collectable_assets_list}
        collectable_assets_price_dic = {key: [] for key in collectable_assets_list}
        collectable_assets_price_change_dic = {key: {} for key in collectable_assets_list}

        last_24_hours_sales_path = FileHandler.get_base_path("last_24_hours_sales")
        last_24_hours_price_path = FileHandler.get_base_path("last_24_hours_price")
        last_24_hours_price_change_path = FileHandler.get_base_path("last_24_hours_price_change")

        for currency in currencies_list:
            for quality in quality_list:

                current_sales_dic = copy.deepcopy(collectable_assets_sales_dic)
                current_price_dic = copy.deepcopy(collectable_assets_price_dic)
                current_price_change_dic = copy.deepcopy(collectable_assets_price_change_dic)

                for day_entries, card_name_dic in today_filled_order_timeline_dic.items():

                    day_and_hour = day_entries.split(":")[0]
                    minutes = day_entries.split(":")[1]
                    time_key = day_and_hour + ":" + minutes + ":00"

                    for card_name, info in card_name_dic.items():
                        card_count = 0
                        price_list = []

                        for order_id, entry in info.items():
                            if entry["currency"] == currency and entry["card_quality"] == quality:
                                card_count = card_count + 1
                                current_price = entry["price_euro_at_updated_timestamp_day"]

                                if current_price != None:
                                    price_list.append(current_price)

                        if card_name == "Oddi, Valka’s Herald":
                            card_name = "Oddi, Valka's Herald"

                        if (card_name in current_sales_dic) and (card_name in current_price_dic):
                            previous_entry_sale = current_sales_dic[card_name]
                            new_entry_sale = previous_entry_sale + card_count
                            current_sales_dic[card_name] = new_entry_sale

                            if len(price_list) > 0 and price_list != None:
                                previous_entry_price = current_price_dic[card_name]
                                if previous_entry_price == None:
                                    previous_entry_price = []
                                else:
                                    previous_entry_price.extend(price_list)

                                current_price_dic[card_name] = previous_entry_price

                                card_name_price_change_dic = current_price_change_dic[card_name]
                                if time_key in card_name_price_change_dic:
                                    previous_entry = card_name_price_change_dic[time_key]
                                    previous_entry.extend(price_list)
                                    card_name_price_change_dic[time_key] = previous_entry
                                else:
                                    new_entry = price_list
                                    card_name_price_change_dic[time_key] = new_entry
                                current_price_change_dic[card_name] = card_name_price_change_dic

                        else:
                            raise Exception(f"Card with name \"{card_name}\" is not in gods_unchained_updated_assets")

                final_today_sales_dic = {}
                for card_name, price_list in current_price_dic.items():
                    if price_list != None:
                        if len(price_list) > 0:
                            average_price = statistics.mean(price_list)
                        else:
                            average_price = None
                    else:
                        average_price = None

                    final_today_sales_dic[card_name] = average_price

                final_today_price_change_dic = {}
                for card_name, price_change_dic in current_price_change_dic.items():
                    if len(price_change_dic) > 0:
                        time_counter_list_unix = []
                        price_list = []

                        for time_key, prices in price_change_dic.items():

                            time_stamp = datetime.strptime(time_key, "%Y-%m-%dT%H:%M:%S")
                            time_stamp_unix = int(str(mktime(time_stamp.timetuple())).split('.')[0])

                            for price in prices:
                                time_counter_list_unix.append(time_stamp_unix)
                                price_list.append(price)

                        regressor = LinearRegression()
                        x_array = np.asarray(time_counter_list_unix).reshape(-1, 1)
                        regressor.fit(X=x_array, y=price_list)
                        price_change = float(regressor.coef_[0])
                    else:
                        price_change = None

                    final_today_price_change_dic[card_name] = price_change

                store_current_sale_file_path = str(last_24_hours_sales_path) + "/last_24_hours_sales_" + currency + "_" + quality + ".json"

                with open(store_current_sale_file_path, 'w', encoding='utf-8') as store_current_sale_file:
                    json.dump(current_sales_dic, store_current_sale_file, ensure_ascii=False, indent=4)
                store_current_sale_file.close()

                del current_sales_dic

                store_current_price_file_path = str(last_24_hours_price_path) + "/last_24_hours_price_" + currency + "_" + quality + ".json"

                with open(store_current_price_file_path, 'w', encoding='utf-8') as store_current_price_file:
                    json.dump(final_today_sales_dic, store_current_price_file, ensure_ascii=False, indent=4)
                store_current_price_file.close()

                del final_today_sales_dic

                store_current_price_change_file_path = str(last_24_hours_price_change_path) + "/last_24_hours_price_change_" + currency + "_" + quality + ".json"

                with open(store_current_price_change_file_path, 'w', encoding='utf-8') as store_current_price_change_file:
                    json.dump(final_today_price_change_dic, store_current_price_change_file, ensure_ascii=False, indent=4)
                store_current_price_change_file.close()

                del final_today_price_change_dic

    @staticmethod
    def create_filled_orders_sales_timeline(filled_order_timeline_dic):
        """
        A method to create information about all sales that happened in the last month
        :param filled_order_timeline_dic: the sale timeline of the last month
        :return: None
        """

        last_info_update_path = FileHandler.get_base_path("last_info_update")

        current_time_local = datetime.now()
        this_day_utc = current_time_local.astimezone(pytz.utc).isoformat().replace("+00:00", "Z").split('T')[0]

        if os.path.isfile(last_info_update_path):
            with open(last_info_update_path, 'r', encoding='utf-8') as last_info_update_file:
                last_info_update_dic = json.load(last_info_update_file)
            last_info_update_file.close()

            last_downloaded_day = last_info_update_dic["last_downloaded_day"]

            if last_downloaded_day == this_day_utc:
                today_not_created = False
            else:
                today_not_created = True
        else:
            today_not_created = True

        if today_not_created:

            filled_order_timeline_dic = DataCreator.determine_all_needed_dics(filled_order_timeline_dic, 30)

            gods_unchained_updated_assets_dic = GodsUnchainedScrapper.get_all_gods_unchained_assets()

            collectable_assets_list = [key.replace("\u2019", "'") for (key, value) in gods_unchained_updated_assets_dic.items() if value["collectable"] == True and value["set"] != "welcome"]
            #collectable_assets_list = ["Oddi, Valka’s Herald" if x == "Oddi, Valka's Herald" else x for x in collectable_assets_list]

            collectable_assets_sales_dic = {key: 0 for key in collectable_assets_list}
            collectable_assets_price_dic = {key: None for key in collectable_assets_list}
            collectable_assets_price_change_dic = {key: None for key in collectable_assets_list}

            currencies_list = ["ETH", "GODS", "IMX", "USDC", "GOG", "OMI"]
            quality_list = ["Gold", "Shadow", "Meteorite", "DIAMOND"]

            current_time_local = datetime.now()
            today_utc = current_time_local.astimezone(pytz.utc)

            days_in_last_30_days = []

            for day in range(1, 31):
                new_day_time_stamp = today_utc - timedelta(days=day)
                new_day_str = new_day_time_stamp.isoformat().split('T')[0]
                days_in_last_30_days.append(new_day_str)

            last_30_days_sales = FileHandler.get_base_path("last_30_days_sales")
            last_30_days_price = FileHandler.get_base_path("last_30_days_price")
            last_30_days_price_change = FileHandler.get_base_path("last_30_days_price_change")

            for currency in currencies_list:
                for quality in quality_list:

                    last_30_days_sales_dic = copy.deepcopy(collectable_assets_sales_dic)
                    last_30_days_price_dic = copy.deepcopy(collectable_assets_price_dic)
                    last_30_days_price_change_dic = copy.deepcopy(collectable_assets_price_change_dic)

                    for card_name, day_entries in filled_order_timeline_dic.items():
                        card_count_dic = {}
                        price_list = []
                        price_change_dic = {}

                        for day_name, day_dic in day_entries.items():
                            if day_name in days_in_last_30_days:
                                for order_id, entry in day_dic.items():
                                    if entry["currency"] == currency and entry["card_quality"] == quality:

                                        if day_name in card_count_dic:
                                            previous_count = card_count_dic[day_name]
                                        else:
                                            previous_count = 0
                                        new_count = previous_count + 1
                                        card_count_dic[day_name] = new_count

                                        if entry["price_euro_at_updated_timestamp_day"] != None:
                                            price_list.append(entry["price_euro_at_updated_timestamp_day"])
                                            #timestamp_list.append()

                                            if day_name in price_change_dic:
                                                previous_entry = price_change_dic[day_name]
                                                current_price = entry["price_euro_at_updated_timestamp_day"]
                                                previous_entry.append(current_price)
                                                price_change_dic[day_name] = previous_entry
                                            else:
                                                new_entry = [entry["price_euro_at_updated_timestamp_day"]]
                                                price_change_dic[day_name] = new_entry

                        if card_name == "Oddi, Valka’s Herald":
                            card_name = "Oddi, Valka's Herald"

                        if (card_name in last_30_days_sales_dic) and (card_name in last_30_days_price_dic) and (card_name in last_30_days_price_change_dic):

                            last_30_days_sales_dic[card_name] = card_count_dic

                            if len(price_list) > 0:
                                price = statistics.mean(price_list)
                            else:
                                price = None
                            last_30_days_price_dic[card_name] = price

                            if len(price_change_dic) > 0:
                                time_counter_list_unix = []
                                price_list = []

                                for time_key, prices in price_change_dic.items():

                                    time_stamp = datetime.strptime(time_key, "%Y-%m-%d")
                                    time_stamp_unix = int(str(mktime(time_stamp.timetuple())).split('.')[0])

                                    for price in prices:
                                        time_counter_list_unix.append(time_stamp_unix)
                                        price_list.append(price)

                                regressor = LinearRegression()
                                x_array = np.asarray(time_counter_list_unix).reshape(-1, 1)
                                regressor.fit(X=x_array, y=price_list)
                                price_change = float(regressor.coef_[0])
                            else:
                                price_change = None

                            last_30_days_price_change_dic[card_name] = price_change

                        else:
                            raise Exception(f"Card with name \"{card_name}\" is not in gods_unchained_updated_assets")

                    store_path_sales = str(last_30_days_sales) + "/last_30_days_sales_" + currency + "_" + quality + ".json"
                    with open(store_path_sales, 'w', encoding='utf-8') as last_week_sales_file:
                        json.dump(last_30_days_sales_dic, last_week_sales_file, ensure_ascii=False, indent=4)
                    last_week_sales_file.close()

                    store_path_price = str(last_30_days_price) + "/last_30_days_price_" + currency + "_" + quality + ".json"
                    with open(store_path_price, 'w', encoding='utf-8') as last_week_price_file:
                        json.dump(last_30_days_price_dic, last_week_price_file, ensure_ascii=False, indent=4)
                    last_week_price_file.close()

                    store_path_price_change = str(last_30_days_price_change) + "/last_30_days_price_change_" + currency + "_" + quality + ".json"
                    with open(store_path_price_change, 'w', encoding='utf-8') as last_week_price_change_file:
                        json.dump(last_30_days_price_change_dic, last_week_price_change_file, ensure_ascii=False, indent=4)
                    last_week_price_change_file.close()

            days_in_last_week = []

            for day in range(1, 8):
                new_day_time_stamp = today_utc - timedelta(days=day)
                new_day_str = new_day_time_stamp.isoformat().split('T')[0]
                days_in_last_week.append(new_day_str)

            last_week_sales_path = FileHandler.get_base_path("last_7_days_sales")
            last_week_price_path = FileHandler.get_base_path("last_7_days_price")
            last_week_price_change_path = FileHandler.get_base_path("last_7_days_price_change")

            for currency in currencies_list:
                for quality in quality_list:

                    last_7_days_sales_dic = copy.deepcopy(collectable_assets_sales_dic)
                    last_7_days_price_dic = copy.deepcopy(collectable_assets_price_dic)
                    last_7_days_price_change_dic = copy.deepcopy(collectable_assets_price_change_dic)

                    for card_name, day_entries in filled_order_timeline_dic.items():
                        card_count_dic = {}
                        price_list = []
                        price_change_dic = {}
                        for day_name, day_dic in day_entries.items():
                            if day_name in days_in_last_week:
                                for order_id, entry in day_dic.items():
                                    if entry["currency"] == currency and entry["card_quality"] == quality:

                                        if day_name in card_count_dic:
                                            previous_count = card_count_dic[day_name]
                                        else:
                                            previous_count = 0
                                        new_count = previous_count + 1
                                        card_count_dic[day_name] = new_count

                                        if entry["price_euro_at_updated_timestamp_day"] != None:
                                            price_list.append(entry["price_euro_at_updated_timestamp_day"])

                                            if day_name in price_change_dic:
                                                previous_entry = price_change_dic[day_name]
                                                current_price = entry["price_euro_at_updated_timestamp_day"]
                                                previous_entry.append(current_price)
                                                price_change_dic[day_name] = previous_entry
                                            else:
                                                new_entry = [entry["price_euro_at_updated_timestamp_day"]]
                                                price_change_dic[day_name] = new_entry

                        if card_name == "Oddi, Valka’s Herald":
                            card_name = "Oddi, Valka's Herald"

                        if (card_name in last_7_days_sales_dic) and (card_name in last_7_days_price_dic):

                            last_7_days_sales_dic[card_name] = card_count_dic

                            if len(price_list) > 0:
                                price = statistics.mean(price_list)
                            else:
                                price = None
                            last_7_days_price_dic[card_name] = price

                            if len(price_change_dic) > 0:
                                time_counter_list_unix = []
                                price_list = []

                                for time_key, prices in price_change_dic.items():

                                    time_stamp = datetime.strptime(time_key, "%Y-%m-%d")
                                    time_stamp_unix = int(str(mktime(time_stamp.timetuple())).split('.')[0])

                                    for price in prices:
                                        time_counter_list_unix.append(time_stamp_unix)
                                        price_list.append(price)

                                regressor = LinearRegression()
                                x_array = np.asarray(time_counter_list_unix).reshape(-1, 1)
                                regressor.fit(X=x_array, y=price_list)
                                price_change = float(regressor.coef_[0])
                            else:
                                price_change = None

                            last_7_days_price_change_dic[card_name] = price_change

                        else:
                            raise Exception(f"Card with name \"{card_name}\" is not in gods_unchained_updated_assets")

                    store_path_sales = str(last_week_sales_path) + "/last_7_days_sales_" + currency + "_" + quality + ".json"
                    with open(store_path_sales, 'w', encoding='utf-8') as last_week_sales_file:
                        json.dump(last_7_days_sales_dic, last_week_sales_file, ensure_ascii=False, indent=4)
                    last_week_sales_file.close()

                    store_path_price = str(last_week_price_path) + "/last_7_days_price_" + currency + "_" + quality + ".json"
                    with open(store_path_price, 'w', encoding='utf-8') as last_week_price_file:
                        json.dump(last_7_days_price_dic, last_week_price_file, ensure_ascii=False, indent=4)
                    last_week_price_file.close()

                    store_path_price_change = str(last_week_price_change_path) + "/last_7_days_price_change_" + currency + "_" + quality + ".json"
                    with open(store_path_price_change, 'w', encoding='utf-8') as last_week_price_change_file:
                        json.dump(last_7_days_price_change_dic, last_week_price_change_file, ensure_ascii=False, indent=4)
                    last_week_price_change_file.close()

            latest_info_update_dic = {}
            latest_info_update_dic["last_downloaded_day"] = this_day_utc

            with open(last_info_update_path, 'w', encoding='utf-8') as last_info_update_file:
                json.dump(latest_info_update_dic, last_info_update_file, ensure_ascii=False, indent=4)
            last_info_update_file.close()

    @staticmethod
    def determine_all_needed_dics(filled_order_timeline_dic, max_number_days):
        """
        A method to determine which timeline dictionaries to load to cover last X days
        :param filled_order_timeline_dic: the overall timeline dictionary
        :param max_number_days: the last x days to consider
        :return: a combined timeline dictionary covering all days
        """

        current_time_local = datetime.now()
        today_utc = current_time_local.astimezone(pytz.utc)
        ago_date_utc = today_utc - timedelta(max_number_days)

        today_month_year = datetime.strftime(today_utc, "%Y-%m-%dT%H:%M:%S.%fZ").split('T')[0].split('-')[:2]
        ago_month_year = datetime.strftime(ago_date_utc, "%Y-%m-%dT%H:%M:%S.%fZ").split('T')[0].split('-')[:2]

        target_date = (int(today_month_year[0]), int(today_month_year[1]))
        change_date = (int(ago_month_year[0]), int(ago_month_year[1]))

        not_found = True
        year_month_list = []
        first_entry = str(change_date[0]) + "-" + str(change_date[1])
        year_month_list.append(first_entry)

        while not_found:

            next_month = int(change_date[1]) + 1
            if next_month > 12:
                next_month = 1
                next_year = int(change_date[0]) + 1
            else:
                next_year = change_date[0]

            next_date = str(next_year) + "-" + str(next_month)

            year_month_list.append(next_date)

            if (next_year == target_date[0]) and (next_month == target_date[1]):
                not_found = False

            change_date = (next_year, next_month)

        to_load_list = []
        for year_month in year_month_list:
            if year_month not in filled_order_timeline_dic:
                to_load_list.append(year_month)

        loaded_dics = FileIoHelper.load_filled_order_timeline_dic(to_load_list)

        for year_month, filled_order_dic in loaded_dics.items():
            filled_order_timeline_dic[year_month] = filled_order_dic

        combined_timeline_dic = DataCreator.create_combined_timeline_dic(filled_order_timeline_dic)

        return combined_timeline_dic

    @staticmethod
    def create_combined_timeline_dic(filled_order_timeline_dic):
        """
        A method to create a combined timeline dictionary
        :param filled_order_timeline_dic: the overall timeline dictionary
        :return: a combined timeline dictionary
        """

        combined_timeline_dic = {}

        for year_month, filled_order_dic in filled_order_timeline_dic.items():

            for card_name, day_dic in filled_order_dic.items():
                if card_name in combined_timeline_dic:
                    card_name_entry = combined_timeline_dic[card_name]
                else:
                    card_name_entry = {}

                for day, order_id_dic in day_dic.items():
                    if day in card_name_entry:
                        date_entry = card_name_entry[day]
                    else:
                        date_entry = {}

                    for order_id, info in order_id_dic.items():
                        if str(order_id) in date_entry:
                            print(f"order_id {order_id} already in dic - potentially duplicate entry from {year_month}")
                        else:
                            date_entry[order_id] = info

                    card_name_entry[day] = date_entry

                combined_timeline_dic[card_name] = card_name_entry

        return combined_timeline_dic

    @staticmethod
    def create_info_for_filled_orders(sell_order_df):
        """
        A method to create information about past sales
        :param sell_order_df: a DataFrame covering the past sales
        :return: None
        """

        currency_df = sell_order_df["currency"].value_counts().to_frame().reset_index()
        plt.pie(currency_df["currency"], labels=currency_df["index"], autopct='%.2f')
        plt.title("Currency Distribution")
        plt.show()
        plt.close()

        quality_df = sell_order_df["card_quality"].value_counts().to_frame().reset_index()
        plt.pie(quality_df["card_quality"], labels=quality_df["index"], autopct='%.2f')
        plt.title("Card Quality Distribution")
        plt.show()
        plt.close()

        rarity_df = sell_order_df["card_rarity"].value_counts().to_frame().reset_index()
        plt.pie(rarity_df["card_rarity"], labels=rarity_df["index"], autopct='%.2f')
        plt.title("Card Rarity Distribution")
        plt.show()
        plt.close()

        god_df = sell_order_df["card_god"].value_counts().to_frame().reset_index()
        plt.pie(god_df["card_god"], labels=god_df["index"], autopct='%.2f')
        plt.title("God Distribution")
        plt.show()
        plt.close()

        tribe_df = sell_order_df["card_tribe"].value_counts().to_frame().reset_index()
        # tribe_df = tribe_df[tribe_df["index"] != ""]
        plt.pie(tribe_df["card_tribe"], labels=tribe_df["index"], autopct='%.2f')
        plt.title("Tribe Distribution")
        plt.show()
        plt.close()

        set_df = sell_order_df["card_set"].value_counts().to_frame().reset_index()
        plt.pie(set_df["card_set"], labels=set_df["index"], autopct='%.2f')
        plt.title("Set Distribution")
        plt.show()
        plt.close()

        test_df = sell_order_df
        test_df["timestamp"] = test_df["updated_timestamp"].dt.strftime('%d/%m/%Y')
        test_df = test_df.groupby(["timestamp"])["order_id"].count().reset_index()

        test_df = test_df.rename(columns={"order_id": "count"})
        test_df["timestamp"] = pd.to_datetime(test_df.timestamp, format='%d/%m/%Y')
        test_df["label"] = test_df["timestamp"].dt.strftime('%d/%m')
        test_df = test_df.sort_values(by="timestamp", ascending=True)
        test_df = test_df[-7:]
        print(test_df)

        fig, ax = plt.subplots()
        ax.bar(x=test_df["timestamp"], height=test_df["count"])
        ax.set_xticks(test_df["timestamp"], test_df["label"], rotation=45)
        ax.set_title("Sale Distribution")
        plt.show()
        plt.close()

    @staticmethod
    def recreate_base_line_updated_active_orders():
        """
        A method to recreate a baseline active updated orders file
        :return: None
        """

        print("Loading Filled Order IDs")
        json_files_filled = FileHandler.get_all_paths_of_get_type_and_status_orders("SELL", "FILLED")
        json_files_filled = [path for path in json_files_filled if os.path.isfile(path)]
        filled_order_id_set = set(OrderAdministratorGU.get_all_order_id_for_type_order(json_files_filled))

        print("Loading Inactive Order IDs")
        json_files_inactive = FileHandler.get_all_paths_of_get_type_and_status_orders("SELL", "INACTIVE")
        json_files_inactive = [path for path in json_files_inactive if os.path.isfile(path)]
        inactive_order_id_set = set(OrderAdministratorGU.get_all_order_id_for_type_order(json_files_inactive))

        print("Loading Expired Order IDs")
        json_files_expired = FileHandler.get_all_paths_of_get_type_and_status_orders("SELL", "EXPIRED")
        json_files_expired = [path for path in json_files_expired if os.path.isfile(path)]
        expired_order_id_set = set(OrderAdministratorGU.get_all_order_id_for_type_order(json_files_expired))

        print("Loading Cancelled Order IDs")
        json_files_cancelled = FileHandler.get_all_paths_of_get_type_and_status_orders("SELL", "CANCELLED")
        json_files_cancelled = [path for path in json_files_cancelled if os.path.isfile(path)]
        cancelled_order_id_set = set(OrderAdministratorGU.get_all_order_id_for_type_order(json_files_cancelled))

        print("Creating Active Order Rolling DF")
        json_files_active = FileHandler.get_all_paths_of_get_type_and_status_orders("SELL", "ACTIVE")
        json_files_active = [path for path in json_files_active if os.path.isfile(path)]
        active_orders_df = OrderAdministratorGU.create_df_from_path_list(json_files_active)

        active_orders_filtered_df_1 = active_orders_df[~active_orders_df["order_id"].isin(filled_order_id_set)]
        active_orders_filtered_df_2 = active_orders_filtered_df_1[~active_orders_filtered_df_1["order_id"].isin(cancelled_order_id_set)]
        active_orders_filtered_df_3 = active_orders_filtered_df_2[~active_orders_filtered_df_2["order_id"].isin(inactive_order_id_set)]
        active_orders_filtered_df_4 = active_orders_filtered_df_3[~active_orders_filtered_df_3["order_id"].isin(expired_order_id_set)]

        final_active_orders_filtered_df = active_orders_filtered_df_4.dropna(subset=["card_name"])

        print("Writing Active Order Updated to File")
        OrderAdministratorGU.write_updated_active_sell_order_df_to_file(final_active_orders_filtered_df)

        active_orders_to_be_processed_file_path_list = Processing_File_Helper.get_path_list_for_type_order_processing(get_type_string="SELL", status_string="ACTIVE")
        if len(active_orders_to_be_processed_file_path_list) > 0:
            for path in active_orders_to_be_processed_file_path_list:
                os.remove(path)

        filled_orders_to_be_processed_file_path_list = Processing_File_Helper.get_path_list_for_type_order_processing(get_type_string="SELL", status_string="FILLED")
        if len(filled_orders_to_be_processed_file_path_list) > 0:
            for path in filled_orders_to_be_processed_file_path_list:
                os.remove(path)

        cancelled_orders_to_be_processed_file_path_list = Processing_File_Helper.get_path_list_for_type_order_processing(get_type_string="SELL", status_string="CANCELLED")
        if len(cancelled_orders_to_be_processed_file_path_list) > 0:
            for path in cancelled_orders_to_be_processed_file_path_list:
                os.remove(path)

        inactive_orders_to_be_processed_file_path_list = Processing_File_Helper.get_path_list_for_type_order_processing(get_type_string="SELL", status_string="INACTIVE")
        if len(inactive_orders_to_be_processed_file_path_list) > 0:
            for path in inactive_orders_to_be_processed_file_path_list:
                os.remove(path)

        expired_orders_to_be_processed_file_path_list = Processing_File_Helper.get_path_list_for_type_order_processing(get_type_string="SELL", status_string="EXPIRED")
        if len(expired_orders_to_be_processed_file_path_list) > 0:
            for path in expired_orders_to_be_processed_file_path_list:
                os.remove(path)

        processing_data_folder_path = str(FileHandler.get_base_path("processing_data_folder"))
        search_string = str(processing_data_folder_path) + "\\*.json"
        for_processing_json_files = glob.glob(search_string)
        for json_file in for_processing_json_files:
            os.remove(json_file)


    @staticmethod
    def recreate_base_line_filled_order_timeline():
        """
        A method to create a base_line filled order timeline
        :return: None
        """

        json_files = FileHandler.get_all_paths_of_type_of_orders("SELL", "FILLED", "ROLLING")

        combined_dic = {}

        for index, file_path in enumerate(json_files):

            print(f"File {index + 1}/{len(json_files)} with path {file_path}")

            order_list = OrderAdministratorGU.create_order_list_from_path(file_path)
            order_list = [x for x in order_list if x.card_name != None]

            year_month_list = DataCreator.determine_year_month_orders_downloaded(order_list)
            previous_filled_orders_dic = FileIoHelper.load_filled_order_timeline_dic(year_month_list)
            new_filled_orders_dic = DataCreator.update_base_line_filled_order_timeline(order_list, previous_filled_orders_dic)
            for year_month, filled_order_dic in new_filled_orders_dic.items():
                combined_dic[year_month] = filled_order_dic
            FileIoHelper.writing_filled_order_timeline_path_to_file(new_filled_orders_dic)

            today_filled_order_timeline_dic = FileIoHelper.load_today_filled_order_timeline_dic()
            new_today_filled_order_timeline_dic = DataCreator.update_today_filled_sales(order_list, today_filled_order_timeline_dic)
            FileIoHelper.writing_today_filled_order_timeline_dic_to_file(new_today_filled_order_timeline_dic)
            DataCreator.create_last_24_hours_filled_orders_sales_timeline(today_filled_order_timeline_dic)

        DataCreator.create_filled_orders_sales_timeline(combined_dic)


    @staticmethod
    def recreate_base_line_win_rate():
        """
        A method to recreate base_line win rate
        :return: None
        """

        print("Loading the max line numbers")
        card_win_rate_to_be_processed_file_path  = FileHandler.get_base_path("card_win_rate_to_be_processed")
        lines_in_win_rate_to_be_processed_file = FileIoHelper.get_lines_in_file(card_win_rate_to_be_processed_file_path)

        start_position = 0
        if lines_in_win_rate_to_be_processed_file < 1000000:
            end_position = lines_in_win_rate_to_be_processed_file
        else:
            end_position = 1000000
        not_caught_up_to_now = True

        while not_caught_up_to_now:

            print(f"Updating from {start_position} to {end_position} out of {lines_in_win_rate_to_be_processed_file}")

            if end_position == lines_in_win_rate_to_be_processed_file:
                not_caught_up_to_now = False

            part_win_rate_list = WinRateAdministrator.create_limited_win_rate_to_be_processed_list(start_position, end_position)

            print("Creating Month Overview")
            DataCreator.update_win_rate_month_overview(part_win_rate_list)

            start_position = end_position

            if (end_position + 1000000) > lines_in_win_rate_to_be_processed_file:
                end_position = lines_in_win_rate_to_be_processed_file
            else:
                end_position = end_position + 1000000

        os.remove(card_win_rate_to_be_processed_file_path)
