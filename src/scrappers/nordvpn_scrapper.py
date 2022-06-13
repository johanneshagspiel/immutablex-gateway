import json

import requests

from util.files.file_handler import File_Handler


class NordVPN_Scrapper():

    def __init__(self):
        None

    @staticmethod
    def download_server_list():
        url = "https://nordvpn.com/api/server"
        response = requests.request("GET", url)
        parsed = json.loads(response.text)

        server_list = []
        country_list = ["Belgium", "Bulgaria", "Croatia", "Republic of Cyprus", "Czech Republic", "Denmark", "Estonia",
                        "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia", "Lithuania",
                        "Luxembourg", "Netherlands", "Poland", "Portugal", "Romania", "Slovakia",
                        "Slovenia", "Spain", "Sweden"]

        for country in country_list:
            country_results = list(filter(lambda x: x["country"] == country, parsed))
            country_standard_servers = list(
                filter(lambda x: {"name": "Standard VPN servers"} in x["categories"], country_results))
            country_server_names = [x["name"] for x in country_standard_servers]
            server_list.extend(country_server_names)

        storage_path = File_Handler.get_base_path("nordvpn_server_names")

        with open(storage_path, 'w', encoding='utf-8') as server_name_file:
            json.dump(server_list, server_name_file, ensure_ascii=False, indent=4)
        server_name_file.close()