
class WinRateEntry:
    """
    A class representing the win_rate information associated with one game
    """

    def __init__(self, user_id, user_rank, time_finished, day_finished, unix_time_finished, god, card_list, status):
        """
        The constructor of the WinRateEntry
        :param user_id: the id of the user involved in the game
        :param user_rank: the rank of the user
        :param time_finished: the timestamp when the game was finished
        :param day_finished: the day when the game was finished
        :param unix_time_finished: the unix timestamp when the game was finished
        :param god: the god used by the user (specific to gods unchained)
        :param card_list: the list of the cards used
        :param status: the status of the game
        """
        self.user_id = user_id
        self.user_rank = user_rank

        self.time_finished = time_finished
        self.day_finished = day_finished

        self.unix_time_finished = unix_time_finished
        self.god = god
        self.card_list = card_list
        self.status = status

    def to_string(self):
        """
        A method to convert one WinRateEntry class to string for printing
        :return:
        """
        return '{' + f"""
        user_id = {self.user_id}
        user_rank = {self.user_rank}
        time_finished = {self.time_finished}
        day_finished = {self.day_finished}
        unix_time_finished = {self.unix_time_finished}
        god = {self.god}
        card_list = {self.card_list}
        status = {self.status}
        """ + '}'