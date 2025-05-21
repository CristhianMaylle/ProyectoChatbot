# scripts/test_all_functions.py
import sys
import os
import asyncio
import random
from datetime import datetime, timezone

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal, test_connection
from app.services.users import register_user, login_user, get_or_create_anonymous_user
from app.services.measures import (
    record_measure,
    get_latest_measure,
    get_measure_history,
)
from app.services.alerts import send_critical_alert
from app.services.reminders import schedule_reminder, get_reminders, cancel_reminder
from app.services.chatbot import process_user_message
from app.services.arduino_sensor import sensor
from app.utils.email_utils import send_test_email
from app.utils.sms_utils import send_test_sms
from app.schemas.user import UserCreate, LoginRequest
from app.schemas.chat import ChatRequest


async def test_database():
    """Prueba la conexión a la base de datos."""
    print("\n=== PRUEBA DE CONEXIÓN A LA BASE DE DATOS ===")
    try:
        await test_connection()
        print("✅ Conexión a la base de datos exitosa")
        return True
    except Exception as e:
        print(f"❌ Error de conexión a la base de datos: {e}")
        return False


async def test_auth(db: AsyncSession):
    """Prueba el registro y login de usuarios."""
    print("\n=== PRUEBA DE AUTENTICACIÓN ===")

    # Generar datos aleatorios para evitar conflictos
    random_suffix = random.randint(1000, 9999)
    test_email = f"test{random_suffix}@example.com"

    # Crear usuario de prueba
    user_data = UserCreate(
        name=f"Usuario Prueba {random_suffix}",
        email=test_email,
        password="password123",
        phone=f"+519876{random_suffix}",
    )

    try:
        # Registrar usuario
        print(f"Registrando usuario: {test_email}")
        register_result = await register_user(user_data, db)

        if "error" in register_result:
            print(f"❌ Error al registrar usuario: {register_result['error']}")
            return None

        print(f"✅ Usuario registrado correctamente con ID: {register_result['id']}")

        # Iniciar sesión
        login_data = LoginRequest(email=test_email, password="password123")
        login_result = await login_user(login_data, db)

        if "error" in login_result:
            print(f"❌ Error al iniciar sesión: {login_result['error']}")
            return None

        print(f"✅ Inicio de sesión exitoso para: {login_result['email']}")
        return login_result["id"]

    except Exception as e:
        print(f"❌ Error en prueba de autenticación: {e}")
        return None


async def test_anonymous_user(db: AsyncSession):
    """Prueba la creación de usuarios anónimos."""
    print("\n=== PRUEBA DE USUARIO ANÓNIMO ===")

    try:
        anon_user = await get_or_create_anonymous_user(db)
        print(f"✅ Usuario anónimo creado con ID: {anon_user.id}")
        return anon_user.id
    except Exception as e:
        print(f"❌ Error al crear usuario anónimo: {e}")
        return None


async def test_measure(user_id: int, db: AsyncSession):
    """Prueba el registro de mediciones."""
    print("\n=== PRUEBA DE REGISTRO DE MEDICIONES ===")

    try:
        # Registrar medición normal
        spo2_normal = random.randint(95, 99)
        pulse_normal = random.randint(60, 100)

        print(
            f"Registrando medición normal: SpO2={spo2_normal}%, Pulso={pulse_normal} BPM"
        )
        status = await record_measure(user_id, pulse_normal, spo2_normal, db)
        print(f"✅ Medición registrada con estado: {status}")

        # Registrar medición crítica
        spo2_critical = random.randint(80, 89)
        pulse_critical = random.randint(100, 120)

        print(
            f"Registrando medición crítica: SpO2={spo2_critical}%, Pulso={pulse_critical} BPM"
        )
        status = await record_measure(user_id, pulse_critical, spo2_critical, db)
        print(f"✅ Medición crítica registrada con estado: {status}")

        # Obtener última medición
        latest = await get_latest_measure(user_id, db)
        print(
            f"✅ Última medición: SpO2={latest.spo2}%, Pulso={latest.pulse} BPM, Estado={latest.status}"
        )

        # Obtener historial
        history = await get_measure_history(user_id, "7d", db)
        print(f"✅ Historial de mediciones: {len(history)} registros")

        return True
    except Exception as e:
        print(f"❌ Error en prueba de mediciones: {e}")
        return False


async def test_arduino_sensor():
    """Prueba la lectura del sensor Arduino."""
    print("\n=== PRUEBA DE SENSOR ARDUINO ===")

    try:
        print("Intentando conectar con el sensor Arduino...")
        if not sensor.connect():
            print(
                "⚠️ No se pudo conectar al sensor Arduino. Continuando con otras pruebas."
            )
            return False

        print("Leyendo datos del sensor...")
        data = await sensor.read_sensor()

        if "error" in data:
            print(f"⚠️ Error al leer datos del sensor: {data['error']}")
            return False

        print(f"✅ Datos del sensor: SpO2={data['spo2']}%, Pulso={data['pulse']} BPM")
        sensor.disconnect()
        return True
    except Exception as e:
        print(f"⚠️ Error en prueba de Arduino: {e}")
        return False


async def test_alerts(user_id: int, db: AsyncSession):
    """Prueba el sistema de alertas."""
    print("\n=== PRUEBA DE SISTEMA DE ALERTAS ===")

    try:
        # Simular nivel crítico de oxígeno
        spo2_critical = random.randint(80, 89)
        print(f"Enviando alerta crítica para SpO2={spo2_critical}%")

        result = await send_critical_alert(user_id, spo2_critical, db)
        print(f"✅ Resultado de alerta: {result}")

        return True
    except Exception as e:
        print(f"❌ Error en prueba de alertas: {e}")
        return False


async def test_reminders(user_id: int, db: AsyncSession):
    """Prueba el sistema de recordatorios."""
    print("\n=== PRUEBA DE SISTEMA DE RECORDATORIOS ===")

    try:
        # Programar recordatorio horario
        print("Programando recordatorio horario")
        hourly_result = await schedule_reminder(user_id, "hourly", db)
        print(f"✅ {hourly_result}")

        # Programar recordatorio diario
        print("Programando recordatorio diario")
        daily_result = await schedule_reminder(user_id, "daily", db, time="08:00")
        print(f"✅ {daily_result}")

        # Obtener recordatorios
        reminders = await get_reminders(user_id, db)
        print(f"✅ Recordatorios activos: {len(reminders)}")

        # Cancelar un recordatorio
        if reminders:
            cancel_result = await cancel_reminder(reminders[0].id, db)
            print(
                f"✅ Cancelación de recordatorio: {'Exitosa' if cancel_result else 'Fallida'}"
            )

        return True
    except Exception as e:
        print(f"❌ Error en prueba de recordatorios: {e}")
        return False


async def test_chatbot(user_id: int, db: AsyncSession):
    """Prueba el chatbot."""
    print("\n=== PRUEBA DE CHATBOT ===")

    try:
        # Enviar mensaje simple
        print("Enviando mensaje al chatbot: 'Hola, ¿cómo estás?'")
        chat_request = ChatRequest(user_id=user_id, message="Hola, ¿cómo estás?")
        response = await process_user_message(
            db, chat_request.user_id, chat_request.message
        )

        print(
            f"✅ Respuesta del chatbot ({response['type']}): {response.get('content') or response.get('result')}"
        )

        # Enviar mensaje sobre oxígeno
        print(
            "Enviando mensaje al chatbot: '¿Qué significa un nivel de oxígeno de 92%?'"
        )
        chat_request = ChatRequest(
            user_id=user_id, message="¿Qué significa un nivel de oxígeno de 92%?"
        )
        response = await process_user_message(
            db, chat_request.user_id, chat_request.message
        )

        print(
            f"✅ Respuesta del chatbot ({response['type']}): {response.get('content') or response.get('result')}"
        )

        return True
    except Exception as e:
        print(f"❌ Error en prueba de chatbot: {e}")
        return False


async def test_notifications():
    """Prueba el sistema de notificaciones."""
    print("\n=== PRUEBA DE NOTIFICACIONES ===")
    print("Nota: Esta prueba requiere configuración SMTP y/o SMS válida.")

    try_email = input("¿Probar envío de correo? (s/n): ").lower() == "s"
    try_sms = input("¿Probar envío de SMS? (s/n): ").lower() == "s"

    if not try_email and not try_sms:
        print("Omitiendo pruebas de notificaciones.")
        return True

    try:
        if try_email:
            email = input("Ingresa tu dirección de correo electrónico: ")
            print(f"Enviando correo de prueba a {email}")
            email_result = await send_test_email(email)
            print(
                f"{'✅ Correo enviado exitosamente' if email_result else '❌ Error al enviar correo'}"
            )

        if try_sms:
            phone = input(
                "Ingresa tu número de teléfono (con código de país, ej: +51987654321): "
            )
            print(f"Enviando SMS de prueba a {phone}")
            sms_result = await send_test_sms(phone)
            print(
                f"{'✅ SMS enviado exitosamente' if sms_result else '❌ Error al enviar SMS'}"
            )

        return True
    except Exception as e:
        print(f"❌ Error en prueba de notificaciones: {e}")
        return False


async def run_all_tests():
    """Ejecuta todas las pruebas."""
    print("=== INICIANDO PRUEBAS INTEGRALES DE OXYMONITOR ===")
    print(
        f"Fecha y hora: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )

    # Verificar conexión a la base de datos
    db_ok = await test_database()
    if not db_ok:
        print("❌ Pruebas canceladas debido a error de conexión a la base de datos.")
        return

    async with AsyncSessionLocal() as db:
        # Prueba de autenticación
        user_id = await test_auth(db)
        if not user_id:
            print(
                "⚠️ Prueba de autenticación fallida. Usando usuario anónimo para continuar."
            )
            user_id = await test_anonymous_user(db)
            if not user_id:
                print("❌ No se pudo crear usuario para pruebas. Abortando.")
                return

        # Prueba de mediciones
        await test_measure(user_id, db)

        # Prueba de sensor Arduino
        await test_arduino_sensor()

        # Prueba de alertas
        await test_alerts(user_id, db)

        # Prueba de recordatorios
        await test_reminders(user_id, db)

        # Prueba de chatbot
        await test_chatbot(user_id, db)

    # Prueba de notificaciones
    await test_notifications()

    print("\n=== RESUMEN DE PRUEBAS ===")
    print("Se han ejecutado todas las pruebas programadas.")
    print(
        "Revisa los resultados anteriores para verificar el funcionamiento de cada componente."
    )
    print("=== FIN DE PRUEBAS ===")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
