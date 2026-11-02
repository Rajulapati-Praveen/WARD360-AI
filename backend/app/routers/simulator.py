from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..security import audit, get_patient_or_403, require_roles
from ..simulation import SCENARIOS
from ..simulator_runtime import runtime

router = APIRouter(prefix="/api/simulator", tags=["simulator"])
can_control = require_roles("admin", "caregiver")


class ScenarioIn(BaseModel):
    patient_id: int
    scenario: str


@router.get("/status")
def status(user=Depends(can_control)):
    return {"running": runtime.running, "scenarios": SCENARIOS,
            "active": {pid: s.scenario for pid, s in runtime.sims.items()},
            "note": "All data from the simulator is SIMULATED, not a real measurement."}


@router.post("/start")
async def start(db: Session = Depends(get_db), user=Depends(can_control)):
    runtime.start()
    audit(db, user.id, "simulator_started")
    return {"running": True}


@router.post("/stop")
async def stop(db: Session = Depends(get_db), user=Depends(can_control)):
    runtime.stop()
    audit(db, user.id, "simulator_stopped")
    return {"running": False}


@router.post("/scenario")
def scenario(body: ScenarioIn, db: Session = Depends(get_db), user=Depends(can_control)):
    if body.scenario not in SCENARIOS:
        raise HTTPException(422, f"scenario must be one of {SCENARIOS}")
    p = get_patient_or_403(db, user, body.patient_id)
    runtime.sim_for(p).set_scenario(body.scenario)
    if body.scenario != "disconnect":
        dev = db.query(models.Device).filter_by(patient_id=p.id).first()
        if dev and dev.status == "offline":
            pass  # device returns online automatically on next reading
    audit(db, user.id, "scenario_set", f"patient:{p.id}:{body.scenario}")
    return {"patient_id": p.id, "scenario": body.scenario}
