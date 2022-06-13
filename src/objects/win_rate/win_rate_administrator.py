import json
from datetime import datetime

import pytz

from objects.enums.tasks import Download_Task
from objects.win_rate.win_rate_factory import Win_Rate_Factory
from util.files.file_handler import File_Handler

from util.helpers import Task_To_Console_Printer


class Win_Rate_Administrator():

    def __init__(self):
        None

    @staticmethod
    def receive_winrate_list(winrate_list, next_start_time_stamp_str):

        card_win_rate_rolling_path = File_Handler.get_base_path("card_win_rate_rolling")
        with open(card_win_rate_rolling_path, 'a', encoding='utf-8') as card_win_rate_rolling_file:
            for win_rate_entry in winrate_list:
                json.dump(json.dumps(win_rate_entry.__dict__), card_win_rate_rolling_file, ensure_ascii=False)
                card_win_rate_rolling_file.write("\n")
        card_win_rate_rolling_file.close()

        card_win_rate_to_be_processed_path = File_Handler.get_base_path("card_win_rate_to_be_processed")
        with open(card_win_rate_to_be_processed_path, 'a', encoding='utf-8') as card_win_rate_to_be_processed_file:
            for win_rate_entry in winrate_list:
                json.dump(json.dumps(win_rate_entry.__dict__), card_win_rate_to_be_processed_file, ensure_ascii=False)
                card_win_rate_to_be_processed_file.write("\n")
        card_win_rate_to_be_processed_file.close()

        winrate_info_raw_restart_path = File_Handler.get_base_path("card_win_rate_restart_info")
        with open(winrate_info_raw_restart_path, 'w', encoding='utf-8') as winrate_info_raw_restart_file:
            winrate_info_raw_restart_file.write(next_start_time_stamp_str)
        winrate_info_raw_restart_file.close()



    @staticmethod
    def create_win_rate_to_be_processed_list():

        win_rate_to_be_processed_path = File_Handler.get_base_path("card_win_rate_to_be_processed")

        winrate_json_list = []
        with open(win_rate_to_be_processed_path, 'r', encoding='utf-8') as win_rate_to_be_processed_file:
            for line_index, line in enumerate(win_rate_to_be_processed_file):
                try:
                    line_json = json.loads(json.loads(line))
                    winrate_json_list.append(line_json)
                except:
                    try:
                        line_json = json.loads(line)
                        winrate_json_list.append(line_json)
                    except:
                        print(f"Line Index: {line_index}")
                        print(line)
        win_rate_to_be_processed_file.close()

        winrate_list = []
        for winrate_json in winrate_json_list:
            new_winrate_entry = Win_Rate_Factory.string_to_object(winrate_json)
            winrate_list.append(new_winrate_entry)

        return winrate_list


    @staticmethod
    def create_limited_win_rate_to_be_processed_list(from_index, to_index):

        win_rate_to_be_processed_path = File_Handler.get_base_path("card_win_rate_to_be_processed")

        winrate_json_list = []
        with open(win_rate_to_be_processed_path, 'r', encoding='utf-8') as win_rate_to_be_processed_file:
            for line_index, line in enumerate(win_rate_to_be_processed_file):
                if line_index <= to_index:
                    if line_index >= from_index:
                        try:
                            line_json = json.loads(json.loads(line))
                            winrate_json_list.append(line_json)
                        except:
                            try:
                                line_json = json.loads(line)
                                winrate_json_list.append(line_json)
                            except:
                                print(f"Line Index: {line_index}")
                                print(line)

                elif line_index > to_index:
                    break
            win_rate_to_be_processed_file.close()

        winrate_list = []
        for winrate_json in winrate_json_list:
            new_winrate_entry = Win_Rate_Factory.string_to_object(winrate_json)
            winrate_list.append(new_winrate_entry)

        return winrate_list



    @staticmethod
    def create_user_id_list():

        win_rate_to_be_processed_path = File_Handler.get_base_path("card_win_rate_to_be_processed")

        user_id_list = []
        with open(win_rate_to_be_processed_path, 'r', encoding='utf-8') as win_rate_to_be_processed_file:
            for line_index, line in enumerate(win_rate_to_be_processed_file):
                try:
                    line_json = json.loads(json.loads(line))
                    user_id = line_json["user_id"]
                    user_id_list.append(user_id)
                except:
                    try:
                        line_json = json.loads(line)
                        user_id = line_json["user_id"]
                        user_id_list.append(user_id)
                    except:
                        print(f"Line Index: {line_index}")
                        print(line)
        win_rate_to_be_processed_file.close()

        return user_id_list
