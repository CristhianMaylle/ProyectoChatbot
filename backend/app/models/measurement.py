from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    String,
    Text,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    spo2 = Column(Integer, nullable=False)
    pulse = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    measured_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('Normal', 'Precaución', 'Crítico')", name="status_check"
        ),
    )

    user = relationship("User", back_populates="measurements")
    alerts = relationship("Alert", back_populates="measurement")
