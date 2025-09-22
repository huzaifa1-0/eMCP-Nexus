import numpy as np

def calculate_reputation(
        transactions: list,
        ratings: list,
        usage_logs: list,
        success_rate: float,
        avg_processing_time: float
) -> float:
    """
    Computes reputation score.
    """

    if not ratings and not transactions:
        return 0.0
    
    avg_rating_normalized = np.mean(ratings) / 5.0 if ratings else 0
    total_volume_normalized = min(np.sum(transactions) / 1000.0 , 1.0) if transactions else 0
    usage_frequency_normalized = min(len(usage_logs) / 10000.0, 1.0) if usage_logs else 0

    weights = {
        "rating": 0.4,
        "volume": 0.2,
        "usage": 0.1,
        "success": 0.2,
        "speed": 0.1
    }

    score = (
        avg_rating_normalized * weights["rating"] +
        total_volume_normalized * weights["volume"] +
        usage_frequency_normalized * weights["usage"] +
        success_rate * weights["success"] +
        (1 - min(avg_processing_time / 10.0, 1.0)) * weights["speed"] # Lower processing time is better
    )

    return round(score, 3)

def detect_anomalies(usage_logs: list) -> bool:
    """
    Detects unusual usage patterns (e.g., fraud).
    usage_logs: list of call frequencies
    """
    if not usage_logs or len(usage_logs) < 2:
        return False
    
    mean = np.mean(usage_logs)
    std = np.std(usage_logs)

    if std == 0:
        return False
    
    last_usage = usage_logs[-1]
    z_score = abs(last_usage - mean) / std

    return z_score > 3