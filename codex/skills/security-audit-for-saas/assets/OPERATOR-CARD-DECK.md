# Operator Card Deck — Printable Reference

Print these cards. Keep them near your desk. Pick one when stuck.

---

## ⊘ Surface-Transpose

**When stuck:** "What if I came from the other door?"

**Ask:** For this feature, what are ALL the ways to reach it?
- UI
- API
- Webhook
- CLI
- Batch import
- Cron
- OG image
- Admin
- Old API version

**Output:** The weakest surface = attack path.

---

## ⟂ Fail-Open Probe

**When stuck:** "What happens if this dependency dies?"

**Ask:** For each dependency (Redis, DB, OAuth, Stripe, JWKS):
- Find the error handler
- Fail-closed or fail-open?
- If fail-open, what's the attack?

**Output:** Any fail-open on auth/billing/rate-limit = CRITICAL.

---

## ⊙ Identity-Chain Trace

**When stuck:** "Is the identity consistent end-to-end?"

**Ask:** For each auth flow:
- What identity claim arrives?
- Is it cross-verified?
- Can the claim be substituted?
- Is the claim attacker-controllable?

**Output:** Any trustable-looking claim that isn't verified = hijacking vector.

---

## ≡ Invariant-Extract

**When stuck:** "What must be true for this to be secure?"

**Ask:** For each security mechanism:
- List the implicit assumptions
- For each: "What if this is wrong?"
- For each: "Who could make it wrong?"

**Output:** Explicit assumption list. Each one testable.

---

## ✂ Parser-Diverge

**When stuck:** "Where do two parsers see the same input differently?"

**Ask:** Find every duplicate parsing:
- Proxy path vs rate-limiter path
- Frontend Zod vs backend Zod
- Config-time vs runtime validator
- Stripe vs PayPal handlers

**Output:** Diff each pair. Any disagreement = bypass.

---

## ⊕ Creative-Transposition

**When stuck:** "How would a different attacker see this?"

**Apply 5 personas:**
1. Bored user — weird inputs
2. Financial fraudster — free service
3. Competitor — data exfil
4. Disgruntled ex-employee — backdoors
5. Nation-state — persistence

**Output:** 5 different attack ideas.

---

## Shadow-Codebase Scan

**When stuck:** "What's still alive but forgotten?"

**Find:**
- Old API versions (`/api/v1` if `v2` exists)
- Test fixtures live in prod
- Deprecated feature flags
- Commented-out routes
- `.old` / `.bak` files

**Output:** Unaudited code paths.

---

## Normalize-First

**When stuck:** "Is the canonical form the boundary?"

**Check every validation:**
- Is input normalized BEFORE check?
- Is normalization applied to both check and use?
- Can attacker provide non-canonical input?

**Output:** Validation/action divergences.

---

## Mass-Assignment Probe

**When stuck:** "What fields can the client write?"

**For each PATCH/PUT/POST:**
- What fields does the client send?
- What fields are written to DB?
- Is there an explicit allowlist?
- Can the client set: role, isAdmin, orgId?

**Output:** Routes allowing privileged field writes.

---

## Tenant-Leak Probe

**When stuck:** "Can Tenant A see Tenant B?"

**Test:**
- Spin up 2 test tenants
- As A, try every endpoint
- Try direct DB access
- Try aggregate queries
- Try shared caches

**Output:** Any successful cross-tenant read/write.

---

## Self-Heal-Up Detector

**When stuck:** "Does the code auto-promote?"

**Grep for:** writes to role, isAdmin, subscriptionStatus, tier

**For each write:**
- Raising or lowering privilege?
- If raising: is there audit?
- If raising: does it undo revocations?

**Output:** Self-heal-up patterns = CRITICAL.

---

## Error-Oracle Test

**When stuck:** "Do errors leak state?"

**For each auth endpoint:**
- List all error responses
- Do they distinguish user existence?
- Do they distinguish verified/unverified?
- Same shape for all failures?

**Output:** Enumeration oracles.

---

## Timing-Oracle Hunt

**When stuck:** "Can I infer state from timing?"

**Test:**
- Does response time differ by user existence?
- Does it differ by which check failed?
- >10ms difference is detectable

**Output:** Side-channel oracles.

---

## Recovery-Path Walk

**When stuck:** "Is the recovery path audited?"

**For each invariant on primary path:**
- Find the recovery/replay/reconcile code
- Is the invariant re-enforced?
- Is the recovery audited?

**Output:** Recovery-path bypass vectors.

---

## Recovery-Inconsistency

**When stuck:** "Do migrations preserve invariants?"

**For each migration file:**
- What does it write?
- Does it respect RLS?
- What service role does it run as?
- What app-layer checks does it bypass?

**Output:** Migration-layer bugs.

---

## Impossible-Question Probe

**When stuck:** "Ask a question you believe has no answer."

**Write 10 questions you think are impossible:**
- Can a deleted user receive webhooks?
- Can a free user flip to active without payment?
- Can a webhook for Tenant A update Tenant B?
- Can an OG image leak user data?

**For each:** search the code. Trust the code, not your belief.

**Output:** Surprise findings.

---

## Chain-Comp (Meta-Operator)

**When stuck:** "Compose two operators."

**Try chains:**
- Surface-Transpose → Fail-Open Probe
- Identity-Chain → Invariant-Extract
- Normalize-First → Parser-Diverge
- Shadow-Codebase → Tenant-Leak

**Output:** Composed findings neither operator would find alone.
