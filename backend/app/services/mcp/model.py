# backend/app/services/mcp/model.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from app.services.mcp.protocol import get_function_definitions, get_system_instructions
from app.services.function_handler import handle_function_call

load_dotenv()

# Configura el cliente de OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Llama al modelo GPT con historial y funciones disponibles
async def call_gpt_with_mcp(
    messages: list[dict], db, system_message: str = None, user_id_context=None
) -> dict:
    try:
        # Preparar mensajes para la API
        api_messages = []

        # Obtener instrucciones base del sistema
        base_instructions = get_system_instructions()

        # Combinar instrucciones base con mensaje específico si existe
        if system_message:
            system_content = f"{base_instructions}\n\n{system_message}"
        else:
            system_content = base_instructions

        # Añadir mensaje del sistema
        api_messages.append({"role": "system", "content": system_content})

        # Añadir el resto de mensajes del historial
        api_messages.extend(messages)

        # Llamar a la API de OpenAI
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # También puedes usar gpt-3.5-turbo si deseas
            messages=api_messages,
            functions=get_function_definitions(),
            function_call="auto",
        )
        message = response.choices[0].message

        # Verifica si GPT desea llamar una función
        if message.function_call:
            function_name = message.function_call.name
            arguments_json = message.function_call.arguments

            # Convierte los argumentos en dict
            try:
                arguments = json.loads(arguments_json)
            except json.JSONDecodeError:
                return {
                    "response_type": "error",
                    "error": "Error al analizar los argumentos de la función.",
                }
            # Asegura que user_id esté presentes
            # Fuerza que user_id esté presente si tienes el contexto
            if user_id_context is not None:
                arguments["user_id"] = user_id_context

            print(
                f"[DEBUG] Llamando a función: {function_name} con argumentos: {arguments}"
            )

            # Ejecuta la función real en backend
            function_result = await handle_function_call(
                function_name, arguments, db, user_id_context
            )

            return {
                "response_type": "function_result",
                "function_name": function_name,
                "result": function_result,
            }

        else:
            # GPT responde con texto directamente
            return {"response_type": "text", "content": message.content}

    except Exception as e:
        return {"response_type": "error", "error": str(e)}
