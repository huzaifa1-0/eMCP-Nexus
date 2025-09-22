from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from pydantic import BaseModel

from backend import crud
from backend.db import get_async_session
from backend.security import create_access_token, verify_password
from backend.config import settings

router = APIRouter()

class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    username: str
    email: str
    message: str = "User created successfully"

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserRegister, session: AsyncSession = Depends(get_async_session)):
    """
    Register a new user with a hashed password.
    """
    print(f"Registration attempt for: {user.email}")  # Debug log
    
    # Check if user already exists
    existing_user = await crud.get_user_by_email(session, email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create a UserCreate object from the incoming data
    from backend.models.pydantic import UserCreate
    user_create = UserCreate(
        username=user.username,
        email=user.email,
        password=user.password
    )
    
    db_user = await crud.create_user(session, user=user_create)
    
    return UserResponse(
        username=db_user.username,
        email=db_user.email,
        message="User created successfully"
    )

@router.post("/login", response_model=Token)
async def login_for_access_token(user_data: UserLogin, session: AsyncSession = Depends(get_async_session)):
    """
    Authenticate user and return JWT token.
    """
    print(f"Login attempt for: {user_data.email}")  # Debug log
    
    user = await crud.get_user_by_email(session, email=user_data.email)
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},  # Using email as subject for JWT
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Add a simple test endpoint to verify the auth router is working
@router.get("/test")
async def auth_test():
    return {"message": "Auth router is working!"}