from flask_socketio import SocketIO, emit

def register_webhook_endpoints(socketio: SocketIO):
    # Handle a custom event from the client
    @socketio.on('custom_event')
    def handle_custom_event(data):
        print(f"Received data: {data}")
        emit('message', {'data': 'Hello from Flask!'})