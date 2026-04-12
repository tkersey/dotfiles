# SCIM Provisioning Security

SCIM (System for Cross-domain Identity Management) is how enterprises expect
to provision users into your SaaS. It's also a major attack surface: SCIM
endpoints typically have long-lived tokens, high privileges, and minimal
user-facing oversight.

---

## The SCIM Trust Model

When a customer enables SCIM:
1. They configure your SCIM endpoint URL in their IdP (Okta, Azure AD, etc.)
2. You provide them a bearer token
3. Their IdP makes API calls to create/update/delete users in your system
4. Your system trusts the IdP's assertions about who exists and what roles

The SCIM token is essentially a key to the entire tenant.

---

## The Top SCIM Risks

### 1. SCIM token exposure
Token is long-lived, high-privilege, often stored in IdP config (visible to
IdP admins). Leakage = full tenant compromise.

**Defense:**
- Token rotation support
- Token scoped to single tenant
- Token usage audited
- Detect anomalous provisioning patterns

### 2. Mass provisioning flood
Attacker with token provisions 10M users to exhaust your DB.

**Defense:**
- Hard cap on users per tenant
- Rate limit on SCIM endpoints
- Alert on sudden user creation spikes

### 3. Role injection via SCIM
```json
POST /scim/v2/Users
{
  "userName": "attacker@evil.com",
  "roles": [{"value": "admin"}]
}
```

If your SCIM handler blindly assigns roles from the request, attacker creates
admin users at will.

**Defense:**
- Role is never set via SCIM create; always default role
- Role changes require separate admin action
- Or: role field ignored; roles come from group membership

### 4. SCIM email spoofing
Attacker SCIM-creates a user with `userName: victim@company.com`. Your system
trusts this and lets them log in as the victim.

**Defense:**
- SCIM-created users have a `provisioned: true` flag
- Email ownership verified separately (not trusted from SCIM)
- SSO login required for SCIM-provisioned users

### 5. Cross-tenant SCIM via shared endpoint
Your SCIM endpoint is `/scim/v2/Users` (not per-tenant). Auth determines
tenant from token. Token leak = cross-tenant creation.

**Defense:**
- Per-tenant endpoints: `/scim/v2/{tenantId}/Users`
- OR: Token embeds tenant ID, validated server-side
- Never let request body override tenant

### 6. SCIM replay attacks
SCIM requests don't have nonces. If logged/captured, they can be replayed.

**Defense:**
- Idempotency keys on PATCH/POST
- Log all SCIM operations for anomaly detection

### 7. Group membership escalation
SCIM groups often control permissions. Attacker modifies group membership:
```json
PATCH /scim/v2/Groups/admins
{
  "Operations": [{
    "op": "add",
    "path": "members",
    "value": [{"value": "attacker-user-id"}]
  }]
}
```

**Defense:**
- Verify group changes against expected patterns
- Audit log on every membership change
- Alert on admin group changes

### 8. Deprovisioning failure
IdP removes user, SCIM DELETE is called, but your handler fails silently.
User stays active.

**Defense:**
- DELETE operations must be atomic and confirmed
- Retry with exponential backoff
- Reconciliation cron: compare IdP state to local state
- Alert on deprovisioning failures

### 9. Partial updates during provisioning
SCIM PATCH can update arbitrary fields. Attacker updates billing info via
SCIM.

**Defense:**
- Allowlist of SCIM-updatable fields
- Sensitive fields (billing, role, plan) not SCIM-updatable
- Explicit rejection of unknown fields

### 10. SCIM schema confusion
Different IdPs send slightly different SCIM payloads. Your parser may
interpret them differently.

**Defense:**
- Strict schema validation
- Reject unknown extensions
- Test against multiple IdPs

---

## SCIM Authentication Patterns

### Bearer token (most common)
```http
GET /scim/v2/Users
Authorization: Bearer scim_xxx
```

Token stored in IdP config. Simple but high risk.

### OAuth 2.0 (preferred)
Short-lived access tokens from OAuth flow. Rotated automatically.

### Mutual TLS
Certificate-based auth. Hard to configure but very secure.

---

## SCIM Implementation Checklist

### Endpoint setup
- [ ] Per-tenant endpoints (not shared)
- [ ] HTTPS only, HTTP redirects rejected
- [ ] Token scoped to tenant + scope
- [ ] Token rotation supported
- [ ] Old tokens revocable immediately

### Request validation
- [ ] Schema validation on every request
- [ ] Allowlist of writable fields
- [ ] Role field never writable via SCIM
- [ ] Billing fields never writable via SCIM
- [ ] Unknown fields rejected (not ignored)

### Rate limiting
- [ ] Per-tenant rate limit
- [ ] Hard cap on users per tenant
- [ ] Alert on mass operations
- [ ] Backoff on burst traffic

### User lifecycle
- [ ] Default role on creation (minimum privilege)
- [ ] `provisioned: true` flag on SCIM-created users
- [ ] Email ownership verified separately
- [ ] SSO login enforced for SCIM users
- [ ] DELETE confirmed atomically

### Group management
- [ ] Admin group changes audited
- [ ] Alert on admin group membership changes
- [ ] Two-person rule for admin additions (optional)

### Audit logging
- [ ] Every SCIM operation logged
- [ ] Logs include actor (IdP source IP), operation, target
- [ ] Logs immutable, queryable
- [ ] Alert on anomalies (mass ops, admin changes)

### Reconciliation
- [ ] Periodic reconciliation cron
- [ ] Compare IdP state to local state
- [ ] Alert on drift
- [ ] Automatic cleanup of orphaned users

### Error handling
- [ ] Errors don't leak tenant info
- [ ] 404 for not found (not 403)
- [ ] Consistent error format (SCIM spec)

---

## SCIM Response Codes

| Code | Meaning | Notes |
|------|---------|-------|
| 200 | Success | GET/PUT success |
| 201 | Created | POST success |
| 204 | No content | DELETE success |
| 400 | Bad request | Schema error |
| 401 | Unauthorized | Invalid token |
| 403 | Forbidden | Valid token, insufficient scope |
| 404 | Not found | Resource doesn't exist |
| 409 | Conflict | Duplicate (e.g., username exists) |
| 429 | Too many | Rate limited |

---

## The SCIM Threat Model

```
Attacker with SCIM token can:
├─ Create users (arbitrary count)
├─ Modify users (arbitrary fields unless allowlisted)
├─ Delete users (cause disruption)
├─ Modify groups (escalate privileges)
├─ Enumerate users (GET /Users)
└─ Exfiltrate user metadata

Mitigations:
├─ Hard caps prevent creation floods
├─ Field allowlists prevent escalation
├─ Soft delete prevents disruption
├─ Audit logs detect abuse
└─ Rate limits slow attackers
```

---

## SCIM Audit Scenarios

### Scenario 1: Malicious IdP admin
IdP admin at customer company creates SCIM user with admin role, then logs in
as that user.

**Detection:**
- Admin group membership changes via SCIM → alert
- Non-SSO login by SCIM-provisioned user → alert
- New user + immediate admin privilege + immediate login → alert

### Scenario 2: Token leak to third party
SCIM token accidentally committed to public GitHub.

**Detection:**
- Unusual source IP using SCIM token
- Geographic anomaly (token used from unexpected country)
- Time-of-day anomaly

### Scenario 3: IdP compromise
Attacker compromises customer's IdP and uses SCIM to persist access.

**Detection:**
- Mass user creation
- Cross-tenant correlation (same IP across multiple tenants)
- Requires customer-side security (IdP logs)

---

## SCIM Testing Strategy

### Unit tests
- Schema validation for each resource type
- Field allowlist enforcement
- Rate limit enforcement
- Authentication failure modes

### Integration tests
- Full provisioning cycle (create → update → delete)
- Multiple IdPs (Okta, Azure AD, OneLogin)
- Error recovery (partial failure, retry)

### Adversarial tests
- Try to create admin via SCIM (should fail)
- Try to change billing via SCIM (should fail)
- Try mass provisioning (should hit cap)
- Try to provision cross-tenant (should fail)
- Try to pass unknown fields (should reject)

---

## See Also

- [AUTH.md](AUTH.md)
- [MULTI-TENANT.md](MULTI-TENANT.md)
- [API-SECURITY.md](API-SECURITY.md)
- [ADMIN-ESCALATION-PATHS.md](ADMIN-ESCALATION-PATHS.md) — Pattern 22: SCIM race
- [AUDIT-LOGGING.md](AUDIT-LOGGING.md)
