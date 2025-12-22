import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from groq import Groq
from backend.db import get_async_session
from backend.services.vector_search import search_tools

router = APIRouter()

