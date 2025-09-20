from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_async_session
from backend.models.pydantic import UserCreate, User
from backend.security import get_password_hash, verify_password, create_access_token
from backend import crud
import logging

logger = logging.getLogger("ai_marketplace")

router = APIRouter()

class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

@router.post("/register", response_model=User)
async def register_user(user: UserCreate, session: AsyncSession = Depends(get_async_session)) -> User:
    """
    Register a new user with hashed password.
    """
    try:
        # Check if user/email already exists
        existing_user = await crud.get_user_by_username(session, user.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

        existing_email = await crud.get_user_by_email(session, user.email)
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create user
        db_user = await crud.create_user(session, user)
        return db_user
    except Exception as e:
        # Log the full exception
        logger.exception("An error occurred during user registration:")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")


@router.post("/login")
async def login_user(user: UserLogin, session: AsyncSession = Depends(get_async_session)) -> dict:
    """
    Authenticate user and return JWT token.
    """
    from backend.models.db import DBUser
    from sqlalchemy import select
    result = await session.execute(select(DBUser).where(DBUser.email == user.email))
    db_user = result.scalars().first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}