from . config import API_KEY
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


bot = Bot(token=API_KEY)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
