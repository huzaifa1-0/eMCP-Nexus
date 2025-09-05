from fastapi import APIRouter, HTTPException, Depends
from backend.models.db import DBTool, DBUser
from backend.models.pydantic import ToolCreate, ToolResponse
from backend.db import get_async_session
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter()

tools_table = sqlalchemy.Table(
    "tools", sqlalchemy.MetaData(),
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("description", sqlalchemy.String),
    sqlalchemy.Column("cost", sqlalchemy.Float)
)


@router.post("/", response_model=ToolResponse)
async def create_tool(tool_data: ToolCreate, 
                      user: DBUser = Depends(get_current_user), # Assumes you have auth
                      session: AsyncSession = Depends(get_async_session)):
    
    
    db_tool = DBTool(**tool_data.dict(), owner_id=user.id)
    session.add(db_tool)
    await session.commit()
    await session.refresh(db_tool)
    
    
    return db_tool


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(tool_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(DBTool).where(DBTool.id == tool_id)
    result = await session.execute(query)
    tool = result.scalars().first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool