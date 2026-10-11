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
    assert client.get("/api/user/data").status_code == 401
