from ssl import cert_time_to_seconds
from aiogram import types
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from aiogram.dispatcher.filters.builtin import ChatTypeFilter
from aiogram.types import chat, message, user
from datetime import datetime
from parse import *

from . app import dp, bot

from . menu import return_to_menu
from . data_tools import create_task_db
from . tools import alias_to_id, username_to_id


@dp.message_handler(ChatTypeFilter('private'), lambda m: m.text.startswith('.'), state="*")
async def handle_creation(message : types.Message, state : FSMContext):
    raw_text = message.text
    user_id = await username_to_id(message.from_user.id)
    chat_id = message.chat.id
    await state.update_data(user_id=user_id)
    await state.update_data(chat_id=chat_id)
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
    worker = await username_to_id(fields[1])
    creator = await username_to_id(fields[2])
    
    idx = create_task_db(description=description, deadline=date, worker=worker, creator=creator)
    await bot.send_message(chat_id, f"""
Номер: {idx}
Описание: {description}
Дедлайн: {date}
Исполнитель: @{fields[1]}
Контролирующий: @{fields[2]}
"""
    )
    await return_to_menu(state=state)