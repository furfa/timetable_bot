from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from parse import *

from . app import dp, bot

async def write_to_worker(state : FSMContext):
    async with state.proxy() as data:
        idx = data['idx']
        description = data['description']
        deadline = data['deadline']
        worker_id = data['worker']
        initiator_id = data['initiator']
        worker = data['worker_username']
        creator = data['creator_username']

    try:
        await bot.send_message(worker_id, f"""
👋 Вам поставлена новая задача:

Номер: {idx}
Описание: {description}
Дедлайн: {deadline}
Исполнитель: @{worker}
Контролирующий: @{creator}
    """
        )
        await bot.send_message(initiator_id, f"""
Номер: {idx}
Описание: {description}
Дедлайн: {deadline}
Исполнитель: @{worker}
Контролирующий: @{creator}
    """
    )
    except:
        await bot.send_message(initiator_id, f"🙉 Пользователь @{worker} не зарегистрирован, не могу уведомить его")


async def task_closed_by_creator(state : FSMContext):
    async with state.proxy() as data:
        idx = data['idx']
        description = data['description']
        deadline = data['deadline']
        worker_id = data['worker']
        creator_id = data['creator']
        worker = data['worker_username']
        creator = data['creator_username']


    try:
        await bot.send_message(worker, f"""
👏 Задача выполнена!

Номер: {idx}
Описание: {description}
Дедлайн: {deadline}
Исполнитель: @{worker}
Контролирующий: @{creator}
    """
        )
        await bot.send_message(creator_id, f"""
@{worker} получил уведомление 🌈
    """
    )
    except:
        await bot.send_message(creator_id, f"🙉 Пользователь @{worker} не зарегистрирован, не могу уведомить его")


async def task_closed_by_worker(state : FSMContext):
    async with state.proxy() as data:
        idx = data['idx']
        description = data['description']
        deadline = data['deadline']
        worker_id = data['worker']
        creator_id = data['creator']
        worker = data['worker_username']
        creator = data['creator_username']


    try:
        await bot.send_message(creator_id, f"""
👏 Задача выполнена!

Номер: {idx}
Описание: {description}
Дедлайн: {deadline}
Исполнитель: @{worker}
Контролирующий: @{creator}
    """
        )
        await bot.send_message(worker_id, f"""
@{creator} получил уведомление 🌈 
    """
    )
    except:
        await bot.send_message(worker_id, f"🙉 Пользователь @{creator} не зарегистрирован, не могу уведомить его")

