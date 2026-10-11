import threading
from datetime import datetime

import pytest

from dataAccess.database.database import ActionHistory, ActionStatusCode
from execution.login_live_view import LoginLiveView, _Capture


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


def test_add_manual_action_history(
    auth_client, session, make_website, webhooks, user
):
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
        action_history_id=body["id"], website_id=website.id, user_id=user.id
    )


def test_add_manual_action_history_of_other_user_returns_404(
    auth_client, session, make_website, other_user, webhooks
):
    website = make_website(owner=other_user)

    response = auth_client.post(f"/api/action_history/manual_add/{website.id}")

    assert response.status_code == 404
    assert session.query(ActionHistory).count() == 0
    webhooks.action_history_changed.assert_not_called()


# ------------------- GET /api/action_history/{id}/live -------------------


@pytest.fixture
def capture(mocker):
    """Prevents ffmpeg from being started"""
    return mocker.patch.object(LoginLiveView, "_start_capture")


def test_login_live_view_streams_frames_of_own_running_login(
    auth_client, make_website, make_action_history, login_live_view, capture, mocker
):
    website = make_website()
    action_history = make_action_history(website, ActionStatusCode.IN_PROGRESS)
    login_live_view.start(action_history.id)

    def push_frame_and_stop(session):
        fake_capture = _Capture(mocker.Mock())
        session.push_frame(b"\xff\xd8frame\xff\xd9", fake_capture)
        # End the login shortly after, which closes the stream
        threading.Timer(0.3, login_live_view.stop, [action_history.id]).start()
        return fake_capture

    capture.side_effect = push_frame_and_stop

    response = auth_client.get(f"/api/action_history/{action_history.id}/live")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "multipart/x-mixed-replace; boundary=frame"
    )
    assert response.headers["cache-control"] == "no-store"
    assert b"--frame\r\nContent-Type: image/jpeg" in response.content
    assert b"\xff\xd8frame\xff\xd9" in response.content
    session = capture.call_args.args[0]
    assert session.viewers == 0


def test_login_live_view_of_other_users_login_returns_404(
    auth_client, make_website, make_action_history, other_user, login_live_view, capture
):
    website = make_website(owner=other_user)
    action_history = make_action_history(website, ActionStatusCode.IN_PROGRESS)
    login_live_view.start(action_history.id)

    response = auth_client.get(f"/api/action_history/{action_history.id}/live")

    assert response.status_code == 404
    capture.assert_not_called()


def test_login_live_view_of_login_that_is_not_running_returns_404(
    auth_client, make_website, make_action_history, login_live_view, capture
):
    website = make_website()
    running = make_action_history(website, ActionStatusCode.IN_PROGRESS)
    stale = make_action_history(website, ActionStatusCode.IN_PROGRESS)
    login_live_view.start(running.id)

    response = auth_client.get(f"/api/action_history/{stale.id}/live")

    assert response.status_code == 404
    capture.assert_not_called()


def test_login_live_view_unauthenticated(
    client, make_website, make_action_history, login_live_view, capture
):
    website = make_website()
    action_history = make_action_history(website, ActionStatusCode.IN_PROGRESS)
    login_live_view.start(action_history.id)

    response = client.get(f"/api/action_history/{action_history.id}/live")

    assert response.status_code == 401
    capture.assert_not_called()


def test_login_live_view_without_frames_returns_404(
    auth_client, make_website, make_action_history, login_live_view, capture, mocker
):
    mocker.patch("execution.login_live_view.FIRST_FRAME_TIMEOUT", 0.1)
    capture.return_value = None
    website = make_website()
    action_history = make_action_history(website, ActionStatusCode.IN_PROGRESS)
    login_live_view.start(action_history.id)

    response = auth_client.get(f"/api/action_history/{action_history.id}/live")

    assert response.status_code == 404
    capture.assert_called_once()
    assert capture.call_args.args[0].viewers == 0
