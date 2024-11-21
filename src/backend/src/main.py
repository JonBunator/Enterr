from endpoints.login import XPaths, login
from flask import Flask, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import os

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

@app.route('/api/users', methods=['GET'])
def users():
    return jsonify({"users": ["Alice", "Bob", "Charlie"]})

# Handle a custom event from the client
@socketio.on('custom_event')
def handle_custom_event(data):
    print(f"Received data: {data}")
    emit('message', {'data': 'Hello from Flask!'})

if __name__ == '__main__':
    #socketio.run(app, debug=dev_mode, port=8080)
    response = login("https://www.uicore.co/framework/elements/user-login/", "test@mail.com", "password", x_paths=None)
    print(response)
