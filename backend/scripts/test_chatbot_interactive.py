# scripts/test_chatbot_interactive.py
import sys
import os
import asyncio

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.services.chatbot import process_user_message
from app.services.users import get_or_create_anonymous_user


async def interactive_chat():
    """Inicia una sesión de chat interactiva con el chatbot."""
    print("=== CHATBOT OXYMONITOR ===")
    print(
        "Este chatbot está especializado en temas de oxígeno en sangre y pulso cardíaco."
    )
    print("Escribe 'salir' para terminar la conversación.")

    async with AsyncSessionLocal() as db:
        # Crear usuario anónimo para la sesión
        user = await get_or_create_anonymous_user(db)
        user_id = user.id

        print(f"Usuario temporal creado con ID: {user_id}")
        print("Puedes comenzar a chatear:")

        # Enviar un saludo inicial
        initial_response = await process_user_message(db, user_id, "Hola")
        print(
            f"\nChatbot: {initial_response.get('content') or initial_response.get('result')}"
        )

        while True:
            # Obtener mensaje del usuario
            user_input = input("\nTú: ")

            if user_input.lower() in ["salir", "exit", "quit"]:
                print("Finalizando sesión de chat.")
                break

            # Procesar mensaje
            response = await process_user_message(db, user_id, user_input)

            # Mostrar respuesta
            if response["type"] == "text":
                print(f"\nChatbot: {response['content']}")
            elif response["type"] == "function":
                print(f"\nChatbot [{response['function_name']}]: {response['result']}")
            else:
                print(
                    f"\nChatbot [Error]: {response.get('error', 'Error desconocido')}"
                )


if __name__ == "__main__":
    asyncio.run(interactive_chat())
