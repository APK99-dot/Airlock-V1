"""Policy-as-code engine.

A policy is an ordered list of rules. For a proposed action, the FIRST matching
rule wins and supplies the decision + human-readable reason. If nothing matches,
the policy's ``default`` decision applies.

Rules match on three optional axes (all must pass for the rule to fire):

  action:  glob against the action name          e.g. "db.*", "payments.refund"
  args:    {arg_name: regex} searched on str(arg) e.g. {query: "(?i)drop\\s"}
  when:    a boolean expression over ``args``     e.g. "args['amount'] > 10000"

Keeping matching declarative is the point: a non-engineer can read a policy file
and understand exactly what their agents can and cannot do.
"""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from .decisions import Decision

try:  # PyYAML is the only hard dependency; degrade gracefully if absent.
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


@dataclass
class Rule:
    name: str
    decision: Decision
    reason: str
    action: str = "*"
    args: dict[str, re.Pattern] = field(default_factory=dict)
    when: Optional[str] = None
    description: str = ""

    def matches(self, action: str, args: dict[str, Any]) -> bool:
        if not fnmatch.fnmatch(action, self.action):
            return False
        for key, pattern in self.args.items():
            value = args.get(key, "")
            if not pattern.search(str(value)):
                return False
        if self.when is not None and not _safe_eval(self.when, args):
            return False
        return True


@dataclass
class Policy:
    rules: list[Rule]
    default: Decision = Decision.ALLOW
    default_reason: str = "No rule matched; policy default applied."
    version: int = 1

    # ---- constructors -----------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Policy":
        rules: list[Rule] = []
        for raw in data.get("rules", []):
            match = raw.get("match", {})
            arg_patterns = {
                k: re.compile(v) for k, v in (match.get("args") or {}).items()
            }
            rules.append(
                Rule(
                    name=raw["name"],
                    decision=Decision(raw["decision"]),
                    reason=raw.get("reason", raw["name"]),
                    action=match.get("action", "*"),
                    args=arg_patterns,
                    when=match.get("when"),
                    description=raw.get("description", ""),
                )
            )
        return cls(
            rules=rules,
            default=Decision(data.get("default", "allow")),
            version=int(data.get("version", 1)),
        )

    @classmethod
    def from_file(cls, path: str) -> "Policy":
        if yaml is None:  # pragma: no cover
            raise RuntimeError("PyYAML is required to load policy files: pip install pyyaml")
        with open(path, "r", encoding="utf-8") as fh:
            return cls.from_dict(yaml.safe_load(fh))

    # ---- evaluation -------------------------------------------------------

    def evaluate(self, action: str, args: dict[str, Any]) -> tuple[Decision, str, Optional[str]]:
        """Return (decision, reason, rule_name) for a proposed action."""
        for rule in self.rules:
            if rule.matches(action, args):
                return rule.decision, rule.reason, rule.name
        return self.default, self.default_reason, None


# ---------------------------------------------------------------------------
# `when` expression evaluation
#
# Policies are authored by the developer deploying the agent (trusted input),
# not by the agent or an end user. We still strip builtins so a typo can't reach
# the filesystem or network, and expose only the action's args.
# ---------------------------------------------------------------------------

# A small allowlist of pure, side-effect-free helpers usable inside `when`.
_SAFE_BUILTINS = {
    "float": float, "int": int, "str": str, "bool": bool, "len": len,
    "abs": abs, "round": round, "min": min, "max": max,
}


def _safe_eval(expr: str, args: dict[str, Any]) -> bool:
    try:
        return bool(eval(expr, {"__builtins__": _SAFE_BUILTINS}, {"args": args}))
    except Exception:
        # A malformed expression should fail closed for review/block rules,
        # but here we simply treat "couldn't evaluate" as "did not match".
        return False
