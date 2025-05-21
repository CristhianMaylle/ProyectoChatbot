# app/services/alerts.py
from app.models.alert import Alert
from app.models.user import User
from app.utils.email_utils import send_email
from app.utils.sms_utils import send_sms
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


def check_oxygen_alert(spo2: int) -> bool:
    """Verifica si el nivel de oxígeno requiere una alerta."""
    return spo2 < 90


async def send_critical_alert(user_id: int, spo2: int, db: AsyncSession) -> str:
    """
    Envía una alerta crítica al usuario por nivel bajo de oxígeno.

    Args:
        user_id: ID del usuario
        spo2: Nivel de oxígeno medido
        db: Sesión de base de datos

    Returns:
        str: Mensaje indicando el resultado
    """
    message = f"Nivel crítico de oxígeno detectado: {spo2}%"

    # Obtener el usuario
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        return "Usuario no encontrado"

    # Determinar el tipo de alerta según las preferencias del usuario
    alert_type = "correo"  # Por defecto

    # Verificar si el usuario tiene configuración de notificaciones
    if user.notification:
        if user.notification.sms_enabled and user.phone:
            alert_type = "sms"

    # Crear registro de alerta
    alert = Alert(
        user_id=user_id,
        message=message,
        alert_type=alert_type,
        sent=False,  # Se marcará como enviado después de enviar
        sent_at=datetime.now(timezone.utc),
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)

    # Enviar la alerta según el tipo
    sent_ok = False

    if alert_type == "sms" and user.phone:
        # Enviar SMS
        sms_message = f"ALERTA OXYMONITOR: {message} Se recomienda buscar atención médica inmediata."
        sent_ok = await send_sms(user.phone, sms_message)

        if sent_ok:
            result_message = "Alerta enviada por SMS"
        else:
            # Si falla el SMS, intentar con correo como respaldo
            if user.email:
                email_subject = "ALERTA CRÍTICA - Oxymonitor"
                email_body = f"""
                ALERTA DE NIVEL CRÍTICO DE OXÍGENO
                
                Se ha detectado un nivel crítico de oxígeno en sangre: {spo2}%
                
                Este nivel está por debajo del umbral seguro y puede requerir atención médica inmediata.
                
                Por favor, consulte a un profesional de la salud lo antes posible.
                
                Este es un mensaje automático del sistema Oxymonitor.
                """
                sent_ok = await send_email(user.email, email_subject, email_body)
                result_message = "Alerta enviada por correo (SMS falló)"
            else:
                result_message = (
                    "No se pudo enviar la alerta (SMS falló, correo no disponible)"
                )

    elif user.email:
        # Enviar correo electrónico
        email_subject = "ALERTA CRÍTICA - Oxymonitor"
        email_body = f"""
        ALERTA DE NIVEL CRÍTICO DE OXÍGENO
        
        Se ha detectado un nivel crítico de oxígeno en sangre: {spo2}%
        
        Este nivel está por debajo del umbral seguro y puede requerir atención médica inmediata.
        
        Por favor, consulte a un profesional de la salud lo antes posible.
        
        Este es un mensaje automático del sistema Oxymonitor.
        """
        sent_ok = await send_email(user.email, email_subject, email_body)
        result_message = "Alerta enviada por correo"

    else:
        result_message = "No se pudo enviar la alerta (no hay contacto disponible)"

    # Actualizar el estado de envío en la base de datos
    alert.sent = sent_ok
    await db.commit()

    return result_message
