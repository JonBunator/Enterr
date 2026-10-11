import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_pagination import add_pagination

from dataAccess.data_access import DataAccess
from endpoints.api.rest_endpoints import register_rest_endpoints
from execution.notifications.notification_manager import NotificationManager
from utils.exceptions import NotFoundException

WEBSITE = {
    "url": "https://example.com/login",
    "success_url": "https://example.com/home",
    "name": "Example",
    "username": "alice",
    "password": "secret",
    "take_screenshot": False,
    "action_interval": {"date_minutes_start": 1440},
}


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


# ---------------------------- USER ----------------------------


def test_login_with_wrong_password(client, user):
    response = client.post(
        "/api/user/login", data={"username": "testuser", "password": "wrong"}
    )
    assert response.status_code == 401
    assert "access_token" not in response.cookies


def test_login_sets_cookie(client, user):
    response = client.post(
        "/api/user/login", data={"username": "testuser", "password": "testpass123"}
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert "access_token" in response.cookies


def test_user_data(auth_client):
    response = auth_client.get("/api/user/data")
    assert response.json() == {"username": "testuser"}


def test_unauthenticated_request_is_rejected(client):
    assert client.get("/api/websites").status_code == 401


def test_health(client):
    assert client.get("/api/health").json() == {"status": "healthy"}


# ---------------------------- WEBSITES ----------------------------


def test_website_crud(auth_client, webhooks):
    # Add
    response = auth_client.post("/api/websites", json=WEBSITE)
    assert response.status_code == 200
    website = response.json()
    website_id = website["id"]
    assert website["name"] == "Example"
    assert website["paused"] is False
    assert website["next_schedule"] is not None
    assert website["action_interval"]["date_minutes_start"] == 1440

    # List
    response = auth_client.get("/api/websites")
    assert response.status_code == 200
    assert [w["id"] for w in response.json()["items"]] == [website_id]

    # Edit
    response = auth_client.put(
        f"/api/websites/{website_id}", json={"name": "Renamed", "paused": True}
    )
    assert response.status_code == 200

    website = auth_client.get(f"/api/websites/{website_id}").json()
    assert website["name"] == "Renamed"
    assert website["paused"] is True
    assert website["next_schedule"] is None

    # Delete
    assert auth_client.delete(f"/api/websites/{website_id}").status_code == 200
    assert auth_client.get("/api/websites").json()["items"] == []

    assert webhooks.login_data_changed.call_count == 3


def test_website_search(auth_client):
    auth_client.post("/api/websites", json=WEBSITE)
    auth_client.post(
        "/api/websites",
        json=WEBSITE | {"name": "Other", "url": "https://other.org/login"},
    )

    response = auth_client.get("/api/websites", params={"search": "other"})

    assert [w["name"] for w in response.json()["items"]] == ["Other"]


def test_websites_of_other_users_are_hidden(auth_client, make_website, other_user):
    foreign_website = make_website(owner=other_user)

    assert auth_client.get("/api/websites").json()["items"] == []
    # NotFoundException is not mapped to an HTTP status code yet
    with pytest.raises(NotFoundException):
        auth_client.get(f"/api/websites/{foreign_website.id}")


def test_add_invalid_website_is_rejected(auth_client):
    response = auth_client.post("/api/websites", json={"name": "Missing fields"})
    assert response.status_code == 422


@pytest.mark.parametrize(
    "script, valid",
    [
        ("fillUsername()\nfillPassword()\nclickSubmitButton()", True),
        ("fillUsername(", False),
    ],
)
def test_check_custom_login_script(client, script, valid):
    response = client.post(
        "/api/websites/check_custom_login_script", json={"script": script}
    )

    assert response.status_code == 200
    assert (response.json()["error"] is None) is valid


# ---------------------------- ACTION HISTORY ----------------------------


def test_manual_action_history(auth_client, webhooks, make_website):
    website = make_website()

    response = auth_client.post(f"/api/action_history/manual_add/{website.id}")
    assert response.status_code == 200
    assert response.json()["execution_status"] == "SUCCESS"

    histories = auth_client.get(
        "/api/action_history", params={"website_id": website.id}
    ).json()["items"]
    assert len(histories) == 1

    last_login = auth_client.get(
        f"/api/action_history/last_successful_login/{website.id}"
    ).json()
    assert last_login["action_history"]["id"] == histories[0]["id"]

    webhooks.action_history_changed.assert_called_once()
