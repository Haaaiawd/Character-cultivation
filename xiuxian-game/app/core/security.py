# app/core/security.py
from datetime import datetime, timedelta
from typing import Any, Union, Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import ValidationError # For handling token data validation

from app.core.config import settings
from app.schemas.token_schemas import TokenData # Assuming TokenData is in token_schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def decode_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        # The 'sub' field in JWT is typically the username or user ID
        # Adjust TokenData schema if it expects other fields from payload
        token_data = TokenData(username=payload.get("sub"))
        return token_data
    except (JWTError, ValidationError, AttributeError): # Catch AttributeError if payload.get("sub") is None and TokenData expects str
        return None
