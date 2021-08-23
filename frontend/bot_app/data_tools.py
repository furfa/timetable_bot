"""
    Functions that implements CRUD of all objects from DB
"""
from backend import tasks
import aiohttp
import json
from datetime import datetime
from django.core.serializers.json import DjangoJSONEncoder

DEFAULT_URL = 'http://localhost:8000/'

class Task:

    def __init__(
        self,
        description : str,
        deadline,
        worker      : int,
        creator     : int,
        comments    : list[str],
        comments_users : list[int],
        idx         : int = None
    ) -> None:
        self.idx = idx
        self.description = description
        self.deadline = deadline
        self.worker = worker
        self.creator = creator
        self.comments = comments
        self.comments_users = comments_users
        self.status = 0


async def reg_user(user_id : int, username : str, first_name : str, last_name : str):
    async with aiohttp.ClientSession() as session:
        async with session.post(DEFAULT_URL + 'user/', json={
            'telegram_id': user_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name
        }) as resp:
            print(resp.status)

async def create_task_db(
        description : str,
        deadline,
        worker      : int,
        creator     : int,
):
    async with aiohttp.ClientSession() as session:
        content = {
            'description': description,
            'deadline': f"{deadline.isoformat()}+03:00",
            'worker': {
                'telegram_id': worker,
            },
            'creator': {
                'telegram_id': creator,
            },
        }
        
        headers = {'content-type': 'application/json'}
        async with session.post(DEFAULT_URL + 'task/', json=content, headers=headers) as resp:
            response = await resp.json()
            print(response)
    
    return response['pk']

def convert_date(date):
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S+03:00")

async def read_tasks_db_by_type(user_id : int, task_type : str):
    if user_id is None:
        return []
    if task_type not in ('creator', 'worker'):
        return []
    async with aiohttp.ClientSession() as session:
        headers = {'content-type': 'application/json'}
        async with session.get(DEFAULT_URL + f'user_{task_type}_tasks/{user_id}', headers=headers) as resp:
            status = resp.status
            if status == 404:
                print('Catched 404 fuck yeah')
            back_tasks = await resp.json()
        tasks = []
        for item in back_tasks:
            async with session.get(DEFAULT_URL + f'task_comments/{item["pk"]}', headers=headers) as resp:
                back_comments = await resp.json()
            comments = [ x['text'] for x in back_comments ]
            comments_users = [ x['creator']['telegram_id'] for x in back_comments ]
            task = Task(
                idx=item['pk'],
                description=item['description'],
                deadline=convert_date(item['deadline']),
                worker=item['worker']['telegram_id'],
                creator=item['creator']['telegram_id'],
                comments=comments,
                comments_users=comments_users
            )
            task.status = item['status']
            tasks.append(task)
        return tasks

async def read_my_tasks_db(user_id : int):
    return await read_tasks_db_by_type(user_id=user_id, task_type='worker')

async def read_control_tasks_db(user_id : int):
    task = await read_tasks_db_by_type(user_id=user_id, task_type='creator')
    usual_tasks = []
    approve_tasks = []
    for task in tasks:
        if task.status == 0:
            usual_tasks.append(task)
        elif task.status == 1:
            approve_tasks.append(task)
    return usual_tasks, approve_tasks

async def read_task_db(idx : int):
    async with aiohttp.ClientSession() as session:
        headers = {'content-type': 'application/json'}
        async with session.get(DEFAULT_URL + f'task/{idx}', headers=headers) as resp:
            response = await resp.json()
            print(response)
        async with session.get(DEFAULT_URL + f'task_comments/{response["pk"]}', headers=headers) as resp:
                back_comments = await resp.json()
        comments = [ x['text'] for x in back_comments ]
        comments_users = [ x['creator']['telegram_id'] for x in back_comments ]
    task = Task(
                idx=response['pk'],
                description=response['description'],
                deadline=convert_date(response['deadline']),
                worker=response['worker']['telegram_id'],
                creator=response['creator']['telegram_id'],
                comments=comments,
                comments_users=comments_users
            )
    task.status = response['status']
    return task

async def read_comments_db(idx : int):
    task = await read_task_db(idx=idx)
    return task.comments

async def read_comments_users_db(idx : int):
    task = await read_task_db(idx=idx)
    return task.comments_users

async def read_comment_db(idx : int, comment_idx : int):
    comments = await read_comments_db(idx=idx)
    return comments[comment_idx]

async def read_comment_user_db(idx : int, comment_idx : int):
    comments = await read_comments_users_db(idx=idx)
    try:
        return comments[comment_idx]
    except Exception as e:
        return -1

async def add_comment_db(idx : int, user_id : int, comment : str):
    async with aiohttp.ClientSession() as session:
        headers = {'content-type': 'application/json'}
        content = {
            'creator': {
                'telegram_id': user_id
            },
            'text': comment
        }
        async with session.post(DEFAULT_URL + f'task_comments/{idx}', json=content, headers=headers) as resp:
            comment_resp = await resp.json()
            print(comment_resp)

async def read_user_json(user_id : int):
    async with aiohttp.ClientSession() as session:
        headers = {'content-type': 'application/json'}
        async with session.get(DEFAULT_URL + f'user/{user_id}', headers=headers) as resp:
            return await resp.json()

async def read_user_json_by_username(username : str):
    async with aiohttp.ClientSession() as session:
        headers = {'content-type': 'application/json'}
        async with session.get(DEFAULT_URL + f'user_by_username/{username}', headers=headers) as resp:
            return await resp.json()

async def id_to_username_db(user_id : int):
    user_json = await read_user_json(user_id=user_id)
    return user_json['username']

async def username_to_id_db(username : str):
    user_json = await read_user_json_by_username(username=username)
    return user_json['telegram_id']

async def delete_task_db(idx : int):
    async with aiohttp.ClientSession() as session:
        headers = {'content-type': 'application/json'}
        content = {
            'status': 2
        }
        async with session.put(DEFAULT_URL + f'task/{idx}', json=content, headers=headers) as resp:
            task = await resp.json()
            print(task)

async def wait_approve_task_db(idx : int):
    async with aiohttp.ClientSession() as session:
        headers = {'content-type': 'application/json'}
        content = {
            'status': 1
        }
        async with session.put(DEFAULT_URL + f'task/{idx}', json=content, headers=headers) as resp:
            task = await resp.json()
            print(task)

async def reject_approve_task_db(idx : int):
    async with aiohttp.ClientSession() as session:
        headers = {'content-type': 'application/json'}
        content = {
            'status': 0
        }
        async with session.put(DEFAULT_URL + f'task/{idx}', json=content, headers=headers) as resp:
            task = await resp.json()
            print(task)

async def mark_task_notified(task_idx : int):
    async with aiohttp.ClientSession() as session:
        headers = {'content-type': 'application/json'}
        async with session.get(DEFAULT_URL + f'task_mark_notifyed/{task_idx}', headers=headers) as resp:
            print(resp.status)

async def get_task_for_notify():
    async with aiohttp.ClientSession() as session:
        headers = {'content-type': 'application/json'}
        async with session.get(DEFAULT_URL + 'tasks_for_notify/', headers=headers) as resp:
            tasks = await resp.json()
            tasks_idxs = [ x['pk'] for x in tasks ]
            return tasks_idxs

