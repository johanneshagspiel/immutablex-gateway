
class Win_Rate_Entry():

    def __init__(self, user_id, user_rank, time_finished, day_finished, unix_time_finished, god, card_list, status):
        self.user_id = user_id
        self.user_rank = user_rank

        self.time_finished = time_finished
        self.day_finished = day_finished

        self.unix_time_finished = unix_time_finished
        self.god = god
        self.card_list = card_list
        self.status = status

    def to_string(self):
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