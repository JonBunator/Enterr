def test_health(client):
    assert client.get("/api/health").json() == {"status": "healthy"}
