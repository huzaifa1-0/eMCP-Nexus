from collections import defaultdict
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.db import DBUsageLog

usage_stats = defaultdict(list)


async def log_tool_usage(db: AsyncSession, tool_id: int, user_id: int, success: bool, processing_time: float):
    """
    Records usage events for analytics.
    """
    db_log = DBUsageLog(
        tool_id=tool_id,
        user_id=user_id,
        success=success,
        processing_time=processing_time
    )
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log


async def get_tool_usage(db: AsyncSession, tool_id: int) -> list:
    """Returns usage history for a given tool from the database."""
    result = await db.execute(
        select(DBUsageLog).where(DBUsageLog.tool_id == tool_id)
    )
    return result.scalars().all()