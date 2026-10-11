from datetime import datetime

import pytest

from dataAccess.database.database import Website


# ---------------------------- GET /api/websites ----------------------------


def test_get_websites(auth_client, make_website):
    website = make_website()

    response = auth_client.get("/api/websites")

    assert response.status_code == 200
    assert [w["id"] for w in response.json()["items"]] == [website.id]


def test_get_websites_unauthenticated(client):
    assert client.get("/api/websites").status_code == 401


def test_get_websites_hides_other_users_websites(auth_client, make_website, other_user):
    make_website(owner=other_user)

    response = auth_client.get("/api/websites")

    assert response.json()["items"] == []


def test_get_websites_search(auth_client, make_website):
    make_website(name="Example")
    make_website(name="Other", url="https://other.org/login")

    response = auth_client.get("/api/websites", params={"search": "other"})

    assert [w["name"] for w in response.json()["items"]] == ["Other"]


# ---------------------------- GET /api/websites/{id} ----------------------------


def test_get_website(auth_client, make_website):
    website = make_website()

    response = auth_client.get(f"/api/websites/{website.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == website.id
    assert body["name"] == "Example"
    assert body["url"] == "https://example.com/login"
    assert body["action_interval"]["date_minutes_start"] == 1440


def test_get_website_of_other_user_returns_404(auth_client, make_website, other_user):
    website = make_website(owner=other_user)

    response = auth_client.get(f"/api/websites/{website.id}")

    assert response.status_code == 404
    assert response.json() == {"detail": f"Website {website.id} not found"}


# ---------------------------- POST /api/websites ----------------------------


def test_add_website(auth_client, session, user, webhooks, website_payload):
    response = auth_client.post("/api/websites", json=website_payload)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Example"
    assert body["paused"] is False
    assert body["next_schedule"] is not None

    website = session.get(Website, body["id"])
    assert website.user == user.id
    assert website.action_interval.date_minutes_start == 1440
    webhooks.login_data_changed.assert_called_once()


def test_add_invalid_website_is_rejected(auth_client, session, webhooks):
    response = auth_client.post("/api/websites", json={"name": "Missing fields"})

    assert response.status_code == 422
    assert session.query(Website).count() == 0
    webhooks.login_data_changed.assert_not_called()


# ---------------------------- PUT /api/websites/{id} ----------------------------


def test_edit_website(auth_client, session, make_website, webhooks):
    website = make_website(next_schedule=datetime(2030, 1, 1))

    response = auth_client.put(
        f"/api/websites/{website.id}", json={"name": "Renamed", "paused": True}
    )

    assert response.status_code == 200
    session.expire_all()
    website = session.get(Website, website.id)
    assert website.name == "Renamed"
    assert website.paused is True
    assert website.next_schedule is None
    webhooks.login_data_changed.assert_called_once()


def test_edit_website_of_other_user_returns_404(
    auth_client, session, make_website, other_user, webhooks
):
    website = make_website(owner=other_user)

    response = auth_client.put(f"/api/websites/{website.id}", json={"name": "Hijacked"})

    assert response.status_code == 404
    session.expire_all()
    assert session.get(Website, website.id).name == "Example"
    webhooks.login_data_changed.assert_not_called()


# ---------------------------- DELETE /api/websites/{id} ----------------------------


def test_delete_website(auth_client, session, make_website, webhooks):
    website = make_website()

    response = auth_client.delete(f"/api/websites/{website.id}")

    assert response.status_code == 200
    session.expire_all()
    assert session.query(Website).count() == 0
    webhooks.login_data_changed.assert_called_once()


def test_delete_website_of_other_user_returns_404(
    auth_client, session, make_website, other_user, webhooks
):
    website = make_website(owner=other_user)

    response = auth_client.delete(f"/api/websites/{website.id}")

    assert response.status_code == 404
    assert session.query(Website).count() == 1
    webhooks.login_data_changed.assert_not_called()


# ---------------------- POST /api/websites/check_custom_login_script ----------------------


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
