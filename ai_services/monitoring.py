from collections import defaultdict
import datetime

usage_stats = defaultdict(list)


def log_tool_usage(tool_id: int, user_id: int, success: bool, processing_time: float):
    """
    Records usage events for analytics.
    """
    usage_stats[tool_id].append({
        "user_id": user_id,
        "timestamp": datetime.datetime.utcnow().isoformat()
        "success": success,
        "processing_time": processing_time
    })


def get_tool_usage(tool_id: int):
    """
    Returns usage history for a given tool.
    """
    return usage_stats.get(tool_id, [])