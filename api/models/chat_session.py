from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import datetime

from api.database.database import Base


class ChatSession(Base):
    __tablename__ = "chat_session"

    session_id = Column(String, primary_key=True, nullable=False, index=True)
    user_id = Column(String, nullable=False)
    title = Column(String)
    time_created = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    time_updated = Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    messages = relationship(
        "SessionMessages",
        back_populates="session",
        cascade="all, delete-orphan",
    )
