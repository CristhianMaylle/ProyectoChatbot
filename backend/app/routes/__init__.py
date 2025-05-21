from fastapi import APIRouter
from app.routes import auth, users, chat, measures, dashboard, reminders, notifications

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chatbot"])
api_router.include_router(measures.router, prefix="/measures", tags=["Measurements"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["Reminders"])
api_router.include_router(
    notifications.router, prefix="/notifications", tags=["Notifications"]
)


@api_router.get("/health")
async def health_check():
    """Endpoint para verificar que la API está funcionando."""
    return {"status": "ok", "message": "API funcionando correctamente"}
