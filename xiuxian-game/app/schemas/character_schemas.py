# app/schemas/character_schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any # For JSON fields

# --- Identity Schemas ---
class IdentityBase(BaseModel):
    name: str
    description: Optional[str] = None
    starting_benefits: Optional[Dict[str, Any]] = None

class IdentityCreate(IdentityBase):
    pass

class IdentityUpdate(IdentityBase): # For PUT, typically all fields. For PATCH, all optional.
    name: Optional[str] = None # Making fields optional for PATCH-like behavior
    description: Optional[str] = None
    starting_benefits: Optional[Dict[str, Any]] = None


class IdentityInDB(IdentityBase):
    id: int

    class Config:
        from_attributes = True

# --- CharacterAttribute Schemas ---
class CharacterAttributeBase(BaseModel):
    strength: int = 10
    agility: int = 10
    intelligence: int = 10
    constitution: int = 10
    perception: int = 10
    luck: int = 10

class CharacterAttributeCreate(CharacterAttributeBase):
    pass # Attributes can be set on creation or default

class CharacterAttributeUpdate(BaseModel): # Allow partial updates
    strength: Optional[int] = None
    agility: Optional[int] = None
    intelligence: Optional[int] = None
    constitution: Optional[int] = None
    perception: Optional[int] = None
    luck: Optional[int] = None

class CharacterAttributeInDB(CharacterAttributeBase):
    # character_id: int # Not needed if always nested under Character
    pass # No extra fields from model needed if used as nested

    class Config:
        from_attributes = True


# --- Character Schemas ---
class CharacterBase(BaseModel):
    name: str
    identity_id: Optional[int] = None # Identity can be chosen later

class CharacterCreate(CharacterBase):
    # user_id will be set from authenticated user typically
    attributes: Optional[CharacterAttributeCreate] = None # Allow setting attributes on creation

class CharacterUpdate(BaseModel): # Allow partial updates
    name: Optional[str] = None
    identity_id: Optional[int] = None
    level: Optional[int] = None
    cultivation_stage: Optional[str] = None
    experience: Optional[int] = None
    attributes: Optional[CharacterAttributeUpdate] = None


class CharacterInDBBase(CharacterBase):
    id: int
    user_id: int
    level: int
    cultivation_stage: str
    experience: int
    created_at: datetime

    identity: Optional[IdentityInDB] = None # Nested Identity info
    attributes: Optional[CharacterAttributeInDB] = None # Nested attributes

    class Config:
        from_attributes = True

class CharacterSimple(BaseModel): # For lists where full detail isn't needed
    id: int
    name: str
    level: int
    cultivation_stage: str

    class Config:
        from_attributes = True

class CharacterDetailed(CharacterInDBBase): # Full detail for single character GET
    pass
