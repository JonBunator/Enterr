import pytest


def test_unauthenticated_request_is_rejected(client):
    assert client.get("/api/websites").status_code == 401


@pytest.fixture
def created_website(auth_client, webhooks, website_payload):
    """Website added through the API"""
    response = auth_client.post("/api/websites", json=website_payload)
    assert response.status_code == 200
    webhooks.reset_mock()
    return response.json()


def test_add_website(auth_client, webhooks, website_payload):
    response = auth_client.post("/api/websites", json=website_payload)

    assert response.status_code == 200
    website = response.json()
    assert website["name"] == "Example"
    assert website["paused"] is False
    assert website["next_schedule"] is not None
    assert website["action_interval"]["date_minutes_start"] == 1440
    webhooks.login_data_changed.assert_called_once()


def test_get_websites(auth_client, created_website):
    response = auth_client.get("/api/websites")

    assert response.status_code == 200
    assert [w["id"] for w in response.json()["items"]] == [created_website["id"]]


def test_get_website(auth_client, created_website):
    response = auth_client.get(f"/api/websites/{created_website['id']}")

    assert response.status_code == 200
    assert response.json() == created_website


def test_edit_website(auth_client, webhooks, created_website):
    website_id = created_website["id"]

    response = auth_client.put(
        f"/api/websites/{website_id}", json={"name": "Renamed", "paused": True}
    )

    assert response.status_code == 200
    website = auth_client.get(f"/api/websites/{website_id}").json()
    assert website["name"] == "Renamed"
    assert website["paused"] is True
    assert website["next_schedule"] is None
    webhooks.login_data_changed.assert_called_once()


def test_delete_website(auth_client, webhooks, created_website):
    website_id = created_website["id"]

    response = auth_client.delete(f"/api/websites/{website_id}")

    assert response.status_code == 200
    assert auth_client.get("/api/websites").json()["items"] == []
    assert auth_client.get(f"/api/websites/{website_id}").status_code == 404
    webhooks.login_data_changed.assert_called_once()


def test_website_search(auth_client, website_payload):
    auth_client.post("/api/websites", json=website_payload)
    auth_client.post(
        "/api/websites",
        json=website_payload | {"name": "Other", "url": "https://other.org/login"},
    )

    response = auth_client.get("/api/websites", params={"search": "other"})

    assert [w["name"] for w in response.json()["items"]] == ["Other"]


def test_websites_of_other_users_are_hidden(auth_client, make_website, other_user):
    foreign_website = make_website(owner=other_user)

    assert auth_client.get("/api/websites").json()["items"] == []

    response = auth_client.get(f"/api/websites/{foreign_website.id}")
    assert response.status_code == 404
    assert response.json() == {"detail": f"Website {foreign_website.id} not found"}

    assert auth_client.delete(f"/api/websites/{foreign_website.id}").status_code == 404
    assert auth_client.put(
        f"/api/websites/{foreign_website.id}", json={"name": "Hijacked"}
    ).status_code == 404


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
