import asyncio
from typing import List
from backend import crud
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Header
from ..models.db import DBTool, DBUser, DBSubscription  # ← ADDED DBSubscription
from ..models.pydantic import ToolCreate, Tool
from ..security import get_current_user
from ..db import get_async_session
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.ai_services.search_engine import add_tool_to_faiss
from backend.ai_services.monitoring import log_tool_usage
import random 
import time
from backend.middleware.subscription_check import check_subscription_access, get_user_subscriptions
from backend.config import settings
from backend.services.crypto import verify_payment

from backend.services.deployment import deploy_tool, get_service_status, fetch_repo_readme
from backend.services.discovery import discover_tools

router = APIRouter()



async def monitor_deployment_and_discover(service_id: str, db_tool_id: int, db_session_factory):
    """
    Polls Render API until service is live, then runs discovery.
    Refactored to avoid holding DB sessions open during network calls.
    """
    print(f"⏳ Starting monitoring for Service ID: {service_id}")

    max_retries = 60
    # Store these variables to use outside the DB session
    tool_url = None
    tool_name = ""
    repo_url = ""
    branch = ""

    for i in range(max_retries):
        # 1. Check Status (Network Call)
        status = await get_service_status(service_id)
        print(f"   Status check {i+1}: {status}")

        # 2. Update Status in DB (Short-lived Session)
        async with db_session_factory() as session:
            result = await session.execute(select(DBTool).where(DBTool.id == db_tool_id))
            tool = result.scalar_one_or_none()
            
            if tool:
                tool.status = status
                await session.commit()
                # Cache info for the discovery phase
                tool_url = tool.url
                tool_name = tool.name
                repo_url = tool.repo_url
                branch = tool.branch

        if status == "live" and tool_url:
            print(f"🚀 Service is LIVE! Waiting 20s for server warmup at {tool_url}...")
            
            # CRITICAL FIX: Wait for the app inside the container to actually boot
            await asyncio.sleep(20)

            # 3. Network Discovery (NO DB SESSION HERE)
            readme_text = await fetch_repo_readme(repo_url, branch)
            discovered_tools = await discover_tools(tool_url)
            
            search_context = ""

            # 4. Save Discovery Results (New Short-lived Session)
            final_description = tool_name # Fallback
            async with db_session_factory() as session:
                result = await session.execute(select(DBTool).where(DBTool.id == db_tool_id))
                tool = result.scalar_one_or_none()
                
                if tool:
                    tool.readme = readme_text
                    if discovered_tools:
                        tool.tool_definitions = discovered_tools
                        summaries = [f"{t['name']} ({t.get('description', 'No desc')})" for t in discovered_tools]
                        tool.description = f"{tool.description} | Capabilities: {'; '.join(summaries)}"
                    await session.commit()
                    final_description = tool.description

            # 5. Update Vector DB (In-memory operation)
            await add_tool_to_faiss(db_tool_id, tool_name, final_description, readme_text)
            break
        
        await asyncio.sleep(5)

@router.get("/", response_model=List[Tool])
async def read_tools(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_async_session)
):
    """Get a list of all available tools from the database."""
    tools = await crud.get_tools(session, skip=skip, limit=limit)
    return tools

async def get_tool(tool_id: int, session: AsyncSession):
    result = await session.execute(select(DBTool).where(DBTool.id == tool_id))
    return result.scalar_one_or_none()



@router.post("/", response_model=Tool)
async def create_tool(
    tool_data: ToolCreate,
    background_tasks: BackgroundTasks, 
    user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> DBTool:
    # 🚀 REAL MODE: Deploy to Render
    deployment_info = await deploy_tool(
        repo_url=tool_data.repo_url,
        branch=tool_data.branch,
        build_command=tool_data.build_command,
        start_command=tool_data.start_command,
        root_dir=tool_data.root_dir,
        env_vars=tool_data.env_vars
    )
    
    

    service_id = deployment_info.get("serviceId", "unknown")

    db_tool = DBTool(
        name = tool_data.name,
        description = tool_data.description,
        cost = tool_data.cost,
        repo_url = tool_data.repo_url,
        branch = tool_data.branch,
        build_command = tool_data.build_command,
        start_command = tool_data.start_command,
        root_dir = tool_data.root_dir,
        url = deployment_info["url"],
        deploy_id = service_id,
        owner_id = user.id,
        status = "deploying"
    )
    session.add(db_tool)
    await session.commit()
    await session.refresh(db_tool)


    from backend.db import async_session_factory
    background_tasks.add_task(
        monitor_deployment_and_discover,
        service_id,
        db_tool.id,
        async_session_factory
    )
    
    
    return db_tool


# ============ PROTECTED ENDPOINTS FOR SUBSCRIPTIONS ============

@router.get("/protected/{tool_id}")
async def access_protected_tool(
    tool_id: int,
    subscription = Depends(check_subscription_access),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Protected endpoint that only users with active subscription can access.
    Returns tool details and grants access to the paid tool.
    """
    # Get tool details
    result = await session.execute(select(DBTool).where(DBTool.id == tool_id))
    tool = result.scalar_one_or_none()
    
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return {
        "access_granted": True,
        "tool_id": tool.id,
        "tool_name": tool.name,
        "tool_description": tool.description,
        "message": f"You have access to {tool.name}",
        "redirect_url": tool.url
    }


@router.get("/my-subscriptions")
async def my_subscriptions(
    subscriptions = Depends(get_user_subscriptions)
):
    """
    Get all active subscriptions for the logged-in user.
    Returns list of tools the user has subscribed to.
    """
    return subscriptions


@router.get("/check-access/{tool_id}")
async def check_tool_access(
    tool_id: int,
    user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Check if current user has access to a specific tool.
    Returns access status without blocking.
    """
    try:
        # First, check if tool exists
        tool_result = await session.execute(select(DBTool).where(DBTool.id == tool_id))
        tool = tool_result.scalar_one_or_none()
        
        if not tool:
            return {
                "has_access": False,
                "tool_exists": False,
                "message": "Tool not found"
            }
        
        # Check for active subscription
        sub_result = await session.execute(
            select(DBSubscription).where(
                DBSubscription.user_id == user.id,
                DBSubscription.tool_id == tool_id,
                DBSubscription.status == "active"
            )
        )
        subscription = sub_result.scalar_one_or_none()
        
        if subscription:
            return {
                "has_access": True,
                "tool_exists": True,
                "tool_id": tool.id,
                "tool_name": tool.name,
                "plan": subscription.plan,
                "status": subscription.status,
                "message": "You have an active subscription"
            }
        else:
            return {
                "has_access": False,
                "tool_exists": True,
                "tool_id": tool.id,
                "tool_name": tool.name,
                "requires_payment": True,
                "price": tool.cost,
                "currency": "USD",
                "message": f"Subscription required. ${tool.cost}/month"
            }
    except Exception as e:
        print(f"Error in check_access: {e}")
        return {
            "has_access": False,
            "error": str(e),
            "message": "Error checking access"
        }


# ============ EXISTING USE TOOL ENDPOINT ============

@router.post("/use/{tool_id}", tags=["Tools"])
async def use_tool(
    tool_id: int, 
    background_tasks: BackgroundTasks,
    x_transaction_hash: str = Header(None),
    user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Simulates a user using a tool, and logs its performance."""
    
    
    tool = await get_tool(tool_id, session)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    if tool.cost > 0:
        # A. If no payment proof provided
        if not x_transaction_hash:
            raise HTTPException(
                status_code=402, # Payment Required
                detail={
                    "message": "Payment required",
                    "amount": tool.cost,
                    "currency": "ETH",
                    "receiver": settings.RECEIVER_WALLET_ADDRESS
                }
            )
        
        # B. Verify the provided hash
        is_valid = verify_payment(
            tx_hash=x_transaction_hash,
            required_amount=tool.cost,
            receiver_address=settings.RECEIVER_WALLET_ADDRESS
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid payment transaction")

        

    # 1. Simulate the tool's execution
    start_time = time.time()
    # In a real-world scenario, you would call the tool's actual API here
    success = random.choice([True, False]) # Placeholder for actual success status
    processing_time = time.time() - start_time

    # 2. Log the performance in the background
    background_tasks.add_task(
        log_tool_usage,
        db=session,
        tool_id=tool_id,
        user_id=user.id,
        success=success,
        processing_time=processing_time
    )
    
    return {
        "status": "success" if success else "failure",
        "message": f"Tool {tool.name} executed.",
        "processing_time": round(processing_time, 3),
        "result": "Sample output data from tool..."
    }