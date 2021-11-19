# import requests
# import json
from data_base import sqlite_db


db = sqlite_db.DBHelper


def foo():
    db.get_items()

# url = "https://hotels4.p.rapidapi.com/locations/v2/search"

# querystring = {"query": "Санкт-Петербург",
#                "locale": "en_US", "currency": "USD"}

# headers = {
#     'x-rapidapi-host': "hotels4.p.rapidapi.com",
#     'x-rapidapi-key': "9a96ad3166mshcb1e0c50caf0471p18b161jsnc1276688d044"
#     }

# response = requests.request("GET", url, headers=headers, params=querystring)
# all_hotels = json.loads(response.text)

# print(all_hotels)
