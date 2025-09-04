from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..services import payments

router = APIRouter()

class PaymentRequest(BaseModel):
    tool_id: int
    user_id: int
    amount: float
    currency: str = "USD"
    method: str = "crypto" or "stripe"
