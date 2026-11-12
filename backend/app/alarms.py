from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Alarm, Reading, Room, utcnow
from app.rules import evaluate_temperature

SEVERITY_RANK = {"yellow": 1, "red": 2}
PRIORITY_RANK = {"low": 0, "normal": 1, "urgent": 2}


def active_alarm(db: Session, room_id: int, kind: str) -> Alarm | None:
    return db.scalar(
        select(Alarm).where(
            Alarm.room_id == room_id, Alarm.kind == kind, Alarm.cleared_at.is_(None)
        )
    )


def update_cold_alarm(db: Session, room: Room, reading: Reading) -> None:
    result = evaluate_temperature(
        reading.temperature, reading.occupied,
        settings.warn_below_c, settings.critical_below_c,
    )
    alarm = active_alarm(db, room.id, "cold")

    if result is None:
        clear_at = settings.warn_below_c + settings.clear_deadband_c
        if alarm and reading.temperature >= clear_at:
            alarm.cleared_at = utcnow()
        return

    severity, priority = result
    state = "occupied" if reading.occupied else "empty"
    message = f"{room.name} is {reading.temperature:.1f}°C ({state})"

    if alarm is None:
        db.add(Alarm(room_id=room.id, kind="cold", severity=severity,
                     priority=priority, message=message))
        return

    new_rank = (SEVERITY_RANK[severity], PRIORITY_RANK[priority])
    old_rank = (SEVERITY_RANK[alarm.severity], PRIORITY_RANK[alarm.priority])
    if new_rank > old_rank:
        alarm.acknowledged_at = None

    alarm.severity = severity
    alarm.priority = priority
    alarm.message = message