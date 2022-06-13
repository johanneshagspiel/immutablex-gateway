import concurrent.futures
import json
import logging

import requests
import time
from datetime import datetime
from objects.win_rate.win_rate_entry import Win_Rate_Entry
from scrappers.immutable_x_scrapper import Immutable_X_Scrapper
from util.custom_exceptions import TooManyAPICalls, Response_Error


class Parallel_Rank_Downloader():

    def __init__(self):
        self._shut_down = False


    def parallel_download_rank(self, user_id_list):

        connections = len(user_id_list)
        result = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=connections) as executor:

            future_win_rate = (executor.submit(self._load_rank, user_id) for user_id in user_id_list)

            for future in concurrent.futures.as_completed(future_win_rate):
                try:
                    data = future.result()

                    for user_id, rank_level in data.items():
                        result[user_id] = rank_level

                except Exception as e:
                    raise

                if self._shut_down:
                    executor.shutdown(wait=False, cancel_futures=True)

        return result


    def _load_rank(self, user_id):

        url = "https://api.godsunchained.com/v0/rank?user_id=" + str(user_id)

        try:
            response = requests.request("GET", url)

            if response.status_code == 429:
                raise TooManyAPICalls()

            else:
                parsed = json.loads(response.text)

                if parsed["records"] != None:

                    for game_mode in parsed["records"]:
                        if game_mode["game_mode"] == 13:

                            rank_level = game_mode["rank_level"]

                            result = {}
                            result[user_id] = rank_level

                            return result

        except requests.exceptions.ConnectionError as connection_error:
            raise TooManyAPICalls()
        except Exception as e:
            raise e