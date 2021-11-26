import requests
import json
from data_base import sqlite_db


def fetch_city_name():
    db = sqlite_db.DBHelper()
    db.setup()
    city = db.get_items()
    return city


def fetch_all_data(city):
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"

    querystring = {"query": city,
                   "locale": "ru_RU", "currency": "RUB"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "9a96ad3166mshcb1e0c50caf0471p18b161jsnc1276688d044"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    all_id = json.loads(response.text)

    return all_id


my_data = []


def fetch_all_id(struct):
    for key in struct.keys():
        if key == "destinationId":
            my_data.append(struct[key])

    for sub_struct in struct.values():
        if isinstance(sub_struct, dict):
            fetch_all_id(sub_struct)
    return my_data


def fetch_hotel_details(number_id):
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": number_id, "pageNumber": "1", "pageSize": "25",
                   "checkIn": "2020-01-08", "checkOut": "2020-01-15", "adults1": "1",
                   "sortOrder": "PRICE", "locale": "ru_RU", "currency": "RUB"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "9a96ad3166mshcb1e0c50caf0471p18b161jsnc1276688d044"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    all_details = json.loads(response.text)

    return all_details


def get_some_data():
    city_name = fetch_city_name()
    hotels_data = fetch_all_data(city_name)
    one_shit = fetch_hotel_details(hotels_data)

    for key, value in one_shit.items():
        if key == "name":
            return value
    for sub_struct in one_shit.values()

