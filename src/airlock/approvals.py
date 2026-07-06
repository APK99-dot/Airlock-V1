"""Human-in-the-loop approvers.

When a policy returns REVIEW, Airlock hands the pending action to an Approver,
which returns True (approve -> execute) or False (deny -> block). Approvers are
pluggable so the same policy works in a notebook, a CI pipeline, or behind a
Slack bot without changing a line of agent code.
"""

from __future__ import annotations

import json
from typing import Any, Protocol


class Approver(Protocol):
    def request(self, action: str, args: dict[str, Any], reason: str) -> bool:
        """Return True to approve the action, False to deny it."""
        ...


class AutoDenyApprover:
    """Fail-closed default: if no human is wired up, REVIEW becomes BLOCK.

    This is the safe posture for production — an unattended agent should never
    be able to self-approve a sensitive action.
    """

    def request(self, action: str, args: dict[str, Any], reason: str) -> bool:
        return False


class AutoApproveApprover:
    """Fail-open: approve everything routed to review. For tests/demos ONLY."""

    def request(self, action: str, args: dict[str, Any], reason: str) -> bool:
        return True


class TerminalApprover:
    """Prompt a human on the CLI. Great for local demos and dev loops."""

    def request(self, action: str, args: dict[str, Any], reason: str) -> bool:
        print("\n" + "=" * 60)
        print("  AIRLOCK: human approval required")
        print("=" * 60)
        print(f"  Action : {action}")
        print(f"  Args   : {json.dumps(args, default=str)[:200]}")
        print(f"  Reason : {reason}")
        try:
            answer = input("  Approve this action? [y/N] ").strip().lower()
        except EOFError:
            answer = "n"
        return answer in {"y", "yes"}


class CallbackApprover:
    """Delegate to any callable — wire this to Slack, a webhook, or the dashboard."""

    def __init__(self, fn) -> None:
        self._fn = fn

    def request(self, action: str, args: dict[str, Any], reason: str) -> bool:
        return bool(self._fn(action, args, reason))
