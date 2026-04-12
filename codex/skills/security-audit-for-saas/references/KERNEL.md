# The Security Audit Kernel

> A "kernel" is the minimal, load-bearing set of axioms and objectives that govern
> all security reasoning about a SaaS system. If you skip any axiom, you miss a whole
> class of vulnerabilities. The kernel is **compositional**: each axiom unlocks a
> different category of hunt.

This file is the distilled methodology. Treat it as executable, not descriptive. If
you cannot show a check against each axiom in your audit report, the audit is
incomplete.

---

<!-- SECURITY_AUDIT_KERNEL_START v1.0 -->

## AXIOMS (Non-Negotiable)

### Axiom 1 — Every fail-open is a DoS pivot

If a dependency (Redis, Stripe, JWKS, subscription service, RLS, cache) fails, does
the code fail-closed (deny) or fail-open (allow)? Any fail-open on an auth, billing,
or rate-limit path is a **CRITICAL** finding: the attack is not "exploit the auth
logic," it's "break the dependency."

**Corollary 1a:** Graceful degradation is a security property. "The site stays up
when Redis dies" is a feature only if the degradation is fail-closed for security
gates.

**Corollary 1b:** Retries and fallbacks compound. A primary + fallback + in-memory
cache creates three failure modes. Each can be attacked independently.

**How to test:**
- Grep for `catch { return true }`, `|| fallback`, `?? defaultAllow`
- Simulate each dependency failure in a staging environment
- Ask: "If I can DoS Redis, what bypass do I get?"

### Axiom 2 — Duplicate parsers diverge → smuggling

Whenever the same input (URL, path, header, cookie, email, JSON) is parsed at two
layers, their interpretations will drift over time. The drift is the bypass. Single
source of truth parsing is a security property.

**Examples of duplicate parsers found in the wild:**
- Proxy path matcher `(?:/|$)` vs rate-limiter path matcher `$`
- Config-time URL validator vs runtime fetcher
- Frontend Zod schema vs backend Zod schema
- Two languages deserialize JSON differently (Python bool vs JS truthy)
- OPTIONS preflight CORS check vs POST CORS check

**How to test:**
- Find every place the same input is parsed twice
- Diff the parsers (write a fuzzer that finds disagreements)
- Any disagreement on path/auth/tenant boundary is a bypass

### Axiom 3 — Normalize before validate, always

Validation on raw input is already bypassed. Before every validation step, canonicalize
the input: trim whitespace, NFC normalize unicode, decode URL-encoding, resolve
symlinks, case-fold, strip zero-width chars.

**Failure modes:**
- Device code: `z.string().min(8)` passes "A B C D 1 2 3 4" but normalization
  produces the real 8-char code → length check bypassed
- Path check: `filepath.Clean` doesn't resolve symlinks → symlink escape
- Email: attacker registers `user@example.com` and `user+tag@example.com` as
  "different" users

**How to test:**
- Find every `z.string().min(N)`, `length >= N`, `startsWith(...)`, path check
- Verify normalization happens BEFORE the check, not after
- Verify the same normalization is used in both the check and the use

### Axiom 4 — Self-heal down, never up

Reconciliation loops that raise privilege are an attacker's dream. If `requireAdmin()`
finds a whitelisted email without the admin flag and auto-promotes, then revocation
is undone by the next invocation.

**Pattern (vulnerable):**
```typescript
if (ADMIN_EMAILS.includes(user.email) && !user.isAdmin) {
  await db.update(users).set({ isAdmin: true }).where(eq(id, user.id));
}
```

**Pattern (safe):**
```typescript
// Never auto-promote. The whitelist gates LOGIN; role is durable state.
if (!ADMIN_EMAILS.includes(user.email)) return redirect('/forbidden');
if (!user.isAdmin) return redirect('/not-authorized'); // manual admin grant
```

**How to test:**
- Grep for role/status writes in middleware or auth functions
- Any write that RAISES privilege in a check-and-fix loop is a bug
- Revocation must survive the next page load

### Axiom 5 — Every error is an oracle

Auth/lookup responses must be indistinguishable across account states. "Invalid
password" vs "user not found" is a free email enumeration API. Timing differences
between "user exists" and "user missing" is the same oracle over a different channel.

**Oracle categories:**
- **Distinct error messages** for different states
- **Timing** of bcrypt/scrypt only when user exists
- **Status codes** (200 vs 401 vs 404 for similar operations)
- **Response size** (JSON shape differs)
- **Response time** (DB query time differs)

**How to test:**
- For login, password reset, magic link: verify all responses identical
- For email/username/promo code lookups: verify generic response regardless of state
- For auth failures: constant-time regardless of which step failed

### Axiom 6 — Presence-only header checks are worthless

`Authorization: Bearer anything`, `X-Admin: true`, `CF-Access-JWT-Assertion: .*`,
`X-Real-IP: <forged>`. Without cryptographic verification, headers are
attacker-controlled at L7.

**Safe patterns:**
- JWT: verify signature AND claims AND expiry
- Cloudflare Access: verify JWT + source IP range
- Bearer tokens: timing-safe compare against hash

**How to test:**
- Grep for `headers.get(` followed by truthiness check without verification
- Any `if (request.headers.has("X-Admin"))` is CRITICAL
- Verify IP trust chain: does the deployment environment ACTUALLY prevent spoofing?

### Axiom 7 — The recovery path is a shadow codebase

Every invariant on the primary path (signature verification, idempotency,
authorization, rate limiting) must be re-enforced on:
- Reconciliation crons
- Webhook replays
- Database restores
- Migration runners
- Test fixtures that mirror production

**Example:** Primary webhook handler verifies Stripe signature. Reconciliation cron
fetches events from Stripe API directly (no signature) — it must treat Stripe's
response as trusted via a different mechanism (TLS cert validation, PAT scope).

**How to test:**
- For each primary-path invariant, find the recovery path
- Verify the invariant is re-enforced (possibly via a different mechanism)
- Audit includes: crons, batch jobs, migration files, backup restores

### Axiom 8 — Attack surfaces expand faster than defenses

Webhooks, CLIs, import/export, batch jobs, OG-image endpoints, admin APIs, old API
versions, debug endpoints, cron secrets, health checks, telemetry endpoints,
support interfaces. Each was added without a security review.

**Enumerate before audit:**
1. All `/api/*` routes
2. All webhook endpoints (Stripe, PayPal, internal)
3. All cron jobs (`/api/cron/*`)
4. All admin endpoints
5. All CLI-accessible endpoints
6. All batch/import/export endpoints
7. All health/telemetry/debug endpoints
8. All auth callback endpoints (OAuth, SSO, SAML)
9. All file upload endpoints
10. All OG-image/thumbnail endpoints
11. All old API versions (`/api/v1`, `/api/v2`)
12. All test-only routes still active in production

### Axiom 9 — Prices, identities, and entitlements are server-side

Any value the client can modify is attacker-controllable. Prices, plan IDs, user
IDs, org IDs, roles, feature flags — all must be derived from server-authoritative
state, not request bodies.

**How to test:**
- Grep route handlers for `body.amount`, `body.userId`, `body.role`, `body.orgId`
- Each must be derived from `session.user.id` or DB lookup
- Stripe price IDs must be validated against an allowlist constant

### Axiom 10 — Multi-tenancy is RLS + app-layer

RLS alone is insufficient (service role key bypasses it). App-layer checks alone
are insufficient (developers forget). Both layers must enforce the boundary.

**How to test:**
- For each cross-tenant operation, verify BOTH:
  1. RLS policy prevents direct DB access
  2. App layer calls `requireOrgRole()` or equivalent
- Test with a second tenant in fixtures to catch default-tenant bugs

<!-- SECURITY_AUDIT_KERNEL_END -->

---

## OBJECTIVE FUNCTION

For each finding, compute: **Risk = Impact × Probability × Discoverability**

- **Impact (1-10):** Revenue loss, data breach, privilege escalation, reputation
- **Probability (1-10):** How likely is an attacker to find this?
- **Discoverability (1-10):** How easy to find with basic enumeration?

**Risk ≥ 300:** CRITICAL — escalate immediately, pause feature
**Risk 100-299:** HIGH — fix within 24 hours
**Risk 30-99:** MEDIUM — fix within sprint
**Risk < 30:** LOW — log for future

---

## OPERATOR COMPOSITION

Operators are not applied in isolation. The kernel composes them into hunts:

**Authentication audit chain:**
```
⊘ Surface-Transpose → ⟂ Fail-Open Probe → ≡ Invariant-Extract → ⊙ Identity-Chain
```
(Find all surfaces) → (Probe each for fail-opens) → (Extract assumptions) → (Trace identity)

**Billing audit chain:**
```
⊘ Surface-Transpose → ⊙ Identity-Chain → ✂ Parser-Diverge → ⟂ Fail-Open Probe
```
(Every checkout surface) → (Every identity claim) → (Duplicate parsers) → (Fail modes)

**Data exposure audit chain:**
```
≡ Invariant-Extract → ⊕ Creative-Transposition → ⊙ Identity-Chain
```
(What must be private?) → (Different attacker views) → (How does data flow?)

**Escalation audit chain:**
```
⊘ Surface-Transpose → Self-Heal Detector → ⟂ Fail-Open Probe
```
(Every role-touching surface) → (Auto-promotion patterns) → (Fail-open in auth)

See [OPERATORS.md](OPERATORS.md) for full operator cards.

---

## VALIDATION GATES

A kernel application is valid only if:

- [ ] All 10 axioms have been explicitly checked against the target system
- [ ] Each finding cites which axiom(s) it violates
- [ ] Risk score computed for each finding using the objective function
- [ ] Operator compositions logged (which chain found each finding)
- [ ] False positives validated and rejected (not just dismissed)
- [ ] Report includes both findings AND positive observations (what's correct)
- [ ] If any CRITICAL finding: explicit escalation recommendation included
