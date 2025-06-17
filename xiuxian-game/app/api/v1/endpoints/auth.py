# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas # Use this form of import
from app import crud # Use this form of import
from app.models.user_models import User as UserModel # For type hinting if needed, changed from app.models
from app.core.security import create_access_token, verify_password
from app.db.session import get_db # Import get_db

router = APIRouter()

@router.post("/register", response_model=schemas.BaseResponse[schemas.User])
def register_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    """
    db_user_by_username = crud.crud_user.get_user_by_username(db, username=user_in.username)
    if db_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    db_user_by_email = crud.crud_user.get_user_by_email(db, email=user_in.email)
    if db_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    created_user = crud.crud_user.create_user(db=db, user=user_in)
    # Construct the standard response
    return schemas.BaseResponse[schemas.User](
        success=True,
        message="User registered successfully",
        data=schemas.User.model_validate(created_user) # Pydantic V2
    )

@router.post("/login", response_model=schemas.BaseResponse[schemas.Token])
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = crud.crud_user.get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=user.username) # Use username as subject

    token_data = schemas.Token(access_token=access_token, token_type="bearer")
    return schemas.BaseResponse[schemas.Token](
        success=True,
        message="Login successful",
        data=token_data
    )

# Example of a protected endpoint (to be moved/used later)
# from app.api.deps import get_current_user # This dep would be created later
# @router.get("/users/me", response_model=schemas.User)
# async def read_users_me(current_user: UserModel = Depends(get_current_user)):
#     return current_user
