from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional



class ToolBase(BaseModel):
    name: str
    description: str
    cost: float
    url: str

class ToolCreate(ToolBase):
    pass 

class ToolResponse(ToolBase):
    id: int
    owner_id: int
    
    model_config = ConfigDict(from_attributes=True) 


class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str # 

class UserResponse(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True) 


class TransactionResponse(BaseModel):
    id: int
    tool_id: int
    user_id: int
    amount: float
    currency: str
    method: str
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)