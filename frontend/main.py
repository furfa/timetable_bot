#!/usr/bin/env python
import asyncio
from aiogram import executor
from concurrent.futures import ThreadPoolExecutor
from loguru import logger


from bot_app import dp

from bot_app.data_tools import get_task_for_notify, mark_task_notified
from bot_app.notiflicate import notiflication_for_worker


async def notiflicate():
    while True:
        try:
            tasks_idxs = await get_task_for_notify()
            logger.info(f"Tasks for notify {tasks_idxs}")
            for task_idx in tasks_idxs:
                status = await notiflication_for_worker(task_idx=task_idx)
                if status:
                    await mark_task_notified(task_idx)
        except Exception as e:
            logger.error(f"{type(e)}, {e}")
        await asyncio.sleep(30)


if __name__ == '__main__':

    # Notiflications
    loop = asyncio.get_event_loop()
    wait_complete_task = loop.create_task(notiflicate())

    # Bot
    executor.start_polling(dp, skip_updates=True)
    exit(0)