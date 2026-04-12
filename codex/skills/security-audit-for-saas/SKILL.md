---
name: security-audit-for-saas
description: >-
  Audit SaaS billing security: payment bypass, webhook integrity, auth gaps, RLS,
  secrets. Use when "security audit", "billing security", or pre-launch review.
---

<!-- TOC: Kernel | Operators | Prompt | Methodology | 15 Domains | Creativity | Anti-Patterns | References -->

# Security Audit for SaaS

> **Core Insight:** SaaS security failures cluster around billing bypass, auth gaps, and
> stale-cache entitlement errors -- not just OWASP generics. This skill operationalizes
> 130+ real vulnerabilities found, diagnosed, and fixed across production SaaS applications
> (jeffreys-skills.md, jeffreysprompts_premium, midas_edge, fix_my_documents, and others).

> **This is not a checklist. It is a cognitive toolkit.** Checklists find the bugs you
> already know exist. The operators, creativity triggers, and attack-scenario catalogs
> below find the bugs that haven't been invented yet in your codebase.

---

## THE SECURITY KERNEL (Axioms)

Every audit must assume these axioms. They are load-bearing -- if you skip one, you
will miss whole classes of vulnerabilities.

<!-- SECURITY_AUDIT_KERNEL_START v1.0 -->

**Axiom 1 — Every fail-open is a DoS pivot.**
If a dependency fails (Redis, Stripe, JWKS, subscription service), what does the code
do? If it degrades to "allow," then degrading the dependency unlocks the gate. The
attacker's first move is to break Redis, not to break auth.

**Axiom 2 — Duplicate parsers diverge → smuggling.**
If two layers parse the same data (proxy vs route, middleware vs rate-limiter, URL
validator vs fetch), their interpretations will drift over time. The smallest drift
becomes a bypass gadget. Single-source-of-truth parsing is a security property.

**Axiom 3 — Normalize before validate, always.**
Whitespace, unicode, URL encoding, trailing slashes, case-folding, symlinks. The
canonical form IS the security boundary. Validation that operates on raw input is
already bypassed.

**Axiom 4 — Self-heal down, never up.**
Reconciliation loops that raise privilege (re-add admin flag, re-enable expired role,
re-link subscription) undo revocations and create un-killable escalation paths. Drift
should always decay toward lower privilege.

**Axiom 5 — Every error is an oracle.**
Auth responses must be indistinguishable across account states. "Invalid password" vs
"user not found" is a free email enumeration service. Timing differences between
"user exists" and "user missing" is the same oracle by a different channel.

**Axiom 6 — Presence-only header checks are worthless.**
Trusting `X-Admin: true`, `Authorization: anything`, `CF-Access-JWT-Assertion:
anything`, or `X-Real-IP` without cryptographic verification. Headers are
attacker-controlled at L7 unless you prove otherwise.

**Axiom 7 — The recovery path is a shadow codebase.**
Every invariant on the primary path (signature verification, idempotency,
authorization) must be re-enforced on the reconciliation cron, the migration runner,
the webhook replay, and the database restore. Recovery paths are where audits go to
die.

**Axiom 8 — Attack surfaces expand faster than defenses.**
Webhooks, CLIs, import/export, batch jobs, OG-image endpoints, admin APIs, old API
versions, debug endpoints, cron secrets -- each was added without a security review.
Enumerate ALL surfaces before auditing any.

**Axiom 9 — Prices, identities, and entitlements are server-side, period.**
Any value the client can modify is attacker-controllable. Prices, plan IDs, user IDs,
org IDs, roles, feature flags -- all must be derived from server-authoritative state,
not request bodies.

**Axiom 10 — Multi-tenancy is RLS + belt-and-suspenders app-layer checks.**
RLS alone is insufficient (service role key bypasses it). App-layer checks alone are
insufficient (devs forget). You need both, and you need to verify both at every
boundary where data crosses tenant lines.

<!-- SECURITY_AUDIT_KERNEL_END -->

---

## COGNITIVE OPERATORS (The Thinking Moves)

These are composable **mental moves** that find vulnerabilities. They are not
checklists. Apply them to any system, any domain, any stack. Each operator has
triggers (when to use it), failure modes (when it misleads you), and a prompt module
(copy-paste for sub-agents). See [OPERATORS.md](references/OPERATORS.md) for the full
card library (17 operators).

### ⊘ Surface-Transpose — "What if I came from the other door?"

**Definition:** Protection verified on one surface (API) may not exist on another
surface (webhook, cron, CLI, admin UI, batch import, old API version).

**Triggers:**
- Codebase has webhooks + APIs + admin + CLI + batch jobs
- Auth is described as "applied in middleware"
- You see `/api/v2/*` -- does `/api/v1/*` still work?
- Feature exists in UI -- does it exist in CSV import?

**Failure modes:**
- Forgetting that cron jobs run as "system" (often root-like)
- Assuming deprecated = disabled
- Missing the "OG image" or "health check" or "telemetry" endpoints

**Prompt module:**
```
[OPERATOR: ⊘ Surface-Transpose]
1) List EVERY way to reach this feature/data: UI, API, webhook, CLI, CSV
   import, cron, OG image, debug, admin, old API version, test-only.
2) For each, ask: "What authorization is enforced here?"
3) Find the weakest. That's the attack surface.
```

### ⟂ Fail-Open Probe — "What happens if this dependency dies?"

**Definition:** Every dependency (cache, DB, OAuth provider, rate limiter) has a
failure mode. Find the code's response and check if it's fail-closed or fail-open.

**Triggers:**
- You see `try { ... } catch { return /* something */ }`
- You see `|| fallback` on a permission or subscription check
- You see `redis.get(...)` without a fallback defined

**Failure modes:**
- Assuming "the error handler catches it" means it's safe
- Missing secondary fail-opens (e.g., Redis fails → in-memory fallback fails across
  instances → effectively unlimited)

**Prompt module:**
```
[OPERATOR: ⟂ Fail-Open Probe]
For each external dependency (Redis, DB, Stripe, PayPal, JWKS, OAuth provider,
subscription service, cache):
1) Find the failure handler
2) Determine: fail-closed (deny) or fail-open (allow)?
3) For fail-opens: what's the attack? (e.g., DoS Redis → unlimited brute force)
4) Report CRITICAL for any fail-open on auth/billing/rate-limit paths
```

### ≡ Invariant-Extract — "What must be true for this to be secure?"

**Definition:** Make the implicit assumptions explicit. Each security mechanism
depends on invariants. List them. Attack them individually.

**Triggers:**
- "This is safe because X" — what if X is wrong?
- Architecture review ("the service won't be reached from Y")
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
```

### ✂ Parser-Diverge — "Where do two parsers see the same input differently?"

**Definition:** Whenever two layers parse the same input, they will diverge. The
smallest divergence becomes a bypass.

**Triggers:**
- Proxy + middleware + route layer each check the same path
- URL validator (config-time) and fetcher (delivery-time)
- Frontend regex + backend regex for email/phone/URL
- Two languages deserialize the same JSON

**Prompt module:**
```
[OPERATOR: ✂ Parser-Diverge]
Find every place where the same input is parsed by two layers:
- Proxy path matcher vs rate-limiter path matcher
- CORS origin validator vs CSRF origin validator
- Config-time URL validator vs runtime fetcher
- Frontend Zod schema vs backend Zod schema
Diff the two parsers. Any edge case they disagree on is a bypass.
```

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
2) What does the handler use it for? (look up user, update sub)
3) Is the claim cross-verified against other identity fields? (e.g., payer_id
   matches stored customerId)
4) Is the claim attacker-controllable? (almost always yes for custom_id)
5) Can an attacker craft a claim pointing to a victim's userId?
```

### ⊕ Creative-Transposition — "How would [different attacker] see this?"

**Definition:** Shift attacker persona. A "bored user" finds different bugs than a
"financial fraudster" finds different bugs than a "nation-state" finds different bugs
than a "disgruntled insider."

**Triggers:**
- Audit feels stuck
- All obvious checks pass
- Need to find novel vulns

**Prompt module:**
```
[OPERATOR: ⊕ Creative-Transposition]
Re-audit the same code from 5 attacker personas:
1) Bored user — what edge cases break it for fun?
2) Financial fraudster — how do I get free service?
3) Competitor — how do I exfiltrate data or disrupt?
4) Disgruntled ex-employee — what backdoors do I know?
5) Nation-state — what long-term access do I plant?
Each persona sees different vulns. Use all 5.
```

**See [OPERATORS.md](references/OPERATORS.md) for 11 more operators** including:
Recovery-Path Walk (for webhook reconciliation), Normalize-First (for canonical form
attacks), Timing-Oracle Hunt (for side channels), Self-Heal-Up Detector (for
escalation via reconciliation), Tenant-Leak Probe (for multi-tenancy), Error-Oracle
Test (for enumeration via errors), Recovery-Inconsistency (for migration/replay
gaps), Mass-Assignment Probe (for DTO discipline), Expansion-Surface Hunt (for
serialization attacks), Shadow-Codebase Scan (for deprecated paths), and Chain-Comp
(composing operators into hunts).

## When to Use What

| Need | Skill |
|------|-------|
| SaaS-specific security (billing, subscriptions, entitlements) | **security-audit-for-saas** (this) |
| General codebase quality audit (any domain) | codebase-audit |
| Find bugs and fix iteratively | multi-pass-bug-hunting |
| Payment integration reference | stripe-checkout |
| Database/RLS reference | supabase |

---

## THE EXACT PROMPT

```
Run a security audit of this SaaS application.

Focus areas (in priority order):
1. Payment/billing bypass (can users get service without paying?)
2. Webhook integrity (signature verification, idempotency, race conditions)
3. Auth & authorization (RBAC gaps, TOCTOU in permission checks)
4. Entitlement enforcement (cache staleness, grace period logic)
5. Secrets exposure (env vars, client bundle, health endpoints)
6. Database access control (RLS coverage, missing policies)
7. Web security (redirects, CSRF, SSRF, XSS in user content)

For each finding: file:line, severity, attack vector, and fix.
Use the domain checklists from references/.
```

### Quick Billing-Only Audit

```
Audit payment security only: webhook handlers, checkout flows,
subscription status checks, and entitlement gating.
Top 5 issues, with severity and fix. Under 50 lines.
```

---

## Methodology: The 7-Domain Sweep

Work through domains in this order. Each domain has a detailed checklist in `references/`.

### 1. Payment & Billing ([BILLING.md](references/BILLING.md))

**Key question:** Can a user access paid features without paying?

| Check | What to grep | Why |
|-------|-------------|-----|
| Webhook signatures verified | `constructEvent`, `verify-webhook-signature` | Unsigned webhooks = forged events |
| Prices are server-side | `amount`, `price`, `unit_amount` in route handlers | Client-submitted prices = free service |
| Idempotency via DB constraint | `ON CONFLICT`, `payment_events` | Duplicate webhooks = double-credit |
| Checkout uses FOR UPDATE | `FOR UPDATE`, `advisory` in checkout routes | Race condition = double subscription |
| PayPal custom_id validated | `custom_id`, `validatePayPalUserId` | Attacker-controlled = subscription hijacking |
| Cache invalidated on sub change | cache event types, `after()` callbacks | Stale cache = entitlement mismatch |
| Seat count enforced | `maxSeats`, member addition flow | No check = unlimited free seats |

### 2. Auth & Authorization ([AUTH.md](references/AUTH.md))

**Key question:** Can a user escalate privileges or bypass access controls?

- TOCTOU: Are permission checks inside DB transactions with row locks?
- RBAC: Do billing endpoints require owner (not just admin)?
- CSRF: Does session auth fall back when Authorization header is present?
- Rate limiting: Do token exchange/refresh/revoke have independent limits?
- Timing-safe: Are ALL secret comparisons using `timingSafeEqual`?
- SSO: State param, nonce, redirect validation at every stage?

### 3. Entitlement Enforcement ([ENTITLEMENTS.md](references/ENTITLEMENTS.md))

**Key question:** Does subscription status always reflect reality?

- Server actions check premium tier before allowing premium operations
- Subscription status endpoint handles org-only users correctly
- Grace period uses correct `currentPeriodEnd` (not stale/undefined)
- Unknown provider statuses are logged, not silently swallowed
- Pending checkout state is cleared after completion

### 4. Secrets Management ([KEY-MANAGEMENT.md](references/KEY-MANAGEMENT.md))

**Key question:** Are any secrets accessible outside their intended scope?

- All env access through single `env.ts` module
- Only `NEXT_PUBLIC_*` vars in client code
- No `.env` files with real secrets in git
- Health endpoints show key prefixes only
- SSO configs use redacted types in API responses
- Service role key isolated to admin client function

### 5. Database Access Control ([DATABASE.md](references/DATABASE.md))

**Key question:** Can users read/write data they shouldn't?

- RLS enabled on every table with user data
- Migration coverage validated against full table inventory
- No overly permissive `using (true)` for authenticated role on sensitive tables
- Admin policies don't depend on tables that block their own RLS queries
- Anon role privileges fully revoked

### 6. Web Security ([WEB.md](references/WEB.md))

**Key question:** Are standard web attack vectors mitigated?

- Open redirects: `startsWith("/") && !startsWith("//")` everywhere
- Single shared `getSafeRedirectPath()` used at all redirect points
- SSRF: webhook URLs validated at config-time AND delivery-time
- Markdown: `rehype-sanitize` allowlist (not blocklist)
- Security headers: HSTS, X-Content-Type-Options, Referrer-Policy, Permissions-Policy
- CORS: only intentional `*` endpoints (public, no credentials)

### 7. Infrastructure ([INFRASTRUCTURE.md](references/INFRASTRUCTURE.md))

**Key question:** Do operational patterns introduce vulnerabilities?

- Rate limiters use Redis in serverless (not in-memory)
- DLQ has exponential backoff + max retry count
- Shell commands use `exec.Command` with separate args (no `sh -c` concat)
- Webhook handlers return 200 on errors (prevent retry storms)
- Dunning/batch processors have cursor pagination (no silent truncation)

### 8. Rate Limiting & Abuse Detection ([RATE-LIMITING.md](references/RATE-LIMITING.md))

**Key question:** Can an attacker brute-force, enumerate, or cost-exhaust the system?

- Tiered limits: anon < authenticated < subscriber < CLI; never throttle paying users
- Subscriber short-circuit returns allow BEFORE hitting Redis (don't tax Redis on payers)
- Exponential backoff cooldown on Redis failure (prevents cascading failures)
- Fail-open on Redis outage (CRITICAL: audit whether this is acceptable)
- Abuse signals tracked as multi-signal behavioral detection (not single-metric)
- Admins and `system` source exempt (avoid banning Stripe/PayPal IPs on cert rotation)
- Strict endpoint overrides for checkout/webhook/auth (not global defaults)

### 9. Multi-Tenant Isolation ([MULTI-TENANT.md](references/MULTI-TENANT.md))

**Key question:** Can Tenant A see, modify, or infer Tenant B's data?

- RLS policies enforce tenant boundary on EVERY query (not just some)
- App-layer `requireOrgRole()` checks parallel RLS (belt-and-suspenders)
- Cross-tenant lookups use server-side tenant from session, never request body
- Shared resources (skill packs, templates) have explicit public/private flag
- Aggregate queries (counts, analytics) don't leak other-tenant data by inference
- Test fixtures include at least 2 tenants to catch default-tenant bugs
- Tenant deletion is cascading and audit-logged (GDPR right to be forgotten)

### 10. Third-Party Integration Security ([THIRD-PARTY.md](references/THIRD-PARTY.md))

**Key question:** Is every external boundary cryptographically verified?

- Stripe: HMAC `constructEvent`, raw body preserved
- PayPal: API `verify-webhook-signature`, all 5 headers, 10s timeout
- OAuth providers: error responses are opaque (don't log body → secret leak)
- OAuth: certificate pinning for providers that support it
- Cloudflare Access: verify JWT signature, not header presence
- Supabase: use `getClaims()` not `getSession()` (JWT signature validation)
- Webhook URLs user-supplied: validate at config-time AND delivery-time, shared function
- Third-party API keys: rotation schedule, versioned storage

### 11. Data Security & Privacy ([DATA-SECURITY.md](references/DATA-SECURITY.md))

**Key question:** Is sensitive data classified, protected, and deletable?

- Data classified: public / internal / user / sensitive (PII) / secret
- Encryption at rest for sensitive columns (not just disk-level)
- TLS + cert validation for all external calls
- GDPR right to be forgotten: scripted user deletion with cascade
- Backup restoration access is logged and 2-person-rule for prod
- PII never in error messages, logs, or stack traces
- Analytics queries exclude PII by design (anonymization at query time)
- Data retention policies enforced by cron (not manual cleanup)

### 12. Incident Response & Forensics ([INCIDENT-RESPONSE.md](references/INCIDENT-RESPONSE.md))

**Key question:** When (not if) a breach happens, can you detect, contain, and recover?

- Detection: abuse signal alerts, anomaly detection on billing, RLS denial spikes
- Forensic queries ready: "find users who accessed premium without subscription"
- Refund computation script: "how much did bypassed users cost us?"
- Notification templates: customer, compliance, team, legal
- Rollback procedures: disable a broken webhook handler without full deploy
- Evidence preservation: snapshots, logs, audit trails frozen
- Post-incident RCA template: root cause, blast radius, detection gap, prevention

### 13. Audit Logging & Compliance ([AUDIT-LOGGING.md](references/AUDIT-LOGGING.md))

**Key question:** Can you answer "who did what, when, from where" for any action?

- Schema: actor, action, resource, timestamp, IP, user-agent, request-id, result
- Non-blocking writes: audit log failures don't block user requests
- Sensitive data redacted (no PII, no secrets in log messages)
- Immutable append-only (database triggers prevent UPDATE/DELETE)
- Retention policy (compliance-driven, e.g., 7 years for SOC2)
- Compliance queries: export all actions for user X (GDPR), activity for date range (SOC2)
- Admin actions logged in SEPARATE table (harder to tamper)

### 14. LLM & AI-Specific Security ([LLM-SECURITY.md](references/LLM-SECURITY.md))

**Key question:** If the app uses LLMs, are prompt/tool/output attack vectors covered?

- Prompt injection via user input: structural delimiting, not textual "ignore injections"
- Tool use authorization: each tool call re-verified against user permissions
- Output validation: LLM output treated as untrusted, re-validated before storage/display
- Context window poisoning: untrusted data clearly marked as untrusted
- Model output XSS: HTML/JS from LLM sanitized like any user content
- Model output prompt injection downstream: nested LLM calls re-wrap user text
- Token budget abuse: rate limits per-user on LLM calls (prevent bill bombs)

### 15. API Security ([API-SECURITY.md](references/API-SECURITY.md))

**Key question:** Does every API endpoint enforce validation, authorization, and shape discipline?

- Input validation via Zod schemas at every route (no `as string` casts)
- Field masking: responses strip internal fields (stripeId, hash, internal flags)
- Pagination: cursor-based (not offset, prevents billion-row DoS)
- Mass assignment guarded: explicit column allowlist, not spread-operator
- Error responses don't leak DB schema, stack traces, or library versions
- Idempotency keys honored (X-Request-Id or equivalent)
- PATCH semantics: partial update only specified fields, never full replace
- Unknown fields rejected (strict Zod) to prevent DTO drift attacks

---

## Severity Classification

| Level | SaaS-Specific Criteria | Example |
|-------|------------------------|---------|
| **Critical** | Direct revenue loss or data breach | Billing bypass, subscription hijacking, RLS missing on users table |
| **High** | Exploitable with effort, auth escalation | TOCTOU in RBAC, missing rate limits on auth, secrets in git |
| **Medium** | Limited scope, defense-in-depth gap | Overly permissive RLS, stale cache, missing security headers |
| **Low** | Best practice, not directly exploitable | Idempotency key fallback, unsanitized log field, informational leak |

---

## Output Template

```markdown
# SaaS Security Audit: [Project Name]

## Summary
- **Domains audited:** 7/7
- **Critical:** X | **High:** Y | **Medium:** Z | **Low:** W
- **Top risk:** [one-sentence summary of worst finding]

## Critical Findings
### [Title]
- **Location:** `file.ts:42`
- **Attack vector:** [How an attacker exploits this]
- **Impact:** [Revenue loss / data exposure / privilege escalation]
- **Fix:** [Specific code change]

## [High / Medium / Low sections, same format]

## Positive Findings
[Things done well -- helps prioritize effort]
```

---

## Anti-Patterns

| Don't | Do |
|-------|-----|
| Only check OWASP generics | Start with billing/payment bypass |
| Trust client-submitted prices or plan IDs | Verify all pricing is server-side |
| Assume `as string` is safe for Stripe objects | Use type guards: `typeof x === 'string' ? x : x.id` |
| Skip PayPal custom_id validation | Validate full identity chain: custom_id -> user -> payerId |
| Put auth checks outside transactions | Move permission checks inside `FOR UPDATE` transactions |
| Use `===` for secret comparison | Use `crypto.timingSafeEqual()` everywhere |
| Use in-memory rate limiters in serverless | Use Redis-backed rate limiting (Upstash, etc.) |
| Show key suffixes in health checks | Show prefix only, never suffix |
| Assume RLS migration covers all tables | Script-verify coverage against `information_schema.tables` |

---

## CREATIVITY TRIGGERS — For When the Obvious Checks Pass

When the 15-domain sweep comes back clean, the audit is not done. Most real
vulnerabilities are invisible to checklists because they are compositions of
"individually safe" components. Use these prompts to break out of checklist mode.

### The "Invisible" Vulnerabilities
- **What data changes silently?** Tokens refresh, permissions expire, caches
  invalidate, logs rotate. Find the side channels.
- **What happens at 80+ characters?** Command truncation, URL length limits,
  email normalization, username padding.
- **What's the default that nobody changes?** API keys, DB passwords, TLS certs,
  admin emails, cron secrets. Audit as if a user never touched config.
- **What runs outside normal UX?** Power-user CLI, admin batch jobs, webhook
  replay, reconciliation cron, data exports.

### The "Layered" Attack
- **How would you slowly escalate?** viewer → member → admin → owner → service
  role. What's the shortest path?
- **What permissions compound?** Read + write + export = data exfiltration. Each
  alone was approved.
- **What can be done with timing?** Race conditions between permission check and
  action. Token rotation windows. Grace period edge cases.
- **What sequence is forbidden but individually allowed?** State machine bypass
  via unexpected ordering.

### The "Hidden" Surface
- **Where does this system integrate?** Webhooks, callbacks, imports, third parties.
- **What administrative paths exist?** Support interfaces, debug endpoints, batch ops.
- **What was deprecated but still works?** Old API versions, legacy endpoints,
  test-only routes.
- **What accepts "unexpected" data?** JSON in form field, query string in body,
  metadata passed through a downstream LLM.

### The "Trust Assumption" That's Wrong
- "Only legitimate users reach this" — is it publicly findable?
- "This input is validated upstream" — is upstream bypassable?
- "This only stores non-sensitive data" — does it combine with other data?
- "This isn't exploitable without X" — is X easier than assumed?
- "The CDN strips this header" — does it strip it on OPTIONS but not POST?
- "Only paying customers have this feature" — is there a trial bypass?

**See [CREATIVITY-TRIGGERS.md](references/CREATIVITY-TRIGGERS.md) for the full
catalog** of 50+ prompts, including attacker personas, red team scenarios, and
the "impossible question" technique (ask questions you believe have no answer,
then let the search find the answer).

---

## THE AUDIT WORKFLOW (End-to-End)

A real audit is not a linear checklist. It is a spiral: surface enumeration,
threat modeling, domain sweep, creativity phase, validation, reporting.

```
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 1: PREPARE (15 min)                                        │
│ → Threat model (attacker goal, budget, access)                   │
│ → Surface enumeration (every entry point)                        │
│ → Trust boundary mapping (every data flow)                       │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 2: KERNEL CHECK (10 min)                                   │
│ → Apply all 10 axioms to the system                              │
│ → Any axiom that doesn't hold = investigate immediately          │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 3: DOMAIN SWEEP (60-90 min)                                │
│ → 15 domain checklists, billing first (highest revenue impact)   │
│ → Parallel where possible (auth + data + web = independent)      │
│ → Document findings as you go (not at the end)                   │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 4: OPERATOR CHAINS (30-60 min)                             │
│ → Apply ⊘ Surface-Transpose to each finding                      │
│ → Apply ⟂ Fail-Open Probe to each dependency                     │
│ → Apply ⊙ Identity-Chain Trace to each auth flow                 │
│ → Apply ≡ Invariant-Extract to each security mechanism           │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 5: CREATIVITY PHASE (30 min)                               │
│ → Apply ⊕ Creative-Transposition (5 attacker personas)           │
│ → Walk through creativity triggers for unexpected paths          │
│ → Red team scenarios from references/ATTACK-SCENARIOS.md         │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 6: VALIDATION (15 min)                                     │
│ → For each finding: can you PROVE it's exploitable?              │
│ → False positives discarded                                      │
│ → Severity recalibrated against actual impact                    │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ PHASE 7: REPORT (15 min)                                         │
│ → Structured report with file:line, attack, impact, fix          │
│ → Create beads for each finding (priority by severity)           │
│ → If CRITICAL: recommend immediate pause + escalation            │
└──────────────────────────────────────────────────────────────────┘
```

Total: ~4 hours for a comprehensive audit of a production SaaS.

---

## ECOSYSTEM INTEGRATION

This skill is one node in a network. It cross-references and is cross-referenced
by other skills. Use together for compound effects.

| Workflow | Skills to Chain |
|----------|----------------|
| Pre-launch audit | this → [multi-pass-bug-hunting](../multi-pass-bug-hunting/) → [release-preparations](../release-preparations/) |
| Post-incident forensics | this (INCIDENT-RESPONSE.md) → [codebase-archaeology](../codebase-archaeology/) |
| Security test suite | this (SECURITY-TESTING.md) → [testing-fuzzing](../testing-fuzzing/) → [testing-metamorphic](../testing-metamorphic/) |
| Triangulated security review | this → [code-review-gemini-swarm-with-ntm](../code-review-gemini-swarm-with-ntm/) → [multi-model-triangulation](../multi-model-triangulation/) |
| Third-party integration audit | this (THIRD-PARTY.md) → [stripe-checkout](../stripe-checkout/) → [supabase](../supabase/) |
| CI/CD security hardening | this (INFRASTRUCTURE.md) → [gh-actions](../gh-actions/) (SECURITY-CORE.md) |
| Secure deployment | this → [vercel](../vercel/) (SECRETS.md) |
| Vulnerability reporting | this → [reporting-sensitive-encrypted-gh-issues](../reporting-sensitive-encrypted-gh-issues/) |

**Cross-skill references** (don't duplicate, LINK):
- RLS patterns: see [supabase/references/RLS-PATTERNS.md](../supabase/references/RLS-PATTERNS.md)
- Stripe webhook patterns: see [stripe-checkout/references/WEBHOOKS.md](../stripe-checkout/references/WEBHOOKS.md)
- CI/CD security: see [gh-actions/references/SECURITY-CORE.md](../gh-actions/references/SECURITY-CORE.md)
- Vercel secrets: see [vercel/references/SECRETS.md](../vercel/references/SECRETS.md)
- Fuzzing harnesses: see [testing-fuzzing/](../testing-fuzzing/)

---

## References

### Core Domains (15)

| Topic | File |
|-------|------|
| Payment & billing deep checklist | [BILLING.md](references/BILLING.md) |
| Auth & authorization checklist | [AUTH.md](references/AUTH.md) |
| Entitlement enforcement patterns | [ENTITLEMENTS.md](references/ENTITLEMENTS.md) |
| Secrets management checklist | [KEY-MANAGEMENT.md](references/KEY-MANAGEMENT.md) |
| Database access control (RLS) | [DATABASE.md](references/DATABASE.md) |
| Web security checklist | [WEB.md](references/WEB.md) |
| Infrastructure security | [INFRASTRUCTURE.md](references/INFRASTRUCTURE.md) |
| Rate limiting & abuse detection | [RATE-LIMITING.md](references/RATE-LIMITING.md) |
| Multi-tenant isolation | [MULTI-TENANT.md](references/MULTI-TENANT.md) |
| Third-party integration | [THIRD-PARTY.md](references/THIRD-PARTY.md) |
| Data security & privacy (GDPR) | [DATA-SECURITY.md](references/DATA-SECURITY.md) |
| Incident response & forensics | [INCIDENT-RESPONSE.md](references/INCIDENT-RESPONSE.md) |
| Audit logging & compliance | [AUDIT-LOGGING.md](references/AUDIT-LOGGING.md) |
| LLM/AI-specific security | [LLM-SECURITY.md](references/LLM-SECURITY.md) |
| API security | [API-SECURITY.md](references/API-SECURITY.md) |

### Cognitive Tooling

| Topic | File |
|-------|------|
| Triangulated security kernel | [KERNEL.md](references/KERNEL.md) |
| Cognitive operators (17 cards) | [OPERATORS.md](references/OPERATORS.md) |
| Creativity triggers (50+ prompts) | [CREATIVITY-TRIGGERS.md](references/CREATIVITY-TRIGGERS.md) |
| Attack scenarios & red team | [ATTACK-SCENARIOS.md](references/ATTACK-SCENARIOS.md) |
| Threat modeling | [THREAT-MODELING.md](references/THREAT-MODELING.md) |

### Real-World Reference

| Topic | File |
|-------|------|
| Real-world case studies (anonymized) | [CASE-STUDIES.md](references/CASE-STUDIES.md) |
| Real code snippets (positive examples) | [COOKBOOK.md](references/COOKBOOK.md) |
| Fail-open patterns catalog | [FAIL-OPEN-PATTERNS.md](references/FAIL-OPEN-PATTERNS.md) |
| Security testing strategy | [SECURITY-TESTING.md](references/SECURITY-TESTING.md) |
| Grep patterns for quick scanning | [GREP-PATTERNS.md](references/GREP-PATTERNS.md) |
| Observability for security | [OBSERVABILITY.md](references/OBSERVABILITY.md) |
| Prompt archetypes (5 audit modes) | [PROMPT-ARCHETYPES.md](references/PROMPT-ARCHETYPES.md) |

### Automated Tooling

| Script | Purpose |
|--------|---------|
| `scripts/rls-coverage.sql` | Verify every table has RLS policies |
| `scripts/leak-scan.sh` | Find hardcoded secrets & env var leaks |
| `scripts/webhook-signature-test.sh` | Test webhook signature verification |
| `scripts/api-auth-mapper.sh` | Map every API route to its auth requirement |
| `scripts/find-fail-open.sh` | Grep for fail-open patterns in codebase |
| `scripts/audit-quick.sh` | 60-second automated surface audit |

### Compliance & Frameworks

| Topic | File |
|-------|------|
| OWASP SaaS Top 10 (breach-driven) | [OWASP-SAAS-TOP-10.md](references/OWASP-SAAS-TOP-10.md) |
| MITRE ATT&CK mapping for SaaS | [MITRE-ATTACK-MAPPING.md](references/MITRE-ATTACK-MAPPING.md) |
| SOC 2 / GDPR / PCI / HIPAA / ISO 27001 | [COMPLIANCE-DEEPDIVE.md](references/COMPLIANCE-DEEPDIVE.md) |
| 15 famous breach case studies | [BREACH-CASE-STUDIES.md](references/BREACH-CASE-STUDIES.md) |

### Adversarial Thinking

| Topic | File |
|-------|------|
| 9 threat modeling frameworks | [ADVERSARIAL-THINKING.md](references/ADVERSARIAL-THINKING.md) |
| Field stories from the trenches | [FIELD-GUIDE.md](references/FIELD-GUIDE.md) |
| Attack scenario genealogy (composing bugs) | [ATTACK-SCENARIO-GENEALOGY.md](references/ATTACK-SCENARIO-GENEALOGY.md) |
| Business logic flaws (40+ patterns) | [BUSINESS-LOGIC-FLAWS.md](references/BUSINESS-LOGIC-FLAWS.md) |
| Performance as security (DoS/DoW) | [PERFORMANCE-DOS-VECTORS.md](references/PERFORMANCE-DOS-VECTORS.md) |

### Deep Technical Topics

| Topic | File |
|-------|------|
| Idempotency patterns (distributed locking) | [IDEMPOTENCY.md](references/IDEMPOTENCY.md) |
| Timing-safe comparisons (3 variants) | [TIMING-SAFE.md](references/TIMING-SAFE.md) |
| Crypto fundamentals (dos and don'ts) | [CRYPTO-FUNDAMENTALS.md](references/CRYPTO-FUNDAMENTALS.md) |
| Session management lifecycle | [SESSION-MANAGEMENT.md](references/SESSION-MANAGEMENT.md) |
| Admin impersonation (audit + cookies) | [IMPERSONATION.md](references/IMPERSONATION.md) |
| CLI auth via RFC 8628 device code | [CLI-AUTH.md](references/CLI-AUTH.md) |
| CSP patterns (per-path, per-env) | [CSP-PATTERNS.md](references/CSP-PATTERNS.md) |

### Architecture & Maturity

| Topic | File |
|-------|------|
| Zero trust for SaaS | [ZERO-TRUST-SAAS.md](references/ZERO-TRUST-SAAS.md) |
| Defense in depth (7 layers) | [DEFENSE-IN-DEPTH.md](references/DEFENSE-IN-DEPTH.md) |
| Security maturity model (5 levels) | [SECURITY-MATURITY.md](references/SECURITY-MATURITY.md) |
| Week-1 onboarding audit | [ONBOARDING-AUDIT.md](references/ONBOARDING-AUDIT.md) |

### Dispatched Subagents

For parallel, focused work, dispatch these subagents (in `subagents/`):

| Subagent | Use When |
|----------|----------|
| `billing-archaeologist` | Tracing payment flows, finding divergence |
| `rls-auditor` | Auditing Supabase RLS coverage |
| `entitlement-checker` | Finding missing feature gates |
| `recovery-path-walker` | Auditing crons, migrations, replays |
| `webhook-divergence-detective` | Comparing provider handlers |
| `admin-escalation-mapper` | Mapping privilege escalation |
| `red-team-agent` | Creative vulnerability hunting |
| `incident-responder` | Active incident triage |

### Modern Attack Surfaces

| Topic | File |
|-------|------|
| Honeypots, canaries, deception tech | [HONEYPOTS-AND-DECEPTION.md](references/HONEYPOTS-AND-DECEPTION.md) |
| Canary tokens & tripwires (detail) | [CANARY-TOKENS.md](references/CANARY-TOKENS.md) |
| WebAuthn / Passkeys / FIDO2 | [WEBAUTHN-PASSKEYS.md](references/WEBAUTHN-PASSKEYS.md) |
| Supply chain (SBOM, SLSA, Sigstore) | [SUPPLY-CHAIN-DEEP.md](references/SUPPLY-CHAIN-DEEP.md) |
| Cloud provider security (AWS/GCP/Vercel) | [CLOUD-PROVIDER-SECURITY.md](references/CLOUD-PROVIDER-SECURITY.md) |
| Email security (SPF/DKIM/DMARC) | [EMAIL-SECURITY.md](references/EMAIL-SECURITY.md) |
| DNS security (subdomain takeover, DNSSEC) | [DNS-SECURITY.md](references/DNS-SECURITY.md) |
| GraphQL security (depth, complexity, field-auth) | [GRAPHQL-SECURITY.md](references/GRAPHQL-SECURITY.md) |
| WebSocket security (CSWSH, per-msg authz) | [WEBSOCKET-SECURITY.md](references/WEBSOCKET-SECURITY.md) |
| SCIM provisioning security (enterprise) | [SCIM-PROVISIONING.md](references/SCIM-PROVISIONING.md) |
| AI/ML-specific security (beyond prompts) | [AI-ML-SECURITY.md](references/AI-ML-SECURITY.md) |
| Red team playbook (kill chain for SaaS) | [RED-TEAM-PLAYBOOK.md](references/RED-TEAM-PLAYBOOK.md) |
| Bug bounty program design | [BUG-BOUNTY.md](references/BUG-BOUNTY.md) |
| Security debt quantification | [SECURITY-DEBT.md](references/SECURITY-DEBT.md) |
| 25 admin escalation paths | [ADMIN-ESCALATION-PATHS.md](references/ADMIN-ESCALATION-PATHS.md) |

### Advanced Defenses & Economics

| Topic | File |
|-------|------|
| Security economics (ALE, ROSI, budget defense) | [SECURITY-ECONOMICS.md](references/SECURITY-ECONOMICS.md) |
| Data exfiltration defense (egress, staging, DLP) | [DATA-EXFILTRATION-DEFENSE.md](references/DATA-EXFILTRATION-DEFENSE.md) |
| CORS deep-dive (10 real misconfig classes) | [CORS-DEEP.md](references/CORS-DEEP.md) |
| Modern browser security APIs (COOP/COEP/Trusted Types) | [BROWSER-SECURITY-APIS.md](references/BROWSER-SECURITY-APIS.md) |
| Post-quantum crypto migration prep | [POST-QUANTUM-PREP.md](references/POST-QUANTUM-PREP.md) |

### Assets & Templates

| Asset | Purpose |
|-------|---------|
| `assets/AUDIT-REPORT-TEMPLATE.md` | Final audit report format |
| `assets/FINDING-TEMPLATE.md` | Structured finding format |
| `assets/THREAT-MODEL-CANVAS.md` | 30-min threat model sketch |
| `assets/OPERATOR-CARD-DECK.md` | Printable operator cards |
