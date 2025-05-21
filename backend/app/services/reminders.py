# app/services/reminders.py
from app.models.reminder import Reminder
from app.models.user import User
from app.utils.email_utils import send_email
from app.utils.sms_utils import send_sms
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update


async def schedule_reminder(
    user_id: int, frequency: str, db: AsyncSession, time: str = None
):
    """
    Programa un recordatorio para medir oxígeno.

    Args:
        user_id: ID del usuario
        frequency: Frecuencia del recordatorio ('hourly' o 'daily')
        db: Sesión de base de datos
        time: Hora específica para recordatorios diarios (formato HH:MM)

    Returns:
        str: Mensaje de confirmación
    """
    # Calcular próxima ejecución
    now = datetime.now(timezone.utc)

    if frequency == "hourly":
        next_run = now + timedelta(hours=1)
    else:  # daily
        # Si se especifica una hora, programar para esa hora
        if time:
            try:
                hour, minute = map(int, time.split(":"))
                next_day = now + timedelta(days=1)
                next_run = datetime(
                    next_day.year,
                    next_day.month,
                    next_day.day,
                    hour,
                    minute,
                    0,
                    tzinfo=timezone.utc,
                )

                # Si la hora ya pasó hoy, programar para hoy
                if next_run.hour > now.hour or (
                    next_run.hour == now.hour and next_run.minute > now.minute
                ):
                    next_run = datetime(
                        now.year,
                        now.month,
                        now.day,
                        hour,
                        minute,
                        0,
                        tzinfo=timezone.utc,
                    )
            except ValueError:
                # Si el formato de hora es inválido, usar el predeterminado
                next_run = now + timedelta(days=1)
        else:
            # Sin hora específica, programar para 24 horas después
            next_run = now + timedelta(days=1)

    # Crear el recordatorio
    reminder = Reminder(
        user_id=user_id,
        action="Medir oxígeno",
        frequency=frequency,
        next_run=next_run,
        active=True,
        created_at=now,
    )

    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)

    # Formatear mensaje de confirmación
    if frequency == "hourly":
        return f"Recordatorio programado cada hora, comenzando a las {next_run.strftime('%H:%M')}"
    else:
        return f"Recordatorio programado diariamente a las {next_run.strftime('%H:%M')}"


async def get_reminders(user_id: int, db: AsyncSession):
    """Obtiene los recordatorios activos de un usuario."""
    result = await db.execute(
        select(Reminder).where(Reminder.user_id == user_id, Reminder.active == True)
    )
    return result.scalars().all()


async def cancel_reminder(reminder_id: int, db: AsyncSession):
    """Cancela un recordatorio específico."""
    result = await db.execute(select(Reminder).where(Reminder.id == reminder_id))
    reminder = result.scalar_one_or_none()

    if reminder:
        reminder.active = False
        await db.commit()
        return True

    return False


async def run_reminder_engine(db: AsyncSession):
    """
    Ejecuta el motor de recordatorios para enviar notificaciones programadas.
    Esta función debe ser llamada periódicamente (por ejemplo, cada minuto)
    mediante un programador de tareas o un worker.
    """
    now = datetime.now(timezone.utc)

    # Obtener recordatorios pendientes
    result = await db.execute(
        select(Reminder).where(Reminder.next_run <= now, Reminder.active == True)
    )
    reminders = result.scalars().all()

    for reminder in reminders:
        # Obtener información del usuario
        user_result = await db.execute(select(User).where(User.id == reminder.user_id))
        user = user_result.scalar_one_or_none()

        if not user:
            continue

        # Enviar recordatorio según preferencias del usuario
        sent_ok = False

        # Verificar si el usuario tiene configuración de notificaciones
        if user.notification and user.notification.sms_enabled and user.phone:
            # Enviar por SMS
            message = f"RECORDATORIO OXYMONITOR: Es hora de medir tu nivel de oxígeno."
            sent_ok = await send_sms(user.phone, message)

        # Si no se envió por SMS o falló, intentar por correo
        if not sent_ok and user.email:
            subject = "Recordatorio de Medición - Oxymonitor"
            body = f"""
            RECORDATORIO DE MEDICIÓN
            
            Es hora de medir tu nivel de oxígeno.
            
            Recuerda registrar tu medición en la aplicación Oxymonitor para mantener un seguimiento adecuado.
            
            Este es un mensaje automático del sistema Oxymonitor.
            """
            sent_ok = await send_email(user.email, subject, body)

        # Reprogramar el próximo recordatorio
        if reminder.frequency == "hourly":
            reminder.next_run = now + timedelta(hours=1)
        else:  # daily
            reminder.next_run = now + timedelta(days=1)

    # Guardar cambios
    if reminders:
        await db.commit()

    return len(reminders)  # Devolver cantidad de recordatorios procesados
