from aiogram.dispatcher.filters.state import State, StatesGroup


class CreateS(StatesGroup):
    menu = State()

    """
        Tasks CRUD
    """

    # Create
    create_description = State()
    create_deadline = State()
    create_worker = State()
    create_comment = State()

    # Read my
    read_my_awaiting_idx = State()
    read_my_idx = State()
    read_my_menu = State()

    # Read control
    read_control_awaiting_idx = State()
    read_control_idx = State()
    read_control_menu = State()

    # Delete
    delete = State()

    # Update
    update = State()
    update_description = State()
    update_deadline = State()
    update_worker = State()
    update_creator = State()

    """
        Comments CRUD
    """
    add_comment = State()
    read_comments_awaiting_idx = State()
    read_comment = State()
    delete_comment = State()
