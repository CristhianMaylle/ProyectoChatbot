from pydantic import BaseModel
from datetime import datetime
from typing import List


class LatestMeasure(BaseModel):
    spo2: int
    status: str
    measured_at: str
    pulse: int


class OxygenHistoryPoint(BaseModel):
    timestamp: str
    spo2: int
    pulse: int
    status: str


class DashboardResponse(BaseModel):
    latest_measure: LatestMeasure | None
    history: List[OxygenHistoryPoint]
    critical_alerts: int
