# Security Debt — Quantifying and Managing

Technical debt is well-understood. Security debt is equally real but less
often managed. This file is the framework for quantifying, tracking, and
systematically paying down security debt.

---

## What Is Security Debt?

Security debt = gap between current security posture and desired security
posture, accumulated over time as a result of deferred work.

**Sources:**
- Known vulnerabilities not yet fixed
- Missing security controls (no MFA, no audit log, etc.)
- Outdated dependencies with CVEs
- Deprecated auth patterns still in use
- Missing documentation (threat models, runbooks)
- Accepted risks that were never revisited
- "We'll add that later" decisions

Like financial debt, security debt accrues interest (attacks get easier,
regulations tighten, customer expectations rise).

---

## The Debt Ledger

Maintain a single source of truth for security debt:

```markdown
# Security Debt Ledger

Last updated: 2026-04-09

## Summary
- Total items: 34
- Critical: 2
- High: 8
- Medium: 16
- Low: 8
- Estimated work: 320 days
- Estimated cost: $96K (labor)

## Critical (2)
### SD-001: No MFA on admin accounts
- **Impact:** If any admin credential leaks, attacker has full access
- **Added:** 2025-08-15
- **Effort:** 5 days
- **Owner:** Security team
- **Deadline:** 2026-05-01
- **Blocked by:** Procurement of MFA solution
- **Status:** In progress

### SD-002: Missing RLS on users table
- **Impact:** Any authenticated user can query all users via Supabase anon key
- **Added:** 2026-03-22
- **Effort:** 3 days
- **Owner:** @alice
- **Deadline:** 2026-04-15
- **Blocked by:** None
- **Status:** Open

## High (8)
...
```

### Fields to track
- ID (for reference)
- Title (short, actionable)
- Severity (Critical / High / Medium / Low)
- Impact (what goes wrong if exploited)
- Added date (when we found it)
- Effort (engineering days)
- Owner (person or team)
- Deadline (target fix date)
- Blockers (what's stopping progress)
- Status (Open / In progress / Waiting / Fixed / Accepted)
- Compensating controls (what reduces risk in the interim)
- Related findings (from audits, pen tests, incidents)

---

## Scoring Debt Items

### The formula
```
Priority = (Impact × Likelihood × Exposure) / Effort
```

**Impact:** 1-10, how bad is exploitation?
**Likelihood:** 1-10, how likely to be exploited?
**Exposure:** 1-10, how accessible is the vulnerability?
**Effort:** engineering days to fix

Higher priority score = fix first.

### Example
- SD-001 (No MFA): Impact 9 × Likelihood 7 × Exposure 8 / 5 days = 100.8
- SD-002 (No RLS on users): Impact 10 × Likelihood 8 × Exposure 10 / 3 days = 266.7
- SD-042 (Old dependency, no CVE): Impact 3 × Likelihood 2 × Exposure 2 / 1 day = 12

Fix SD-002 first.

---

## Tracking Debt Over Time

### The monthly metric
Every month, compute:
- **Debt incurred:** new items added
- **Debt paid:** items fixed
- **Net debt:** incurred - paid
- **Debt age:** average days since oldest item

### Goal
**Negative net debt** every month (paying down faster than accumulating).

If you consistently have positive net debt, you're falling behind.

### Dashboard
```
Security Debt Dashboard
═══════════════════════

Month: April 2026

Incurred:     8 items (15 days work)
Paid down:   12 items (22 days work)
Net:         -4 items (-7 days)  ✓

Total open:
├─ Critical: 2 (↓1 from March)
├─ High:     8 (↓2)
├─ Medium:  16 (↑3)
└─ Low:      8 (→0)

Oldest open: SD-003 (180 days)
```

---

## Debt Categorization

### By Type
- **Missing controls** — things we should have but don't
- **Outdated controls** — things we have but are old
- **Known vulnerabilities** — bugs we haven't fixed
- **Technical limitations** — things we can't fix easily
- **Process gaps** — missing procedures

### By Blast Radius
- **Localized** — affects one feature
- **Product-wide** — affects whole application
- **Customer-visible** — affects customers directly
- **Compliance** — affects SOC 2 / GDPR compliance

### By Fix Complexity
- **Trivial** (< 1 day) — easy wins, fix immediately
- **Small** (1-5 days) — can fit in a sprint
- **Medium** (5-20 days) — needs planning
- **Large** (20+ days) — needs a project

---

## Debt Budgets

Allocate a percentage of engineering capacity to debt reduction:

| Security Maturity | % of time on security debt |
|-------------------|---------------------------|
| Level 1 (Foundation) | 0-5% |
| Level 2 (Operational) | 5-10% |
| Level 3 (Compliance) | 10-15% |
| Level 4 (Mature) | 15-20% |
| Level 5 (Best-in-class) | 20%+ |

This is *maintenance*, not incident response. Incidents are on top of this.

---

## Accepted Risk

Not all debt should be fixed. Some items should be accepted with:
- Documentation of WHY it's accepted
- Compensating controls
- Review date (revisit in N months)
- Sign-off from appropriate level (CTO, CISO, etc.)

```markdown
## SD-018: In-memory rate limiter on Vercel serverless

**Status:** ACCEPTED

**Impact:** During traffic spikes, rate limits are per-instance, not global.
**Effective limit:** ~N × configured limit where N is concurrent instances.

**Why accepted:**
- Current traffic levels don't make this exploitable
- Implementing Redis costs $100/mo + dev time
- Compensating controls: monitoring for abuse patterns, manual intervention
  capable of blocking IPs

**Review date:** 2026-10-01 (or when traffic > 10K req/min sustained)

**Sign-off:** @alice (CTO), 2026-04-09
```

Accepted risks are not "fixed" but they're also not actively blocking fixes.

---

## Preventing Debt Accumulation

### "Don't ship new debt"
New features shouldn't add security debt. If they do, fixing must be in the
plan before launch.

### "Debt paydown sprints"
Dedicate one sprint per quarter to security debt reduction. No feature work,
only paying down the ledger.

### "Boy scout rule"
When touching code near security debt, fix it opportunistically if cheap.

### "Stop the bleeding"
If debt is growing, stop adding new debt even if it means slowing feature velocity.

---

## Debt-Based Decision Making

### New feature proposal
Before approving a new feature, ask:
- Does this add security debt? (Any compromises or deferred work?)
- What's the paydown plan?
- Does the current debt level allow this?

If current critical debt > 5 items, defer non-urgent features.

### Engineering hiring
Track debt-per-engineer ratio:
- >10 items per engineer → hire more (or deprioritize)
- <3 items per engineer → good posture, focus on features

### Investment decisions
When allocating budget:
- Debt > certain threshold → invest in security tooling
- Tooling ROI = hours saved from debt reduction

---

## Communicating Debt to Stakeholders

### To engineering
Show the ledger. Make debt visible. Assign owners.

### To product
"We have 2 critical items that must be fixed before the enterprise launch."

### To executives
- Risk in dollars (Expected Loss = Likelihood × Impact $)
- Trend over time
- Benchmark against industry
- Cost of fixing vs cost of breach

### To board / investors
- SOC 2 compliance status (affects enterprise sales)
- Critical items (affects risk posture)
- Investment needed

### To customers
- Transparent policy: "We fix critical issues within X days"
- Don't share specific debt items
- Share outcomes: "We closed N security findings last quarter"

---

## Debt and Incidents

When an incident happens:
1. Check if the root cause was in the debt ledger
2. If yes: the debt was a known risk, review why it wasn't fixed
3. If no: add it to the ledger AND investigate why it wasn't detected earlier

Incidents validate (or invalidate) your debt prioritization. Use them to
calibrate.

---

## The Debt Anti-Patterns

### 1. "Ignore it, it's not critical"
Low severity items rot. They accumulate until a chain forms a critical path.

### 2. "We'll revisit later"
Without a concrete date, "later" = never.

### 3. "The team will fix it when they have time"
Without explicit capacity, fix time is zero.

### 4. "We don't have debt"
Everyone has debt. If you can't see it, you're not looking.

### 5. "Fix the easy ones first"
Easy items let the hard ones fester. Prioritize by priority score, not effort.

### 6. "Fix everything at once"
Overwhelm kills progress. Systematic paydown works.

### 7. "Outsource to consultants"
Consultants can audit, but fixing requires ownership. Debt you don't own
doesn't get fixed.

---

## Audit Checklist

### Debt tracking
- [ ] Security debt ledger exists
- [ ] Ledger updated monthly (minimum)
- [ ] Each item has owner, deadline, effort
- [ ] Items scored with priority formula
- [ ] Oldest item is < 6 months (aim for < 3 months)

### Debt reduction
- [ ] Debt budget allocated (% of capacity)
- [ ] Monthly net debt is negative (paying down faster than incurring)
- [ ] Quarterly paydown sprints scheduled
- [ ] Accepted risks documented with review dates

### Communication
- [ ] Debt ledger visible to engineering team
- [ ] Monthly summary shared with leadership
- [ ] Debt metrics reviewed in leadership meetings
- [ ] Incidents correlated with debt ledger

---

## See Also

- [SECURITY-MATURITY.md](SECURITY-MATURITY.md) — maturity-based debt budgets
- [SECURITY-ECONOMICS.md](SECURITY-ECONOMICS.md) — cost of breach calculations
- [INCIDENT-RESPONSE.md](INCIDENT-RESPONSE.md) — debt correlation with incidents
