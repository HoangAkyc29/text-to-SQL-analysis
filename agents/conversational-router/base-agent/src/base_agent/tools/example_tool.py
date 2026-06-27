"""Example native Strands tool — replace with domain-specific tools."""

from __future__ import annotations

from strands import tool


@tool
def example_tool(note: str = "") -> dict:
    """
    TODO: implement a native tool (not MCP) if your agent needs one.
    Example: finalize_strategy, lock_params, submit_review, …
    """
    return {"status": "todo", "note": note or "Implement example_tool"}
