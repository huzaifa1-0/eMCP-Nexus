import stripe
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from backend.config import settings
from backend.db import get_async_session
from backend.security import get_current_user
from backend.models.db import DBUser, DBTool, DBSubscription

router = APIRouter()

# Set Stripe API key (from your .env)
stripe.api_key = settings.STRIPE_KEY

# !!! IMPORTANT: Replace these with YOUR actual Stripe Price IDs !!!
# Go to Stripe Dashboard → Products → Copy Price IDs
PLAN_PRICES = {
    "monthly": "price_1TMrre2E22cgamZQr73xSIho",  # ← CHANGE THIS  
    
}

# Pydantic model for request validation
class CheckoutRequest(BaseModel):
    tool_id: int
    plan: str  # weekly, monthly, yearly

# ENDPOINT 1: Create checkout session (called from frontend)
@router.post("/create-checkout-session")
async def create_checkout_session(
    req: CheckoutRequest,
    session: AsyncSession = Depends(get_async_session),
    user: DBUser = Depends(get_current_user),
):
    """
    This endpoint:
    1. Validates the request (tool exists, plan is valid)
    2. Creates a Stripe Checkout Session
    3. Saves a "pending" subscription in your database
    4. Returns the Stripe checkout URL to redirect the user
    """
    
    # Step 1: Validate the plan
    if req.plan not in PLAN_PRICES:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    # Step 2: Find the tool
    result = await session.execute(select(DBTool).where(DBTool.id == req.tool_id))
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    try:
        # Step 3: Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],  # Accept credit/debit cards
            mode="subscription",  # Recurring payment, not one-time
            line_items=[{
                "price": PLAN_PRICES[req.plan],  # Which price (weekly/monthly/yearly)
                "quantity": 1,
            }],
            # Where to send user after payment
            success_url=f"{settings.FRONTEND_URL}/marketplace?payment=success&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/marketplace?payment=cancelled",
            # Store custom data to identify this subscription
            metadata={
                "user_id": str(user.id),
                "tool_id": str(req.tool_id),
                "plan": req.plan,
            },
            client_reference_id=str(user.id),
        )
        
        # Step 4: Save to your database (status = pending)
        subscription = DBSubscription(
            user_id=user.id,
            tool_id=req.tool_id,
            stripe_session_id=checkout_session.id,  # Link to Stripe session
            plan=req.plan,
            status="pending"  # Not active until payment confirmed
        )
        session.add(subscription)
        await session.commit()
        
        # Step 5: Return the URL for frontend to redirect
        return {"checkout_url": checkout_session.url}
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ENDPOINT 2: Webhook - Stripe calls THIS when payment completes
@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Stripe calls this endpoint automatically after payment.
    This is CRITICAL - it's how you know payment succeeded.
    """
    
    # Get the raw request body
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    # Verify this webhook actually came from Stripe (security)
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        # If verification fails, reject the webhook
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    
    # Handle different event types
    if event["type"] == "checkout.session.completed":
        # Payment succeeded!
        session_obj = event["data"]["object"]
        session_id = session_obj["id"]
        stripe_sub_id = session_obj.get("subscription")
        
        # Find the pending subscription in your database
        result = await session.execute(
            select(DBSubscription).where(DBSubscription.stripe_session_id == session_id)
        )
        sub = result.scalar_one_or_none()
        
        if sub:
            # Mark as active
            sub.status = "active"
            sub.stripe_subscription_id = stripe_sub_id
            await session.commit()
            print(f"✅ Subscription activated for user {sub.user_id}")
    
    elif event["type"] == "customer.subscription.deleted":
        # User cancelled their subscription
        subscription_obj = event["data"]["object"]
        stripe_sub_id = subscription_obj["id"]
        
        result = await session.execute(
            select(DBSubscription).where(DBSubscription.stripe_subscription_id == stripe_sub_id)
        )
        sub = result.scalar_one_or_none()
        if sub:
            sub.status = "cancelled"
            await session.commit()
            print(f"❌ Subscription cancelled for user {sub.user_id}")
    
    return {"status": "ok"}

# ENDPOINT 3: Get user's active subscriptions
@router.get("/my-subscriptions")
async def get_my_subscriptions(
    session: AsyncSession = Depends(get_async_session),
    user: DBUser = Depends(get_current_user),
):
    """Returns all active subscriptions for the logged-in user"""
    result = await session.execute(
        select(DBSubscription).where(
            DBSubscription.user_id == user.id,
            DBSubscription.status == "active"
        )
    )
    subs = result.scalars().all()
    return [
        {
            "id": s.id,
            "tool_id": s.tool_id,
            "plan": s.plan,
            "status": s.status,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in subs
    ]