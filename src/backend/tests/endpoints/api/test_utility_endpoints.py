from datetime import datetime

import pytest

from dataAccess.database.database import Website


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


def test_get_screenshot(auth_client, screenshot_dir):
    (screenshot_dir / "abc.png").write_bytes(b"\x89PNG fake image")

    response = auth_client.get("/api/screenshot/abc")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content == b"\x89PNG fake image"


def test_get_missing_screenshot_returns_404(auth_client, screenshot_dir):
    response = auth_client.get("/api/screenshot/missing")

    assert response.status_code == 404


def test_get_screenshot_unauthenticated(client, screenshot_dir):
    (screenshot_dir / "abc.png").write_bytes(b"\x89PNG fake image")

    assert client.get("/api/screenshot/abc").status_code == 401
