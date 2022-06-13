from datetime import datetime, timedelta
from colorama import Fore, Style
import pytz


class Windows_Path_Helper():

    @staticmethod
    def convert_string_to_legal_windows_path(string):

        illegal_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

        character_list = []
        for character in string:
            if character in illegal_characters:
                ascii_value = ord(character)
                replacement_string = "{asc(" + str(ascii_value) + ")}"
                character_list.append(replacement_string)
            else:
                character_list.append(character)

        cleaned_string = "".join(character_list)
        return cleaned_string


class Future_Helper():

    @staticmethod
    def at_least_one_future_not_done(future_list):

        for future in future_list:
            if future.done():
                return False

        return True

class Result_Collection_Filter():

    @staticmethod
    def get_trade_addresses(order_json):
        address_1 = order_json["sell"]["data"]["token_address"]
        address_2 = order_json["buy"]["data"]["token_address"]

        trade_string = str(address_1) + "_" + str(address_2)

        return trade_string

    @staticmethod
    def is_trade(order_json):

        if ("buy" not in order_json) or ("sell" not in order_json):
            raise Exception(f"What kind of order is this: {order_json}")


        if ("decimals" in order_json["buy"]["data"]) or ("decimals" in order_json["sell"]["data"]):
            return False
        else:
            return True


    @staticmethod
    def belongs_to_gu(order_json):

        if "decimals" in order_json["buy"]["data"]:
            collection_address = order_json["sell"]["data"]["token_address"]

        elif "decimals" in order_json["sell"]["data"]:
            collection_address = order_json["buy"]["data"]["token_address"]

        else:
            print("#")
            print(order_json)
            print("#")
            raise Exception("Collection Filter - belong - where is the collection address")

        return collection_address == "0xacb3c6a43d15b907e8433077b6d38ae40936fe2c"


class Panda_Helper():

    @staticmethod
    def filtering_bot_user_series(x, sorted_bot_dic):

        value_list = list(x.values)
        total_amount = len(value_list)
        total_amount_str = str(total_amount)

        bot_amount = 0

        for value in value_list:
            if value in sorted_bot_dic:
                bot_amount = bot_amount + 1

        value_list = str(bot_amount)
        final_label = value_list + "to" + total_amount_str

        return final_label

    @staticmethod
    def total_sales_in_the_past(day_sale_dic):
        total_sale_count = 0
        if day_sale_dic:
            for sales in day_sale_dic.values():
                total_sale_count = total_sale_count + sales
        return total_sale_count


    @staticmethod
    def days_in_last_x_with_at_least_y_sales(day_sale_dic, amount_of_days, min_sales):

        if day_sale_dic:

            today_utc = datetime.utcnow()

            days_in_last_x_days = []
            for day in range(1, amount_of_days):
                new_day_time_stamp = today_utc - timedelta(days=day)
                new_day_str = new_day_time_stamp.isoformat().split('T')[0]
                days_in_last_x_days.append(new_day_str)

            day_count = 0
            for day in days_in_last_x_days:
                if day in day_sale_dic:
                    sale_amount = day_sale_dic[day]
                    if sale_amount >= min_sales:
                        day_count = day_count + 1

            return day_count == (amount_of_days - 1)

        else:
            return False

class Safe_Datetime_Converter():

    @staticmethod
    def string_to_datetime(datetime_str):

        try:
            datetime_res = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        except Exception as e1:
            try:
                datetime_res = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ")
            except:
                raise Exception(f"Error converting this string: {str(datetime_str)} of type {str(type(datetime_str))}")

        return datetime_res


    @staticmethod
    def datetime_to_string(timestamp):

        try:
            datetime_str = datetime.strftime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        except Exception as e1:
            try:
                datetime_str = datetime.strftime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
            except:
                raise Exception(f"Error converting this timestamp: {str(timestamp)} of type {str(type(timestamp))}")

        return datetime_str



class Task_To_Console_Printer():

    @staticmethod
    def print_downloading_task_info(status_string, get_type_string, from_str, to_str, additional_info=None):

        current_time_local = datetime.now()
        current_time_utc = current_time_local.astimezone(pytz.utc).isoformat().replace("+00:00", "Z").split('T')[1]

        if status_string == "WIN_RATE":
            print(Fore.YELLOW + f"{current_time_utc}" + Style.RESET_ALL + ": Downloading\t" + Fore.YELLOW + "WIN_RATE\t\t" + Style.RESET_ALL + f" from {str(from_str)} to {str(to_str)}")

        elif status_string == "USER_RANK":
            print(Fore.YELLOW + f"{current_time_utc}" + Style.RESET_ALL + ": Downloading\t" + Fore.YELLOW + "USER RANK\t\t" + Style.RESET_ALL + f" from {str(from_str)} to {str(to_str)}")

        elif status_string == "ACTIVE":
            print(Fore.BLUE + f"{current_time_utc}" + Style.RESET_ALL + ": Downloading\t" + Fore.BLUE + f"ACTIVE {str(get_type_string).upper()}\t\t" + Style.RESET_ALL + f" Orders from {str(from_str)} to {str(to_str)}")

        elif status_string == "CANCELLED":
            print(Fore.MAGENTA + f"{current_time_utc}" + Style.RESET_ALL + ": Downloading\t" + Fore.MAGENTA + f"CANCELLED {str(get_type_string).upper()}\t" + Style.RESET_ALL + f" Orders from {str(from_str)} to {str(to_str)}")

        elif status_string == "FILLED":
            print(Fore.GREEN + f"{current_time_utc}" + Style.RESET_ALL + ": Downloading\t" + Fore.GREEN + f"FILLED {str(get_type_string).upper()}\t\t" + Style.RESET_ALL + f" Orders from {str(from_str)} to {str(to_str)}")

        elif status_string == "MISSED":
            print(Fore.CYAN + f"{current_time_utc}" + Style.RESET_ALL + ": Downloading\t" + Fore.LIGHTCYAN_EX + f"MISSED\t\t\t" + Style.RESET_ALL + f" Orders from {str(from_str)} to {str(to_str)} out of {additional_info}")

        elif status_string == "DOUBLE_CHECKED":
            print(Fore.CYAN + f"{current_time_utc}" + Style.RESET_ALL + ": Downloading\t" + Fore.CYAN + f"DOUBLE_CHECKED\t" + Style.RESET_ALL + f" Orders from {str(from_str)} to {str(to_str)} up to {additional_info}")


    @staticmethod
    def print_waiting_task_info(status_string, get_type_string):

        current_time_local = datetime.now()
        current_time_utc = current_time_local.astimezone(pytz.utc).isoformat().replace("+00:00", "Z").split('T')[1]

        if status_string == "WIN_RATE":
            print(Fore.YELLOW + f"{current_time_utc}" + Style.RESET_ALL + ": Task\t\t\t" + Fore.YELLOW + "WIN_RATE\t\t" + Style.RESET_ALL + f" is waiting until something new can be downloaded")

        elif status_string == "USER_RANK":
            print(Fore.YELLOW + f"{current_time_utc}" + Style.RESET_ALL + ": Task\t\t\t" + Fore.YELLOW + "USER RANK\t\t" + Style.RESET_ALL + f" is waiting until something new can be downloaded")

        elif status_string == "ACTIVE":
            print(Fore.BLUE + f"{current_time_utc}" + Style.RESET_ALL + ": Task\t\t\t" + Fore.BLUE + f"ACTIVE {str(get_type_string).upper()}\t\t" + Style.RESET_ALL + f" is waiting until something new can be downloaded")

        elif status_string == "CANCELLED":
            print(Fore.MAGENTA + f"{current_time_utc}" + Style.RESET_ALL + ": Task\t\t\t" + Fore.MAGENTA + f"CANCELLED {str(get_type_string).upper()}\t" + Style.RESET_ALL + f" is waiting until something new can be downloaded")

        elif status_string == "FILLED":
            print(Fore.GREEN + f"{current_time_utc}" + Style.RESET_ALL + ": Task\t\t\t" + Fore.GREEN + f"FILLED {str(get_type_string).upper()}\t\t" + Style.RESET_ALL + f" is waiting until something new can be downloaded")

        elif status_string == "MISSED":
            print(Fore.CYAN + f"{current_time_utc}" + Style.RESET_ALL + ": Task\t\t\t" + Fore.LIGHTCYAN_EX + f"MISSED\t\t\t" + Style.RESET_ALL + f" is waiting until something new can be downloaded")

        elif status_string == "DOUBLE_CHECKED":
            print(Fore.CYAN + f"{current_time_utc}" + Style.RESET_ALL + ": Task\t\t\t" + Fore.CYAN + f"DOUBLE_CHECKED\t" + Style.RESET_ALL + f" is waiting until something new can be downloaded")


    @staticmethod
    def print_writing_warning(status_str, get_type_string):

        current_time_local = datetime.now()
        current_time_utc = current_time_local.astimezone(pytz.utc).isoformat().replace("+00:00", "Z").split('T')[1]

        if status_str == "WIN_RATE":
            print(Fore.RED + f"{current_time_utc}" + Style.RESET_ALL + ": Writing\t\t" + Fore.RED + "WIN_RATE" + Style.RESET_ALL)

        elif status_str == "USER_RANK":
            print(Fore.RED + f"{current_time_utc}" + Style.RESET_ALL + ": Writing\t\t" + Fore.RED + "USER_RANK" + Style.RESET_ALL)

        elif status_str == "ACTIVE":
            print(Fore.RED + f"{current_time_utc}" + Style.RESET_ALL + ": Writing\t\t" + Fore.RED + f"{status_str.upper()} {get_type_string.upper()}\t\t" + Style.RESET_ALL + f" Orders")

        elif status_str == "FILLED":
            print(Fore.RED + f"{current_time_utc}" + Style.RESET_ALL + ": Writing\t\t" + Fore.RED + f"{status_str.upper()} {get_type_string.upper()}\t\t" + Style.RESET_ALL + f" Orders")

        elif status_str == "CANCELLED":
            print(Fore.RED + f"{current_time_utc}" + Style.RESET_ALL + ": Writing\t\t" + Fore.RED + f"{status_str.upper()} {get_type_string.upper()}\t" + Style.RESET_ALL + f" Orders")

        elif status_str == "MISSED":
            print(Fore.RED + f"{current_time_utc}" + Style.RESET_ALL + ": Writing\t\t" + Fore.RED + f"{status_str.upper()}\t\t\t" + Style.RESET_ALL + f" Orders")

        elif status_str == "DOUBLE_CHECKED":
            print(Fore.RED + f"{current_time_utc}" + Style.RESET_ALL + ": Writing\t\t" + Fore.RED + f"{status_str.upper()}\t" + Style.RESET_ALL + f" Orders")


    @staticmethod
    def print_finished_task_info(status_str, get_type_string):

            current_time_local = datetime.now()
            current_time_utc = current_time_local.astimezone(pytz.utc).isoformat().replace("+00:00", "Z").split('T')[1]

            if status_str == "WIN_RATE":
                print(Fore.RED + f"{current_time_utc}" + Style.RESET_ALL + ": Finished with\t" + Fore.RED + "WIN_RATE" + Style.RESET_ALL)

            elif status_str == "USER_RANK":
                print(Fore.RED + f"{current_time_utc}" + Style.RESET_ALL + ": Finished with\t" + Fore.RED + "USER_RANK" + Style.RESET_ALL)

            elif status_str == "ACTIVE":
                print(Fore.RED + f"{current_time_utc}" + Style.RESET_ALL + ": Finished with\t" + Fore.RED + f"{status_str.upper()} {get_type_string.upper()}\t\t" + Style.RESET_ALL + f" Orders")

            elif status_str == "FILLED":
                print(Fore.RED + f"{current_time_utc}" + Style.RESET_ALL + ": Finished with\t" + Fore.RED + f"{status_str.upper()} {get_type_string.upper()}\t\t" + Style.RESET_ALL + f" Orders")

            elif status_str == "CANCELLED":
                print(Fore.RED + f"{current_time_utc}" + Style.RESET_ALL + ": Finished with\t" + Fore.RED + f"{status_str.upper()} {get_type_string.upper()}\t" + Style.RESET_ALL + f" Orders")

            elif status_str == "MISSED":
                print(Fore.RED + f"{current_time_utc}" + Style.RESET_ALL + ": Finished with\t" + Fore.RED + f"{status_str.upper()}\t\t\t" + Style.RESET_ALL + f" Orders")

            elif status_str == "DOUBLE_CHECKED":
                print(Fore.RED + f"{current_time_utc}" + Style.RESET_ALL + ": Finished with\t" + Fore.RED + f"{status_str.upper()}\t" + Style.RESET_ALL + f" Orders")
