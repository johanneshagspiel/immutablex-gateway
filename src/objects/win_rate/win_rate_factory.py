from objects.win_rate.win_rate_entry import Win_Rate_Entry


class Win_Rate_Factory():

    @staticmethod
    def string_to_object(order_string):
        user_id = order_string["user_id"]
        user_rank = order_string["user_rank"]
        time_finished = order_string["time_finished"]
        day_finished = order_string["day_finished"]
        unix_time_finished = order_string["unix_time_finished"]
        god = order_string["god"]
        card_list = order_string["card_list"]
        status = order_string["status"]

        win_rate_entry = Win_Rate_Entry(user_id, user_rank, time_finished, day_finished, unix_time_finished, god, card_list, status)

        return win_rate_entry