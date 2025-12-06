from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any

from backend.db import get_async_session
from backend.security import get_current_user
from backend.models.db import DBUser, DBTool, DBTransaction, DBUsageLog

router = APIRouter()

@router.get("/stats")
