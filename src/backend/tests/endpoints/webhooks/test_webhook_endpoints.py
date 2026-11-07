import asyncio

import pytest
from fastapi import FastAPI, WebSocket
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from endpoints.webhooks.webhook_endpoints import WebhookEndpoints
from utils.security import create_access_token


@pytest.fixture
def webhook_endpoints():
    return WebhookEndpoints()


@pytest.fixture
def ws_client(session_factory, webhook_endpoints):
    app = FastAPI()

    @app.websocket("/api/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await webhook_endpoints.handle_connection(websocket)

    return TestClient(app)


def _connect(ws_client, username: str):
    ws_client.cookies.set("access_token", f"Bearer {create_access_token(username)}")
    return ws_client.websocket_connect("/api/ws")


def test_connection_of_known_user_is_accepted(ws_client, webhook_endpoints, user):
    with _connect(ws_client, user.username):
        assert list(webhook_endpoints._connections.values()) == [user.id]


def test_connection_of_unknown_user_is_rejected(ws_client):
    with pytest.raises(WebSocketDisconnect) as error:
        with _connect(ws_client, "doesnotexist") as websocket:
            websocket.receive_text()

    assert error.value.code == 1008


def test_connection_without_token_is_rejected(ws_client):
    with pytest.raises(WebSocketDisconnect) as error:
        with ws_client.websocket_connect("/api/ws") as websocket:
            websocket.receive_text()

    assert error.value.code == 1008


def test_messages_are_only_sent_to_the_owner(webhook_endpoints, mocker):
    owner_socket = mocker.AsyncMock()
    other_socket = mocker.AsyncMock()
    webhook_endpoints._connections = {owner_socket: 1, other_socket: 2}

    asyncio.run(
        webhook_endpoints._send_message("action_history_changed", {"id": 5}, user_id=1)
    )

    owner_socket.send_json.assert_awaited_once_with(
        {"event": "action_history_changed", "data": {"id": 5}}
    )
    other_socket.send_json.assert_not_awaited()


def test_failing_connection_is_removed(webhook_endpoints, mocker):
    broken_socket = mocker.AsyncMock()
    broken_socket.send_json.side_effect = RuntimeError("closed")
    webhook_endpoints._connections = {broken_socket: 1}

    asyncio.run(webhook_endpoints._send_message("login_data_changed", {}, user_id=1))

    assert webhook_endpoints._connections == {}
