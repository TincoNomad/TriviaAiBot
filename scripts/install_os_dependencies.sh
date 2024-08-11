#!/usr/bin/env bash

apt update -y
apt install -y software-properties-common
add-apt-repository ppa:deadsnakes/ppa -y
apt install -y build-essential python3.9 python3.9-venv