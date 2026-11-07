from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination

from dataAccess.data_access import DataAccess
from dataAccess.database.database import ActionHistory, Notification, User
from endpoints.api.rest_endpoints import register_rest_endpoints
from execution.login_live_view import LoginLiveView
from execution.notifications.notification_manager import NotificationManager
from utils.security import create_access_token


@pytest.fixture
def notification_manager(mocker):
    return mocker.Mock(spec=NotificationManager)


@pytest.fixture
def login_live_view():
    login_live_view = LoginLiveView()
    yield login_live_view
    active = login_live_view._active
    if active is not None:
        login_live_view.stop(active.action_history_id)


@pytest.fixture
def app(session_factory, webhooks, notification_manager, login_live_view):
    """App with all REST endpoints, without the side effects of main.py"""
    app = FastAPI()
    register_rest_endpoints(
        app=app,
        data_access=DataAccess(webhook_endpoints=webhooks),
        notification_manager=notification_manager,
        login_live_view=login_live_view,
    )
    add_pagination(app)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def auth_client(client, user):
    """Client authenticated as `user` without calling the login endpoint"""
    client.cookies.set("access_token", f"Bearer {create_access_token(user.username)}")
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


@pytest.fixture
def make_action_history(session):
    def _make_action_history(website, status, started=datetime(2024, 5, 10, 8, 0)):
        action_history = ActionHistory(
            execution_started=started, execution_status=status, website=website.id
        )
        session.add(action_history)
        session.commit()
        session.refresh(action_history)
        return action_history

    return _make_action_history


@pytest.fixture
def make_notification(session, user):
    def _make_notification(owner: User = None, **overrides):
        values = dict(
            name="My notification",
            apprise_token="json://localhost",
            title="{WEBSITE_NAME}",
            body="{STATUS}",
            user=(owner or user).id,
        )
        values.update(overrides)
        triggers = values.pop("triggers", [])
        notification = Notification(**values)
        notification.triggers = triggers
        session.add(notification)
        session.commit()
        session.refresh(notification)
        return notification

    return _make_notification
