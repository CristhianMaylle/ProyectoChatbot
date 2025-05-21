from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.reminder import ReminderCreate, ReminderOut
from app.services.reminders import schedule_reminder, get_reminders

router = APIRouter()


@router.post("/", response_model=str)
async def create_reminder(data: ReminderCreate, db: AsyncSession = Depends(get_db)):
    return await schedule_reminder(data.user_id, data.frequency, db)


@router.get("/", response_model=list[ReminderOut])
async def list_reminders(user_id: int, db: AsyncSession = Depends(get_db)):
    return await get_reminders(user_id, db)
