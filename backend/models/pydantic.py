from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


# --- Tool Models ---
class ToolBase(BaseModel):
    name: str
    description: str
    cost: float
    url: str

class ToolCreate(ToolBase):
    pass # For creating a new tool, no extra fields needed

class ToolResponse(ToolBase):
    id: int
    owner_id: int
    # This config is essential to convert SQLAlchemy ORM objects to Pydantic models
    model_config = ConfigDict(from_attributes=True) 