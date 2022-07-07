import json
from src.objects.win_rate.winratefactory import WinRateFactory
from src.util.files.filehandler import FileHandler


class WinRateAdministrator:
    """
    A class to handle and store downloaded win_rate information
    """

    def __init__(self):
        """
        The constructor of the WinRateAdministrator class
        """
        pass

    @staticmethod
    def receive_winrate_list(winrate_list, next_start_time_stamp_str):
        """
        A method to store downloaded win_rate information appropriately
        :param winrate_list: the downloaded win_rate list
        :param next_start_time_stamp_str: the next timestamp to be downloaded
        :return: None
        """

        card_win_rate_rolling_path = FileHandler.get_base_path("card_win_rate_rolling")
        with open(card_win_rate_rolling_path, 'a', encoding='utf-8') as card_win_rate_rolling_file:
            for WinRateEntry in winrate_list:
                json.dump(json.dumps(WinRateEntry.__dict__), card_win_rate_rolling_file, ensure_ascii=False)
                card_win_rate_rolling_file.write("\n")
        card_win_rate_rolling_file.close()

        card_win_rate_to_be_processed_path = FileHandler.get_base_path("card_win_rate_to_be_processed")
        with open(card_win_rate_to_be_processed_path, 'a', encoding='utf-8') as card_win_rate_to_be_processed_file:
            for WinRateEntry in winrate_list:
                json.dump(json.dumps(WinRateEntry.__dict__), card_win_rate_to_be_processed_file, ensure_ascii=False)
                card_win_rate_to_be_processed_file.write("\n")
        card_win_rate_to_be_processed_file.close()

        winrate_info_raw_restart_path = FileHandler.get_base_path("card_win_rate_restart_info")
        with open(winrate_info_raw_restart_path, 'w', encoding='utf-8') as winrate_info_raw_restart_file:
            winrate_info_raw_restart_file.write(next_start_time_stamp_str)
        winrate_info_raw_restart_file.close()

    @staticmethod
    def create_win_rate_to_be_processed_list():
        """
        Create a list of the win_rate information that still has to be processed
        :return: the list of WinRateEntry
        """

        win_rate_to_be_processed_path = FileHandler.get_base_path("card_win_rate_to_be_processed")

        winrate_json_list = []
        with open(win_rate_to_be_processed_path, 'r', encoding='utf-8') as win_rate_to_be_processed_file:
            for line_index, line in enumerate(win_rate_to_be_processed_file):
                try:
                    line_json = json.loads(json.loads(line))
                    winrate_json_list.append(line_json)
                except Exception:
                    try:
                        line_json = json.loads(line)
                        winrate_json_list.append(line_json)
                    except Exception:
                        print(f"Line Index: {line_index}")
                        print(line)
        win_rate_to_be_processed_file.close()

        winrate_list = []
        for winrate_json in winrate_json_list:
            new_winrate_entry = WinRateFactory.string_to_object(winrate_json)
            winrate_list.append(new_winrate_entry)

        return winrate_list

    @staticmethod
    def create_limited_win_rate_to_be_processed_list(from_index, to_index):
        """
        A method to create a list of to be processed win_rate information based on a start and end index
        :param from_index: the from_index
        :param to_index: the to_index
        :return: a list of WinRateEntry
        """

        win_rate_to_be_processed_path = FileHandler.get_base_path("card_win_rate_to_be_processed")

        winrate_json_list = []
        with open(win_rate_to_be_processed_path, 'r', encoding='utf-8') as win_rate_to_be_processed_file:
            for line_index, line in enumerate(win_rate_to_be_processed_file):
                if line_index <= to_index:
                    if line_index >= from_index:
                        try:
                            line_json = json.loads(json.loads(line))
                            winrate_json_list.append(line_json)
                        except Exception:
                            try:
                                line_json = json.loads(line)
                                winrate_json_list.append(line_json)
                            except Exception:
                                print(f"Line Index: {line_index}")
                                print(line)

                elif line_index > to_index:
                    break
            win_rate_to_be_processed_file.close()

        winrate_list = []
        for winrate_json in winrate_json_list:
            new_winrate_entry = WinRateFactory.string_to_object(winrate_json)
            winrate_list.append(new_winrate_entry)

        return winrate_list

    @staticmethod
    def create_user_id_list():
        """
        A method to create a list of the order id of all users
        :return: a list of order ids
        """

        win_rate_to_be_processed_path = FileHandler.get_base_path("card_win_rate_to_be_processed")

        user_id_list = []
        with open(win_rate_to_be_processed_path, 'r', encoding='utf-8') as win_rate_to_be_processed_file:
            for line_index, line in enumerate(win_rate_to_be_processed_file):
                try:
                    line_json = json.loads(json.loads(line))
                    user_id = line_json["user_id"]
                    user_id_list.append(user_id)
                except Exception:
                    try:
                        line_json = json.loads(line)
                        user_id = line_json["user_id"]
                        user_id_list.append(user_id)
                    except Exception:
                        print(f"Line Index: {line_index}")
                        print(line)
        win_rate_to_be_processed_file.close()

        return user_id_list
