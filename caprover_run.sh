#!/bin/sh

python manage.py collectstatic --noinput
python manage.py migrate
gunicorn -w 4 -k uvicorn.workers.UvicornWorker queueapp.asgi:application