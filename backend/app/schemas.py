from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReadingIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    room_id: int = Field(gt=0)
    temperature: float = Field(ge=-20, le=60)
    occupied: bool


class ReadingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    temperature: float
    occupied: bool
    created_at: datetime


class RoomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    heater_on: bool
    cold_fault: bool
    heater_failed: bool


class AlarmOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    kind: str
    severity: str
    priority: str
    message: str
    raised_at: datetime
    acknowledged_at: datetime | None
    cleared_at: datetime | None

class HeaterCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    on: bool


class SimulationCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cold_fault: bool | None = None
    heater_failed: bool | None = None