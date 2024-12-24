from enum import Enum
from flask_socketio import SocketIO

class Topic(Enum):
    LOGIN_DATA_CHANGED = "login_data_changed"
    ACTION_HISTORY_CHANGED = "action_history_changed"

class WebhookEndpoints:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio

    def _send_webhook_message(self, topic: str, message: any):
        self.socketio.emit(topic, message)

    def login_data_changed(self):
        self._send_webhook_message(Topic.LOGIN_DATA_CHANGED.value, {})

    def action_history_changed(self, action_history_id: int):
        self._send_webhook_message(Topic.ACTION_HISTORY_CHANGED.value, {"id": action_history_id})


