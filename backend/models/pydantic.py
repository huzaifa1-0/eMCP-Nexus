from pydantic import BaseModel, ConfigDict
from datetime import datetime




class ToolBase(BaseModel):
    name: str
    description: str
    cost: float
    url: str

class ToolCreate(ToolBase):
    pass 

class Tool(ToolBase):
    id: int
    owner_id: int
    
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
    amount: float
    currency: str
    method: str
    tool_id: int

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    user_id: int
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)