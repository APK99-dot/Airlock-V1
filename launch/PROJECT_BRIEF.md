# Airlock — project brief & rationale

The strategy behind the build. README is the storefront; this is the war room.

## Who this is for (your inputs)
- **Your expertise:** AI/ML engineering — so the project must be technically real, not a demo shell.
- **Audience to win:** enterprise & non-technical decision-makers — so the *framing* is risk/governance, the *demo* is visual, and the *ledger* (not the code) is the hero for them.
- **Time budget:** evenings over ~2 weeks — scoped to one hero feature that already runs today.

## Phase 2 — Why Airlock (choose & justify)

**Three trends I validated by live search this month**, and how each intersects you:

| Trend | Evidence (2026) | Why it fit / didn't |
|---|---|---|
| Agentic AI mainstream | Market $8.5B→$45B by 2030; 85% of firms customizing agents | Real but crowded; hard to differentiate solo |
| MCP as the tool protocol | 200+ servers; prod stacks run 5–9 concurrently | Great distribution surface — used it as an *integration*, not the whole product |
| **Agent governance / runtime guardrails** ✅ | 47% of CISOs saw agents act without authorization; only 5% confident they could contain one; only 21% have mature governance; a coding agent deleted a prod DB + backups in 9 seconds | **The winner** — underserved by solo builders, and it's the exact fear my audience feels |

**Alternatives considered & rejected:**
- *"Another RAG chatbot"* — saturated, low credibility signal, no decision-maker urgency.
- *"An MCP server for X"* — buildable but commoditized; 200+ already exist.
- *"An eval/observability tool"* — valuable but crowded (Galileo, Arize, LangSmith) and less viscerally demoable.

**One-sentence why it wins:** Airlock beats the alternatives on all three engagement levers at once — **credibility** (real policy engine, tests, MCP/LangChain integration = shows AI/ML depth), **trend heat** (rides the single hottest, incident-driven enterprise AI story of 2026), and **demoability** (a rogue agent getting stopped live is a 40-second "wow" a non-technical exec instantly understands).

## Phase 3 — Scope (ruthless)

**The ONE hero feature:** Pre-execution action interception — evaluate every proposed agent action against readable policy-as-code and return ALLOW / BLOCK / REVIEW, with human-in-the-loop approval and a full ledger.

**Explicit non-goals** (say no loudly so scope can't creep):
- No content moderation / prompt-injection filtering (different layer — compose with NeMo/Galileo).
- No model hosting, no eval platform, no observability suite.
- No enterprise IAM/SSO/RBAC.
- No code sandbox / execution isolation.

**Checks:**
- ✅ **Demoable in <60s** — `python examples/rogue_agent_demo.py` runs the full allow/block/review/block story in ~10s of output; scripted for a 45s recording.
- ✅ **Safe to open-source** — zero client data or IP; pure framework + synthetic demo. MIT.
- ✅ **Fits the time budget** — core engine, decorator, MCP + LangChain adapters, tests, and demo already work. Weekend-2 polish is the dashboard + demo GIF + a second policy pack.

## Phase 4 — What was produced
- Working Python package (`src/airlock/`) — policy engine, `Airlock` core, approvers, ledger, MCP proxy, LangChain adapter.
- `examples/rogue_agent_demo.py` — the 60-second demo (runs today, 10/10 tests pass).
- Storefront `README.md`, `docs/architecture.md` (mermaid diagrams), CI, MIT license, CONTRIBUTING.
- Optional live dashboard (`dashboard/`) for the visual stakeholder story.
- This launch kit: 3-post LinkedIn sequence, demo shot-list, metrics tracker.

## Phase 5 — Self-critique

**Single biggest risk to engagement:** *"Cool demo, but is it real / would I actually use it?"* — the classic fate of a portfolio repo that's a pretty README over nothing. **Mitigation:** the code genuinely runs (10 passing tests, a demo that executes, real MCP/LangChain integration surfaces, CI on 3 Python versions). The README leads with dated real-world incidents, not hype, and the comparison table honestly positions Airlock as *one layer* that composes with existing tools — credibility through precision, not overclaim.

**Secondary risk:** name/category collision (Microsoft shipped an "Agent Governance Toolkit"; "guardrails" is a busy space). **Mitigation:** sharp, narrow positioning — *action layer, one-line adoption, readable policy, MCP-native* — is a defensible wedge distinct from heavyweight platforms and content filters.

### Assumptions I made (correct me in one pass)
1. **Name "Airlock"** and GitHub repo is `APK99-dot/Airlock`. PyPI package name `airlock-agents` (verify availability before publishing).
2. Public identity is **APK99-dot** — used in LICENSE, pyproject, README. Swap to a real/display name if you'd prefer that on a portfolio piece.
3. **Python** as the stack (matches AI/ML expertise + the agent ecosystem). Not TypeScript.
4. **1 project**, not 2–3 — I judged one sharp shipped tool beats a spread. Say the word for a second concept.
5. The **incident stats** are from live July-2026 search (sources in the launch notes); re-verify the exact figures before quoting them publicly in a post.

## Sources (live search, July 2026)
- Saviynt 2026 CISO AI Risk Report — 47% observed unauthorized agent behavior; 5% containment confidence.
- Deloitte 2026 State of AI in the Enterprise — 85% customizing agents; 21% mature governance.
- Cursor/PocketOS production-DB deletion incident (Apr 25, 2026); Meta rogue-agent data exposure (Mar 18, 2026).
- Databricks / Firecrawl / Galileo / Microsoft Open Source (Agent Governance Toolkit) — 2026 agentic-guardrails landscape.
- OSSInsight AI trending; LangChain 2026 framework survey; MCP server ecosystem (200+ servers).
