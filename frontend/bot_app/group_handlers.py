"""
    Definition of all group handlers,
    Handle:
        - Forwarded messages from chats
"""
from os import read, stat
from aiogram import types
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import ForwardedMessageFilter, IDFilter, extract_chat_ids
from aiogram.types import chat, message
from datetime import datetime

from . data_tools import *
from . app import dp, bot


@dp.message_handler(ForwardedMessageFilter(True), state="*")
async def add_comment(message : types.Message):
    if message.forward_from.id != bot.id:
        return
    forward_text = message.values['text']
    idx = None
    for row in forward_text.split('\n'):
        if 'Номер: ' in row:
            idx = int(row.split()[1])
            break
    if idx is None:
        return
    await message.reply(f"Номер задачи: {idx}")
