#!/bin/bash

if [ "$1" = "create_user" ]; then
    shift
    exec python /app/backend/src/user_management.py "$@"
else
    exec "$@"
fi
