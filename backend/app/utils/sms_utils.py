# app/utils/sms_utils.py
import logging
import httpx
from app.config import settings

# Configurar logging
logger = logging.getLogger(__name__)


async def send_sms_twilio(to: str, message: str):
    """
    Envía un SMS usando Twilio.

    Args:
        to: Número de teléfono del destinatario (formato E.164, ej: +51987654321)
        message: Contenido del mensaje

    Returns:
        bool: True si el envío fue exitoso, False en caso contrario
    """
    try:
        # URL de la API de Twilio
        url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"

        # Datos para la solicitud
        data = {"To": to, "From": settings.TWILIO_PHONE_NUMBER, "Body": message}

        # Autenticación básica con SID y token
        auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        # Realizar solicitud POST
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data, auth=auth)

        # Verificar respuesta
        if response.status_code == 201:
            logger.info(f"SMS enviado exitosamente a {to}")
            return True
        else:
            logger.error(f"Error al enviar SMS: {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error al enviar SMS a {to}: {str(e)}")
        return False


async def send_sms_messagebird(to: str, message: str):
    """
    Envía un SMS usando MessageBird.

    Args:
        to: Número de teléfono del destinatario (formato E.164, ej: +51987654321)
        message: Contenido del mensaje

    Returns:
        bool: True si el envío fue exitoso, False en caso contrario
    """
    try:
        # URL de la API de MessageBird
        url = "https://rest.messagebird.com/messages"

        # Datos para la solicitud
        data = {
            "recipients": to,
            "originator": settings.MESSAGEBIRD_ORIGINATOR,
            "body": message,
        }

        # Headers con la clave de API
        headers = {
            "Authorization": f"AccessKey {settings.MESSAGEBIRD_ACCESS_KEY}",
            "Content-Type": "application/json",
        }

        # Realizar solicitud POST
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)

        # Verificar respuesta
        if response.status_code == 201:
            logger.info(f"SMS enviado exitosamente a {to}")
            return True
        else:
            logger.error(f"Error al enviar SMS: {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error al enviar SMS a {to}: {str(e)}")
        return False


async def send_sms(to: str, message: str):
    """
    Envía un SMS usando el proveedor configurado.

    Args:
        to: Número de teléfono del destinatario
        message: Contenido del mensaje

    Returns:
        bool: True si el envío fue exitoso, False en caso contrario
    """
    # Verificar que el número tenga formato internacional
    if not to.startswith("+"):
        to = f"+{to}"

    # Seleccionar el proveedor configurado
    provider = settings.SMS_PROVIDER.lower()

    if provider == "twilio":
        return await send_sms_twilio(to, message)
    elif provider == "messagebird":
        return await send_sms_messagebird(to, message)
    else:
        logger.error(f"Proveedor de SMS no soportado: {provider}")
        return False


async def send_test_sms(to: str):
    """Envía un SMS de prueba para verificar la configuración."""
    message = "Prueba de Oxymonitor: Si recibes este mensaje, la configuración de SMS está funcionando correctamente."
    return await send_sms(to, message)
