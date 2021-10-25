import telebot

bot = telebot.TeleBot("2004736420:AAHL4hHRiOySvTP5hTzUp-cucFB0l7jMH80")


@bot.message_handler(content_types=['text'])
def send_welcome(message):
	if message.text == "Привет":
		bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
	elif message.text == "/hello-world":
		bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
	else:
		bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /hello-world.")


bot.polling(none_stop=True, interval=0)
