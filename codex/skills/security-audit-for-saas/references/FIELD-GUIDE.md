# Field Guide — Stories from the Trenches

Production security knowledge lives in code comments, incident post-mortems,
and the small acts of desperate engineering that follow a near-miss. This file
collects those stories, anonymized but technically accurate, from 8+ production
SaaS audits.

Each story follows the pattern: **what the comment revealed → what actually
happened → the lesson → the generalized rule**.

---

## Story 1: "Previous implementation had a TOCTOU race"

**The comment:**
```typescript
// Previous implementation had a TOCTOU race: count query and delete query
// used separate timestamps, allowing concurrent calls to both see the same
// "valid" backup code and both successfully delete it.
```

**What actually happened:** An internal user noticed they could use a single
backup code twice if they submitted two requests concurrently. The count query
("does this code exist?") and the delete query ("remove it") were in separate
transactions. Between them, another request could see the same code as valid.

**The fix:** `DELETE ... WHERE id = ? RETURNING id` in a single statement.
Zero-row return = code already used.

**The lesson:** Never separate "check" from "act." If you find yourself writing
`if (exists) delete`, you've already lost the race.

**The generalized rule:** For any operation that's "check state then mutate
based on state," the check and the mutate must be the same SQL statement. Use
`INSERT ... ON CONFLICT`, `UPDATE ... WHERE condition RETURNING`, `DELETE
... WHERE condition RETURNING`.

**See:** [AUTH.md](AUTH.md) TOCTOU section

---

## Story 2: "Degraded monitoring is better than blocked admin access"

**The comment:**
```typescript
// Audit log is non-blocking - degraded monitoring is better than blocked
// admin access. If the audit log DB is down, log the failure and continue.
```

**What happened:** After an incident where the audit log database had connection
issues, all admin actions were blocked. The team couldn't disable compromised
accounts during the incident because the audit write was failing. They added a
non-blocking write pattern.

**The fix:** `after()` callback or queue-based audit writes that don't block
the request.

**The lesson:** Audit logs are critical, but so is the ability to operate during
an incident. Non-blocking audit with strong alerting on write failures is the
right compromise.

**The generalized rule:** For every "nice to have" write in a critical flow,
ask: "What if this write fails?" If the answer is "the primary operation blocks,"
move it to a non-blocking path with alerting.

**See:** [AUDIT-LOGGING.md](AUDIT-LOGGING.md) non-blocking section

---

## Story 3: "strict-dynamic was removed because it blocks Next.js chunks"

**The comment:**
```typescript
// 'strict-dynamic' was removed because it blocks Next.js dynamically loaded
// chunks that don't have nonces. A future improvement could use Next.js's
// built-in CSP nonce support via the metadata API.
```

**What happened:** The team added `strict-dynamic` to their CSP for maximum
security. The app immediately broke because Next.js dynamically loads JavaScript
chunks that don't carry the nonce. Rather than remove the nonce entirely (losing
the security benefit), they removed `strict-dynamic` and accepted the partial
protection.

**The lesson:** Security controls often conflict with framework internals. The
"ideal" CSP may not be achievable with your framework. Document the compromise.

**The generalized rule:** When a security control breaks your app, don't just
turn it off — document WHY it broke, what partial benefit remains, and what
full implementation would look like. Future engineers (or framework updates)
may unblock the full fix.

**See:** [CSP-PATTERNS.md](CSP-PATTERNS.md)

---

## Story 4: "These headers can be spoofed if the origin is reachable directly"

**The comment:**
```typescript
// SECURITY: Cloudflare Access headers (cf-access-authenticated-user-email)
// can be spoofed if the origin is reachable directly. Require explicit opt-in
// via BRENNER_TRUST_CF_ACCESS_HEADERS=1 AND configure the origin to reject
// non-CF traffic at the network level.
```

**What happened:** A dev deployed behind Cloudflare Access but forgot to
restrict the origin to CF's IP ranges. An attacker found the origin IP directly
(via DNS history or Shodan), bypassed CF, and sent requests with forged
`cf-access-authenticated-user-email` headers. The app trusted the header
presence and granted admin access.

**The fix:** (1) Require explicit env var to trust CF headers. (2) Verify JWT
signature on `CF_Authorization` header, not just presence. (3) Document the
origin IP restriction requirement.

**The lesson:** Every "the CDN/proxy handles that" assumption has an escape
hatch. Attackers find the origin. Design as if the origin is publicly reachable.

**The generalized rule:** Any header that conveys trust from an upstream proxy
must be cryptographically verified. Opt-in, not opt-out.

**See:** [KERNEL.md](KERNEL.md) Axiom 6 (presence-only header checks)

---

## Story 5: "Without a transaction, if insert fails after delete, user has no backup codes"

**The comment:**
```typescript
// Without a transaction, if insert fails after delete, user has NO backup codes.
// This was a P0 incident: user with 2FA enabled lost all recovery options when
// the insert failed due to unique constraint violation in our seed data.
```

**What happened:** The backup code regeneration flow was: delete old codes,
insert new codes. A unique constraint violation in the insert left the user
with zero codes. If the user also lost their authenticator, they were locked
out.

**The fix:** Wrap in a transaction. If insert fails, delete is rolled back.

**The lesson:** Any "replace" operation needs atomicity. Delete-then-insert is
a TOCTOU between the two operations.

**The generalized rule:** Replace operations must be atomic. Use transactions
or upserts. The invariant "user has N codes" must hold throughout the operation.

**See:** [BILLING.md](BILLING.md), [COOKBOOK.md](COOKBOOK.md)

---

## Story 6: "In-memory rate limiting provides only per-instance protection"

**The comment:**
```typescript
// NOTE: In-memory rate limiting on serverless platforms like Vercel provides
// only per-instance protection. With N concurrent instances, effective limit
// is N × configured_limit. This is acknowledged limitation; upgrade to Redis
// when scale requires.
```

**What happened:** The team initially used an in-memory rate limiter on Vercel.
During a traffic spike, Vercel spun up 8 instances. The effective rate limit
became 8x the configured value. Attackers noticed the limit was "loose" and
exploited it.

**The lesson:** Serverless is not single-process. In-memory state doesn't work.

**The generalized rule:** Any state shared across requests must be in a shared
store (Redis, DB). The only exception is request-scoped cached data.

**See:** [RATE-LIMITING.md](RATE-LIMITING.md) serverless section

---

## Story 7: "Local gateway commonly runs over HTTP... Never force HTTPS upgrades for docs pages"

**The comment:**
```typescript
// NOTE: upgradeInsecureRequests: false for docs pages because local gateway
// commonly runs over HTTP in development. Forcing HTTPS upgrade breaks
// docs browsing. This is fine because docs pages don't handle sensitive data.
// BUT: /api/* does have upgradeInsecureRequests: true enforced.
```

**What happened:** A developer set `upgradeInsecureRequests` globally in CSP.
Everything worked in production (HTTPS everywhere), but local dev broke because
the gateway ran on HTTP. Devs had to work around by turning off the CSP
entirely, defeating the purpose.

**The fix:** Per-path CSP. Docs can upgrade; API must upgrade; localhost gets
a relaxed version.

**The lesson:** One CSP doesn't fit all routes. Dev environments have different
needs than production.

**The generalized rule:** Security headers should be per-path, per-environment.
Documentation pages, API endpoints, admin consoles, and health checks all have
different security profiles.

**See:** [CSP-PATTERNS.md](CSP-PATTERNS.md)

---

## Story 8: "Fail open on upstream errors so auth/API routes stay responsive"

**The comment:**
```typescript
// Rate limiter fail-open on Redis timeout (350ms). Comment: "Fail open on
// upstream errors so auth/API routes stay responsive." This is a deliberate
// tradeoff: brief rate limit bypass during Redis outages vs site-wide failure.
```

**What happened:** When Upstash had a brief outage, the rate limiter was
blocking all requests because it couldn't check limits. The site effectively
went down for 3 minutes. The team added a 350ms timeout with fail-open.

**The tradeoff:** Brief bypass during outage vs total outage. They chose bypass.

**The counter-argument:** For auth endpoints, failing open is worse than failing
closed (attackers can DoS Redis to enable brute force). For regular API, fail-
open is acceptable.

**The lesson:** Fail-open vs fail-closed is endpoint-specific. Document the
decision.

**The generalized rule:** For each dependency failure mode, explicitly decide:
fail-open or fail-closed? Write it in a comment next to the catch block.

**See:** [FAIL-OPEN-PATTERNS.md](FAIL-OPEN-PATTERNS.md)

---

## Story 9: "Premium users get 'free' tier limits... this hasn't been a user-facing issue"

**The comment:**
```typescript
// NOTE: Premium users get "free" tier limits (120/min) instead of "premium"
// (300/min). We'd need to hit the DB in middleware to distinguish, which
// adds 20ms latency to every request. Current: limits are generous enough
// that this hasn't been a user-facing issue.
```

**What happened:** Ideally, premium users should get higher rate limits. But
detecting "premium" in middleware requires a DB call (slow) or a JWT claim
(requires session refresh on subscription change). The team accepted the tradeoff.

**The lesson:** Perfect tier enforcement can be expensive. Sometimes good
enough is better than perfect.

**The generalized rule:** When a security decision has a performance cost, do
the math: cost of the lookup × frequency vs benefit of stricter check. Document
the decision.

**See:** [RATE-LIMITING.md](RATE-LIMITING.md) tier detection section

---

## Story 10: "API routes resolve auth directly and this removes a high-volume Supabase call"

**The comment:**
```typescript
// Skip Supabase session refresh for API routes. API routes resolve auth
// directly via JWT verification. This removes a high-volume Supabase call
// from every API request. Cost savings: ~$400/month at current scale.
```

**What happened:** Every request was calling `supabase.auth.getUser()` which
hits Supabase's API. At scale, this was a significant cost and added latency.
The team added a path-based skip for API routes, relying on direct JWT
verification instead.

**The lesson:** Auth cost is a real thing. Cached or local verification can
significantly reduce latency and cost, if done correctly.

**The generalized rule:** Separate "is the session valid?" (cheap, local JWT
verify) from "is the user still allowed?" (expensive, requires DB). Do the
cheap check on every request, the expensive check only when needed.

**See:** [SESSION-MANAGEMENT.md](SESSION-MANAGEMENT.md)

---

## Story 11: "Superseded stale webhook processing claim"

**The comment:**
```typescript
// Stale claim takeover: if another worker claimed this event more than 10
// minutes ago and the heartbeat is stale, we take over. This handles crashed
// workers that left events half-processed.
```

**What happened:** A webhook handler worker crashed mid-processing. The event
was marked "processing" in the database, so no other worker would touch it.
The event was stuck forever — until the team added stale-claim detection.

**The fix:** (1) Each claim has a heartbeat (updated every 30s). (2) If
heartbeat is >10 min old, a new worker can take over. (3) Original worker's
updates are ignored if they arrive late (via version checking).

**The lesson:** Claim-based coordination has failure modes. Heartbeats and
takeover logic are essential.

**The generalized rule:** For any "claimed resource" pattern (webhook claim,
job lease, lock), include: heartbeat, takeover after timeout, version checking
on updates.

**See:** [COOKBOOK.md](COOKBOOK.md) Stripe webhook handler

---

## Story 12: "invoice.payment_failed can arrive after invoice.payment_succeeded"

**The comment:**
```typescript
// Skipping dunning creation - subscription is active. invoice.payment_failed
// can arrive after invoice.payment_succeeded (retry succeeded, initial failure
// webhook was delayed). Check current status before creating dunning state.
```

**What happened:** Stripe's webhook delivery is not ordered. `invoice.payment_
failed` could arrive hours after `invoice.payment_succeeded`. If the handler
created a dunning email based on the failed event without checking current
state, users got harassment emails after their payment had succeeded.

**The fix:** Before acting on any webhook event, re-fetch current state from
Stripe or check the DB. Don't trust webhook ordering.

**The lesson:** Webhook ordering is a myth. Always re-check state.

**The generalized rule:** Webhook handlers must be idempotent AND
order-independent. Use the webhook event as a trigger, not as truth.

**See:** [BILLING.md](BILLING.md)

---

## Story 13: "Self-healing: copying userId from customer to subscription metadata"

**The comment:**
```typescript
// Self-healing: If subscription.metadata.userId is missing, fetch the customer
// and copy from customer.metadata.userId. Patch the subscription via
// stripe.subscriptions.update so future webhooks are fast. If patch fails:
// CRITICAL log.
```

**What happened:** Early Stripe subscriptions had `userId` only in customer
metadata, not subscription metadata. Webhook handlers had to do an extra
customer fetch on every event. To optimize, the team added self-healing: first
time we see a subscription without metadata, copy it from the customer and
update the subscription.

**The lesson:** Self-healing is OK for optimization. But log loudly when the
heal fails — it may indicate a drift problem worth investigating.

**The generalized rule:** Self-healing is a performance pattern, not a security
pattern. Never self-heal privileges up. Do self-heal denormalized data, with
audit logging.

**See:** [KERNEL.md](KERNEL.md) Axiom 4 (self-heal down, never up)

---

## Story 14: "$0 Premium via Stripe Metadata"

**What we saw:** During a red team exercise, we discovered that the webhook
handler trusted `metadata.userId` from Stripe events. We created a $0 product
in our own Stripe account, crafted a checkout session with `metadata.userId`
set to a victim userId, completed the $0 "purchase," and watched the webhook
activate the victim's subscription.

**The gap:** The handler didn't verify that the event came from OUR Stripe
account. `event.account` was never checked.

**The fix:**
```typescript
if (event.account !== process.env.STRIPE_ACCOUNT_ID) {
  return new Response("Wrong Stripe account", { status: 400 });
}
```

Also: fetch the price from Stripe API and verify it matches the expected plan.

**The lesson:** Webhook signature verification proves the sender. It doesn't
prove the sender is YOU. Check the account ID.

**The generalized rule:** Signature verification is necessary but not
sufficient. Verify: (1) who sent it (signature), (2) that it came from your
account (account ID), (3) that the referenced data matches your expectations
(price, product, plan).

**See:** [ATTACK-SCENARIOS.md](ATTACK-SCENARIOS.md) Scenario A1

---

## Story 15: "Legacy PayPal IPN echo-back with zero idempotency"

**What we saw:** A SaaS still had the legacy PayPal IPN endpoint running
alongside modern webhooks. The IPN endpoint:
- Posted back to `ipnpb.paypal.com` to verify (correct)
- Read user ID from `custom` field (attacker-controlled)
- Granted credits based on `payment_gross` (attacker-controllable via $0.01 txn)
- Had no idempotency check on `txn_id`
- PayPal retries IPN up to 15 times → credits granted up to 15x
- Failed silently on errors (returned 200)

**The attack chain:** Craft a $0.01 PayPal transaction. `custom` = victim's
userId. `payment_gross` = 1000. IPN verifies against PayPal (valid, it's a real
$0.01 transaction). Handler extracts custom field, grants 1000 credits. Retry
14 more times as PayPal backs off. Victim now has 15,000 credits.

**The fix:** Multiple layers. (1) `txn_id` idempotency. (2) Re-derive credit
amount from server-side catalog, not payment. (3) Verify user ID matches
authenticated session. Better: migrate off legacy IPN.

**The lesson:** Legacy payment integrations are attack gold mines. They predate
modern signature and idempotency patterns. Audit them or remove them.

**The generalized rule:** Legacy code paths have legacy security. Don't assume
security work you did recently covers the code that's been running for 5 years.

---

## Story 16: "Credit amount trusted from client-controlled custom_id"

**What we saw:** Another variant — the PayPal order creation stored
`custom_id=userId:credits:promoCode` on the order. On capture, the code parsed
the credits from custom_id without verifying against the catalog.

```typescript
if (customId && customId.includes(':')) {
  const [uid, creditsStr, promo] = customId.split(':');
  credits = parseInt(creditsStr, 10) || 0;  // ← attacker sets credits
}
```

Attacker creates a PayPal order with `custom_id=attacker_uid:99999:FAKE`, pays
$0.01, gets 99,999 credits.

**The fix:** `custom_id` should only be used for CORRELATION, not for VALUE.
Look up the expected credits from the catalog based on the price paid.

**The lesson:** Any field you control on the payment provider side can end up
in the webhook. Treat it as untrusted.

**The generalized rule:** Payment provider metadata is attacker-controllable if
the attacker can create payments. Always derive values from your server-side
catalog, not from metadata.

**See:** [BILLING.md](BILLING.md)

---

## Story 17: "Free-credit signup bonus IP dedup bypass via X-Forwarded-For"

**What we saw:** A signup flow that granted free credits based on IP deduplication
to prevent abuse. The implementation:
```typescript
const ip = request.headers.get('x-forwarded-for') || 'unknown';
if (ip === 'unknown') { /* skip dedup check */ }
const existing = await db.query.bonuses.findFirst({ where: eq(ip, ip) });
if (existing) return error('already claimed');
```

Multiple failure modes:
1. Trusts `x-forwarded-for` without infra validation
2. Missing header → `'unknown'` → dedup skipped
3. TOCTOU: check, then create (no unique constraint)
4. NAT'd households share IP (legitimate users blocked)
5. `console.log('session:', session)` leaks session tokens

**The fix:** Multi-signal anti-abuse. Don't rely on IP alone. Use: email
domain, device fingerprint, behavior patterns, CAPTCHA.

**The lesson:** Simple IP-based deduplication is both too permissive (easy to
bypass) and too restrictive (blocks NAT'd users).

**The generalized rule:** Anti-abuse should be multi-signal. Any single signal
is bypassable. Any single hard block has false positives.

---

## Story 18: "Role from env var, never from client"

**The comment:**
```typescript
export function getServerAdminRole(): AdminRole {
  const raw = process.env.JFP_ADMIN_ROLE;
  // ...
  // privilege can never be escalated by a client-supplied header.
}
```

**What happened:** Earlier, the team had used a `X-Admin-Role` header for
debugging. A developer accidentally left the check in the production code path.
During a red team exercise, this was exploited to gain admin privileges by
setting the header.

**The fix:** Role comes from server environment or database, never client.
Development debugging uses a separate env var guarded by `NODE_ENV !==
'production'`.

**The lesson:** Debug features in production are a recipe for incidents.
Explicit guards with environment checks.

**The generalized rule:** Client-supplied input can never directly grant
privilege. Privilege is determined server-side from server state.

---

## Story 19: "Dev-bypass with localhost guard + opt-in flag + warning log"

**The pattern:**
```typescript
if (
  process.env.NODE_ENV !== 'production' &&
  process.env.JFP_ADMIN_DEV_BYPASS === 'true' &&
  isLocalhostOrigin(request)
) {
  console.warn('🚨 DEV BYPASS ACTIVE 🚨');
  return mockAdminUser;
}
```

**What happened:** Multiple teams had been burned by "left dev bypass on in
prod." This pattern uses three conditions:
1. Not in production environment
2. Explicit opt-in env var
3. Request from localhost

Also: loud warning log so developers remember it's active.

**The lesson:** Dev bypasses are necessary but dangerous. Three-condition guards
make them hard to accidentally trigger in production.

**The generalized rule:** Any bypass of security controls must have:
(a) environment check, (b) explicit opt-in flag, (c) physical/network constraint,
(d) visible warning when active.

---

## Story 20: "PKCE code fingerprint truncated to 64 bits"

**What we saw:** An OIDC implementation truncated the PKCE code_verifier
fingerprint to 64 bits for storage efficiency. At scale, birthday collisions
caused legitimate concurrent OAuth flows to be rejected as "replays."

**The fix:** Use full 256-bit SHA-256 output. Storage cost is negligible;
correctness is not.

**The lesson:** Cryptographic truncation has consequences. Birthday bound =
2^(n/2), where n is the bit length. 64-bit fingerprint → collisions at 4
billion operations, which is reachable for popular services.

**The generalized rule:** Don't truncate cryptographic outputs. The "optimization"
is false economy.

**See:** [CRYPTO-FUNDAMENTALS.md](CRYPTO-FUNDAMENTALS.md)

---

## How to Add to This Guide

When you find a security-relevant comment in production code, or when a
post-mortem reveals a non-obvious lesson, add it here with the structure:

1. **The comment** (verbatim, anonymized)
2. **What actually happened** (the story)
3. **The fix** (what they did)
4. **The lesson** (the specific insight)
5. **The generalized rule** (how to apply elsewhere)

The goal is to preserve institutional knowledge that would otherwise be lost
when engineers leave or memories fade. These stories are more valuable than
any checklist because they encode the "why" behind rules.

---

## Meta-Lessons

Across all 20 stories, themes emerge:

### Theme 1: Comments reveal history
When you see a non-obvious choice, there's usually a story behind it. Read the
git blame and commit messages.

### Theme 2: "Ideal" security conflicts with reality
Framework quirks, cost constraints, latency requirements, and UX needs all
push back against idealized security. Document the compromises.

### Theme 3: Every incident becomes a new pattern
Most of these stories originated as incidents. The fixes became the patterns.
Future incidents will generate future patterns.

### Theme 4: Non-obvious is the norm
Security is rarely intuitive at the design stage. Most vulnerabilities are
discovered by surprise. Humility and curiosity are the auditor's best traits.

### Theme 5: Write it down
Every story in this file started with someone thinking "I should write this
down." Future engineers will thank you.
