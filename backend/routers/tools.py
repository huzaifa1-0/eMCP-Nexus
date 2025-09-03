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

