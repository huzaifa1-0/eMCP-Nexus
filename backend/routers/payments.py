from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.models.pydantic import RatingBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..services import payments
from ai_services.monitoring import log_tool_usage
from backend.services.logging import log_event
from ai_services.reputation import calculate_reputation
from backend.db import get_async_session
from backend.models.db import DBTransaction, DBRating, DBUser
from backend.security import get_current_active_user
import random 
import time
from ai_services.monitoring import get_tool_usage

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
        # Simulate the tool running and getting performance data
        start_time = time.time()
        # In a real app, you'd get this from the tool's execution result
        success = random.choice([True, False]) 
        processing_time = time.time() - start_time
        tx = await payments.handle_payment(request)
        log_tool_usage(
            tool_id=request.tool_id, 
            user_id=request.user_id,
            success=success,
            processing_time=processing_time
        )
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
        log_event(f"Payment processed for tool {request.tool_id} by user {request.user_id}")
        return {"status": "success", "transaction": tx}
    except Exception as e:
        await session.rollback()
        log_event(f"Payment failed for tool {request.tool_id} by user {request.user_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Payment failed: {str(e)}")

@router.post("/rate/{tool_id}")
async def rate_tool(
    tool_id: int,
    rating_req: RatingBase,
    session: AsyncSession = Depends(get_async_session),
    user: DBUser = Depends(get_current_active_user)
) -> dict:
    """
    Allows users to rate tools (0-5). Requires authentication.
    """
    db_rating = DBRating(
        rating=rating_req.rating,
        tool_id=tool_id,
        user_id=user.id
    )
    try:
        session.add(db_rating)
        await session.commit()
        await session.refresh(db_rating)
        log_event(f"User {user.id} rated tool {tool_id} with {rating_req.rating}")
        return {"status": "success", "tool_id": tool_id, "rating": rating_req.rating}
    except Exception as e:
        await session.rollback()
        log_event(f"Rating failed for tool {tool_id} by user {user.id}: {str(e)}")
        if "unique_tool_user_rating" in str(e):
            raise HTTPException(status_code=400, detail="You have already rated this tool.")
        raise HTTPException(status_code=400, detail=f"Rating failed: {str(e)}")

