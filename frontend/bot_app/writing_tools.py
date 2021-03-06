from . keyboards import get_task_markup, get_task_approve_keyboard
from . data_tools import *
from . tools import username_to_id

# from aiogram.utils.markdown import bold

emojies = [
    '๐',
    '๐ฎ',
    '๐',
    '๐',
    '๐',
    '๐',
    '๐',
    '๐น',
    '๐ป',
    '๐ผ',
    '๐',
    '๐บ',
    '๐ฅญ',
    '๐ผ',
    '๐ฐ',
    '๐ญ',
    '๐',
    'โพ',
    'โฝ',
    '๐ฑ',
    '๐',
    '๐',
    '๐',
    '๐ท',
    '๐ฟ',
    '๐',
    'โ',
    '๐',
    '๐ธ',
    '๐ฌ',
    '๐ชด',
    '๐ช',
    '๐ฉ',
    '๐ฅ',
    '๐พ',
    '๐ซ',
    '๐',
    '๐ง',
    '๐',
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
            comments[comment_idx] = f"โ๏ธ (admin) {comment}"
        elif worker_id == comments_users[comment_idx]:
            comments[comment_idx] = f"๐น {comment}"
        elif creator_id == comments_users[comment_idx]:
            comments[comment_idx] = f"๐ธ {comment}"
        else:
            comments[comment_idx] = f"โ๏ธ (admin) {comment}"

    comments_text = '\n'.join([''] + comments)
    return f"""
{emoji} ะะพะผะตั: {idx}
ะะฟะธัะฐะฝะธะต: <b>{description}</b>
ะะตะดะปะฐะนะฝ: {deadline: %d/%m/%Y %H:%M}
ะัะฟะพะปะฝะธัะตะปั ๐น @{worker_username}
ะะพะฝััะพะปะธััััะธะน ๐ธ @{creator_username}
""" + comments_text

def format_task_card_markup(
        idx,
        task_permissions
    ):
    if task_permissions == 'approve':
        return get_task_approve_keyboard(idx=idx)
    return get_task_markup(idx=idx, task_permissions=task_permissions)

