from dataAccess.database.database import ActionStatusCode, Notification

NOTIFICATION_PAYLOAD = {
    "name": "My notification",
    "apprise_token": "json://localhost",
    "title": "{WEBSITE_NAME}",
    "body": "{STATUS}",
    "triggers": ["FAILED"],
}


# ---------------------------- GET /api/notifications ----------------------------


def test_get_notifications(auth_client, make_notification, other_user):
    notification = make_notification(triggers=[ActionStatusCode.FAILED])
    make_notification(owner=other_user)

    response = auth_client.get("/api/notifications")

    assert response.status_code == 200
    assert response.json()["items"] == [
        {
            "id": notification.id,
            "name": "My notification",
            "apprise_token": "json://localhost",
            "title": "{WEBSITE_NAME}",
            "body": "{STATUS}",
            "triggers": ["FAILED"],
        }
    ]


def test_get_notifications_unauthenticated(client):
    assert client.get("/api/notifications").status_code == 401


# ---------------------------- POST /api/notifications ----------------------------


def test_add_notification(auth_client, session, user, webhooks):
    response = auth_client.post("/api/notifications", json=NOTIFICATION_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body == NOTIFICATION_PAYLOAD | {"id": body["id"]}

    stored = session.get(Notification, body["id"])
    assert stored.user == user.id
    assert stored.triggers == [ActionStatusCode.FAILED]
    webhooks.notifications_changed.assert_called_once()


def test_add_invalid_notification_is_rejected(auth_client, session, webhooks):
    response = auth_client.post("/api/notifications", json={"name": "Missing fields"})

    assert response.status_code == 422
    assert session.query(Notification).count() == 0
    webhooks.notifications_changed.assert_not_called()


# ---------------------------- PUT /api/notifications/{id} ----------------------------


def test_edit_notification(auth_client, session, make_notification, webhooks):
    notification = make_notification(triggers=[ActionStatusCode.FAILED])

    response = auth_client.put(
        f"/api/notifications/{notification.id}",
        json={"title": "New title", "triggers": ["SUCCESS", "FAILED"]},
    )

    assert response.status_code == 200
    session.expire_all()
    stored = session.get(Notification, notification.id)
    assert stored.title == "New title"
    assert stored.name == "My notification"
    assert stored.triggers == [ActionStatusCode.SUCCESS, ActionStatusCode.FAILED]
    webhooks.notifications_changed.assert_called_once()


def test_edit_notification_of_other_user_returns_404(
    auth_client, session, make_notification, other_user, webhooks
):
    notification = make_notification(owner=other_user)

    response = auth_client.put(
        f"/api/notifications/{notification.id}", json={"title": "Hijacked"}
    )

    assert response.status_code == 404
    session.expire_all()
    assert session.get(Notification, notification.id).title == "{WEBSITE_NAME}"
    webhooks.notifications_changed.assert_not_called()


# ---------------------------- DELETE /api/notifications/{id} ----------------------------


def test_delete_notification(auth_client, session, make_notification, webhooks):
    notification = make_notification()

    response = auth_client.delete(f"/api/notifications/{notification.id}")

    assert response.status_code == 200
    session.expire_all()
    assert session.query(Notification).count() == 0
    webhooks.notifications_changed.assert_called_once()


def test_delete_notification_of_other_user_returns_404(
    auth_client, session, make_notification, other_user, webhooks
):
    notification = make_notification(owner=other_user)

    response = auth_client.delete(f"/api/notifications/{notification.id}")

    assert response.status_code == 404
    assert session.query(Notification).count() == 1
    webhooks.notifications_changed.assert_not_called()


# ---------------------------- POST /api/notifications/test ----------------------------


def test_test_notification(auth_client, session, notification_manager):
    response = auth_client.post("/api/notifications/test", json=NOTIFICATION_PAYLOAD)

    assert response.status_code == 200
    notification_manager.test_notification.assert_called_once()
    notification = notification_manager.test_notification.call_args.args[0]
    assert notification.apprise_token == "json://localhost"
    assert notification.title == "{WEBSITE_NAME}"
    assert notification.triggers == [ActionStatusCode.FAILED]
    assert session.query(Notification).count() == 0


def test_test_notification_unauthenticated(client, notification_manager):
    response = client.post("/api/notifications/test", json=NOTIFICATION_PAYLOAD)

    assert response.status_code == 401
    notification_manager.test_notification.assert_not_called()
