import os
import pandas as pd
from src.operators.datacreator import DataCreator
from src.objects.orders.gods_unchained.orderadministratorgu import OrderAdministratorGU
from src.operators.helpers.file_helpers import Processing_File_Helper
from src.util.files.fileiohelper import FileIoHelper
from datetime import datetime
from src.util.helpers import SafeDatetimeConverter


class ErrorHandler:
    """
    A class to conduct error checks
    """

    def __init__(self):
        """
        The constructor of the ErrorHandler class
        """
        pass

    @staticmethod
    def start_up_check():
        """
        A method to check the files at start_up
        :return: None
        """
        ErrorHandler.check_processing_logs()

    @staticmethod
    def check_processing_logs():
        """
        A method to check the download log files and rectify errors if encountered
        :return: None
        """
        processing_logs_dic = FileIoHelper.load_processing_logs()

        get_type_string = "SELL"

        if processing_logs_dic["processing_updated_active_orders"] == "started":

            print("Handling previous error with processing_updated_active_orders")

            active_orders_to_be_processed_order_path_list = Processing_File_Helper.get_path_list_for_type_order_processing(get_type_string=get_type_string, status_string="active")
            active_orders_to_be_processed_exist = len(active_orders_to_be_processed_order_path_list) > 0
            if active_orders_to_be_processed_exist:
                print("Creating Active Orders To Be Processed DF")
                start_time = datetime.now()
                additional_active_orders_df = OrderAdministratorGU.create_df_from_path_list(active_orders_to_be_processed_order_path_list)

                processing_logs_dic["active_to_be_processed"] = "started"
                processing_logs_dic["processing_updated_active_orders"] = "started"
                processing_logs_dic["creating_info_active_orders"] = "started"
                FileIoHelper.write_processing_logs(processing_logs_dic)

                print(f"t: {(datetime.now() - start_time).total_seconds()}")

            filled_orders_to_be_processed_order_path_list = Processing_File_Helper.get_path_list_for_type_order_processing(get_type_string=get_type_string, status_string="filled")
            filled_orders_to_be_processed_exist = len(filled_orders_to_be_processed_order_path_list) > 0
            if filled_orders_to_be_processed_exist:
                print("Determining Filled Orders ID")
                start_time = datetime.now()
                filled_orders_to_be_processed_order_list = OrderAdministratorGU.create_order_list_from_path_list(
                    filled_orders_to_be_processed_order_path_list)

                filled_orders_to_be_processed_id = [order.order_id for order in filled_orders_to_be_processed_order_list]

                processing_logs_dic["processing_today_timeline"] = "started"
                processing_logs_dic["processing_baseline_timeline"] = "started"

                processing_logs_dic["filled_to_be_processed"] = "started"
                processing_logs_dic["processing_updated_active_orders"] = "started"
                processing_logs_dic["creating_info_active_orders"] = "started"
                FileIoHelper.write_processing_logs(processing_logs_dic)

                print(f"t: {(datetime.now() - start_time).total_seconds()}")

            cancelled_orders_to_be_processed_order_path_list = Processing_File_Helper.get_path_list_for_type_order_processing(get_type_string=get_type_string, status_string="cancelled")
            cancelled_orders_to_be_processed_exist = len(cancelled_orders_to_be_processed_order_path_list) > 0
            if cancelled_orders_to_be_processed_exist:
                print("Determining Cancelled Orders ID")
                start_time = datetime.now()
                cancelled_orders_to_be_processed_order_list = OrderAdministratorGU.create_order_list_from_path_list(cancelled_orders_to_be_processed_order_path_list)
                cancelled_orders_to_be_processed_id = [order.order_id for order in cancelled_orders_to_be_processed_order_list]

                processing_logs_dic["cancelled_to_be_processed"] = "started"
                processing_logs_dic["processing_updated_active_orders"] = "started"
                processing_logs_dic["creating_info_active_orders"] = "started"
                FileIoHelper.write_processing_logs(processing_logs_dic)

                print(f"t: {(datetime.now() - start_time).total_seconds()}")

            inactive_orders_to_be_processed_order_path_list = Processing_File_Helper.get_path_list_for_type_order_processing(get_type_string=get_type_string, status_string="inactive")
            inactive_orders_to_be_processed_exist = len(inactive_orders_to_be_processed_order_path_list) > 0
            if inactive_orders_to_be_processed_exist:
                print("Determining Inactive Orders ID")
                start_time = datetime.now()
                inactive_orders_to_be_processed_order_list = OrderAdministratorGU.create_order_list_from_path_list(inactive_orders_to_be_processed_order_path_list)
                inactive_orders_to_be_processed_id = [order.order_id for order in inactive_orders_to_be_processed_order_list]

                processing_logs_dic["inactive_to_be_processed"] = "started"
                processing_logs_dic["processing_updated_active_orders"] = "started"
                processing_logs_dic["creating_info_active_orders"] = "started"
                FileIoHelper.write_processing_logs(processing_logs_dic)

                print(f"t: {(datetime.now() - start_time).total_seconds()}")

            expired_orders_to_be_processed_order_path_list = Processing_File_Helper.get_path_list_for_type_order_processing(get_type_string=get_type_string, status_string="expired")
            expired_orders_to_be_processed_exist = len(expired_orders_to_be_processed_order_path_list) > 0
            if expired_orders_to_be_processed_exist:
                print("Determining Expired Orders ID")
                start_time = datetime.now()
                expired_orders_to_be_processed_order_list = OrderAdministratorGU.create_order_list_from_path_list(expired_orders_to_be_processed_order_path_list)
                expired_orders_to_be_processed_id = [order.order_id for order in expired_orders_to_be_processed_order_list]

                processing_logs_dic["expired_to_be_processed"] = "started"
                processing_logs_dic["processing_updated_active_orders"] = "started"
                processing_logs_dic["creating_info_active_orders"] = "started"
                FileIoHelper.write_processing_logs(processing_logs_dic)

                print(f"t: {(datetime.now() - start_time).total_seconds()}")

            if active_orders_to_be_processed_exist or cancelled_orders_to_be_processed_exist \
                    or filled_orders_to_be_processed_exist or inactive_orders_to_be_processed_exist or expired_orders_to_be_processed_exist:

                print("Loading Previous Updated Active Sell Orders")
                start_time = datetime.now()
                active_updated_orders_df = OrderAdministratorGU.create_active_updated_orders_df(get_type_string="SELL")
                print(f"t: {(datetime.now() - start_time).total_seconds()}")

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
                active_updated_orders_df = active_updated_orders_df[~active_updated_orders_df["order_id"].isin(combined_id_list)]

                print(f"t: {(datetime.now() - start_time).total_seconds()}")

                print("Filtering Out Duplicate Active Orders")
                start_time = datetime.now()
                active_updated_orders_df.sort_values(by=["token_id", "updated_timestamp"], ascending=False)
                active_updated_orders_df.drop_duplicates(subset=["token_id"], keep="first")

                print(f"t: {(datetime.now() - start_time).total_seconds()}")

                print("Writing Updated Orders List to File")
                start_time = datetime.now()
                OrderAdministratorGU.write_updated_active_sell_order_df_to_file(active_updated_orders_df)

                now_timestamp_str = SafeDatetimeConverter.datetime_to_string(datetime.utcnow())
                FileIoHelper.write_updated_active_sell_orders_timestamp(now_timestamp_str)

                processing_logs_dic["processing_updated_active_orders"] = "finished"
                FileIoHelper.write_processing_logs(processing_logs_dic)

                print(f"t: {(datetime.now() - start_time).total_seconds()}")
            print(" ")

        if processing_logs_dic["processing_baseline_timeline"] == "started":

            print("Handling previous error with processing_baseline_timeline")

            print("Creating Filled Orders List")
            start_time = datetime.now()
            filled_orders_to_be_processed_order_list = Processing_File_Helper.get_order_list_for_type_order_processing(get_type_string=get_type_string, status_string="filled")
            print(f"t: {(datetime.now() - start_time).total_seconds()}")

            print("Determining Covered Month - Year")
            start_time = datetime.now()
            year_month_list = DataCreator.determine_year_month_orders_downloaded(filled_orders_to_be_processed_order_list)
            print(f"t: {(datetime.now() - start_time).total_seconds()}")

            print("Loading Previous Filled Order Timeline Dic")
            start_time = datetime.now()
            previous_filled_orders_dic = FileIoHelper.load_filled_order_timeline_dic(year_month_list)
            print(f"t: {(datetime.now() - start_time).total_seconds()}")

            print("Updating Base Line Filled Orders Timeline")
            start_time = datetime.now()
            new_filled_order_timeline_dic = DataCreator.update_base_line_filled_order_timeline(filled_orders_to_be_processed_order_list, previous_filled_orders_dic)
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
            print(" ")

        if processing_logs_dic["processing_today_timeline"] == "started":

            print("Handling previous error with processing_today_timeline")

            print("Creating Filled Orders List")
            start_time = datetime.now()
            filled_orders_to_be_processed_order_list = Processing_File_Helper.get_order_list_for_type_order_processing(get_type_string=get_type_string, status_string="filled")
            print(f"t: {(datetime.now() - start_time).total_seconds()}")

            print("Loading Today Filled Order Timeline Dic")
            start_time = datetime.now()
            today_filled_order_timeline_dic = FileIoHelper.load_today_filled_order_timeline_dic()
            print(f"t: {(datetime.now() - start_time).total_seconds()}")

            print("Updating Today Filled Orders Timeline")
            start_time = datetime.now()
            new_today_filled_order_timeline_dic = DataCreator.update_today_filled_sales(filled_orders_to_be_processed_order_list,today_filled_order_timeline_dic)
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
            print(" ")

        # if processing_logs_dic["card_win_rate_to_be_processed"] == "started":
        #
        #     print("Handling previous error with card_win_rate_to_be_processed")
        #     start_time = datetime.now()
        #
        #     win_rate_to_be_processed_list = WinRateAdministrator.create_win_rate_to_be_processed_list()
        #     DataCreator.update_win_rate_month_overview(win_rate_to_be_processed_list)
        #     DataCreator.create_win_rate_info()
        #
        #     card_win_rate_to_be_processed_file_path = File_Handler.get_base_path("card_win_rate_to_be_processed")
        #     os.remove(card_win_rate_to_be_processed_file_path)
        #
        #     processing_logs_dic["card_win_rate_to_be_processed"] = "finished"
        #     File_IO_Helper.write_processing_logs(processing_logs_dic)
        #
        #     print(f"t: {(datetime.now() - start_time).total_seconds()}")
        #     print(" ")

        if processing_logs_dic["creating_info_active_orders"] == "started":

            print("Handling previous error with creating_info_active_orders")

            print("Loading Previous Updated Active Sell Orders")
            start_time = datetime.now()
            active_updated_orders_df = OrderAdministratorGU.create_active_updated_orders_df(get_type_string="SELL")
            print(f"t: {(datetime.now() - start_time).total_seconds()}")

            print("Creating Updated Orders Info")
            start_time = datetime.now()
            DataCreator.create_info_for_active_orders(active_updated_orders_df, "ETH", "GODS", 1)

            processing_logs_dic["creating_info_active_orders"] = "finished"
            FileIoHelper.write_processing_logs(processing_logs_dic)

            print(f"t: {(datetime.now() - start_time).total_seconds()}")
            print(" ")

        if processing_logs_dic["active_to_be_processed"] == "started":

            print("Handling previous error with active_to_be_processed")

            for path in active_orders_to_be_processed_order_path_list:
                os.remove(path)
            processing_logs_dic["active_to_be_processed"] = "finished"
            FileIoHelper.write_processing_logs(processing_logs_dic)
            print(" ")

        if processing_logs_dic["filled_to_be_processed"] == "started":

            print("Handling previous error with filled_to_be_processed")

            for path in filled_orders_to_be_processed_order_path_list:
                os.remove(path)
            processing_logs_dic["filled_to_be_processed"] = "finished"
            FileIoHelper.write_processing_logs(processing_logs_dic)
            print(" ")

        if processing_logs_dic["cancelled_to_be_processed"] == "started":

            print("Handling previous error with cancelled_to_be_processed")

            for path in cancelled_orders_to_be_processed_order_path_list:
                os.remove(path)
            processing_logs_dic["cancelled_to_be_processed"] = "finished"
            FileIoHelper.write_processing_logs(processing_logs_dic)
            print(" ")

        if processing_logs_dic["inactive_to_be_processed"] == "started":

            print("Handling previous error with inactive_to_be_processed")

            for path in inactive_orders_to_be_processed_order_path_list:
                os.remove(path)
            processing_logs_dic["inactive_to_be_processed"] = "finished"
            FileIoHelper.write_processing_logs(processing_logs_dic)
            print(" ")

        if processing_logs_dic["expired_to_be_processed"] == "started":

            print("Handling previous error with expired_to_be_processed")

            for path in expired_orders_to_be_processed_order_path_list:
                os.remove(path)
            #Processing_File_Helper.delete_to_be_processed_orders(get_type_string=get_type_string, status_string="expired")
            processing_logs_dic["expired_to_be_processed"] = "finished"
            FileIoHelper.write_processing_logs(processing_logs_dic)
            print(" ")
