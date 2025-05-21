# Configuracion general
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Carga el .env desde el directorio backend
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str

    # Seguridad
    SECRET_KEY: str

    # Configuración SMTP para correos
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_SENDER: str
    SMTP_USE_TLS: bool  # Cambiar a False si se usa SSL

    # Configuración SMS
    SMS_PROVIDER: str  # Opciones: "twilio", "messagebird"

    # Twilio (si se usa como proveedor de SMS)
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str

    # MessageBird (si se usa como proveedor de SMS)
    MESSAGEBIRD_ACCESS_KEY: str
    MESSAGEBIRD_ORIGINATOR: str

    # OpenAI
    OPENAI_API_KEY: str


class Config:
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")


settings = Settings()
