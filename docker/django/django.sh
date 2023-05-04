#!/bin/bash

echo "-- MakeMigrations --"
python manage.py makemigrations api
echo ====================================

echo "-- Migrate --"
python manage.py migrate
echo ====================================

echo "-- Server --"
python manage.py runserver 0.0.0.0:8000