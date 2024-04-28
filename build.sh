#!/usr/bin/env bash
# exit on error

set -o errexit

pip install --upgrade pip setuptools wheel

sudo apt-get install portaudio19-dev

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate