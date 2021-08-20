import telethon
from pathlib import Path


FILE_PATH = Path(__file__).resolve().parent
client = telethon.TelegramClient(
    str(FILE_PATH / "sessions" / "12482787387.session"),
    1,
    "b6b154c3707471f5339bd661645ed3d6",
)

async def username_to_id(username : str):
    await client.connect()
    entity_id = None
    try:
        entity = await client.get_entity(username)
        entity_id = entity.id
    except Exception as e:
        print(e)
        pass
    return entity_id

async def id_to_username(user_id : int):
    await client.connect()
    entity_username = None
    try:
        entity = await client.get_entity(user_id)
        entity_username = entity.username
    except Exception as e:
        print(e)
        pass
    return entity_username


# Саша ну ты посмотри что он исполняет, это просто шок)
# TODO
def alias_to_id(alias : str) -> int:
    return hash(str) % 2147483648
