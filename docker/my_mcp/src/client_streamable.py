# client_streamable.py (fixed)
import asyncio
import os
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

#
# To test by bypassing nginx
# podman exec -it mcp bash
# export MCP_BASE_URL=http://localhost:8000/mcp
# python client_streamable.py

base_url = os.getenv("MCP_BASE_URL", "http://localhost:8081/mcp")  # default: talk to Nginx from inside container


async def main():

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
