import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
import sys

async def discover_tools(mcp_url: str):
    """
    Connects to a live MCP server via SSE and lists available tools.
    """
    # Ensure URL doesn't end with slash before appending /sse
    base_url = mcp_url.rstrip("/")
    sse_endpoint = f"{base_url}/sse"
    
    print(f"🔍 Attempting discovery at: {sse_endpoint}")

    try:
        # 1. PRE-CHECK: Verify the endpoint exists AND is an Event Stream
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                # Use stream=True so we don't download an infinite stream if it works
                async with client.stream("GET", sse_endpoint) as resp:
                    if resp.status_code != 200:
                        print(f"❌ SSE Endpoint returned status {resp.status_code} (Not 200 OK)")
                        return []
                    
                    content_type = resp.headers.get("content-type", "")
                    if "text/event-stream" not in content_type:
                        print(f"❌ Invalid Content-Type: Received '{content_type}', expected 'text/event-stream'.")
                        print("   The server might be sending HTML (e.g., an error page) or JSON instead of SSE.")
                        return []
                        
            except httpx.ConnectError:
                 print(f"❌ Connection Refused: The server at {base_url} is not reachable yet.")
                 return []

        # 2. CONNECT: If pre-check passes, use the MCP client
        async with sse_client(sse_endpoint) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()

                tools_found = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputschema": tool.inputschema,
                    }
                    for tool in result.tools
                ]
                print(f"✅ Discovery successful: Found {len(tools_found)} tools.")
                return tools_found

    except Exception as e:
        # Handle Python 3.11+ ExceptionGroups specifically
        if type(e).__name__ == "ExceptionGroup":
            print(f"❌ Discovery crashed (TaskGroup Error). Sub-errors: {e.exceptions}")
        else:
            print(f"❌ Discovery failed for {mcp_url}: {type(e).__name__} - {e}")
        return []