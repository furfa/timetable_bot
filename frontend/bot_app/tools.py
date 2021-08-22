from . data_tools import username_to_id_db, id_to_username_db


async def username_to_id(username : str):
    return await username_to_id_db(username=username)

async def id_to_username(user_id : int):
    return await id_to_username_db(user_id=user_id)
