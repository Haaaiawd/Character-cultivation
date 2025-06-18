# app/schemas/token_schemas.py
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    # Add other fields if needed, e.g. user_id
    # user_id: Optional[int] = None
