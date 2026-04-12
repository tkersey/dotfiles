# Security Economics for SaaS

Security investment is not a cost center, it is risk financing. This file
gives you the vocabulary and the math to make budget and prioritization
arguments that land with CFOs, not just CISOs.

See also: [SECURITY-DEBT.md](SECURITY-DEBT.md) for quantifying existing
risk and [BUG-BOUNTY.md](BUG-BOUNTY.md) for bounty ROI.

---

## The Core Equations

### Annualized Loss Expectancy (ALE)

```
ALE = SLE × ARO

SLE (Single Loss Expectancy) = AssetValue × ExposureFactor
ARO (Annualized Rate of Occurrence) = expected events per year
```

Example — a cross-tenant data leak in a multi-tenant SaaS:

- Asset value: $5M (sum of all tenant data that could leak in a worst case)
- Exposure factor: 0.4 (40% of tenants likely affected before detection)
- ARO: 0.1 (once every 10 years, based on incident history)

```
SLE = 5,000,000 × 0.4 = 2,000,000
ALE = 2,000,000 × 0.1 = 200,000/year
```

You can spend up to **$200k/year** defending against this one scenario
and still come out ahead in expectation. Spending $50k/year to prevent it
is a 4x return on security investment (ROSI).

### Return on Security Investment (ROSI)

```
ROSI = (ALE × RiskReduction − ControlCost) / ControlCost
```

- `ALE × RiskReduction` = expected value of avoided losses
- Control cost = annualized fully-loaded cost of the control
  (engineering time, SaaS subscription, compute, auditor time)

A control with **ROSI > 0** is net positive. A control with **ROSI > 1**
doubles your money in expectation. Anything under 0 is costing you.

### Bayesian updating as incidents happen

ARO is not static. After every incident (yours or an analogous SaaS), you
should be updating your ARO estimate:

```
new_ARO = (old_ARO × prior_weight + observed_rate × observation_weight) / total_weight
```

Rule of thumb: give 3–5 years of observation before treating your own
incident rate as authoritative. Before that, blend with industry data
(Verizon DBIR, IBM Cost of a Data Breach Report).

---

## What your losses actually look like

Engineers routinely underestimate breach costs. The real cost stack:

| Category | Typical share | Notes |
|----------|---------------|-------|
| Detection & escalation | 10–15% | Forensics, IR retainer |
| Notification | 5–10% | Legal, customer comms, regulator filings |
| Post-breach response | 20–30% | Credit monitoring, identity protection, call center |
| Lost business | 30–40% | Churn, deal pauses, reputational damage |
| Regulatory fines | 5–30% | Varies wildly by jurisdiction and data type |
| Litigation | 5–25% | Class actions, contract claims |

**The largest category is almost always lost business**, not fines. A
well-timed breach can stall a Series B fundraise or kill an enterprise
deal pipeline for 6–9 months.

### Back-of-envelope per-record costs (2026)

| Data type | Cost per record (USD) |
|-----------|------------------------|
| Email + password | $5–15 |
| Full PII (name, address, SSN) | $150–250 |
| Payment card | $75–200 |
| Health records (US HIPAA) | $400–600 |
| Source code / IP leak | Highly variable — sometimes $0, sometimes the whole company |

Multiply by affected records to get a rough SLE floor.

### The asymmetric tail

Breach costs have a **fat-tailed distribution**. Most breaches cost the
median, but a small number cost 10–100x the median. Don't just optimize
for expected value — apply Kelly-criterion thinking. A catastrophic
breach that kills the company is infinitely worse than two moderate
breaches summing to the same dollar amount.

**Practical rule:** if a single incident could end the company, spend
more than ROSI suggests. Treat existential risks as "must fix" not
"optimize spend."

---

## Building a defensible security budget

### Bottom-up: per-control ROSI

1. Enumerate your top 20 risks (use STRIDE, see [ADVERSARIAL-THINKING.md](ADVERSARIAL-THINKING.md))
2. Estimate ALE for each (use the per-record costs above)
3. For each proposed control, estimate:
   - Annualized cost (eng time + SaaS + ops)
   - Risk reduction (what fraction of the ALE goes away)
4. Compute ROSI for each control
5. Fund controls in ROSI-descending order until budget exhausted

### Top-down: percentage of revenue

Industry benchmarks for SaaS:

| Company maturity | Security spend (% of revenue) |
|------------------|-------------------------------|
| Seed / pre-product-market-fit | 1–3% |
| Series A/B | 3–6% |
| Series C+ | 6–10% |
| Regulated (fintech, health) | 8–15% |
| Public company | 10–15%+ |

Use top-down as a sanity check on bottom-up. If your bottom-up says
"spend 25% of revenue on security," your ALE estimates are probably
wrong.

### The "known-unknown" reserve

Reserve 10–20% of the security budget for unpredictable risks. You will
find surprises every year. If your budget is already 100% committed,
you cannot respond to them.

---

## Per-engineer productivity cost

Security work has a hidden cost: it slows down feature development.
Measure this explicitly or you will be blind-sided by engineering
pushback.

**Key metric: security friction per PR**

```
friction = (time spent on security checklist + time waiting for review) / total PR time
```

Healthy: <10%. Concerning: 10–25%. Dysfunctional: >25%.

If you're above 25%, you are paying for security in engineering velocity
— often more than the control itself costs. Consider:

- Automating the check (pre-commit hook, CI rule)
- Making it asynchronous (post-merge scan, weekly audit)
- Consolidating checks (one reviewer, one checklist)
- Killing the check if it hasn't caught a real issue in 6 months

---

## Insurance as a budget line

Cyber insurance is cheap risk transfer for **tail events**. It is not
a substitute for controls — insurers exclude anything you should have
controlled for.

### When to buy

- Company is > Series A and handling customer data
- You have a real SLA/contractual commitment that includes breach
  liability
- You need coverage for regulatory fines that are otherwise
  uninsurable

### What to watch out for

- **Exclusions:** most policies exclude failure to patch known CVEs,
  weak auth, and lack of MFA. Your controls must be good enough to
  not trigger exclusions.
- **Retro dates:** policies only cover incidents after a specific date.
  Check continuous coverage when switching insurers.
- **Notification clauses:** most require notification within 24–72h of
  discovery. Missing this window voids coverage.
- **Ransomware sublimits:** often capped at 10–25% of total limit.

### Typical premiums (2026)

- Series A SaaS, 1M policy: $8k–$25k/year
- Series B SaaS, 5M policy: $30k–$80k/year
- Series C SaaS, 10M policy: $80k–$200k/year

Underwriters will discount 10–30% for MFA, SSO, and EDR in place.
Bounty programs and formal IR retainers also help.

---

## The compliance vs security tradeoff

Compliance spending and security spending overlap but are not the same.
A rational allocation looks like this:

| Activity | Compliance? | Security? |
|----------|:-:|:-:|
| SOC 2 audit | Yes | No |
| Pen test | Partial | Yes |
| Bug bounty | No | Yes |
| RLS policies | No | Yes |
| Audit logging | Yes | Yes |
| Vendor review | Yes | Partial |
| Incident response drills | No | Yes |

**Pathology:** companies that spend 80% of their security budget on
compliance ticks and 20% on actual hardening. They get clean audits and
still get breached.

**Rule:** for every dollar spent on compliance, spend at least a dollar
on controls that would catch or prevent actual attacks.

---

## Security metrics that matter to the CFO

Don't report vulnerability counts to finance. Report dollars.

| Metric | What it answers |
|--------|-----------------|
| Residual ALE | What is our total risk exposure? |
| ALE reduction this quarter | What did security spend buy us? |
| Cost per vulnerability found | Which finding channel is cheapest? |
| Mean time to detect (MTTD) | How long would a breach run before we noticed? |
| Mean time to remediate (MTTR) | How fast can we close a critical finding? |
| Security debt $ | What's the cost of not fixing known issues? |
| Coverage % (SAST/DAST/bounty) | What fraction of surface is being tested? |

Chart these quarterly. A board presentation with trending ALE is
infinitely more useful than "we have 47 criticals in Snyk."

---

## Cost-per-vulnerability across channels

Data from published studies and my own observations:

| Channel | Cost per valid finding (USD) |
|---------|-------------------------------|
| Static analysis (SAST) | $100–500 |
| Dynamic analysis (DAST) | $500–2,000 |
| Internal code review | $1,000–5,000 |
| External pen test | $5,000–15,000 |
| Bug bounty | $500–10,000 (depends on severity) |
| Post-breach (incident-driven discovery) | $100,000+ |

**Lesson:** cheap upstream channels (SAST, DAST, internal review) are
almost always cheaper per finding than incidents. The economics of
"shift left" are real — the only question is whether you're willing to
invest in the tooling.

---

## The "security as insurance" framing

When selling security spend internally, use the insurance framing:

> "We are paying $X per year to avoid $Y in expected loss and potentially
>  $Z in tail-event loss. This is equivalent to buying a cyber insurance
>  policy with better coverage and lower deductible than anything on the
>  market."

CFOs understand insurance. They do not understand "defense in depth."
Meet them where they are.

---

## Common economic anti-patterns

1. **Buying the expensive tool instead of fixing the bug.**
   A $100k/year SaaS doesn't fix a missing authorization check.

2. **Pursuing certifications you can't operationalize.**
   SOC 2 with no incident drills is a paper exercise.

3. **Optimizing for the last breach, not the next one.**
   Your last incident was probably an outlier. Build for the median.

4. **Not budgeting for incident response.**
   An IR retainer is 10x cheaper than emergency IR at 3am on a Sunday.

5. **Treating security spend as fixed cost.**
   It should scale with revenue, headcount, and surface area.

6. **Ignoring vendor risk.**
   Every SaaS vendor is a shared-fate security decision. Budget for
   vendor review and breach notification monitoring.

---

## Audit questions for the CFO/CEO

1. **What's our total ALE?** (If they can't answer, neither can you.)
2. **What would a 72-hour outage cost us in lost contracts?**
3. **Which customer accounts have breach liability clauses?**
4. **What's our cyber insurance retention (deductible)?**
5. **Who owns the decision to pay a ransom?**
6. **What's the budget line for incident response retainer?**
7. **If we had $100k more to spend on security tomorrow, what would we
   buy?** (Reveals whether there's a prioritized backlog.)
8. **If we had $100k less, what would we cut?** (Reveals whether anything
   is actually optional.)

---

## One-page summary for leadership

```
SECURITY BUDGET PROPOSAL

Current ALE:        $2.4M
Budget ask:         $480k (20% of ALE)
Expected ALE post:  $1.1M
Expected ROI:       170%

Top 3 risks addressed:
1. Cross-tenant data leak (ALE $800k → $150k)
2. Webhook forgery (ALE $400k → $50k)
3. Admin credential compromise (ALE $600k → $200k)

Top 3 controls funded:
1. RLS hardening + coverage monitoring ($120k)
2. Webhook signature verification library ($40k)
3. MFA + device-bound admin access ($180k)

Unfunded tail risk: $140k/year for IR retainer
(Board discussion required)
```

This is the format that gets approved.
