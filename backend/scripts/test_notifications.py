# scripts/test_notifications.py

import sys
import os
import asyncio

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.email_utils import send_test_email
from app.utils.sms_utils import send_test_sms


async def test_email():
    """Prueba el envío de correo electrónico."""
    print("Probando envío de correo electrónico...")
    email = input("Ingresa tu dirección de correo electrónico: ")

    result = await send_test_email(email)

    if result:
        print("✅ Correo enviado exitosamente. Verifica tu bandeja de entrada.")
    else:
        print("❌ Error al enviar el correo. Verifica la configuración SMTP.")


async def test_sms():
    """Prueba el envío de SMS."""
    print("Probando envío de SMS...")
    phone = input(
        "Ingresa tu número de teléfono (con código de país, ej: +51987654321): "
    )

    result = await send_test_sms(phone)

    if result:
        print("✅ SMS enviado exitosamente. Verifica tu teléfono.")
    else:
        print("❌ Error al enviar el SMS. Verifica la configuración del proveedor.")


async def main():
    """Menú principal para pruebas."""
    print("=== PRUEBA DE NOTIFICACIONES OXYMONITOR ===")
    print("1. Probar envío de correo electrónico")
    print("2. Probar envío de SMS")
    print("3. Probar ambos")
    print("0. Salir")

    option = input("Selecciona una opción: ")

    if option == "1":
        await test_email()
    elif option == "2":
        await test_sms()
    elif option == "3":
        await test_email()
        print("\n")
        await test_sms()
    elif option == "0":
        print("Saliendo...")
    else:
        print("Opción no válida.")


if __name__ == "__main__":
    asyncio.run(main())
