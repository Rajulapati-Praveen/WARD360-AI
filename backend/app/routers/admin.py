from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..security import require_roles
from ..util import iso

router = APIRouter(prefix="/api", tags=["admin"])


@router.get("/audit-logs")
def audit_logs(limit: int = 100, db: Session = Depends(get_db), user=Depends(require_roles("admin"))):
    rows = db.execute(select(models.AuditLog, models.User.name).outerjoin(models.User, models.User.id == models.AuditLog.user_id)
                      .order_by(models.AuditLog.id.desc()).limit(min(limit, 500))).all()
    return [{"id": a.id, "user": n or "-", "action": a.action, "target": a.target, "ts": iso(a.ts)} for a, n in rows]
