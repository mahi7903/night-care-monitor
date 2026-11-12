from app.config import settings


def post_reading(client, room_id, temperature, occupied=True):
    return client.post(
        "/api/readings",
        json={"room_id": room_id, "temperature": temperature, "occupied": occupied},
    )


def active_alarms(client):
    return client.get("/api/alarms", params={"active_only": True}).json()


def test_reading_out_of_range_is_rejected(client):
    res = post_reading(client, 1, 999)
    assert res.status_code == 422


def test_reading_for_unknown_room_returns_404(client):
    res = post_reading(client, 99, 19.0)
    assert res.status_code == 404


def test_cold_occupied_room_raises_urgent_alarm(client):
    post_reading(client, 1, 15.0)
    alarms = active_alarms(client)
    assert len(alarms) == 1
    assert alarms[0]["severity"] == "red"
    assert alarms[0]["priority"] == "urgent"


def test_alarm_clears_only_after_deadband(client):
    post_reading(client, 1, 17.5)
    post_reading(client, 1, 18.2)
    assert len(active_alarms(client)) == 1
    post_reading(client, 1, 18.6)
    assert active_alarms(client) == []


def test_acknowledge_sets_timestamp(client):
    post_reading(client, 1, 17.0)
    alarm_id = active_alarms(client)[0]["id"]
    res = client.post(f"/api/alarms/{alarm_id}/acknowledge")
    assert res.status_code == 200
    assert res.json()["acknowledged_at"] is not None


def test_heater_with_no_effect_escalates_then_clears(client, monkeypatch):
    monkeypatch.setattr(settings, "heater_escalate_after_s", 0)
    post_reading(client, 1, 15.0)
    client.post("/api/rooms/1/heater", json={"on": True})
    post_reading(client, 1, 15.0)
    post_reading(client, 1, 14.8)

    kinds = [a["kind"] for a in active_alarms(client)]
    assert "equipment_fault" in kinds

    post_reading(client, 1, 15.6)
    kinds = [a["kind"] for a in active_alarms(client)]
    assert "equipment_fault" not in kinds