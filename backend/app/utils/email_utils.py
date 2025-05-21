# app/utils/email_utils.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import logging
from app.config import settings

# Configurar logging
logger = logging.getLogger(__name__)


async def send_email(to: str, subject: str, body: str, html_body: str = None):
    """
    Envía un correo electrónico usando la configuración SMTP definida en settings.

    Args:
        to: Dirección de correo del destinatario
        subject: Asunto del correo
        body: Cuerpo del mensaje en texto plano
        html_body: Cuerpo del mensaje en HTML (opcional)

    Returns:
        bool: True si el envío fue exitoso, False en caso contrario
    """
    try:
        # Crear mensaje
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_SENDER
        msg["To"] = to

        # Adjuntar versión texto plano
        msg.attach(MIMEText(body, "plain"))

        # Adjuntar versión HTML si está disponible
        if html_body:
            msg.attach(MIMEText(html_body, "html"))

        # Configurar conexión segura
        context = ssl.create_default_context()

        # Conectar al servidor SMTP
        if settings.SMTP_USE_TLS:
            # Para conexiones TLS (puerto 587 típicamente)
            server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
            server.starttls(context=context)
        else:
            # Para conexiones SSL (puerto 465 típicamente)
            server = smtplib.SMTP_SSL(
                settings.SMTP_SERVER, settings.SMTP_PORT, context=context
            )

        # Iniciar sesión
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)

        # Enviar correo
        server.sendmail(settings.SMTP_SENDER, to, msg.as_string())

        # Cerrar conexión
        server.quit()

        logger.info(f"Correo enviado exitosamente a {to}")
        return True

    except Exception as e:
        logger.error(f"Error al enviar correo a {to}: {str(e)}")
        return False


async def send_test_email(to: str):
    """Envía un correo de prueba para verificar la configuración."""
    subject = "Prueba de Configuración - Oxymonitor"
    body = """
    Este es un correo de prueba del sistema Oxymonitor.
    
    Si estás recibiendo este mensaje, la configuración de correo electrónico está funcionando correctamente.
    
    Saludos,
    El equipo de Oxymonitor
    """

    html_body = """
    <html>
    <body>
        <h2>Prueba de Configuración - Oxymonitor</h2>
        <p>Este es un correo de prueba del sistema Oxymonitor.</p>
        <p><strong>Si estás recibiendo este mensaje, la configuración de correo electrónico está funcionando correctamente.</strong></p>
        <p>Saludos,<br>El equipo de Oxymonitor</p>
    </body>
    </html>
    """

    return await send_email(to, subject, body, html_body)
