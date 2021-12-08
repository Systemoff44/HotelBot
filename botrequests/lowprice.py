import requests
import json
from data_base import sqlite_db


def fetch_sqlite_data():
    """Возвращает последние записанные данные из библиотеки sqlite

    Returns:
        (tuple): кортеж из city(город), quantity(количество отелей),
        photo(количесто фотографий)
    """
    db = sqlite_db.DBHelper()
    db.setup()
    city, quantity, photo = db.get_items()
    return city, quantity, photo


def fetch_all_data(city):
    """Парсинг данных по определенному городу 

    Args:
        city (str): город, который ввел пользователь

    Returns:
        (dict): словарь с данными по определенному городу
    """
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"

    querystring = {"query": city,
                   "locale": "ru_RU", "currency": "RUB"}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "9a96ad3166mshcb1e0c50caf0471p18b161jsnc1276688d044"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    all_id = json.loads(response.text)
    # Если "moresuggestions" == 0, то город был введен некоректно, и возвращает None
    if all_id["moresuggestions"] == 0:
        return None
    else:
        return all_id


def fetch_needed_data(struct, key):
    """Проходится по словарю с данными и извлекает все по выбранному ключу

    Args:
        struct (dict): данные полученные парсингом
        key (str): ключ,по которому извлекаются данные из словаря 

    Yields:
        (Any): все данные по ключу
    """
    if isinstance(struct, list):
        for item in struct:
            for second_item in fetch_needed_data(item, key):
                yield second_item
    elif isinstance(struct, dict):
        if key in struct:
            yield struct[key]
        for third_item in struct.values():
            for forth_item in fetch_needed_data(third_item, key):
                yield forth_item


def fetch_hotel_details(number_id):
    """Делает парсинг всех данных по определенному id места

    Args:
        number_id (int): номер id

    Returns:
        (dict): данные с отелями по определенному id места
    """
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

# Парсинг фотографий, пока не работает
# def fetch_hotel_photos():
#     url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

#     querystring = {"id": "599670"}

#     headers = {
#         'x-rapidapi-host': "hotels4.p.rapidapi.com",
#         'x-rapidapi-key': "9a96ad3166mshcb1e0c50caf0471p18b161jsnc1276688d044"
#         }

#     response = requests.request("GET", url, headers=headers, params=querystring)
#     all_photos = json.loads(response.text)

#     return all_photos


def fetch_all_data_from_parsing(all_data, city):
    """Извлечение необходимых данных по каждому отелю из словаря  

    Args:
        all_data (dict): словарь с данными
        city (str): город, необходим для того, чтобы проверить,
        по тому ли городу извлекаются данные

    Yields:
        (tuple): кортеж из названия, адреса, удаленности от центра и цены
    """
    try:
        length = len(all_data["data"]["body"]["searchResults"]["results"])
    except KeyError:
        return
    for index in range(length):
        try:
            # проверка тот ли город в данных
            if all_data["data"]["body"]["searchResults"][
                "results"][index]["address"]["locality"] == city:
                # сбор данных в кортеж
                name = all_data["data"]["body"]["searchResults"]["results"][index]["name"]
                adress = all_data["data"]["body"]["searchResults"]["results"][index]["address"]["streetAddress"]
                center = all_data["data"]["body"]["searchResults"]["results"][index]["landmarks"][0]["distance"]
                price = all_data["data"]["body"]["searchResults"]["results"][index]["ratePlan"]["price"]["exactCurrent"]
                result = (name, adress, center, price)
                yield result
            else:
                return
        except KeyError:
            return


def start_of_searh():
    """Оснавная функция,которая запускает весь процесс

    Returns:
        (list): список отелей, состоит из кортежей с необходимой информацией
    """
    # извлечение переменных с именем города, кол-вом отелей и фотографий
    city_name, hotel_quantity, photo_quantity = fetch_sqlite_data()
    # извлечение данных по отелям
    hotels_data = fetch_all_data(city_name)
    if hotels_data:
        all_id = list(fetch_needed_data(hotels_data, "destinationId"))

        hotels = []
        for id in all_id:
            data = fetch_hotel_details(id)
            extracted_data = list(fetch_all_data_from_parsing(data, city_name))
            hotels.append(extracted_data)
        # избавление от лишних списков внутри основного списка и затем избавление от дубликатов
        hotels = [item for item_2 in hotels for item in item_2]
        duplicate = []
        new_data = []
        for hotel in hotels:
            if hotel[0] not in duplicate:
                duplicate.append(hotel[0])
                new_data.append(hotel)
        # сбор отсортированных отелей в список, такое кол-во, какое указал пользователь 
        sorted_data = sorted(new_data, key=lambda item: item[3])
        result = []
        hotel_count = 0
        for item in sorted_data:
            result.append(item)
            hotel_count += 1
            if hotel_count == int(hotel_quantity):
                break
        return result
    else:
        return None
