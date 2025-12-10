#!/bin/bash

python manage.py migrate
python manage.py collectstatic --noinput
gunicorn 2p-griills-backend.wsgi:application --bind 0.0.0.0:$PORT
