from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from decouple import config
from botrequests import keybord_client
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data_base import sqlite_db


if __name__ == '__main__':
    storage = MemoryStorage()

    bot = Bot(config('Token'))
    dp = Dispatcher(bot, storage=storage)


    async def on_startup(_):
        print("Бот запущен")
        sqlite_db.sql_start()

    class ReceiveData(StatesGroup):
        city = State()
        quantity = State()
        photo = State()
        quantity_photo = State()

    @dp.message_handler(commands=["start", "help"])
    async def command_start(message: types.Message):
        await bot.send_message(message.from_user.id, "Выберите команду", reply_markup=keybord_client)

    # Начало диалога после любой команды
    @dp.message_handler(commands=["lowprice", "highprice", "history", "bestdeal"], state=None)
    async def all_command(message: types.Message):
        global command
        command = message.text
        await ReceiveData.city.set()
        await message.reply("Укажите город")

    # Ловим ответ и пишем в словарь
    @dp.message_handler(state=ReceiveData.city)
    async def receive_city(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data["city"] = message.text
        await ReceiveData.next()
        await message.reply("Укажите количество отелей")

    # Ловим второй ответ
    @dp.message_handler(state=ReceiveData.quantity)
    async def receive_quantity(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data["quantity"] = int(message.text)
        await ReceiveData.next()
        await message.reply("Нужны ли фотографии? (да/нет)")

    # Ловим третий ответ
    @dp.message_handler(state=ReceiveData.photo)
    async def receive_photo(message: types.Message, state: FSMContext):
        if message.text == "да":
            await ReceiveData.next()
            await message.reply("Сколько фотографий?")
        elif message.text == "нет":
            async with state.proxy() as data:
                data["photo"] = message.text

            await sqlite_db.sql_add_command(state)
            await state.finish()

    # Ловим четвертый возможный ответ
    @dp.message_handler(state=ReceiveData.quantity_photo)
    async def receive_another_photo(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data["photo"] = int(message.text)
        await sqlite_db.sql_add_command(state)

        await state.finish()

    # Здесь будет реализовываться команда /lowprice
    async def command_execution():
        if command == "/lowprice":
            pass


    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
