from . keyboards import get_task_markup

emojies = [
    '🍀',
    '🔮',
    '🍏',
    '🍐',
    '🍊',
    '🍋',
    '🍇',
    '🍒',
    '🍑'
]

def get_emoji_by_idx(idx : int):
    return emojies[idx % len(emojies)]

def format_task_card_text(
    idx,
    description,
    deadline,
    worker_username,
    creator_username,
    ):
    emoji = get_emoji_by_idx(idx)
    return f"""
{emoji} Номер: {idx}
Описание: {description}
Дедлайн: {deadline: %d/%m/%Y %H:%M}
Исполнитель: @{worker_username}
Контролирующий: @{creator_username}
"""

def format_task_card_markup(
    idx,
    task_permissions
    ):
    return get_task_markup(idx=idx, task_permissions=task_permissions)

