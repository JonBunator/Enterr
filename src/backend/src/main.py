from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from jose import JWTError
from datetime import datetime, timedelta

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
dev_mode = True
app = FastAPI()
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

# Serve React frontend in production
"""
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if dev_mode:
        return jsonify(
            {
                "message": "Frontend not served in debug mode. Start the frontend separately."
            }
        )

    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


class SPAStaticFiles(StaticFiles):
    def get_response(self, path: str, scope):
        try:
            return super().get_response(path, scope)
        except HTTPException as ex:
            if ex.status_code == 404:
                return super().get_response("index.html", scope)
            else:
                raise ex


app.mount("/", SPAStaticFiles(directory="dist", html=True), name="spa-static-files")
"""
init_db()
if dev_mode:
    create_user(username="debug", password="123", create_db=False)
webhook_endpoints = WebhookEndpoints()
data_access = DataAccess(webhook_endpoints=webhook_endpoints)
data_access_internal = DataAccessInternal(webhook_endpoints=webhook_endpoints)
notification_manager = NotificationManager(data_access=data_access_internal)
scheduler = Scheduler(data_access_internal=data_access_internal)
register_database_events(scheduler=scheduler, notification_manager=notification_manager)
register_rest_endpoints(
    app=app, data_access=data_access, notification_manager=notification_manager
)
scheduler.start()
