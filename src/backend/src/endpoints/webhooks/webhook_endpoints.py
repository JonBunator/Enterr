import asyncio
from enum import Enum
import socketio
from endpoints.webhooks.socketio import sio

class Topic(Enum):
    LOGIN_DATA_CHANGED = "login_data_changed"
    ACTION_HISTORY_CHANGED = "action_history_changed"
    NOTIFICATIONS_CHANGED = "notifications_changed"


class WebhookEndpoints(socketio.AsyncNamespace):

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
