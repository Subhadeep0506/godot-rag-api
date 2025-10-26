from sqlalchemy import JSON, Column, ForeignKey, String, Integer, DateTime
from sqlalchemy.orm import relationship
import datetime
from api.database.database import Base
from uuid import uuid4


class SessionMessages(Base):
    __tablename__ = "session_messages"

    message_id = Column(
        String, primary_key=True, nullable=False, index=True, default=str(uuid4())
    )
    session_id = Column(
        String,
        ForeignKey("chat_session.session_id", ondelete="CASCADE"),
        nullable=False,
    )
    feedback = Column(String, default=None)
    like = Column(String, default=None)
    stars = Column(Integer, default=0)
    content = Column(JSON, nullable=False)
    sources = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    # Relationship back to ChatSession (many-to-one)
    session = relationship("ChatSession", back_populates="messages")
