# app/crud/crud_character.py
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.character_models import Character, CharacterAttribute, Identity
from app.schemas.character_schemas import CharacterCreate, CharacterUpdate, CharacterAttributeCreate # Added CharacterAttributeCreate

def get_character(db: Session, character_id: int) -> Optional[Character]:
    return db.query(Character).filter(Character.id == character_id).first()

def get_characters_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Character]:
    return db.query(Character).filter(Character.user_id == user_id).offset(skip).limit(limit).all()

def create_character(db: Session, character_in: CharacterCreate, user_id: int) -> Character:
    db_character = Character(
        name=character_in.name,
        user_id=user_id,
        identity_id=character_in.identity_id # Can be None
        # level, cultivation_stage, experience will use defaults from model
    )
    db.add(db_character)
    db.flush() # Use flush to get db_character.id before creating attributes

    if character_in.attributes:
        # If attributes are provided in CharacterCreate, create them
        db_attributes = CharacterAttribute(
            character_id=db_character.id, # Link to the new character
            **character_in.attributes.model_dump() # Pydantic V2
        )
        db.add(db_attributes)
    else:
        # If no attributes provided, create with default values
        db_attributes = CharacterAttribute(character_id=db_character.id)
        db.add(db_attributes)

    db.commit()
    db.refresh(db_character)
    # db.refresh(db_attributes) # attributes are related, refreshing character should load them if relationship is set up correctly
    return db_character

def update_character(db: Session, character: Character, character_update: CharacterUpdate) -> Character:
    update_data = character_update.model_dump(exclude_unset=True) # Pydantic V2

    for field, value in update_data.items():
        if field == "attributes" and value is not None:
            if character.attributes: # Check if attributes object exists
                # The 'value' here is CharacterAttributeUpdate schema
                # We need to iterate its fields if it's a dict, or directly if it's an object
                # Assuming value is a dict from model_dump() of CharacterAttributeUpdate
                for attr_field, attr_value in value.items(): # value should be a dict from character_update.attributes.model_dump()
                    if attr_value is not None: # Only update if value is provided
                        setattr(character.attributes, attr_field, attr_value)
            # else:
                # If character.attributes is None, it means the CharacterAttribute record was never created.
                # This case should ideally be handled by creating a new CharacterAttribute record.
                # For MVP, assume attributes record exists if trying to update. (Handled in create_character)
        elif value is not None: # Ensure other fields are not None before setting
            setattr(character, field, value)

    db.add(character) # Add character to session before commit
    db.commit()
    db.refresh(character)
    return character

# CRUD for Identity (Optional for this step, but good to have if creating characters involves selecting identities)
def get_identity(db: Session, identity_id: int) -> Optional[Identity]:
    return db.query(Identity).filter(Identity.id == identity_id).first()

def get_identities(db: Session, skip: int = 0, limit: int = 100) -> List[Identity]:
    return db.query(Identity).offset(skip).limit(limit).all()

# Potentially: create_identity, if identities are managed via API
# For MVP, identities might be pre-populated.
