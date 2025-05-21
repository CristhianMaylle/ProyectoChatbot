from fastapi import APIRouter, Depends
from app.schemas.user import UserCreate
from app.services.users import register_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()


@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await register_user(user, db)
