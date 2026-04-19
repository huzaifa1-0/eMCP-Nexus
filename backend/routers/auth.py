from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from pydantic import BaseModel

from backend import crud
from backend.db import get_async_session
from backend.security import create_access_token, verify_password, get_current_user
from backend.models.db import DBUser
from backend.config import settings
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from starlette.responses import RedirectResponse
import uuid

router = APIRouter()

# Initialize OAuth
oauth = OAuth()
oauth.register(
    name='github',
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

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

# --- GitHub OAuth Routes ---

@router.get("/github/login")
async def github_login(request: Request):
    """
    Redirect the user to GitHub for authentication.
    """
    redirect_uri = request.url_for('github_callback')
    return await oauth.github.authorize_redirect(request, str(redirect_uri))

@router.get("/github/callback", name="github_callback")
async def github_callback(request: Request, session: AsyncSession = Depends(get_async_session)):
    """
    Handle the callback from GitHub, get user info, and log them in.
    """
    try:
        token = await oauth.github.authorize_access_token(request)
        resp = await oauth.github.get('user', token=token)
        user_info = resp.json()
        
        if not isinstance(user_info, dict):
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth-callback?error=GitHub returned an invalid profile response")

        # Get user email
        email = user_info.get("email")
        if not email:
            emails_resp = await oauth.github.get('user/emails', token=token)
            emails = emails_resp.json()
            
            if isinstance(emails, list):
                # Find primary email
                for e in emails:
                    if isinstance(e, dict) and e.get("primary") and e.get("verified"):
                        email = e.get("email")
                        break
                if not email and len(emails) > 0:
                    email = emails[0].get("email")
        
        if not email:
            return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth-callback?error=Could not retrieve a verified email from your GitHub account")

        # Check if user exists
        db_user = await crud.get_user_by_email(session, email=email)
        
        if not db_user:
            # Create a new user if they don't exist
            from backend.models.pydantic import UserCreate
            username = user_info.get("login") or email.split("@")[0]
            
            # Check if username is taken, append random suffix if needed
            existing_username = await crud.get_user_by_username(session, username=username)
            if existing_username:
                username = f"{username}_{uuid.uuid4().hex[:4]}"
            
            user_create = UserCreate(
                username=username,
                email=email,
                password=str(uuid.uuid4()) # Random password for social login
            )
            db_user = await crud.create_user(session, user=user_create)
        
        # Create JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.email},
            expires_delta=access_token_expires
        )
        
        # Redirect back to frontend
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth-callback?token={access_token}&email={email}")

    except Exception as e:
        print(f"GitHub Auth Error: {e}")
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth-callback?error=Authentication failed: {str(e)}")

# --- Profile Management Routes ---

@router.get("/me")
async def get_my_profile(current_user: DBUser = Depends(get_current_user)):
    """
    Returns the current user's profile information.
    """
    return {
        "username": current_user.username,
        "email": current_user.email,
        "id": current_user.id
    }

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Verifies current password and updates to a new one.
    """
    # Verify current password
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    await crud.update_user_password(session, user_id=current_user.id, new_password=request.new_password)
    
    return {"message": "Password updated successfully"}
