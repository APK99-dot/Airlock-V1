"""Airlock — the action firewall for AI agents.

Your agents can think freely. Nothing dangerous gets *executed* without passing
the airlock. Policy-as-code + human-in-the-loop approval + a full ledger,
at the one boundary that matters: where an agent's decision becomes an action.
"""

from .approvals import (
    AutoApproveApprover,
    AutoDenyApprover,
    CallbackApprover,
    TerminalApprover,
)
from .ledger import Ledger
from .core import Airlock
from .decisions import BlockedActionError, Decision, Verdict
from .policy import Policy, Rule

__version__ = "0.1.0"

__all__ = [
    "Airlock",
    "Policy",
    "Rule",
    "Decision",
    "Verdict",
    "BlockedActionError",
    "Ledger",
    "TerminalApprover",
    "AutoDenyApprover",
    "AutoApproveApprover",
    "CallbackApprover",
]
