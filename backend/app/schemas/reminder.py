from pydantic import BaseModel
from datetime import datetime


class ReminderCreate(BaseModel):
    user_id: int
    frequency: str
    time: str | None = None


class ReminderOut(BaseModel):
    id: int
    action: str
    frequency: str
    next_run: datetime
    active: bool

    class Config:
        orm_mode = True
