#!/usr/bin/env bash

cd /home/ubuntu/api
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt