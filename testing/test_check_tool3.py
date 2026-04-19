# testing/check_tool_3.py
import requests

EMAIL = "ans121@gmail.com"
PASSWORD = "Ans@121"

print("=" * 50)
print("CHECKING ACCESS TO BACKGROUND REMOVER PRO (TOOL ID 3)")
print("=" * 50)

# Login
print("\n📝 Logging in...")
login_response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"email": EMAIL, "password": PASSWORD}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.json()}")
    exit()

token = login_response.json()["access_token"]
print(f"✅ Logged in successfully")

# Check subscriptions
print("\n" + "=" * 50)
print("YOUR ACTIVE SUBSCRIPTIONS:")
print("=" * 50)

sub_response = requests.get(
    "http://localhost:8000/api/tools/my-subscriptions",
    headers={"Authorization": f"Bearer {token}"}
)

if sub_response.status_code == 200:
    subs = sub_response.json()
    if subs:
        print(f"✅ You have {len(subs)} active subscription(s):")
        for sub in subs:
            print(f"   🎯 Tool ID: {sub.get('tool_id')}")
            print(f"   📛 Tool Name: {sub.get('tool_name')}")
            print(f"   📅 Plan: {sub.get('plan')}")
            print(f"   ✅ Status: {sub.get('status')}")
            print()
    else:
        print("❌ No active subscriptions found!")
        print("   Did you complete the payment?")
else:
    print(f"Error: {sub_response.status_code}")

# Check access to Tool ID 3 (Background Remover Pro)
print("=" * 50)
print("CHECKING ACCESS TO BACKGROUND REMOVER PRO (TOOL ID 3):")
print("=" * 50)

access_response = requests.get(
    "http://localhost:8000/api/tools/check-access/3",
    headers={"Authorization": f"Bearer {token}"}
)

if access_response.status_code == 200:
    data = access_response.json()
    if data.get("has_access"):
        print(f"✅✅✅ YOU HAVE ACCESS! ✅✅✅")
        print(f"   Tool: {data.get('tool_name')}")
        print(f"   Plan: {data.get('plan')}")
        print(f"   Status: {data.get('status')}")
        print(f"\n🚀 You can now use the tool at:")
        print(f"   http://localhost:8000/tool/background-remover")
    else:
        print(f"❌ No access to Tool ID 3")
        print(f"   Reason: {data.get('message')}")
else:
    print(f"Error: {access_response.status_code}")

# Try the protected endpoint
print("\n" + "=" * 50)
print("TESTING PROTECTED ENDPOINT (TOOL ID 3):")
print("=" * 50)

protected_response = requests.get(
    "http://localhost:8000/api/tools/protected/3",
    headers={"Authorization": f"Bearer {token}"}
)

if protected_response.status_code == 200:
    data = protected_response.json()
    print(f"✅✅✅ PROTECTED ENDPOINT GRANTED ACCESS! ✅✅✅")
    print(f"   Message: {data.get('message')}")
    print(f"   Redirect URL: {data.get('redirect_url')}")
elif protected_response.status_code == 403:
    print(f"❌ Protected endpoint denied access")
    print(f"   Response: {protected_response.json()}")
else:
    print(f"Status: {protected_response.status_code}")