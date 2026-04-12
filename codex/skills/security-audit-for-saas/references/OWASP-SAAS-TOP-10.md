# OWASP SaaS Top 10 — Breach-Driven Edition

The standard OWASP Top 10 was written for generic web applications. It misses the
classes of vulnerabilities that actually dominate SaaS breaches. This file is the
**SaaS-specific Top 10**, synthesized from ~50 public SaaS breach post-mortems and
the CASS mining of production SaaS audits.

Use this for: prioritizing an audit, training new security reviewers, explaining
risk to non-technical stakeholders, regulatory reporting.

---

## Table of Contents

1. [S01: Subscription & Entitlement Bypass](#s01-subscription--entitlement-bypass)
2. [S02: Cross-Tenant Exposure (IDOR/RLS Gaps)](#s02-cross-tenant-exposure-idorrls-gaps)
3. [S03: Webhook Forgery & Replay](#s03-webhook-forgery--replay)
4. [S04: Admin Console Compromise](#s04-admin-console-compromise)
5. [S05: PII/Secret Leakage via Errors/Logs](#s05-piisecret-leakage-via-errorslogs)
6. [S06: Broken Authentication & Sessions](#s06-broken-authentication--sessions)
7. [S07: OAuth/SSO Misconfiguration](#s07-oauthsso-misconfiguration)
8. [S08: Supply Chain & Third-Party Compromise](#s08-supply-chain--third-party-compromise)
9. [S09: Insecure Uploads & File Processing](#s09-insecure-uploads--file-processing)
10. [S10: Insufficient Logging & Incident Response](#s10-insufficient-logging--incident-response)

---

## S01: Subscription & Entitlement Bypass

**Definition:** A free or expired user accesses paid features, or a user gets
service without completing payment.

### Canonical patterns
- Stale cache after subscription cancellation → user retains access
- PayPal `custom_id` attacker-controlled → subscription hijacking
- Refund processed but entitlement not demoted
- TOCTOU between "check subscription" and "use feature"
- Server action creates premium content without checking user's tier
- Org-level subscription bypass of individual subscription check
- Grace period logic allows access after canceled
- `subscription_status` derived from cache, not DB
- Unknown provider event type silently swallowed
- Trial reset via email alias (`user+1@example.com`)

### Why SaaS-specific
Generic web apps don't have "entitlement" — they have "logged in" or "not." SaaS
has a layered grant system (free, trial, paid, team, admin) with cache, webhook,
and reconciliation layers. Each layer can fail independently.

### Detection
- Query audit log for "premium feature access" events by users with no active
  subscription during the access window
- Compare cache vs DB subscription status for all users weekly
- Load-test the subscription check endpoint; measure DB hits vs cache hits
- Red team: "The $0 Premium Exploit" from [ATTACK-SCENARIOS.md](ATTACK-SCENARIOS.md)

### Prevention
See [BILLING.md](BILLING.md), [ENTITLEMENTS.md](ENTITLEMENTS.md),
[FAIL-OPEN-PATTERNS.md](FAIL-OPEN-PATTERNS.md) Pattern 2.

### Historical analog
Many SaaS billing incidents remain unreported publicly, but private audits show
this is the most common critical finding in SaaS security reviews.

---

## S02: Cross-Tenant Exposure (IDOR/RLS Gaps)

**Definition:** User in Tenant A can read, modify, or infer data from Tenant B.

### Canonical patterns
- RLS policy subquery references another table with RLS that blocks access
- App-layer check uses `session.defaultOrgId` instead of the URL's tenant
- Aggregate query (count, sum) leaks other-tenant data by inference
- Shared cache keyed by resource ID without tenant prefix
- Admin dashboard shows "top users" without tenant scoping
- Deletion doesn't cascade; orphan rows retain access
- Search/index includes other-tenant records
- OG image endpoint fetches arbitrary user data for "public profile" rendering
- Push notification subscription lookup by endpoint-only (not endpoint+user)
- Service role key used in code path that should have used scoped user client

### Why SaaS-specific
Generic apps don't have tenants. SaaS multi-tenancy is the single most common
source of catastrophic breaches (Salesforce, Zoom, Slack each had variants).

### Detection
- Spin up 2 test tenants with sample data; try every endpoint from Tenant A
- RLS coverage script ([scripts/rls-coverage.sql](../scripts/rls-coverage.sql))
- Search for `session.orgId` vs `params.orgId` inconsistencies

### Prevention
See [MULTI-TENANT.md](MULTI-TENANT.md), [DATABASE.md](DATABASE.md).

### Historical analog
- **Snowflake 2024:** credential stuffing enabled cross-tenant data exfiltration
  across ~165 organizations
- **Twilio 2022:** employees phished → customer data access across tenants

---

## S03: Webhook Forgery & Replay

**Definition:** Attacker sends forged or replayed webhook events to trigger
state changes (subscription activation, refund, data sync).

### Canonical patterns
- Webhook endpoint skips signature verification if header missing
- Signature verification on parsed JSON body (not raw bytes)
- No event ID deduplication → duplicate processing
- No timestamp validation → replay attacks
- `return true` in catch block of signature verification
- Provider webhook handler trusts all provider-signed events (wrong provider
  account forgery)
- Cron reconciliation skips signature verification for "known good" sources

### Why SaaS-specific
Webhooks are the control plane for billing and third-party integration. A forged
webhook can do more damage than a forged API call (admin privileges, state
transitions).

### Detection
- Send unsigned webhook → should return 400/401
- Send signed-but-tampered webhook → should return 401
- Send duplicate webhook → second should be idempotent (200 no-op)
- Send webhook with stale timestamp → should reject
- Audit: webhook signature failure rate anomalies

### Prevention
See [BILLING.md](BILLING.md), [THIRD-PARTY.md](THIRD-PARTY.md),
[COOKBOOK.md](COOKBOOK.md) patterns 1-2.

### Historical analog
- **Shopify multiple incidents:** forged webhooks used to trigger refund
  workflows in connected apps
- **GitHub webhook replay:** attackers used replay to trigger repeated CI runs

---

## S04: Admin Console Compromise

**Definition:** An attacker gains access to an admin account or bypasses admin
authorization checks.

### Canonical patterns
- Admin whitelist self-heal: `if email in whitelist → auto-set isAdmin = true`
  (undoes revocations)
- Admin check based on email `@company.com` suffix without MFA
- Admin impersonation without audit log or rate limit
- Admin session with no timeout / no re-authentication for sensitive actions
- Impersonator cookie readable by any user (lacks HttpOnly/Secure/SameSite)
- Admin API endpoint checks `isAdmin` flag but the flag source is a cached column
- Admin actions logged in the same table users can query
- Single-env-var admin check (`ADMIN_EMAIL=...`)
- Debug/internal endpoints on the public-facing domain
- Support tool has broader permissions than any customer-facing admin

### Why SaaS-specific
Admin consoles in SaaS have cross-tenant reach by design. Compromising one admin
account is equivalent to compromising every tenant.

### Detection
- Audit log queries for admin actions outside business hours
- Admin login from new country / device
- High volume of admin actions in short time
- Honeypot: fake "sensitive" admin action that alerts on use
- Red team: "The Admin Takeover" from [ATTACK-SCENARIOS.md](ATTACK-SCENARIOS.md)

### Prevention
See [AUTH.md](AUTH.md), [ADMIN-ESCALATION-PATHS.md](ADMIN-ESCALATION-PATHS.md),
[IMPERSONATION.md](IMPERSONATION.md).

### Historical analog
- **Twitter 2020:** internal admin tool compromised via social engineering →
  attackers tweeted from ~130 high-profile accounts
- **Uber 2022:** MFA fatigue attack → attacker accessed internal tools via
  compromised contractor account
- **LastPass 2022:** engineer's Plex client → admin credentials → vault data

---

## S05: PII/Secret Leakage via Errors/Logs

**Definition:** Sensitive data appears in error messages, stack traces, logs,
analytics events, or other unexpected locations.

### Canonical patterns
- Stack trace returned to client in production (reveals schema, paths, versions)
- Error message includes user email or internal user ID
- Logs contain request bodies with PII
- OAuth error response body logged verbatim (echoes `client_secret`/`refresh_token`)
- Sentry captures full request headers including session cookies
- GA4/Mixpanel events include email or full name
- Health endpoint shows env vars or DB URL
- `.env.local` committed to git
- Build output contains secrets from env substitution
- Support tool displays raw JSON with internal fields

### Why SaaS-specific
SaaS apps log heavily for debugging/observability, and the volume of data
processed means leakage vectors are everywhere. One error message that includes
an email is a free enumeration oracle at scale.

### Detection
- Grep logs for patterns: emails, JWTs, API key prefixes (`sk_`, `whsec_`)
- Automated scan of Sentry/Datadog events for PII
- Secret scan of build output ([scripts/leak-scan.sh](../scripts/leak-scan.sh))
- Honeypot: fake API key in env; alert on any use

### Prevention
See [KEY-MANAGEMENT.md](KEY-MANAGEMENT.md), [AUDIT-LOGGING.md](AUDIT-LOGGING.md),
[DATA-SECURITY.md](DATA-SECURITY.md).

### Historical analog
- **GitLab various incidents:** sensitive tokens appearing in CI logs
- **Many startups:** production secrets leaked via Sentry → indexed by attackers

---

## S06: Broken Authentication & Sessions

**Definition:** Attackers can bypass login, impersonate users, or maintain
sessions beyond revocation.

### Canonical patterns
- JWT verified with `jwt.decode()` instead of `jwt.verify()`
- JWT algorithm not locked (allows `alg: none`)
- JWT `kid` header matches any active signing key during rotation window
- Session fixation: pre-login session ID preserved after auth
- Refresh token rotation DoS: legit users locked out on replay detection
- Password reset token in query param (leaks via Referer, analytics)
- Timing-safe comparison missing on secret check
- Device fingerprinting trivially spoofable (`hash(userAgent + IP)`)
- MFA bypass via "remember me" flag that survives password reset
- Session cookie lacks `HttpOnly` / `Secure` / `SameSite`
- Cookie named `sb-<ref>-auth-token` trusted by middleware for tier assignment

### Detection
- JWT library config review (algorithms, issuer, audience, expiry)
- Attempt login with various tampered JWT variants
- Timing-attack test on login endpoint (email enumeration)
- Session fixation test: set cookie pre-login, verify new ID post-login

### Prevention
See [AUTH.md](AUTH.md), [SESSION-MANAGEMENT.md](SESSION-MANAGEMENT.md),
[TIMING-SAFE.md](TIMING-SAFE.md).

### Historical analog
- **Microsoft Storm-0558 (2023):** stolen signing key → forged JWTs for cloud
  services
- **Twitter "zero-day" (2022):** JWT implementation allowed account enumeration
- **Okta (2022):** session persistence after password reset enabled takeovers

---

## S07: OAuth/SSO Misconfiguration

**Definition:** Federated identity flows are misconfigured, enabling account
takeover or data exfiltration.

### Canonical patterns
- `redirect_uri` allowlist uses `startsWith` (allows `https://example.com.evil.com`)
- OAuth `state` parameter missing or not validated timing-safely
- PKCE not enforced for public clients
- ID token signature not verified (only access token)
- ID token `aud` (audience) not checked
- SAML InResponseTo validated non-timing-safely
- SSO provisioning auto-joins user to any org whose domain matches their email
- OAuth scopes upgraded mid-flow without consent
- Refresh token stored in plaintext
- Client secret in public (mobile) app

### Why SaaS-specific
SSO is the #1 enterprise sales requirement. Rushing SSO implementation to close
deals is the most common SaaS security regression.

### Detection
- Audit OAuth flow: check every parameter validation
- Test redirect_uri with various bypass payloads
- Verify SSO provisioning logic: can an attacker's email join victim's org?

### Prevention
See [AUTH.md](AUTH.md), [THIRD-PARTY.md](THIRD-PARTY.md).

### Historical analog
- **GitHub OAuth 2022:** Heroku/Travis CI tokens abused to clone private repos
- **Okta 2022:** Sitel support contractor compromise → Okta admin access
- **Dropbox 2022:** OAuth tokens exfiltrated from GitHub, used to access
  proprietary code

---

## S08: Supply Chain & Third-Party Compromise

**Definition:** An attacker compromises a dependency or third-party service
and uses that to attack your SaaS.

### Canonical patterns
- Typosquatting: `reqeust` instead of `request`
- Dependency confusion: attacker publishes private package name on public npm
- Malicious `postinstall` script exfiltrates env vars
- Compromised build tool (SolarWinds SUNBURST pattern)
- Unpinned GitHub Action version (`@main` instead of SHA)
- CI secrets exposed to forked PRs
- Third-party script tag on admin page (supply chain for admin session)
- Vendor admin has credentials to customer data
- Compromised analytics script (Codecov 2021 pattern)
- npm package hijacked via abandoned maintainer account

### Why SaaS-specific
SaaS apps have 100+ dependencies, each with their own update cadence and
security posture. A single compromised dependency affects every customer.

### Detection
- Continuous dependency scanning (Snyk, Socket.dev)
- Lock file integrity (`npm ci` not `npm install`)
- SBOM generation and review
- Hash-pinning in CI
- Vendor assessment before integration

### Prevention
See [THIRD-PARTY.md](THIRD-PARTY.md), [INFRASTRUCTURE.md](INFRASTRUCTURE.md).

### Historical analog
- **SolarWinds SUNBURST (2020):** compromised build → backdoored updates → 18K
  organizations affected
- **Codecov (2021):** bash uploader script modified to exfiltrate CI secrets
- **ua-parser-js (2021):** npm package hijacked, malicious version published
- **xz-utils (2024):** long-running social engineering → backdoor in compression
  library

---

## S09: Insecure Uploads & File Processing

**Definition:** File upload or processing enables attacker code execution or
data theft.

### Canonical patterns
- File type validation by extension only (not content)
- MIME type trusted from client
- Uploaded files stored with predictable names
- Uploaded files served with `Content-Type: application/octet-stream` but named
  `.html` → XSS
- SVG upload with embedded JavaScript
- Zip bomb / decompression bomb
- Path traversal in archive extraction (`../../etc/passwd`)
- Symlink in uploaded archive escapes extraction directory
- PDF/image parser has CVEs (ImageTragick, PDF.js vulns)
- Thumbnail generator runs user-controlled code (ImageMagick)
- File stored in S3 bucket with public read default

### Why SaaS-specific
SaaS with user-generated content (documents, images, avatars) have many more
upload surfaces than simple apps.

### Detection
- Fuzz file upload endpoints with malicious payloads
- Scan extracted archives for symlinks and path traversal
- Audit file serving headers

### Prevention
- Validate file content via magic bytes, not extension
- Store uploads in separate domain/subdomain to prevent same-origin attacks
- Reprocess images through trusted libraries (Sharp, Pillow) to strip metadata
- Scan for symlinks before extraction

### Historical analog
- **ImageMagick "ImageTragick" (2016):** RCE via crafted image
- **Multiple SaaS incidents:** SVG XSS in user avatars

---

## S10: Insufficient Logging & Incident Response

**Definition:** The SaaS lacks the observability to detect or respond to a
security incident.

### Canonical patterns
- No audit log at all
- Audit log in same DB as user data (attacker can delete it)
- Logs retained <30 days (most breaches discovered 200+ days later)
- No alerting on auth failure spikes
- No playbook for rotation on key compromise
- No forensic queries documented
- No customer notification templates
- Logs include PII, so log retention is limited by GDPR
- Log destination (Datadog, Sentry) is itself a breach surface
- No test of incident response (never a tabletop)

### Why SaaS-specific
SaaS incidents have legal notification requirements (GDPR 72 hours,
state breach laws, SOC 2 obligations). Insufficient logging converts a
recoverable incident into a regulatory disaster.

### Detection
- Review audit log schema and coverage
- Review alerting rules
- Review retention policy
- Run a tabletop incident response exercise

### Prevention
See [AUDIT-LOGGING.md](AUDIT-LOGGING.md), [INCIDENT-RESPONSE.md](INCIDENT-RESPONSE.md),
[OBSERVABILITY.md](OBSERVABILITY.md).

### Historical analog
- **Equifax (2017):** breach went undetected for 76 days; insufficient monitoring
- **Marriott (2018):** 4 years of undetected access before discovery
- **Uber (2016):** breach and cover-up — insufficient response process

---

## Priority Ranking by Frequency × Impact

Based on CASS mining and public breach analysis:

| Rank | Category | Frequency | Impact | Priority |
|------|---------|-----------|--------|----------|
| 1 | S01 (Entitlement bypass) | Very high | High | **P0** |
| 2 | S03 (Webhook forgery) | High | Very high | **P0** |
| 3 | S02 (Cross-tenant) | Medium | Catastrophic | **P0** |
| 4 | S04 (Admin compromise) | Medium | Catastrophic | **P0** |
| 5 | S05 (PII leakage) | High | High | **P1** |
| 6 | S06 (Broken auth) | High | High | **P1** |
| 7 | S07 (OAuth/SSO) | Medium | High | **P1** |
| 8 | S10 (Logging/IR) | Very high | Medium (amplifier) | **P1** |
| 9 | S08 (Supply chain) | Low | Very high | **P2** |
| 10 | S09 (Uploads) | Low (if no uploads) | High | **P2** |

Audits should address P0 items first, in order. P1 items can be addressed in
parallel once P0 is clean.

---

## Mapping to Other Resources

- **Standard OWASP Top 10:** This list subsumes several OWASP entries (A01
  Broken Access Control → S02, A02 Cryptographic Failures → part of S06, A07
  Auth Failures → S06/S07) and adds SaaS-specific items (S01, S03, S04, S10)
- **Kernel Axioms:** Each of the 10 axioms from [KERNEL.md](KERNEL.md) catches
  vulnerabilities across multiple S-categories
- **MITRE ATT&CK:** See [MITRE-ATTACK-MAPPING.md](MITRE-ATTACK-MAPPING.md) for
  technique-level mapping
- **Compliance frameworks:** See [COMPLIANCE-DEEPDIVE.md](COMPLIANCE-DEEPDIVE.md)
  for SOC 2 / GDPR / PCI-DSS / HIPAA / ISO 27001 cross-walks
