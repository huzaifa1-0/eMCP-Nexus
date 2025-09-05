from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..services import payments
from ai_services.monitoring import log_tool_usage
from ai_services.reputation import calculate_reputation
from backend.db import get_async_session
from backend.models.db import DBTransaction, DBRating, DBUser
from backend.security import get_current_active_user

router = APIRouter()

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
async def process_payment(
    request: PaymentRequest, 
    session: AsyncSession = Depends(get_async_session)
) -> dict:
    try:
        tx = await payments.handle_payment(request)
        log_tool_usage(tool_id=request.tool_id, user_id=request.user_id)
        db_tx = DBTransaction(
            amount=request.amount,
            currency=request.currency,
            method=request.method,
            tool_id=request.tool_id,
            user_id=request.user_id
        )
        session.add(db_tx)
        await session.commit()
        await session.refresh(db_tx)
        return {"status": "success", "transaction": tx}
    except Exception as e:
        await session.rollback()
        # Optionally log the error here
        raise HTTPException(status_code=400, detail=f"Payment failed: {str(e)}")

@router.post("/rate/{tool_id}")
async def rate_tool(
    tool_id: int,
    rating: int,
    session: AsyncSession = Depends(get_async_session),
    user: DBUser = Depends(get_current_active_user)
) -> dict:
    """
    Allows users to rate tools (0-5). Requires authentication.
    """
    if rating < 0 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 0 and 5")
    db_rating = DBRating(
        rating=rating,
        tool_id=tool_id,
        user_id=user.id
    )
    try:
        session.add(db_rating)
        await session.commit()
        await session.refresh(db_rating)
        return {"status": "success", "tool_id": tool_id, "rating": rating}
    except Exception as e:
        await session.rollback()
        # Optionally log the error here
        raise HTTPException(status_code=400, detail=f"Rating failed: {str(e)}")

@router.get("/reputation/{tool_id}", response_model=ReputationResponse)
async def get_reputation(tool_id: int, session: AsyncSession = Depends(get_async_session)) -> dict:
    """
    Computes reputation score from payments + ratings.
    """
    # Get all transactions for this tool
    txs_result = await session.execute(select(DBTransaction.amount).where(DBTransaction.tool_id == tool_id))
    txs = [row[0] for row in txs_result.all()]
    # Get all ratings for this tool
    ratings_result = await session.execute(select(DBRating.rating).where(DBRating.tool_id == tool_id))
    ratings = [row[0] for row in ratings_result.all()]
    score = calculate_reputation(txs, ratings)
    return {"tool_id": tool_id, "reputation_score": score}