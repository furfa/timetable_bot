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
from . tools import id_to_username, username_to_id
from . notiflicate import task_closed_by_creator, task_closed_by_worker

command_to_type = {
    MY_TASKS_COMMAND: "my",
    CONTROL_TASKS_COMMAND: "control"
}

@dp.message_handler(ChatTypeFilter('private'), lambda m: m.text in (MY_TASKS_COMMAND, CONTROL_TASKS_COMMAND), state="*")
async def handle_menu(message : types.Message, state : FSMContext):
    async with state.proxy() as data:
        menu_message_id = data.get('menu_message_id')
    chat_id = message.chat.id
    user_id = message.from_user.id
    await state.update_data(chat_id=chat_id)
    await state.update_data(user_id=user_id)
    if menu_message_id is not None:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=menu_message_id)
        except Exception as e:
            pass
    task_type = message.text

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
        tasks = await read_control_tasks_db(user_id)
    elif task_type == 'my':
        # await CreateS.read_my_awaiting_idx.set()
        tasks = await read_my_tasks_db(user_id)
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
        worker_username = await id_to_username(task.worker)
        creator_username = await id_to_username(task.creator)
        message = await bot.send_message(chat_id, f"""
Номер: {task.idx}
Описание: {task.description}
Дедлайн: {task.deadline}
Исполнитель: @{worker_username}
Контролирующий: @{creator_username}
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
        to_edit = data['to_edit']
    comments = await read_comments_db(idx=idx, user_id=user_id)
    if not comments:
        await bot.edit_message_text(chat_id=chat_id, message_id=to_edit.message_id, text=to_edit.text + '\n\nНет комментариев')
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=to_edit.message_id)
        # await bot.send_message(chat_id, "Нет комментариев")
        # await state.update_data(menu_title="Нет комментариев")
        # await return_to_menu(state=state)
    for comment in comments:
        await bot.send_message(chat_id, comment)
    # await CreateS.previous()
    await return_to_menu(state=state)

async def add_comment(state : FSMContext):
    async with state.proxy() as data:
        idx = data['idx']
        user_id = data['user_id']
        chat_id = data['chat_id']
        to_edit = data['to_edit']
    await bot.edit_message_text(chat_id=chat_id, message_id=to_edit.message_id, text=to_edit.text + '\n\nВведите комментарий')
    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=to_edit.message_id)

@dp.message_handler(ChatTypeFilter('private'), state=CreateS.add_comment)
async def handle_add_comment(message : types.Message, state : FSMContext):
    async with state.proxy() as data:
        data['comment'] = f"{message.from_user.first_name} {message.from_user.last_name}: {message.text}"
        idx = data['idx']
        user_id = data['user_id']
        await add_comment_db(idx=idx, user_id=user_id, comment=data['comment'])
    # await CreateS.previous()
    await return_to_menu(state=state)

@dp.callback_query_handler(state=CreateS.read_my_menu)
async def read_my_menu_callback(callback_query : types.CallbackQuery, state : FSMContext):
    # await bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    idx = int(callback_query.data.split('_')[-1])
    await state.update_data(idx=idx)
    await state.update_data(to_edit=callback_query.message)
    if callback_query.data.startswith('delete_'):
        await delete_task(state=state, delete_from='worker')
        return
    elif callback_query.data.startswith('add_comment_'):
        await CreateS.add_comment.set()
        await add_comment(state=state)
        # await state.update_data(task_permissions='my')
    elif callback_query.data.startswith('comments_'):
        await CreateS.read_comments.set()
        await read_comments(state=state)
    else:
        await return_to_menu(state=state)

async def delete_task(state : FSMContext, delete_from : str):
    async with state.proxy() as data:
        chat_id = data['chat_id']
        idx = data['idx']
        to_edit = data['to_edit']
    await delete_task_db(idx=idx)
    task = await read_task_db(idx=idx)
    await state.update_data(description=task.description)
    await state.update_data(deadline=task.deadline)
    await state.update_data(worker=task.worker)
    await state.update_data(creator=task.creator)
    await state.update_data(worker_username=await id_to_username(task.worker))
    await state.update_data(creator_username=await id_to_username(task.creator))
    try:
        await bot.delete_message(chat_id, to_edit.message_id)
        if delete_from == 'creator':
            await task_closed_by_creator(state=state)
        else:
            await task_closed_by_worker(state=state)
        await state.update_data(menu_title="Задача завершена")
    except Exception as e:
        await state.update_data(menu_title="Попросите пользователей зарегистрироваться в боте 😡")
    await return_to_menu(state=state)

@dp.callback_query_handler(state=CreateS.read_control_menu)
async def read_control_menu_callback(callback_query : types.CallbackQuery, state : FSMContext):
    # await bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    idx = int(callback_query.data.split('_')[-1])
    await state.update_data(to_edit=callback_query.message)
    await state.update_data(idx=idx)
    if callback_query.data.startswith('update_'):
        await CreateS.update.set()
        await bot.send_message(chat_id, "Выберите параметр для изменения", reply_markup=inline_kb_update)
    elif callback_query.data.startswith('delete_'):
        await delete_task(state=state, delete_from='creator')
        return
    elif callback_query.data.startswith('add_comment_'):
        await CreateS.add_comment.set()
        await add_comment(state=state)
        # await state.update_data(task_permissions='control')
    elif callback_query.data.startswith('comments_'):
        await CreateS.read_comments.set()
        await read_comments(state=state)
    else:
        await return_to_menu(state=state)