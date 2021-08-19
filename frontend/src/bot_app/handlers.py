"""
    Definition of all private handlers,
    Handle:
        - Commands from commands.py
        - Keyboards chooses 
"""
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


MENU_INTERFACE = [
    'create',                   # C
    'read_control', 'read_my',  # R
    'update',                   # U
    'delete'                    # D
]

CONTROL_MENU_INTERFACE = [
    'update',
    'delete',
    'add_comment',
    'comments'
]

MY_MENU_INTERFACE = [
    'add_comment',
    'comments'
]

LIST_INTERFACE = [
    'menu',
    'next',
    'previous'
]

UPDATE_INTERFACE = [
    'menu',
    'description',
    'deadline',
    'worker',
    'creator',
    'comments'
]

TASK_PREFIX = "task_"
COMMENT_PREFIX = "comment_"

async def return_to_menu(chat_id : int, menu_title : str ="Меню"):
    await CreateS.menu.set()
    message = await bot.send_message(chat_id, menu_title, reply_markup=inline_kb_menu)

async def create_init(chat_id : int):
    await CreateS.create_description.set()
    await bot.send_message(chat_id, "Введите описание задачи")

async def empty_list(chat_id : int):
    await return_to_menu(chat_id=chat_id, menu_title="Список пуст")

async def read_control_init(chat_id : int, state : FSMContext):
    await CreateS.read_control_awaiting_idx.set()
    tasks = read_control_tasks_db(chat_id)
    if not tasks:
        await empty_list(chat_id=chat_id)
        return
    custom_markup = get_tasks_markup(tasks_list=tasks, page=0)
    message = await bot.send_message(chat_id, "Выберите задачу", reply_markup=custom_markup)
    async with state.proxy() as data:
        data['message_id'] = message.message_id
        data['page'] = 0

async def read_my_init(chat_id : int, state : FSMContext):
    await CreateS.read_my_awaiting_idx.set()
    tasks = read_my_tasks_db(chat_id)
    if not tasks:
        await empty_list(chat_id=chat_id)
        return
    custom_markup = get_tasks_markup(tasks_list=tasks, page=0)
    message = await bot.send_message(chat_id, "Выберите задачу", reply_markup=custom_markup)
    async with state.proxy() as data:
        data['message_id'] = message.message_id
        data['page'] = 0

@dp.callback_query_handler(lambda c: c.data in LIST_INTERFACE or c.data.startswith(TASK_PREFIX), state=CreateS.read_control_awaiting_idx)
async def read_control_callback(callback_query : types.CallbackQuery, state : FSMContext):
    await bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if callback_query.data in LIST_INTERFACE:
        async with state.proxy() as data:
            message_id = data['message_id']
            page = data['page']
        tasks = read_control_tasks_db(chat_id)
        if callback_query.data == 'menu':
            await return_to_menu(chat_id=chat_id)
        elif callback_query.data == 'next':
            custom_markup = get_tasks_markup(tasks_list=tasks, page=page + 1)
            await state.update_data(page=page + 1)
            await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=custom_markup)
        elif callback_query.data == 'previous':
            custom_markup = get_tasks_markup(tasks_list=tasks, page=page - 1)
            await state.update_data(page=page - 1)
            await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=custom_markup)
    else:
        idx = int(callback_query.data.removeprefix(TASK_PREFIX))
        async with state.proxy() as data:
            data['idx'] = idx
        await read_by_idx(chat_id=chat_id, idx=idx, task_permissions='control', state=state)

@dp.callback_query_handler(lambda c: c.data in LIST_INTERFACE or c.data.startswith(TASK_PREFIX), state=CreateS.read_my_awaiting_idx)
async def read_my_callback(callback_query : types.CallbackQuery, state : FSMContext):
    await bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if callback_query.data in LIST_INTERFACE:
        async with state.proxy() as data:
            message_id = data['message_id']
            page = data['page']
        tasks = read_control_tasks_db(chat_id)
        if callback_query.data == 'menu':
            await return_to_menu(chat_id=chat_id)
        elif callback_query.data == 'next':
            custom_markup = get_tasks_markup(tasks_list=tasks, page=page + 1)
            await state.update_data(page=page + 1)
            await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=custom_markup)
        elif callback_query.data == 'previous':
            custom_markup = get_tasks_markup(tasks_list=tasks, page=page - 1)
            await state.update_data(page=page - 1)
            await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=custom_markup)
    else:
        idx = int(callback_query.data.removeprefix(TASK_PREFIX))
        async with state.proxy() as data:
            data['idx'] = idx
        await read_by_idx(chat_id=chat_id, idx=idx, task_permissions='my', state=state)

async def read_by_idx(chat_id : int, idx : int, task_permissions : str, state : FSMContext):
    task = read_task_db(idx=idx)
    await state.update_data(idx=idx)
    if task is None:
        await bot.send_message(chat_id, "Не существует задачи с таким именем")
        return
    custom_markup = None
    if task_permissions == 'control':
        custom_markup = get_task_markup(task_permissions='control')
        await CreateS.read_control_menu.set()
    elif task_permissions == 'my':
        custom_markup = get_task_markup(task_permissions='my')
        await CreateS.read_my_menu.set()
    message = await bot.send_message(chat_id, f"""
Номер: {task.idx}
Описание: {task.description}
Дедлайн: {task.deadline}
Исполнитель: {task.worker}
""", reply_markup=custom_markup
    )


@dp.callback_query_handler(lambda c: c.data in UPDATE_INTERFACE, state=CreateS.update)
async def update_task_callback(callback_query : types.CallbackQuery, state : FSMContext):
    await bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if callback_query.data == 'menu':
        await return_to_menu(chat_id=chat_id)
    elif callback_query.data == 'description':
        await CreateS.update_description.set()
        await bot.send_message(chat_id, "Введите новое описание")
    elif callback_query.data == 'deadline':
        await CreateS.update_deadline.set()
        await bot.send_message(chat_id, "Введите новый дедлайн")
    elif callback_query.data == 'worker':
        await CreateS.update_worker.set()
        await bot.send_message(chat_id, "Введите нового исполнителя")
    elif callback_query.data == 'creator':
        await CreateS.update_creator.set()
        await bot.send_message(chat_id, "Введите нового заказчика")

@dp.message_handler(ChatTypeFilter('private'), state=CreateS.add_comment)
async def add_comment(message : types.Message, state : FSMContext):
    async with state.proxy() as data:
        data['comment'] = message.text
        idx = data['idx']
        user_id = message.from_user.id
        task_permissions = data['task_permissions']
        add_comment_db(idx=idx, user_id=user_id, comment=data['comment'])
    await read_by_idx(chat_id=message.chat.id, idx=idx, task_permissions=task_permissions, state=state)

async def read_comments(chat_id : int, state : FSMContext):
    async with state.proxy() as data:
        idx = data['idx']
        user_id = data['user_id']
    comments = read_comments_db(idx=idx, user_id=user_id)
    if not comments:
        await empty_list(chat_id=chat_id)
        return
    custom_markup = get_comments_markup(comments_list=comments, page=0)
    message = await bot.send_message(chat_id, "Выберите комментарий", reply_markup=custom_markup)
    async with state.proxy() as data:
        data['message_id'] = message.message_id
        data['comments_page'] = 0

async def read_comment(chat_id : int, state : FSMContext):
    async with state.proxy() as data:
        idx = data['idx']
        user_id = data['user_id']
        comment_idx = data['comment_idx']
    comment = read_comment_db(idx=idx, comment_idx=comment_idx, user_id=user_id)
    if comment is None:
        await bot.send_message(chat_id, "Не существует такого комментария")
        return
    await CreateS.read_comment.set()
    await bot.send_message(chat_id, comment, reply_markup=inline_kb_comment)

@dp.callback_query_handler(state=CreateS.read_comment)
async def read_comment_handler(callback_query : types.CallbackQuery, state : FSMContext):
    async with state.proxy() as data:
        idx = data['idx']
        user_id = data['user_id']
        comment_idx = data['comment_idx']
    await bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if callback_query.data == 'delete':
        delete_comment_db(idx=idx, user_id=user_id, comment_idx=comment_idx)
        await return_to_menu(chat_id=chat_id, menu_title="Удалено")
    else:
        await return_to_menu(chat_id=chat_id)
        return

@dp.callback_query_handler(lambda c: c.data in LIST_INTERFACE or c.data.startswith(COMMENT_PREFIX), state=CreateS.read_comments_awaiting_idx)
async def read_comments_callback(callback_query : types.CallbackQuery, state : FSMContext):
    await bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if callback_query.data in LIST_INTERFACE:
        async with state.proxy() as data:
            message_id = data['message_id']
            comments_page = data['comments_page']
            user_id = data['user_id']
            idx = data['idx']
        comments = read_comments_db(idx=idx, user_id=user_id)
        if callback_query.data == 'menu':
            await return_to_menu(chat_id=chat_id)
        elif callback_query.data == 'next':
            custom_markup = get_comments_markup(comments_list=comments, page=comments_page + 1)
            await state.update_data(comments_page=comments_page + 1)
            await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=custom_markup)
        elif callback_query.data == 'previous':
            custom_markup = get_comments_markup(comments_list=comments, page=comments_page - 1)
            await state.update_data(comments_page=comments_page - 1)
            await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=custom_markup)
    else:
        idx = int(callback_query.data.removeprefix(COMMENT_PREFIX))
        async with state.proxy() as data:
            data['comment_idx'] = idx
        await read_comment(chat_id=chat_id, state=state)


@dp.callback_query_handler(lambda c: c.data in CONTROL_MENU_INTERFACE, state=CreateS.read_control_menu)
async def read_control_menu_callback(callback_query : types.CallbackQuery, state : FSMContext):
    await bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if callback_query.data == 'update':
        await CreateS.update.set()
        await bot.send_message(chat_id, "Выберите параметр для изменения", reply_markup=inline_kb_update)
    elif callback_query.data == 'delete':
        # TODO мейби вынести отдельно
        async with state.proxy() as data:
            idx = data['idx']
            status = delete_task_db(idx=idx)
            if status:
                await return_to_menu(chat_id=chat_id, menu_title='Задача удалена')
            else:
                await return_to_menu(chat_id=chat_id, menu_title='Задача не найдена')
            return
    elif callback_query.data == 'add_comment':
        await CreateS.add_comment.set()
        await state.update_data(task_permissions='control')
        await bot.send_message(chat_id, 'Введите комментарий')
    elif callback_query.data == 'comments':
        await CreateS.read_comments_awaiting_idx.set()
        await read_comments(chat_id=chat_id, state=state)
    else:
        await return_to_menu(chat_id)

@dp.callback_query_handler(lambda c: c.data in MY_MENU_INTERFACE, state=CreateS.read_my_menu)
async def read_my_menu_callback(callback_query : types.CallbackQuery, state : FSMContext):
    await bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if callback_query.data == 'add_comment':
        await CreateS.add_comment.set()
        await state.update_data(task_permissions='my')
        await bot.send_message(chat_id, 'Введите комментарий')
    elif callback_query.data == 'comments':
        await CreateS.read_comments_awaiting_idx.set()
        await read_comments(chat_id=chat_id, state=state)
    else:
        await return_to_menu(chat_id)

@dp.message_handler(ChatTypeFilter('private'), commands=["start", "menu"], state="*")
async def menu_handler(message: types.Message):
    await return_to_menu(chat_id=message.chat.id)

@dp.callback_query_handler(lambda c: c.data in MENU_INTERFACE, state=CreateS.menu)
async def menu_callback(callback_query : types.CallbackQuery, state : FSMContext):
    await bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    await state.update_data(user_id=chat_id)
    async with state.proxy() as data:
        data['message_id'] = callback_query.message.message_id
    if callback_query.data == 'create':
        await create_init(chat_id=chat_id)
    elif callback_query.data == 'read_control':
        await read_control_init(chat_id=chat_id, state=state)
    elif callback_query.data == 'read_my':
        await read_my_init(chat_id=chat_id, state=state)
    else:
        return


@dp.message_handler(ChatTypeFilter('private'), commands="help")
async def create_task(message: types.Message):
    await bot.send_message(message.chat.id, f"""
👨‍💻 Для работы в личных сообщениях:
Помощь по командам: /help
Основное меню: /menu

👨‍💻 Для работы в группе:
Добавьте меня в группу и назначьте администратором,
Затем перешлите сообщение с описанием задачи и текст сообщения будет добавлен в качестве комментария
    """)


@dp.message_handler(ChatTypeFilter('private'), commands=CREATE_TASK_COMMAND)
async def create_task(message: types.Message):
    await create_init(chat_id=message.chat.id)


@dp.message_handler(state=CreateS.create_description)
async def hanle_description_create(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await CreateS.create_deadline.set()
    await bot.send_message(message.chat.id, "Введите время и дату дедлайна\nчч:мм дд.мм.гггг")

@dp.message_handler(state=CreateS.update_description)
async def hanle_description_update(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    async with state.proxy() as data:
        idx = data['idx']
        user_id = data['user_id']
        data['description'] = message.text
    update_description_db(idx=idx, user_id=user_id, description=message.text)
    await CreateS.update.set()
    await bot.send_message(chat_id, "Выберите параметр для изменения", reply_markup=inline_kb_update)

@dp.message_handler(state=CreateS.update_deadline)
async def hanle_deadline_update(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    date = None
    try:
        date = datetime.strptime(message.text, "%H:%M %d.%m.%Y") 
    except Exception as e:
        await message.reply('Некорректно введена дата, попробуйте еще раз')
        return

    async with state.proxy() as data:
        idx = data['idx']
        user_id = data['user_id']
        data['deadline'] = date
    update_deadline_db(idx=idx, user_id=user_id, deadline=date)
    await CreateS.update.set()
    await bot.send_message(chat_id, "Выберите параметр для изменения", reply_markup=inline_kb_update)

@dp.message_handler(state=CreateS.update_worker)
async def hanle_worker_update(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    async with state.proxy() as data:
        idx = data['idx']
        user_id = data['user_id']
        data['worker'] = message.text
    update_worker_db(idx=idx, user_id=user_id, worker=message.text)
    await CreateS.update.set()
    await bot.send_message(chat_id, "Выберите параметр для изменения", reply_markup=inline_kb_update)

@dp.message_handler(state=CreateS.update_creator)
async def hanle_worker_update(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    async with state.proxy() as data:
        idx = data['idx']
        user_id = data['user_id']
        data['creator'] = message.text
    update_creator_db(idx=idx, user_id=user_id, creator=message.text)
    await CreateS.update.set()
    await bot.send_message(chat_id, "Выберите параметр для изменения", reply_markup=inline_kb_update)

@dp.message_handler(state=CreateS.create_deadline)
async def hanle_deadline_create(message: types.Message, state: FSMContext):
    date = None
    try:
        date = datetime.strptime(message.text, "%H:%M %d.%m.%Y") 
    except Exception as e:
        await message.reply('Некорректно введена дата, попробуйте еще раз')
        return

    async with state.proxy() as data:
        data['deadline'] = date
    await CreateS.create_comment.set()
    await bot.send_message(message.chat.id, "Введите комментарий", reply_markup=inline_kb_skip)


@dp.message_handler(state=CreateS.create_comment)
async def hanle_comment_create(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['comment'] = message.text
    await CreateS.create_worker.set()
    await bot.send_message(message.chat.id, "Введите alias исполнителя")


@dp.callback_query_handler(lambda c: c.data == 'skip', state=CreateS.create_comment)
async def skip_comment_callback(callback_query : types.CallbackQuery, state : FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.update_data(comment="")
    await CreateS.create_worker.set()
    await bot.send_message(callback_query.from_user.id, "Введите alias исполнителя")


@dp.message_handler(state=CreateS.create_worker)
async def hanle_worker_create(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['worker'] = message.text
        create_task_db(
            description=data['description'],
            deadline=data['deadline'],
            worker=data['worker'],
            creator=message.from_user.id,
            comment=data['comment']
        )
    await return_to_menu(chat_id=message.chat.id, menu_title="Задача создана")


@dp.message_handler(ChatTypeFilter('private'), commands=READ_CONTROL_TASK_COMMAND, state=CreateS.read_control_awaiting_idx)
async def read_task(message: types.Message):
    splited = message.text.split()
    if len(splited) != 2:
        await return_to_menu(chat_id=message.chat.id, menu_title="Некорректная команда")
        return
    idx = 0
    try:
        idx = int(splited[1])
    except Exception as e:
        await return_to_menu(chat_id=message.chat.id, menu_title="Некорректный индекс")
        return

    await read_by_idx(chat_id=message.chat.id, idx=idx, task_permissions='control', state=state)

async def update_task():
    pass

async def delete_task(chat_id : int, idx : int):
    pass