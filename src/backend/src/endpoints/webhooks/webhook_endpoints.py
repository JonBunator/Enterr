import asyncio
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

    def __init__(self, event_loop: asyncio.AbstractEventLoop):
        super().__init__("/")
        self._event_loop = event_loop

    def on_connect(self, sid, environ):
        headers = environ["asgi.scope"]["headers"]
        cookie_header = None
        for name, value in headers:
            if name == b"cookie":
                cookie_header = value.decode("utf-8")
                break
        if not cookie_header:
            return False

        decoded = unquote(cookie_header)
        cookies = SimpleCookie()
        cookies.load(decoded)

        if "access_token" not in cookies:
            return False
        raw_token = cookies["access_token"].value
        access_token = raw_token[len("Bearer ") :]
        username = decode_token(access_token)
        if username is None:
            return False

        return True

    def connect_error(*args):
        print("The connection failed!", args)

    @staticmethod
    async def _send_message(topic: str, message: any):
        await sio.emit(topic, message)

    def _send_webhook_message(self, topic: str, message: any):
        asyncio.run_coroutine_threadsafe(
            WebhookEndpoints._send_message(topic, message), self._event_loop
        )

    @staticmethod
    async def _send_webhook_message_async(topic: str, message: any):
        await WebhookEndpoints._send_message(topic, message)

    def login_data_changed(self):
        self._send_webhook_message(Topic.LOGIN_DATA_CHANGED.value, {})

    def action_history_changed(self, action_history_id: int):
        self._send_webhook_message(
            Topic.ACTION_HISTORY_CHANGED.value, {"id": action_history_id}
        )

    def notifications_changed(self):
        self._send_webhook_message(Topic.NOTIFICATIONS_CHANGED.value, {})
