# app/api/deps.py
from fastapi import Depends, HTTPException, status, Request # Ensure Request is imported
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from app.core.security import decode_token
from app.crud import crud_user
from app.db.session import get_db
from app.models.user_models import User as UserModel
from app.schemas.token_schemas import TokenData # Assuming this schema exists
from app.core.rag_system import RAGSystem # For type hinting
from app.core.plugin_system import PluginManager # For type hinting

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> UserModel:
    token_data = decode_token(token)
    if not token_data or not token_data.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials (token data missing)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = crud_user.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found (from token)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    # Add is_active check here if implemented in UserModel
    return current_user

# --- RAGSystem and PluginManager Dependencies ---
def get_rag_system(request: Request) -> RAGSystem:
    if not hasattr(request.app.state, 'rag_system') or request.app.state.rag_system is None:
        # This error indicates a setup problem in main.py
        raise RuntimeError("RAGSystem instance has not been set on app.state.")
    return request.app.state.rag_system

def get_plugin_manager(request: Request) -> PluginManager:
    if not hasattr(request.app.state, 'plugin_manager') or request.app.state.plugin_manager is None:
        # This error indicates a setup problem in main.py
        raise RuntimeError("PluginManager instance has not been set on app.state.")
    return request.app.state.plugin_manager
