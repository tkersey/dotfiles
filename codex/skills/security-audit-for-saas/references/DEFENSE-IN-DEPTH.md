# Defense in Depth

Defense in depth is the principle of having multiple independent layers of
security, so that if one fails, others catch the attack. It's complementary to
zero trust (which ensures each layer verifies explicitly).

---

## The Layers

### Layer 1: Network
- Firewalls
- WAF (Web Application Firewall)
- DDoS protection (Cloudflare, AWS Shield)
- Rate limiting at the edge
- Bot detection (Turnstile, reCAPTCHA)

### Layer 2: Proxy / Middleware
- HTTPS enforcement (HSTS)
- Request size limits
- CSRF validation
- CORS policy
- Rate limiting at the app edge

### Layer 3: Application Authentication
- Session validation
- JWT signature verification
- MFA enforcement
- Device fingerprinting

### Layer 4: Application Authorization
- RBAC role checks
- Resource ownership checks
- Tenant boundary enforcement
- Feature flag / tier checks

### Layer 5: Data Access
- RLS policies
- Query scoping
- Field-level access control
- Audit logging

### Layer 6: Data Protection
- Encryption at rest
- Encryption in transit
- Key rotation
- Backup security

### Layer 7: Monitoring & Response
- Anomaly detection
- Alert routing
- Incident response
- Forensic queries

**Total: 7 layers.** An attacker must defeat ALL of them to succeed. If any
single layer catches them, the attack fails.

---

## The Principle of Independence

For defense in depth to work, layers must be INDEPENDENT. If layer N fails,
layer N+1 must NOT fail for the same reason.

**Bad example:** Both the WAF and the app use the same regex for input
validation. If an attacker bypasses the regex, both layers fail.

**Good example:** WAF blocks known attack patterns. App also validates with
structured schema. If an attacker crafts a novel payload that bypasses the
WAF, the app's schema validation still catches it.

---

## Concrete Defense Chains

### Chain 1: Protecting Admin Endpoints

| Layer | Control |
|-------|---------|
| Network | Cloudflare WAF with admin IP allowlist |
| Proxy | CSRF validation, HSTS, IP detection |
| Application | `requireAdmin()` middleware |
| Application | MFA challenge for sensitive actions |
| Data | RLS policies prevent non-admin queries |
| Audit | Every action logged with actor + justification |
| Monitoring | Alert on admin actions outside business hours |

**Bypass requires:** Defeating the WAF + stealing a session + bypassing MFA +
having the DB role + being untraceable. Catastrophically hard.

### Chain 2: Protecting the Billing Pipeline

| Layer | Control |
|-------|---------|
| Network | Stripe only sends webhooks from known IPs |
| Proxy | CSRF exempt (webhooks use signature) |
| Application | HMAC signature verification |
| Application | Account ID verification (event.account === EXPECTED) |
| Application | Idempotency key check (no duplicate processing) |
| Data | Row-level uniqueness on (provider, event_id) |
| Audit | Every webhook event logged |
| Reconciliation | Cron reconciles with Stripe API |

**Bypass requires:** Forging webhook signature AND passing account check AND
finding non-idempotent code path. Very hard.

### Chain 3: Protecting User Data

| Layer | Control |
|-------|---------|
| Network | TLS 1.3 |
| Proxy | HTTPS enforcement |
| Application | Session validation |
| Application | `requireOrgRole()` for cross-tenant |
| Data | RLS policies |
| Data | Column-level encryption for PII |
| Monitoring | Alert on bulk data access |
| Audit | Every data access logged |

**Bypass requires:** Stealing session + bypassing RLS + decrypting data. Very
hard.

---

## Defense Layer Audit

For each critical feature, list the defense layers. If any layer is missing,
that's a finding.

### Template
```markdown
## Feature: [name]

| Layer | Control | Present? | Notes |
|-------|---------|----------|-------|
| Network | DDoS | ✓ | Cloudflare |
| Proxy | CSRF | ✓ | lib/csrf.ts |
| App Auth | Session | ✓ | requireAuth |
| App Authz | Tenant | ✗ | MISSING: should add requireOrgRole |
| Data | RLS | ✓ | 2026-03 migration |
| Audit | Log | ✓ | audit_log table |
| Monitor | Alert | ✗ | MISSING: no alert on bulk access |
```

Missing layers are findings. Not necessarily CRITICAL (other layers still
protect), but HIGH because they reduce defense-in-depth.

---

## The Weakest Link Analysis

Security chain's strength = strength of the weakest link. Identify the
weakest link in each chain:

### For admin endpoints
Weakest link: If no MFA, then a stolen password = full admin access.

### For billing pipeline
Weakest link: If no account ID verification, attacker can use their own
Stripe account to forge "legitimate" events.

### For user data
Weakest link: If RLS missing on some tables, direct DB queries bypass
everything.

Fix the weakest link first. The strongest link doesn't matter if another
link is already broken.

---

## Redundancy vs Waste

**Redundant controls (good):** Multiple independent layers checking the same
thing. If any catches the attack, it fails.

**Wasteful controls (bad):** Duplicate controls that share a common failure
mode. They look like defense-in-depth but provide only single-layer protection.

**Example:**
- Two WAFs from the same vendor → shared vulnerabilities. Wasteful.
- WAF + app-layer input validation → independent, catches different attacks. Good.

**Another example:**
- Two database connection pools → redundant, but doesn't help security.
  Wasteful from a security perspective.
- Database RLS + application-layer tenant check → independent mechanisms
  catching the same attack. Good.

---

## Cost of Defense

Each layer has a cost (latency, complexity, operational burden). Balance
defense depth against cost:

| Layer | Latency | Complexity | Cost |
|-------|---------|------------|------|
| Network (Cloudflare) | +0-5ms | Low | $$ |
| Proxy middleware | +1-2ms | Low | Free |
| App auth | +5-20ms | Medium | Free |
| App authz | +1-10ms | Medium | Free |
| Data RLS | +1-5ms | High | Free |
| Encryption | +1-2ms | High | Free |
| Audit logging | Non-blocking | Medium | $ (storage) |
| Monitoring | Async | High | $$ |

Total added latency: ~20-50ms for a full chain. Acceptable for most SaaS.

---

## When One Layer Is Enough

Not every feature needs 7 layers. Calibrate to risk:

**Public features (blog, marketing site):**
- Network + Proxy + TLS
- 3 layers. Enough.

**User features (dashboard, data):**
- All 7 layers.

**Admin features (user management, billing config):**
- All 7 + MFA + JIT elevation
- 9 layers.

**Crown jewels (admin of admins, signing keys):**
- All layers + air gap + 2-person rule
- Extraordinary protection.

---

## The Defense-in-Depth Mindset

When reviewing code, ask: "If this check fails, what catches the attack?"

If nothing catches it, add another layer. If multiple things catch it,
consider if you can simplify (removing redundant controls with no added value).

---

## See Also

- [ZERO-TRUST-SAAS.md](ZERO-TRUST-SAAS.md)
- [KERNEL.md](KERNEL.md) — Axiom 2 (parser divergence can break defense in depth)
- [FAIL-OPEN-PATTERNS.md](FAIL-OPEN-PATTERNS.md) — when one layer fails open
