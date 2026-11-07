import asyncio
from concurrent.futures import Future
from enum import Enum
from fastapi import WebSocket, WebSocketDisconnect, status
from starlette.concurrency import run_in_threadpool

from dataAccess.database.change_database import DataBase
from utils.security import decode_token


class Topic(Enum):
    LOGIN_DATA_CHANGED = "login_data_changed"
    ACTION_HISTORY_CHANGED = "action_history_changed"
    NOTIFICATIONS_CHANGED = "notifications_changed"


class WebhookEndpoints:

    def __init__(self):
        self._event_loop: asyncio.AbstractEventLoop | None = None
        # Maps every open connection to the id of its user
        self._connections: dict[WebSocket, int] = {}

    def set_event_loop(self, event_loop: asyncio.AbstractEventLoop):
        # Must be the loop uvicorn is serving on, so set it at runtime (not at import)
        self._event_loop = event_loop

    @staticmethod
    def _get_user_id(websocket: WebSocket) -> int | None:
        raw_token = websocket.cookies.get("access_token")
        if not raw_token or not raw_token.startswith("Bearer "):
            return None
        access_token = raw_token[len("Bearer ") :]
        username = decode_token(access_token)
        if username is None:
            return None
        user = DataBase.get_user(username)
        return user.id if user is not None else None

    async def handle_connection(self, websocket: WebSocket):
        user_id = await run_in_threadpool(WebhookEndpoints._get_user_id, websocket)
        if user_id is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await websocket.accept()
        self._connections[websocket] = user_id
        try:
            while True:
                # Incoming messages are ignored, only used to detect disconnects
                await websocket.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            self._connections.pop(websocket, None)

    async def _send_message(self, topic: str, message: any, user_id: int):
        payload = {"event": topic, "data": message}
        for connection, connection_user_id in list(self._connections.items()):
            # Users must only be notified about their own data
            if connection_user_id != user_id:
                continue
            try:
                await connection.send_json(payload)
            except Exception:
                self._connections.pop(connection, None)

    @staticmethod
    def _log_send_error(future: Future):
        if future.cancelled():
            return
        exception = future.exception()
        if exception is not None:
            print(f"Failed to send websocket message: {exception!r}")

    def _send_webhook_message(self, topic: str, message: any, user_id: int):
        if self._event_loop is None or self._event_loop.is_closed():
            return
        future = asyncio.run_coroutine_threadsafe(
            self._send_message(topic, message, user_id), self._event_loop
        )
        future.add_done_callback(WebhookEndpoints._log_send_error)

    async def _send_webhook_message_async(
        self, topic: str, message: any, user_id: int
    ):
        await self._send_message(topic, message, user_id)

    def login_data_changed(self, user_id: int):
        self._send_webhook_message(Topic.LOGIN_DATA_CHANGED.value, {}, user_id)

    def action_history_changed(
        self, action_history_id: int, website_id: int, user_id: int
    ):
        self._send_webhook_message(
            Topic.ACTION_HISTORY_CHANGED.value,
            {"action_history_id": action_history_id, "website_id": website_id},
            user_id,
        )

    def notifications_changed(self, user_id: int):
        self._send_webhook_message(Topic.NOTIFICATIONS_CHANGED.value, {}, user_id)
