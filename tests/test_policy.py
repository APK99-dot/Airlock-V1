"""Tests for the policy engine and enforcement flow.

Run: pytest   (pythonpath is set in pyproject so `import airlock` works)
"""

import pytest

from airlock import (
    Airlock,
    AutoApproveApprover,
    AutoDenyApprover,
    BlockedActionError,
    Decision,
    Policy,
)

POLICY = {
    "version": 1,
    "default": "allow",
    "rules": [
        {
            "name": "block-drop",
            "match": {"action": "db.*", "args": {"query": "(?i)\\bdrop\\b"}},
            "decision": "block",
            "reason": "no drops",
        },
        {
            "name": "review-big-refund",
            "match": {"action": "payments.refund", "when": "float(args.get('amount', 0)) > 10000"},
            "decision": "review",
            "reason": "big refund",
        },
    ],
}


def make(approver=None):
    return Airlock.from_dict(POLICY, approver=approver or AutoDenyApprover())


def test_allow_by_default():
    v = make().check("email.read", {"id": 1})
    assert v.decision is Decision.ALLOW
    assert v.rule is None


def test_block_destructive_sql():
    v = make().check("db.query", {"query": "DROP TABLE users"})
    assert v.decision is Decision.BLOCK
    assert v.rule == "block-drop"


def test_first_match_wins():
    # A benign SELECT should not trip the drop rule.
    v = make().check("db.query", {"query": "SELECT * FROM users"})
    assert v.decision is Decision.ALLOW


def test_review_resolves_to_allow_when_approved():
    v = make(AutoApproveApprover()).check("payments.refund", {"amount": 25000})
    assert v.decision is Decision.ALLOW
    assert "approved" in v.reason.lower()


def test_review_resolves_to_block_when_denied():
    v = make(AutoDenyApprover()).check("payments.refund", {"amount": 25000})
    assert v.decision is Decision.BLOCK


def test_small_refund_allowed():
    v = make().check("payments.refund", {"amount": 50})
    assert v.decision is Decision.ALLOW


def test_guard_decorator_raises_on_block():
    lock = make()

    @lock.guard("db.query")
    def run(query):
        return "ran"

    with pytest.raises(BlockedActionError):
        run(query="DROP DATABASE prod")


def test_guard_decorator_executes_when_allowed():
    lock = make()

    @lock.guard("db.query")
    def run(query):
        return "ran"

    assert run(query="SELECT 1") == "ran"


def test_ledger_records_every_attempt():
    lock = make()
    lock.check("email.read", {"id": 1})
    lock.check("db.query", {"query": "DROP TABLE x"})
    assert len(lock.ledger.entries) == 2
    assert lock.ledger.summary()["block"] == 1


def test_yaml_policy_loads(tmp_path):
    import textwrap
    p = tmp_path / "pol.yaml"
    p.write_text(textwrap.dedent("""
        version: 1
        default: block
        rules:
          - name: allow-reads
            match: {action: "*.read"}
            decision: allow
            reason: reads are fine
    """))
    lock = Airlock(Policy.from_file(str(p)))
    assert lock.check("email.read", {}).decision is Decision.ALLOW
    assert lock.check("email.send", {}).decision is Decision.BLOCK
