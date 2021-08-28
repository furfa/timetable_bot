from aiogram import types
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from loguru import logger

from . data_tools import reg_user


class RegisterMiddleware(BaseMiddleware):

    def init(self, *args, **kwargs):
        super(RegisterMiddleware, self).init(*args, **kwargs)

    async def on_pre_process_message(self, message: types.Message, data: dict):
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name

        resp_json = await reg_user(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name
            )

        logger.info(f"update user {resp_json}")
            
        if not resp_json["is_staff"]:  
            await message.reply("🤦 Администратор не разрешил вам пользоваться ботом. Попросите, чтобы он поставил вам статус персонала и снова напишите /start.")
            raise CancelHandler()