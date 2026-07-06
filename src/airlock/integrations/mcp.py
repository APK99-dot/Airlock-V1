"""MCP proxy: put an airlock in front of any MCP server.

MCP is how agents call tools in 2026 — a production stack runs 5-9 servers at
once, each exposing tools the agent can invoke autonomously. That is exactly the
boundary where a rogue action becomes a rogue *outcome*.

AirlockMCPProxy sits between the agent and a downstream MCP server: it forwards
``tools/list`` untouched, but every ``tools/call`` is evaluated by the policy
first. Blocked calls never reach the real server; they return a structured MCP
error the agent can reason about ("this was blocked because ...").

This module is a framework-agnostic reference implementation over the MCP
JSON-RPC envelope. Wire ``handle_tool_call`` into your transport of choice
(stdio, SSE, streamable-HTTP) — see docs/architecture.md.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from ..core import Airlock
from ..decisions import BlockedActionError

# A downstream caller: given (tool_name, arguments) actually invokes the real
# MCP server and returns its result payload.
DownstreamCall = Callable[[str, dict[str, Any]], Awaitable[Any]]


class AirlockMCPProxy:
    def __init__(self, airlock: Airlock, downstream: DownstreamCall, namespace: str = "") -> None:
        self.airlock = airlock
        self.downstream = downstream
        # Optional prefix so policies can target a specific server, e.g. "github."
        self.namespace = namespace

    async def handle_tool_call(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Evaluate then (maybe) forward an MCP tools/call. Returns an MCP result."""
        action = f"{self.namespace}{tool_name}" if self.namespace else tool_name
        try:
            self.airlock.enforce(action, arguments or {})
        except BlockedActionError as exc:
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"[AIRLOCK BLOCKED] Tool '{tool_name}' was not executed. "
                            f"Reason: {exc.verdict.reason}"
                        ),
                    }
                ],
                "_airlock": exc.verdict.to_dict(),
            }
        result = await self.downstream(tool_name, arguments)
        return result
