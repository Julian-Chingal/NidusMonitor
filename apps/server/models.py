from sqlalchemy import Column, Integer, String, Text, DateTime, func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BabyEvent(Base):
    __tablename__ = "baby_events"

    id = Column(Integer, primary_key=True, index=True)
    baby_id = Column(Integer, nullable=False, default=1)
    event_type = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
