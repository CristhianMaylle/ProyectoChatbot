from pydantic import BaseModel
from datetime import datetime


class AlertOut(BaseModel):
    message: str
    alert_type: str
    sent: bool
    sent_at: datetime | None = None

    class Config:
        orm_mode = True
