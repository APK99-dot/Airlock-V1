"""Tamper-evident-ish ledger.

Every verdict is appended to an in-memory list and (optionally) a JSONL file.
The JSONL format is intentionally boring: one verdict per line, so it streams
cleanly into the dashboard, Splunk, Datadog, or `jq` without a schema migration.

This is the artifact a compliance or risk reviewer actually asks for: "show me
every action the agent attempted, what you decided, and why."
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Callable, Optional

from .decisions import Verdict


class Ledger:
    def __init__(self, path: Optional[str] = None) -> None:
        self._path = Path(path) if path else None
        self._entries: list[Verdict] = []
        self._lock = threading.Lock()
        self._subscribers: list[Callable[[Verdict], None]] = []
        if self._path:
            self._path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, verdict: Verdict) -> None:
        with self._lock:
            self._entries.append(verdict)
            if self._path:
                with self._path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(verdict.to_dict()) + "\n")
        for cb in list(self._subscribers):
            try:
                cb(verdict)
            except Exception:
                pass  # a broken subscriber must never break the guarded action

    def subscribe(self, callback: Callable[[Verdict], None]) -> None:
        """Register a live listener (used by the dashboard for push updates)."""
        self._subscribers.append(callback)

    @property
    def entries(self) -> list[Verdict]:
        with self._lock:
            return list(self._entries)

    def summary(self) -> dict[str, int]:
        counts = {"allow": 0, "block": 0, "review": 0}
        for v in self.entries:
            counts[v.decision.value] += 1
        return counts
