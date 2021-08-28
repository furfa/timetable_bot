from . app import dp
from aiogram import types

@dp.message_handler(state="*")
async def handle_unknown(message : types.Message):
    await message.reply("🤦 Недопустимая команда. Чтобы узнать допустимые напишите /start")