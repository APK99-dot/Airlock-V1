"""Core decision types for Airlock.

Every proposed agent action resolves to exactly one Decision. This module keeps
those types dependency-free so they can be imported anywhere (policy engine,
integrations, ledger) without pulling in heavier machinery.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Decision(str, Enum):
    """What Airlock decided to do with a proposed action.

    ALLOW  - action is safe under policy; execute it.
    BLOCK  - action is forbidden; raise instead of executing.
    REVIEW - action is ambiguous; pause and route to a human approver.
    """

    ALLOW = "allow"
    BLOCK = "block"
    REVIEW = "review"


class BlockedActionError(Exception):
    """Raised when a guarded action is blocked (or a review is denied)."""

    def __init__(self, verdict: "Verdict") -> None:
        self.verdict = verdict
        super().__init__(
            f"Airlock blocked action '{verdict.action}': {verdict.reason}"
        )


@dataclass
class Verdict:
    """The full record of a single policy evaluation.

    This is what gets written to the ledger and shown on the dashboard.
    """

    action: str
    args: dict[str, Any]
    decision: Decision
    reason: str
    rule: Optional[str] = None
    latency_ms: float = 0.0
    approved_by: Optional[str] = None
    ts: float = field(default_factory=time.time)

    @property
    def allowed(self) -> bool:
        return self.decision is Decision.ALLOW

    def to_dict(self) -> dict[str, Any]:
        return {
            "ts": self.ts,
            "action": self.action,
            "args": _redactable(self.args),
            "decision": self.decision.value,
            "reason": self.reason,
            "rule": self.rule,
            "latency_ms": round(self.latency_ms, 3),
            "approved_by": self.approved_by,
        }


def _redactable(args: dict[str, Any]) -> dict[str, Any]:
    """Shallow copy so the ledger never holds a live reference to caller args."""
    return dict(args)
