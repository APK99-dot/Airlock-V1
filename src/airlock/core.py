"""The Airlock: the single object developers interact with.

    from airlock import Airlock

    lock = Airlock.from_file("policies/example.yaml")

    # 1) Decorate a tool the agent can call
    @lock.guard("payments.refund")
    def issue_refund(amount: float, account: str) -> str:
        ...

    # 2) Or check imperatively at your framework's tool-execution boundary
    verdict = lock.check("db.execute", {"query": sql})
    if verdict.allowed:
        run(sql)

Design goal: adding Airlock to an existing agent should be a one-line change at
the point where the agent's decisions become real-world actions.
"""

from __future__ import annotations

import functools
import time
from typing import Any, Callable, Optional

from .approvals import Approver, AutoDenyApprover
from .ledger import Ledger
from .decisions import BlockedActionError, Decision, Verdict
from .policy import Policy


class Airlock:
    def __init__(
        self,
        policy: Policy,
        approver: Optional[Approver] = None,
        ledger: Optional[Ledger] = None,
    ) -> None:
        self.policy = policy
        self.approver = approver or AutoDenyApprover()
        self.ledger = ledger or Ledger()

    # ---- constructors -----------------------------------------------------

    @classmethod
    def from_file(cls, path: str, **kwargs: Any) -> "Airlock":
        return cls(Policy.from_file(path), **kwargs)

    @classmethod
    def from_dict(cls, data: dict[str, Any], **kwargs: Any) -> "Airlock":
        return cls(Policy.from_dict(data), **kwargs)

    # ---- the core evaluation ---------------------------------------------

    def check(self, action: str, args: dict[str, Any]) -> Verdict:
        """Evaluate a proposed action WITHOUT executing it.

        REVIEW rules are resolved here by consulting the approver, so the
        returned verdict is always terminal: ALLOW or BLOCK.
        """
        started = time.perf_counter()
        decision, reason, rule = self.policy.evaluate(action, args)
        approved_by: Optional[str] = None

        if decision is Decision.REVIEW:
            approved = self.approver.request(action, args, reason)
            approved_by = type(self.approver).__name__
            decision = Decision.ALLOW if approved else Decision.BLOCK
            reason = (
                f"Human approved: {reason}" if approved
                else f"Human denied: {reason}"
            )

        verdict = Verdict(
            action=action,
            args=args,
            decision=decision,
            reason=reason,
            rule=rule,
            latency_ms=(time.perf_counter() - started) * 1000,
            approved_by=approved_by,
        )
        self.ledger.record(verdict)
        return verdict

    def enforce(self, action: str, args: dict[str, Any]) -> Verdict:
        """Like ``check`` but raises BlockedActionError if the action is blocked."""
        verdict = self.check(action, args)
        if not verdict.allowed:
            raise BlockedActionError(verdict)
        return verdict

    # ---- the decorator ----------------------------------------------------

    def guard(self, action: str, arg_map: Optional[Callable[..., dict]] = None):
        """Wrap a tool function so every call passes through the airlock first.

        ``action`` is the policy action name. By default the function's keyword
        args are used as the action args; pass ``arg_map`` to customise (e.g. to
        pull fields out of a positional object).
        """

        def decorator(fn: Callable) -> Callable:
            @functools.wraps(fn)
            def wrapper(*a: Any, **kw: Any) -> Any:
                args = arg_map(*a, **kw) if arg_map else dict(kw)
                self.enforce(action, args)  # raises if blocked
                return fn(*a, **kw)

            wrapper.__airlock_action__ = action  # type: ignore[attr-defined]
            return wrapper

        return decorator
