from decouple import config
import telebot
from data_base import sqlite_db
from telebot import types
from botrequests import lowprice


bot = telebot.TeleBot(config('Token'))
db = sqlite_db.DBHelper()
db.setup()

keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
keyboard.add("/lowprice", "/highprice")
keyboard.add("/bestdeal", "/history")
keyboard.add("/cancel")


@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(message.chat.id, "Выберите команду", reply_markup=keyboard)


@bot.message_handler(commands=["lowprice", "highprice", "bestdeal", "history"])
def all_commands(message):
    global comma
    comma = message.text
    bot.send_message(message.chat.id, "Введите город")
    bot.register_next_step_handler(message, city)


def city(message):
    db.city = message.text
    bot.send_message(message.chat.id, "Введите количество отелей")
    bot.register_next_step_handler(message, quantity)


def quantity(message):
    db.quantity = message.text
    bot.send_message(message.chat.id, "Нужны фотографии?")
    bot.register_next_step_handler(message, photo)


def photo(message):
    if str(message.text).lower() == "нет":
        db.photo = 0
        db.add_data()
        bot.send_message(message.chat.id, "Записал")
        if comma == "/lowprice":
            # bot.send_message(message.chat.id, str(db.get_items()))
            bot.send_message(message.chat.id, str(lowprice.foo()))

    elif str(message.text).lower() == "да":
        bot.send_message(message.chat.id, "Сколько фотографий?")
        bot.register_next_step_handler(message, second_quantity)

    else:
        bot.send_message(message.chat.id, "Введите да или нет")
        bot.register_next_step_handler(message, photo)


def second_quantity(message):
    db.photo = message.text
    db.add_data()
    bot.send_message(message.chat.id, "Записал!")


@bot.message_handler(content_types=["text"])
def error_message(message):
    bot.send_message(message.chat.id, "Выберите команду из списка",
                     reply_markup=keyboard)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
