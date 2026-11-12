from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.alarms import update_cold_alarm
from app.database import get_db
from app.models import Alarm, Reading, Room
from app.schemas import AlarmOut, ReadingIn, ReadingOut, RoomOut

router = APIRouter(prefix="/api")


@router.get("/rooms", response_model=list[RoomOut])
def list_rooms(db: Session = Depends(get_db)):
    return db.scalars(select(Room).order_by(Room.id)).all()


@router.post("/readings", response_model=ReadingOut, status_code=status.HTTP_201_CREATED)
def create_reading(payload: ReadingIn, db: Session = Depends(get_db)):
    room = db.get(Room, payload.room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    reading = Reading(**payload.model_dump())
    db.add(reading)
    update_cold_alarm(db, room, reading)
    db.commit()
    db.refresh(reading)
    return reading


@router.get("/alarms", response_model=list[AlarmOut])
def list_alarms(active_only: bool = False, db: Session = Depends(get_db)):
    query = select(Alarm)
    if active_only:
        query = query.where(Alarm.cleared_at.is_(None))
    query = query.order_by(Alarm.raised_at.desc()).limit(100)
    return db.scalars(query).all()