# client_streamable.py (fixed)
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    base_url = "http://localhost:8081/mcp"  # or http://localhost:8000/mcp if bypassing Nginx

    async with streamablehttp_client(base_url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("TOOLS:", [t.name for t in tools.tools])

            result = await session.call_tool("add", {"a": 2, "b": 3})
            print("add(2,3) ->", result.content[0].text if result.content else result)

            result = await session.call_tool("greet", {"name": "MCP"})
            print("greet('MCP') ->", result.content[0].text if result.content else result)

            result = await session.call_tool("get_hn_newest", {"limit": 5})
            print("get_hn_newest(5) ->", result.content[0].text if result.content else result)

if __name__ == "__main__":
    asyncio.run(main())
