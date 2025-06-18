# app/schemas/game_schemas.py
from pydantic import BaseModel
from datetime import datetime # Keep if used by other schemas like GameStateInDB's created_at
from typing import Optional, List, Dict, Any

# --- StoryChoice schema (remains the same) ---
class StoryChoice(BaseModel):
    id: str
    text: str

# --- StoryScene schema (UPDATED) ---
class StoryScene(BaseModel):
    scene_id: Optional[str] = None
    plot: str  # Changed from 'description' to 'plot' for clarity with new requirements
    choices: List[StoryChoice]
    duration_days: Optional[int] = None # ADDED: Suggested duration from RAG
    # game_state: Optional['GameStateInDB'] = None # This was in a previous version, removing if not explicitly needed by current task

# --- GameStateBase schema (UPDATED) ---
class GameStateBase(BaseModel):
    current_scene_id: Optional[str] = None
    story_history: List[Dict[str, Any]] = []
    game_data: Dict[str, Any] = {}
    current_date: Optional[str] = None # ADDED: e.g., "Day 1"

# --- GameStateCreate schema (Illustrative - ensure it exists and inherits from GameStateBase if needed) ---
class GameStateCreate(GameStateBase):
    character_id: int
    # current_date will be initialized by CRUD, not directly by API client on create

# --- GameStateUpdate schema (Illustrative - ensure it exists if needed for partial updates) ---
class GameStateUpdate(BaseModel):
    current_scene_id: Optional[str] = None
    story_history: Optional[List[Dict[str, Any]]] = None
    game_data: Optional[Dict[str, Any]] = None
    current_date: Optional[str] = None # Allow date update if necessary, though usually by game logic

# --- GameStateInDB schema (UPDATED) ---
class GameStateInDB(GameStateBase): # Inherits current_date from GameStateBase
    id: int
    character_id: int
    created_at: datetime # Assuming this was already here
    updated_at: datetime # Assuming this was already here
    class Config:
        from_attributes = True

# --- Other game-related schemas (GameSaveBase, GameSaveCreate, GameSaveInDB, GameStartRequest, GameChoiceRequest, GameLoadRequest) ---
# These generally remain unchanged by this specific subtask, but ensure they are present as per previous steps.
class GameSaveBase(BaseModel):
    save_name: str
    character_id: int
    save_slot: Optional[int] = None

class GameSaveCreate(GameSaveBase):
    pass
    # user_id and game_state_id will be derived in CRUD/API layer typically

class GameSaveUpdate(BaseModel): # Added from previous step, ensure it's here
    save_name: Optional[str] = None
    save_slot: Optional[int] = None

class GameSaveInDB(GameSaveBase):
    id: int
    user_id: int
    game_state_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class GameStartRequest(BaseModel):
    character_id: int

class GameChoiceRequest(BaseModel):
    character_id: int
    choice_id: str

class GameLoadRequest(BaseModel):
    save_id: int
