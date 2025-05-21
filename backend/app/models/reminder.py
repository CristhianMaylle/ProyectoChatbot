from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    Boolean,
    DateTime,
    Text,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    action = Column(Text, nullable=False)
    frequency = Column(String, nullable=False)
    next_run = Column(DateTime(timezone=True))
    active = Column(Boolean, default=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        CheckConstraint("frequency IN ('hourly', 'daily')", name="frequency_check"),
    )

    user = relationship("User", back_populates="reminders")
