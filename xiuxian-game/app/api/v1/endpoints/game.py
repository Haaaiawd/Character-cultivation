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
<<<<<<< HEAD
    """Starts a new game for a character or resumes if an active game state exists (MVP: creates new)."""
=======
>>>>>>> origin/haa
    character = crud.crud_character.get_character(db, character_id=game_start_request.character_id)
    if not character or character.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found or not owned by user")

<<<<<<< HEAD
    # For MVP, starting a game always creates a new game state.
    game_state = crud.crud_game.create_game_state(db, character_id=character.id)

    # Prepare data for 'game_started' event
    char_data_for_event = schemas.CharacterDetailed.model_validate(character).model_dump()
    gs_data_for_event = schemas.GameStateInDB.model_validate(game_state).model_dump()

    event_data = {
        "character": char_data_for_event,
        "game_state": gs_data_for_event,
=======
    game_state = crud.crud_game.create_game_state(db, character_id=character.id)

    char_model_for_event = schemas.CharacterDetailed.model_validate(character)
    gs_model_for_event = schemas.GameStateInDB.model_validate(game_state)

    event_data = {
        "character": char_model_for_event.model_dump(),
        "game_state": gs_model_for_event.model_dump(),
>>>>>>> origin/haa
        "messages": []
    }
    event_data_after_plugins = plugin_mgr.emit_event("game_started", event_data)

<<<<<<< HEAD
    char_dict_for_rag = event_data_after_plugins.get("character", char_data_for_event)
    gs_dict_for_rag = event_data_after_plugins.get("game_state", gs_data_for_event)

    story_scene = rag_sys.generate_story(
=======
    char_dict_for_rag = event_data_after_plugins.get("character", char_model_for_event.model_dump())
    gs_dict_for_rag = event_data_after_plugins.get("game_state", gs_model_for_event.model_dump())

    initial_story_scene = rag_sys.generate_story(
>>>>>>> origin/haa
        game_state=gs_dict_for_rag,
        character=char_dict_for_rag
    )

<<<<<<< HEAD
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
=======
    initial_scene_duration = initial_story_scene.duration_days if initial_story_scene.duration_days is not None else 1
    date_before_event = game_state.current_date

    updated_gs_after_start_scene = crud.crud_game.update_game_state(
        db, game_state=game_state,
        story_event={},
        new_scene_id=initial_story_scene.scene_id,
        advance_days=initial_scene_duration
    )

    story_event_for_start = {
        "scene_id": initial_story_scene.scene_id,
        "plot": initial_story_scene.plot,
        "choices_presented": [c.model_dump() for c in initial_story_scene.choices],
        "messages": event_data_after_plugins.get("messages", []),
        "event_type": "game_started",
        "duration_applied_days": initial_scene_duration,
        "date_before_event": date_before_event,
        "date_after_event": updated_gs_after_start_scene.current_date
    }

    if isinstance(updated_gs_after_start_scene.story_history, list):
        updated_gs_after_start_scene.story_history = (updated_gs_after_start_scene.story_history or [])[:-1] + [story_event_for_start]
    else: # Should not happen based on model default, but as a safeguard
        updated_gs_after_start_scene.story_history = [story_event_for_start]
    db.commit()
    db.refresh(updated_gs_after_start_scene)

    return schemas.BaseResponse[schemas.StoryScene](
        data=initial_story_scene,
        message="Game started. In-game date: " + str(updated_gs_after_start_scene.current_date) + ". " + " ".join(event_data_after_plugins.get("messages", []))
>>>>>>> origin/haa
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
<<<<<<< HEAD
    """Processes a player's choice and returns the next game scene."""
=======
>>>>>>> origin/haa
    character = crud.crud_character.get_character(db, character_id=choice_request.character_id)
    if not character or character.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found or not owned by user")

    game_state = crud.crud_game.get_active_game_state_for_character(db, character_id=character.id)
    if not game_state:
<<<<<<< HEAD
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active game state not found for this character.")
=======
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active game state not found.")
>>>>>>> origin/haa

    made_choice_obj = {"id": choice_request.choice_id, "text": f"Choice text for {choice_request.choice_id} (not found in history)"}
    if game_state.story_history and isinstance(game_state.story_history, list) and len(game_state.story_history) > 0:
        last_event = game_state.story_history[-1]
        if isinstance(last_event, dict) and "choices_presented" in last_event and isinstance(last_event["choices_presented"], list):
            found_choice = next((c for c in last_event["choices_presented"] if isinstance(c, dict) and c.get("id") == choice_request.choice_id), None)
<<<<<<< HEAD
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
=======
            if found_choice: made_choice_obj = found_choice
            else: logging.warning(f"Choice ID '{choice_request.choice_id}' not found in previous scene for char {character.id}.")

    char_model_for_event = schemas.CharacterDetailed.model_validate(character)
    gs_model_for_event = schemas.GameStateInDB.model_validate(game_state)

    event_data_choice_made = {
        "character": char_model_for_event.model_dump(),
        "game_state": gs_model_for_event.model_dump(),
        "choice": made_choice_obj,
        "messages": []
    }
    event_data_after_choice_plugins = plugin_mgr.emit_event("choice_made", event_data_choice_made)

    char_dict_for_rag = event_data_after_choice_plugins.get("character", char_model_for_event.model_dump())
    gs_dict_for_rag = event_data_after_choice_plugins.get("game_state", gs_model_for_event.model_dump())
>>>>>>> origin/haa

    next_story_scene = rag_sys.generate_story(
        game_state=gs_dict_for_rag,
        character=char_dict_for_rag
    )

<<<<<<< HEAD
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
=======
    current_event_duration = next_story_scene.duration_days if next_story_scene.duration_days is not None else 1
    date_before_event = game_state.current_date

    game_data_plugin_updates = event_data_after_choice_plugins.get("game_state", {}).get("game_data")

    updated_gs_after_choice_action = crud.crud_game.update_game_state(
        db, game_state=game_state,
        story_event={},
        new_scene_id=next_story_scene.scene_id,
        game_data_updates=game_data_plugin_updates,
        advance_days=current_event_duration
    )

    story_event_for_choice = {
        "scene_id": next_story_scene.scene_id,
        "plot": next_story_scene.plot,
        "choices_presented": [c.model_dump() for c in next_story_scene.choices],
        "action_taken": made_choice_obj,
        "messages": event_data_after_choice_plugins.get("messages", []),
        "event_type": "choice_made",
        "duration_applied_days": current_event_duration,
        "date_before_event": date_before_event,
        "date_after_event": updated_gs_after_choice_action.current_date
    }
    if isinstance(updated_gs_after_choice_action.story_history, list):
        updated_gs_after_choice_action.story_history = (updated_gs_after_choice_action.story_history or [])[:-1] + [story_event_for_choice]
    else: # Should not happen
        updated_gs_after_choice_action.story_history = [story_event_for_choice]
    db.commit()
    db.refresh(updated_gs_after_choice_action)

    scene_event_data = {
        "character": char_dict_for_rag,
        "game_state": schemas.GameStateInDB.model_validate(updated_gs_after_choice_action).model_dump(),
>>>>>>> origin/haa
        "scene": next_story_scene.model_dump(),
        "messages": []
    }
    scene_event_data_after_plugins = plugin_mgr.emit_event("scene_generated", scene_event_data)

<<<<<<< HEAD
    final_messages = event_data_after_plugins.get("messages", []) + scene_event_data_after_plugins.get("messages", [])

    return schemas.BaseResponse[schemas.StoryScene](
        data=next_story_scene,
        message="Choice processed. " + " ".join(m for m in final_messages if isinstance(m, str))
=======
    final_messages = event_data_after_choice_plugins.get("messages", []) + scene_event_data_after_plugins.get("messages", [])

    return schemas.BaseResponse[schemas.StoryScene](
        data=next_story_scene,
        message="Choice processed. In-game date: " + str(updated_gs_after_choice_action.current_date) + ". " + " ".join(m for m in final_messages if isinstance(m, str))
>>>>>>> origin/haa
    )

@router.get("/state/{character_id}", response_model=schemas.BaseResponse[schemas.GameStateInDB])
def get_character_game_state(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_active_user)
):
<<<<<<< HEAD
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
=======
    character = crud.crud_character.get_character(db, character_id=character_id)
    if not character or character.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found.")
    game_state = crud.crud_game.get_active_game_state_for_character(db, character_id=character.id)
    if not game_state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active game state not found.")
    return schemas.BaseResponse[schemas.GameStateInDB](data=schemas.GameStateInDB.model_validate(game_state))

@router.post("/save", response_model=schemas.BaseResponse[schemas.GameSaveInDB])
def save_game(
>>>>>>> origin/haa
    *,
    db: Session = Depends(get_db),
    save_request: schemas.GameSaveCreate,
    current_user: UserModel = Depends(deps.get_current_active_user)
):
<<<<<<< HEAD
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
=======
    character = crud.crud_character.get_character(db, character_id=save_request.character_id)
    if not character or character.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found for save.")
    active_game_state = crud.crud_game.get_active_game_state_for_character(db, character_id=save_request.character_id)
    if not active_game_state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active game to save.")
    game_save = crud.crud_game.create_game_save(
        db=db, user_id=current_user.id, character_id=save_request.character_id,
        game_state_id=active_game_state.id, save_name=save_request.save_name, save_slot=save_request.save_slot
    )
    return schemas.BaseResponse[schemas.GameSaveInDB](data=schemas.GameSaveInDB.model_validate(game_save), message="Game saved.")

@router.get("/saves", response_model=schemas.BaseResponse[List[schemas.GameSaveInDB]])
def list_saves(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_active_user),
    skip: int = 0, limit: int = 100
):
    game_saves = crud.crud_game.get_game_saves_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return schemas.BaseResponse[List[schemas.GameSaveInDB]](data=[schemas.GameSaveInDB.model_validate(gs) for gs in game_saves])

@router.post("/load", response_model=schemas.BaseResponse[schemas.StoryScene])
def load_game(
>>>>>>> origin/haa
    *,
    db: Session = Depends(get_db),
    load_request: schemas.GameLoadRequest,
    current_user: UserModel = Depends(deps.get_current_active_user),
<<<<<<< HEAD
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
=======
    rag_sys: RAGSystem = Depends(deps.get_rag_system),
    plugin_mgr: PluginManager = Depends(deps.get_plugin_manager)
):
    game_save = crud.crud_game.get_game_save(db, game_save_id=load_request.save_id)
    if not game_save or game_save.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game save not found.")

    loaded_game_state_from_db = crud.crud_game.get_game_state(db, game_state_id=game_save.game_state_id)
    if not loaded_game_state_from_db:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Saved game state data not found.")

    character = crud.crud_character.get_character(db, character_id=loaded_game_state_from_db.character_id)
    if not character or character.user_id != current_user.id:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Character access denied.")

    char_model_for_event = schemas.CharacterDetailed.model_validate(character)
    gs_model_for_event = schemas.GameStateInDB.model_validate(loaded_game_state_from_db)

    game_loaded_event_data = {
        "character": char_model_for_event.model_dump(),
        "game_state": gs_model_for_event.model_dump(),
        "messages": []
    }
    event_data_after_load_plugins = plugin_mgr.emit_event("game_loaded", game_loaded_event_data)

    # Use game state potentially modified by plugins for RAG and scene reconstruction
    current_gs_dict = event_data_after_load_plugins.get("game_state", gs_model_for_event.model_dump())
    current_char_dict = event_data_after_load_plugins.get("character", char_model_for_event.model_dump())


    story_scene_to_return: Optional[schemas.StoryScene] = None
    if current_gs_dict.get("story_history") and isinstance(current_gs_dict["story_history"], list) and current_gs_dict["story_history"]:
        last_event = current_gs_dict["story_history"][-1]
        if isinstance(last_event, dict) and "plot" in last_event and "choices_presented" in last_event:
            story_scene_to_return = schemas.StoryScene(
                scene_id=last_event.get("scene_id", current_gs_dict.get("current_scene_id")),
                plot=last_event["plot"],
                choices=[schemas.StoryChoice(**c) for c in last_event["choices_presented"] if isinstance(c, dict)],
                duration_days=last_event.get("duration_applied_days")
            )

    if not story_scene_to_return:
        story_scene_from_rag = rag_sys.generate_story(
            game_state=current_gs_dict,
            character=current_char_dict
        )
        loaded_event_duration = story_scene_from_rag.duration_days if story_scene_from_rag.duration_days is not None else 1
        date_before_event = current_gs_dict.get("current_date", "Day 1")

        # Update the GameState model instance from DB
        updated_gs_after_load_resume = crud.crud_game.update_game_state(
            db, game_state=loaded_game_state_from_db,
            story_event={}, # Placeholder, updated below
            new_scene_id=story_scene_from_rag.scene_id,
            advance_days=loaded_event_duration
        )

        resumed_event = {
            "scene_id": story_scene_from_rag.scene_id,
            "plot": story_scene_from_rag.plot,
            "choices_presented": [c.model_dump() for c in story_scene_from_rag.choices],
            "messages": event_data_after_load_plugins.get("messages", []) + ["Game loaded. Resuming narrative with a newly generated scene."],
            "event_type": "game_loaded_resume",
            "duration_applied_days": loaded_event_duration,
            "date_before_event": date_before_event,
            "date_after_event": updated_gs_after_load_resume.current_date
        }
        if isinstance(updated_gs_after_load_resume.story_history, list):
             updated_gs_after_load_resume.story_history = (updated_gs_after_load_resume.story_history or [])[:-1] + [resumed_event]
        else: # Should not happen
            updated_gs_after_load_resume.story_history = [resumed_event]
        db.commit()
        db.refresh(updated_gs_after_load_resume)

        story_scene_to_return = story_scene_from_rag

    if not story_scene_to_return:
        return schemas.BaseResponse[schemas.StoryScene](success=False, message="Failed to reconstruct or generate scene on load.", data=None)

    final_response_message = f"Game loaded from save '{game_save.save_name}'. Current in-game date: {loaded_game_state_from_db.current_date}."
    plugin_messages_on_load = event_data_after_load_plugins.get("messages", [])
    if plugin_messages_on_load:
        final_response_message += " " + " ".join(m for m in plugin_messages_on_load if isinstance(m, str))

    return schemas.BaseResponse[schemas.StoryScene](
        data=story_scene_to_return,
        message=final_response_message
>>>>>>> origin/haa
    )
