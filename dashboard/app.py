"""Optional live ledger dashboard — the visual for non-technical stakeholders.

    pip install -e ".[dashboard]"
    # generate some ledger data first:
    python examples/rogue_agent_demo.py > /dev/null   # writes ledger.jsonl if configured
    uvicorn dashboard.app:app --reload
    # open http://localhost:8000

It reads the JSONL ledger and renders allow/block/review verdicts as they
happen. Point AIRLOCK_LEDGER_PATH at any ledger file your agents write.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse, JSONResponse
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install dashboard extras: pip install -e '.[dashboard]'") from exc

LEDGER_PATH = Path(os.environ.get("AIRLOCK_LEDGER_PATH", "ledger.jsonl"))
INDEX = (Path(__file__).parent / "index.html").read_text(encoding="utf-8")

app = FastAPI(title="Airlock Dashboard")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return INDEX


@app.get("/api/verdicts")
def verdicts() -> JSONResponse:
    rows = []
    if LEDGER_PATH.exists():
        for line in LEDGER_PATH.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    counts = {"allow": 0, "block": 0, "review": 0}
    for r in rows:
        d = r.get("decision", "allow")
        counts[d] = counts.get(d, 0) + 1
    return JSONResponse({"verdicts": rows[-200:], "counts": counts})
