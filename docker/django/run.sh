#!/bin/bash

echo "-- wait-for-it --"
./wait-for-it.sh "${DB_IP}:${DB_PORT}" --strict --timeout=300 -- ./django.sh
echo ====================================