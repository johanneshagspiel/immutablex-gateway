import concurrent.futures
import json
import requests
from src.util.custom_exceptions import TooManyAPICalls


class ParallelRankDownloader:
    """
    A class to parallel download ranks
    """

    def __init__(self):
        """
        The constructor of the ParallelRankDownloader class
        """
        self._shut_down = False


    def parallel_download_rank(self, user_id_list):
        """
        A method to parallel download ranks
        :param user_id_list: a list of user ids for whom to download the rank
        :return: the result
        """

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
        """
        A method to download the rank of one user
        :param user_id: the id of the user to be downloaded
        :return: None
        """

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
