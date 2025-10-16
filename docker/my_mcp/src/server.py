# server.py
from __future__ import annotations
import os
from typing import List, Dict, Any

from mcp.server.fastmcp import FastMCP
import feedparser


mcp = FastMCP("DemoMCP", host="0.0.0.0", port=8000)

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers and return the sum."""
    return a + b


@mcp.tool()
def greet(name: str = "World") -> str:
    """Return a friendly greeting for the given name."""
    return f"Hello, {name}! ✨"


@mcp.tool()
def get_hn_newest(limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch the newest Hacker News posts via hnrss.org/newest.

    Args:
    limit: max number of items to return (default 10)

    Returns:
    A list of dicts with keys: title, link, published, id, comments, author
    """
    feed = feedparser.parse("https://hnrss.org/newest")
    items: List[Dict[str, Any]] = []
    for entry in feed.entries[: max(0, min(limit, 100))]:
        items.append({
            "title": getattr(entry, "title", None),
            "link": getattr(entry, "link", None),
            "published": getattr(entry, "published", None),
            "id": getattr(entry, "id", None),
            "comments": getattr(entry, "comments", None),
            "author": getattr(entry, "author", None),
        })
    return items


if __name__ == "__main__":
#  By default run in stdio for local dev; set MCP_TRANSPORT=http for HTTP mode
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    if transport in {"http", "streamable-http", "streamable_http"}:
        mcp.run(transport="streamable-http")
    else:
        mcp.run() # stdio
