# app/api/v1/endpoints/characters.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import schemas # Root import for schemas
from app import crud    # Root import for crud
from app.api import deps # For dependencies like get_current_active_user
from app.db.session import get_db # Corrected: get_db is in app.db.session, not directly app.db
from app.models.user_models import User as UserModel # For type hint on current_user

router = APIRouter()

@router.post("/", response_model=schemas.BaseResponse[schemas.CharacterDetailed])
def create_new_character(
    *, # Enforce keyword arguments
    db: Session = Depends(get_db),
    character_in: schemas.CharacterCreate,
    current_user: UserModel = Depends(deps.get_current_active_user)
):
    """
    Create a new character for the current user.
    """
    # Optional: Validate identity_id if provided
    if character_in.identity_id:
        identity = crud.crud_character.get_identity(db, identity_id=character_in.identity_id)
        if not identity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Identity with id {character_in.identity_id} not found."
            )

    created_character = crud.crud_character.create_character(
        db=db, character_in=character_in, user_id=current_user.id
    )
    # Use .model_validate for Pydantic V2
    return schemas.BaseResponse[schemas.CharacterDetailed](
        data=schemas.CharacterDetailed.model_validate(created_character)
    )


@router.get("/", response_model=schemas.BaseResponse[List[schemas.CharacterSimple]])
def read_user_characters(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(deps.get_current_active_user)
):
    """
    Retrieve characters for the current user.
    """
    characters = crud.crud_character.get_characters_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    # Use .model_validate for Pydantic V2
    validated_characters = [schemas.CharacterSimple.model_validate(char) for char in characters]
    return schemas.BaseResponse[List[schemas.CharacterSimple]](data=validated_characters)


@router.get("/{character_id}", response_model=schemas.BaseResponse[schemas.CharacterDetailed])
def read_character_by_id(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_active_user)
):
    """
    Get a specific character by id, owned by the current user.
    """
    character = crud.crud_character.get_character(db=db, character_id=character_id)
    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    if character.user_id != current_user.id:
        # This check might be redundant if queries always filter by user_id,
        # but it's a good safeguard for direct ID lookups.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    # Use .model_validate for Pydantic V2
    return schemas.BaseResponse[schemas.CharacterDetailed](
        data=schemas.CharacterDetailed.model_validate(character)
    )

# Placeholder for PUT /api/v1/characters/{character_id} if needed later
# @router.put("/{character_id}", response_model=schemas.BaseResponse[schemas.CharacterDetailed])
# def update_existing_character(
#     character_id: int,
#     character_in: schemas.CharacterUpdate,
#     db: Session = Depends(get_db),
#     current_user: UserModel = Depends(deps.get_current_active_user)
# ):
#     character = crud.crud_character.get_character(db=db, character_id=character_id)
#     if not character:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
#     if character.user_id != current_user.id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

#     updated_character = crud.crud_character.update_character(db=db, character=character, character_update=character_in)
#     return schemas.BaseResponse[schemas.CharacterDetailed](
#         data=schemas.CharacterDetailed.model_validate(updated_character)
#     )
