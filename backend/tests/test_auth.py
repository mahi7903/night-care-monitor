def test_login_returns_token(anon_client):
    res = anon_client.post("/api/auth/login", json={"username": "nurse", "password": "correct-horse"})
    assert res.status_code == 200
    assert res.json()["access_token"]


def test_login_with_wrong_password_is_rejected(anon_client):
    res = anon_client.post("/api/auth/login", json={"username": "nurse", "password": "wrong"})
    assert res.status_code == 401


def test_dashboard_data_requires_login(anon_client):
    assert anon_client.get("/api/alarms").status_code == 401


def test_posting_readings_requires_device_key(anon_client):
    res = anon_client.post(
        "/api/readings", json={"room_id": 1, "temperature": 19.0, "occupied": True}
    )
    assert res.status_code == 401