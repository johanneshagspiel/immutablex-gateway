import json
import os

import pytz

from objects.win_rate.win_rate_administrator import Win_Rate_Administrator
from parallel_workers.parallel_rank_downloader import Parallel_Rank_Downloader
from parallel_workers.parallel_win_rate_start_time_downloader import Parallel_Win_Rate_Start_Time_Downloader
from datetime import datetime, timedelta

from util.files.file_handler import File_Handler
from util.helpers import Task_To_Console_Printer, Safe_Datetime_Converter
from util.to_download_list_creator import To_Download_List_Creator


class Gods_Unchained_Winrate_Poller():

    def __init__(self):
        self.pwrstd = Parallel_Win_Rate_Start_Time_Downloader()
        self.prk = Parallel_Rank_Downloader()


    def download_latest_winrate(self):

        winrate_info_raw_restart_path = File_Handler.get_base_path("card_win_rate_restart_info")

        if os.path.isfile(winrate_info_raw_restart_path):

            with open(winrate_info_raw_restart_path, 'r', encoding='utf-8') as winrate_info_raw_restart_file:
                start_time_stamp_str = winrate_info_raw_restart_file.readline()
            winrate_info_raw_restart_file.close()

            start_time_stamp = Safe_Datetime_Converter.string_to_datetime(start_time_stamp_str)

        else:
            current_time_utc = datetime.utcnow()
            start_time_stamp = current_time_utc - timedelta(days=62) - timedelta(hours=current_time_utc.hour) - timedelta(minutes=current_time_utc.minute) - timedelta(seconds=current_time_utc.second) - timedelta(microseconds=current_time_utc.microsecond)

        not_caught_up_to_now = True

        print(f"Downloading WIN_RATE")

        while not_caught_up_to_now:

            current_time_stamp = datetime.utcnow()

            difference = (current_time_stamp - start_time_stamp).total_seconds()
            if difference > 60:

                time_stamp_str_list, next_start_time_stamp_str, new_not_caught_up_to_now = To_Download_List_Creator.create_timestamp_list(start_time_stamp, current_time_stamp, "download_win_rate")

                start_time_stamp_str = Safe_Datetime_Converter.datetime_to_string(start_time_stamp)

                Task_To_Console_Printer.print_downloading_task_info(status_string="WIN_RATE", get_type_string=None, from_str=start_time_stamp_str, to_str=time_stamp_str_list[-1][1])

                win_rate_list = self.pwrstd.parallel_download_win_rate(time_stamp_str_list)

                win_rate_list = sorted(win_rate_list, key= lambda x: x.unix_time_finished, reverse=False)

                Task_To_Console_Printer.print_writing_warning("win_rate", get_type_string=None)

                Win_Rate_Administrator.receive_winrate_list(win_rate_list, next_start_time_stamp_str)

                not_caught_up_to_now = new_not_caught_up_to_now
                start_time_stamp = Safe_Datetime_Converter.string_to_datetime(next_start_time_stamp_str)


            else:
                not_caught_up_to_now = False

        self._add_new_user_to_user_dic()


        current_time_local = datetime.now()
        current_time_utc = current_time_local.astimezone(pytz.utc).isoformat().replace("+00:00", "Z").split('T')[1]

        print(f"{current_time_utc}: Finished Downloading WIN_RATE")


    def _add_new_user_to_user_dic(self):

        user_dic_path = File_Handler.get_base_path("user_ranking_dic")

        if os.path.isfile(user_dic_path):

            with open(user_dic_path, 'r', encoding='utf-8') as user_dic_file:
                user_dic = json.load(user_dic_file)
            user_dic_file.close()

        else:
            user_dic = {}

        user_id_list = Win_Rate_Administrator.create_user_id_list()
        for user_id in user_id_list:
            user_id_str = str(user_id)

            if user_id_str not in user_dic:
                user_dic[user_id_str] = -1

        with open(user_dic_path, 'w', encoding='utf-8') as user_dic_file:
            json.dump(user_dic, user_dic_file, ensure_ascii=False, indent=4)
        user_dic_file.close()

        new_user_id_list = []
        for user_id, rank in user_dic.items():
            if rank == -1:
                new_user_id_list.append(user_id)

        check_more = True
        start_position = 0
        one_time_download_amount = 15

        if len(new_user_id_list) > one_time_download_amount:
            end_position = one_time_download_amount
        else:
            end_position = len(new_user_id_list)

        while check_more:

            if end_position == len(new_user_id_list):
                check_more = False

            next_portion_check = new_user_id_list[start_position:end_position]

            if len(next_portion_check) > 0:

                end_str = f"to {str(end_position)} out of {str(len(new_user_id_list))}"

                Task_To_Console_Printer.print_downloading_task_info(status_string="USER_RANK", get_type_string=None, from_str=str(start_position), to_str=end_str)

                rank_dic = self.prk.parallel_download_rank(next_portion_check)

                for user_id, rank in rank_dic.items():
                    new_entry = {}
                    new_entry["new"] = rank
                    user_dic[user_id] = new_entry

                Task_To_Console_Printer.print_writing_warning(status_str="USER_RANK", get_type_string=None)

                with open(user_dic_path, 'w', encoding='utf-8') as user_dic_file:
                    json.dump(user_dic, user_dic_file, ensure_ascii=False, indent=4)
                user_dic_file.close()

                if len(new_user_id_list) < (end_position + one_time_download_amount):
                    start_position = end_position
                    end_position = len(new_user_id_list)
                else:
                    start_position = end_position
                    end_position = end_position + one_time_download_amount
            else:
                check_more = False


    def _recreate_user_dic(self):

        user_dic_path = File_Handler.get_base_path("user_ranking_dic")

        with open(user_dic_path, 'r', encoding='utf-8') as user_dic_file:
            user_dic = json.load(user_dic_file)
        user_dic_file.close()

        new_user_id_list = []
        for user_id, rank in user_dic.items():
            if rank == -1:
                new_user_id_list.append(user_id)

        check_more = True
        start_position = 0
        one_time_download_amount = 60

        if len(new_user_id_list) > one_time_download_amount:
            end_position = one_time_download_amount
        else:
            end_position = len(new_user_id_list)

        while check_more:

            if end_position == len(new_user_id_list):
                check_more = False

            next_portion_check = new_user_id_list[start_position:end_position]

            if len(next_portion_check) > 0:

                end_str = f"to {str(end_position)} out of {str(len(new_user_id_list))}"

                Task_To_Console_Printer.print_downloading_task_info(status_string="USER_RANK", get_type_string=None, from_str=str(start_position), to_str=end_str)

                rank_dic = self.prk.parallel_download_rank(next_portion_check)

                for user_id, rank in rank_dic.items():
                    new_entry = {}
                    new_entry["new"] = rank
                    user_dic[user_id] = new_entry

                Task_To_Console_Printer.print_writing_warning(status_str="USER_RANK", get_type_string=None)

                with open(user_dic_path, 'w', encoding='utf-8') as user_dic_file:
                    json.dump(user_dic, user_dic_file, ensure_ascii=False, indent=4)
                user_dic_file.close()

                if len(new_user_id_list) < (end_position + one_time_download_amount):
                    start_position = end_position
                    end_position = len(new_user_id_list)
                else:
                    start_position = end_position
                    end_position = end_position + one_time_download_amount
            else:
                check_more = False



    def update_user_dic_on_friday(self):

        print("Updating Rank of Users")

        user_dic_path = File_Handler.get_base_path("user_ranking_dic")

        if os.path.isfile(user_dic_path) == False:
            print("There is no user_dic to update")

        else:
            with open(user_dic_path, 'r', encoding='utf-8') as user_dic_file:
                user_dic = json.load(user_dic_file)
            user_dic_file.close()

            current_time_local = datetime.now()
            current_time_utc = current_time_local.astimezone(pytz.utc)
            current_day = current_time_utc.isoformat().split('T')[0]

            to_updated_ids = []
            for user_id, rank_dic in user_dic.items():
                if current_day not in rank_dic:
                    to_updated_ids.append(user_id)

            check_more = True
            start_position = 0

            if len(to_updated_ids) > 30:
                end_position = 30
            else:
                end_position = len(to_updated_ids)

            while check_more:

                if end_position == len(to_updated_ids):
                    check_more = False

                next_portion_check = to_updated_ids[start_position:end_position]
                rank_dic = self.prk.parallel_download_rank(next_portion_check)

                for user_id, rank in rank_dic.items():
                    previous_dic = user_dic[user_id]
                    previous_dic[current_day] = rank
                    user_dic[user_id] = previous_dic

                with open(user_dic_path, 'w', encoding='utf-8') as user_dic_file:
                    json.dump(user_dic, user_dic_file, ensure_ascii=False, indent=4)
                user_dic_file.close()

                if len(to_updated_ids) < (end_position + 30):
                    start_position = end_position
                    end_position = len(to_updated_ids)
                else:
                    start_position = end_position
                    end_position = end_position + 30

        print("Finished Updating Rank of Users")
