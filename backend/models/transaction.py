from pydantic import BaseModel
from datetime import datetime


class Transaction(BaseModel):
    id: int
    tool_id: int
    user_id: int
    amount: float
    currency: str
    method: str
    timestamp: datetime