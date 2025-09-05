from fastapi import APIRouter
from ai_services import reputation
from pydantic import BaseModel
from typing import List

router = APIRouter()

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
