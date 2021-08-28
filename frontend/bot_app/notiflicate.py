from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from parse import *

from . app import dp, bot
from . writing_tools import format_task_card_text, format_task_card_markup
from . keyboards import get_task_approve_keyboard, keyboard_kb_menu
from . data_tools import read_task_db, id_to_username_db

async def send_shadow(chat_id: int):
    await bot.send_message(chat_id, "Выберите действие", reply_markup=keyboard_kb_menu, parse_mode="HTML")

async def write_to_worker(state : FSMContext, initiator_markup=keyboard_kb_menu):
    async with state.proxy() as data:
        idx = data['idx']
        initiator_id = data['initiator']
    task = await read_task_db(idx=idx)
    description = task.description
    deadline = task.deadline
    worker_id = task.worker
    creator_id = task.creator
    worker = await id_to_username_db(worker_id)
    creator = await id_to_username_db(creator_id)

    notify_text = await format_task_card_text(
        idx=idx,
        description=description,
        deadline=deadline,
        worker_username=worker,
        creator_username=creator
    )
    notify_markup = format_task_card_markup(idx=idx, task_permissions='my')

    try:
        await bot.send_message(worker_id, '👋 Вам поставлена новая задача:\n' + notify_text, reply_markup=notify_markup, parse_mode="HTML")
        await send_shadow(worker_id)
        await bot.send_message(initiator_id, notify_text, reply_markup=initiator_markup, parse_mode="HTML")
    except:
        await bot.send_message(initiator_id, f"🙉 Пользователь @{worker} не зарегистрирован, не могу уведомить его", reply_markup=initiator_markup, parse_mode="HTML")


async def action_for_worker(task_idx : int, prefix_text : str):
    task = await read_task_db(idx=task_idx)

    idx = task.idx
    description = task.description
    deadline = task.deadline
    worker_id = task.worker
    creator_id = task.creator
    worker = await id_to_username_db(worker_id)
    creator = await id_to_username_db(creator_id)
    
    notify_text = f'{prefix_text}\n' + await format_task_card_text(
        idx=idx,
        description=description,
        deadline=deadline,
        worker_username=worker,
        creator_username=creator
    )
    notify_markup = format_task_card_markup(idx=idx, task_permissions='my')
    await bot.send_message(worker_id, notify_text,  reply_markup=keyboard_kb_menu, parse_mode="HTML")


async def notiflication_for_worker(task_idx : int):
    try:
        await action_for_worker(task_idx=task_idx, prefix_text="🗓 У вас новое уведомление")
        return True
    except:
        return False

async def action_by_creator(state : FSMContext, prefix_text : str):
    async with state.proxy() as data:
        idx = data['idx']
    task = await read_task_db(idx=idx)
    description = task.description
    deadline = task.deadline
    worker_id = task.worker
    creator_id = task.creator
    worker = await id_to_username_db(worker_id)
    creator = await id_to_username_db(creator_id)

    notify_text = f'{prefix_text}\n' + await format_task_card_text(
        idx=idx,
        description=description,
        deadline=deadline,
        worker_username=worker,
        creator_username=creator
    )
    notify_markup = format_task_card_markup(idx=idx, task_permissions='my')

    try:
        await bot.send_message(worker_id, notify_text,  reply_markup=keyboard_kb_menu, parse_mode="HTML")
        await bot.send_message(creator_id, f"@{worker} получил уведомление 🔔", reply_markup=keyboard_kb_menu, parse_mode="HTML")
    except:
        await bot.send_message(creator_id, f"🙉 Пользователь @{worker} не зарегистрирован, не могу уведомить его", reply_markup=keyboard_kb_menu, parse_mode="HTML")


async def task_closed_by_creator(state : FSMContext):
    await action_by_creator(state=state, prefix_text='👏 Задача выполнена!')

async def add_comment_from_creator(state : FSMContext):
    await action_by_creator(state=state, prefix_text='📬 Новый комментарий по задаче')

async def update_deadline_from_creator(state : FSMContext):
    await action_by_creator(state=state, prefix_text='📆 Сроки выполнения задачи были изменены')

async def action_by_worker(state : FSMContext, prefix_text : str, notify_markup=None):
    async with state.proxy() as data:
        idx = data['idx']
    task = await read_task_db(idx=idx)
    description = task.description
    deadline = task.deadline
    worker_id = task.worker
    creator_id = task.creator
    worker = await id_to_username_db(worker_id)
    creator = await id_to_username_db(creator_id)

    notify_text = f'{prefix_text}\n' + await format_task_card_text(
        idx=idx,
        description=description,
        deadline=deadline,
        worker_username=worker,
        creator_username=creator
    )
    notify_markup = notify_markup

    try:
        await bot.send_message(creator_id, notify_text, reply_markup=notify_markup, parse_mode="HTML")
        await bot.send_message(worker_id, f"@{creator} получил уведомление 🔔", reply_markup=keyboard_kb_menu, parse_mode="HTML")
    except:
        await bot.send_message(worker_id, f"🙉 Пользователь @{creator} не зарегистрирован, не могу уведомить его", reply_markup=keyboard_kb_menu, parse_mode="HTML")


async def task_closed_by_worker(state : FSMContext):
    async with state.proxy() as data:
        idx = data['idx']
    await action_by_worker(
        state=state,
        prefix_text='👏 Задача ждет подтверждения!',
        notify_markup=get_task_approve_keyboard(idx=idx)
    )

async def add_comment_from_worker(state : FSMContext):
    await action_by_worker(state=state, prefix_text='📬 Новый комментарий по задаче')

async def update_deadline_from_worker(state : FSMContext):
    await action_by_worker(state=state, prefix_text='📆 Исполнитель перенес сроки выполнения задачи')

