from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..services import payments
from ai_services.monitoring import log_tool_usage
from ai_services.reputation import calculate_reputation

router = APIRouter()


transactions_db = {}
ratings_db = {}

class PaymentRequest(BaseModel):
    tool_id: int
    user_id: int
    amount: float
    currency: str = "USD"
    method: str = "crypto" or "stripe"


class ReputationResponse(BaseModel):
    tool_id: int
    reputation_score: float


@router.post("/pay")
async def process_payment(request: PaymentRequest):
    try:
        tx = await payments.handle_payment(request)
        log_tool_usage(tool_id=request.tool_id, user_id=request.user_id)
        transactions_db.setdefault(request.tool_id, []).append(request.amount)
        return {"status": "success", "transaction": tx}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/rate/{tool_id}")
async def rate_tool(tool_id: int, rating: int):
    """
    Allows users to rate tools (0-5).
    """
    if rating < 0 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 0 and 5")
    
    ratings_db.setdefault(tool_id, []).append(rating)
    return {"status": "success", "tool_id": tool_id, "rating": rating}



@router.get("/reputation/{tool_id}", response_model=ReputationResponse)
async def get_reputation(tool_id: int):
    """
    Computes reputation score from payments + ratings.
    """
    txs = transactions_db.get(tool_id, [])
    ratings = ratings_db.get(tool_id, [])
    score = calculate_reputation(txs, ratings)
    return {"tool_id": tool_id, "reputation_score": score}