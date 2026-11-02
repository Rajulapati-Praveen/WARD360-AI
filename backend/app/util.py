from datetime import datetime, timezone


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def aware(dt):
    """SQLite returns naive datetimes; we always store UTC, so re-attach it."""
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def iso(dt):
    dt = aware(dt)
    return dt.isoformat() if dt else None
