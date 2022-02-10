from decouple import config
import telebot
from data_base import sqlite_db, user_data, history_data
from telebot import types
from botrequests import highprice, lowprice, bestdeal
from telegram_bot_calendar import WYearTelegramCalendar
from telebot.types import InputMediaPhoto
import datetime
from loguru import logger
import re
from typing import Any


logger.add("file_{time}.log", format="{time} | {level} | {message}", level="INFO")
logger.debug("Debag message")


bot = telebot.TeleBot(config('Token'))
db = sqlite_db.DBHelper()
db.setup()


# создание клавиатуры
keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
keyboard.add("/lowprice", "/highprice")
keyboard.add("/bestdeal", "/history")
keyboard.add("/cancel")


# начало работы команда start и help
@logger.catch
@bot.message_handler(commands=["start", "help"])
def start_message(message: Any) -> None:
    """ Выводит клавиатуру с кнопками"""
    bot.send_message(message.chat.id, "Выберите команду", reply_markup=keyboard)


# Кнопка прерывания запроса
@logger.catch
@bot.message_handler(commands=["cancel"])
def farewell_message(message: Any) -> None:
    """ Выводит прощание и клавиатуру с кнопками"""
    bot.send_message(message.chat.id, "До свидания!", reply_markup=types.ReplyKeyboardRemove())


# Кнопка history
@logger.catch
@bot.message_handler(commands="history")
def history_command(message: Any) -> None:
    """После нажатия кнопки /history получает id пользователя,
       делает запрос в бд по id
       и сохраняет в словарь всю историю."""
    user = user_data.User.get_user(message.chat.id)
    user_id = user.get_id()
    result = sqlite_db.fetch_history(user_id)
    # Инициализация класса History для записи туда истории запросов юзера
    user_history = history_data.History.get_user(message.chat.id)
    all_users_history = dict()
    keyboard = types.InlineKeyboardMarkup()
    for index, item in enumerate(result):
        keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text="Посмотреть результат поиска", callback_data=str(index))
        keyboard.add(button)
        all_users_history[index] = (item[0], item[1], item[2],
                                    item[3], item[4], item[5],
                                    item[6], item[7], item[8])
        text = f'Команда запроса:\n{item[5]}\nГород:\n{item[0]}\nВремя запроса:\n{item[8]}'
        bot.send_message(message.chat.id, text, reply_markup=keyboard)
    user_history.create_all_data(all_users_history)


@logger.catch
@bot.message_handler(commands=["lowprice", "highprice", "bestdeal"])
def all_commands(message: Any) -> None:
    """Вызов (вызов и создание) пользователя в классе User и запись
       комманды в класс User"""
    user = user_data.User.get_user(message.chat.id)
    # Запись команды в класс User
    user.create_command(message.text)
    now = datetime.datetime.now()
    time = now.strftime("%d-%m-%Y %H:%M")
    user.create_time(time)
    bot.send_message(message.chat.id, "Введите город")
    bot.register_next_step_handler(message, calendar_checkin)


@logger.catch
def calendar_checkin(message: Any) -> None:
    """Вызов пользователся из класса User, запись города в класс User"""
    user = user_data.User.get_user(message.chat.id)
    user.create_city(message.text)
    command = user.get_command()
    if command in ["/lowprice", "/highprice"]:
        # Вывод клавиатуры для записи даты вьезда
        now = datetime.datetime.now().date()
        calendar, step = WYearTelegramCalendar(calendar_id=1, min_date=now, locale="ru").build()
        LSTEP = {"m": "месяц", "d": "день"}
        bot.send_message(message.chat.id, "Выберите когда будете заезжать")
        bot.send_message(message.chat.id,
                         f"Выберите {LSTEP[step]}",
                         reply_markup=calendar)
    elif command == "/bestdeal":
        bot.send_message(message.chat.id,
                         "Введите диапазон цен \n(минимальную и максимальную сумму через пробел")
        bot.register_next_step_handler(message, range_of_price)


@logger.catch
def calendar_checkout(message):
    """Вызов клавиатуры для записи даты отъезда пользователя"""
    now = datetime.datetime.now().date()
    calendar, step = WYearTelegramCalendar(calendar_id=2, min_date=now, locale="ru").build()
    LSTEP = {"m": "месяц", "d": "день"}
    bot.send_message(message.chat.id, "Выберите когда будете уезжать")
    bot.send_message(message.chat.id,
                     f"Выберите {LSTEP[step]}",
                     reply_markup=calendar)


@logger.catch
@bot.callback_query_handler(func=WYearTelegramCalendar.func(calendar_id=1))
def first_call(item: Any) -> None:
    """ Call клавиатуры для записи даты въезда"""
    now = datetime.datetime.now().date()
    result, key, step = WYearTelegramCalendar(calendar_id=1, locale="ru", min_date=now).process(item.data)
    if not result and key:
        LSTEP = {"m": "месяц", "d": "день"}
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              item.message.chat.id,
                              item.message.message_id,
                              reply_markup=key)
    if result:
        bot.send_message(item.message.chat.id, f"Вы заезжаете {result}")
        user = user_data.User.get_user(item.message.chat.id)
        user.create_checkin(result)
        calendar_checkout(item.message)


@logger.catch
@bot.callback_query_handler(func=WYearTelegramCalendar.func(calendar_id=2))
def second_call(item: Any) -> None:
    """ Call клавиатуры для записи даты отъезда"""
    now = datetime.datetime.now().date()
    result, key, step = WYearTelegramCalendar(calendar_id=2, locale="ru", min_date=now).process(item.data)
    if not result and key:
        LSTEP = {"m": "месяц", "d": "день"}
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              item.message.chat.id,
                              item.message.message_id,
                              reply_markup=key)
    if result:
        bot.send_message(item.message.chat.id, f"Вы уезжаете {result}")
        user = user_data.User.get_user(item.message.chat.id)
        user.create_checkout(result)
        request_of_quantity(item.message)


@logger.catch
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: Any) -> None:
    """ Хэндлер для кнопок с запросами, смодулированных при вызове
        комманды /history """
    user_choice = int(call.data)
    # Создание повторного запроса (запись данных в класс User,
    # затем создание строки из данных в бд)
    user_history = history_data.History.get_user(call.message.chat.id)
    data = user_history.get_all_data()
    user = user_data.User.get_user(call.message.chat.id)
    id = user.get_id()
    user.create_city(data[user_choice][0])
    user.create_checkin(data[user_choice][1])
    user.create_checkout(data[user_choice][2])
    user.create_quantity(data[user_choice][3])
    user.create_photo(data[user_choice][4])
    user.create_command(data[user_choice][5])
    user.create_range(data[user_choice][6])
    user.create_distance(data[user_choice][7])
    user.create_time(data[user_choice][8])
    sqlite_db.create_request(id)
    bot.send_message(call.message.chat.id, "Повторяем запрос")
    realization_of_command(call.message)


@logger.catch
def range_of_price(message: Any) -> None:
    """ Запрос на введение диапазона цен """
    user = user_data.User.get_user(message.chat.id)
    model = r'\d+\s\d+'
    check_if_match = re.fullmatch(model, message.text)
    if check_if_match:
        user.create_range(message.text)
        bot.send_message(message.chat.id, "Введите максимальное расстояние до центра (в км)")
        bot.register_next_step_handler(message, distance_from_center)
    else:
        bot.send_message(message.chat.id,
                         "Вы неккоректно ввели ценовой диапазон,\nнужно ввести два целых числа через пробел")
        bot.register_next_step_handler(message, range_of_price)


@logger.catch
def distance_from_center(message: Any) -> None:
    """ Записывает в класс User удаленность от центра """
    try:
        digit = int(message.text)
        user = user_data.User.get_user(message.chat.id)
        user.create_distance(digit)
        request_of_quantity(message)
    except ValueError:
        bot.send_message(message.chat.id, "Введите цифру")
        bot.register_next_step_handler(message, distance_from_center)


@logger.catch
def request_of_quantity(message: Any) -> None:
    """запрос у пользователя необходимое кол-во отелей"""
    bot.send_message(message.chat.id, "Введите количество отелей")
    bot.register_next_step_handler(message, quantity)


@logger.catch
def quantity(message: Any) -> None:
    """Запрос у пользователя необходимое кол-во фотографий"""
    try:
        digit = int(message.text)
        user = user_data.User.get_user(message.chat.id)
        user.create_quantity(digit)
        bot.send_message(message.chat.id, "Нужны фотографии?")
        bot.register_next_step_handler(message, photo)
    except ValueError:
        bot.send_message(message.chat.id, "Введите цифру")
        bot.register_next_step_handler(message, quantity)


@logger.catch
def photo(message: Any) -> None:
    """ Вызов пользователя из User и запись кол-во фото - 0 в User,
        если пользователь вводит 'нет'"""
    user = user_data.User.get_user(message.chat.id)
    if str(message.text).lower() == "нет":
        user.create_photo(0)
        bot.send_message(message.chat.id, "Записал")
        id = user.get_id()
        # запись данных этого пользователя в бд
        sqlite_db.create_request(id)
        command = user.get_command()
        if command in ["/lowprice", "/highprice", "/bestdeal"]:
            realization_of_command(message)

    elif str(message.text).lower() == "да":
        bot.send_message(message.chat.id, "Сколько фотографий?")
        bot.register_next_step_handler(message, second_quantity)

    else:
        bot.send_message(message.chat.id, "Введите да или нет")
        bot.register_next_step_handler(message, photo)


@logger.catch
def second_quantity(message: Any) -> None:
    """ Вызов пользователя из User и запись кол-во фотографий в User"""
    try:
        digit = int(message.text)
        user = user_data.User.get_user(message.chat.id)
        user.create_photo(digit)
        bot.send_message(message.chat.id, "Записал!")
        # Запись данных этого пользователя в бд
        id = user.get_id()
        sqlite_db.create_request(id)
        command = user.get_command()
        if command in ["/lowprice", "/highprice", "/bestdeal"]:
            realization_of_command(message)
        else:
            bot.send_message(message.chat.id, command)
    except ValueError:
        bot.send_message(message.chat.id, "Введите цифру")
        bot.register_next_step_handler(message, second_quantity)


# реализация команды lowprice
@logger.catch
def realization_of_command(message: Any) -> None:
    """Вызов пользователя, его id, запрос на необходимые парсинги в файле lowprice
       и вывод полученных данных пользователя"""

    user = user_data.User.get_user(message.chat.id)
    id = user.get_id()
    bot.send_message(message.chat.id, "Подождите, ищем...")

    command = user.get_command()
    if command == "/lowprice":
        parsing_data = lowprice.start_of_searh(id)
    elif command == "/highprice":
        parsing_data = highprice.start_of_searh(id)
    elif command == "/bestdeal":
        parsing_data = bestdeal.start_of_searh(id)
    else:
        bot.send_message(message.chat.id, "Че-то не то")

    if parsing_data:
        if isinstance(parsing_data, str):
            bot.send_message(message.chat.id, parsing_data)
        else:
            # Запрос из бд количество отелей и фотографий, которые ввел пользователь,
            # если цифра меньше, выведется сообщение о том, что нашлось меньше, чем нужно
            quantity, photo = sqlite_db.fetch_quantities_from_sqlite(id)
            if quantity > len(parsing_data):
                bot.send_message(message.chat.id,
                                 f"Вы запрашивали {quantity} отелей, но нашлось только {len(parsing_data)}")
            # Сбор данных и отсылка сообщения
            for item in parsing_data:
                message_to_user = []
                name = f"Название: {item[0]}"
                message_to_user.append(name)
                adress = f"Адрес: {item[1]}"
                message_to_user.append(adress)
                center_location = f"От центра: {item[2]}"
                message_to_user.append(center_location)
                if len(item) > 6:
                    price = f"Цена: {item[3]}, {item[6]}"
                    message_to_user.append(price)
                else:
                    price = f"Вы некорректно указали даты:\nЦена: {item[3]} (цена за сутки)"
                    message_to_user.append(price)
                web_link = f"Ссылка на сайт: https://ru.hotels.com/ho{item[4]}"
                message_to_user.append(web_link)
                answer = "\n".join(message_to_user)
                bot.send_message(message.chat.id, answer, disable_web_page_preview=True)
                # Проверка, есть ли фотографии и отправка сообщения
                if isinstance(item[5], list):
                    all_photo = []
                    if photo > len(item[5]):
                        bot.send_message(message.chat.id,
                                         f"Вы хотели {photo} фотографи, но нашлось только {len(item[5])}")
                    for url_photo in item[5]:
                        url_photo = url_photo.format(size="b")
                        all_photo.append(url_photo)
                    media_group = []
                    for url in all_photo:
                        media_group.append(InputMediaPhoto(media=url))
                    bot.send_media_group(message.chat.id, media=media_group)
            bot.send_message(message.chat.id, "Если хотите продолжить, введите '/start'")
    else:
        bot.send_message(message.chat.id, "Не корректно введен город")
        bot.send_message(message.chat.id, "Выберите команду из списка",
                         reply_markup=keyboard)


# если пользователем введена не команда
@logger.catch
@bot.message_handler(content_types=["text"])
def error_message(message: Any) -> None:
    """ Реагирует на любой текст пользователя"""
    bot.send_message(message.chat.id, "Выберите команду из списка",
                     reply_markup=keyboard)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
