from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    AnonymousChatRequest,
    InitiateChatResponse,
)
from app.services.chatbot import process_user_message
from app.services.users import get_or_create_anonymous_user, get_user_by_id
from app.services.mcp.context import is_new_session

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await process_user_message(db, request.user_id, request.message)
    except Exception as e:
        print(f"[Error /api/chat]: {e}")
        return {
            "type": "error",
            "content": str(e),
        }


@router.post("/anonymous", response_model=ChatResponse)
async def anonymous_chat(
    request: AnonymousChatRequest, db: AsyncSession = Depends(get_db)
):
    """Endpoint para chatear sin estar registrado."""
    # Crear un usuario anónimo
    anon_user = await get_or_create_anonymous_user(db)

    # Procesar el mensaje
    return await process_user_message(db, anon_user.id, request.message)


@router.get("/initiate/{user_id}", response_model=InitiateChatResponse)
async def initiate_chat(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Endpoint para iniciar una sesión de chat.
    Devuelve información sobre el usuario y un mensaje de bienvenida.
    """
    try:
        # Verificar si el usuario existe
        user = await get_user_by_id(user_id, db)

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Verificar si es una nueva sesión
        new_session = await is_new_session(db, user_id)

        # Generar mensaje de bienvenida
        if new_session:
            # Procesar un mensaje vacío para generar el saludo
            welcome_response = await process_user_message(db, user_id, "Hola")
            welcome_message = (
                welcome_response.get("content")
                or welcome_response.get("result")
                or "¡Bienvenido!"
            )
        else:
            welcome_message = "Continuando conversación anterior."

        return {
            "user_id": user_id,
            "user_name": user.name,
            "is_anonymous": user.is_anonymous,
            "welcome_message": welcome_message,
            "new_session": new_session,
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/initiate-anonymous", response_model=InitiateChatResponse)
async def initiate_anonymous_chat(db: AsyncSession = Depends(get_db)):
    """
    Endpoint para iniciar una sesión de chat anónima.
    Crea un usuario anónimo y devuelve un mensaje de bienvenida.
    """
    try:
        # Crear un usuario anónimo
        anon_user = await get_or_create_anonymous_user(db)

        # Procesar un mensaje vacío para generar el saludo
        welcome_response = await process_user_message(db, anon_user.id, "Hola")
        welcome_message = (
            welcome_response.get("content")
            or welcome_response.get("result")
            or "¡Bienvenido!"
        )

        return {
            "user_id": anon_user.id,
            "user_name": None,
            "is_anonymous": True,
            "welcome_message": welcome_message,
            "new_session": True,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
