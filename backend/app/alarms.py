from sqlalchemy import func, select
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


def update_heater_escalation(db: Session, room: Room, reading: Reading) -> None:
    if not room.heater_on or room.heater_on_since is None:
        return

    alarm = active_alarm(db, room.id, "equipment_fault")

    if reading.temperature >= settings.warn_below_c:
        if alarm:
            alarm.cleared_at = utcnow()
        return

    elapsed = (utcnow() - room.heater_on_since).total_seconds()
    if elapsed < settings.heater_escalate_after_s:
        return

    lowest_temp = db.scalar(
        select(func.min(Reading.temperature))
        .where(Reading.room_id == room.id, Reading.created_at >= room.heater_on_since)
    )
    if lowest_temp is None:
        return

    if reading.temperature - lowest_temp >= settings.heater_min_rise_c:
        if alarm:
            alarm.cleared_at = utcnow()
        return

    if alarm is None:
        db.add(Alarm(
            room_id=room.id, kind="equipment_fault", severity="red", priority="urgent",
            message=f"{room.name}: heater on for {int(elapsed)}s with no temperature rise. "
                    "Equipment fault: escalate to on-call",
        ))