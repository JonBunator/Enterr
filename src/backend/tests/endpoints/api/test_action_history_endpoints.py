def test_manual_action_history(auth_client, webhooks, make_website):
    website = make_website()

    response = auth_client.post(f"/api/action_history/manual_add/{website.id}")
    assert response.status_code == 200
    assert response.json()["execution_status"] == "SUCCESS"

    histories = auth_client.get(
        "/api/action_history", params={"website_id": website.id}
    ).json()["items"]
    assert len(histories) == 1

    last_login = auth_client.get(
        f"/api/action_history/last_successful_login/{website.id}"
    ).json()
    assert last_login["action_history"]["id"] == histories[0]["id"]

    webhooks.action_history_changed.assert_called_once()
