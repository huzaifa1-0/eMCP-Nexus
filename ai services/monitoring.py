from collections import defaultdict
import datetime

usage_stats = defaultdict(list)


def log_tool_usage(tool_id: int, user_id: int):
    """
    Records usage events for analytics.
    """
    usage_stats[tool_id].append({
        "user_id": user_id,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })