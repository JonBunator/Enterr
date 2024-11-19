from flask import Flask, jsonify, send_from_directory
from dotenv import load_dotenv
import os

app = Flask(__name__, static_folder='../frontend/dist')

# Serve React frontend in production
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if os.getenv('FLASK_ENV') != 'production':
        return jsonify({"message": "Frontend not served in debug mode. Start the frontend separately."})

    if path != '' and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/users', methods=['GET'])
def users():
    return jsonify({"users": ["Alice", "Bob", "Charlie"]})

if __name__ == '__main__':
    load_dotenv()
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, port = 8080)