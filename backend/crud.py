from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.models.db import DBUser, DBTool, DBTransaction
from backend.models.pydantic import ToolCreate, UserCreate, TransactionCreate


# Use the real password hashing utility from security.py
from backend.security import get_password_hash

# ==================================
# CRUD for Users
# ==================================

async def get_user(db: AsyncSession, user_id: int):
    """Fetch a single user by their ID."""
    result = await db.execute(select(DBUser).filter(DBUser.id == user_id))
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str):
    """Fetch a single user by their username."""
    result = await db.execute(select(DBUser).filter(DBUser.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate):
    """Create a new user in the database."""
    hashed_password = get_password_hash(user.password)
    db_user = DBUser(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# ==================================
# CRUD for Tools
# =-================================

async def get_tools(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Fetch multiple tools with pagination."""
    result = await db.execute(select(DBTool).offset(skip).limit(limit))
    return result.scalars().all()

async def create_user_tool(db: AsyncSession, tool: ToolCreate, user_id: int):
    """Create a new tool associated with a user."""
    db_tool = DBTool(**tool.model_dump(), owner_id=user_id)
    db.add(db_tool)
    await db.commit()
    await db.refresh(db_tool)
    return db_tool

# ==================================
# CRUD for Transactions
# ==================================

async def create_transaction(db: AsyncSession, transaction: TransactionCreate, user_id: int):
    """Create a new transaction for a user."""
    db_transaction = DBTransaction(
        **transaction.model_dump(),
        user_id=user_id
    )
    db.add(db_transaction)
    await db.commit()
    await db.refresh(db_transaction)
    return db_transaction
