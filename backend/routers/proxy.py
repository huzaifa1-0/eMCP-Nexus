import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db import get_async_session
from backend.models.db import DBTool
from backend.services.crypto import verify_payment
from backend.config import settings
from starlette.background import BackgroundTask

router = APIRouter()

async def get_target_tool_url(tool_id: int, session: AsyncSession) -> str:
    """Helper: Get the real URL (Render) from the DB."""
    result = await session.execute(select(DBTool).where(DBTool.id == tool_id))
    tool = result.scalar_one_or_none()
    if not tool or not tool.url:
        raise HTTPException(status_code=404, detail="Tool not found or inactive")
    return tool.url.rstrip("/")

@router.get("/{tool_id}/sse")
async def proxy_sse_handshake(
    tool_id: int, 
    request: Request, 
    session: AsyncSession = Depends(get_async_session)
):
    """
    1. Connection Handshake
    We allow the connection to open for free so the client can discover tools.
    """
    target_base = await get_target_tool_url(tool_id, session)
    target_url = f"{target_base}/sse"

    client = httpx.AsyncClient()
    # Forward the connection request to the real tool
    req = client.build_request("GET", target_url, headers=request.headers, timeout=None)
    r = await client.send(req, stream=True)
    
    return StreamingResponse(
        r.aiter_raw(),
        status_code=r.status_code,
        headers=dict(r.headers),
        background=BackgroundTask(client.aclose)
    )

@router.post("/{tool_id}/messages")
async def proxy_messages(
    tool_id: int, 
    request: Request, 
    session: AsyncSession = Depends(get_async_session)
):
    """
    2. Message Interception (YOUR TASK)
    This is where we charge per request.
    """
    # Get tool details
    result = await session.execute(select(DBTool).where(DBTool.id == tool_id))
    tool = result.scalar_one_or_none()
    if not tool or not tool.url:
        raise HTTPException(status_code=404, detail="Tool not found")

    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # === PAYMENT LOGIC ===
    # We only charge when they actually 'call' a tool, not when they just list them.
    if body.get("method") == "tools/call" and tool.cost > 0:
        
        




        
        tx_hash = request.headers.get("x-transaction-hash")
        
        # 1. No Payment Proof? -> Stop them with 402
        if not tx_hash:
            raise HTTPException(
                status_code=402, # Payment Required
                detail={
                    "error": "Payment Required",
                    "amount": tool.cost,
                    "currency": "ETH",
                    "receiver": settings.RECEIVER_WALLET_ADDRESS,
                    "message": "Please sign the transaction in your MCP Client."
                }
            )
        
        # 2. Verify the Payment
        is_valid = verify_payment(tx_hash, tool.cost, settings.RECEIVER_WALLET_ADDRESS)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid Crypto Transaction")

    # === FORWARDING ===
    # If payment is valid (or tool is free), forward to the real tool
    target_url = f"{tool.url.rstrip('/')}/messages"
    
    async with httpx.AsyncClient() as client:
        proxy_req = client.build_request(
            "POST", 
            target_url, 
            json=body, 
            headers=request.headers,
            timeout=60.0
        )
        response = await client.send(proxy_req)
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )