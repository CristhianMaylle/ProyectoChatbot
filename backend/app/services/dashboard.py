# backend/app/services/dashboard.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from datetime import datetime, timedelta, timezone
from app.models.measurement import Measurement
from app.models.alert import Alert


# 1. Última medición (oxígeno y estado)
async def get_latest_oxygen_data(user_id: int, db: AsyncSession):
    result = await db.execute(
        select(Measurement)
        .where(Measurement.user_id == user_id)
        .order_by(desc(Measurement.measured_at))
        .limit(1)
    )
    measurement = result.scalar_one_or_none()

    if not measurement:
        return None

    return {
        "spo2": measurement.spo2,
        "status": measurement.status,
        "measured_at": measurement.measured_at.isoformat(),
        "pulse": measurement.pulse,
    }


# 2. Gráfico histórico (últimos 30 días)
async def get_oxygen_history(user_id: int, db: AsyncSession, days: int):
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(
            Measurement.measured_at,
            Measurement.spo2,
            Measurement.pulse,
            Measurement.status,
        )
        .where(Measurement.user_id == user_id, Measurement.measured_at >= start_date)
        .order_by(Measurement.measured_at)
    )
    history = result.all()
    return [
        {
            "timestamp": row[0].isoformat(),
            "spo2": row[1],
            "pulse": row[2],
            "status": row[3],
        }
        for row in history
    ]


# 3. Conteo de alertas críticas
async def get_critical_alert_count(user_id: int, db: AsyncSession):
    result = await db.execute(
        select(func.count(Alert.id)).where(
            and_(Alert.user_id == user_id, Alert.message.ilike("%Crítico%"))
        )
    )
    count = result.scalar()
    return count
