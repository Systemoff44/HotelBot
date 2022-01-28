import requests
import json
from data_base import sqlite_db
from decouple import config
from loguru import logger


logger.add("file_{time}.log", format="{time} | {level} | {message}", level="INFO")
logger.debug("Debag message")


@logger.catch
def fetch_all_data(city, headers):
    """Парсинг данных по определенному городу

    Args:
        city (str): город, который ввел пользователь

    Returns:
        (dict): словарь с данными по определенному городу
    """
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"

    querystring = {"query": city,
                   "locale": "ru_RU", "currency": "RUB"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    all_id = json.loads(response.text)
    # Если "moresuggestions" == 0, то город был введен некоректно, и возвращает None
    if all_id["moresuggestions"] == 0:
        return None
    else:
        return all_id


@logger.catch
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


@logger.catch
def fetch_hotel_details(number_id, data_in, data_out, headers, price="PRICE"):
    """Делает парсинг всех данных по определенному id места

    Args:
        number_id (int): номер id
        data_in (str): дата заезда
        data_out (str): дата уезда

    Returns:
        (dict): данные с отелями по определенному id места
    """
    url = "https://hotels4.p.rapidapi.com/properties/list"

    querystring = {"destinationId": number_id, "pageNumber": "1", "pageSize": "25",
                   "checkIn": data_in, "checkOut": data_out, "adults1": "1",
                   "sortOrder": price, "locale": "ru_RU", "currency": "RUB"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    all_details = json.loads(response.text)

    return all_details


@logger.catch
def fetch_hotel_photos(hotel_id, headers):
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": hotel_id}

    response = requests.request("GET", url, headers=headers, params=querystring)
    all_photos = json.loads(response.text)

    return all_photos


@logger.catch
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
                        "results"][index]["address"]["locality"].lower() == city.lower():
                # сбор данных в кортеж
                name = all_data["data"]["body"]["searchResults"]["results"][index]["name"]
                adress = all_data["data"]["body"]["searchResults"]["results"][index]["address"]["streetAddress"]
                center = all_data["data"]["body"]["searchResults"]["results"][index]["landmarks"][0]["distance"]
                price = all_data["data"]["body"]["searchResults"]["results"][index]["ratePlan"]["price"]["exactCurrent"]
                id = all_data["data"]["body"]["searchResults"]["results"][index]["id"]
                photo = 0
                if "info" in all_data["data"]["body"]["searchResults"]["results"][index]["ratePlan"]["price"]:
                    info = all_data["data"]["body"]["searchResults"]["results"][index]["ratePlan"]["price"]["info"]
                    result = (name, adress, center, price, id, photo, info)
                else:
                    result = (name, adress, center, price, id, photo)
                yield result
            else:
                return
        except KeyError:
            return


@logger.catch
def search_for_photos(data, quantity, head_parsing):
    """Получает готовый список из отелей и вместо переменной id записывает
       список из url картинок. Возвращает обратно список отелей

    Args:
        data (list): список отелей
        quantity (int): количество фотографий, указанное пользователем

    Returns:
        (list): список отелей, где в кортежах сохранены все данные о
        каждом отеле и необходимое кол-во фотографий
    """
    new_data_with_photos = []
    for index in range(len(data)):
        item = fetch_hotel_photos(data[index][4], head_parsing)
        name = data[index][0]
        adress = data[index][1]
        center = data[index][2]
        price = data[index][3]
        id = data[index][4]
        photo = []
        for second_index in range(quantity):
            url = item["hotelImages"][second_index]["baseUrl"]
            photo.append(url)
        if len(data[index]) > 6:
            result = (name, adress, center, price, id, photo, data[index][6])
        else:
            result = (name, adress, center, price, id, photo)
        new_data_with_photos.append(result)
    return new_data_with_photos


@logger.catch
def start_of_searh(user_id):
    """Оснавная функция,которая запускает весь процесс

    Returns:
        (list): список отелей, состоит из кортежей с необходимой информацией
    """
    headers_for_parsing = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': config("token_api")
        }

    # извлечение переменных с именем города, кол-вом отелей и фотографий
    (city_name, hotel_checkin, hotel_checkout,
     hotel_quantity, photo_quantity) = sqlite_db.fetch_sqlite_data(user_id)
    # извлечение данных по отелям
    hotels_data = fetch_all_data(city_name, headers_for_parsing)
    if hotels_data:
        all_id = list(fetch_needed_data(hotels_data, "destinationId"))

        hotels = []
        for id in all_id:
            data = fetch_hotel_details(id, hotel_checkin, hotel_checkout, headers_for_parsing)
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
        # если нужны фотографии (кол-во больше нуля), отправляет готовый список
        # в следующую функцию для парсинга фотографий
        if int(photo_quantity) > 0:
            data_with_photos = search_for_photos(result, int(photo_quantity), headers_for_parsing)
            return data_with_photos
        return result
    else:
        return None
