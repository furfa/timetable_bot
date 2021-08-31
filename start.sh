#/bin/bash

pip install poetry

poetry install

(trap 'kill 0' INT; (cd backend && poetry run ./manage.py runserver 0.0.0.0:8000 --insecure) & (cd frontend && poetry run ./main.py) )
