# Conexión a postgreSQL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
from sqlalchemy import text

# Base para modelos
Base = declarative_base()

# Motor de conexión
engine = create_async_engine(settings.DATABASE_URL, echo=True)
# Sesion asincrona
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Dependency para inyección
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Dependencia para pruebas
async def test_connection():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            print("✅ Conexión exitosa a PostgreSQL")
    except Exception as e:
        print("❌ Error en la conexión:", e)
