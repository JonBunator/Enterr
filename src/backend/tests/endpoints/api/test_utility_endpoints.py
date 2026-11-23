from datetime import datetime

import pytest

from dataAccess.database.database import ActionStatusCode, User, Website


# ---------------------------- GET /api/health ----------------------------


def test_health(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# ---------------------------- POST /api/trigger_login/{id} ----------------------------


def test_trigger_login(auth_client, session, make_website):
    website = make_website(next_schedule=datetime(2099, 1, 1))

    response = auth_client.post(f"/api/trigger_login/{website.id}")

    assert response.status_code == 200
    session.expire_all()
    assert session.get(Website, website.id).next_schedule < datetime(2099, 1, 1)


def test_trigger_login_of_other_user_returns_404(
    auth_client, session, make_website, other_user
):
    website = make_website(owner=other_user, next_schedule=datetime(2099, 1, 1))

    response = auth_client.post(f"/api/trigger_login/{website.id}")

    assert response.status_code == 404
    session.expire_all()
    assert session.get(Website, website.id).next_schedule == datetime(2099, 1, 1)


# ---------------------------- GET /api/screenshot/{id} ----------------------------


@pytest.fixture
def screenshot_dir(tmp_path, monkeypatch):
    """In dev mode screenshots are read from ../config/images relative to the cwd"""
    monkeypatch.delenv("RUN_MODE", raising=False)
    working_dir = tmp_path / "backend"
    working_dir.mkdir()
    monkeypatch.chdir(working_dir)
    images = tmp_path / "config" / "images"
    images.mkdir(parents=True)
    return images


SCREENSHOT_ID = "0b7a3c4e-5d6f-4a8b-9c0d-1e2f3a4b5c6d"


@pytest.fixture
def make_screenshot(session, screenshot_dir, make_website, make_action_history):
    """Stores a screenshot file that belongs to a login of the given user's website"""

    def _make_screenshot(owner: User = None, screenshot_id: str = SCREENSHOT_ID):
        website = make_website(owner=owner)
        action_history = make_action_history(website, ActionStatusCode.SUCCESS)
        action_history.screenshot_id = screenshot_id
        session.commit()
        (screenshot_dir / f"{screenshot_id}.png").write_bytes(b"\x89PNG fake image")

    return _make_screenshot


def test_get_screenshot(auth_client, make_screenshot):
    make_screenshot()

    response = auth_client.get(f"/api/screenshot/{SCREENSHOT_ID}")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content == b"\x89PNG fake image"


def test_get_screenshot_of_other_user_returns_404(
    auth_client, make_screenshot, other_user
):
    make_screenshot(owner=other_user)

    response = auth_client.get(f"/api/screenshot/{SCREENSHOT_ID}")

    assert response.status_code == 404


def test_get_screenshot_without_action_history_returns_404(
    auth_client, screenshot_dir
):
    (screenshot_dir / f"{SCREENSHOT_ID}.png").write_bytes(b"\x89PNG fake image")

    response = auth_client.get(f"/api/screenshot/{SCREENSHOT_ID}")

    assert response.status_code == 404


def test_get_missing_screenshot_file_returns_404(
    auth_client, make_screenshot, screenshot_dir
):
    make_screenshot()
    (screenshot_dir / f"{SCREENSHOT_ID}.png").unlink()

    response = auth_client.get(f"/api/screenshot/{SCREENSHOT_ID}")

    assert response.status_code == 404


@pytest.mark.parametrize("screenshot_id", ["abc", "..", "..%2Fsecret"])
def test_get_screenshot_with_invalid_id_returns_404(
    auth_client, screenshot_dir, screenshot_id
):
    response = auth_client.get(f"/api/screenshot/{screenshot_id}")

    assert response.status_code == 404


def test_get_screenshot_unauthenticated(client, make_screenshot):
    make_screenshot()

    assert client.get(f"/api/screenshot/{SCREENSHOT_ID}").status_code == 401
