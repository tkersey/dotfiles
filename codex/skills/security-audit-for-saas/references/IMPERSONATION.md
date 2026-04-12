# Admin Impersonation Security

Admin impersonation ("log in as user X") is a common SaaS feature for support.
It's also one of the highest-risk features. A broken impersonation implementation
gives the support team (and whoever compromises them) the keys to the kingdom.

---

## Why Impersonation Is Hard

### The requirements
1. Support agents can see what a user sees (debug their issues)
2. Actions taken during impersonation must be attributed to the agent
3. Users must know (or have the option to know) they were impersonated
4. Compromised agent accounts shouldn't cascade to all users
5. Impersonation sessions must be time-limited
6. All impersonation events must be auditable

### The failures
- Agent can impersonate without logging
- Impersonated user gets billing emails for the agent's actions
- Agent keeps impersonation session indefinitely
- Another user can "resume" an agent's impersonation session
- Agent can impersonate the CEO and read financial reports
- Impersonation bypasses MFA / rate limits

---

## The Production Pattern

### Three Cookies + Audit Trail

```typescript
// Cookies set during impersonation
const IMPERSONATION_COOKIES = {
  targetUserId: 'impersonate_user_id',       // Who we're impersonating
  expiresAt: 'impersonate_expires',          // 30 min TTL
  impersonatorId: 'impersonator_id',         // Who the real user is
};
```

### Start Impersonation
```typescript
// POST /api/admin/impersonation/start
export async function POST(req: Request) {
  const session = await requireAdminSession(req);
  const { targetUserId, justification } = await req.json();

  // Validations
  if (!targetUserId || typeof targetUserId !== 'string') {
    return error('Invalid target', 400);
  }
  if (targetUserId === session.userId) {
    return error('Cannot impersonate self', 400);
  }
  if (!justification || justification.length < 10) {
    return error('Justification required (10+ chars)', 400);
  }

  // Verify target exists
  const target = await db.query.users.findFirst({ where: eq(users.id, targetUserId) });
  if (!target) return error('Target not found', 404);

  // Check if admin has permission to impersonate THIS target
  // (some orgs have customers they can't impersonate, e.g., other admins)
  if (!canImpersonate(session, target)) {
    return error('Forbidden', 403);
  }

  // Create audit log entry BEFORE setting cookies
  const auditEntry = await db.insert(impersonationAudit).values({
    impersonatorId: session.userId,
    targetUserId,
    startedAt: new Date(),
    justification,
    ipAddress: getClientIp(req),
    userAgent: req.headers.get('user-agent'),
    expiresAt: new Date(Date.now() + 30 * 60 * 1000),
  }).returning();

  // Set cookies
  const response = NextResponse.redirect('/');
  response.cookies.set(IMPERSONATION_COOKIES.targetUserId, targetUserId, {
    httpOnly: true,
    secure: true,
    sameSite: 'strict',
    maxAge: 30 * 60,
  });
  response.cookies.set(IMPERSONATION_COOKIES.expiresAt, String(Date.now() + 30 * 60 * 1000), {
    httpOnly: true,
    secure: true,
    sameSite: 'strict',
    maxAge: 30 * 60,
  });
  response.cookies.set(IMPERSONATION_COOKIES.impersonatorId, session.userId, {
    httpOnly: true,
    secure: true,
    sameSite: 'strict',
    maxAge: 30 * 60,
  });

  // Notify the target user (email or in-app notification)
  await notifyUserOfImpersonation({
    userId: targetUserId,
    impersonatorEmail: session.email,
    justification,
  });

  return response;
}
```

### Resolve Impersonated Identity on Every Request
```typescript
// In auth middleware
async function authenticateRequest(req: Request): Promise<AuthenticatedUser> {
  const session = await getSession(req);
  if (!session) return null;

  // Check for impersonation cookies
  const impersonatedUserId = req.cookies.get(IMPERSONATION_COOKIES.targetUserId)?.value;
  const impersonatorId = req.cookies.get(IMPERSONATION_COOKIES.impersonatorId)?.value;
  const expiresAt = req.cookies.get(IMPERSONATION_COOKIES.expiresAt)?.value;

  if (!impersonatedUserId || !impersonatorId || !expiresAt) {
    // No impersonation — return real user
    return { ...session, isImpersonating: false };
  }

  // Validate impersonation
  const resolved = resolveImpersonation({
    sessionUserId: session.userId,
    impersonatedUserId,
    impersonatorId,
    expiresAt: parseInt(expiresAt),
  });

  if (!resolved.ok) {
    // Rejection: drop cookies silently, proceed as real user
    logger.warn({
      sessionUserId: session.userId,
      impersonatedUserId,
      impersonatorId,
      reason: resolved.reason,
    }, 'auth:impersonation:rejected');
    return { ...session, isImpersonating: false };
  }

  const impersonatedUser = await db.query.users.findFirst({
    where: eq(users.id, impersonatedUserId),
  });
  if (!impersonatedUser) {
    return { ...session, isImpersonating: false };
  }

  return {
    ...impersonatedUser,
    isImpersonating: true,
    realUserId: impersonatorId,
    impersonatorEmail: session.email,
  };
}

// Pure function for testability
function resolveImpersonation(params: {
  sessionUserId: string;
  impersonatedUserId: string;
  impersonatorId: string;
  expiresAt: number;
}): { ok: true } | { ok: false; reason: string } {
  // CRITICAL: impersonator_id cookie must match session user
  // Prevents attacker with just cookies from impersonating
  if (params.impersonatorId !== params.sessionUserId) {
    return { ok: false, reason: 'impersonator_session_mismatch' };
  }

  // CRITICAL: prevent self-impersonation (catches some bugs)
  if (params.impersonatedUserId === params.impersonatorId) {
    return { ok: false, reason: 'self_impersonation' };
  }

  // Check expiry
  if (Date.now() > params.expiresAt) {
    return { ok: false, reason: 'expired' };
  }

  return { ok: true };
}
```

### End Impersonation
```typescript
// POST /api/admin/impersonation/end
export async function POST(req: Request) {
  const session = await requireAdminSession(req);

  // Log the end
  await db.update(impersonationAudit)
    .set({ endedAt: new Date() })
    .where(and(
      eq(impersonationAudit.impersonatorId, session.userId),
      isNull(impersonationAudit.endedAt)
    ));

  // Clear cookies
  const response = NextResponse.redirect('/admin');
  response.cookies.delete(IMPERSONATION_COOKIES.targetUserId);
  response.cookies.delete(IMPERSONATION_COOKIES.expiresAt);
  response.cookies.delete(IMPERSONATION_COOKIES.impersonatorId);

  return response;
}
```

---

## UI Indicators

### The Agent's View
When impersonating, the agent MUST see a persistent visual indicator:

```tsx
function ImpersonationBanner({ user }: { user: AuthenticatedUser }) {
  if (!user.isImpersonating) return null;

  return (
    <div className="bg-red-600 text-white py-2 px-4 text-center font-bold sticky top-0 z-50">
      🎭 You are impersonating {user.email} — Actions are logged as you
      <form action="/api/admin/impersonation/end" method="POST">
        <button className="underline ml-4">End impersonation</button>
      </form>
    </div>
  );
}
```

### The User's Notification
After impersonation ends, email the user:
```
Subject: Your account was accessed by support

Hi {user.name},

Our support team viewed your account on {date} to help with {justification}.
Actions taken: {summary}.

If you didn't request this, please contact us immediately at security@example.com.
```

---

## Action Attribution

### The Audit Problem
If an agent impersonates a user and performs an action, who "did" it?

**Correct answer:** Both. The audit log must record both the impersonated user
(as the nominal actor) and the real user (as the responsible party).

```typescript
async function logAction(action: string, resource: string, user: AuthenticatedUser) {
  await db.insert(auditLog).values({
    actor_id: user.id,  // The impersonated user (who the action affected)
    real_actor_id: user.realUserId ?? user.id,  // The real agent (for responsibility)
    is_impersonated: user.isImpersonating,
    action,
    resource,
    timestamp: new Date(),
  });
}
```

### Forbidden Actions During Impersonation
Some actions should NEVER happen during impersonation:
- Password changes (they're changing someone else's password)
- Payment method changes (billing risk)
- Delete account (devastating if malicious)
- Enable/disable 2FA (they're modifying user's security)
- Export all data (data theft path)

```typescript
function canPerformAction(action: string, user: AuthenticatedUser): boolean {
  if (user.isImpersonating) {
    const FORBIDDEN_WHILE_IMPERSONATING = [
      'password.change',
      'payment_method.add',
      'payment_method.remove',
      'account.delete',
      'mfa.enable',
      'mfa.disable',
      'export.all_data',
    ];
    if (FORBIDDEN_WHILE_IMPERSONATING.includes(action)) return false;
  }
  return true;
}
```

---

## Read-Only Mode

### The Pattern
Default impersonation to read-only. Require explicit "write mode" for
mutations.

```typescript
// Two impersonation modes
type ImpersonationMode = 'read_only' | 'full';

// Cookie stores mode
response.cookies.set('impersonate_mode', mode, { /* ... */ });

// Middleware enforces
function canMutate(user: AuthenticatedUser): boolean {
  if (!user.isImpersonating) return true;
  return user.impersonationMode === 'full';
}
```

Read-only mode covers 90% of support use cases (viewing user's account to
debug). Write mode requires justification and is more heavily audited.

---

## Rate Limiting

### Per-Agent Limits
One agent shouldn't impersonate 1000 users in a day.

```typescript
const IMPERSONATION_LIMITS = {
  perAgentPerDay: 20,     // Max distinct users impersonated per day
  perAgentPerHour: 5,     // Max distinct users per hour
  concurrent: 1,          // Only one active impersonation at a time
};
```

### Alert Rules
- Agent impersonates >5 users in 1 hour → Slack alert
- Agent impersonates admin/owner → alert security team
- Agent impersonates outside business hours → alert
- Agent impersonates the same user multiple times in short succession → alert

---

## Prevention of Common Mistakes

### Mistake 1: Impersonator cookie not bound to session
```typescript
// BAD: trusts impersonator_id cookie without verification
const impersonatorId = cookies.get('impersonator_id');

// GOOD: verify it matches current session user
if (impersonatorId !== session.userId) return null;
```

### Mistake 2: No expiry
```typescript
// BAD: cookies don't expire
response.cookies.set('impersonate_user_id', targetUserId);

// GOOD: explicit expiry
response.cookies.set('impersonate_user_id', targetUserId, {
  maxAge: 30 * 60,
});
```

### Mistake 3: Audit as fire-and-forget that can silently fail
```typescript
// BAD: if audit fails, impersonation proceeds anyway with no record
db.insert(auditLog).values({ /* ... */ }).catch(() => {});
proceed();

// GOOD: audit entry creation is part of the transaction
// BUT: don't block admin access if audit DB is down (see Story 2 in FIELD-GUIDE.md)
```

### Mistake 4: No user notification
Users should know they were impersonated. This is both a legal requirement (in
some jurisdictions) and a detection mechanism (users can report unauthorized
access).

### Mistake 5: No mode indicator in UI
Without a visual indicator, an agent can forget they're impersonating and
treat their actions as their own. Makes the audit trail confusing.

### Mistake 6: Impersonation bypasses MFA
Target user has MFA enabled → impersonation bypasses it. Correct: impersonation
is an admin action that should require the admin's MFA, not the user's.

---

## Audit Query Templates

### "Show all impersonation for a user in the last 30 days"
```sql
SELECT
  ia.impersonator_id,
  u.email as impersonator_email,
  ia.started_at,
  ia.ended_at,
  ia.justification,
  ia.ip_address
FROM impersonation_audit ia
JOIN users u ON u.id = ia.impersonator_id
WHERE ia.target_user_id = $user_id
  AND ia.started_at > now() - interval '30 days'
ORDER BY ia.started_at DESC;
```

### "Show agents with unusual impersonation activity"
```sql
SELECT
  impersonator_id,
  COUNT(DISTINCT target_user_id) as unique_targets,
  COUNT(*) as total_sessions,
  MIN(started_at) as first_activity,
  MAX(started_at) as last_activity
FROM impersonation_audit
WHERE started_at > now() - interval '24 hours'
GROUP BY impersonator_id
HAVING COUNT(DISTINCT target_user_id) > 5
ORDER BY unique_targets DESC;
```

### "All admin actions taken during impersonation"
```sql
SELECT
  al.*,
  ia.impersonator_id,
  ia.target_user_id,
  ia.justification
FROM audit_log al
JOIN impersonation_audit ia ON ia.impersonator_id = al.real_actor_id
  AND al.actor_id = ia.target_user_id
  AND al.created_at BETWEEN ia.started_at AND COALESCE(ia.ended_at, now())
WHERE al.action LIKE 'admin_%'
ORDER BY al.created_at DESC;
```

---

## Audit Checklist

- [ ] Impersonation requires admin role AND justification
- [ ] Impersonator cookie is bound to session user
- [ ] Session expires automatically (30 min max)
- [ ] Visible banner during impersonation
- [ ] User notified of impersonation
- [ ] Audit log: impersonator, target, timestamp, justification
- [ ] Forbidden actions list (password, payments, delete, MFA)
- [ ] Rate limiting per agent
- [ ] Alerts on unusual patterns
- [ ] Cannot impersonate self
- [ ] Cannot impersonate other admins (optional but recommended)
- [ ] Read-only mode as default
- [ ] All actions during impersonation attribute both actors

---

## See Also

- [ADMIN-ESCALATION-PATHS.md](ADMIN-ESCALATION-PATHS.md)
- [AUDIT-LOGGING.md](AUDIT-LOGGING.md)
- [FIELD-GUIDE.md](FIELD-GUIDE.md) — Story 2 (degraded monitoring)
- [ATTACK-SCENARIOS.md](ATTACK-SCENARIOS.md) — admin compromise scenarios
