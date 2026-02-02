import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client


async def discover_tools(mcp_url: str):
    """
    Connects to a live MCP server via SSE and lists available tools.
    """
    # Ensure URL doesn't end with slash before appending /sse
    base_url = mcp_url.rstrip("/")
    sse_endpoint = f"{base_url}/sse"
    
    print(f"🔍 Attempting discovery at: {sse_endpoint}")

    try:
        # Check if URL is reachable first to avoid TaskGroup crash
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(sse_endpoint)
            if resp.status_code == 404:
                print(f"❌ SSE Endpoint not found (404) at {sse_endpoint}")
                return []

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

    except httpx.ConnectError:
        print(f"❌ Connection Refused: The server at {mcp_url} is not accepting connections yet.")
    except Exception as e:
        print(f"❌ Discovery failed for {mcp_url}: {type(e).__name__} - {e}")
        return []