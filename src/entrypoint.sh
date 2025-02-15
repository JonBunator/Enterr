#!/bin/bash

if [ "$1" = "create_user" ]; then
    shift
    exec python /app/backend/src/user_management.py create_user "$@"
elif [ "$1" = "set_password" ]; then
    shift
    exec python /app/backend/src/user_management.py set_password "$@"
elif [ "$1" = "delete_user" ]; then
    shift
    exec python /app/backend/src/user_management.py delete_user "$@"
else
    exec "$@"
fi
