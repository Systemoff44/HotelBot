from decouple import config
import telebot
from data_base import sqlite_db
from telebot import types
from botrequests import lowprice


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


@bot.message_handler(commands=["lowprice", "highprice", "bestdeal", "history"])
def all_commands(message):
    # в глобальную переменную comma попадает сама команда
    global comma
    comma = message.text
    bot.send_message(message.chat.id, "Введите город")
    bot.register_next_step_handler(message, city)


def city(message):
    db.city = message.text
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


def lowprice_command(message):
    bot.send_message(message.chat.id, "Подождите, ищем...")

    parsing_data = lowprice.start_of_searh()
    if parsing_data:
        for item in parsing_data:
            bot.send_message(message.chat.id, f"Название: {item[0]}")
            bot.send_message(message.chat.id, f"Адрес: {item[1]}")
            bot.send_message(message.chat.id, f"От центра: {item[2]}")
            bot.send_message(message.chat.id, f"Цена: {item[3]}")
            bot.send_message(message.chat.id, "="*30)
    else:
        bot.send_message(message.chat.id, "Не корректно введен город")
        bot.send_photo(message.chat.id, "https://exp.cdn-hotels.com/hotels/16000000/15410000/15403500/15403453/2af5883d_300px.jpg")
        bot.send_message(message.chat.id, "Выберите команду из списка",
                         reply_markup=keyboard)

@bot.message_handler(content_types=["text"])
def error_message(message):
    bot.send_message(message.chat.id, "Выберите команду из списка",
                     reply_markup=keyboard)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
