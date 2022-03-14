#!/bin/bash
set -e

# Environment variable check
python ./util/check.py
# makemigrate should be commented out once we start deploying the app
python manage.py makemigrations mapnotes
python manage.py migrate
python manage.py createsuperuser --noinput || true
python manage.py init
#python manage.py uploadstatic --insecure

# python manage.py runserver 127.0.0.1:8000
python manage.py runserver 0.0.0.0:8000