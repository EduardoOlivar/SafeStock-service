#!/bin/bash

echo "-- MakeMigrations --"
python manage.py makemigrations api
echo ====================================

echo "-- Migrate --"
python manage.py migrate
echo ====================================

echo "-- Scripts --"
python manage.py shell < Scripts/preload_categories.py
echo ====================================

echo "-- Server --"
python manage.py runserver 0.0.0.0:8000