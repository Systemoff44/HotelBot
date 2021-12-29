from decouple import config
import telebot
from data_base import sqlite_db
from telebot import types
from botrequests import lowprice
from telegram_bot_calendar import DetailedTelegramCalendar


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
    bot.send_message(message.chat.id, "Выберите команду", reply_markup=keyboard)

@bot.message_handler(commands=["cancel"])
def start_message(message):
    bot.send_message(message.chat.id, "До свидания!", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=["lowprice", "highprice", "bestdeal", "history"])
def all_commands(message):
    # в глобальную переменную comma попадает сама команда
    global comma
    comma = message.text
    bot.send_message(message.chat.id, "Введите город")
    bot.register_next_step_handler(message, calendar_checkin)


def calendar_checkin(message):
    db.city = message.text
    calendar, step = DetailedTelegramCalendar(calendar_id=1).build()
    LSTEP = {"y": "год", "m": "месяц", "d": "день"}
    bot.send_message(message.chat.id, "Выберите когда будете заезжать")
    bot.send_message(message.chat.id,
                     f"Выберите {LSTEP[step]}",
                     reply_markup=calendar)


def calendar_checkout(message):
    calendar, step = DetailedTelegramCalendar(calendar_id=2).build()
    LSTEP = {"y": "год", "m": "месяц", "d": "день"}
    bot.send_message(message.chat.id, "Выберите когда будете уезжать")
    bot.send_message(message.chat.id,
                     f"Выберите {LSTEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def call(item):
    result, key, step = DetailedTelegramCalendar(calendar_id=1, locale="ru").process(item.data)
    if not result and key:
        LSTEP = {"y": "год", "m": "месяц", "d": "день"}
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              item.message.chat.id,
                              item.message.message_id,
                              reply_markup=key)
    if result:
        bot.send_message(item.message.chat.id, f"Вы заезжаете {result}")
        db.checkin = result
        calendar_checkout(item.message)

@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def call(item):
    result, key, step = DetailedTelegramCalendar(calendar_id=2, locale="ru").process(item.data)
    if not result and key:
        LSTEP = {"y": "год", "m": "месяц", "d": "день"}
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              item.message.chat.id,
                              item.message.message_id,
                              reply_markup=key)
    if result:
        bot.send_message(item.message.chat.id, f"Вы уезжаете {result}")
        db.checkout = result
        city(item.message)
      
def city(message):
    bot.send_message(message.chat.id, "Введите количество отелей")
    bot.register_next_step_handler(message, quantity)


def quantity(message):
    try:
        digit = int(message.text)
        db.quantity = digit
        bot.send_message(message.chat.id, "Нужны фотографии?")
        bot.register_next_step_handler(message, photo)
    except ValueError:
        bot.send_message(message.chat.id, "Введите цифру")
        bot.register_next_step_handler(message, quantity)


def photo(message):
    if str(message.text).lower() == "нет":
        db.photo = 0
        db.add_data()
        bot.send_message(message.chat.id, "Записал")
        if comma == "/lowprice":
            lowprice_command(message)

    elif str(message.text).lower() == "да":
        bot.send_message(message.chat.id, "Сколько фотографий?")
        bot.register_next_step_handler(message, second_quantity)

    else:
        bot.send_message(message.chat.id, "Введите да или нет")
        bot.register_next_step_handler(message, photo)


def second_quantity(message):
    try:
        digit = int(message.text)
        db.photo = digit
        db.add_data()
        bot.send_message(message.chat.id, "Записал!")
        lowprice_command(message)
    except ValueError:
        bot.send_message(message.chat.id, "Введите цифру")
        bot.register_next_step_handler(message, second_quantity)


# реализация команды lowprice
def lowprice_command(message):
    bot.send_message(message.chat.id, "Подождите, ищем...")

    parsing_data = lowprice.start_of_searh()
    if parsing_data:
        # Запрос из бд количество отелей и фотографий, которые ввел пользователь,
        # если цифра меньше, выведется сообщение о том, что нашлось меньше, чем нужно
        quantity, photo = lowprice.fetch_quantities_from_sqlite()
        if quantity > len(parsing_data):
            bot.send_message(message.chat.id,
                             f"Вы запрашивали {quantity} отелей, но нашлось только {len(parsing_data)}")
        for item in parsing_data:
            bot.send_message(message.chat.id, f"Название: {item[0]}")
            bot.send_message(message.chat.id, f"Адрес: {item[1]}")
            bot.send_message(message.chat.id, f"От центра: {item[2]}")
            if len(item) > 6:
                bot.send_message(message.chat.id, f"Цена: {item[3]}, {item[6]}")
            else:
                bot.send_message(message.chat.id, "Вы некорректно указали даты:")
                bot.send_message(message.chat.id, f"Цена: {item[3]} (цена за сутки)")
            bot.send_message(message.chat.id, f"{quantity}, {photo}")
            bot.send_message(message.chat.id,
                             f"Ссылка на сайт: https://ru.hotels.com/ho{item[4]}")
            if isinstance(item[5], list):
                if photo > len(item[5]):
                    bot.send_message(message.chat.id,
                                     f"Вы хотели {photo} фотографи, но нашлось только {len(item[5])}")
                for url_photo in item[5]:
                    url_photo = url_photo.format(size="b")
                    bot.send_photo(message.chat.id, photo=url_photo)
            bot.send_message(message.chat.id, "="*30)
        bot.send_message(message.chat.id, "Хотите продолжить:",
                         reply_markup=keyboard)
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
