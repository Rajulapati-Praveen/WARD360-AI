"""Creates SYNTHETIC demo users, patients, devices and history. Safe to run repeatedly."""
from app.database import Base, SessionLocal, engine
from app.seed_data import seed

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    print("Seeded synthetic demo data." if seed(db) else "Database already seeded.")
