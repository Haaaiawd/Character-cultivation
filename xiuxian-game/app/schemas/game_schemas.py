# app/schemas/game_schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any # For JSON and list fields
# from .character_schemas import CharacterSimple # Example if needed

# --- GameState Schemas ---
# Assuming StoryChoice might be defined here or imported if used by GameState/StoryScene directly
class StoryChoice(BaseModel):
    id: str
    text: str

class StoryScene(BaseModel):
    scene_id: Optional[str] = None # ADDED
    description: str
    choices: List[StoryChoice]
    game_state: Optional['GameStateInDB'] = None # Optionally return full state, forward ref if GameStateInDB defined later

class GameStateBase(BaseModel):
    current_scene_id: Optional[str] = None
    story_history: List[Dict[str, Any]] = []
    game_data: Dict[str, Any] = {}

class GameStateCreate(GameStateBase): # Added for completeness, though not explicitly in this step's changes
    character_id: int

class GameStateUpdate(BaseModel): # Added for completeness
    current_scene_id: Optional[str] = None
    story_history: Optional[List[Dict[str, Any]]] = None
    game_data: Optional[Dict[str, Any]] = None

class GameStateInDB(GameStateBase):
    id: int
    character_id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# --- GameSave Schemas ---
class GameSaveBase(BaseModel):
    save_name: str
    character_id: int # ENSURE PRESENT
    save_slot: Optional[int] = None

class GameSaveCreate(GameSaveBase):
    # user_id and game_state_id will be derived in CRUD/API layer typically
    pass

class GameSaveUpdate(BaseModel): # Added for completeness
    save_name: Optional[str] = None
    save_slot: Optional[int] = None

class GameSaveInDB(GameSaveBase):
    id: int
    user_id: int
    game_state_id: int # ADDED
    created_at: datetime
    # character: Optional[CharacterSimple] = None # Example for nesting
    # game_state: Optional[GameStateInDB] = None # Example for nesting
    class Config:
        from_attributes = True

# --- Schemas for Game API ---
class GameStartRequest(BaseModel):
    character_id: int

class GameChoiceRequest(BaseModel):
    character_id: int # ADDED
    choice_id: str
    # choice_data: Optional[Dict[str, Any]] = None # As per original, but keeping it simple for now

class GameLoadRequest(BaseModel): # ADDED
    save_id: int
