#!/usr/bin/env bash

cd /home/ubuntu/api
source venv/bin/activate
nohup python manage.py runserver 0.0.0.0:8000 > /dev/null 2> /dev/null < /dev/null &