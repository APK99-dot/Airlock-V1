"""LangChain / LangGraph integration.

LangChain remains the most-adopted agent framework in 2026, and LangGraph runs
in production at Cisco, Uber, LinkedIn, BlackRock, and JPMorgan. This adapter
guards tools at the ``on_tool_start`` boundary via a callback handler, so you get
Airlock enforcement without rewriting your agent graph.

    from langchain_core.callbacks import BaseCallbackHandler
    handler = AirlockCallbackHandler(lock)
    agent.invoke(inputs, config={"callbacks": [handler]})

This is a reference adapter kept dependency-free (LangChain is an optional
extra). It raises BlockedActionError from on_tool_start, which LangGraph surfaces
as a tool error the agent can observe and react to.
"""

from __future__ import annotations

from typing import Any

from ..core import Airlock


class AirlockCallbackHandler:
    """Minimal LangChain-compatible callback that enforces policy on every tool.

    Subclass ``langchain_core.callbacks.BaseCallbackHandler`` in your own code
    and mix this in, or use as-is if you only need tool guarding.
    """

    def __init__(self, airlock: Airlock) -> None:
        self.airlock = airlock

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        action = (serialized or {}).get("name", "unknown_tool")
        # LangChain passes tool input as a string or dict depending on version;
        # normalise to a dict of args for policy matching.
        inputs = kwargs.get("inputs")
        args = inputs if isinstance(inputs, dict) else {"input": input_str}
        self.airlock.enforce(action, args)  # raises BlockedActionError if blocked
