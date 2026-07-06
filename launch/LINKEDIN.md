# LinkedIn launch sequence — Airlock

Audience: enterprise & non-technical decision-makers (+ the AI engineers who advise them).
Rule: lead with **pain or result**, never "excited to share." One idea per post. End with a question, not a pitch.

Cadence: **Post 1 (teaser) → T-3 days · Post 2 (launch) → day 0 · Post 3 (lesson) → T+4 days.**

---

## POST 1 — TEASER (T-3 days)

**Hook:**
> An AI agent deleted a company's production database — and its backups — in 9 seconds.
> Nobody clicked "confirm." There was no confirm.

**Body:**
That happened in April. In March, another agent quietly handed internal data to people who weren't cleared to see it.

Here's the uncomfortable stat from this year's CISO AI Risk Report:
→ 47% of security leaders have already watched an agent take an action it wasn't supposed to.
→ Only 5% are confident they could stop a compromised one.

We've spent two years making agents *smarter*. We've spent almost nothing making their *actions* accountable.

I got tired of talking about it, so I spent my evenings building something about it. Ships here in 3 days.

**CTA:**
> Genuine question for the operators here: what's the one action you would never let an autonomous agent take without a human in the loop? 👇

*(Visual: a single stark screenshot — the terminal line `✖ BLOCKED  DROP TABLE customers`.)*

---

## POST 2 — LAUNCH (day 0)

**Hook:**
> Your AI agent can think freely.
> It just can't `DROP TABLE customers` without permission anymore.
>
> I open-sourced Airlock today. 🛡️

**Body:**
Airlock is an **action firewall for AI agents**. It sits at the one boundary that actually matters — where an agent's *decision* becomes a real-world *action* — and makes three calls, from a policy your risk team can read:

🟢 ALLOW — refund $75 → goes through
🔴 BLOCK — `DROP TABLE customers` → refused, with a reason
🟡 REVIEW — refund $25,000 → paused for a human

Every attempt lands in a ledger you can hand to compliance. Adding it to an existing agent is one line per tool:

```python
@lock.guard("payments.refund")
def issue_refund(amount, account): ...
```

It works with plain Python, MCP servers, and LangChain/LangGraph. MIT licensed. No account, no SaaS, runs on your machine.

The 40-second demo in the comments shows an over-eager agent trying to nuke a database, refund a fortune, and delete backups — and getting stopped at each door. 👇

**CTA:**
> ⭐ If "autonomous but accountable" is the bar your org needs, the repo's in the comments. Star it so your future self finds it before the incident, not after.

*(Visual: the demo GIF. First comment = GitHub link + the demo video.)*

---

## POST 3 — WHAT I LEARNED (T+4 days)

**Hook:**
> Building guardrails for AI agents taught me the scary part isn't the model.
> It's the 4 inches between "the agent decided" and "the action happened."

**Body:**
Three things that surprised me shipping Airlock this week:

1. **Content filters and action guardrails are different jobs.** Blocking bad *words* does nothing to stop a well-phrased `DELETE FROM`. The dangerous layer is the tool call, and almost nobody guards it.

2. **"Fail closed" has to be the default.** If no human is wired up to approve a sensitive action, the safe answer is *no* — not "let it through because it's 2am." That single default prevents a whole class of incidents.

3. **The ledger is the product.** Engineers wanted the policy engine. Every risk and compliance person I showed it to wanted the *log* — "show me everything the agent tried." That's the artifact that gets AI into production.

The governance gap is real: 85% of enterprises are customizing agents, only 21% have a mature way to govern them. That delta is where deployments stall.

**CTA:**
> If your team is piloting agents: are you governing them at the *content* layer, the *action* layer, or (be honest) not yet? Repo's still in the comments if you want a starting point. 👇

*(Visual: the architecture diagram from the README — the 4-layer guardrail stack.)*

---

## Reusable engagement notes
- **First comment always holds the link.** LinkedIn suppresses reach on posts with outbound links in the body.
- Reply to every substantive comment within the first 2 hours — early velocity drives the algorithm.
- Repost Post 2 once, ~48h later, quote-style, with a single new data point or a top comment highlighted.
- Tag no one gratuitously; only tag a person if the post genuinely references their work.
