from fastapi import APIRouter
from backend.ai_services import reputation
from pydantic import BaseModel
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.ai_services.monitoring import get_tool_usage
from backend.db import get_async_session
from backend.models.db import DBTransaction, DBRating
from backend.models.pydantic import BaseModel

router = APIRouter()


class ReputationResponse(BaseModel):
    tool_id: int
    reputation_score: float
class ReputationRequest(BaseModel):
    transactions: List[float]
    ratings: List[int]

class AnomalyRequest(BaseModel):
    usage_logs: List[int]


@router.post("/calculate")
async def calculate_reputation(request: ReputationRequest) -> dict:
    """
    Calculate reputation score based on payments + ratings.
    """
    score = reputation.calculate_reputation(request.transactions, request.ratings)
    return {"reputation_score": score}


@router.post("/anomalies")
async def detect_anomalies(request: AnomalyRequest) -> dict:
    """
    Detect anomalies in usage logs.
    """
    is_anomaly = reputation.detect_anomalies(request.usage_logs)
    return {"anomaly_detected": is_anomaly}

@router.get("/{tool_id}", response_model=ReputationResponse)
async def get_tool_reputation(tool_id: int, session: AsyncSession = Depends(get_async_session)):
    """Computes and returns the reputation score for a tool."""
    
    # Fetch data from the database
    txs_result = await session.execute(select(DBTransaction.amount).where(DBTransaction.tool_id == tool_id))
    txs = [row[0] for row in txs_result.all()]
    
    ratings_result = await session.execute(select(DBRating.rating).where(DBRating.tool_id == tool_id))
    ratings = [row[0] for row in ratings_result.all()]
    
    usage_logs = await get_tool_usage(session, tool_id)
    
    # Calculate performance metrics
    if usage_logs:
        total_runs = len(usage_logs)
        successful_runs = sum(1 for log in usage_logs if log.success)
        success_rate = successful_runs / total_runs if total_runs > 0 else 0.0
        
        total_time = sum(log.processing_time for log in usage_logs)
        avg_processing_time = total_time / total_runs if total_runs > 0 else 0.0
    else:
        success_rate = 0.0
        avg_processing_time = 0.0

    # Calculate the final score
    score = reputation.calculate_reputation(
        transactions=txs, 
        ratings=ratings,
        usage_logs=usage_logs,
        success_rate=success_rate,
        avg_processing_time=avg_processing_time
    )
    
    return {"tool_id": tool_id, "reputation_score": score}