from src.objects.win_rate.winrateentry import WinRateEntry


class WinRateFactory:
    """
    A class to create a WinRateEntry
    """

    @staticmethod
    def string_to_object(order_string):
        """
        A metho to convert a string to a WinRateEntry
        :param order_string: the string to be converted
        :return: a WinRateEntry
        """
        user_id = order_string["user_id"]
        user_rank = order_string["user_rank"]
        time_finished = order_string["time_finished"]
        day_finished = order_string["day_finished"]
        unix_time_finished = order_string["unix_time_finished"]
        god = order_string["god"]
        card_list = order_string["card_list"]
        status = order_string["status"]

        WinRateEntry = WinRateEntry(user_id, user_rank, time_finished, day_finished, unix_time_finished, god,
                                      card_list, status)

        return WinRateEntry
