from ssl import cert_time_to_seconds
from aiogram import types
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from aiogram.dispatcher.filters.builtin import ChatTypeFilter
from aiogram.types import chat, message, user
from datetime import datetime
from parse import *
from loguru import logger

from . app import dp, bot

from . menu import return_to_menu
from . data_tools import create_task_db
from . tools import username_to_id
from . notiflicate import write_to_worker


def parse_date(date_raw : str):
    date = None
    try:
        date = datetime.strptime(date_raw, "%H:%M %d.%m.%Y")
    except Exception as e:
        pass
    if date is not None:
        return date
    try:
        date = datetime.strptime(date_raw, "%d.%m")
        date = date.replace(year=2021, hour=23, minute=59)
    except Exception as e:
        pass
    return date

# ChatTypeFilter('private')
@dp.message_handler(lambda m: m.text.startswith('.'), state="*")
async def handle_creation(message : types.Message, state : FSMContext):
    logger.info(f'Try to create with text: {message.text}')
    raw_text = message.text
    user_id = message.from_user.id
    chat_id = message.chat.id
    await state.update_data(user_id=user_id)
    await state.update_data(chat_id=chat_id)
    fields = None
    try:
        parsed = parse(". {} @{} @{} {}", raw_text)
        fields = parsed.fixed
    except Exception as e:
        fields = None
    if not fields:
        try:
            parsed = parse(". {} @{} {}", raw_text)
            fields = list(parsed.fixed)
            fields.append(fields[2])
            fields[2] = message.from_user.username
        except Exception as e:
            fields = None
    if not fields:
        menu_title = """
Для добавления задачи напишите
. [Описание] @[исполнитель] @[контролирующий] [дата]

Формат даты:
ДД.ММ
или
ММ:ЧЧ ДД.ММ.ГГГГ

Пример
. Необходимо сделать работу @worker @boss 20.08
        """
        await state.update_data(menu_title=menu_title)

        if message.chat.type == 'private':
            await return_to_menu(state=state)
        return
    if len(fields) < 4:
        state.update_data(menu_title="Некорректная команда")

        if message.chat.type == 'private':
            await return_to_menu(state=state)
        return
    date = parse_date(fields[3])
    
    if date is None:
        await message.reply('Некорректно введена дата')
        return
    
    description = fields[0]
    worker = await username_to_id(fields[1])
    creator = await username_to_id(fields[2])
    # print(worker, creator)
    idx = None
    try:
        idx = await create_task_db(description=description, deadline=date, worker=worker, creator=creator)
    except Exception as e:
        await state.update_data(menu_title='Попросите пользователей зарегистрироваться в боте 😡')

        if message.chat.type == 'private':
            await return_to_menu(state=state)
        return

    await state.update_data(idx=idx)
    await state.update_data(description=description)
    await state.update_data(deadline=date)
    await state.update_data(worker=worker)
    await state.update_data(creator=creator)
    await state.update_data(initiator=chat_id)
    await state.update_data(worker_username=fields[1])
    await state.update_data(creator_username=fields[2])

    await write_to_worker(state=state)
    if message.chat.type == 'private':
        await return_to_menu(state=state)