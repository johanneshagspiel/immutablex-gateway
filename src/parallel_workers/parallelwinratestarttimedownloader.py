import concurrent.futures
import json
from time import mktime
import pytz
import requests
from datetime import datetime
from src.util.custom_exceptions import TooManyAPICalls
from src.util.helpers import SafeDatetimeConverter


class ParallelWinRateStartTimeDownloader:
    """
    A class to parallel download win-rate based on a start time
    """

    def __init__(self):
        """
        The constructor of the ParallelWinRateStartTimeDownloader class
        """
        self._shut_down = False


    def parallel_download_win_rate(self, time_stamp_str_list):
        """
        A method to parallel download win-rate
        :param time_stamp_str_list:
        :return:
        """
        connections = len(time_stamp_str_list)
        result = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=connections) as executor:
            future_win_rate = (executor.submit(self._load_win_rate, from_time_stamp_str, to_time_stamp_str) for (from_time_stamp_str, to_time_stamp_str) in time_stamp_str_list)
            for future in concurrent.futures.as_completed(future_win_rate):
                try:
                    data = future.result()
                    result.append(data)
                except Exception as e:
                    raise

                if self._shut_down:
                    executor.shutdown(wait=False, cancel_futures=True)

        flattened_result = [item for sublist in result for item in sublist]

        return flattened_result


    def _load_win_rate(self, from_time_stamp_str, to_time_stamp_str):

        range_start_time_stamp = SafeDatetimeConverter.string_to_datetime(from_time_stamp_str)
        range_end_time_stamp = SafeDatetimeConverter.string_to_datetime(to_time_stamp_str)

        range_start_time_unix = int(str(mktime(range_start_time_stamp.timetuple())).split('.')[0])
        range_end_time_unix = int(str(mktime(range_end_time_stamp.timetuple())).split('.')[0])

        range = str(range_start_time_unix) + "-" + str(range_end_time_unix)

        url = f"https://api.godsunchained.com/v0/match?end_time={range}&perPage=99999999999999"

        try:
            response = requests.request("GET", url)

            if response.status_code == 429:
                raise TooManyAPICalls()

            else:
                parsed = json.loads(response.text)

                result = []

                if "records" in parsed:
                    if parsed["records"] != None:

                        for game in parsed["records"]:

                            if int(game["game_mode"]) == 13:

                                timestamp_finished = game["end_time"]
                                time_finished = datetime.fromtimestamp(int(timestamp_finished)).isoformat()
                                day_finished = time_finished.split('T')[0]

                                status_dic = {}
                                status_dic[game["player_won"]] = "winner"
                                status_dic[game["player_lost"]] = "loser"

                                player_info_list = game["player_info"]

                                for player in player_info_list:

                                    user_id = player["user_id"]
                                    user_rank = None
                                    god = player["god"]
                                    card_list = player["cards"]
                                    status = status_dic[user_id]

                                    WinRateEntry = WinRateEntry(user_id, user_rank, time_finished, day_finished, timestamp_finished, god, card_list, status)

                                    result.append(WinRateEntry)
                else:

                    current_time_local = datetime.now()
                    current_time_utc = current_time_local.astimezone(pytz.utc)
                    current_time_unix = int(str(mktime(current_time_utc.timetuple())).split('.')[0])

                    print("#")
                    print("win_rate_no_records_in_parsed")
                    print(current_time_utc)
                    print(current_time_unix)
                    print(parsed)
                    print("#")

                return result

        except requests.exceptions.ConnectionError as connection_error:
            raise TooManyAPICalls()
        except Exception as e:
            raise e
