# app/models/game_models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime # Correct import for datetime
from app.models.base import CustomBase
# Ensure User and Character are imported if type hinting or direct use
# from app.models.user_models import User
# from app.models.character_models import Character

class GameState(CustomBase): # Ensure GameState is defined before GameSave
    __tablename__ = "game_states"
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    current_scene_id = Column(String, nullable=True)
    story_history = Column(JSON, default=list)
    game_data = Column(JSON, default=dict)

    current_date = Column(String, nullable=True) # ADDED: For in-game date, e.g., "Day 1"

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    character = relationship("Character", back_populates="game_states")

    def __repr__(self) -> str:
        # Assuming self.id is available from CustomBase after instance creation and DB flush/commit
        return f"<GameState(id={getattr(self, 'id', None)}, char_id={self.character_id}, date='{self.current_date}')>"

class GameSave(CustomBase):
    __tablename__ = "game_saves"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    game_state_id = Column(Integer, ForeignKey("game_states.id"), nullable=False) # MODIFIED/ADDED
    save_name = Column(String, nullable=False)
    save_slot = Column(Integer, nullable=True) # Nullable if not always used
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="game_saves")
    character = relationship("Character", back_populates="game_saves") # MODIFIED/ADDED back_populates
    game_state = relationship("GameState") # MODIFIED/ADDED

    def __repr__(self) -> str:
        return f"<GameSave(name='{self.save_name}', gs_id={self.game_state_id})>"
