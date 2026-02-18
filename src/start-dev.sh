#!/bin/bash

# Start Xvfb on display :99
Xvfb -ac :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &

sleep 1

# Start Vite dev server in background
cd /app/frontend
npm run start -- --host &

# Start uvicorn with hot reload
cd /app/backend
exec uvicorn main:app --host 0.0.0.0 --port 7653 --reload --reload-dir /app/backend/src
