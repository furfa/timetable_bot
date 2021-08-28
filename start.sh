#/bin/bash

pip install poetry

poetry install

cd backend
poetry run ./manage.py runserver 0.0.0.0:8000&

cd ../frontend

poetry run ./main.py
