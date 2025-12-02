#!/bin/bash

# Start Xvfb on display :99
Xvfb -ac :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &

sleep 1

exec uvicorn main:app --host 0.0.0.0 --port 7653
