from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from backend import crud
from backend.db import get_async_session
from backend.models.pydantic import UserCreate, User
from backend.security import create_access_token, verify_password
from backend.config import settings
from pydantic import BaseModel

router = APIRouter()

class UserLogin(BaseModel):
    email: str
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=User)
async def register_user(user: UserCreate, session: AsyncSession = Depends(get_async_session)):
    """
    Register a new user with a hashed password.
    """
    existing_user = await crud.get_user_by_email(session, email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = await crud.create_user(session, user=user)
    return db_user

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: UserLogin, session: AsyncSession = Depends(get_async_session)):
    """
    Authenticate user and return JWT token.
    """
    user = await crud.get_user_by_email(session, email=form_data.email)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}