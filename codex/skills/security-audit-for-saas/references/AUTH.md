# Auth & Authorization Security Checklist

Deep checklist for auditing SaaS authentication and authorization. Every item from real vulnerabilities.

---

## TOCTOU in Permission Checks

The most common auth vulnerability found: permission checks outside database transactions.

### Pattern (Vulnerable)
```typescript
// CHECK (outside transaction)
const member = await getOrgMember(orgId, userId);
if (member.role !== 'owner') throw new Error('Forbidden');

// USE (inside transaction, but check is stale)
await db.transaction(async (tx) => {
  await tx.update(organizations).set({ billingEmail }).where(eq(id, orgId));
});
```

### Pattern (Fixed)
```typescript
await db.transaction(async (tx) => {
  // CHECK (inside transaction with lock)
  const [member] = await tx.select().from(organization_members)
    .where(and(eq(orgId, orgId), eq(userId, userId)))
    .for('update');
  if (member.role !== 'owner') throw new Error('Forbidden');

  // USE (same transaction, check is fresh)
  await tx.update(organizations).set({ billingEmail }).where(eq(id, orgId));
});
```

### Known TOCTOU Locations (audit these patterns)
1. Admin invite creation -- auth check outside insert transaction
2. Billing email change -- owner check outside update transaction
3. Member role change -- actor permission not re-verified before role change
4. Member removal -- admin can be demoted between check and delete
5. Owner leave -- ownership could change between check and delete

---

## RBAC Hierarchy

### Billing Operations = Owner Only
Never `admin`. Billing endpoints are the highest-value RBAC target.

```typescript
// WRONG - admin can manipulate billing
requireOrgPermission('manage_billing', 'admin');

// RIGHT - only owner manages billing
requireOrgPermission('manage_billing', 'owner');
```

**Audit:** Every route under `/api/*/billing`, `/api/*/checkout`, `/api/*/subscription`.

### Full Route Audit Checklist
Map every API route to its required auth middleware:

| Route Pattern | Required Auth |
|---------------|---------------|
| `/api/admin/*` | `requireAdmin` |
| `/api/*/billing/*` | `requireOrgPermission('manage_billing')` with owner role |
| `/api/*/members/*` | `requireOrgPermission('manage_members')` |
| `/api/*/settings/*` | `requireOrgPermission('manage_settings')` |
| `/api/subscription/*` | `requireUser` + subscription checks |
| `/api/v1/*` (CLI) | API key auth (`jsm_*` prefix) |
| `/api/webhooks/*` | Signature verification (no session auth) |
| `/api/cron/*` | Cron secret verification |

---

## CSRF Protection

### Rules
- [ ] Origin/Referer header validation for state-changing requests
- [ ] Webhook endpoints explicitly exempted (they use signature verification)
- [ ] API key requests skip CSRF (they don't use session cookies)
- [ ] **Never fall back to session auth when Authorization header is present** -- this prevents CSRF bypass by sending a fake bearer token

### Proxy-Level CSRF
- [ ] CSRF skip condition is narrow: only for verified token prefixes (e.g., `jsm_`), not for any JWT-shaped string
- [ ] Route-layer auth independently validates CSRF as defense-in-depth

---

## Rate Limiting on Auth Endpoints

Every auth endpoint needs independent rate limiting BEFORE expensive operations:

| Endpoint | Required Limit | Why |
|----------|---------------|-----|
| Login/token exchange | 10/min per IP | Brute-force prevention |
| Token refresh | 30/min per token family | Refresh token abuse |
| Token revoke | 30/min per user | Enumeration prevention |
| Device code poll | 5/sec per device code | Polling abuse |
| Password reset | 5/hr per email | Email bombing |
| SSO initiation | 10/min per IP | Org enumeration |

**Return 200 on revoke regardless of token validity** (RFC 7009 -- prevents token enumeration).

---

## Timing-Safe Comparisons

ALL secret/token comparisons must use `crypto.timingSafeEqual()`:

- [ ] API key comparison
- [ ] HMAC signature verification
- [ ] OIDC state parameter validation
- [ ] SAML InResponseTo validation
- [ ] Webhook signature verification
- [ ] Admin API key comparison
- [ ] Bearer token hash comparison

```typescript
import { timingSafeEqual } from 'crypto';

function timingSafeCompare(a: string, b: string): boolean {
  const bufA = Buffer.from(a);
  const bufB = Buffer.from(b);
  if (bufA.length !== bufB.length) return false;
  return timingSafeEqual(bufA, bufB);
}
```

**Never use `===` or `!==` for secret comparison.**

---

## SSO / OIDC / SAML

SSO is one of the highest-risk areas because it involves multiple external redirects.

### OIDC
- [ ] State parameter: cryptographically random, timing-safe comparison
- [ ] Nonce: stored server-side, verified on callback
- [ ] Redirect URI: exact match, not prefix match
- [ ] Token endpoint: uses client_secret_post (not in URL)
- [ ] ID token: validated signature, issuer, audience, expiry

### SAML
- [ ] InResponseTo: timing-safe comparison
- [ ] Assertion signed, not just response envelope
- [ ] XML signature wrapping attacks prevented
- [ ] Destination validation matches expected ACS URL

### General SSO
- [ ] Redirect URLs validated at every stage (entry, callback, provisioning)
- [ ] Seat limit enforcement during auto-provisioning
- [ ] SSO configs in API responses use redacted types (no client secrets)
- [ ] Config shows fingerprint, not full secret
- [ ] Org slug sanitized for injection/enumeration prevention

---

## Token Lifecycle

### CLI Tokens (`jsm_*` prefix)
- [ ] `expiresAt` checked on every use
- [ ] Hash stored in DB (not raw token)
- [ ] Last-used tracking debounces updates (1 hour)
- [ ] Revocation is immediate

### Session Tokens
- [ ] 32 bytes (256 bits) cryptographically secure random
- [ ] Token family-based replay detection for refresh tokens
- [ ] Tamper detection via user agent hash
- [ ] Session limit enforcement (e.g., max 10 active)
- [ ] Refresh token rotation: handle compromise detection without locking out legitimate users

### Device Code Flow
- [ ] Codes are ephemeral (15 min TTL)
- [ ] Cryptographically secure random (32 bytes)
- [ ] Verify user actually initiated the device code request
- [ ] Rate limit polling endpoint

---

## Admin Access

- [ ] Multi-factor: email whitelist + admin flag + (optionally) ADMIN_API_KEY
- [ ] Admin role expiry checking
- [ ] No single point of failure (more than 2 admin emails)
- [ ] Break-glass procedure documented
- [ ] Admin actions logged with actor identity
- [ ] Admin client uses service role key with cookies disabled
