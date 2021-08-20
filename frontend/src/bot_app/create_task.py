from ssl import cert_time_to_seconds
from aiogram import types
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from aiogram.dispatcher.filters.builtin import ChatTypeFilter
from aiogram.types import chat, message, user
from datetime import datetime
from parse import *

from . app import dp

from . menu import return_to_menu
from . data_tools import create_task_db
from . tools import alias_to_id


@dp.message_handler(ChatTypeFilter('private'), lambda m: m.text.startswith('.'), state="*")
async def handle_creation(message : types.Message, state : FSMContext):
    raw_text = message.text

    await state.update_data(chat_id=message.chat.id)
    fields = parse(". {} @{} @{} {}", raw_text).fixed
    if len(fields) < 4:
        state.update_data(menu_title="Некорректная команда")
        await return_to_menu(state=state)
        return
    date = None
    try:
        date = datetime.strptime(fields[3], "%H:%M %d.%m.%Y") 
    except Exception as e:
        await message.reply('Некорректно введена дата')
        return
    
    description = fields[0]
    worker = alias_to_id(fields[1])
    creator = alias_to_id(fields[2])
    
    create_task_db(description=description, deadline=date, worker=worker, creator=creator)
    await state.update_data(menu_title="Задача создана")
    await return_to_menu(state=state)