from datetime import datetime, timedelta

import pytest

from dataAccess.database.database import ActionStatusCode, Website


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


def test_get_websites_sort_by_name(auth_client, make_website):
    make_website(name="Bravo")
    make_website(name="Alpha")

    response = auth_client.get("/api/websites", params={"sort": "+name"})

    assert [w["name"] for w in response.json()["items"]] == ["Alpha", "Bravo"]


@pytest.mark.parametrize(
    "sort, expected",
    [
        ("+expiration", ["Unknown", "Soon", "Late"]),
        ("-expiration", ["Late", "Soon", "Unknown"]),
    ],
)
def test_get_websites_sort_by_expiration(
    auth_client, make_website, make_action_history, sort, expected
):
    # Late: older login but much longer interval -> expires after Soon
    late = make_website(name="Late", expiration_interval=timedelta(days=30))
    soon = make_website(name="Soon", expiration_interval=timedelta(days=1))
    make_website(name="Unknown")
    make_action_history(
        late, ActionStatusCode.SUCCESS, datetime(2024, 5, 1), datetime(2024, 5, 1, 0, 1)
    )
    make_action_history(
        soon, ActionStatusCode.SUCCESS, datetime(2024, 5, 10), datetime(2024, 5, 10, 0, 1)
    )
    # A newer failed login must not count as the last successful one
    make_action_history(
        soon, ActionStatusCode.FAILED, datetime(2024, 6, 10), datetime(2024, 6, 10, 0, 1)
    )

    response = auth_client.get("/api/websites", params={"sort": sort})

    items = response.json()["items"]
    assert [w["name"] for w in items] == expected
    expiration_dates = {w["name"]: w["expiration_date"] for w in items}
    assert expiration_dates == {
        "Late": "2024-05-31T00:01:00Z",
        "Soon": "2024-05-11T00:01:00Z",
        "Unknown": None,
    }


def test_get_websites_expiration_without_successful_login(
    auth_client, make_website, make_action_history
):
    website = make_website(expiration_interval=timedelta(days=1))
    make_action_history(
        website, ActionStatusCode.FAILED, datetime(2024, 5, 1), datetime(2024, 5, 1, 0, 1)
    )

    response = auth_client.get("/api/websites")

    assert response.json()["items"][0]["expiration_date"] is None


def test_get_websites_expiration_uses_latest_started_success(
    auth_client, make_website, make_action_history
):
    # The newest success has no end time, so an older success must not be used instead
    website = make_website(expiration_interval=timedelta(days=1))
    make_action_history(
        website, ActionStatusCode.SUCCESS, datetime(2024, 5, 1), datetime(2024, 5, 1, 0, 1)
    )
    make_action_history(website, ActionStatusCode.SUCCESS, datetime(2024, 5, 10))

    response = auth_client.get("/api/websites")

    assert response.json()["items"][0]["expiration_date"] is None


@pytest.fixture
def websites_with_statuses(make_website, make_action_history):
    """One website per effective status, named after it"""
    success = make_website(name="Success")
    make_action_history(success, ActionStatusCode.FAILED, datetime(2024, 5, 1))
    make_action_history(success, ActionStatusCode.SUCCESS, datetime(2024, 5, 2))

    failed = make_website(name="Failed")
    make_action_history(failed, ActionStatusCode.SUCCESS, datetime(2024, 5, 1))
    make_action_history(failed, ActionStatusCode.FAILED, datetime(2024, 5, 2))

    # A website without any login counts as failed
    make_website(name="Never")

    running = make_website(name="Running")
    make_action_history(running, ActionStatusCode.IN_PROGRESS, datetime(2024, 5, 2))

    # Paused takes precedence over the last login result
    paused = make_website(name="Paused", paused=True)
    make_action_history(paused, ActionStatusCode.SUCCESS, datetime(2024, 5, 2))


@pytest.mark.parametrize(
    "status, expected",
    [
        ("SUCCESS", ["Success"]),
        ("FAILED", ["Failed", "Never"]),
        ("IN_PROGRESS", ["Running"]),
        ("PAUSED", ["Paused"]),
    ],
)
def test_get_websites_filter_by_status(
    auth_client, websites_with_statuses, status, expected
):
    response = auth_client.get("/api/websites", params={"status": status})

    assert response.status_code == 200
    assert response.json()["total"] == len(expected)
    assert [w["name"] for w in response.json()["items"]] == expected


def test_get_websites_invalid_status_is_rejected(auth_client):
    response = auth_client.get("/api/websites", params={"status": "UNKNOWN"})

    assert response.status_code == 422


# ---------------------------- GET /api/websites/status-counts ----------------------------


def test_get_website_status_counts(auth_client, websites_with_statuses):
    response = auth_client.get("/api/websites/status-counts")

    assert response.status_code == 200
    assert response.json() == {
        "SUCCESS": 1,
        "FAILED": 2,
        "PAUSED": 1,
        "IN_PROGRESS": 1,
    }


def test_get_website_status_counts_search(auth_client, websites_with_statuses):
    response = auth_client.get("/api/websites/status-counts", params={"search": "fail"})

    assert response.json() == {
        "SUCCESS": 0,
        "FAILED": 1,
        "PAUSED": 0,
        "IN_PROGRESS": 0,
    }


def test_get_website_status_counts_hides_other_users_websites(
    auth_client, make_website, other_user
):
    make_website(owner=other_user)

    response = auth_client.get("/api/websites/status-counts")

    assert response.json() == {
        "SUCCESS": 0,
        "FAILED": 0,
        "PAUSED": 0,
        "IN_PROGRESS": 0,
    }


def test_get_website_status_counts_unauthenticated(client):
    assert client.get("/api/websites/status-counts").status_code == 401


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
