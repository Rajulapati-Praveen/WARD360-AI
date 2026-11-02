"""Built-in simulator: feeds simulated readings through the same pipeline as the HTTP /api/ingest."""
import asyncio

from sqlalchemy import select

from . import models, services
from .config import settings
from .database import SessionLocal
from .simulation import PatientSim
from .ws import manager


class SimRuntime:
    def __init__(self):
        self.task = None
        self.sims = {}

    @property
    def running(self):
        return self.task is not None and not self.task.done()

    def sim_for(self, patient):
        if patient.id not in self.sims:
            self.sims[patient.id] = PatientSim(services.get_baseline(patient))
        return self.sims[patient.id]

    def start(self):
        if not self.running:
            self.task = asyncio.create_task(self._loop())

    def stop(self):
        if self.task:
            self.task.cancel()
            self.task = None

    async def _loop(self):
        while True:
            try:
                with SessionLocal() as db:
                    events = []
                    for p in db.scalars(select(models.Patient)).all():
                        data = self.sim_for(p).next()
                        if data is None:
                            continue
                        dev = db.scalar(select(models.Device).where(models.Device.patient_id == p.id))
                        events += services.process_reading(db, p, dev, data)
                await manager.broadcast(events)
            except asyncio.CancelledError:
                raise
            except Exception as e:  # keep the demo alive
                print("simulator error:", e)
            await asyncio.sleep(settings.SIM_INTERVAL_SECONDS)


runtime = SimRuntime()
