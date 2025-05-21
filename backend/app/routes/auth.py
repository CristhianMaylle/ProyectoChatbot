from fastapi import APIRouter, Depends
from app.schemas.user import LoginRequest
from app.services.users import login_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()


@router.post("/login")
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await login_user(credentials, db)
