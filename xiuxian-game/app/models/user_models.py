# app/models/user_models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime # Correct import for datetime
from app.models.base import CustomBase # Use CustomBase

class User(CustomBase):
    __tablename__ = "users" # Explicit tablename is fine, or use generated one

    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    characters = relationship("Character", back_populates="user")
    game_saves = relationship("GameSave", back_populates="user")

    def __repr__(self) -> str:
        return f"<User(username='{self.username}', email='{self.email}')>"
