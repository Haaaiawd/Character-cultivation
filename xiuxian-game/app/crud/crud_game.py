# app/crud/crud_game.py
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import re # Import re for parsing "Day X"

from app.models.game_models import GameState, GameSave
# Note: Schemas like GameStateCreate are for API input, not direct DB creation here.
# CRUD functions typically take model instances or primitive types for creation/update.

def create_game_state(db: Session, character_id: int, initial_scene_id: Optional[str] = "start", initial_history: Optional[List[Dict[str,Any]]] = None) -> GameState:
    """Creates a new game state for a character, initializing current_date."""
    db_game_state = GameState(
        character_id=character_id,
        current_scene_id=initial_scene_id,
        story_history=initial_history if initial_history is not None else [],
        game_data={},
        current_date="Day 1"  # ADDED: Initialize current_date
    )
    db.add(db_game_state)
    db.commit()
    db.refresh(db_game_state)
    return db_game_state

def get_game_state(db: Session, game_state_id: int) -> Optional[GameState]:
    """Retrieves a specific game state by its ID."""
    return db.query(GameState).filter(GameState.id == game_state_id).first()

def get_active_game_state_for_character(db: Session, character_id: int) -> Optional[GameState]:
    """
    Retrieves the most recently updated game state for a character,
    considered the 'active' one for MVP.
    """
    return db.query(GameState).filter(GameState.character_id == character_id).order_by(GameState.updated_at.desc()).first()

def update_game_state(
    db: Session,
    game_state: GameState,
    story_event: Dict[str, Any],
    new_scene_id: Optional[str],
    game_data_updates: Optional[Dict[str, Any]] = None,
    advance_days: Optional[int] = None  # ADDED parameter
) -> GameState:
    """
    Updates a game state: appends to story history, changes current scene,
    updates game_data, and advances in-game date if specified.
    """
    current_history = game_state.story_history
    if not isinstance(current_history, list):
        current_history = []
    game_state.story_history = current_history + [story_event]

    if new_scene_id is not None:
        game_state.current_scene_id = new_scene_id

    current_game_data = game_state.game_data
    if not isinstance(current_game_data, dict):
        current_game_data = {}
    if game_data_updates:
        game_state.game_data = {**current_game_data, **game_data_updates}

    # ADDED: Logic to advance current_date
    if advance_days is not None and advance_days > 0:
        current_date_str = game_state.current_date if game_state.current_date else "Day 0" # Default if None
        day_match = re.match(r"Day (\d+)", current_date_str)
        if day_match:
            try:
                current_day_num = int(day_match.group(1))
                new_day_num = current_day_num + advance_days
                game_state.current_date = f"Day {new_day_num}"
            except ValueError:
                print(f"Warning: Could not parse day number from current_date '{current_date_str}'. Date not advanced.")
                # Optionally, set to a default or log error more formally
        else:
            # If current_date is not in "Day X" format, and we need to advance,
            # we could try to initialize it or log a warning.
            # For simplicity, if format is unexpected, we'll start from advance_days.
            print(f"Warning: current_date '{current_date_str}' not in 'Day X' format. Advancing from Day 0 implicitly.")
            game_state.current_date = f"Day {advance_days}"


    db.add(game_state)
    db.commit()
    db.refresh(game_state)
    return game_state

def create_game_save(
    db: Session,
    user_id: int,
    character_id: int,
    game_state_id: int,
    save_name: str,
    save_slot: Optional[int] = None
) -> GameSave:
    """Creates a new game save entry."""
    db_game_save = GameSave(
        user_id=user_id,
        character_id=character_id,
        game_state_id=game_state_id,
        save_name=save_name,
        save_slot=save_slot
    )
    db.add(db_game_save)
    db.commit()
    db.refresh(db_game_save)
    return db_game_save

def get_game_save(db: Session, game_save_id: int) -> Optional[GameSave]:
    """Retrieves a specific game save by its ID."""
    return db.query(GameSave).filter(GameSave.id == game_save_id).first()

def get_game_saves_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[GameSave]:
    """Retrieves a list of game saves for a specific user, ordered by creation date."""
    return db.query(GameSave).filter(GameSave.user_id == user_id).order_by(GameSave.created_at.desc()).offset(skip).limit(limit).all()

# Note: Delete operations for GameState or GameSave can be added later if required.
# For MVP, they are not explicitly listed in the API endpoints.
