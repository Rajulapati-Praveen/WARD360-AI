
import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models, services
from .config import settings
from .database import Base, SessionLocal, engine, get_db
from .seed_data import seed
from .routers import admin, alerts, auth, monitoring, patients, reports, simulator
from .security import allowed_patient_ids, user_from_token
from .simulator_runtime import runtime
from .ws import manager


async def monitor_loop():
    """Detect disconnected devices and escalate unacknowledged alerts."""
    while True:
        await asyncio.sleep(5)

        try:
            with SessionLocal() as db:
                events = (
                    services.run_device_check(db)
                    + services.run_escalation_check(db)
                )

            await manager.broadcast(events)

        except asyncio.CancelledError:
            raise
        except Exception as e:
            print("Monitor error:", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)

    # Initialize synthetic demo accounts and sample data
    with SessionLocal() as db:
        seed(db)

    # Start background monitoring
    task = None

    if not settings.DISABLE_BACKGROUND:
        task = asyncio.create_task(monitor_loop())

    try:
        yield
    finally:
        runtime.stop()

        if task:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

        engine.dispose()


app = FastAPI(
    title="WARD360 AI",
    version="1.0.0",
    lifespan=lifespan,
    description=(
        "Home health monitoring decision-support prototype. "
        "SYNTHETIC data only. Not a medical device."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.CORS_ORIGINS.split(",")
        if origin.strip()
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
for router_module in (
    auth,
    patients,
    monitoring,
    alerts,
    simulator,
    reports,
    admin,
):
    app.include_router(router_module.router)


@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    return {
        "status": "ok",
        "disclaimer": (
            "Synthetic data. Decision-support prototype, "
            "not a medical device."
        ),
        "users": db.scalar(select(func.count(models.User.id))),
        "patients": db.scalar(select(func.count(models.Patient.id))),
        "devices": db.scalar(select(func.count(models.Device.id))),
        "simulator_running": runtime.running,
    }


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket, token: str = ""):
    with SessionLocal() as db:
        user = user_from_token(db, token)
        allowed = allowed_patient_ids(db, user) if user else None

    if not user:
        await ws.close(code=4401)
        return

    await ws.accept()
    manager.add(ws, allowed)

    try:
        while True:
            await ws.receive_text()

    except WebSocketDisconnect:
        manager.remove(ws)
