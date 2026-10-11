import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination

from dataAccess.data_access import DataAccess
from endpoints.api.rest_endpoints import register_rest_endpoints
from execution.notifications.notification_manager import NotificationManager


@pytest.fixture
def app(session_factory, webhooks, mocker):
    """App with all REST endpoints, without the side effects of main.py"""
    app = FastAPI()
    register_rest_endpoints(
        app=app,
        data_access=DataAccess(webhook_endpoints=webhooks),
        notification_manager=mocker.Mock(spec=NotificationManager),
    )
    add_pagination(app)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def auth_client(client, user):
    response = client.post(
        "/api/user/login", data={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    return client


@pytest.fixture
def website_payload():
    return {
        "url": "https://example.com/login",
        "success_url": "https://example.com/home",
        "name": "Example",
        "username": "alice",
        "password": "secret",
        "take_screenshot": False,
        "action_interval": {"date_minutes_start": 1440},
    }
