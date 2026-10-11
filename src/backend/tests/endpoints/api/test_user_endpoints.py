from utils.security import decode_token


# ---------------------------- POST /api/user/login ----------------------------


def test_login(client, user):
    response = client.post(
        "/api/user/login", data={"username": "testuser", "password": "testpass123"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert decode_token(body["access_token"]) == "testuser"
    assert response.cookies["access_token"].strip('"') == f"Bearer {body['access_token']}"


def test_login_with_wrong_password(client, user):
    response = client.post(
        "/api/user/login", data={"username": "testuser", "password": "wrong"}
    )

    assert response.status_code == 401
    assert "access_token" not in response.cookies


def test_login_with_unknown_user(client, user):
    response = client.post(
        "/api/user/login", data={"username": "nobody", "password": "testpass123"}
    )

    assert response.status_code == 401


# ---------------------------- POST /api/user/logout ----------------------------


def test_logout_deletes_cookie(auth_client):
    response = auth_client.post("/api/user/logout")

    assert response.status_code == 200
    set_cookie = response.headers["set-cookie"]
    assert set_cookie.startswith("access_token=")
    assert "Max-Age=0" in set_cookie


# ---------------------------- GET /api/user/data ----------------------------


def test_get_user_data(auth_client):
    response = auth_client.get("/api/user/data")

    assert response.status_code == 200
    assert response.json() == {"username": "testuser"}


def test_get_user_data_unauthenticated(client):
    assert client.get("/api/user/data").status_code == 401


def test_get_user_data_with_invalid_token(client):
    client.cookies.set("access_token", "Bearer invalid-token")
    assert client.get("/api/user/data").status_code == 401
