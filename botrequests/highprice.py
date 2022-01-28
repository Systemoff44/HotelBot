from loguru import logger
from . import lowprice
from decouple import config
from data_base import sqlite_db


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
    hotels_data = lowprice.fetch_all_data(city_name, headers_for_parsing)
    if hotels_data:
        all_id = list(lowprice.fetch_needed_data(hotels_data, "destinationId"))
        price = "PRICE_HIGHEST_FIRST"
        hotels = []
        for id in all_id:
            data = lowprice.fetch_hotel_details(id, hotel_checkin, hotel_checkout, headers_for_parsing, price)
            extracted_data = list(lowprice.fetch_all_data_from_parsing(data, city_name))
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
        sorted_data = sorted(new_data, key=lambda item: item[3], reverse=True)
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
            data_with_photos = lowprice.search_for_photos(result, int(photo_quantity), headers_for_parsing)
            return data_with_photos
        return result
    else:
        return None
