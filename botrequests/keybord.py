from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

lowprice_button = KeyboardButton("/lowprice")
history_button = KeyboardButton("/history")
highprice_button = KeyboardButton("/highprice")
bestdeal_button = KeyboardButton("/bestdeal.py")

keybord_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
keybord_client.row(lowprice_button, highprice_button).row(history_button, bestdeal_button)
