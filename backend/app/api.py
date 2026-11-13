from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import timedelta
from app.alarms import update_cold_alarm
from app.database import get_db

from app.alarms import active_alarm, update_cold_alarm, update_heater_escalation
from app.models import Alarm, Reading, Room, StaffUser, utcnow
from app.schemas import (
    AlarmOut, HeaterCommand, LoginIn, ReadingIn, ReadingOut, RoomOut, SimulationCommand, TokenOut,
)
from app.auth import (
    create_access_token, require_device, require_staff, require_staff_or_device, verify_password,
)
from app.ratelimit import login_limiter


router = APIRouter(prefix="/api")


@router.get("/rooms", response_model=list[RoomOut], dependencies=[Depends(require_staff_or_device)])
def list_rooms(db: Session = Depends(get_db)):
    return db.scalars(select(Room).order_by(Room.id)).all()


@router.get("/readings", response_model=list[ReadingOut], dependencies=[Depends(require_staff)])
def list_readings(minutes: int = Query(default=10, ge=1, le=60), db: Session = Depends(get_db)):
    since = utcnow() - timedelta(minutes=minutes)
    query = select(Reading).where(Reading.created_at >= since).order_by(Reading.created_at)
    return db.scalars(query).all()


@router.post("/readings", response_model=ReadingOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_device)])
def create_reading(payload: ReadingIn, db: Session = Depends(get_db)):
    room = db.get(Room, payload.room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    reading = Reading(**payload.model_dump())
    db.add(reading)
    update_cold_alarm(db, room, reading)
    update_heater_escalation(db, room, reading)
    db.commit()
    db.refresh(reading)
    return reading


@router.get("/alarms", response_model=list[AlarmOut], dependencies=[Depends(require_staff)])
def list_alarms(active_only: bool = False, db: Session = Depends(get_db)):
    query = select(Alarm)
    if active_only:
        query = query.where(Alarm.cleared_at.is_(None))
    query = query.order_by(Alarm.raised_at.desc()).limit(100)
    return db.scalars(query).all()


def get_room_or_404(db: Session, room_id: int) -> Room:
    room = db.get(Room, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.post("/alarms/{alarm_id}/acknowledge", response_model=AlarmOut, dependencies=[Depends(require_staff)])
def acknowledge_alarm(alarm_id: int, db: Session = Depends(get_db)):
    alarm = db.get(Alarm, alarm_id)
    if alarm is None:
        raise HTTPException(status_code=404, detail="Alarm not found")
    if alarm.acknowledged_at is None:
        alarm.acknowledged_at = utcnow()
        db.commit()
        db.refresh(alarm)
    return alarm


@router.post("/rooms/{room_id}/heater", response_model=RoomOut, dependencies=[Depends(require_staff)])
def set_heater(room_id: int, command: HeaterCommand, db: Session = Depends(get_db)):
    room = get_room_or_404(db, room_id)
    if command.on and not room.heater_on:
        room.heater_on_since = utcnow()
    if not command.on:
        room.heater_on_since = None
        alarm = active_alarm(db, room.id, "equipment_fault")
        if alarm:
            alarm.cleared_at = utcnow()
    room.heater_on = command.on
    db.commit()
    db.refresh(room)
    return room


@router.post("/rooms/{room_id}/simulate", response_model=RoomOut, dependencies=[Depends(require_staff)])
def simulate(room_id: int, command: SimulationCommand, db: Session = Depends(get_db)):
    room = get_room_or_404(db, room_id)
    for field, value in command.model_dump(exclude_none=True).items():
        setattr(room, field, value)
    db.commit()
    db.refresh(room)
    return room

@router.post("/auth/login", response_model=TokenOut)
def login(payload: LoginIn, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    key = f"{client_ip}:{payload.username.lower()}"
    if login_limiter.is_blocked(key):
        raise HTTPException(
            status_code=429, detail="Too many failed attempts. Try again in a few minutes."
        )

    user = db.scalar(select(StaffUser).where(StaffUser.username == payload.username))
    if user is None or not verify_password(payload.password, user.password_hash):
        login_limiter.record_failure(key)
        raise HTTPException(status_code=401, detail="Invalid username or password")

    login_limiter.reset(key)
    return TokenOut(access_token=create_access_token(user), username=user.username)