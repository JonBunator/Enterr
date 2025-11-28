from enum import Enum
from http.cookies import SimpleCookie
from urllib.parse import unquote
import socketio

from endpoints.webhooks.socketio import sio
from utils.security import decode_token


class Topic(Enum):
    LOGIN_DATA_CHANGED = "login_data_changed"
    ACTION_HISTORY_CHANGED = "action_history_changed"
    NOTIFICATIONS_CHANGED = "notifications_changed"


class WebhookEndpoints(socketio.AsyncNamespace):

    def on_connect(self, sid, environ):
        headers = environ["asgi.scope"]["headers"]
        cookie_header = None
        for name, value in headers:
            if name == b'cookie':
                cookie_header = value.decode('utf-8')
                break
        if not cookie_header:
            return False

        decoded = unquote(cookie_header)
        cookies = SimpleCookie()
        cookies.load(decoded)

        if 'access_token' not in cookies:
            return False
        raw_token = cookies['access_token'].value
        access_token = raw_token[len("Bearer "):]
        username = decode_token(access_token)
        if username is None:
            return False

        return True

    def connect_error(*args):
        print("The connection failed!", args)


    @staticmethod
    async def _send_message(topic: str, message: any):
        await sio.emit(topic, message)

    @staticmethod
    def _send_webhook_message(topic: str, message: any):
        print("asdasdas")
        #asyncio.create_task(WebhookEndpoints._send_message(topic, message))

    @staticmethod
    async def _send_webhook_message_async(topic: str, message: any):
        await WebhookEndpoints._send_message(topic, message)

    def login_data_changed(self):
        WebhookEndpoints._send_webhook_message(Topic.LOGIN_DATA_CHANGED.value, {})

    def action_history_changed(self, action_history_id: int):
        WebhookEndpoints._send_webhook_message(Topic.ACTION_HISTORY_CHANGED.value, {"id": action_history_id})

    @staticmethod
    async def action_history_changed_async(action_history_id: int):
        print("cahgendads, ", action_history_id)
        await WebhookEndpoints._send_webhook_message_async(Topic.ACTION_HISTORY_CHANGED.value, {"id": action_history_id})

    def notifications_changed(self):
        WebhookEndpoints._send_webhook_message(Topic.NOTIFICATIONS_CHANGED.value, {})
