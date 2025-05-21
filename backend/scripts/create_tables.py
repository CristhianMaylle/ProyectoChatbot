# scripts/create_tables.py

import asyncio
import sys
import os

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, engine
from app.models import (
    User,
    Measurement,
    Alert,
    NotificationSetting,
    Reminder,
    ChatLog,
    AdminExport,
)


async def create_tables():
    async with engine.begin() as conn:
        # Eliminar tablas existentes (opcional, comenta si no quieres eliminar)
        # await conn.run_sync(Base.metadata.drop_all)

        # Crear todas las tablas
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Tablas creadas correctamente")


if __name__ == "__main__":
    asyncio.run(create_tables())
