
class URL_Analyzer():

    def __init__(self):
        None

    @staticmethod
    def analyze_url(url):
        info_part = url.split('?', maxsplit=1)[1]
        sections = info_part.split('&')

        url_info_dic = {}
        info_str = ""
        info_dic = {}

        if len(sections) > 1:
            for section in sections:
                key = section.split("=")[0]
                value = section.split("=")[1]
                url_info_dic[key] = value

            if "status" in url_info_dic:
                status_str = str(url_info_dic["status"])
                info_str = info_str + status_str + " orders"
                info_dic["status"] = status_str
            else:
                info_dic["status"] = "double_checked"

            if "buy_token_address" in url_info_dic:
                info_dic["type"] = "buy"

            if "sell_token_address" in url_info_dic:
                info_dic["type"] = "sell"

            if "updated_min_timestamp" in url_info_dic:
                from_str = str(url_info_dic["updated_min_timestamp"])
                info_str = info_str + " from " + from_str
                info_dic["from"] = from_str

            if "updated_max_timestamp" in url_info_dic:
                to_str = str(url_info_dic["updated_max_timestamp"])
                info_str = info_str + " to " + to_str
                info_dic["to"] = to_str

            if "min_timestamp" in url_info_dic:
                from_str = str(url_info_dic["min_timestamp"])
                info_str = info_str + " from " + from_str
                info_dic["from"] = from_str

            if "max_timestamp" in url_info_dic:
                to_str = str(url_info_dic["max_timestamp"])
                info_str = info_str + " to " + to_str
                info_dic["to"] = to_str

        return info_str, info_dic