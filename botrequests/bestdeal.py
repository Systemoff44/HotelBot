from loguru import logger
from . import lowprice
from decouple import config
from data_base import sqlite_db
from typing import Any 


@logger.catch
def start_of_searh(user_id):
    """Оснавная функция,которая запускает весь процесс

    Returns:
        Any: либо список отелей, состоящий из кортежей с необходимой 
        информацией, либо строку, что информация не
    """
    headers_for_parsing = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': config("token_api")
        }

    # извлечение переменных с именем города, кол-вом отелей и фотографий
    (city_name, hotel_quantity, photo_quantity,
     hotel_range, hotel_distance) = sqlite_db.fetch_sqlite_bestdeal(user_id)
    prices = hotel_range.split()
    # извлечение данных по отелям
    hotels_data = lowprice.fetch_all_data(city_name, headers_for_parsing)
    if hotels_data:
        all_id = list(lowprice.fetch_needed_data(hotels_data, "destinationId"))
        hotels = []
        for id in all_id:
            data = lowprice.fetch_hotel_details(id, None, None,
                                                headers_for_parsing,
                                                price_min=prices[0],
                                                price_max=prices[1])
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
        # сортировка по дистанции от центра
        sorted_data = sorted(new_data, key=lambda item: item[3])
        result_with_distance = []
        for item in sorted_data:
            digit = item[2].split()
            new_digit = digit[0].replace(',', '.')
            if float(new_digit) < float(hotel_distance):
                result_with_distance.append(item)
        
        # сбор отсортированных отелей в список, такое кол-во, какое указал пользователь
        final_result = []
        if result_with_distance:
            hotel_count = 0
            for item in result_with_distance:
                final_result.append(item)
                hotel_count += 1
                if hotel_count == int(hotel_quantity):
                    break
        else:
            result = "К сожалению, с таким расстоянием и ценником ничего не нашлось"
            return result
        # если нужны фотографии (кол-во больше нуля), отправляет готовый список
        # в следующую функцию для парсинга фотографий
        if int(photo_quantity) > 0:
            data_with_photos = lowprice.search_for_photos(final_result, int(photo_quantity), headers_for_parsing)
            return data_with_photos
        return final_result
    else:
        return None
