"""The 60-second demo: watch an over-eager agent get stopped at the airlock.

Run it (no install needed — only PyYAML):
    pip install pyyaml
    python examples/rogue_agent_demo.py            # auto-approves the review step
    python examples/rogue_agent_demo.py --human     # you approve/deny in the terminal

A scripted agent attempts four escalating actions. Airlock ALLOWS the safe one,
BLOCKS the two dangerous ones with a readable reason, and ROUTES the ambiguous
one to a human. No agent code is changed — only the tool functions are guarded.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# Run straight from a clone without installing: put ../src on the path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from airlock import (
    Airlock,
    Ledger,
    AutoApproveApprover,
    BlockedActionError,
    TerminalApprover,
)

# ANSI colors — no dependencies, works in any terminal / asciinema recording.
G, R, Y, B, DIM, BOLD, END = (
    "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[2m", "\033[1m", "\033[0m",
)

POLICY = Path(__file__).resolve().parents[1] / "policies" / "example.yaml"


def banner(text: str) -> None:
    print(f"\n{B}{BOLD}{'━' * 62}{END}")
    print(f"{B}{BOLD}  {text}{END}")
    print(f"{B}{BOLD}{'━' * 62}{END}")


def attempt(lock: Airlock, action: str, args: dict, fn) -> None:
    """Have the 'agent' try to run a guarded tool and narrate what happens."""
    label = f"{args}"
    if len(label) > 46:
        label = label[:43] + "...}"
    print(f"\n{DIM}agent →{END} calling {BOLD}{action}{END}({label})")
    time.sleep(0.6)
    try:
        result = fn(**args)
        print(f"  {G}✔ ALLOWED{END}  {result}")
    except BlockedActionError as exc:
        v = exc.verdict
        rule = f" [{v.rule}]" if v.rule else ""
        print(f"  {R}✖ BLOCKED{END}{DIM}{rule}{END}  {v.reason}")
    time.sleep(0.6)


def build_agent(lock: Airlock):
    """The 'tools' our agent can call — each guarded with a one-line decorator."""

    @lock.guard("db.query")
    def db_query(query: str) -> str:
        return f"executed SQL: {query!r}"

    @lock.guard("payments.refund")
    def refund(amount: float, account: str) -> str:
        return f"refunded ${amount:,.2f} to {account}"

    @lock.guard("infra.run")
    def infra_run(command: str) -> str:
        return f"ran: {command!r}"

    return db_query, refund, infra_run


def main() -> None:
    human = "--human" in sys.argv
    approver = TerminalApprover() if human else AutoApproveApprover()

    # Write the trail to JSONL so the optional dashboard can render it live.
    # Start each run clean so the dashboard shows just this session.
    ledger_path = os.environ.get("AIRLOCK_LEDGER_PATH", "ledger.jsonl")
    Path(ledger_path).unlink(missing_ok=True)
    ledger = Ledger(ledger_path)
    lock = Airlock.from_file(str(POLICY), approver=approver, ledger=ledger)
    db_query, refund, infra_run = build_agent(lock)

    banner("AIRLOCK  ·  the action firewall for AI agents")
    print(f"{DIM}policy: {POLICY.name}   ·   approver: {type(approver).__name__}{END}")

    # 1) Safe action — should sail through.
    attempt(lock, "payments.refund",
            {"amount": 75.00, "account": "cust_8842"}, refund)

    # 2) The nightmare headline — an agent trying to delete the database.
    attempt(lock, "db.query",
            {"query": "DROP TABLE customers;"}, db_query)

    # 3) Ambiguous — a big refund. Routed to a human (auto-approved unless --human).
    attempt(lock, "payments.refund",
            {"amount": 25000.00, "account": "cust_0001"}, refund)

    # 4) Infra teardown — hard blocked.
    attempt(lock, "infra.run",
            {"command": "aws s3 rb s3://prod-backups --force"}, infra_run)

    # The receipt: a full ledger, ready for a compliance reviewer.
    counts = lock.ledger.summary()
    banner("LEDGER")
    for v in lock.ledger.entries:
        color = {"allow": G, "block": R, "review": Y}[v.decision.value]
        print(f"  {color}{v.decision.value.upper():6}{END} "
              f"{v.action:18} {DIM}{v.latency_ms:.2f}ms  {v.reason}{END}")
    print(f"\n  {G}allow={counts['allow']}{END}  "
          f"{R}block={counts['block']}{END}  "
          f"{Y}review→resolved{END}   "
          f"{DIM}(every attempt logged, nothing dangerous executed){END}\n")


if __name__ == "__main__":
    main()
