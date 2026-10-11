import asyncio
from concurrent.futures import Future
from enum import Enum
from fastapi import WebSocket, WebSocketDisconnect, status

from utils.security import decode_token


class Topic(Enum):
    LOGIN_DATA_CHANGED = "login_data_changed"
    ACTION_HISTORY_CHANGED = "action_history_changed"
    NOTIFICATIONS_CHANGED = "notifications_changed"


class WebhookEndpoints:

    def __init__(self):
        self._event_loop: asyncio.AbstractEventLoop | None = None
        self._connections: set[WebSocket] = set()

    def set_event_loop(self, event_loop: asyncio.AbstractEventLoop):
        # Must be the loop uvicorn is serving on, so set it at runtime (not at import)
        self._event_loop = event_loop

    @staticmethod
    def _is_authenticated(websocket: WebSocket) -> bool:
        raw_token = websocket.cookies.get("access_token")
        if not raw_token or not raw_token.startswith("Bearer "):
            return False
        access_token = raw_token[len("Bearer ") :]
        return decode_token(access_token) is not None

    async def handle_connection(self, websocket: WebSocket):
        if not WebhookEndpoints._is_authenticated(websocket):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await websocket.accept()
        self._connections.add(websocket)
        try:
            while True:
                # Incoming messages are ignored, only used to detect disconnects
                await websocket.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            self._connections.discard(websocket)

    async def _send_message(self, topic: str, message: any):
        payload = {"event": topic, "data": message}
        for connection in list(self._connections):
            try:
                await connection.send_json(payload)
            except Exception:
                self._connections.discard(connection)

    @staticmethod
    def _log_send_error(future: Future):
        if future.cancelled():
            return
        exception = future.exception()
        if exception is not None:
            print(f"Failed to send websocket message: {exception!r}")

    def _send_webhook_message(self, topic: str, message: any):
        if self._event_loop is None or self._event_loop.is_closed():
            return
        future = asyncio.run_coroutine_threadsafe(
            self._send_message(topic, message), self._event_loop
        )
        future.add_done_callback(WebhookEndpoints._log_send_error)

    async def _send_webhook_message_async(self, topic: str, message: any):
        await self._send_message(topic, message)

    def login_data_changed(self):
        self._send_webhook_message(Topic.LOGIN_DATA_CHANGED.value, {})

    def action_history_changed(self, action_history_id: int, website_id: int):
        self._send_webhook_message(
            Topic.ACTION_HISTORY_CHANGED.value,
            {"action_history_id": action_history_id, "website_id": website_id},
        )

    def notifications_changed(self):
        self._send_webhook_message(Topic.NOTIFICATIONS_CHANGED.value, {})
