from os import read, stat
from aiogram import types
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from aiogram.dispatcher.filters.builtin import ChatTypeFilter
from aiogram.types import chat, message, user
from datetime import datetime

from . data_tools import *
from . app import dp, bot
from . commands import *
from . states import CreateS
from . keyboards import *
from . tools import username_to_id

HELP_INFO = f"""
👨‍💻 Для работы в личных сообщениях:
👉 Помощь по командам: /help
👉 Основное меню: /menu
👉 Добавить задачу:
. [Описание] [@исполнитель] [@контролирующий] [дата]
Формат даты:
ММ:ЧЧ ДД.ММ.ГГГГ
или
ДД.ММ

👨‍💻 Для работы в группе:
👉 Добавьте меня в группу и назначьте администратором,
👉 Введите /start
👉 Добавляйте задачи
"""

@dp.message_handler(ChatTypeFilter('private'), commands="start", state="*")
async def create_task(message: types.Message, state : FSMContext):
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    if first_name is None:
        first_name = ""
    last_name = message.from_user.last_name
    if last_name is None:
        last_name = ""
    await reg_user(
        user_id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name
        )
    await bot.send_message(chat_id, HELP_INFO, parse_mode="HTML")
    await state.update_data(chat_id=chat_id)
    await return_to_menu(state=state)

@dp.message_handler(ChatTypeFilter('private'), commands="help", state="*")
async def create_task(message: types.Message, state : FSMContext):
    chat_id = message.chat.id
    await bot.send_message(chat_id, HELP_INFO, parse_mode="HTML")
    await state.update_data(chat_id=chat_id)
    await return_to_menu(state=state)

async def return_to_menu(state : FSMContext):
    await CreateS.menu.set()
    async with state.proxy() as data:
        chat_id = data['chat_id']
        menu_title = 'Выберите тип задачи'
        if 'menu_title' in data:
            menu_title = data['menu_title']
            del data['menu_title']
    message = await bot.send_message(chat_id, menu_title, reply_markup=keyboard_kb_menu)
    await state.update_data(menu_message_id=message.message_id)


@dp.callback_query_handler(ChatTypeFilter('private'), lambda m: m.data == 'menu', state="*")
async def menu_query_handler(message: types.Message, state : FSMContext):
    await return_to_menu(state=state)

@dp.message_handler(ChatTypeFilter('private'), commands="menu", state="*")
async def menu_handler(message: types.Message, state : FSMContext):
    user_id = message.from_user.id
    await state.update_data(chat_id=message.chat.id)
    await state.update_data(user_id=user_id)
    await return_to_menu(state=state)
