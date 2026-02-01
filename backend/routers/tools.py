import asyncio
from typing import List
from backend import crud
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from ..models.db import DBTool, DBUser
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

from backend.services.deployment import deploy_tool, get_service_status, fetch_repo_readme
from backend.services.discovery import discover_tools

router = APIRouter()



async def monitor_deployment_and_discover(service_id: str, db_tool_id: int, db_session_factory):
    """
    Polls Render API until service is live, then runs discovery.
    """
    print(f"⏳ Starting monitoring for Service ID: {service_id}")

    async with db_session_factory() as session:
        max_retries = 60

        for i in range(max_retries):
            status = await get_service_status(service_id)
            print(f"   Status check {i+1}: {status}")

            result = await session.execute(select(DBTool).where(DBTool.id == db_tool_id))
            tool = result.scalar_one_or_none()

            if tool:
                tool.status = status
                await session.commit()
            
            if status == "live":
                print(f"🚀 Service is LIVE! Starting discovery on {tool.url}...")

                await asyncio.sleep(10)

                # 1. Fetch README for AI (but don't save to DB)
                readme_text = await fetch_repo_readme(tool.repo_url, tool.branch)

                # 2. Discover Tools
                discovered_tools = await discover_tools(tool.url)
                
                # 3. Prepare Display Description (For UI - keep it relatively short)
                if discovered_tools:
                    tool.tool_definitions = discovered_tools
                    discovered_summaries = [
                        f"{t['name']} ({t.get('description', 'No description')})" 
                        for t in discovered_tools
                    ]
                    # We append discovered capabilities to DB so users see what tools are inside
                    tool.description = f"{tool.description} | Capabilities: {'; '.join(discovered_summaries)}"
                    await session.commit()

                # 4. Prepare Rich Search Context (For Vector DB - Include EVERYTHING)
                # This combines: User Desc + Capabilities + Full README
                search_context = tool.description 
                if readme_text:
                    search_context += f" | README Content: {readme_text}"

                # 5. Index the RICH content, but keep the DB content CLEAN
                await add_tool_to_faiss(tool.id, tool.name, search_context)
                
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


@router.post("/use/{tool_id}", tags=["Tools"])
async def use_tool(
    tool_id: int, 
    background_tasks: BackgroundTasks,
    user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Simulates a user using a tool, and logs its performance."""
    
    
    tool = await get_tool(tool_id, session)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

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


