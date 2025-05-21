# backend/app/services/users.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, LoginRequest
import bcrypt
from datetime import datetime, timezone, timedelta
import jwt
from app.config import settings


async def register_user(user_data: UserCreate, db: AsyncSession):
    # Verificar si el email ya existe
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return {"error": "El email ya está registrado"}

    # Hash de la contraseña
    hashed_password = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt())

    # Crear nuevo usuario
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=hashed_password.decode(),
        is_anonymous=False,
        created_at=datetime.now(timezone.utc),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Generar token JWT
    token = generate_token(new_user.id)

    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "token": token,
    }


async def login_user(credentials: LoginRequest, db: AsyncSession):
    # Buscar usuario por email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user:
        return {"error": "Usuario no encontrado"}

    # Verificar contraseña
    if not bcrypt.checkpw(credentials.password.encode(), user.password_hash.encode()):
        return {"error": "Contraseña incorrecta"}

    # Generar token JWT
    token = generate_token(user.id)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_admin": user.is_admin,
        "token": token,
    }


def generate_token(user_id: int) -> str:
    """Genera un token JWT para el usuario."""
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=1),
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


async def get_user_by_id(user_id: int, db: AsyncSession):
    """Obtiene un usuario por su ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_or_create_anonymous_user(db: AsyncSession):
    """Obtiene o crea un usuario anónimo para mediciones sin registro."""
    # Crear un nuevo usuario anónimo
    anon_user = User(
        name="Usuario No Identificado",
        email=None,
        password_hash=None,
        is_anonymous=True,
        created_at=datetime.now(timezone.utc),
    )

    db.add(anon_user)
    await db.commit()
    await db.refresh(anon_user)

    return anon_user
