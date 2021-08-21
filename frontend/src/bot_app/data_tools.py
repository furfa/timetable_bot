"""
    Functions that implements CRUD of all objects from DB
"""
import aiohttp
import json
from datetime import datetime
from django.core.serializers.json import DjangoJSONEncoder

DEFAULT_URL = 'http://localhost:8000/'


tasks_count = -1
def reserve_one():
    global tasks_count
    tasks_count += 1
    return tasks_count

class Task:

    def __init__(
        self,
        description : str,
        deadline,
        worker      : int,
        creator     : int,
        comments    : list[str],
        idx         : int = None
    ) -> None:
        if idx is None:
            idx = reserve_one()
        self.idx = idx
        self.description = description
        self.deadline = deadline
        self.worker = worker
        self.creator = creator
        self.comments = comments

data = []

async def reg_user(user_id : int):
    async with aiohttp.ClientSession() as session:
        async with session.post(DEFAULT_URL + 'user/', json={
            'telegram_id': user_id
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
            'deadline': deadline.isoformat(),
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

async def read_tasks_db_by_type(user_id : int, task_type : str):
    if user_id is None:
        return []
    if task_type not in ('creator', 'worker'):
        return []
    async with aiohttp.ClientSession() as session:
        headers = {'content-type': 'application/json'}
        async with session.get(DEFAULT_URL + f'user_{task_type}_tasks/{user_id}', headers=headers) as resp:
            back_tasks = await resp.json()
        tasks = []
        for item in back_tasks:
            async with session.get(DEFAULT_URL + f'task_comments/{item["pk"]}', headers=headers) as resp:
                back_comments = await resp.json()
            comments = [ x['text'] for x in back_comments ]
            tasks.append(Task(
                idx=item['pk'],
                description=item['description'],
                deadline=datetime.strptime(item['deadline'], "%Y-%m-%dT%H:%M:%SZ"),
                worker=item['worker']['telegram_id'],
                creator=item['creator']['telegram_id'],
                comments=comments
            )
            )
        return tasks

async def read_my_tasks_db(user_id : int):
    return await read_tasks_db_by_type(user_id=user_id, task_type='worker')

async def read_control_tasks_db(user_id : int):
    return await read_tasks_db_by_type(user_id=user_id, task_type='creator')

async def read_task_db(idx : int):
    async with aiohttp.ClientSession() as session:
        headers = {'content-type': 'application/json'}
        async with session.get(DEFAULT_URL + f'task/{idx}', headers=headers) as resp:
            response = await resp.json()
            print(response)
        async with session.get(DEFAULT_URL + f'task_comments/{response["pk"]}', headers=headers) as resp:
                back_comments = await resp.json()
        comments = [ x['text'] for x in back_comments ]
    task = Task(
                idx=response['pk'],
                description=response['description'],
                deadline=datetime.strptime(response['deadline'], "%Y-%m-%dT%H:%M:%SZ"),
                worker=response['worker']['telegram_id'],
                creator=response['creator']['telegram_id'],
                comments=comments
            )
    return task

def update_task_db():
    pass

def update_description_db(idx : int, user_id : int, description : str):
    for task in data:
        if task.idx == idx and task.creator == user_id:
            task.description = description
            break

def update_deadline_db(idx : int, user_id : int, deadline):
    for task in data:
        if task.idx == idx and task.creator == user_id:
            task.deadline = deadline
            break

def update_worker_db(idx : int, user_id : int, worker : int):
    for task in data:
        if task.idx == idx and task.creator == user_id:
            task.worker = worker
            break

def update_creator_db(idx : int, user_id : int, creator : int):
    for task in data:
        if task.idx == idx and task.creator == user_id:
            task.creator = creator
            break

async def read_comments_db(idx : int, user_id : int):
    task = await read_task_db(idx=idx)
    return task.comments

async def read_comment_db(idx : int, comment_idx : int, user_id : int):
    comments = await read_comments_db(idx=idx, user_id=user_id)
    return comments[comment_idx]

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

def delete_comment_db(idx : int, user_id : int, comment_idx : int):
    for task in data:
        if task.idx == idx and (task.worker == user_id or task.creator == user_id):
            if comment_idx < len(task.comments):
                task.comments.remove(task.comments[comment_idx])

async def delete_task_db(idx : int):
    async with aiohttp.ClientSession() as session:
        headers = {'content-type': 'application/json'}
        content = {
            'done': True
        }
        async with session.put(DEFAULT_URL + f'task/{idx}', json=content, headers=headers) as resp:
            task = await resp.json()
            print(task)
