# Real-World Case Studies

Anonymized case studies from production SaaS security audits. Each case study documents the vulnerability, discovery method, impact, and fix.

---

## Case 1: PayPal Subscription Hijacking via custom_id

**Severity:** CRITICAL
**Discovery method:** Manual code review of PayPal webhook handler
**Project type:** SaaS with dual-provider (Stripe + PayPal) billing

### Vulnerability
PayPal's `custom_id` field in subscription webhooks is set during checkout creation and passed back in all subsequent webhook events. It was used to identify which user a subscription belongs to. However, `custom_id` is attacker-controlled -- an attacker can create a PayPal subscription with a victim's userId as the custom_id, causing the webhook handler to assign the subscription to the victim's account.

### Impact
Attacker creates a subscription, victim gets billed. Or attacker's subscription status overwrites victim's legitimate subscription.

### Fix
Implemented `validatePayPalUserId()` that cross-references three fields:
1. User exists in database
2. User has no existing PayPal customerId (first-time linking OK)
3. OR user's existing customerId matches the webhook's payerId
4. Mismatches: log security event + reject

### Lesson
**Never trust provider-supplied identity fields.** Always validate the full identity chain against your own database before updating subscription status.

---

## Case 2: TOCTOU Race Conditions in Checkout Flows (10 Patterns)

**Severity:** CRITICAL to HIGH (varies by pattern)
**Discovery method:** Systematic audit of all checkout routes for atomicity
**Project type:** SaaS with team billing and seat management

### Vulnerability
Checkout creation follows a pattern: (1) read current state, (2) validate eligibility, (3) create checkout session. Steps 1-2 happen outside a database transaction, creating a Time-of-Check-to-Time-of-Use gap. Concurrent requests between steps 2 and 3 could create duplicate subscriptions or bypass eligibility checks.

### Worst Case: Team PayPal Checkout
THREE separate state checks (existing subscription, pending checkout, cancellation grace period) all done without locks. Any concurrent modification between checks creates an inconsistent state.

### Fix
- Wrapped checkout creation in `SELECT ... FOR UPDATE` transaction
- Added unique constraints on (userId/orgId, provider)
- Implemented pending checkout state with 30-minute TTL
- Added optimistic concurrency control in webhook handlers

### Lesson
**Payment checkout creation is a critical section.** Every checkout flow must use database-level locking. Check for this pattern in every route that creates a Stripe/PayPal session.

---

## Case 3: Missing RLS on Core Tables

**Severity:** HIGH
**Discovery method:** Script comparing pg_tables against pg_policies
**Project type:** SaaS with Supabase backend

### Vulnerability
An RLS repair migration covered 73 tables but excluded the most critical ones: `users` (email, admin flag, subscription status), `organizations` (billing info, SSO config), `organization_members`, `subscriptions`, and `external_identities`. These tables had policies in an earlier migration that may not have been re-applied.

### Impact
Any authenticated user could potentially read all user emails, subscription statuses, and organization billing information via direct Supabase client queries.

### Fix
- Added RLS policies for all excluded core tables
- Created a CI script that verifies every table in `public` schema has either RLS policies or an explicit exemption
- Added 8 intelligence tables that had RLS never enabled

### Lesson
**RLS migrations must be validated against the complete table inventory.** Use a script:
```sql
SELECT tablename FROM pg_tables WHERE schemaname = 'public'
EXCEPT
SELECT DISTINCT tablename FROM pg_policies WHERE schemaname = 'public';
```
Run this in CI after every migration.

---

## Case 4: Cache Invalidation Failure Causing Entitlement Mismatch

**Severity:** CRITICAL
**Discovery method:** Tracing the post-webhook flow in serverless environment
**Project type:** SaaS with dashboard cache

### Vulnerability
After webhook updates subscription status in DB, cache invalidation runs in an `after()` callback. In Vercel's serverless environment, `after()` is best-effort -- if the worker suspends, the callback never runs. Result: user pays, DB says "active", but dashboard cache shows "not subscribed" for up to 5 minutes.

Additionally, the cache event system had no subscription-related events at all. Event types only included: `usage:recorded`, `skill:deleted`, `skill:updated`, `user:settings_changed`, `manual:refresh`.

### Fix
- Made cache invalidation synchronous within the webhook handler
- Added `subscription:activated`, `subscription:cancelled`, `subscription:status_changed` to cache event types
- Ensured entitlement authorization checks hit DB directly, not cache

### Lesson
**Never use unreliable callbacks for security-critical state updates.** Authorization decisions must read from the source of truth (DB), not cache. Cache is for UX, not security.

---

## Case 5: Protocol-Relative URL Open Redirect

**Severity:** HIGH
**Discovery method:** Manual review of redirect handling code
**Project type:** SaaS with auth redirects

### Vulnerability
Redirect validation checked `startsWith("/")` to ensure same-origin redirects. However, `//evil.com` starts with "/" but is a protocol-relative URL that redirects to the attacker's domain.

### Impact
Used in phishing: attacker sends `https://app.example.com/login?returnTo=//evil.com/fake-login` which redirects after auth to attacker-controlled page.

### Fix
```typescript
// Added !startsWith("//") guard
if (url.startsWith("/") && !url.startsWith("//")) {
  return redirect(url);
}
```

### Lesson
**Every redirect from user input needs the `//` check.** Create a single `getSafeRedirectPath()` function and use it at every redirect point. Grep for `redirect(` and verify each one uses the safe function.

---

## Case 6: Secrets Committed to Version Control

**Severity:** CRITICAL (remediated)
**Discovery method:** `git log --all --diff-filter=A -- .env*`
**Project type:** SaaS with Stripe/PayPal/Supabase

### Vulnerability
`.env.local` committed to git containing: Stripe live secret key (`sk_live_...`), Supabase service role key, database URL with password, Google client secret, JWT secret, and all API tokens.

### Impact
Anyone with repo access (or if repo was briefly public) had full admin access to payment systems, database, and auth infrastructure.

### Fix
1. Rotated ALL exposed secrets immediately
2. Removed file from git tracking
3. Used `git filter-repo` to purge from history
4. Added `.env.local` to `.gitignore`
5. Added `detect-secrets` pre-commit hook
6. Created `.env.example` with placeholder values

### Lesson
**Pre-commit hooks for secret detection are not optional.** Use `detect-secrets`, `gitleaks`, or equivalent. Audit `.gitignore` at project creation.

---

## Case 7: Seat Count Bypass in Team Billing

**Severity:** CRITICAL
**Discovery method:** Code review of team member addition flow
**Project type:** SaaS with team/org subscription model

### Vulnerability
Two issues:
1. `createTeamCheckoutSession()` reads seat count without locks. Between reading and creating Stripe session, concurrent member additions cause under-billing.
2. `pauseIndividualSubscriptionForOrgMember()` is called for all members added but there is NO check that adding a member would exceed `maxSeats`. Users could add unlimited members to the org.

### Impact
Unlimited free team members. Stripe bills for fewer seats than actual usage.

### Fix
- Transaction advisory lock before reading seat count
- `maxSeats` validation in member addition flow
- Seat delta calculation for Stripe subscription update

### Lesson
**Team billing requires seat count enforcement at two points:** checkout creation AND member addition. Both must be atomic with the count read.

---

## Case 8: OWASP Security Test Suite as Prevention

**Discovery method:** Proactive security test creation
**Project type:** SaaS with premium content

### Approach
Created 269 security tests across 5 test files covering OWASP Top 10:
- `auth.security.test.ts` -- JWT validation, device code auth, session management
- `authz.security.test.ts` -- tier-based access control, IDOR prevention
- `input.security.test.ts` -- XSS, SQL injection, path traversal
- `headers.security.test.ts` -- CSP, HSTS, CORS, cookie attributes
- `csrf.security.test.ts` -- token validation, SameSite cookies

### Lesson
**Build security tests proactively, not reactively.** A test suite covering OWASP Top 10 catches regressions before they reach production. Run in CI on every PR.
