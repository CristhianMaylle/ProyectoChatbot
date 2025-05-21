from pydantic import BaseModel
from datetime import datetime


class MeasurementCreate(BaseModel):
    user_id: int
    spo2: int
    pulse: int


class AnonymousMeasurement(BaseModel):
    spo2: int
    pulse: int


class MeasurementOut(BaseModel):
    spo2: int
    pulse: int
    status: str
    measured_at: datetime

    class Config:
        orm_mode = True


class HistoryPoint(BaseModel):
    timestamp: str
    spo2: int
