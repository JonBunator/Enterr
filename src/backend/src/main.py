import asyncio
import os
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from contextlib import asynccontextmanager
from execution.notifications.notification_manager import NotificationManager
from dataAccess.data_access_internal import DataAccessInternal
from user_management import create_user
from dataAccess.data_access import DataAccess
from dataAccess.database.database import init_db
from dotenv import load_dotenv
from dataAccess.database.database_events import register_database_events
from endpoints.api.rest_endpoints import register_rest_endpoints
from endpoints.webhooks.webhook_endpoints import WebhookEndpoints
from execution.login_live_view import LoginLiveView
from execution.scheduler import Scheduler

load_dotenv()
dev_mode = os.getenv("RUN_MODE") != "production"

init_db()

if dev_mode:
    create_user(username="debug", password="123", create_db=False)

webhook_endpoints = WebhookEndpoints()
data_access = DataAccess(webhook_endpoints=webhook_endpoints)
data_access_internal = DataAccessInternal(webhook_endpoints=webhook_endpoints)
notification_manager = NotificationManager(data_access=data_access_internal)
login_live_view = LoginLiveView()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Uvicorn may import this module before its event loop runs,
    # so the loop has to be captured here instead of at import time
    webhook_endpoints.set_event_loop(asyncio.get_running_loop())
    scheduler = Scheduler(
        data_access_internal=data_access_internal,
        webhook_endpoints=webhook_endpoints,
        login_live_view=login_live_view,
    )
    register_database_events(
        scheduler=scheduler, notification_manager=notification_manager
    )
    try:
        scheduler.start()
        yield
    finally:
        scheduler.stop()

if dev_mode:
    app = FastAPI(lifespan=lifespan)
else:
    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

if dev_mode:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await webhook_endpoints.handle_connection(websocket)


register_rest_endpoints(
    app=app,
    data_access=data_access,
    notification_manager=notification_manager,
    login_live_view=login_live_view,
)

add_pagination(app)

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
