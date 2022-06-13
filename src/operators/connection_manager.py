import json
import random
import statistics
import subprocess
import time
from datetime import datetime

import pytz

from util.files.file_handler import File_Handler
from util.helpers import Safe_Datetime_Converter


class Connection_Manager():

    def __init__(self):

        nordvpn_server_time_and_names_path = File_Handler.get_base_path("nordvpn_server_time_and_names")

        self._server_name_list = []
        with open(nordvpn_server_time_and_names_path, 'r', encoding='utf-8') as nordvpn_server_time_and_names_file:
            self._server_time_and_name_list = json.load(nordvpn_server_time_and_names_file)
        nordvpn_server_time_and_names_file.close()

        self._server_name_list = []
        unnormalized_weight_list = []

        for (server_name, time_list) in self._server_time_and_name_list:
            average_server_up_time = statistics.mean(time_list)

            self._server_name_list.append(server_name)
            unnormalized_weight_list.append(average_server_up_time)

        self._weight_list = [float(unnormalized_weight)/sum(unnormalized_weight_list) for unnormalized_weight in unnormalized_weight_list]


    def switch_ip(self, not_first_time=True):

        if not_first_time:
            print("Switching IP")
        else:
            print("Connecting to a Server")

        disconnect_command = r"""cd "C:\Program Files\NordVPN\" &&nordvpn --d"""
        pipe = subprocess.run(disconnect_command, capture_output=True, shell=True)
        time.sleep(5)


        server_up_time_path = File_Handler.get_base_path("server_up_time")
        nordvpn_server_time_and_names_path = File_Handler.get_base_path("nordvpn_server_time_and_names")

        current_time_local = datetime.now()
        current_time_utc = current_time_local.astimezone(pytz.utc)
        current_day_iso = current_time_utc.isoformat().replace("+00:00", "Z")


        if not_first_time:
            with open(server_up_time_path, 'r', encoding='utf-8') as server_up_time_file:
                previous_server_start_tuple = json.load(server_up_time_file)
            server_up_time_file.close()

            prev_server_name = previous_server_start_tuple[0]
            prev_start_time = previous_server_start_tuple[1]

            prev_start_time_timestamp = Safe_Datetime_Converter.string_to_datetime(prev_start_time)
            current_time_utc_without_timezone_info = current_time_utc.replace(tzinfo=None)
            time_difference = int((current_time_utc_without_timezone_info - prev_start_time_timestamp).total_seconds())

            new_server_time_and_name_list = []
            for (server_name, time_list) in self._server_time_and_name_list:

                if server_name == prev_server_name:
                    new_time_list = time_list
                    new_time_list.append(time_difference)

                    new_entry = (server_name, new_time_list)
                else:
                    new_entry = (server_name, time_list)
                new_server_time_and_name_list.append(new_entry)

            self._server_time_and_name_list = new_server_time_and_name_list
            with open(nordvpn_server_time_and_names_path, 'w', encoding='utf-8') as nordvpn_server_time_and_names_file:
                json.dump(new_server_time_and_name_list, nordvpn_server_time_and_names_file, ensure_ascii=False, indent=4)
            nordvpn_server_time_and_names_file.close()


        next_server_name = random.choices(population=self._server_name_list, weights=self._weight_list, k=1)[0]

        server_start_dic = (next_server_name, current_day_iso)

        with open(server_up_time_path, 'w', encoding='utf-8') as server_up_time_file:
            json.dump(server_start_dic, server_up_time_file, ensure_ascii=False, indent=4)
        server_up_time_file.close()


        command_1 = r"""cd "C:\Program Files\NordVPN\" &&nordvpn -c -n """
        command_2 = '"' + next_server_name + '"'
        command = command_1 + command_2
        pipe = subprocess.run(command, capture_output=True, shell=True)

        time.sleep(10)

        if not_first_time:
            print(f"Changed IP to \"{next_server_name}\"")
        else:
            print(f"Connected to \"{next_server_name}\"")

