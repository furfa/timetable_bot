from typing import final
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.mixins import T


from . data_tools import Task
from . commands import *

"""
    Approve task markup
"""
def get_task_approve_keyboard(idx):
    approve_button = InlineKeyboardButton("Подтвердить", callback_data=f'approve_{idx}')
    reject_button = InlineKeyboardButton("Отклонить", callback_data=f'reject_{idx}')
    inline_kb_task_approve = InlineKeyboardMarkup()
    inline_kb_task_approve.row(approve_button, reject_button)
    return inline_kb_task_approve


"""
    Skip markup
"""
inline_button_skip = InlineKeyboardButton("Пропустить", callback_data='skip')
inline_kb_skip = InlineKeyboardMarkup()
inline_kb_skip.add(inline_button_skip)

"""
    Menu markup (Inline)
"""
inline_button_create = InlineKeyboardButton("Новая задача", callback_data='create')
inline_button_read_my = InlineKeyboardButton("Мои задачи", callback_data='read_my')
inline_button_read = InlineKeyboardButton("Задачи на контроле", callback_data='read_control')
inline_kb_menu = InlineKeyboardMarkup()
inline_kb_menu.add(inline_button_create)
inline_kb_menu.row(inline_button_read_my, inline_button_read)

"""
    Return to menu
"""
inline_button_return_to_menu = InlineKeyboardButton("К меню", callback_data='menu')
inline_kb_return_to_menu = InlineKeyboardMarkup()
inline_kb_return_to_menu.add(inline_button_return_to_menu)

"""
    Menu markup (Keyboard)
"""
keyboard_button_my = KeyboardButton(MY_TASKS_COMMAND)
keyboard_button_control = KeyboardButton(CONTROL_TASKS_COMMAND)
keyboard_kb_menu = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_kb_menu.row(keyboard_button_my, keyboard_button_control)

"""
    Tasks markup
"""

def get_task_button(text, idx):
    final_text = text[:50]
    if len(text) > 50:
        final_text += '...'
    return InlineKeyboardButton(f"[{idx}] {final_text}", callback_data=f'task_{idx}')


inline_button_next = InlineKeyboardButton("Дальше", callback_data='next')
inline_button_previous = InlineKeyboardButton("Назад", callback_data='previous')
inline_button_back_to_menu = InlineKeyboardButton("К меню", callback_data='menu')
def get_tasks_markup(tasks_list : list[Task], page=0, step=3):
        markup = InlineKeyboardMarkup()
        for task in tasks_list[page * step : page * step + step ]:
            markup.add(get_task_button(task.description, task.idx))
        markup.add(inline_button_back_to_menu)
        markup.row(inline_button_previous, inline_button_next)
        return markup


"""
    Task menu markup
"""

def get_task_markup(task_permissions : str, idx : int):
    # inline_button_task_update = InlineKeyboardButton("Редактировать", callback_data=f'update_{idx}')
    inline_button_task_delete = InlineKeyboardButton("Завершить", callback_data=f'control-delete_{idx}')
    inline_button_task_delete_ = InlineKeyboardButton("Готово!", callback_data=f'my-delete_{idx}')
    inline_button_task_comments = InlineKeyboardButton("Комментарии", callback_data=f'comments_{idx}')
    inline_button_task_add_comment = InlineKeyboardButton("Новый комментарий", callback_data=f'control-add-comment_{idx}')
    inline_button_task_add_comment_ = InlineKeyboardButton("Новый комментарий", callback_data=f'my-add-comment_{idx}')
    inline_button_task_reschedule = InlineKeyboardButton("Перенести", callback_data=f'control-reschedule_{idx}')
    inline_button_task_reschedule_ = InlineKeyboardButton("Перенести", callback_data=f'my-reschedule_{idx}')

    inline_kb_control_task = InlineKeyboardMarkup()
    inline_kb_my_task = InlineKeyboardMarkup()

    inline_kb_control_task.row(inline_button_task_add_comment, inline_button_task_reschedule, inline_button_task_delete)
    inline_kb_my_task.row(inline_button_task_add_comment_, inline_button_task_reschedule_, inline_button_task_delete_)
    if task_permissions == 'control':
        return inline_kb_control_task
    elif task_permissions == 'my':
        return inline_kb_my_task
    else:
        return None

"""
    Task update markup
"""
inline_button_description = InlineKeyboardButton("Описание", callback_data='description')
inline_button_deadline = InlineKeyboardButton("Дедлайн", callback_data='deadline')
inline_button_worker = InlineKeyboardButton("Исполнитель", callback_data='worker')
inline_button_creator = InlineKeyboardButton("Заказчик", callback_data='creator')

inline_kb_update = InlineKeyboardMarkup()
inline_kb_update.add(inline_button_back_to_menu)
inline_kb_update.row(inline_button_description, inline_button_deadline)
inline_kb_update.row(inline_button_worker, inline_button_creator)

"""
    Comments markup
"""
def get_comment_button(text, idx):
    final_text = text[:50]
    if len(text) > 50:
        final_text += '...'
    return InlineKeyboardButton(f"{idx}. {final_text}", callback_data=f'comment_{idx}')


inline_button_next = InlineKeyboardButton("Дальше", callback_data='next')
inline_button_previous = InlineKeyboardButton("Назад", callback_data='previous')
inline_button_back_to_menu = InlineKeyboardButton("К меню", callback_data='menu')
def get_comments_markup(comments_list : list[str], page=0, step=3):
        markup = InlineKeyboardMarkup()
        idx = page * step
        for comment in comments_list[page * step : page * step + step ]:
            markup.add(get_comment_button(comment, idx))
            idx += 1
        markup.add(inline_button_back_to_menu)
        markup.row(inline_button_previous, inline_button_next)
        return markup

inline_button_delete = InlineKeyboardButton("Удалить", callback_data='delete')
inline_kb_comment = InlineKeyboardMarkup()
inline_kb_comment.add(inline_button_delete)
