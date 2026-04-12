# Cognitive Operators — The Full Library

Operators are atomic cognitive moves that find vulnerabilities. They are composable,
transferable across contexts, and each has explicit triggers, failure modes, and a
copy-paste prompt module for subagents.

This library has **17 operators** organized into five families:
1. **Enumeration operators** — find what exists
2. **Invariant operators** — find implicit assumptions
3. **Identity operators** — trace trust chains
4. **Failure operators** — probe degradation
5. **Creative operators** — break out of checklist mode

---

## 1. Enumeration Operators

### ⊘ Surface-Transpose — "What if I came from the other door?"

**Definition:** Protection verified on one surface (API) may not exist on another
(webhook, cron, CLI, admin UI, import, old API version).

**Triggers:**
- Auth described as "applied in middleware"
- Multiple ways to reach the same data
- Comments saying "only accessed via UI"

**Prompt module:**
```
[OPERATOR: ⊘ Surface-Transpose]
1) List EVERY way to reach this feature/data: UI, API, webhook, CLI, CSV
   import, cron, OG image, debug, admin, old API version, test-only.
2) For each, determine: what authorization is enforced here?
3) Find the weakest. That's the attack surface.
4) Output: table of (surface, auth mechanism, weakness).
```

**Real finding (caam):** OAuth refresh logged error bodies verbatim. Error path
was an invisible secret exfiltration surface nobody had audited.

### ⊘ Shadow-Codebase Scan — "What's still alive but undocumented?"

**Definition:** Old API versions, deprecated routes, test fixtures, legacy code
paths that still compile but aren't in the current mental model.

**Triggers:**
- Project older than 1 year
- Version bumps in API (`/api/v1`, `/api/v2`)
- Migration history shows many renames

**Prompt module:**
```
[OPERATOR: Shadow-Codebase Scan]
1) List all API versions. Are old ones still routable?
2) Find test-only routes (e.g., /api/test/*, /api/dev/*). Are any live in prod?
3) Grep for DEPRECATED comments. Is the deprecated code actually unreachable?
4) Check for .bak, .old, _v1 files in the source tree.
5) Look for commented-out routes that were actually just disabled locally.
```

### ⊘ Expansion-Surface Hunt — "What does this feature pull in?"

**Definition:** Every new dependency, third-party integration, or imported package
expands the attack surface. Audit the dependencies themselves.

**Triggers:**
- New npm/pip/cargo package added
- Dependency upgrade
- Third-party SaaS integrated

**Prompt module:**
```
[OPERATOR: Expansion-Surface Hunt]
For each new dependency:
1) What data does it receive?
2) What data does it return?
3) What network calls does it make?
4) Does it store data outside the app?
5) Has the package itself been security-audited?
6) Supply chain: is this the real package or a typosquat?
```

---

## 2. Invariant Operators

### ≡ Invariant-Extract — "What must be true for this to be secure?"

**Definition:** Make implicit assumptions explicit. Each security mechanism depends
on invariants. List them. Attack them individually.

**Triggers:**
- "This is safe because X" — what if X is wrong?
- Architecture review
- Any comment starting with "Assumes..."

**Prompt module:**
```
[OPERATOR: ≡ Invariant-Extract]
For this security mechanism, list every invariant it depends on:
- Network: is the service actually unreachable from that network?
- Clients: do they always send expected data?
- Storage: is the DB state always consistent with cache?
- Timing: are all operations strictly ordered?
For each invariant: "What if this were false? Who could make it false?"
Output: list of (invariant, who-could-violate, attack-if-violated).
```

**Real finding (jeffreys-skills.md):** "All our prices come from Stripe plan IDs"
— but one code path accepted `price_id` from the request body and validated against
a LIST of allowed IDs. The list was updated, but the validation wasn't.

### ≡ Normalize-First — "Is the canonical form the boundary?"

**Definition:** Validation on raw input is already bypassed. Find every check that
operates on un-normalized data.

**Triggers:**
- String length checks
- Path checks
- Email comparisons
- Filename validation
- URL comparison

**Prompt module:**
```
[OPERATOR: ≡ Normalize-First]
For every validation check:
1) Is the input canonicalized first? (trim, NFC unicode, URL decode, symlink resolve)
2) Is the canonical form used for BOTH validation AND action?
3) Can attacker provide non-canonical input that passes check but acts differently?
Output: bugs where validation and action see different forms of the same input.
```

### ≡ Mass-Assignment Probe — "What fields can the client write?"

**Definition:** Spread-operator updates (`{...body}`), unknown-field tolerance, DTO
without explicit allowlist → any column becomes writable.

**Triggers:**
- `db.update(...).set({...body})` or `Object.assign(user, body)`
- Zod schema without `.strict()`
- Python dict unpacking

**Prompt module:**
```
[OPERATOR: ≡ Mass-Assignment Probe]
For every PATCH/PUT/POST route:
1) What fields does the client send?
2) What fields are written to DB?
3) Is there an explicit column allowlist?
4) Can the client set: role, isAdmin, subscriptionStatus, orgId, ownerId?
5) Does Zod use .strict() to reject unknown fields?
Output: routes that let clients write privileged columns.
```

---

## 3. Identity Operators

### ⊙ Identity-Chain Trace — "Is the identity consistent end-to-end?"

**Definition:** Auth starts with a claim (JWT, custom_id, payer_id, email) and
propagates to actions (webhook updates subscription for user X). Trace the chain;
anywhere the claim can be substituted without re-verification is a hijacking vector.

**Triggers:**
- Payment webhooks with custom_id / metadata
- Multi-provider billing (Stripe + PayPal)
- OAuth/SSO identity linking
- Email-based lookups

**Prompt module:**
```
[OPERATOR: ⊙ Identity-Chain Trace]
For each webhook/auth flow:
1) What identity claim arrives? (custom_id, sub, email, payer_id)
2) What does the handler use it for? (look up user, update sub, grant access)
3) Is the claim cross-verified against other identity fields?
4) Is the claim attacker-controllable? (almost always yes for custom_id)
5) Can an attacker craft a claim pointing to a victim's userId?
Output: identity propagation diagram with each hop marked safe/unsafe.
```

**Real finding (jeffreys-skills.md):** PayPal `custom_id` attacker-controllable →
subscription hijacking. Fix cross-references `custom_id`, `payer_id`, and stored
`customerId` with explicit rejection on mismatch.

### ⊙ Tenant-Leak Probe — "Can Tenant A see Tenant B?"

**Definition:** Multi-tenant boundary violations via direct DB access, aggregate
queries, shared caches, or app-layer bugs.

**Triggers:**
- Multi-tenant system
- Shared resources (templates, skill packs, analytics)
- Cross-tenant admin operations

**Prompt module:**
```
[OPERATOR: ⊙ Tenant-Leak Probe]
For each cross-tenant operation:
1) Does RLS enforce the tenant boundary?
2) Does the app layer ALSO check the tenant?
3) Does the cache key include the tenant ID?
4) Can a user infer other-tenant data from aggregates (counts, averages)?
5) Does the deletion cascade across all tenant data?
Test: spin up 2 tenants, try to make Tenant A see/modify Tenant B's data.
```

### ⊙ Self-Heal-Up Detector — "Does the code auto-promote?"

**Definition:** Reconciliation loops that raise privilege. The worst kind of bug:
revocation silently undone.

**Triggers:**
- Middleware that writes role/status
- "Sync from IdP" code
- Email-based whitelists

**Prompt module:**
```
[OPERATOR: Self-Heal-Up Detector]
Grep for writes to role, isAdmin, subscriptionStatus, tier, permissions.
For each write:
1) What condition triggers it?
2) Is it raising or lowering privilege?
3) If raising: is there a corresponding audit log?
4) If raising: will it undo an explicit revocation?
Output: CRITICAL for any auto-raise; HIGH for auto-raise without audit.
```

---

## 4. Failure Operators

### ⟂ Fail-Open Probe — "What happens if this dependency dies?"

**Definition:** Every dependency has a failure mode. Find the code's response and
check fail-closed vs fail-open.

**Triggers:**
- `try { ... } catch { ... }`
- `|| fallback` on permission/subscription check
- `redis.get(...)` without fallback defined

**Prompt module:**
```
[OPERATOR: ⟂ Fail-Open Probe]
For each external dependency (Redis, DB, Stripe, PayPal, JWKS, OAuth provider,
subscription service, cache, rate limiter):
1) Find the failure handler
2) Determine: fail-closed (deny) or fail-open (allow)?
3) For fail-opens: what's the attack? (e.g., DoS Redis → unlimited brute force)
4) Report CRITICAL for any fail-open on auth/billing/rate-limit paths
Output: table of (dependency, failure handler, mode, attack if fail-open).
```

**Real finding (jeffreysprompts_premium):** Rate limiter caught Redis errors and
returned `{ allowed: true, fallback: true }`. DoS Redis → unlimited login attempts.

### ⟂ Recovery-Path Walk — "Is the recovery path audited?"

**Definition:** Every invariant on the primary path must be re-enforced on
reconciliation, replay, restore. Recovery paths are where audits go to die.

**Triggers:**
- Reconciliation cron exists
- Webhook replay endpoint
- Database restore procedure
- Manual admin override for bad state

**Prompt module:**
```
[OPERATOR: ⟂ Recovery-Path Walk]
For each invariant enforced on the primary path (signature verification,
idempotency, authorization, rate limit):
1) Find the recovery/replay/reconcile code path
2) Is the invariant re-enforced there?
3) If via different mechanism: is that mechanism equivalent?
4) Does the recovery path have its own audit log?
Output: list of invariants violated on recovery paths.
```

### ⟂ Timing-Oracle Hunt — "Can I infer state from timing?"

**Definition:** Response time differences reveal internal state. bcrypt on valid
user but not missing user. DB query on cache miss but not cache hit.

**Triggers:**
- Password checks
- Email/username lookup
- Promo code validation
- Password reset

**Prompt module:**
```
[OPERATOR: ⟂ Timing-Oracle Hunt]
For each sensitive lookup:
1) Does the response time differ based on whether the target exists?
2) Does the response time differ based on which step failed?
3) Can you measure it externally? (>10ms difference is detectable)
Test: send 100 requests for real user + 100 for fake user. Compare p50 latencies.
```

### ⟂ Error-Oracle Test — "Do errors leak state?"

**Definition:** Distinct error messages for distinct states = enumeration oracle.

**Triggers:**
- Login / registration / password reset
- Email / username / promo code validation
- Subscription lookup

**Prompt module:**
```
[OPERATOR: ⟂ Error-Oracle Test]
For each auth-related endpoint:
1) List all possible error responses
2) Do they distinguish "exists but wrong password" vs "doesn't exist"?
3) Do they distinguish "user exists" vs "user exists but email unverified"?
4) Do they distinguish "promo code valid" vs "promo code expired" vs "not eligible"?
Fix: always return identical generic error for any failure state.
```

### ⟂ Recovery-Inconsistency — "Do migrations preserve invariants?"

**Definition:** Schema migrations, data backfills, and batch updates often skip
app-layer validation. Audit the migration files themselves.

**Triggers:**
- Migration files with UPDATE or INSERT
- Data backfill scripts
- Schema changes that set defaults

**Prompt module:**
```
[OPERATOR: ⟂ Recovery-Inconsistency]
For each migration file:
1) What data does it write?
2) Does it respect existing RLS policies?
3) Does it preserve the invariants of the target tables?
4) If it sets defaults: are they safe? (e.g., default role = 'viewer' not 'admin')
5) Is it running as service_role? What checks does it bypass?
```

---

## 5. Creative Operators

### ⊕ Creative-Transposition — "How would [different attacker] see this?"

**Definition:** Shift attacker persona. Different motivations find different bugs.

**Prompt module:**
```
[OPERATOR: ⊕ Creative-Transposition]
Re-audit the same code from 5 attacker personas:
1) Bored user — what edge cases break it for fun?
2) Financial fraudster — how do I get free service / commit refund fraud?
3) Competitor — how do I exfiltrate data or disrupt?
4) Disgruntled ex-employee — what backdoors do I know?
5) Nation-state — what long-term access do I plant?
For each: what's the MOST valuable thing they'd go after? How would they do it?
Each persona sees different vulns. Use all 5.
```

### ⊕ Cross-Domain Transposition — "Has this bug happened in a different domain?"

**Definition:** Vulnerability patterns recur across domains. Database race conditions
are isomorphic to filesystem race conditions. Apply patterns from one domain to
another.

**Prompt module:**
```
[OPERATOR: ⊕ Cross-Domain Transposition]
For each feature, ask: has this bug been documented in a different domain?
- Race conditions: DB TOCTOU ↔ filesystem ↔ cache
- Injection: SQL ↔ template ↔ LDAP ↔ NoSQL ↔ LLM prompt
- Escalation: OS sudo ↔ DB role ↔ OAuth scope ↔ LLM tool use
- Bypass: header spoof ↔ TLS downgrade ↔ protocol downgrade
Apply each known pattern from other domains.
```

### ⊕ Impossible-Question Probe — "Ask a question you believe has no answer"

**Definition:** Assume the system is bulletproof, then ask a provocative question.
Let the search find the answer.

**Prompt module:**
```
[OPERATOR: ⊕ Impossible-Question Probe]
Write down 10 questions you believe have no answer:
- "Can a free user create a Stripe checkout for $0?"
- "Can a user's JWT be accepted for a different user's session?"
- "Can a deleted user still receive webhook events?"
- "Can a webhook signed for Tenant A update Tenant B's subscription?"
For each, search the codebase for the answer. Trust the code, not your belief.
```

### ⊕ Attack-Chain Composer — "What if I compose 3 low-severity findings?"

**Definition:** A LOW bug + a LOW bug + a LOW bug can = CRITICAL chain. Look for
compositions.

**Prompt module:**
```
[OPERATOR: ⊕ Attack-Chain Composer]
Take your LOW and MEDIUM findings. For each pair, ask:
- Does bug A enable bug B?
- Does bug B give access that bug A alone wouldn't?
- Does bug C (any other) provide the missing step?
The worst breaches are compositions of "not worth fixing" findings.
Output: attack chains that elevate low bugs to critical.
```

### ⊕ Chain-Comp — "Compose operators into hunts"

**Definition:** Meta-operator. Apply two or more operators in sequence to find
higher-order bugs.

**Prompt module:**
```
[OPERATOR: ⊕ Chain-Comp]
Try these chains:
1) ⊘ Surface-Transpose → ⟂ Fail-Open Probe
   (Find every auth surface → does it fail-closed?)
2) ⊙ Identity-Chain Trace → ≡ Invariant-Extract
   (Trace identity flow → what assumptions does each hop make?)
3) ≡ Normalize-First → ✂ Parser-Diverge
   (Find normalizations → do two layers normalize differently?)
4) ⊘ Shadow-Codebase Scan → ⊙ Tenant-Leak Probe
   (Find forgotten routes → can they cross tenants?)
Each chain finds bugs neither operator would find alone.
```

---

## How to Use This Library

1. **Start with the kernel** ([KERNEL.md](KERNEL.md)) — verify all 10 axioms hold
2. **Run enumeration operators** — build a complete surface map
3. **Run invariant operators** — extract implicit assumptions
4. **Run identity operators** — trace every trust chain
5. **Run failure operators** — probe every dependency
6. **Run creative operators** — find what checklists miss
7. **Chain operators** — compose for higher-order bugs

Each operator is ~15-30 minutes of focused audit time. A full sweep of all 17
operators on a medium-sized SaaS is 4-8 hours, and will find findings that no
checklist-based audit would catch.
