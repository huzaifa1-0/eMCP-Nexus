import numpy as np

def calculate_reputation(transactions: list, ratings: list) -> float:
    """
    Computes reputation score based on payments + user ratings.
    transactions: list of amounts paid
    ratings: list of user ratings [0-5]
    """

    if not ratings:
        return 0.0
    
    avg_rating = np.mean(ratings) / 5.0
    total_volume = np.sum(transactions)

    score = (avg_rating * 0.7) + (min(total_volume / 100.0, 1.0) * 0.3)
    return round(score, 3)

def detect_anomalies(usage_logs: list) -> bool:
    """
    Detects unusual usage patterns (e.g., fraud).
    usage_logs: list of call frequencies
    """
    if not usage_logs:
        return False
    
    mean = np.mean(usage_logs)
    std = np.std(usage_logs)

    return abs(usage_logs[-1] - mean) > 3 * std