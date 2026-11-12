from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    heater_on: Mapped[bool] = mapped_column(default=False)
    heater_on_since: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cold_fault: Mapped[bool] = mapped_column(default=False)
    heater_failed: Mapped[bool] = mapped_column(default=False)

    readings: Mapped[list["Reading"]] = relationship(back_populates="room")


class Reading(Base):
    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    temperature: Mapped[float]
    occupied: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )

    room: Mapped[Room] = relationship(back_populates="readings")


class Alarm(Base):
    __tablename__ = "alarms"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    kind: Mapped[str] = mapped_column(String(30))
    severity: Mapped[str] = mapped_column(String(10))
    priority: Mapped[str] = mapped_column(String(10))
    message: Mapped[str] = mapped_column(String(200))
    raised_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cleared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    room: Mapped[Room] = relationship()