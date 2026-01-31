from pydantic import BaseModel, ConfigDict
from datetime import datetime
from pydantic import field_validator, Field
from typing import Optional, List, Any

class ToolBase(BaseModel):
    name: str
    description: str
    cost: float = Field(..., ge=0, description="Tool cost must be positive")
    repo_url: str
    branch: str = "main"
    build_command: str = "npm install && npm run build"
    start_command: str = "npm start"
    root_dir: str = ""

class ToolCreate(ToolBase):
    env_vars: Optional[dict] = None 

class Tool(ToolBase):
    id: int
    owner_id: int
    url: Optional[str] = None              
    tool_definitions: Optional[List[Any]]
    
    model_config = ConfigDict(from_attributes=True) 


class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str 

class User(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True) 


class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0, description="Transaction amount must be positive")
    currency: str
    method: str
    tool_id: int

# Add a rating model for validation
class RatingBase(BaseModel):
    rating: int = Field(..., ge=0, le=5, description="Rating must be between 0 and 5")
    tool_id: int

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    user_id: int
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)