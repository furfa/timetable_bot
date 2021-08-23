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
from . notiflicate import *
from . writing_tools import format_task_card_text, format_task_card_markup, get_emoji_by_idx

command_to_type = {
    MY_TASKS_COMMAND: "my",
    CONTROL_TASKS_COMMAND: "control"
}

MY_TASKS_MENU = ['my-delete', 'my-add-comment'] 
CONTROL_TASKS_MENU = ['control-delete', 'control-add-comment'] 


@dp.message_handler(ChatTypeFilter('private'), lambda m: m.text in (MY_TASKS_COMMAND, CONTROL_TASKS_COMMAND), state="*")
async def handle_menu(message : types.Message, state : FSMContext):
    chat_id = message.chat.id
    user_id = message.from_user.id

    task_type = message.text
    task_type = command_to_type[task_type]

    await state.update_data(chat_id=chat_id)
    await state.update_data(user_id=user_id)
    await state.update_data(task_type=task_type)

    await read_all_tasks(state=state)
    return

async def read_all_tasks(state : FSMContext):
    async with state.proxy() as data:
        task_type = data['task_type']
        user_id = data['user_id']
    tasks = []
    approve_tasks = []
    if task_type == 'control':
        tasks, approve_tasks = await read_control_tasks_db(user_id)
    elif task_type == 'my':
        tasks = await read_my_tasks_db(user_id)
    await read_tasks(tasks=tasks, state=state)
        
    

async def read_tasks(state : FSMContext, tasks):
    async with state.proxy() as data:
        chat_id = data['chat_id']
        task_type = data['task_type']
    if not tasks:
        await state.update_data(menu_title="Список пуст")
        await return_to_menu(state=state)
        return
    for task in tasks:
        task_permissions = 'my'
        if task_type == 'control':
            task_permissions = 'control'
            await CreateS.read_control_menu.set()
        elif task_type == 'approve':
            task_permissions = 'approve'
        elif task_type == 'my':
            task_permissions = 'my'
            await CreateS.read_my_menu.set()

        worker_username = await id_to_username(task.worker)
        creator_username = await id_to_username(task.creator)

        message_text = await format_task_card_text(
            idx=task.idx,
            description=task.description,
            deadline=task.deadline,
            worker_username=worker_username,
            creator_username=creator_username,
        )
        custom_markup = format_task_card_markup(
            idx=task.idx,
            task_permissions=task_permissions
        )
        await bot.send_message(chat_id, message_text, reply_markup=custom_markup)
    await send_shadow(chat_id=chat_id)
    
"""
    Read task info
"""

async def read_comments(state : FSMContext):
    async with state.proxy() as data:
        idx = data['idx']
        chat_id = data['chat_id']
        to_edit = data.get('to_edit')
    comments = await read_comments_db(idx=idx)
    if not comments and to_edit is not None:
        await bot.edit_message_text(chat_id=chat_id, message_id=to_edit.message_id, text=to_edit.text + '\n\nНет комментариев', reply_markup=to_edit.reply_markup)
    else:
        task = await read_task_db(idx=idx)
        message_text = await format_task_card_text(
            idx=task.idx,
            description=task.description,
            deadline=task.deadline,
            worker_username=await id_to_username(task.worker),
            creator_username=await id_to_username(task.creator)
        )
        if to_edit is not None:
            await bot.edit_message_text(chat_id=chat_id, message_id=to_edit.message_id, text=message_text, reply_markup=to_edit.reply_markup)
        async with state.proxy() as data:
            if 'to_edit' in data:
                del data['to_edit']

async def add_comment(state : FSMContext, add_from : str):
    async with state.proxy() as data:
        idx = data['idx']
        chat_id = data['chat_id']
    await state.update_data(add_comment_from=add_from)
    message = await bot.send_message(chat_id, f"{get_emoji_by_idx(idx)} Введите комментарий к задаче {idx}")
    await state.update_data(to_delete_last=message.message_id)

@dp.message_handler(ChatTypeFilter('private'), state=CreateS.add_comment)
async def handle_add_comment(message : types.Message, state : FSMContext):
    
    async with state.proxy() as data:
        idx = data['idx']
        add_comment_from = data['add_comment_from']
        user_id = data['user_id']
        to_delete_last = data['to_delete_last']
        data['comment'] = message.text
    await add_comment_db(idx=idx, user_id=user_id, comment=data['comment'])
    await bot.delete_message(chat_id=user_id, message_id=message.message_id)
    await bot.delete_message(chat_id=user_id, message_id=to_delete_last)
    await read_comments(state=state)
    if add_comment_from == 'creator':
        await add_comment_from_creator(state=state)
    elif add_comment_from == 'worker':
        await add_comment_from_worker(state=state)
    else:
        pass 
    await CreateS.previous()

async def delete_task(state : FSMContext, delete_from : str):
    async with state.proxy() as data:
        task_type = data['task_type']
        chat_id = data['chat_id']
        idx = data['idx']
        to_edit = data.get('to_edit')
    # task = await read_task_db(idx=idx)
    try:
        if to_edit is not None:
            await bot.delete_message(chat_id, to_edit.message_id)
        if delete_from == 'creator':
            await delete_task_db(idx=idx)
            await task_closed_by_creator(state=state)
        else:
            await wait_approve_task_db(idx=idx)
            await task_closed_by_worker(state=state)
    except Exception as e:
        if to_edit is not None:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=to_edit.message_id,
                text=to_edit.text + '\nПопросите пользователей зарегистрироваться в боте 😡'
                )
    async with state.proxy() as data:
        if 'to_edit' in data:
            del data['to_edit']

async def fill_task_data(state : FSMContext, task):
    await state.update_data(idx=task.idx)
    await state.update_data(description=task.description)
    await state.update_data(deadline=task.deadline)
    await state.update_data(worker=task.worker)
    await state.update_data(creator=task.creator)
    await state.update_data(worker_username=await id_to_username(task.worker))
    await state.update_data(creator_username=await id_to_username(task.creator))

@dp.callback_query_handler(lambda c: c.data.split('_')[0] in MY_TASKS_MENU, state="*")
async def read_my_menu_callback(callback_query : types.CallbackQuery, state : FSMContext):
    if state != CreateS.read_my_menu:
        await state.update_data(chat_id=callback_query.from_user.id)
        await state.update_data(user_id=callback_query.from_user.id)
        await CreateS.read_my_menu.set()
    # await bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    idx = int(callback_query.data.split('_')[-1])
    await state.update_data(task_type='my')
    await state.update_data(idx=idx)
    await state.update_data(to_edit=callback_query.message)
    task = await read_task_db(idx=idx)
    await fill_task_data(state=state, task=task)
    if task.status != 0:
        await callback_query.answer("Задача больше не доступна 🔒")
        return
    if callback_query.data.startswith('my-delete_'):
        await delete_task(state=state, delete_from='worker')
        return
    elif callback_query.data.startswith('my-add-comment_'):
        await CreateS.add_comment.set()
        await add_comment(state=state, add_from='worker')
    elif callback_query.data.startswith('comments_'):
        await CreateS.read_comments.set()
        await read_comments(state=state)
    else:
        await return_to_menu(state=state)

@dp.callback_query_handler(lambda c: c.data.split('_')[0] in CONTROL_TASKS_MENU, state="*")
async def read_control_menu_callback(callback_query : types.CallbackQuery, state : FSMContext):
    # await bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    idx = int(callback_query.data.split('_')[-1])
    if state != CreateS.read_control_menu:
        await state.update_data(chat_id=callback_query.from_user.id)
        await state.update_data(user_id=callback_query.from_user.id)
        await CreateS.read_control_menu.set()
    await state.update_data(task_type='control')
    await state.update_data(to_edit=callback_query.message)
    await state.update_data(idx=idx)

    task = await read_task_db(idx=idx)
    await fill_task_data(state=state, task=task)
    if task.status == 2:
        await callback_query.answer("Задача больше не доступна 🔒")
        return
    if callback_query.data.startswith('update_'):
        await CreateS.update.set()
        await bot.send_message(chat_id, "Выберите параметр для изменения", reply_markup=inline_kb_update)
    elif callback_query.data.startswith('control-delete_'):
        await delete_task(state=state, delete_from='creator')
        return
    elif callback_query.data.startswith('control-add-comment_'):
        await CreateS.add_comment.set()
        await add_comment(state=state, add_from='creator')
    elif callback_query.data.startswith('comments_'):
        await CreateS.read_comments.set()
        await read_comments(state=state)
    else:
        await return_to_menu(state=state)

@dp.callback_query_handler(lambda c: c.data.startswith('approve_') or c.data.startswith('reject_'), state="*")
async def approve_handler(callback_query : types.CallbackQuery, state : FSMContext):
    request = callback_query.data.split('_')
    chat_id = callback_query.from_user.id
    idx = int(request[1])
    await state.update_data(task_type='control')
    await state.update_data(idx=idx)
    await state.update_data(chat_id=chat_id)
    await state.update_data(chat_id=chat_id)
    if request[0] == 'approve':
        await delete_task(state=state, delete_from='creator')
        await bot.send_message(chat_id, "Запрос на завершение одобрен!")
    elif request[0] == 'reject':
        await reject_approve_task_db(idx=idx)
        await bot.send_message(chat_id, "Запрос на завершение отклонён")
    await bot.delete_message(chat_id=chat_id, message_id=callback_query.message.message_id)
    