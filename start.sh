#!/bin/bash
python manage.py createsuperuser --noinput
python manage.py makemigrations mapnotes
python manage.py migrate
python manage.py runserver 0.0.0.0:8080