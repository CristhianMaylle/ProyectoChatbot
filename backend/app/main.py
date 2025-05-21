# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import api_router

app = FastAPI(
    title="Oxymonitor Backend",
    description="API para monitoreo de oxígeno, alertas, chatbot e historial",
    version="1.0.0",
)

# Configura CORS (ajusta origins en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://0.0.0.0:8080"],  # Puedes restringir en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(api_router, prefix="/api")
