from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    Text,
    DateTime,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class AdminExport(Base):
    __tablename__ = "admin_exports"

    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    export_type = Column(String, nullable=False)
    file_path = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        CheckConstraint(
            "export_type IN ('mediciones', 'alertas', 'usuarios', 'todo')",
            name="export_type_check",
        ),
    )
