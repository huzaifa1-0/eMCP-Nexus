# testing/test_stripe_payment.py
import requests

EMAIL = "ans121@gmail.com"
PASSWORD = "Ans@121"  # Replace with your actual password

# Login
login_response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"email": EMAIL, "password": PASSWORD}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.json()}")
    exit()

token = login_response.json()["access_token"]
print("✅ Logged in")

# Create Stripe checkout session for Tool ID 2
checkout_response = requests.post(
    "http://localhost:8000/api/stripe/create-checkout-session",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    json={
        "tool_id": 2,  # ← USING TOOL ID 2
        "plan": "monthly"
    }
)

if checkout_response.status_code != 200:
    print(f"❌ Error: {checkout_response.json()}")
    exit()

checkout_url = checkout_response.json()["checkout_url"]
print(f"\n🔗 Go to this URL to test payment:")
print(f"{checkout_url}")
print("\n💳 Use test card: 4242 4242 4242 4242")