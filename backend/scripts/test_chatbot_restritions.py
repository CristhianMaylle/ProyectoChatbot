# scripts/test_chatbot_restrictions.py
import sys
import os
import asyncio

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.services.chatbot import process_user_message
from app.services.users import get_or_create_anonymous_user


async def test_chatbot_restrictions():
    """Prueba las restricciones temáticas del chatbot."""
    print("=== PRUEBA DE RESTRICCIONES TEMÁTICAS DEL CHATBOT ===")

    async with AsyncSessionLocal() as db:
        # Crear usuario anónimo para la sesión
        user = await get_or_create_anonymous_user(db)
        user_id = user.id

        print(f"Usuario temporal creado con ID: {user_id}")

        # Lista de preguntas para probar
        test_questions = [
            # Preguntas relacionadas (deberían ser respondidas)
            "¿Qué significa un nivel de oxígeno de 92%?",
            "¿Es normal tener un pulso de 110 latidos por minuto?",
            "¿Qué debo hacer si mi oxígeno está por debajo de 90%?",
            "¿Cómo afecta la altitud a la saturación de oxígeno?",
            "¿Qué factores pueden causar un aumento en la frecuencia cardíaca?",
            # Preguntas no relacionadas (deberían ser rechazadas)
            "¿Cuál es la capital de Francia?",
            "¿Me puedes ayudar a resolver esta ecuación: 2x + 5 = 15?",
            "¿Cuáles son los mejores lugares para visitar en vacaciones?",
            "¿Puedes escribirme un poema sobre el amor?",
            "¿Cómo puedo preparar una lasaña?",
        ]

        # Probar cada pregunta
        for i, question in enumerate(test_questions):
            print(f"\n--- Pregunta {i+1}: {question} ---")

            response = await process_user_message(db, user_id, question)

            if response["type"] == "text":
                print(f"Respuesta: {response['content']}")
            elif response["type"] == "function":
                print(
                    f"Respuesta (función {response['function_name']}): {response['result']}"
                )
            else:
                print(f"Error: {response.get('error', 'Error desconocido')}")

            # Pequeña pausa entre preguntas
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(test_chatbot_restrictions())
