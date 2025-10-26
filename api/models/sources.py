from sqlalchemy import Column, String, DateTime, JSON, Integer
import datetime

from api.database.database import Base


class Source(Base):
    __tablename__ = "source"

    source_id = Column(String, primary_key=True, nullable=False, index=True)
    title = Column(String)
    tags = Column(JSON)
    sources = Column(JSON)
    categories = Column(JSON)
    sub_categories = Column(JSON)
    document_count = Column(Integer)
    time_added = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    time_updated = Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )
