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


@dp.message_handler(ChatTypeFilter('private'), commands="help")
async def create_task(message: types.Message):
    await bot.send_message(message.chat.id, f"""
👨‍💻 Для работы в личных сообщениях:
Помощь по командам: /help
Основное меню: /menu
Добавить задачу:
. [Описание] [@исполнитель] [@контролирующий] [дата]
Формат даты: ММ:ЧЧ ДД.ММ.ГГ

👨‍💻 Для работы в группе:
Добавьте меня в группу и назначьте администратором,
Затем перешлите сообщение с описанием задачи и текст сообщения будет добавлен в качестве комментария
    """)

async def return_to_menu(state : FSMContext):
    await CreateS.menu.set()
    async with state.proxy() as data:
        chat_id = data['chat_id']
        menu_title = 'Выберите тип задачи'
        if 'menu_title' in data:
            menu_title = data['menu_title']
    message = await bot.send_message(chat_id, menu_title, reply_markup=keyboard_kb_menu)
    await state.update_data(menu_message_id=message.message_id)


@dp.message_handler(ChatTypeFilter('private'), commands=["start", "menu"], state="*")
async def menu_handler(message: types.Message, state : FSMContext):
    await state.update_data(chat_id=message.chat.id)
    await state.update_data(user_id=message.from_user.id)
    await return_to_menu(state=state)


@dp.message_handler(ChatTypeFilter('private'), state=CreateS.menu)
async def handle_menu(message : types.Message, state : FSMContext):
    async with state.proxy() as data:
        menu_message_id = data['menu_message_id']
        chat_id = data['chat_id']
    await bot.delete_message(chat_id=chat_id, message_id=menu_message_id)
    task_type = message.text
    if task_type not in (MY_TASKS_COMMAND, CONTROL_TASKS_COMMAND):
        await return_to_menu(state=state)
        return
    
    await state.update_data(task_type=task_type)
    if task_type == MY_TASKS_COMMAND:
        pass #TODO
    elif task_type == CONTROL_TASKS_COMMAND:
        pass #TODO
    else:
        await return_to_menu(state=state)
        return

