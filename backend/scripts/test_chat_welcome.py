# scripts/test_chat_welcome.py
import sys
import os
import asyncio

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.services.chatbot import process_user_message
from app.services.users import get_or_create_anonymous_user, register_user
from app.schemas.user import UserCreate


async def test_welcome_messages():
    """Prueba los mensajes de bienvenida del chatbot."""
    print("=== PRUEBA DE MENSAJES DE BIENVENIDA DEL CHATBOT ===")

    async with AsyncSessionLocal() as db:
        # 1. Probar con usuario anónimo
        print("\n--- Prueba con usuario anónimo ---")
        anon_user = await get_or_create_anonymous_user(db)
        print(f"Usuario anónimo creado con ID: {anon_user.id}")

        print("Enviando primer mensaje...")
        anon_response = await process_user_message(db, anon_user.id, "Hola")
        print(
            f"Respuesta para usuario anónimo: {anon_response.get('content') or anon_response.get('result')}"
        )

        # 2. Probar con usuario registrado
        print("\n--- Prueba con usuario registrado ---")
        user_data = UserCreate(
            name="María García",
            email="maria_test@example.com",
            password="password123",
            phone="+519876543210",
        )

        # Intentar registrar (puede fallar si el usuario ya existe)
        try:
            reg_result = await register_user(user_data, db)
            user_id = reg_result["id"]
            print(f"Usuario registrado con ID: {user_id}")
        except Exception as e:
            print(f"Error al registrar usuario (probablemente ya existe): {e}")
            # Buscar el usuario por email
            from sqlalchemy import select
            from app.models.user import User

            result = await db.execute(select(User).where(User.email == user_data.email))
            user = result.scalar_one_or_none()
            if user:
                user_id = user.id
                print(f"Usuario encontrado con ID: {user_id}")
            else:
                print("No se pudo encontrar o crear el usuario de prueba.")
                return

        print("Enviando primer mensaje...")
        reg_response = await process_user_message(db, user_id, "Hola")
        print(
            f"Respuesta para usuario registrado: {reg_response.get('content') or reg_response.get('result')}"
        )

        # 3. Probar continuación de sesión
        print("\n--- Prueba de continuación de sesión ---")
        print("Enviando segundo mensaje al mismo usuario...")
        cont_response = await process_user_message(db, user_id, "¿Cómo estás?")
        print(
            f"Respuesta para continuación: {cont_response.get('content') or cont_response.get('result')}"
        )


if __name__ == "__main__":
    asyncio.run(test_welcome_messages())
