from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import uuid

from backend.db import get_async_session
from backend.models.db import DBTool, DBSubscription, DBUser
from backend.services.crypto import verify_payment
from backend.config import settings
from backend.security import get_current_user

router = APIRouter()

class UnlockRequest(BaseModel):
    tool_id: int
    tx_hash: str

@router.post("/unlock")
async def unlock_tool_with_web3(
    request: UnlockRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: DBUser = Depends(get_current_user)
):
    # 1. Get the tool to find its cost
    result = await session.execute(select(DBTool).where(DBTool.id == request.tool_id))
    tool = result.scalar_one_or_none()
    
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
        
    if tool.cost <= 0:
        raise HTTPException(status_code=400, detail="This tool is free, no payment needed.")
        
    # 2. Check if user already has an active subscription to this tool
    sub_result = await session.execute(
        select(DBSubscription).where(
            DBSubscription.tool_id == request.tool_id,
            DBSubscription.user_id == current_user.id,
            DBSubscription.status == "active"
        )
    )
    existing_sub = sub_result.scalar_one_or_none()
    if existing_sub:
        return {
            "message": "Tool already unlocked", 
            "api_key": current_user.api_key
        }
        
    # 3. Verify the transaction
    is_valid = verify_payment(
        request.tx_hash, 
        tool.cost, 
        settings.RECEIVER_WALLET_ADDRESS
    )
    
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or insufficient Web3 transaction.")
        
    # 4. Create the subscription (Unlock)
    new_sub = DBSubscription(
        user_id=current_user.id,
        tool_id=request.tool_id,
        plan="lifetime", # One-time unlock for Web3 in this implementation
        status="active"
    )
    session.add(new_sub)
    
    # 5. Ensure the user has an API Key
    if not current_user.api_key:
        current_user.api_key = f"emcp_{uuid.uuid4().hex}"
        
    await session.commit()
    
    return {
        "message": "Tool successfully unlocked!",
        "api_key": current_user.api_key
    }
