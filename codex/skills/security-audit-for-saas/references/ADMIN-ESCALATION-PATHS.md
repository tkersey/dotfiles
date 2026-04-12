# Admin Escalation Paths

This file catalogs every way a lower-privilege user can become a higher-
privilege user in a SaaS application. These paths are the most valuable
targets for attackers and the most common source of CRITICAL findings.

---

## The Privilege Ladder

Standard SaaS RBAC ladder (from lowest to highest):

```
Anonymous
    ↓
Free user
    ↓
Paid user / Subscriber
    ↓
Team member
    ↓
Team admin
    ↓
Team owner
    ↓
Platform admin
    ↓
Super admin / Service role
```

Each step up is an escalation. Each should require explicit authorization.

---

## The 25 Escalation Patterns

### Pattern 1: Role Auto-Promotion on Whitelist Match
**Attack:** Email in admin whitelist → auto-set `isAdmin = true`
**Defense:** Never auto-promote. Whitelist gates login, not role.
**Reference:** [KERNEL.md](KERNEL.md) Axiom 4

### Pattern 2: TOCTOU in Role Change
**Attack:** Permission check outside transaction; role changes between check and action
**Defense:** Move check inside transaction with row lock
**Reference:** [AUTH.md](AUTH.md), [ATTACK-SCENARIOS.md](ATTACK-SCENARIOS.md) B1

### Pattern 3: Self-Promotion via API
**Attack:** `PATCH /api/users/me { role: "admin" }` — mass assignment
**Defense:** Explicit column allowlist; never allow role in user update endpoints
**Reference:** [API-SECURITY.md](API-SECURITY.md), [BUSINESS-LOGIC-FLAWS.md](BUSINESS-LOGIC-FLAWS.md) BL-30

### Pattern 4: Invite Link Role Injection
**Attack:** Invite URL includes `?role=admin`; handler trusts query param
**Defense:** Role stored server-side in invitation record; URL only references invitation ID

### Pattern 5: SSO Auto-Provisioning with Default Admin Role
**Attack:** New SSO users default to admin instead of member
**Defense:** Default to minimum role; admin grants require explicit action

### Pattern 6: Race in Invitation Acceptance
**Attack:** Accept invitation N times concurrently; each adds role
**Defense:** Unique constraint on (user_id, org_id); idempotent accept

### Pattern 7: Support Impersonation Without Audit
**Attack:** Support team has "log in as user" with no audit trail
**Defense:** See [IMPERSONATION.md](IMPERSONATION.md)

### Pattern 8: Session Persistence After Role Removal
**Attack:** Role revoked, but old sessions still have admin claims (JWT)
**Defense:** Short-lived JWT + revocation list; OR session generation counter

### Pattern 9: RBAC Cache Staleness
**Attack:** Role cached for 5 minutes; revoked but still accepted
**Defense:** Cache invalidation on role change; OR no cache for privileged checks

### Pattern 10: Owner Leave Race
**Attack:** Owner tries to leave org; check passes but then role transfers unexpectedly
**Defense:** Owner cannot leave without transferring ownership first

### Pattern 11: Billing Owner vs Team Owner Confusion
**Attack:** Different roles for billing and team management; escalation via one grants the other
**Defense:** Separate permission matrix; explicit grants per capability

### Pattern 12: Email Change Bypasses Admin Check
**Attack:** User changes email to admin's address; re-auth grants admin via whitelist
**Defense:** Email changes require verification AND don't trigger role re-evaluation

### Pattern 13: Device Code Verification Without User Check
**Attack:** Attacker enters device code; authentication completes without verifying user initiated
**Defense:** Verify user actually started the device code flow
**Reference:** [CLI-AUTH.md](CLI-AUTH.md)

### Pattern 14: API Key Scoping Error
**Attack:** User API key with `read:users` scope can also `write:admin` due to scope check bug
**Defense:** Scope checks use explicit allowlist; default deny

### Pattern 15: Service Role Key Exposure
**Attack:** Service role key leaks to client code; client bypasses RLS
**Defense:** Service role key only in server code; never in `NEXT_PUBLIC_*`

### Pattern 16: Migration Script Creates Admin
**Attack:** DB migration inserts admin user; migration runs in production
**Defense:** Migrations go through code review; no test data in production migrations

### Pattern 17: Support Tool Has More Power Than Customer UI
**Attack:** Internal support tool can do things the admin UI can't (e.g., read payment details)
**Defense:** Principle of least privilege for internal tools; audit their capabilities

### Pattern 18: Credential Reset Bypasses MFA
**Attack:** Password reset flow doesn't require MFA; attacker resets via email access
**Defense:** Password reset requires current MFA OR account lockout with manual recovery

### Pattern 19: OAuth Grant Escalation
**Attack:** OAuth provider returns additional scopes not requested
**Defense:** Validate actual scopes match requested; reject extras

### Pattern 20: Webhook-Driven Role Change
**Attack:** Webhook handler updates user role based on provider event; provider is attacker-controlled
**Defense:** Role changes never triggered by external webhooks; or verify identity chain

### Pattern 21: Org Transfer Without New Owner Consent
**Attack:** Owner initiates transfer to another user without their consent; auto-accepted
**Defense:** Explicit accept required; confirmation email

### Pattern 22: SCIM Provisioning Race
**Attack:** SCIM creates user with admin role; race between create and role assignment allows bypass
**Defense:** Atomic user creation with role; or default role then explicit upgrade

### Pattern 23: Break-Glass Account Abuse
**Attack:** Emergency admin account used for routine work; credentials get phished
**Defense:** Break-glass accounts audited monthly; only used in actual emergencies

### Pattern 24: Nested Impersonation
**Attack:** Admin impersonates user who impersonates another user; escalation chain
**Defense:** Block nested impersonation; only real admins can impersonate

### Pattern 25: Role Change via Unused Legacy Endpoint
**Attack:** Old API version (`/api/v1`) has role change endpoint without modern auth
**Defense:** Audit all API versions; remove or patch legacy

---

## The Escalation Audit Methodology

### Step 1: Map the RBAC hierarchy
List every role and its explicit permissions. Use permission matrix.

### Step 2: Find every role change endpoint
```bash
grep -rn 'role.*=\|role:\|updateRole\|setRole\|promoteUser' src/
```

### Step 3: For each endpoint, trace:
- Who can call it?
- What's the input validation?
- Is there a transaction?
- Is the check inside or outside the transaction?
- Is there an audit log?
- Can the caller modify their own role?
- Can the caller target a higher role than theirs?

### Step 4: Check the full auth chain
For each role-touching endpoint:
- Does it re-verify the caller's role (not just a cached flag)?
- Does it validate the target exists and is valid?
- Does it check for self-action (can they modify themselves)?
- Does it check for higher-target (can they modify above their level)?

### Step 5: Check indirect paths
Role changes might happen via:
- Invitations
- SSO provisioning
- SCIM
- Batch imports
- Admin UIs
- CLI tools
- Webhooks
- Reconciliation crons
- Migration scripts

Each is a potential bypass.

### Step 6: Audit the audit logs
For each role change, verify:
- Audit log written atomically with change
- Log includes actor, target, before/after role, reason
- Log is immutable
- Log is queryable for forensics

---

## The Minimum Guardrails

Every SaaS should have:

### 1. Explicit RBAC model
Roles and permissions defined as code, not scattered if/else.

### 2. Transaction-bound authorization
All role changes in transactions; auth check re-read from DB in the transaction.

### 3. Self-action protection
Can't change your own role (to any direction).

### 4. Hierarchy enforcement
Can't promote above your level. Can't demote someone at or above your level.

### 5. Audit everything
Every role change logged with actor + target + reason.

### 6. Two-person rule for sensitive changes
Promoting to admin/owner requires another admin's confirmation.

### 7. Alerting on escalations
Slack alert when any role is promoted.

### 8. Quarterly access review
List all admin/owner users; confirm each still needs access.

---

## Access Review Checklist

Every quarter, for every admin-level account:
- [ ] Is this person still employed?
- [ ] Do they still need admin access?
- [ ] Did they log in in the last 30 days?
- [ ] Are their permissions still appropriate?
- [ ] Do they have MFA enabled?
- [ ] When was their password last changed?
- [ ] Any unusual activity in audit log?

Downgrade or remove anyone who doesn't pass.

---

## Break-Glass Procedures

For emergencies when normal auth is broken:

### The break-glass account
- Separate from regular admin accounts
- Physical credentials (hardware key)
- Stored in a safe, in an envelope
- Monitored 24/7
- Password/key rotated annually (or on use)

### Using break-glass
1. Document the reason
2. Get approval from multiple parties
3. Open sealed envelope, use credentials
4. Complete emergency task
5. Rotate credentials
6. Post-mortem within 48 hours
7. Restore normal auth

Don't use break-glass for routine work.

---

## The Escalation Decision Tree

```
Finding: Role change vulnerability
         ↓
Can it be triggered by anonymous users? → CRITICAL (immediate fix)
         ↓ No
Can it be triggered by free users? → CRITICAL (fix within 24 hours)
         ↓ No
Can it be triggered by paid users? → HIGH (fix this week)
         ↓ No
Can it be triggered by team members? → HIGH (fix this sprint)
         ↓ No
Can it be triggered by admins only? → MEDIUM (fix in backlog)
         ↓ No
Only via internal tools? → LOW (document)
```

---

## See Also

- [AUTH.md](AUTH.md)
- [KERNEL.md](KERNEL.md) — Axioms 1, 4
- [BUSINESS-LOGIC-FLAWS.md](BUSINESS-LOGIC-FLAWS.md)
- [ATTACK-SCENARIOS.md](ATTACK-SCENARIOS.md)
- [IMPERSONATION.md](IMPERSONATION.md)
- [subagents/admin-escalation-mapper.md](../subagents/admin-escalation-mapper.md)
