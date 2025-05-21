# backend/app/services/mcp/context.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.chat_log import ChatLog
from datetime import datetime, timezone, timedelta


# Cargar historial de conversación de un usuario
async def load_chat_context(
    db: AsyncSession, user_id: int, limit: int = 10
) -> list[dict]:
    result = await db.execute(
        select(ChatLog)
        .where(ChatLog.user_id == user_id)
        .order_by(ChatLog.timestamp.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    messages.reverse()  # Invertir para mantener orden correcto
    return [{"role": msg.role, "content": msg.message} for msg in messages]


# Guardar un nuevo mensaje en el historial
async def store_message(db: AsyncSession, user_id: int, role: str, message: str):
    new_msg = ChatLog(
        user_id=user_id,
        role=role,
        message=message,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(new_msg)
    await db.commit()


# Verificar si es una nueva sesión de chat (sin mensajes en las últimas 2 horas)
async def is_new_session(db: AsyncSession, user_id: int) -> bool:
    # Definir el tiempo límite para considerar una nueva sesión (2 horas)
    session_timeout = datetime.now(timezone.utc) - timedelta(hours=2)

    # Buscar el último mensaje del usuario
    result = await db.execute(
        select(ChatLog)
        .where(ChatLog.user_id == user_id)
        .order_by(ChatLog.timestamp.desc())
        .limit(1)
    )
    last_message = result.scalar_one_or_none()

    # Si no hay mensajes o el último mensaje es más antiguo que el timeout, es una nueva sesión
    if not last_message or last_message.timestamp < session_timeout:
        return True

    return False


# Obtener estadísticas de chat de un usuario
async def get_chat_stats(db: AsyncSession, user_id: int) -> dict:
    # Contar total de mensajes
    result = await db.execute(
        select(func.count(ChatLog.id)).where(ChatLog.user_id == user_id)
    )
    total_messages = result.scalar_one()

    # Contar mensajes del usuario
    result = await db.execute(
        select(func.count(ChatLog.id)).where(
            ChatLog.user_id == user_id, ChatLog.role == "user"
        )
    )
    user_messages = result.scalar_one()

    # Contar mensajes del asistente
    result = await db.execute(
        select(func.count(ChatLog.id)).where(
            ChatLog.user_id == user_id, ChatLog.role == "assistant"
        )
    )
    assistant_messages = result.scalar_one()

    # Obtener fecha del primer mensaje
    result = await db.execute(
        select(ChatLog.timestamp)
        .where(ChatLog.user_id == user_id)
        .order_by(ChatLog.timestamp.asc())
        .limit(1)
    )
    first_message = result.scalar_one_or_none()

    return {
        "total_messages": total_messages,
        "user_messages": user_messages,
        "assistant_messages": assistant_messages,
        "first_interaction": first_message.isoformat() if first_message else None,
    }
