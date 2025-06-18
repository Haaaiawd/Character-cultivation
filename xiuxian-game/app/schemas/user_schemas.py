# app/schemas/user_schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List # Required for CharacterInDB below (even if empty for now)
# Forward references for Character related schemas if defined later or for clarity
# from .character_schemas import CharacterInDB # Example

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase): # UserUpdate should also allow partial updates, so all fields optional
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True # Pydantic V2 uses from_attributes instead of orm_mode

class User(UserInDBBase): # Schema for returning a user
    pass

# If you need to return user with their characters, you'd define something like:
# class UserWithCharacters(User):
#     # Ensure character_schemas.py defines CharacterInDB or similar
#     # from .character_schemas import CharacterInDB
#     characters: List['CharacterInDB'] # Forward ref if CharacterInDB is in another file
