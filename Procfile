release: python manage.py migrate
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker queueapp.asgi:application --log-file -
worker: python manage.py runworker