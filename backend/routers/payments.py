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


@router.post("/pay")
async def process_payment(request: PaymentRequest):
    try:
        tx = await payments.handle_payment(request)
        return {"status": "success", "transaction": tx}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))