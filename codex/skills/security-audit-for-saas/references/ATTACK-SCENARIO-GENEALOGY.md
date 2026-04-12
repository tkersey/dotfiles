# Attack Scenario Genealogy

The worst breaches aren't single bugs. They're compositions — a LOW bug + a
LOW bug + a LOW bug = CRITICAL chain. This file documents how to find and
analyze these attack genealogies.

---

## The Core Idea

Most auditors list bugs individually, each with its own severity. A bug
marked LOW might be dismissed as "not worth fixing."

But bugs compose. Three LOW findings can form a chain that achieves a CRITICAL
outcome.

**Example:**
- LOW: stale cache after subscription cancel (users see 5 min of stale status)
- LOW: admin action via query parameter
- LOW: admin endpoint lacks rate limiting

Composed: attacker uses query parameter to trigger admin action that extends
their subscription in the stale cache window, using rate-limit-free endpoint
to automate. Result: CRITICAL billing bypass.

---

## The Composition Rules

### Rule 1: Bugs Compose When They Share State
If bug A affects state S, and bug B affects state S, they can be chained if
S is the attacker's goal state.

### Rule 2: Bugs Compose Along the Kill Chain
ATT&CK tactics (initial access → persistence → privilege escalation → ...)
are inherently composable. An "initial access" bug + "persistence" bug >
either alone.

### Rule 3: Bugs Compose Across Layers
Network bug + app bug + DB bug composed can defeat defense-in-depth. Each
alone wouldn't, because another layer catches them.

### Rule 4: Timing Bugs Are Force Multipliers
A timing bug (race condition, TOCTOU, cache staleness) turns many "benign"
bugs into exploitable ones.

### Rule 5: Enumeration Bugs Unlock Other Bugs
A bug that reveals user IDs makes IDOR bugs exploitable. A bug that reveals
table names makes injection bugs exploitable.

---

## The Genealogy Diagram

For each critical asset, build a diagram of attack chains that could reach it.

```
Goal: Access to all customer payment data

Chain 1:
[Low: Email enumeration] → [Low: Password reset via email]
                        → [Medium: No MFA enforcement]
                        → [High: Admin access from user account via role escalation bug]
                        → [Critical: Read all payments]

Chain 2:
[Low: Webhook replay]  → [Medium: No event ID dedup]
                       → [Critical: Create subscription for victim]

Chain 3:
[Low: Stale cache]     → [Medium: Admin status in cache]
                       → [High: Admin endpoints without re-check]
                       → [Critical: Admin actions]
```

Each chain reveals that seemingly-low bugs are actually critical when chained.

---

## How to Hunt Genealogies

### Step 1: List All Findings
Start with an existing audit report. Don't prioritize yet; just list.

### Step 2: Categorize by Effect
Group findings by what they achieve:
- Information leakage
- State mutation
- Timing windows
- Resource consumption
- Privilege escalation
- Persistence

### Step 3: Pair Them
For each pair (A, B), ask: "Does A enable B, or does B enable A?"

Enables examples:
- Email enumeration enables credential stuffing
- Stale cache enables entitlement bypass
- Timing oracle enables password discovery
- Missing rate limit enables brute force
- Error message leak enables SQL injection

### Step 4: Chain Them
Now try triples. Does A enable B which enables C?

The dimensionality grows fast. For 10 findings, there are:
- 10 singletons
- 45 pairs
- 120 triples

Focus on chains that reach a high-value target.

### Step 5: Score the Chain
A chain's severity = max severity of the goal + complexity of the chain.
A 3-step chain reaching CRITICAL is more actionable than a 7-step chain to
the same goal, because it's easier to execute.

---

## Real-World Chain Examples

### Chain 1: The $0 Premium
- **Low 1:** Stripe webhook handler trusts event.metadata.userId
- **Low 2:** No account ID verification
- **Medium 1:** Stale subscription cache

**Composed:**
1. Attacker creates $0 product in their own Stripe account
2. Checkout session with `metadata.userId = victim_id`
3. Completes $0 "purchase"
4. Webhook fires, handler trusts metadata
5. Victim's subscription upgraded
6. Cache goes stale; admin actions don't notice

**Severity of chain:** CRITICAL (billing bypass affecting any user)

### Chain 2: The Admin Takeover
- **Low 1:** Email enumeration via login errors
- **Low 2:** Password reset token in URL (leaked via Referer)
- **Low 3:** Password reset doesn't require MFA
- **Medium 1:** Admin role based on email whitelist + `isAdmin` flag

**Composed:**
1. Attacker enumerates emails via login
2. Finds admin's email
3. Attacker sends a phishing email that hosts an image from attacker's domain
4. Admin clicks; Referer leaks their password reset token (if they recently reset)
5. Attacker uses token to reset password
6. No MFA required on reset
7. Attacker logs in as admin

**Severity of chain:** CRITICAL (full admin compromise)

### Chain 3: The Cross-Tenant Leak
- **Low 1:** Aggregate query leaks user count per tenant
- **Low 2:** User ID format is sequential (not UUIDs)
- **Medium 1:** RLS missing on one non-obvious table

**Composed:**
1. Attacker queries aggregate endpoint to identify target tenant
2. Uses sequential IDs to guess target's user IDs
3. Queries the table without RLS to get their data

**Severity of chain:** HIGH (cross-tenant data exposure)

---

## The "Meaningless Alone" Paradox

The hardest-to-find chains involve bugs that seem meaningless alone.

**Example bugs that individually are dismissed:**
- "Oh, that's just a minor rate limit issue"
- "Error messages slightly differ, but nothing sensitive"
- "Cache staleness is 5 minutes max"
- "Admin action is manually triggered, no API"

**But composed:**
- Rate limit bypass + error enumeration = credential stuffing
- Cache staleness + admin action = authorization bypass window

The fix: Don't dismiss LOW findings. Check if any can chain with MEDIUM+
findings.

---

## The Composition Audit

After your normal audit, spend 30-60 minutes on composition audit:

1. **Print all findings** on sticky notes or in a spreadsheet
2. **Group by effect** (what state they affect)
3. **For each pair**, ask: does this pair enable an attack neither alone could?
4. **Draw the chain**
5. **Escalate the composed severity** in the report

---

## Graph-Based Analysis

For complex systems, model as an attack graph:
- **Nodes:** system states (pre-compromise, authenticated user, admin, root)
- **Edges:** findings that enable transition between states
- **Goal:** find the shortest path from "no access" to "crown jewel"

Tools:
- **MulVAL** — academic attack graph generator
- **Cauldron** — commercial
- **Custom scripts** — most practical for SaaS

The shortest path identifies the critical fix (fix any one edge in the path
and the attack fails).

---

## Genealogy Pruning

Not all chains are worth documenting. Prune by:

1. **Feasibility:** Is the attack chain actually executable? Skip theoretical.
2. **Cost to attacker:** Attacks costing >$10K are state-actor level.
3. **Observability:** Attacks that are obviously detected are less critical.
4. **Common knowledge:** Skip chains that are well-known (standard OWASP).

Focus on chains that are: feasible, cheap, stealthy, novel.

---

## The Output Format

For each significant chain:

```markdown
## Chain: [Name]

**Individual findings in the chain:**
1. F-010 (LOW): [description]
2. F-023 (LOW): [description]
3. F-041 (MEDIUM): [description]

**Composed attack:**
1. Attacker does X (via F-010)
2. Result enables Y (via F-023)
3. Now attacker can Z (via F-041)

**Composed severity:** HIGH / CRITICAL (vs individual max of MEDIUM)

**Recommended fix:** Fix [which finding] — breaks the chain with least effort.
```

---

## Preventing Future Chains

Beyond fixing specific chains, establish practices to prevent them:

### 1. Standardize defense-in-depth
Every security-critical flow has 3+ independent defenses. A bug in one doesn't
cascade.

### 2. Treat "low severity" with suspicion
"Low" alone doesn't mean "ignore." Check if it pairs with anything.

### 3. Automate chain detection
Build tests that cover attack chains, not just single vulnerabilities.

### 4. Review findings in batches
Individual code review catches single bugs. Batch review of findings catches
chains.

### 5. Red team exercises
Dedicated chain-hunting sessions where the red team specifically composes
findings.

---

## See Also

- [KERNEL.md](KERNEL.md) — Axiom composition
- [CREATIVITY-TRIGGERS.md](CREATIVITY-TRIGGERS.md) — Attack-Chain Composer prompt
- [OPERATORS.md](OPERATORS.md) — ⊕ Chain-Comp operator
- [BREACH-CASE-STUDIES.md](BREACH-CASE-STUDIES.md) — real composed attacks
- [ADVERSARIAL-THINKING.md](ADVERSARIAL-THINKING.md) — attacker mindset
