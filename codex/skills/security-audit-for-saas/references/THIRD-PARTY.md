# Third-Party Integration Security

Every third-party integration is a trust boundary, a credential store, and an
attack surface. This file is the checklist for auditing SaaS integrations with
Stripe, PayPal, Auth0, Supabase, SendGrid, Slack, GitHub, and similar.

---

## The Integration Threat Model

Each integration has three attack surfaces:

1. **Outbound:** Your code sends data to them. What data? Can it be crafted maliciously?
2. **Inbound:** They send data to you (webhooks, callbacks). Can it be forged?
3. **Credentials:** You hold tokens/keys for them. Can they be leaked?

---

## Webhook Verification Matrix

Every provider has a different signature scheme. Know each one.

| Provider | Verification | Gotchas |
|----------|-------------|---------|
| **Stripe** | HMAC-SHA256 via `stripe.webhooks.constructEvent()` | Raw body required; timestamp tolerance |
| **PayPal** | API call to `/v1/notifications/verify-webhook-signature` | 5 headers required; PayPal API must be available |
| **Twilio** | HMAC via `x-twilio-signature` | URL + params concatenated for signature |
| **SendGrid** | ECDSA via `x-twilio-email-event-webhook-signature` | Public key from config |
| **Slack** | HMAC via `x-slack-signature` | Timestamp + body signed |
| **GitHub** | HMAC via `x-hub-signature-256` | Body as-received, no parsing first |
| **Linear** | HMAC via `linear-signature` | Raw JSON body |
| **Intercom** | HMAC via `x-hub-signature` | Hex-encoded signature |

**Rule:** For every inbound webhook, verify signature BEFORE any parsing or
action. Reject on missing signature. See [COOKBOOK.md](COOKBOOK.md) for Stripe and
PayPal verification patterns.

---

## OAuth Integration Security

### Redirect URI Validation

OAuth providers redirect back to your configured URI with an authorization code.
The `redirect_uri` parameter is the attack surface.

**Vulnerable:**
```typescript
// "Allow any subdomain" via startsWith
if (redirectUri.startsWith("https://example.com")) return true;
// Allows: https://example.com.evil.com, https://example.comX.evil.com
```

**Safe:**
```typescript
// Exact match against allowlist
const ALLOWED_REDIRECTS = new Set([
  "https://example.com/auth/callback",
  "https://app.example.com/auth/callback",
]);
if (!ALLOWED_REDIRECTS.has(redirectUri)) return reject();
```

### State Parameter

Every OAuth flow MUST include a state parameter:
- Generated fresh per request (crypto random)
- Stored server-side before redirect
- Validated on callback using timing-safe comparison
- Single-use (delete after validation)

### PKCE

Required for public clients (mobile, SPA). Recommended for all clients as
defense-in-depth.

```typescript
const codeVerifier = base64UrlEncode(crypto.randomBytes(32));
const codeChallenge = base64UrlEncode(sha256(codeVerifier));

// Redirect with code_challenge=<codeChallenge>, code_challenge_method=S256
// On callback, exchange code using code_verifier
```

### Token Storage

- Access tokens: in-memory only if possible; else encrypted at rest
- Refresh tokens: encrypted at rest, hashed in DB (store hash, compare hash)
- ID tokens: short-lived, not stored

### OAuth Error Body Leak (real vulnerability!)

```go
// BAD: error message includes response body, which may echo refresh_token
return fmt.Errorf("refresh error %d: %s", resp.StatusCode, string(body))
```

The OAuth response body can echo back `client_secret` or `refresh_token` from
the request. Logging this error exfiltrates secrets. Real finding from caam audit.

**Fix:** Treat OAuth response bodies as untrusted. Log status code and error_description
from a sanitized allowlist; never the raw body.

---

## Credential Rotation

### Per-Provider Rotation Schedule

| Provider | Frequency | Trigger |
|----------|-----------|---------|
| Stripe secret key | 90 days | Any team member leaves |
| Stripe webhook secret | 180 days | Webhook endpoint changes |
| PayPal client secret | 180 days | Any team member leaves |
| Supabase service role | 90 days | Any team member leaves |
| GitHub deploy token | 30 days | Each deploy (short-lived) |
| Slack bot token | 180 days | - |
| Email API key | 90 days | - |

### Rotation Without Downtime

Most providers allow multiple active keys simultaneously:

1. Create new key (both old and new now valid)
2. Update env var in deployment
3. Deploy
4. Verify new key is active in logs
5. Revoke old key
6. Verify old key no longer works

**Critical:** Don't skip step 5. Leaving old keys active defeats rotation.

---

## Certificate Pinning (Where Supported)

For critical OAuth providers (Claude, OpenAI, Stripe, PayPal), consider cert pinning.

```typescript
import https from "https";
import fs from "fs";

const PINNED_FINGERPRINT = "SHA256:..."; // From provider's public docs

const agent = new https.Agent({
  checkServerIdentity: (host, cert) => {
    if (cert.fingerprint256 !== PINNED_FINGERPRINT) {
      return new Error("Certificate fingerprint mismatch");
    }
    return undefined;
  },
});

await fetch("https://api.provider.com/...", { agent });
```

**Tradeoff:** Cert rotation by the provider will break your integration. Have a
runbook.

---

## Dependency Vulnerability Scanning

### Continuous Scanning

```bash
# Node.js
npm audit --audit-level=high
pnpm audit --audit-level=high

# Python
pip-audit

# Rust
cargo audit

# Go
govulncheck ./...
```

Run in CI on every PR. Fail build on high/critical vulnerabilities.

### Lock File Integrity

- Always commit lock files (`package-lock.json`, `pnpm-lock.yaml`, `Cargo.lock`, `Pipfile.lock`)
- Use `npm ci` not `npm install` in CI (strict lock file adherence)
- Hash-pin dependencies where possible (`--integrity` flags)

### Supply Chain Attack Mitigation

- **Typosquatting:** Audit new dependencies manually. `reqeust` is not `request`.
- **Dependency confusion:** Private packages should use a scoped namespace; never a
  name that could be squatted on public npm.
- **Postinstall scripts:** Disable them: `npm config set ignore-scripts true`.
  Enable per-package only when needed.
- **Dependency review bots:** Socket.dev, Snyk, Dependabot.

---

## Vendor Security Assessment

Before integrating a new third-party SaaS, run this checklist:

### Security posture
- [ ] SOC2 Type II? (ask for report)
- [ ] Pentest report available?
- [ ] Incident history public?
- [ ] Published security advisories process?
- [ ] Responsible disclosure program?

### Data handling
- [ ] Data residency options (EU, US)?
- [ ] Encryption at rest?
- [ ] Encryption in transit?
- [ ] Data retention policy?
- [ ] Deletion on request (GDPR)?
- [ ] Backup security?

### Access controls
- [ ] Audit logs for their actions?
- [ ] Admin activity visible to you?
- [ ] Support access to your data?
- [ ] 2FA available for admin accounts?

### Financial stability
- [ ] Funded, not going out of business next quarter?
- [ ] Data export available if you leave?

---

## Webhook Replay Protection

### Timestamp Validation

```typescript
const eventTimestamp = parseInt(event.created_at);
const now = Date.now() / 1000;
const TOLERANCE_SECONDS = 300; // 5 min

if (Math.abs(now - eventTimestamp) > TOLERANCE_SECONDS) {
  return reject("Event timestamp outside tolerance");
}
```

### Event ID Deduplication

```typescript
const result = await db.insert(webhookEvents).values({
  provider: "stripe",
  eventId: event.id,
  eventType: event.type,
  payload: event,
}).onConflictDoNothing().returning();

if (result.length === 0) {
  // Duplicate event; already processed
  return { received: true, duplicate: true };
}
```

---

## Third-Party API Key in Client Bundle

Publishable keys (Stripe pk_*, Supabase anon, PostHog write-only) are safe to
expose client-side. Secret keys (sk_*, service_role, API keys with write access)
are NOT.

### Audit

```bash
# Find all NEXT_PUBLIC_* env vars
rg -n 'NEXT_PUBLIC_' --type ts

# Verify each is a publishable/anon/public key type, not a secret
```

Build output inspection:
```bash
# Build the app
pnpm build

# Search the client bundle for secret patterns
grep -r "sk_live_" .next/
grep -r "whsec_" .next/
grep -r "eyJ" .next/  # JWTs that look like service role keys

# Should return zero matches
```

---

## Third-Party Cleanup on User Deletion

When a user is deleted, you must delete their data from every third-party service:

```typescript
async function deleteUser(userId: string) {
  const user = await getUser(userId);

  // Database
  await db.delete(users).where(eq(users.id, userId));

  // Third parties
  await stripe.customers.del(user.stripeCustomerId);
  await paypal.deleteCustomer(user.paypalPayerId);
  await sendgrid.deleteContact(user.email);
  await posthog.deletePerson(user.posthogDistinctId);
  await intercom.deleteContact(user.intercomId);
  await slack.deleteUserFromChannel(user.slackId);

  // External storage
  await s3.deleteObjects({ Prefix: `users/${userId}/` });

  // Analytics (pseudo-anonymized)
  await amplitude.deleteUser(user.amplitudeUserId);

  // Audit log (keep, but mark actor as deleted)
  await db.update(auditLog)
    .set({ actor_email: `[deleted-${userId}]@example.com` })
    .where(eq(auditLog.actor_id, userId));
}
```

Each line is a potential failure point. Retry logic + idempotency required.

---

## Audit Checklist

- [ ] Every inbound webhook verifies signature before any action
- [ ] Every OAuth integration uses exact redirect URI matching
- [ ] Every OAuth integration uses state parameter (crypto random + server-stored)
- [ ] Every OAuth integration uses PKCE where applicable
- [ ] Token storage: access in memory, refresh encrypted, ID tokens not stored
- [ ] OAuth error bodies treated as untrusted (no logging raw body)
- [ ] Credential rotation schedule documented per provider
- [ ] Rotation without downtime process tested
- [ ] Dependency scanning in CI
- [ ] Lock files committed and `npm ci` in CI
- [ ] `postinstall` scripts disabled globally, enabled per-package
- [ ] Vendor assessment done before new integration
- [ ] Webhook timestamp validation
- [ ] Webhook event ID deduplication
- [ ] Client bundle scanned for secret leaks in build output
- [ ] User deletion cascades to third-party services
- [ ] Audit logs include third-party sync events
