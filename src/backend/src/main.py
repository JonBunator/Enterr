import asyncio
import socketio
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from jose import JWTError, jwt
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from endpoints.webhooks.socketio import sio
from execution.notifications.notification_manager import NotificationManager
from dataAccess.data_access_internal import DataAccessInternal
from user_management import create_user
from dataAccess.data_access import DataAccess
from dataAccess.database.database import init_db, User, get_session
from dotenv import load_dotenv
from dataAccess.database.database_events import register_database_events
from endpoints.rest_endpoints import register_rest_endpoints
from endpoints.webhooks.webhook_endpoints import WebhookEndpoints
from execution.scheduler import Scheduler

load_dotenv()
dev_mode = os.getenv("RUN_MODE") != "production"

# Initialize database and services
init_db()
if dev_mode or True:
    create_user(username="debug", password="123", create_db=False)

event_loop = asyncio.get_event_loop()
webhook_endpoints = WebhookEndpoints(event_loop=event_loop)
data_access = DataAccess(webhook_endpoints=webhook_endpoints)
data_access_internal = DataAccessInternal(webhook_endpoints=webhook_endpoints)
notification_manager = NotificationManager(data_access=data_access_internal)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = Scheduler(data_access_internal=data_access_internal, webhook_endpoints=webhook_endpoints)
    register_database_events(
        scheduler=scheduler, notification_manager=notification_manager
    )
    try:
        scheduler.start()
        yield
    finally:
        scheduler.stop()


app = FastAPI(lifespan=lifespan)

if dev_mode:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

sio.register_namespace(WebhookEndpoints("/"))
sio_asgi_app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app)
app.add_route("/socket.io/", route=sio_asgi_app, methods=["GET", "POST"])
app.add_websocket_route("/socket.io/", sio_asgi_app)

register_rest_endpoints(
    app=app, data_access=data_access, notification_manager=notification_manager
)

# Serve React frontend in production
if not dev_mode:
    app.mount(
        "/assets", StaticFiles(directory="/app/frontend/dist/assets"), name="assets"
    )

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = f"/app/frontend/dist/{full_path}"
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse("/app/frontend/dist/index.html")
