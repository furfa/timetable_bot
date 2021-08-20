from os import stat
from aiogram import types
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from aiogram.dispatcher.filters.builtin import ChatTypeFilter
from aiogram.types import chat, message, user
from datetime import datetime
from parse import *


from . data_tools import *
from . app import dp, bot
from . commands import *
from . states import CreateS
from . keyboards import *
from . menu import return_to_menu
from . interfaces import *

command_to_type = {
    MY_TASKS_COMMAND: "my",
    CONTROL_TASKS_COMMAND: "control"
}

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
    task_type = command_to_type[task_type]
    await state.update_data(task_type=task_type)
    await read_all_tasks(state=state)
    return

async def read_all_tasks(state : FSMContext):
    async with state.proxy() as data:
        task_type = data['task_type']
        chat_id = data['chat_id']
        user_id = data['user_id']
    tasks = []
    if task_type == 'control':
        # await CreateS.read_control_awaiting_idx.set()
        tasks = read_control_tasks_db(user_id)
    elif task_type == 'my':
        # await CreateS.read_my_awaiting_idx.set()
        tasks = read_my_tasks_db(user_id)
    await read_tasks(tasks=tasks, state=state)
    

async def read_tasks(tasks, state : FSMContext):
    async with state.proxy() as data:
        chat_id = data['chat_id']
        task_type = data['task_type']
    if not tasks:
        await state.update_data(menu_title="Список пуст")
        await return_to_menu(state=state)
    for task in tasks:
        idx = task.idx
        custom_markup = None
        if task_type == 'control':
            custom_markup = get_task_markup(task_permissions='control', idx=idx)
            await CreateS.read_control_menu.set()
        elif task_type == 'my':
            custom_markup = get_task_markup(task_permissions='my', idx=idx)
            await CreateS.read_my_menu.set()
        message = await bot.send_message(chat_id, f"""
Номер: {task.idx}
Описание: {task.description}
Дедлайн: {task.deadline}
Исполнитель: {task.worker}
Контролирующий: {task.creator}
""", reply_markup=custom_markup
    )

"""
    Read task info
"""

async def read_comments(state : FSMContext):
    async with state.proxy() as data:
        idx = data['idx']
        user_id = data['user_id']
        chat_id = data['chat_id']
    comments = read_comments_db(idx=idx, user_id=user_id)
    if not comments:
        await state.update_data(menu_title="Нет комментариев")
        await return_to_menu(state=state)
    for comment in comments:
        await bot.send_message(chat_id, comment)

@dp.message_handler(ChatTypeFilter('private'), state=CreateS.add_comment)
async def add_comment(message : types.Message, state : FSMContext):
    async with state.proxy() as data:
        data['comment'] = message.text
        idx = data['idx']
        user_id = data['user_id']
        add_comment_db(idx=idx, user_id=user_id, comment=data['comment'])
    await return_to_menu(state=state)

@dp.callback_query_handler(state=CreateS.read_my_menu)
async def read_my_menu_callback(callback_query : types.CallbackQuery, state : FSMContext):
    await bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    idx = int(callback_query.data.split('_')[-1])
    await state.update_data(idx=idx)
    if callback_query.data.startswith('add_comment_'):
        await CreateS.add_comment.set()
        # await state.update_data(task_permissions='my')
        await bot.send_message(chat_id, 'Введите комментарий')
    elif callback_query.data.startswith('comments_'):
        await CreateS.read_comments.set()
        await read_comments(state=state)
    else:
        await return_to_menu(chat_id)

@dp.callback_query_handler(state=CreateS.read_control_menu)
async def read_control_menu_callback(callback_query : types.CallbackQuery, state : FSMContext):
    await bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    idx = int(callback_query.data.split('_')[-1])
    if callback_query.data.startswith('update'):
        await CreateS.update.set()
        await bot.send_message(chat_id, "Выберите параметр для изменения", reply_markup=inline_kb_update)
    elif callback_query.data.startswith('delete'):
        status = delete_task_db(idx=idx)
        if status:
            await return_to_menu(chat_id=chat_id, menu_title='Задача удалена')
        else:
            await return_to_menu(chat_id=chat_id, menu_title='Задача не найдена')
        return
    elif callback_query.data.startswith('add_comment'):
        await CreateS.add_comment.set()
        # await state.update_data(task_permissions='control')
        await bot.send_message(chat_id, 'Введите комментарий')
    elif callback_query.data.startswith('comments'):
        await CreateS.read_comments_awaiting_idx.set()
        await read_comments(chat_id=chat_id, state=state)
    else:
        await return_to_menu(chat_id)