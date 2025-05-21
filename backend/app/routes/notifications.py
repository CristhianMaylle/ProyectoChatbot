# app/routes/notifications.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.utils.email_utils import send_test_email
from app.utils.sms_utils import send_test_sms
from pydantic import BaseModel, EmailStr

router = APIRouter()


class EmailTestRequest(BaseModel):
    email: EmailStr


class SMSTestRequest(BaseModel):
    phone: str  # Formato E.164, ej: +51987654321


@router.post("/test-email")
async def test_email(request: EmailTestRequest):
    """Endpoint para probar el envío de correo electrónico."""
    result = await send_test_email(request.email)

    if result:
        return {"status": "success", "message": "Correo enviado exitosamente"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Error al enviar el correo. Verifica la configuración SMTP.",
        )


@router.post("/test-sms")
async def test_sms(request: SMSTestRequest):
    """Endpoint para probar el envío de SMS."""
    result = await send_test_sms(request.phone)

    if result:
        return {"status": "success", "message": "SMS enviado exitosamente"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Error al enviar el SMS. Verifica la configuración del proveedor.",
        )
