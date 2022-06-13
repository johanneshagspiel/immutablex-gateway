import time

from util.files.file_handler import File_Handler
import pandas as pd

class Trade_Classifier():

    def __init__(self):
        None

    @staticmethod
    def create_df_of_orders_type_1(inventory_list, purchase_currency, sale_currency):

        potential_purchases_folder_path = File_Handler.get_base_path("potential_purchases")
        path_to_csv_file = str(potential_purchases_folder_path) + '\\' + str(purchase_currency) + "_TO_" + str(sale_currency) + ".csv"

        not_yet_read = True
        while not_yet_read:
            try:
                overall_df = pd.read_csv(path_to_csv_file)
                not_yet_read = False

            except PermissionError:
                time.sleep(2)

        ###

        currency_1_name = str(purchase_currency)
        currency_1_token_id = currency_1_name + "_token_id"
        currency_1_order_id = currency_1_name + "_order_id"
        currency_1_cheapest = "cheapest_" + currency_1_name
        currency_1_cheapest_euro = "cheapest_" + currency_1_name + "_euro"

        currency_2_name = str(sale_currency)
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

        ###


        max_price = 5
        quality = "Meteorite"
        min_profit_span = 1.025
        win_rate_type = "win_4_w"
        min_win_rate = 0.5

        ###

        overall_df = overall_df[overall_df["quality"] == quality]
        overall_df = overall_df[overall_df["t_dif"] > 0]
        overall_df = overall_df[overall_df[currency_1_cheapest_euro] < max_price]
        inventory_card_name_list = [inventory_entry.card_name for inventory_entry in inventory_list if inventory_entry.card_quality == quality and inventory_entry.purchase_currency == purchase_currency]
        overall_df = overall_df[~overall_df["card_name"].isin(inventory_card_name_list)]


        overall_df = overall_df[(min_profit_span * overall_df[currency_1_cheapest_euro]) < overall_df[currency_2_cheapest_euro]]

        overall_df = overall_df[(min_profit_span * overall_df[currency_1_cheapest_euro]) < overall_df[last_24_hours_price]]

        overall_df = overall_df[overall_df[win_rate_type] != None]
        overall_df = overall_df[overall_df[win_rate_type] >= min_win_rate]

        overall_df = overall_df[overall_df[last_24_hours_price_change] >= 0]

        overall_df = overall_df[overall_df[last_7_days_price_change] >= 0]

        overall_df = overall_df[overall_df[last_30_days_at_least_one_sale] == True]


        overall_df = overall_df.sort_values(by='rel_dif', ascending=False)

        overall_df = overall_df[["card_name", currency_1_cheapest_euro, currency_2_cheapest_euro,
                                                 last_24_hours_price, last_7_days_price, last_30_days_price,
                                                 "rel_dif", "t_dif",
                                                 last_24_hours_price_change, last_7_days_price_change, last_30_days_price_change,
                                                 last_24_hours_sales, last_7_days_sales,
                                                 "win_4_w",
                                                 currency_1_order_id, currency_1_cheapest, currency_2_cheapest]]

        ###

        classification_dic = {}
        classification_dic["purchase_currency"] = purchase_currency
        classification_dic["sale_currency"] = sale_currency
        classification_dic["max_price"] = max_price
        classification_dic["quality"] = quality

        classification_dic["min_profit_span"] = min_profit_span

        classification_dic["last_24_hours_price_above_profit_span"] = True

        classification_dic["win_rate_type"] = win_rate_type
        classification_dic["min_win_rate"] = min_win_rate

        classification_dic["last_24_hours_price_change"] = ">= 0"

        classification_dic["last_7_days_price_change"] = ">= 0"

        classification_dic["last_30_days_at_least_one_sale"] = True

        return overall_df, classification_dic


    @staticmethod
    def create_df_of_orders_type_2(inventory_list, purchase_currency, sale_currency):
        potential_purchases_folder_path = File_Handler.get_base_path("potential_purchases")
        path_to_csv_file = str(potential_purchases_folder_path) + '\\' + str(purchase_currency) + "_TO_" + str(
            sale_currency) + ".csv"


        not_yet_read = True
        while not_yet_read:
            try:
                overall_df = pd.read_csv(path_to_csv_file)
                not_yet_read = False

            except PermissionError:
                print(f"File {path_to_csv_file} currently in use - we will wait for 2 seconds")
                time.sleep(2)

        ###

        currency_1_name = str(purchase_currency)
        currency_1_token_id = currency_1_name + "_token_id"
        currency_1_order_id = currency_1_name + "_order_id"
        currency_1_cheapest = "cheapest_" + currency_1_name
        currency_1_cheapest_euro = "cheapest_" + currency_1_name + "_euro"

        currency_2_name = str(sale_currency)
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

        ###

        max_price = 5
        quality = "Meteorite"
        min_profit_span = 1.025
        win_rate_type = "win_4_w"
        min_win_rate = 0.5

        ###

        overall_df = overall_df[overall_df["quality"] == quality]
        overall_df = overall_df[overall_df["t_dif"] > 0]
        overall_df = overall_df[overall_df[currency_1_cheapest_euro] < max_price]
        inventory_card_name_list = [inventory_entry.card_name for inventory_entry in inventory_list if inventory_entry.card_quality == quality and inventory_entry.purchase_currency == purchase_currency]
        overall_df = overall_df[~overall_df["card_name"].isin(inventory_card_name_list)]

        overall_df = overall_df[(min_profit_span * overall_df[currency_1_cheapest_euro]) < overall_df[currency_2_cheapest_euro]]

        overall_df = overall_df[(min_profit_span * overall_df[currency_1_cheapest_euro]) < overall_df[last_24_hours_price]]

        overall_df = overall_df[overall_df[win_rate_type] != None]
        overall_df = overall_df[overall_df[win_rate_type] >= min_win_rate]

        overall_df = overall_df[overall_df[last_24_hours_price_change] >= 0]

        overall_df = overall_df[overall_df[last_30_days_at_least_one_sale] == True]

        overall_df = overall_df.sort_values(by='rel_dif', ascending=False)

        overall_df = overall_df[["card_name", currency_1_cheapest_euro, currency_2_cheapest_euro,
                                 last_24_hours_price, last_7_days_price, last_30_days_price,
                                 "rel_dif", "t_dif",
                                 last_24_hours_price_change, last_7_days_price_change, last_30_days_price_change,
                                 last_24_hours_sales, last_7_days_sales,
                                 "win_4_w",
                                 currency_1_order_id, currency_1_cheapest, currency_2_cheapest]]

        ###

        classification_dic = {}
        classification_dic["purchase_currency"] = purchase_currency
        classification_dic["sale_currency"] = sale_currency
        classification_dic["max_price"] = max_price
        classification_dic["quality"] = quality

        classification_dic["min_profit_span"] = min_profit_span

        classification_dic["last_24_hours_price_above_profit_span"] = True

        classification_dic["win_rate_type"] = win_rate_type
        classification_dic["min_win_rate"] = min_win_rate

        classification_dic["last_24_hours_price_change"] = ">= 0"

        classification_dic["last_30_days_at_least_one_sale"] = True

        return overall_df, classification_dic


    @staticmethod
    def create_df_of_orders_type_3(inventory_list, purchase_currency, sale_currency):
        potential_purchases_folder_path = File_Handler.get_base_path("potential_purchases")
        path_to_csv_file = str(potential_purchases_folder_path) + '\\' + str(purchase_currency) + "_TO_" + str(
            sale_currency) + ".csv"


        not_yet_read = True
        while not_yet_read:
            try:
                overall_df = pd.read_csv(path_to_csv_file)
                not_yet_read = False

            except PermissionError:
                print(f"File {path_to_csv_file} currently in use - we will wait for 2 seconds")
                time.sleep(2)

        ###

        currency_1_name = str(purchase_currency)
        currency_1_token_id = currency_1_name + "_token_id"
        currency_1_order_id = currency_1_name + "_order_id"
        currency_1_cheapest = "cheapest_" + currency_1_name
        currency_1_cheapest_euro = "cheapest_" + currency_1_name + "_euro"

        currency_2_name = str(sale_currency)
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

        ###

        max_price = 5
        quality = "Meteorite"
        min_profit_span = 1.025
        win_rate_type = "win_4_w"
        min_win_rate = 0.5

        ###

        overall_df = overall_df[overall_df["quality"] == quality]
        overall_df = overall_df[overall_df["t_dif"] > 0]
        overall_df = overall_df[overall_df[currency_1_cheapest_euro] < max_price]
        inventory_card_name_list = [inventory_entry.card_name for inventory_entry in inventory_list if inventory_entry.card_quality == quality and inventory_entry.purchase_currency == purchase_currency]
        overall_df = overall_df[~overall_df["card_name"].isin(inventory_card_name_list)]

        overall_df = overall_df[(min_profit_span * overall_df[currency_1_cheapest_euro]) < overall_df[currency_2_cheapest_euro]]

        overall_df = overall_df[(min_profit_span * overall_df[currency_1_cheapest_euro]) < overall_df[last_24_hours_price]]

        overall_df = overall_df[overall_df[win_rate_type] != None]
        overall_df = overall_df[overall_df[win_rate_type] >= min_win_rate]

        overall_df = overall_df[overall_df[last_7_days_price_change] >= 0]

        overall_df = overall_df[overall_df[last_30_days_at_least_one_sale] == True]

        overall_df = overall_df.sort_values(by='rel_dif', ascending=False)

        overall_df = overall_df[["card_name", currency_1_cheapest_euro, currency_2_cheapest_euro,
                                 last_24_hours_price, last_7_days_price, last_30_days_price,
                                 "rel_dif", "t_dif",
                                 last_24_hours_price_change, last_7_days_price_change, last_30_days_price_change,
                                 last_24_hours_sales, last_7_days_sales,
                                 "win_4_w",
                                 currency_1_order_id, currency_1_cheapest, currency_2_cheapest]]

        ###

        classification_dic = {}
        classification_dic["purchase_currency"] = purchase_currency
        classification_dic["sale_currency"] = sale_currency
        classification_dic["max_price"] = max_price
        classification_dic["quality"] = quality

        classification_dic["min_profit_span"] = min_profit_span

        classification_dic["last_24_hours_price_above_profit_span"] = True

        classification_dic["win_rate_type"] = win_rate_type
        classification_dic["min_win_rate"] = min_win_rate

        classification_dic["last_7_days_price_change"] = ">= 0"

        classification_dic["last_30_days_at_least_one_sale"] = True

        return overall_df, classification_dic


    @staticmethod
    def create_df_of_orders_type_4(inventory_list, purchase_currency, sale_currency):
        potential_purchases_folder_path = File_Handler.get_base_path("potential_purchases")
        path_to_csv_file = str(potential_purchases_folder_path) + '\\' + str(purchase_currency) + "_TO_" + str(
            sale_currency) + ".csv"


        not_yet_read = True
        while not_yet_read:
            try:
                overall_df = pd.read_csv(path_to_csv_file)
                not_yet_read = False

            except PermissionError:
                print(f"File {path_to_csv_file} currently in use - we will wait for 2 seconds")
                time.sleep(2)

        ###

        currency_1_name = str(purchase_currency)
        currency_1_token_id = currency_1_name + "_token_id"
        currency_1_order_id = currency_1_name + "_order_id"
        currency_1_cheapest = "cheapest_" + currency_1_name
        currency_1_cheapest_euro = "cheapest_" + currency_1_name + "_euro"

        currency_2_name = str(sale_currency)
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

        ###

        max_price = 5
        quality = "Meteorite"
        min_profit_span = 1.025
        win_rate_type = "win_4_w"
        min_win_rate = 0.5

        ###

        overall_df = overall_df[overall_df["quality"] == quality]
        overall_df = overall_df[overall_df["t_dif"] > 0]
        overall_df = overall_df[overall_df[currency_1_cheapest_euro] < max_price]
        inventory_card_name_list = [inventory_entry.card_name for inventory_entry in inventory_list if inventory_entry.card_quality == quality and inventory_entry.purchase_currency == purchase_currency]
        overall_df = overall_df[~overall_df["card_name"].isin(inventory_card_name_list)]

        overall_df = overall_df[(min_profit_span * overall_df[currency_1_cheapest_euro]) < overall_df[currency_2_cheapest_euro]]

        overall_df = overall_df[(min_profit_span * overall_df[currency_1_cheapest_euro]) < overall_df[last_24_hours_price]]

        overall_df = overall_df[overall_df[win_rate_type] != None]
        overall_df = overall_df[overall_df[win_rate_type] >= min_win_rate]

        overall_df = overall_df[overall_df[last_30_days_at_least_one_sale] == True]

        overall_df = overall_df.sort_values(by='rel_dif', ascending=False)

        overall_df = overall_df[["card_name", currency_1_cheapest_euro, currency_2_cheapest_euro,
                                 last_24_hours_price, last_7_days_price, last_30_days_price,
                                 "rel_dif", "t_dif",
                                 last_24_hours_price_change, last_7_days_price_change, last_30_days_price_change,
                                 last_24_hours_sales, last_7_days_sales,
                                 "win_4_w",
                                 currency_1_order_id, currency_1_cheapest, currency_2_cheapest]]

        ###

        classification_dic = {}
        classification_dic["purchase_currency"] = purchase_currency
        classification_dic["sale_currency"] = sale_currency
        classification_dic["max_price"] = max_price
        classification_dic["quality"] = quality

        classification_dic["min_profit_span"] = min_profit_span

        classification_dic["last_24_hours_price_above_profit_span"] = True

        classification_dic["win_rate_type"] = win_rate_type
        classification_dic["min_win_rate"] = min_win_rate

        classification_dic["last_30_days_at_least_one_sale"] = True

        return overall_df, classification_dic


    @staticmethod
    def create_df_of_orders_type_5(inventory_list, purchase_currency, sale_currency):
        potential_purchases_folder_path = File_Handler.get_base_path("potential_purchases")
        path_to_csv_file = str(potential_purchases_folder_path) + '\\' + str(purchase_currency) + "_TO_" + str(
            sale_currency) + ".csv"


        not_yet_read = True
        while not_yet_read:
            try:
                overall_df = pd.read_csv(path_to_csv_file)
                not_yet_read = False

            except PermissionError:
                print(f"File {path_to_csv_file} currently in use - we will wait for 2 seconds")
                time.sleep(2)

        ###

        currency_1_name = str(purchase_currency)
        currency_1_token_id = currency_1_name + "_token_id"
        currency_1_order_id = currency_1_name + "_order_id"
        currency_1_cheapest = "cheapest_" + currency_1_name
        currency_1_cheapest_euro = "cheapest_" + currency_1_name + "_euro"

        currency_2_name = str(sale_currency)
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

        ###

        max_price = 5
        quality = "Meteorite"
        min_profit_span = 1.025

        ###

        overall_df = overall_df[overall_df["quality"] == quality]
        overall_df = overall_df[overall_df["t_dif"] > 0]
        overall_df = overall_df[overall_df[currency_1_cheapest_euro] < max_price]
        inventory_card_name_list = [inventory_entry.card_name for inventory_entry in inventory_list if inventory_entry.card_quality == quality and inventory_entry.purchase_currency == purchase_currency]
        overall_df = overall_df[~overall_df["card_name"].isin(inventory_card_name_list)]

        overall_df = overall_df[(min_profit_span * overall_df[currency_1_cheapest_euro]) < overall_df[currency_2_cheapest_euro]]

        overall_df = overall_df[(min_profit_span * overall_df[currency_1_cheapest_euro]) < overall_df[last_24_hours_price]]

        overall_df = overall_df[overall_df[last_30_days_at_least_one_sale] == True]

        overall_df = overall_df.sort_values(by='rel_dif', ascending=False)

        overall_df = overall_df[["card_name", currency_1_cheapest_euro, currency_2_cheapest_euro,
                                 last_24_hours_price, last_7_days_price, last_30_days_price,
                                 "rel_dif", "t_dif",
                                 last_24_hours_price_change, last_7_days_price_change, last_30_days_price_change,
                                 last_24_hours_sales, last_7_days_sales,
                                 "win_4_w",
                                 currency_1_order_id, currency_1_cheapest, currency_2_cheapest]]

        ###

        classification_dic = {}
        classification_dic["purchase_currency"] = purchase_currency
        classification_dic["sale_currency"] = sale_currency
        classification_dic["max_price"] = max_price
        classification_dic["quality"] = quality

        classification_dic["min_profit_span"] = min_profit_span

        classification_dic["last_24_hours_price_above_profit_span"] = True

        classification_dic["last_30_days_at_least_one_sale"] = True

        return overall_df, classification_dic
