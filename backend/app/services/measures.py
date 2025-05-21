# Lecturas de oxígeno
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.measurement import Measurement
from datetime import datetime, timedelta, timezone


async def record_measure(user_id: int, pulse: int, spo2: int, db: AsyncSession):
    status = classify_oxygen_level(spo2)
    measurement = Measurement(
        user_id=user_id,
        pulse=pulse,
        spo2=spo2,
        status=status,
        measured_at=datetime.now(timezone.utc),
    )
    db.add(measurement)
    await db.commit()
    return status


async def get_latest_measure(user_id: int, db: AsyncSession):
    result = await db.execute(
        select(Measurement)
        .where(Measurement.user_id == user_id)
        .order_by(desc(Measurement.measured_at))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_measure_history(user_id: int, date_range: str, db: AsyncSession):
    today = datetime.now(timezone.utc)
    if date_range == "1d":
        start = today - timedelta(days=1)
    elif date_range == "7d":
        start = today - timedelta(days=7)
    else:
        start = today - timedelta(days=30)

    result = await db.execute(
        select(Measurement)
        .where(Measurement.user_id == user_id, Measurement.measured_at >= start)
        .order_by(Measurement.measured_at)
    )
    return result.scalars().all()


def classify_oxygen_level(spo2: int) -> str:
    if spo2 >= 95:
        return "Normal"
    elif spo2 >= 90:
        return "Precaución"
    else:
        return "Crítico"
