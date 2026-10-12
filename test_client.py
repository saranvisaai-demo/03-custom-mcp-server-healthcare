"""
test_client.py — Quick manual test client for the Healthcare MCP Server
--------------------------------------------------------------------------
Connects to a running server.py instance over Streamable HTTP, lists the
registered tools, and calls database_schema() to confirm the server
responds correctly.

Usage:
    1. In one terminal: python server.py
    2. In another:      python test_client.py
"""

import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

SERVER_URL = "http://localhost:8000/mcp"


async def main():
    async with streamablehttp_client(SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Tools:", [t.name for t in tools.tools])

            result = await session.call_tool("database_schema", {})
            print("database_schema result:", result)


if __name__ == "__main__":
    asyncio.run(main())
