# app/schemas/__init__.py
from .base_schemas import BaseRequest, BaseResponse
from .token_schemas import Token, TokenData
from .user_schemas import User, UserCreate, UserUpdate, UserInDBBase
from .character_schemas import (
    IdentityBase, IdentityCreate, IdentityUpdate, IdentityInDB,
    CharacterAttributeBase, CharacterAttributeCreate, CharacterAttributeUpdate, CharacterAttributeInDB,
    CharacterBase, CharacterCreate, CharacterUpdate, CharacterInDBBase, CharacterSimple, CharacterDetailed
)
from .game_schemas import (
    GameStateBase, GameStateCreate, GameStateUpdate, GameStateInDB,
    GameSaveBase, GameSaveCreate, GameSaveUpdate, GameSaveInDB,
    GameStartRequest, GameChoiceRequest, StoryChoice, StoryScene,
    GameLoadRequest # ADDED GameLoadRequest here
)

__all__ = [
    "BaseRequest", "BaseResponse",
    "Token", "TokenData",
    "User", "UserCreate", "UserUpdate", "UserInDBBase",
    "IdentityBase", "IdentityCreate", "IdentityUpdate", "IdentityInDB",
    "CharacterAttributeBase", "CharacterAttributeCreate", "CharacterAttributeUpdate", "CharacterAttributeInDB",
    "CharacterBase", "CharacterCreate", "CharacterUpdate", "CharacterInDBBase", "CharacterSimple", "CharacterDetailed",
    "GameStateBase", "GameStateCreate", "GameStateUpdate", "GameStateInDB",
    "GameSaveBase", "GameSaveCreate", "GameSaveUpdate", "GameSaveInDB",
    "GameStartRequest", "GameChoiceRequest", "StoryChoice", "StoryScene",
    "GameLoadRequest", # ADDED GameLoadRequest here
]
