from enum import Enum
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from datetime import datetime


class ServerStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class UserServer(Base):
    __tablename__ = "user_servers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    server_name = Column(String, nullable=False)
    server_url = Column(String, nullable=False)
    interval_seconds = Column(Integer, default=60)
    status = Column(String, default=ServerStatus.ACTIVE.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ServerAnalytics(Base):
    __tablename__ = "server_analytics"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("user_servers.id", ondelete="CASCADE"))
    status_code = Column(Integer)
    latency_ms = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

