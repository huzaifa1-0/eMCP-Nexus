from fastapi import APIRouter, HTTPException
from backend.models.tool import Tool, ToolCreate
from backend.db import database
import sqlalchemy


router = APIRouter()

tools_table = sqlalchemy.Table(
    "tools", sqlalchemy.MetaData(),
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("description", sqlalchemy.String),
    sqlalchemy.Column("cost", sqlalchemy.Float)
)


@router.post("/", response_model=Tool)
async def create_tool(tool: ToolCreate):
    query = tools_table.insert().values(
        name = tool.name,
        description = tool.description,
        cost = tool.cost
    )
    tool_id = await database.execute(query)
    return {**tool.dict(), "id": tool_id}


@router.get("/{tool_id}", response_model=Tool)
async def get_tool(tool_id: int):
    query = tools_table.select().where(tools_table.c.id == tool_id)
    tool = await database.fetch_one(query)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool