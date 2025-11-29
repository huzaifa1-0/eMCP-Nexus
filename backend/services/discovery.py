import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client


async def discover_tools(mcp_url: str):
    """
    Connects to a live MCP server via SSE and lists available tools.
    """
    sse_endpoint = f"{mcp_url}/sse"

    try:
        async with sse_client(sse_endpoint) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.list_tools()

                return [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputschema": tool.inputschema,
                    }
                    for tool in result.tools
                ]
    except Exception as e:
        print(f"Discovery failed for {mcp_url}: {e}")
        return []