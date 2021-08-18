"""
    Functions that implements CRUD of all objects from DB
"""
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
        worker      : str,
        creator     : int,
        comments    : list[str]
    ) -> None:
        self.idx = reserve_one()
        self.description = description
        self.deadline = deadline
        self.worker = worker
        self.creator = creator
        self.comments = comments

data = []

def create_task_db(
        description : str,
        deadline,
        worker      : str,
        creator     : int,
        comment     : str
):
    comments = []
    if comment != '':
        comments.append(comment)
    data.append(
        Task(
            description=description,
            deadline=deadline,
            worker=worker,
            creator=creator,
            comments=comments
        )
    )

def read_my_tasks_db(user_id : int):
    return data

def read_control_tasks_db(user_id : int):
    return data

def read_task_db(idx : int):
    for task in data:
        if task.idx == idx:
            return task
    return None

def update_task_db():
    pass

def read_comments_db(idx : int, user_id : int):
    comments = []
    for task in data:
        if task.idx == idx and (task.worker == user_id or task.creator == user_id):
            for comment in task.comments:
                comments.append(comment)
            break
    return comments

def read_comment_db(idx : int, comment_idx : int, user_id : int):
    comments = []
    for task in data:
        if task.idx == idx and (task.worker == user_id or task.creator == user_id):
            if comment_idx < len(task.comments):
                return task.comments[comment_idx]
            break
    return None

def add_comment_db(idx : int, user_id : int, comment : str):
    for task in data:
        if task.idx == idx and (task.worker == user_id or task.creator == user_id):
            task.comments.append(comment)

def delete_comment_db(idx : int, user_id : int, comment_idx : int):
    for task in data:
        if task.idx == idx and (task.worker == user_id or task.creator == user_id):
            if comment_idx < len(task.comments):
                task.comments.remove(task.comments[comment_idx])

def delete_task_db(idx : int):
    for task in data:
        if task.idx == idx:
            data.remove(task)
            return True
    return False
