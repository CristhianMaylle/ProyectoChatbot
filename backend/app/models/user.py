from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=True)  # Permitimos NULL para usuarios no identificados
    email = Column(
        String, unique=True, nullable=True
    )  # Permitimos NULL para usuarios no identificados
    password_hash = Column(
        String, nullable=True
    )  # Permitimos NULL para usuarios no identificados
    phone = Column(String, nullable=True)
    is_anonymous = Column(Boolean, default=False)  # Nuevo campo para usuarios anónimos
    is_admin = Column(Boolean, default=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    measurements = relationship("Measurement", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")
    alerts = relationship("Alert", back_populates="user")
    chat_logs = relationship("ChatLog", back_populates="user")
    notification = relationship(
        "NotificationSetting", back_populates="user", uselist=False
    )
