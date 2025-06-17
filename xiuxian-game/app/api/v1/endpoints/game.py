# app/api/v1/endpoints/game.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app import schemas # Root import for schemas
from app import crud    # Root import for crud
from app.api import deps # For dependencies
from app.db.session import get_db
from app.models.user_models import User as UserModel
# from app.models.character_models import Character as CharacterModel # For type hints if needed directly
from app.core.rag_system import RAGSystem
from app.core.plugin_system import PluginManager

router = APIRouter()

@router.post("/start", response_model=schemas.BaseResponse[schemas.StoryScene])
def start_game(
    *,
    db: Session = Depends(get_db),
    game_start_request: schemas.GameStartRequest,
    current_user: UserModel = Depends(deps.get_current_active_user),
    rag_sys: RAGSystem = Depends(deps.get_rag_system),
    plugin_mgr: PluginManager = Depends(deps.get_plugin_manager)
):
    """Starts a new game for a character or resumes if an active game state exists (MVP: creates new)."""
    character = crud.crud_character.get_character(db, character_id=game_start_request.character_id)
    if not character or character.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found or not owned by user")

    # For MVP, starting a game always creates a new game state.
    game_state = crud.crud_game.create_game_state(db, character_id=character.id)

    # Prepare data for 'game_started' event
    char_data_for_event = schemas.CharacterDetailed.model_validate(character).model_dump()
    gs_data_for_event = schemas.GameStateInDB.model_validate(game_state).model_dump()

    event_data = {
        "character": char_data_for_event,
        "game_state": gs_data_for_event,
        "messages": []
    }
    event_data_after_plugins = plugin_mgr.emit_event("game_started", event_data)

    char_dict_for_rag = event_data_after_plugins.get("character", char_data_for_event)
    gs_dict_for_rag = event_data_after_plugins.get("game_state", gs_data_for_event)

    story_scene = rag_sys.generate_story(
        game_state=gs_dict_for_rag,
        character=char_dict_for_rag
    )

    current_story_event = {
        "scene_id": story_scene.scene_id,
        "scene_description": story_scene.description,
        "choices_presented": [c.model_dump() for c in story_scene.choices],
        "messages": event_data_after_plugins.get("messages", [])
    }
    crud.crud_game.update_game_state(db, game_state=game_state,
                                   story_event=current_story_event,
                                   new_scene_id=story_scene.scene_id)

    return schemas.BaseResponse[schemas.StoryScene](
        data=story_scene,
        message="Game started. " + " ".join(event_data_after_plugins.get("messages", []))
    )

@router.post("/choice", response_model=schemas.BaseResponse[schemas.StoryScene])
def make_choice(
    *,
    db: Session = Depends(get_db),
    choice_request: schemas.GameChoiceRequest,
    current_user: UserModel = Depends(deps.get_current_active_user),
    rag_sys: RAGSystem = Depends(deps.get_rag_system),
    plugin_mgr: PluginManager = Depends(deps.get_plugin_manager)
):
    """Processes a player's choice and returns the next game scene."""
    character = crud.crud_character.get_character(db, character_id=choice_request.character_id)
    if not character or character.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found or not owned by user")

    game_state = crud.crud_game.get_active_game_state_for_character(db, character_id=character.id)
    if not game_state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active game state not found for this character.")

    made_choice_obj = {"id": choice_request.choice_id, "text": f"Choice text for {choice_request.choice_id} (not found in history)"}
    if game_state.story_history and isinstance(game_state.story_history, list) and len(game_state.story_history) > 0:
        last_event = game_state.story_history[-1]
        if isinstance(last_event, dict) and "choices_presented" in last_event and isinstance(last_event["choices_presented"], list):
            found_choice = next((c for c in last_event["choices_presented"] if isinstance(c, dict) and c.get("id") == choice_request.choice_id), None)
            if found_choice:
                made_choice_obj = found_choice
            else:
                print(f"Warning: Choice ID '{choice_request.choice_id}' not found in previous scene's choices for character {character.id}.")
        else:
            print(f"Warning: Malformed last event or 'choices_presented' in history for character {character.id}.")
    else:
        print(f"Warning: Empty story history for character {character.id}, cannot verify choice_id '{choice_request.choice_id}'.")

    char_data_for_event = schemas.CharacterDetailed.model_validate(character).model_dump()
    gs_data_for_event = schemas.GameStateInDB.model_validate(game_state).model_dump()

    event_data = {
        "character": char_data_for_event,
        "game_state": gs_data_for_event,
        "choice": made_choice_obj,
        "messages": []
    }
    event_data_after_plugins = plugin_mgr.emit_event("choice_made", event_data)

    char_dict_for_rag = event_data_after_plugins.get("character", char_data_for_event)
    gs_dict_for_rag = event_data_after_plugins.get("game_state", gs_data_for_event)

    next_story_scene = rag_sys.generate_story(
        game_state=gs_dict_for_rag,
        character=char_dict_for_rag
    )

    current_story_event = {
        "scene_id": next_story_scene.scene_id,
        "scene_description": next_story_scene.description,
        "choices_presented": [c.model_dump() for c in next_story_scene.choices],
        "action_taken": made_choice_obj,
        "messages": event_data_after_plugins.get("messages", [])
    }

    # Extract potential game_data updates from plugins
    game_data_plugin_updates = event_data_after_plugins.get("game_state", {}).get("game_data")

    updated_gs_after_choice = crud.crud_game.update_game_state(
        db, game_state=game_state,
        story_event=current_story_event,
        new_scene_id=next_story_scene.scene_id,
        game_data_updates=game_data_plugin_updates # Pass updates from plugins
    )

    scene_event_data = {
        "character": char_dict_for_rag,
        "game_state": schemas.GameStateInDB.model_validate(updated_gs_after_choice).model_dump(),
        "scene": next_story_scene.model_dump(),
        "messages": []
    }
    scene_event_data_after_plugins = plugin_mgr.emit_event("scene_generated", scene_event_data)

    final_messages = event_data_after_plugins.get("messages", []) + scene_event_data_after_plugins.get("messages", [])

    return schemas.BaseResponse[schemas.StoryScene](
        data=next_story_scene,
        message="Choice processed. " + " ".join(m for m in final_messages if isinstance(m, str))
    )

@router.get("/state/{character_id}", response_model=schemas.BaseResponse[schemas.GameStateInDB])
def get_character_game_state(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_active_user)
):
    """Retrieves the active game state for a specific character."""
    character = crud.crud_character.get_character(db, character_id=character_id)
    if not character or character.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found.")

    game_state = crud.crud_game.get_active_game_state_for_character(db, character_id=character.id)
    if not game_state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active game state not found for this character.")

    return schemas.BaseResponse[schemas.GameStateInDB](data=schemas.GameStateInDB.model_validate(game_state))

@router.post("/save", response_model=schemas.BaseResponse[schemas.GameSaveInDB])
def save_current_game(
    *,
    db: Session = Depends(get_db),
    save_request: schemas.GameSaveCreate,
    current_user: UserModel = Depends(deps.get_current_active_user)
):
    """Saves the current game progress for a character."""
    character = crud.crud_character.get_character(db, character_id=save_request.character_id)
    if not character or character.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found for saving progress.")

    active_game_state = crud.crud_game.get_active_game_state_for_character(db, character_id=save_request.character_id)
    if not active_game_state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active game state to save for this character.")

    game_save = crud.crud_game.create_game_save(
        db=db,
        user_id=current_user.id,
        character_id=save_request.character_id,
        game_state_id=active_game_state.id,
        save_name=save_request.save_name,
        save_slot=save_request.save_slot
    )
    return schemas.BaseResponse[schemas.GameSaveInDB](
        data=schemas.GameSaveInDB.model_validate(game_save),
        message="Game progress saved successfully."
    )

@router.get("/saves", response_model=schemas.BaseResponse[List[schemas.GameSaveInDB]])
def list_user_saves(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """Lists all game saves for the current user."""
    game_saves = crud.crud_game.get_game_saves_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    validated_saves = [schemas.GameSaveInDB.model_validate(gs) for gs in game_saves]
    return schemas.BaseResponse[List[schemas.GameSaveInDB]](data=validated_saves)

@router.post("/load", response_model=schemas.BaseResponse[schemas.StoryScene])
def load_saved_game(
    *,
    db: Session = Depends(get_db),
    load_request: schemas.GameLoadRequest,
    current_user: UserModel = Depends(deps.get_current_active_user),
    rag_sys: RAGSystem = Depends(deps.get_rag_system)
):
    """Loads a game from a save point and returns the current scene."""
    game_save = crud.crud_game.get_game_save(db, game_save_id=load_request.save_id)
    if not game_save or game_save.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game save not found or access denied.")

    loaded_game_state = crud.crud_game.get_game_state(db, game_state_id=game_save.game_state_id)
    if not loaded_game_state:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Corrupted save data: Associated game state not found.")

    character = crud.crud_character.get_character(db, character_id=loaded_game_state.character_id)
    if not character:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Corrupted save data: Associated character for game state not found.")
    if character.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to this game character denied.")

    story_scene_to_return: Optional[schemas.StoryScene] = None
    if loaded_game_state.story_history and isinstance(loaded_game_state.story_history, list) and len(loaded_game_state.story_history) > 0:
        last_event = loaded_game_state.story_history[-1]
        if isinstance(last_event, dict) and "scene_description" in last_event and "choices_presented" in last_event and isinstance(last_event["choices_presented"], list):
            story_scene_to_return = schemas.StoryScene(
                scene_id=last_event.get("scene_id", loaded_game_state.current_scene_id),
                description=last_event["scene_description"],
                choices=[schemas.StoryChoice(**c) for c in last_event["choices_presented"] if isinstance(c, dict)]
            )

    if not story_scene_to_return:
        story_scene_to_return = rag_sys.generate_story(
            game_state=schemas.GameStateInDB.model_validate(loaded_game_state).model_dump(),
            character=schemas.CharacterDetailed.model_validate(character).model_dump()
        )
        if loaded_game_state.current_scene_id != story_scene_to_return.scene_id or not loaded_game_state.story_history:
            resumed_event = {
                "scene_id": story_scene_to_return.scene_id,
                "scene_description": story_scene_to_return.description,
                "choices_presented": [c.model_dump() for c in story_scene_to_return.choices],
                "messages": ["Game loaded. Resuming narrative from a generated scene."]
            }
            crud.crud_game.update_game_state(db, game_state=loaded_game_state,
                                           story_event=resumed_event,
                                           new_scene_id=story_scene_to_return.scene_id)

    return schemas.BaseResponse[schemas.StoryScene](
        data=story_scene_to_return,
        message=f"Game loaded successfully from save '{game_save.save_name}'."
    )
