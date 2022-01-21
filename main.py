from logging import warning
from decouple import config
import telebot
from data_base import sqlite_db, user_data
from telebot import types
from botrequests import lowprice
from telegram_bot_calendar import DetailedTelegramCalendar
from telebot.types import InputMediaPhoto
import datetime


bot = telebot.TeleBot(config('Token'))
db = sqlite_db.DBHelper()
db.setup()


# создание клавиатуры
keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
keyboard.add("/lowprice", "/highprice")
keyboard.add("/bestdeal", "/history")
keyboard.add("/cancel")


# начало работы команда start и help
@bot.message_handler(commands=["start", "help"])
def start_message(message):
    # Выводит клавиатуру с кнопками
    bot.send_message(message.chat.id, "Выберите команду", reply_markup=keyboard)

# Кнопка прерывания запроса
@bot.message_handler(commands=["cancel"])
def start_message(message):
    # выводит прощание и клавиатуру с кнопками
    bot.send_message(message.chat.id, "До свидания!", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=["lowprice", "highprice", "bestdeal", "history"])
def all_commands(message):
    # Вызов (вызов и создание) пользователя в классе User и запись комманды в класс User 
    user = user_data.User.get_user(message.chat.id)
    user.create_command(message.text)
    bot.send_message(message.chat.id, "Введите город")
    bot.register_next_step_handler(message, calendar_checkin)


def calendar_checkin(message):
    """Вызов пользователся из класса User, запись города в класс User"""
    user = user_data.User.get_user(message.chat.id)
    user.create_city(message.text)
    # Вывод клавиатуры для записи даты вьезда
    now = datetime.datetime.now().date()
    calendar, step = DetailedTelegramCalendar(calendar_id=1, min_date=now).build()
    LSTEP = {"y": "год", "m": "месяц", "d": "день"}
    bot.send_message(message.chat.id, "Выберите когда будете заезжать")
    bot.send_message(message.chat.id,
                     f"Выберите {LSTEP[step]}",
                     reply_markup=calendar)


def calendar_checkout(message):
    """Вызов клавиатуры для записи даты отъезда пользователя"""
    now = datetime.datetime.now().date()
    calendar, step = DetailedTelegramCalendar(calendar_id=2, min_date=now).build()
    LSTEP = {"y": "год", "m": "месяц", "d": "день"}
    bot.send_message(message.chat.id, "Выберите когда будете уезжать")
    bot.send_message(message.chat.id,
                     f"Выберите {LSTEP[step]}",
                     reply_markup=calendar)


# call клавиатуры для записи даты въезда
@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def call(item):
    now = datetime.datetime.now().date()
    result, key, step = DetailedTelegramCalendar(calendar_id=1, locale="ru", min_date=now).process(item.data)
    if not result and key:
        LSTEP = {"y": "год", "m": "месяц", "d": "день"}
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              item.message.chat.id,
                              item.message.message_id,
                              reply_markup=key)
    if result:
        bot.send_message(item.message.chat.id, f"Вы заезжаете {result}")
        user = user_data.User.get_user(item.message.chat.id)
        user.create_checkin(result)
        calendar_checkout(item.message)

# call клавиатуры для записи даты отъезда
@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def call(item):
    now = datetime.datetime.now().date()
    result, key, step = DetailedTelegramCalendar(calendar_id=2, locale="ru", min_date=now).process(item.data)
    if not result and key:
        LSTEP = {"y": "год", "m": "месяц", "d": "день"}
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              item.message.chat.id,
                              item.message.message_id,
                              reply_markup=key)
    if result:
        bot.send_message(item.message.chat.id, f"Вы уезжаете {result}")
        user = user_data.User.get_user(item.message.chat.id)
        user.create_checkout(result)
        request_of_quantity(item.message)


def request_of_quantity(message):
    """запрос у пользователя необходимого кол-ва отелей"""
    bot.send_message(message.chat.id, "Введите количество отелей")
    bot.register_next_step_handler(message, quantity)


def quantity(message):
    """Вызов пользователя из User и запись количества отелей в User"""
    try:
        digit = int(message.text)
        user = user_data.User.get_user(message.chat.id)
        user.create_quantity(digit)
        bot.send_message(message.chat.id, "Нужны фотографии?")
        bot.register_next_step_handler(message, photo)
    except ValueError:
        bot.send_message(message.chat.id, "Введите цифру")
        bot.register_next_step_handler(message, quantity)


def photo(message):
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
        if command == "/lowprice":
            lowprice_command(message)

    elif str(message.text).lower() == "да":
        bot.send_message(message.chat.id, "Сколько фотографий?")
        bot.register_next_step_handler(message, second_quantity)

    else:
        bot.send_message(message.chat.id, "Введите да или нет")
        bot.register_next_step_handler(message, photo)


def second_quantity(message):
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
        if command == "/lowprice":
            lowprice_command(message)
        else:
            bot.send_message(message.chat.id, command)
    except ValueError:
        bot.send_message(message.chat.id, "Введите цифру")
        bot.register_next_step_handler(message, second_quantity)


# реализация команды lowprice
def lowprice_command(message):
    """Вызов пользователя, его id, запрос на необходимые парсинги в файле lowprice
       и вывод полученных данных пользователя"""

    user = user_data.User.get_user(message.chat.id)
    id = user.get_id()
    bot.send_message(message.chat.id, "Подождите, ищем...")

    parsing_data = lowprice.start_of_searh(id)
    if parsing_data:
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
@bot.message_handler(content_types=["text"])
def error_message(message):
    bot.send_message(message.chat.id, "Выберите команду из списка",
                     reply_markup=keyboard)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
