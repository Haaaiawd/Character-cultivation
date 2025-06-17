# app/models/__init__.py
from .base import CustomBase, Base  # Expose CustomBase and original Base if needed
from .user_models import User
from .character_models import Character, CharacterAttribute, Identity
from .game_models import GameState, GameSave

# You can also define __all__ here if you want to control `from app.models import *`
__all__ = [
    "CustomBase",
    "Base",
    "User",
    "Character",
    "CharacterAttribute",
    "Identity",
    "GameState",
    "GameSave",
]
