from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from .base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, unique=True)  # Telegram user ID
    name = Column(String, nullable=False)
    date = Column(DateTime, nullable=False, default=func.now())

    def __init__(self, user_id: int, name: str, date: Optional[datetime] = None):
        self.id = user_id
        self.name = name
        self.date = date or datetime.utcnow()
    
    def __repr__(self):
        try:
            # Access attributes directly from the instance's dict to avoid lazy loading
            id_val = self.__dict__.get('id', 'N/A')
            name_val = self.__dict__.get('name', 'N/A')
            date_val = self.__dict__.get('date', 'N/A')
            return f"<User(id={id_val}, name='{name_val}', date={date_val})>"
        except:
            return f"<User(detached instance)>"

