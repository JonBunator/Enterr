from database.database import init_db
from flask import Flask, jsonify, send_from_directory
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os

from endpoints.rest_endpoints import register_rest_endpoints
from endpoints.webhook_endpoints import register_webhook_endpoints
from execution.scheduler import Scheduler

load_dotenv()
dev_mode = os.getenv('FLASK_ENV') != 'production'
app = Flask(__name__, static_folder='../frontend/dist')

if dev_mode:
    socketio = SocketIO(app, cors_allowed_origins=f"http://localhost:5173")
else:
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

register_rest_endpoints(app)
register_webhook_endpoints(socketio)


if __name__ == '__main__':
    with app.app_context():
        init_db(app)
        Scheduler(app=app).start()
        socketio.run(app, debug=dev_mode, port=8080, use_reloader=False)
    #print(response)
