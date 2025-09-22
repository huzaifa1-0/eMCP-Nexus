from typing import Dict

def get_dynamic_price(base_price: float,tool_id: int, reputation_score: float, usage_stats: Dict) -> float:
    """
    Calculates a dynamic price for a tool based on its reputation and usage.
    """

    # Adjust price based on reputation (higher reputation can command a higher price)
    reputation_multiplier = 1 + (reputation_score * 0.5) # Up to 50% increase for top reputation

    # Adjust price based on demand (higher recent usage could increase the price)
    recent_usage = len(usage_stats.get(tool_id, [])) # Simplified: count all logs
    demand_multiplier = 1 + min(recent_usage / 1000.0, 0.5) # Up to 50% increase for high demand

    dynamic_price = base_price * reputation_multiplier * demand_multiplier

    return round(dynamic_price, 2)

def get_subscription_plans(tool_id: int) -> Dict:
    """
    Returns available subscription plans for a tool.
    This can be expanded to fetch from a database.
    """
    return {
        "basic": {"price": 19.99, "requests": 1000},
        "pro": {"price": 49.99, "requests": 5000},
        "enterprise": {"price": 99.99, "requests": "unlimited"}
    }