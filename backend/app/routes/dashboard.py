from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard import (
    get_latest_oxygen_data,
    get_oxygen_history,
    get_critical_alert_count,
)

router = APIRouter()


@router.get("/", response_model=DashboardResponse)
async def dashboard(
    user_id: int, db: AsyncSession = Depends(get_db), days: str = "30d"
):
    try:
        days_int = int("".join(filter(str.isdigit, days)))
    except Exception:
        days_int = 30
    latest = await get_latest_oxygen_data(user_id, db)
    history = await get_oxygen_history(user_id, db, days_int)
    alerts = await get_critical_alert_count(user_id, db)
    return {"latest_measure": latest, "history": history, "critical_alerts": alerts}
