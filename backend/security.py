from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from clerk_sdk.client import ClerkClient
from .config import settings
from . import crud
from sqlalchemy.ext.asyncio import AsyncSession
from .db import get_async_session
from .models.db import DBUser

# Initialize the Clerk client
clerk_client = ClerkClient(secret_key=settings.CLERK_SECRET_KEY)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # tokenUrl is just a placeholder

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_session)
) -> DBUser:
    """
    Verifies the Clerk JWT and syncs the user with the local database.
    """
    try:
        # Verify the token with Clerk
        decoded_token = clerk_client.sessions.verify_token(token=token)
        user_id = decoded_token["sub"]

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if the user exists in our database
    user = await crud.get_user(db, user_id=user_id)
    if user:
        return user

    # If not, fetch their details from Clerk and create a local record
    clerk_user = clerk_client.users.get_user(user_id=user_id)

    new_user = DBUser(
        id=clerk_user.id,
        email=clerk_user.email_addresses[0].email_address,
        username=clerk_user.username or clerk_user.email_addresses[0].email_address.split('@')[0],
        # We don't store passwords anymore
        hashed_password="managed_by_clerk"
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

# It is important to also update the crud.py to take in the id as a string