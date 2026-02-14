from enum import Enum
from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
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
    status = Column(String, default=ServerStatus.ACTIVE.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
