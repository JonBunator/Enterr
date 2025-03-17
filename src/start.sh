#!/bin/bash

# Start Xvfb on display :99
Xvfb -ac :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &

sleep 3

# Note: More than 1 worker is not supported with socketio
exec gunicorn main:app -b 0.0.0.0:7653 -w 1 --worker-class eventlet
