# Contributing to Airlock

Thanks for helping make AI agents accountable.

## The most valuable contribution

**Real-world policy rules.** If you've seen (or narrowly avoided) an agent doing
something it shouldn't, open an issue titled *"An agent tried to ___"* with the
action, the args, and the decision you'd want. These become test cases and
shipped policy packs — the thing that makes Airlock better for everyone.

## Dev setup

```bash
git clone https://github.com/APK99-dot/Airlock && cd Airlock
pip install pyyaml pytest         # or: pip install -e ".[dev]"  (needs pip >= 21.3)
pytest -q
python examples/rogue_agent_demo.py
```

## Ground rules

- Core stays dependency-light (PyYAML only). Heavier things go in extras.
- Every new matcher or decision path needs a test in `tests/`.
- Fail **closed**: when in doubt, a guardrail should block/review, not allow.
- Keep policies human-readable — a non-engineer should understand a rule.

## Adding an integration

Integrations live in `src/airlock/integrations/` and only need to map a
framework's tool-call boundary onto `Airlock.enforce(action, args)`. See
`mcp.py` and `langchain.py` for the pattern.
