# backend/app/services/chatbot.py

from app.services.mcp.model import call_gpt_with_mcp
from app.services.mcp.context import load_chat_context, store_message, is_new_session
from app.models import ChatLog, User
from datetime import datetime
from app.services.users import get_or_create_anonymous_user, get_user_by_id
from sqlalchemy import select


# Ejecuta el flujo de conversación completa
async def process_user_message(db, user_id: int, user_input: str) -> dict:
    # Si user_id es None, crear un usuario anónimo
    if user_id is None:
        anon_user = await get_or_create_anonymous_user(db)
        user_id = anon_user.id
        user_name = None
        is_anonymous = True
    else:
        # Obtener información del usuario
        user = await get_user_by_id(user_id, db)
        user_name = user.name if user else None
        is_anonymous = user.is_anonymous if user else True

    # Verificar si es una nueva sesión para generar saludo
    new_session = await is_new_session(db, user_id)

    # Cargar historial de mensajes
    context = await load_chat_context(db, user_id)

    # Si es una nueva sesión, añadir instrucción de saludo al sistema
    system_message = None
    if new_session:
        if is_anonymous:
            system_message = (
                "El usuario es anónimo. Salúdalo cordialmente sin mencionar su nombre."
            )
        else:
            system_message = f"El usuario se llama {user_name}. Salúdalo cordialmente usando su nombre."

    # Agregar mensaje actual
    context.append({"role": "user", "content": user_input})

    # Llamar a GPT con las funciones definidas (MCP)
    result = await call_gpt_with_mcp(context, db, system_message, user_id)

    # Guardar mensaje del usuario
    await store_message(db, user_id, "user", user_input)

    if result["response_type"] == "text":
        # Mensaje directo generado por GPT
        content = result["content"]
        await store_message(db, user_id, "assistant", content)
        return {"type": "text", "content": content}

    elif result["response_type"] == "function_result":
        # Resultado de una función real llamada por GPT
        output = result["result"]
        await store_message(
            db, user_id, "assistant", f"[Función: {result['function_name']}] {output}"
        )
        return {
            "type": "function",
            "function_name": result["function_name"],
            "result": output,
        }

    else:
        return {"type": "error", "error": result["error"]}
