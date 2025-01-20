import eventlet
eventlet.monkey_patch(thread=True, time=True)
from dataAccess.data_access import DataAccess
from dataAccess.database.database import init_db
from flask import Flask, jsonify, send_from_directory
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os
from dataAccess.database.database_events import register_database_events
from endpoints.rest_endpoints import register_rest_endpoints
from endpoints.webhook_endpoints import WebhookEndpoints
from execution.scheduler import Scheduler

load_dotenv()
dev_mode = os.getenv('FLASK_ENV') != 'production'

if dev_mode:
    app = Flask(__name__)
    socketio = SocketIO(app, cors_allowed_origins=f"http://localhost:5173", async_mode='eventlet')
else:
    app = Flask(__name__, static_folder='../../frontend/dist')
    socketio = SocketIO(app)

# Serve React frontend in production
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if dev_mode:
        return jsonify({"message": "Frontend not served in debug mode. Start the frontend separately."})

    if path != '' and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

with app.app_context():
    init_db(app)
    webhook_endpoints = WebhookEndpoints(socketio=socketio)
    data_access = DataAccess(webhook_endpoints=webhook_endpoints)
    register_rest_endpoints(app=app, data_access=data_access)
    scheduler = Scheduler(app=app, data_access=data_access)
    register_database_events(scheduler=scheduler)
    scheduler.start()
    if dev_mode: 
        socketio.run(app, debug=True, port=7653, use_reloader=False)
