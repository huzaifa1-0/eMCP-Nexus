# testing/test_subscription_v2.py
import requests
import json

EMAIL = "ans121@gmail.com"
PASSWORD = "Ans@121"

print("=" * 50)
print("STEP 1: Logging in...")
print("=" * 50)

login_response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"email": EMAIL, "password": PASSWORD}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(f"Response: {login_response.text}")
    exit()

token = login_response.json()["access_token"]
print(f"✅ Logged in successfully")

print("\n" + "=" * 50)
print("STEP 2: Checking my subscriptions...")
print("=" * 50)

subscriptions_response = requests.get(
    "http://localhost:8000/api/tools/my-subscriptions",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"Status Code: {subscriptions_response.status_code}")
print(f"Response: {subscriptions_response.text}")

if subscriptions_response.status_code == 200:
    try:
        subscriptions = subscriptions_response.json()
        if subscriptions:
            print(f"✅ You have {len(subscriptions)} active subscription(s):")
            for sub in subscriptions:
                print(f"   - Tool: {sub.get('tool_name', 'Unknown')} ({sub.get('plan', 'N/A')})")
        else:
            print("ℹ️ No active subscriptions yet")
    except:
        print("Could not parse response")

print("\n" + "=" * 50)
print("STEP 3: First, let's see what tools exist...")
print("=" * 50)

tools_response = requests.get("http://localhost:8000/api/tools/")
print(f"Status Code: {tools_response.status_code}")

if tools_response.status_code == 200:
    tools = tools_response.json()
    print(f"✅ Found {len(tools)} tool(s) in database:")
    for tool in tools:
        print(f"   - ID: {tool.get('id')}, Name: {tool.get('name')}, Price: ${tool.get('cost', 0)}")
else:
    print(f"❌ Error: {tools_response.text}")

print("\n" + "=" * 50)
print("STEP 4: Checking access to Tool ID 2...")
print("=" * 50)

access_response = requests.get(
    "http://localhost:8000/api/tools/check-access/2",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"Status Code: {access_response.status_code}")
print(f"Response Text: {access_response.text}")

if access_response.status_code == 200:
    try:
        data = access_response.json()
        if data.get("has_access"):
            print(f"✅ You HAVE access to this tool!")
            print(f"   Plan: {data.get('plan', 'N/A')}")
        else:
            print(f"❌ You do NOT have access to this tool")
            print(f"   Price: ${data.get('price', 'N/A')}/month")
    except:
        print("Could not parse response")
elif access_response.status_code == 404:
    print("❌ Tool ID 2 not found - you need to create the Background Remover tool first!")
    print("   Run: python testing/create_background_remover.py")
else:
    print(f"❌ Error {access_response.status_code}: {access_response.text}")

print("\n" + "=" * 50)
print("STEP 5: Trying protected endpoint...")
print("=" * 50)

protected_response = requests.get(
    "http://localhost:8000/api/tools/protected/2",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"Status Code: {protected_response.status_code}")
print(f"Response: {protected_response.text}")