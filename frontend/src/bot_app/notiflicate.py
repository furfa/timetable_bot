from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from parse import *

from . app import dp, bot
from . writing_tools import format_task_card_text, format_task_card_markup
from . keyboards import get_task_approve_button, keyboard_kb_menu

async def send_shadow(chat_id: int):
    await bot.send_message(chat_id, "Выберите действие", reply_markup=keyboard_kb_menu)

async def write_to_worker(state : FSMContext):
    async with state.proxy() as data:
        idx = data['idx']
        description = data['description']
        deadline = data['deadline']
        worker_id = data['worker']
        initiator_id = data['initiator']
        worker = data['worker_username']
        creator = data['creator_username']

        notify_text =format_task_card_text(
            idx=idx,
            description=description,
            deadline=deadline,
            worker_username=worker,
            creator_username=creator
        )
        notify_markup = format_task_card_markup(idx=idx, task_permissions='my')

    try:
        await bot.send_message(worker_id, '👋 Вам поставлена новая задача:\n' + notify_text, reply_markup=notify_markup)
        await send_shadow(worker_id)
        await bot.send_message(initiator_id, notify_text, reply_markup=keyboard_kb_menu)
    except:
        await bot.send_message(initiator_id, f"🙉 Пользователь @{worker} не зарегистрирован, не могу уведомить его", reply_markup=keyboard_kb_menu)

async def new_comment(reciever : int, comment : str):
    pass


async def task_closed_by_creator(state : FSMContext):
    async with state.proxy() as data:
        idx = data['idx']
        description = data['description']
        deadline = data['deadline']
        worker_id = data['worker']
        creator_id = data['creator']
        worker = data['worker_username']
        creator = data['creator_username']
        
        notify_text = '👏 Задача выполнена!\n' + format_task_card_text(
            idx=idx,
            description=description,
            deadline=deadline,
            worker_username=worker,
            creator_username=creator
        )
        notify_markup = format_task_card_markup(idx=idx, task_permissions='my')

    try:
        await bot.send_message(worker_id, notify_text,  reply_markup=keyboard_kb_menu)
        await bot.send_message(creator_id, f"@{worker} получил уведомление 🌈", reply_markup=keyboard_kb_menu)
    except:
        await bot.send_message(creator_id, f"🙉 Пользователь @{worker} не зарегистрирован, не могу уведомить его", reply_markup=keyboard_kb_menu)


async def task_closed_by_worker(state : FSMContext):
    async with state.proxy() as data:
        idx = data['idx']
        description = data['description']
        deadline = data['deadline']
        worker_id = data['worker']
        creator_id = data['creator']
        worker = data['worker_username']
        creator = data['creator_username']

        notify_text = '👏 Задача ждет подтверждения!\n' + format_task_card_text(
            idx=idx,
            description=description,
            deadline=deadline,
            worker_username=worker,
            creator_username=creator
        )
        notify_markup = get_task_approve_button(idx=idx)

    try:
        await bot.send_message(creator_id, notify_text, reply_markup=notify_markup)
        await bot.send_message(worker_id, f"@{creator} получил уведомление 🌈", reply_markup=keyboard_kb_menu)
    except:
        await bot.send_message(worker_id, f"🙉 Пользователь @{creator} не зарегистрирован, не могу уведомить его", reply_markup=keyboard_kb_menu)

