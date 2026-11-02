import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
_db = Path(tempfile.mkdtemp()) / "test.db"
os.environ.update({"DATABASE_URL": f"sqlite:///{_db}", "DEVICE_API_KEY": "test-key",
                   "SECRET_KEY": "test-secret", "DISABLE_BACKGROUND": "1"})

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.seed_data import seed  # noqa: E402


@pytest.fixture(scope="session")
def client():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db)
    with TestClient(app) as c:
        yield c


def _login(client, email, pw):
    r = client.post("/api/auth/login", json={"email": email, "password": pw})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


@pytest.fixture(scope="session")
def admin(client):
    return _login(client, "admin@ward360.test", "Admin@123")


@pytest.fixture(scope="session")
def caregiver(client):
    return _login(client, "caregiver@ward360.test", "Care@123")


@pytest.fixture()
def new_patient(client, admin):
    """Fresh synthetic patient (+ simulated device) so scenarios do not interfere."""
    def make(name="Synthetic Test Patient"):
        p = client.post("/api/patients", json={"name": name, "age": 70}, headers=admin).json()
        client.post(f"/api/patients/{p['id']}/assign", json={"user_id": 2}, headers=admin)
        return p
    return make


def post_reading(client, device_id, **vals):
    body = {"device_id": device_id, "heart_rate": 75, "spo2": 97, "temperature": 36.8, "resp_rate": 16, **vals}
    r = client.post("/api/ingest", json=body, headers={"X-Device-Key": "test-key"})
    assert r.status_code == 200, r.text
    return r.json()
