from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    String,
    Boolean,
    DateTime,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    measurement_id = Column(Integer, ForeignKey("measurements.id", ondelete="CASCADE"))
    message = Column(Text, nullable=False)
    alert_type = Column(String, nullable=False)
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint(
            "alert_type IN ('correo', 'sms', 'interna')", name="alert_type_check"
        ),
    )

    user = relationship("User", back_populates="alerts")
    measurement = relationship("Measurement", back_populates="alerts")
