# Session Management

Sessions tie authentication to authorization. A broken session is worse than no
session — it's an attacker with full access. This file covers the complete
session lifecycle: creation, validation, refresh, revocation, and cleanup.

---

## The Session Lifecycle

```
┌──────────┐
│  Login   │
└────┬─────┘
     ↓
┌──────────────────┐
│  Session created │  ← credentials verified
└────┬─────────────┘
     ↓
┌──────────────────┐
│  Token issued    │  ← cookie/JWT set
└────┬─────────────┘
     ↓
┌──────────────────┐
│  In use          │  ← every request validates
└────┬─────────────┘
     ↓
┌──────────────────┐
│  Refresh         │  ← extend without re-login
└────┬─────────────┘
     ↓
┌──────────────────┐
│  Revoke          │  ← logout, password change, admin action
└────┬─────────────┘
     ↓
┌──────────────────┐
│  Expired         │  ← cleaned up
└──────────────────┘
```

Each arrow is a potential security issue.

---

## Session Token Types

### Server-side session (classic)
Session ID in a cookie. Server has a session store (Redis, DB). Each request
looks up the session.

**Pros:** Easy to revoke (delete from store). Small cookie.
**Cons:** Stateful (not great for serverless). DB hit per request.

### JWT (stateless)
Signed token containing claims. Server verifies signature; no lookup needed.

**Pros:** Stateless. Fast. Works across services.
**Cons:** Can't revoke until expiry. Larger than cookie.

### Hybrid (recommended)
JWT for fast verification + session store for revocation list.

```typescript
async function validateSession(token: string): Promise<User | null> {
  // Fast: verify JWT signature and claims
  let payload: JWTPayload;
  try {
    payload = await jwt.verify(token, publicKey);
  } catch {
    return null;
  }

  // Check revocation list (short-lived cache + DB)
  const isRevoked = await checkRevocationList(payload.jti);
  if (isRevoked) return null;

  return getUserFromClaims(payload);
}
```

Revocation list only contains tokens that were explicitly revoked before
expiry. Entries can be cleaned up after their natural expiry time.

---

## Cookie Configuration

### The Correct Settings
```typescript
const SESSION_COOKIE_OPTIONS = {
  name: '__Host-session',  // __Host- prefix requires HTTPS + no Domain
  httpOnly: true,          // JS can't read it
  secure: true,            // Only over HTTPS
  sameSite: 'lax',         // CSRF protection; 'strict' blocks some legit flows
  path: '/',               // Required for __Host-
  maxAge: 24 * 60 * 60,    // 24 hours
};
```

### Cookie Name Prefixes

**`__Host-`**: Requires HTTPS, no Domain attribute, path must be `/`. Strongest
guarantees against cookie tossing.

**`__Secure-`**: Requires HTTPS, but allows Domain. Weaker.

**No prefix**: No guarantees.

Use `__Host-` unless you have a specific reason not to.

### SameSite Values

- **`strict`:** Cookie only sent for same-site requests. Blocks CSRF completely
  but breaks some legitimate flows (external links don't carry cookie).
- **`lax`:** Cookie sent for top-level navigation (GET) from other sites.
  Balance of security and usability.
- **`none`:** Cookie sent everywhere (requires `secure`). Use only if you
  need cross-site cookies (rare).

### The Supabase Quirk
Supabase auth cookies can't be `httpOnly: true` because the Supabase JS client
reads them from JavaScript for auth state management.

**This is a known security tradeoff.** Mitigations:
- Strong CSP to prevent XSS
- Short-lived tokens
- Refresh token rotation
- Careful error message handling (no eval-able content)

---

## Session Creation (Login)

### Constant-Time Login
```typescript
async function login(email: string, password: string): Promise<LoginResult> {
  // Always run bcrypt — prevent timing oracle for user existence
  const user = await db.query.users.findFirst({ where: eq(users.email, email.toLowerCase().trim()) });
  const hashToCheck = user?.passwordHash ?? DUMMY_BCRYPT_HASH;
  const passwordOk = await bcrypt.compare(password, hashToCheck);

  if (!user || !passwordOk) {
    // Generic error, normalized timing
    await normalizeTiming();
    return { error: 'Invalid email or password' };
  }

  // Check account state
  if (user.suspendedAt) {
    await normalizeTiming();
    return { error: 'Account suspended' }; // OR same generic error
  }

  if (!user.emailVerified) {
    return { error: 'Email not verified', action: 'resend_verification' };
  }

  // Create session
  const session = await createSession(user);
  return { session, user };
}
```

### Session Fixation Prevention
When a user logs in, issue a NEW session ID. Don't reuse a pre-login session ID.

```typescript
async function createSession(user: User, oldSessionId?: string): Promise<Session> {
  // Invalidate any pre-existing session (session fixation defense)
  if (oldSessionId) {
    await db.delete(sessions).where(eq(sessions.id, oldSessionId));
  }

  // Create new session with fresh ID
  const sessionId = crypto.randomBytes(32).toString('base64url');
  await db.insert(sessions).values({
    id: sessionId,
    userId: user.id,
    createdAt: new Date(),
    expiresAt: new Date(Date.now() + SESSION_TTL_MS),
    userAgent: req.headers.get('user-agent'),
    ipAddress: getClientIp(req),
  });

  return { id: sessionId, /* ... */ };
}
```

**Why this matters:** Session fixation attack is when an attacker obtains a
session ID (e.g., by setting it via query param), tricks the victim into
logging in with that session ID, and then uses the session ID themselves.
Creating a new ID post-login prevents this.

### Device/Session Limit
```typescript
const MAX_ACTIVE_SESSIONS = 10;

async function createSessionWithLimit(userId: string): Promise<Session> {
  const activeSessions = await db.query.sessions.findMany({
    where: and(eq(sessions.userId, userId), gt(sessions.expiresAt, new Date())),
    orderBy: asc(sessions.createdAt),
  });

  // If at limit, revoke the oldest
  if (activeSessions.length >= MAX_ACTIVE_SESSIONS) {
    const oldest = activeSessions[0];
    await db.delete(sessions).where(eq(sessions.id, oldest.id));
  }

  return await createSession(userId);
}
```

This prevents infinite session accumulation and surfaces compromised sessions
sooner.

---

## Session Validation (Every Request)

### The Three Checks
```typescript
async function validateSession(req: Request): Promise<User | null> {
  // 1. Extract session from cookie or header
  const sessionId = extractSessionFromRequest(req);
  if (!sessionId) return null;

  // 2. Look up session
  const session = await db.query.sessions.findFirst({
    where: eq(sessions.id, sessionId),
  });
  if (!session) return null;

  // 3. Validate
  if (session.expiresAt < new Date()) return null;
  if (session.revokedAt) return null;

  // 4. Fetch user (separate query or JOIN)
  const user = await db.query.users.findFirst({
    where: eq(users.id, session.userId),
  });
  if (!user) return null;

  // 5. Check user state
  if (user.suspendedAt) return null;
  if (user.deletedAt) return null;

  return user;
}
```

### Performance Optimization
Session lookup on every request is slow. Options:

**Option A: JWT with revocation list**
Fast in the happy path (verify signature, check revocation cache).

**Option B: Cached session**
```typescript
const sessionCache = new LRUCache<string, Session>({ max: 10000, ttl: 60_000 });

async function validateSessionCached(sessionId: string): Promise<User | null> {
  const cached = sessionCache.get(sessionId);
  if (cached && cached.expiresAt > new Date()) {
    // Fast path: cached, not expired
    return await getUserById(cached.userId);
  }

  // Slow path: DB lookup
  const session = await db.query.sessions.findFirst({ where: eq(sessions.id, sessionId) });
  if (session) sessionCache.set(sessionId, session);
  return await getUserFromSession(session);
}
```

**Tradeoff:** Cache hides revocations. A revoked session can still be valid for
up to the cache TTL. For high-security endpoints, bypass the cache.

---

## Session Refresh

### The Rotation Pattern
```typescript
async function refreshSession(refreshToken: string): Promise<{ access: string; refresh: string } | null> {
  // 1. Hash the refresh token to look up (never store raw)
  const refreshHash = hashToken(refreshToken);

  // 2. Look up the token
  const tokenRecord = await db.query.refreshTokens.findFirst({
    where: eq(refreshTokens.hash, refreshHash),
  });

  if (!tokenRecord) return null;
  if (tokenRecord.revokedAt) {
    // CRITICAL: if a revoked token is used, it means someone has the raw token
    // — possible compromise. Revoke the entire token family.
    await revokeTokenFamily(tokenRecord.familyId);
    return null;
  }
  if (tokenRecord.expiresAt < new Date()) return null;

  // 3. Issue new tokens
  const newRefresh = generateRefreshToken();
  const newAccess = generateAccessToken(tokenRecord.userId);

  // 4. Rotate: revoke old refresh token, insert new
  await db.transaction(async (tx) => {
    await tx.update(refreshTokens)
      .set({ revokedAt: new Date(), replacedBy: newRefresh.id })
      .where(eq(refreshTokens.id, tokenRecord.id));

    await tx.insert(refreshTokens).values({
      id: newRefresh.id,
      hash: hashToken(newRefresh.token),
      userId: tokenRecord.userId,
      familyId: tokenRecord.familyId, // Same family as original
      createdAt: new Date(),
      expiresAt: new Date(Date.now() + REFRESH_TOKEN_TTL_MS),
    });
  });

  return { access: newAccess, refresh: newRefresh.token };
}
```

### The Token Family
Each original refresh token starts a "family." Rotation keeps the family ID
but issues new tokens. If an old (already-rotated) token is reused, it means
someone kept the raw value — probable compromise. Revoke the entire family.

```typescript
async function revokeTokenFamily(familyId: string) {
  await db.update(refreshTokens)
    .set({ revokedAt: new Date(), revokedReason: 'family_compromise_detected' })
    .where(eq(refreshTokens.familyId, familyId));

  logger.warn({ familyId }, 'Token family revoked due to reuse of rotated token');
}
```

### The Refresh Token Storage
**Raw token:** Returned to client once, never stored server-side.
**Hash:** Stored server-side for lookup.
**Family ID:** Groups related tokens.

```typescript
function generateRefreshToken(): { id: string; token: string } {
  const id = crypto.randomUUID();
  const token = crypto.randomBytes(32).toString('base64url');
  return { id, token };
}

function hashToken(token: string): string {
  return crypto.createHash('sha256').update(token).digest('hex');
}
```

---

## Session Revocation

### Triggers for Revocation
- User clicks "Sign out"
- User changes password → revoke ALL other sessions
- User deletes account
- Admin suspends user
- Password reset completed → revoke all sessions
- MFA enabled → revoke all sessions (optional but recommended)
- Detected compromise (IP anomaly, credential leak detected)
- Max session age reached (forced re-auth)

### The Revoke Operation
```typescript
async function revokeSession(sessionId: string, reason: string) {
  await db.transaction(async (tx) => {
    // Revoke the session record
    await tx.update(sessions)
      .set({ revokedAt: new Date(), revokedReason: reason })
      .where(eq(sessions.id, sessionId));

    // Revoke associated refresh tokens
    await tx.update(refreshTokens)
      .set({ revokedAt: new Date(), revokedReason: reason })
      .where(eq(refreshTokens.sessionId, sessionId));
  });

  // Clear cache (if using)
  sessionCache.delete(sessionId);
}

async function revokeAllUserSessions(userId: string, reason: string) {
  const userSessions = await db.query.sessions.findMany({
    where: eq(sessions.userId, userId),
  });

  await Promise.all(userSessions.map(s => revokeSession(s.id, reason)));

  logger.info({ userId, sessionCount: userSessions.length, reason },
    'All user sessions revoked');
}
```

### Revocation Endpoint (RFC 7009)
```typescript
// POST /api/auth/revoke
// ALWAYS returns 200 regardless of token validity (prevents enumeration)
export async function POST(req: Request) {
  const { token, type } = await req.json();

  if (type === 'access') {
    // Access tokens are typically JWTs; add to revocation list
    const payload = jwt.decode(token); // decode without verify; we're adding to a block list
    if (payload?.jti) {
      await db.insert(revocationList).values({ jti: payload.jti, expiresAt: new Date(payload.exp * 1000) })
        .onConflictDoNothing();
    }
  } else if (type === 'refresh') {
    const refreshHash = hashToken(token);
    await db.update(refreshTokens)
      .set({ revokedAt: new Date(), revokedReason: 'user_revoked' })
      .where(eq(refreshTokens.hash, refreshHash));
  }

  return new Response('OK', { status: 200 });
}
```

**Always return 200.** This prevents attackers from using the revoke endpoint
to enumerate valid tokens.

---

## Session Storage Cleanup

Expired sessions accumulate. Clean them up:

```typescript
// cron: daily
async function cleanupExpiredSessions() {
  const deleted = await db.delete(sessions)
    .where(lt(sessions.expiresAt, new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)));

  logger.info({ deletedCount: deleted.rowCount }, 'Expired sessions cleaned up');
}
```

Keep recently-expired sessions for 7 days for forensics, then delete.

---

## Session Auditing

Every session event should be logged:

```typescript
type SessionAuditEvent =
  | { type: 'session_created'; method: 'password' | 'oauth' | 'sso' | 'magic_link' }
  | { type: 'session_refreshed' }
  | { type: 'session_revoked'; reason: string }
  | { type: 'session_expired' };

async function logSessionEvent(
  sessionId: string,
  userId: string,
  event: SessionAuditEvent,
  context: { ip: string; userAgent: string }
) {
  await db.insert(auditLog).values({
    actor_id: userId,
    action: event.type,
    resource_type: 'session',
    resource_id: sessionId,
    metadata: { ...event, ...context },
  });
}
```

Query patterns for incident response:
- All sessions for a user in the last 7 days
- All sessions from a specific IP
- All sessions where reason = 'family_compromise_detected'

---

## The Logout Everywhere Flow

When a user changes their password or detects compromise, they may want to log
out of all devices.

```typescript
async function logoutEverywhere(userId: string) {
  // Option A: Revoke all current sessions
  await revokeAllUserSessions(userId, 'user_logout_all');

  // Option B: Rotate the user's "generation" number; existing sessions with
  // old generation are invalid
  await db.update(users)
    .set({ sessionGeneration: sql`session_generation + 1` })
    .where(eq(users.id, userId));
}

// In validation:
async function validateSessionWithGeneration(session: Session): Promise<boolean> {
  const user = await getUserById(session.userId);
  return session.userGeneration === user.sessionGeneration;
}
```

Option B is faster (one UPDATE vs many) and scales better for users with many
sessions.

---

## Audit Checklist

### Cookie security
- [ ] Session cookies are `HttpOnly` (unless Supabase SDK limitation)
- [ ] Cookies are `Secure` in production
- [ ] Cookies use `SameSite=Lax` or stricter
- [ ] Cookie names use `__Host-` or `__Secure-` prefix

### Session creation
- [ ] Session ID is cryptographically random (32+ bytes)
- [ ] Pre-login session ID is invalidated (no session fixation)
- [ ] Login uses constant-time password comparison
- [ ] Login normalizes timing across user existence
- [ ] Session creation logged with IP and user agent

### Session validation
- [ ] Every request validates session (not just home page)
- [ ] Validation checks: exists, not revoked, not expired, user not suspended
- [ ] Cached validation has short TTL or bypasses cache for high-risk endpoints

### Session refresh
- [ ] Refresh tokens rotated on each use
- [ ] Old refresh tokens are invalidated, not just expired
- [ ] Reuse of rotated token triggers family revocation
- [ ] Refresh tokens stored as hashes, not raw

### Revocation
- [ ] Password change revokes all sessions
- [ ] Logout endpoint works
- [ ] Admin can force-revoke user sessions
- [ ] Revocation endpoint always returns 200 (no enumeration)

### Cleanup
- [ ] Expired sessions cleaned up daily
- [ ] Recently-expired sessions retained for 7 days for forensics

### Audit
- [ ] All session events logged
- [ ] Session logs queryable for incident response
- [ ] Alerts on unusual session patterns (multiple countries in short time)

---

## See Also

- [AUTH.md](AUTH.md) — authentication section
- [COOKBOOK.md](COOKBOOK.md) — real production implementations
- [TIMING-SAFE.md](TIMING-SAFE.md) — constant-time login
- [RATE-LIMITING.md](RATE-LIMITING.md) — rate limits on auth endpoints
