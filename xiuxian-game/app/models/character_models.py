# app/models/character_models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime # Correct import for datetime
from app.models.base import CustomBase # Use CustomBase
# Ensure User is imported if type hinting or direct use, though relationship strings handle resolution
# from app.models.user_models import User

# Forward declaration for relationships if models are in the same file or circular
# Not strictly necessary here as structure is linear, but good practice.
# Character = None
# CharacterAttribute = None
# Identity = None

class Identity(CustomBase):
    __tablename__ = "identities"

    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    starting_benefits = Column(JSON) # As per MVP doc

    characters = relationship("Character", back_populates="identity") # Relationship to Character

    def __repr__(self) -> str:
        return f"<Identity(name='{self.name}')>"

class Character(CustomBase):
    __tablename__ = "characters"

    name = Column(String, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    identity_id = Column(Integer, ForeignKey("identities.id"), nullable=True) # Allow nullable if character can be created without identity initially
    level = Column(Integer, default=1)
    cultivation_stage = Column(String, default="炼气期一层")
    experience = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="characters")
    identity = relationship("Identity", back_populates="characters") # Corrected back_populates

    # Corrected relationship for CharacterAttribute: one-to-one
    attributes = relationship("CharacterAttribute", back_populates="character", uselist=False, cascade="all, delete-orphan")
    game_states = relationship("GameState", back_populates="character", cascade="all, delete-orphan")
    game_saves = relationship("GameSave", back_populates="character", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Character(name='{self.name}', user_id={self.user_id})>"

class CharacterAttribute(CustomBase):
    __tablename__ = "character_attributes"

    # character_id is primary key and foreign key for one-to-one
    character_id = Column(Integer, ForeignKey("characters.id"), primary_key=True)
    strength = Column(Integer, default=10)
    agility = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    constitution = Column(Integer, default=10)
    perception = Column(Integer, default=10)
    luck = Column(Integer, default=10)

    character = relationship("Character", back_populates="attributes")

    def __repr__(self) -> str:
        return f"<CharacterAttribute(character_id={self.character_id})>"
