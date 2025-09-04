from datetime import datetime
from ..models.transaction import Transaction

async def handle_payment(request) -> dict:
    """
    Simulates payment processing (crypto / stripe).
    """

    tx = Transaction(
        id=1,
        tool_id=request.tool_id,
        user_id=request.user_id,
        amount=request.amount,
        currency=request.currency,
        method=request.method,
        timestamp=datetime.utcnow()
    )

    return tx.dict()