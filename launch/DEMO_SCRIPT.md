# The 40–60s demo script — Airlock

Goal: in under a minute, a viewer *feels* "oh — this stops the thing I'm afraid of."
Format: screen recording of a terminal (optionally split with the dashboard). No talking head needed; on-screen captions carry it. Record with [asciinema](https://asciinema.org) or QuickTime, export GIF with [`agg`](https://github.com/asciinema/agg) or Gifski.

## Setup (before recording)
```bash
pip install -e .
clear
# Big, legible font. Dark terminal. Window ~100 cols.
```

## Shot list (target 45s)

| Time | On screen | Caption overlay |
|------|-----------|-----------------|
| 0:00–0:04 | The policy file open — scroll `policies/example.yaml` slowly | **"Rules your risk team can read."** |
| 0:04–0:07 | Type `python examples/rogue_agent_demo.py` and hit enter | **"Now let's turn an agent loose."** |
| 0:07–0:13 | `refund $75` → `✔ ALLOWED` (green) | **"Safe action? Straight through."** |
| 0:13–0:22 | `DROP TABLE customers;` → `✖ BLOCKED` (red) — hold 2s | **"The 9-second database deletion? Stopped."** |
| 0:22–0:30 | `refund $25,000` → routed to human → approved → `✔` | **"Ambiguous? A human decides — not the agent."** |
| 0:30–0:36 | `aws s3 rb … prod-backups` → `✖ BLOCKED` (red) | **"Deleting backups? Not without an operator."** |
| 0:36–0:45 | The LEDGER block renders; `allow=2 block=2` | **"Every attempt logged. Nothing dangerous ran."** |
| 0:45–0:48 | Cut to text card: `🛡️ Airlock — github.com/APK99-dot/Airlock · MIT` | **"Autonomous. Not unaccountable."** |

## Punch-up options
- **Split-screen:** run `uvicorn dashboard.app:app` on the right; watch red/green rows appear live as the left terminal fires. Higher production value for the launch post.
- **The `--human` take:** record a second, longer cut using `python examples/rogue_agent_demo.py --human` where *you* type `n` to deny the $25k refund — great for the "human-in-the-loop" talking point in Post 3.

## Recording tips
- Slow your typing; add a beat before each result so the color change is the moment.
- Keep total length under 50s — LinkedIn autoplays muted; the captions must stand alone.
- First frame should already show a red `✖ BLOCKED` if possible (thumbnail = the hook).
- Export at 720p+; name it `airlock_demo.gif` and drop it at `docs/demo.gif` (README references it).
