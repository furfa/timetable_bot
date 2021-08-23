from . keyboards import get_task_markup, get_task_approve_keyboard
from . data_tools import *
from . tools import username_to_id

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

async def format_task_card_text(
    idx,
    description,
    deadline,
    worker_username,
    creator_username,
    ):
    emoji = get_emoji_by_idx(idx)
    comments = await read_comments_db(idx=idx)
    comments_users = await read_comments_users_db(idx=idx)

    worker_id = await username_to_id(worker_username)
    creator_id = await username_to_id(creator_username)

    for comment_idx, comment in enumerate(comments):
        if comment_idx >= len(comments_users):
            comments[comment_idx] = f"⚙️ (admin) {comment}"
        elif worker_id == comments_users[comment_idx]:
            comments[comment_idx] = f"🔹 {comment}"
        elif creator_id == comments_users[comment_idx]:
            comments[comment_idx] = f"🔸 {comment}"
        else:
            comments[comment_idx] = f"⚙️ (admin) {comment}"

    comments_text = '\n'.join([''] + comments)
    return f"""
{emoji} Номер: {idx}
Описание: {description}
Дедлайн: {deadline: %d/%m/%Y %H:%M}
Исполнитель 🔹 @{worker_username}
Контролирующий 🔸 @{creator_username}
""" + comments_text

def format_task_card_markup(
    idx,
    task_permissions
    ):
    if task_permissions == 'approve':
        return get_task_approve_keyboard(idx=idx)
    return get_task_markup(idx=idx, task_permissions=task_permissions)

