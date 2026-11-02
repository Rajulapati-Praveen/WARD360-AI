"""10 scenarios from the project brief. All data is SYNTHETIC."""
from datetime import timedelta

from app import services
from app.database import SessionLocal
from app.util import now_utc
from conftest import post_reading


def alerts_for(client, headers, pid, **q):
    return client.get("/api/alerts", params={"patient_id": pid, **q}, headers=headers).json()


def test_1_normal_readings(client, caregiver, new_patient):
    p = new_patient()
    r = post_reading(client, p["device"]["id"])
    assert r["risk"] == "normal" and r["anomaly"] is False
    assert alerts_for(client, caregiver, p["id"]) == []


def test_2_unusual_heart_rate(client, caregiver):
    # seeded patient 1 has history, so Isolation Forest is active too
    r = post_reading(client, 1, heart_rate=140)
    assert r["anomaly"] is True
    live = client.get("/api/patients/1/live", headers=caregiver).json()
    assert live["anomaly"]["feature"] == "heart_rate"
    assert any(a["source"] == "risk" for a in alerts_for(client, caregiver, 1))


def test_3_low_spo2(client, caregiver, new_patient):
    p = new_patient()
    levels = [post_reading(client, p["device"]["id"], spo2=85)["risk"] for _ in range(3)]
    assert levels[0] in ("warning", "critical") and levels[-1] == "critical"
    assert any(a["level"] == "critical" for a in alerts_for(client, caregiver, p["id"]))


def test_4_increasing_trend(client, caregiver, new_patient):
    p = new_patient()
    for i in range(25):
        post_reading(client, p["device"]["id"], heart_rate=75 + i * 1.2)
    t = client.get(f"/api/patients/{p['id']}/analysis", headers=caregiver).json()["trends"]["heart_rate"]
    assert t["direction"] == "rising" and t["abnormal"] is True and len(t["forecast"]) == 10
    assert any(a["source"] == "trend" for a in alerts_for(client, caregiver, p["id"]))


def test_5_sensor_disconnection(client, caregiver, new_patient):
    p = new_patient()
    post_reading(client, p["device"]["id"])
    with SessionLocal() as db:
        ev = services.run_device_check(db, now=now_utc() + timedelta(seconds=120))
    assert any(e["type"] == "device" for e in ev)
    dev = client.get(f"/api/patients/{p['id']}", headers=caregiver).json()["devices"][0]
    assert dev["status"] == "offline"
    assert any(a["source"] == "device" for a in alerts_for(client, caregiver, p["id"]))


def test_6_missing_and_invalid_data(client, caregiver, new_patient):
    p = new_patient()
    r = post_reading(client, p["device"]["id"], heart_rate=None, spo2=None, temperature=None, resp_rate=None)
    assert r["quality"] == "missing"
    assert client.get(f"/api/patients/{p['id']}/live", headers=caregiver).json()["risk"]["level"] == "unknown"
    r = post_reading(client, p["device"]["id"], heart_rate=500)  # physiologically impossible -> rejected value
    assert r["quality"] == "poor" and r["issues"]
    last = client.get(f"/api/patients/{p['id']}/live", headers=caregiver).json()["reading"]
    assert last["heart_rate"] is None and last["ts"]


def test_7_multiple_patients(client, caregiver, new_patient):
    a, b = new_patient("Synthetic Multi A"), new_patient("Synthetic Multi B")
    post_reading(client, a["device"]["id"], heart_rate=60)
    post_reading(client, b["device"]["id"], heart_rate=90)
    rows = {p["id"]: p for p in client.get("/api/patients", headers=caregiver).json()}
    assert len(rows) >= 5
    assert rows[a["id"]]["latest"]["heart_rate"] == 60 and rows[b["id"]]["latest"]["heart_rate"] == 90


def test_8_acknowledge_alert(client, caregiver, new_patient):
    p = new_patient()
    al = client.post(f"/api/patients/{p['id']}/emergency", json={"message": "test"}, headers=caregiver).json()
    r = client.post(f"/api/alerts/{al['id']}/acknowledge", json={"note": "On my way"}, headers=caregiver)
    assert r.status_code == 200 and r.json()["status"] == "acknowledged"
    assert r.json()["acknowledgements"][0]["note"] == "On my way"
    assert client.post(f"/api/alerts/{al['id']}/acknowledge", json={}, headers=caregiver).status_code == 409


def test_9_unacknowledged_escalation(client, caregiver, new_patient):
    p = new_patient()
    al = client.post(f"/api/patients/{p['id']}/emergency", json={}, headers=caregiver).json()
    with SessionLocal() as db:
        ev = services.run_escalation_check(db, now=now_utc() + timedelta(seconds=300), seconds=60)
    assert any(e["alert"]["id"] == al["id"] for e in ev)
    full = alerts_for(client, caregiver, p["id"])[0]
    assert full["status"] == "escalated" and full["escalated_at"]
    assert any(n["kind"] == "escalation" for n in full["notifications"])


def test_10_unauthorised_access(client, admin, caregiver, new_patient):
    p = new_patient()
    client.post("/api/users", json={"name": "Other Caregiver", "email": "other@ward360.test",
                                    "password": "Other@1234", "role": "caregiver"}, headers=admin)
    tok = client.post("/api/auth/login", json={"email": "other@ward360.test", "password": "Other@1234"}).json()["token"]
    other = {"Authorization": f"Bearer {tok}"}
    assert client.get(f"/api/patients/{p['id']}", headers=other).status_code == 403
    assert client.get(f"/api/patients/{p['id']}/vitals", headers=other).status_code == 403
    assert client.get("/api/patients", headers=other).json() == []
    assert client.get(f"/api/patients/{p['id']}").status_code == 401
    assert client.post("/api/patients", json={"name": "X Y", "age": 5}, headers=caregiver).status_code == 403
    assert client.post("/api/ingest", json={"device_id": 1}, headers={"X-Device-Key": "wrong"}).status_code == 401
    assert client.get("/api/audit-logs", headers=caregiver).status_code == 403
    logs = client.get("/api/audit-logs", headers=admin).json()
    assert any(l["action"] == "access_denied" for l in logs)


def test_extra_pdf_report_and_fall(client, caregiver):
    post_reading(client, 2, accel_magnitude=3.4, activity="fall_impact")
    assert any(a["source"] == "fall" for a in alerts_for(client, caregiver, 2))
    r = client.get("/api/reports/2/pdf?period=daily", headers=caregiver)
    assert r.status_code == 200 and r.content[:4] == b"%PDF"
