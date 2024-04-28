#!/usr/bin/env bash
# exit on error

set -o errexit

while read p; do
  apt-get install -y "$p"
done <packages.txt

pip install --upgrade pip setuptools wheel

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate