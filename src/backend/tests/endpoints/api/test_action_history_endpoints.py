from datetime import datetime

from dataAccess.database.database import ActionHistory, ActionStatusCode


# ---------------------------- GET /api/action_history ----------------------------


def test_get_action_histories(auth_client, make_website, make_action_history):
    website = make_website()
    older = make_action_history(website, ActionStatusCode.SUCCESS, datetime(2024, 1, 1))
    newer = make_action_history(website, ActionStatusCode.FAILED, datetime(2024, 2, 1))

    response = auth_client.get("/api/action_history", params={"website_id": website.id})

    assert response.status_code == 200
    items = response.json()["items"]
    assert [h["id"] for h in items] == [newer.id, older.id]
    assert [h["execution_status"] for h in items] == ["FAILED", "SUCCESS"]


def test_get_action_histories_of_other_users_website_returns_404(
    auth_client, make_website, other_user
):
    website = make_website(owner=other_user)

    response = auth_client.get("/api/action_history", params={"website_id": website.id})

    assert response.status_code == 404


# ---------------------------- GET /api/action_history/{id} ----------------------------


def test_get_action_history(auth_client, make_website, make_action_history):
    website = make_website()
    action_history = make_action_history(website, ActionStatusCode.SUCCESS)

    response = auth_client.get(f"/api/action_history/{action_history.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == action_history.id
    assert body["execution_status"] == "SUCCESS"
    assert body["failed_details"] is None


def test_get_action_history_of_other_user_returns_404(
    auth_client, make_website, make_action_history, other_user
):
    website = make_website(owner=other_user)
    action_history = make_action_history(website, ActionStatusCode.SUCCESS)

    response = auth_client.get(f"/api/action_history/{action_history.id}")

    assert response.status_code == 404


# ------------------- GET /api/action_history/last_successful_login/{id} -------------------


def test_get_last_successful_login(auth_client, make_website, make_action_history):
    website = make_website()
    make_action_history(website, ActionStatusCode.SUCCESS, datetime(2024, 1, 1))
    latest = make_action_history(website, ActionStatusCode.SUCCESS, datetime(2024, 2, 1))
    make_action_history(website, ActionStatusCode.FAILED, datetime(2024, 3, 1))

    response = auth_client.get(f"/api/action_history/last_successful_login/{website.id}")

    assert response.status_code == 200
    assert response.json()["action_history"]["id"] == latest.id


def test_get_last_successful_login_without_success(
    auth_client, make_website, make_action_history
):
    website = make_website()
    make_action_history(website, ActionStatusCode.FAILED)

    response = auth_client.get(f"/api/action_history/last_successful_login/{website.id}")

    assert response.status_code == 200
    assert response.json() == {"action_history": None}


def test_get_last_successful_login_of_other_user_returns_404(
    auth_client, make_website, other_user
):
    website = make_website(owner=other_user)

    response = auth_client.get(f"/api/action_history/last_successful_login/{website.id}")

    assert response.status_code == 404


# ------------------- POST /api/action_history/manual_add/{id} -------------------


def test_add_manual_action_history(auth_client, session, make_website, webhooks):
    website = make_website()

    response = auth_client.post(f"/api/action_history/manual_add/{website.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["execution_status"] == "SUCCESS"
    assert body["execution_ended"] is not None

    stored = session.get(ActionHistory, body["id"])
    assert stored.website == website.id
    assert stored.execution_status == ActionStatusCode.SUCCESS
    webhooks.action_history_changed.assert_called_once_with(
        action_history_id=body["id"], website_id=website.id
    )


def test_add_manual_action_history_of_other_user_returns_404(
    auth_client, session, make_website, other_user, webhooks
):
    website = make_website(owner=other_user)

    response = auth_client.post(f"/api/action_history/manual_add/{website.id}")

    assert response.status_code == 404
    assert session.query(ActionHistory).count() == 0
    webhooks.action_history_changed.assert_not_called()
