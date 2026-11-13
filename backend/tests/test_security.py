PREFLIGHT = {"Access-Control-Request-Method": "GET"}


def test_cors_allows_configured_origin(anon_client):
    res = anon_client.options("/api/rooms", headers={"Origin": "http://allowed.test", **PREFLIGHT})
    assert res.headers.get("access-control-allow-origin") == "http://allowed.test"


def test_cors_blocks_unknown_origin(anon_client):
    res = anon_client.options("/api/rooms", headers={"Origin": "http://evil.test", **PREFLIGHT})
    assert "access-control-allow-origin" not in res.headers


def test_login_locks_after_repeated_failures(anon_client):
    for _ in range(5):
        anon_client.post("/api/auth/login", json={"username": "nurse", "password": "wrong"})
    res = anon_client.post("/api/auth/login", json={"username": "nurse", "password": "correct-horse"})
    assert res.status_code == 429