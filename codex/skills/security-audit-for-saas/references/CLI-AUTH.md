# CLI Authentication (Device Code Flow)

For SaaS with a CLI tool, authenticating the CLI is harder than authenticating
a browser. The user can't easily paste a token, can't store cookies, and can't
open a browser from a headless terminal. RFC 8628 Device Authorization Grant
(device code flow) is the solution.

---

## The Device Code Flow (RFC 8628)

```
┌────────┐                              ┌──────┐                   ┌─────┐
│  CLI   │                              │ SaaS │                   │User │
└───┬────┘                              └──┬───┘                   └──┬──┘
    │                                      │                           │
    │ POST /api/cli/device-code            │                           │
    │─────────────────────────────────────>│                           │
    │                                      │                           │
    │  { device_code, user_code,           │                           │
    │    verification_uri, expires_in,     │                           │
    │    interval }                        │                           │
    │<─────────────────────────────────────│                           │
    │                                      │                           │
    │  Print: "Go to https://app/cli       │                           │
    │         and enter code ABCD-1234"    │                           │
    │                                      │                           │
    │  User opens browser                  │                           │
    │ ────────────────────────────────────────────────────────────────>│
    │                                      │                           │
    │                                      │   User enters ABCD-1234   │
    │                                      │<──────────────────────────│
    │                                      │                           │
    │                                      │   Login + approve         │
    │                                      │<──────────────────────────│
    │                                      │                           │
    │ POST /api/cli/device-token           │                           │
    │ (poll every 5s with device_code)     │                           │
    │─────────────────────────────────────>│                           │
    │                                      │                           │
    │  { access_token, refresh_token }     │                           │
    │<─────────────────────────────────────│                           │
    │                                      │                           │
```

---

## Implementation

### Step 1: Device Code Generation

```typescript
// POST /api/cli/device-code
export async function POST(req: Request) {
  // Rate limit: 5/min per IP
  const rl = await checkRateLimit(req, 'device-code-issue');
  if (!rl.allowed) return Response.json({ error: 'Rate limited' }, { status: 429 });

  // Generate codes
  const deviceCode = generateDeviceCode();    // 40 bytes → base64url
  const userCode = generateUserCode();         // Human-typable 8 chars

  const expiresAt = new Date(Date.now() + 15 * 60 * 1000); // 15 min

  await db.insert(deviceCodes).values({
    id: crypto.randomUUID(),
    deviceCodeHash: hashToken(deviceCode),
    userCode,
    expiresAt,
    pollInterval: 5,
    ipHash: hashIp(getClientIp(req)),
    createdAt: new Date(),
  });

  return Response.json({
    device_code: deviceCode,
    user_code: userCode,
    verification_uri: `https://app.example.com/cli`,
    verification_uri_complete: `https://app.example.com/cli?code=${userCode}`,
    expires_in: 900,  // 15 min
    interval: 5,
  });
}

function generateDeviceCode(): string {
  return crypto.randomBytes(40).toString('base64url');
}

function generateUserCode(): string {
  // Safe alphabet: excludes confusable chars (0, O, I, l, 1)
  const chars = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';

  // Rejection sampling for uniform distribution
  const code: string[] = [];
  while (code.length < 8) {
    const byte = crypto.randomBytes(1)[0];
    // 31 chars in alphabet, 248 = floor(256/31)*31 (largest multiple < 256)
    if (byte < 248) {
      code.push(chars[byte % chars.length]);
    }
  }

  // Format as ABCD-1234 for readability
  return code.slice(0, 4).join('') + '-' + code.slice(4).join('');
}
```

### Step 2: User Verification

```typescript
// POST /api/cli/verify (called from the web UI)
export async function POST(req: Request) {
  // Require session
  const session = await requireSession(req);

  // Rate limit: 10/min per IP (user-typed, one-time)
  const rl = await checkRateLimit(req, 'device-code-verify');
  if (!rl.allowed) return Response.json({ error: 'Rate limited' }, { status: 429 });

  const { userCode } = await req.json();

  // Normalize user code (strip spaces, case-insensitive)
  const normalized = userCode.toUpperCase().replace(/[^A-Z0-9]/g, '');
  if (normalized.length !== 8) {
    return Response.json({ error: 'Invalid format' }, { status: 400 });
  }

  // Atomic update: only succeed if not yet verified
  const result = await db.update(deviceCodes)
    .set({
      userId: session.userId,
      verifiedAt: new Date(),
    })
    .where(and(
      eq(deviceCodes.userCode, normalized),
      isNull(deviceCodes.verifiedAt),
      gt(deviceCodes.expiresAt, new Date()),
    ))
    .returning();

  if (result.length === 0) {
    // Track failed attempt
    await trackAbuseSignal({
      signal: 'device_code_verify_failed',
      request: req,
      source: 'user',
    });
    return Response.json({ error: 'Invalid or expired code' }, { status: 400 });
  }

  return Response.json({ success: true });
}
```

**CRITICAL:** The atomic update with `isNull(verifiedAt)` prevents race
conditions and double-verification.

### Step 3: Token Polling

```typescript
// POST /api/cli/device-token (called by CLI)
export async function POST(req: Request) {
  // Rate limit: 30/min per IP (matches RFC 8628 5-sec poll interval)
  const rl = await checkRateLimit(req, 'device-code-poll');
  if (!rl.allowed) return Response.json({ error: 'slow_down' }, { status: 429 });

  const { device_code } = await req.json();
  if (!device_code) {
    return Response.json({ error: 'invalid_request' }, { status: 400 });
  }

  const codeHash = hashToken(device_code);
  const record = await db.query.deviceCodes.findFirst({
    where: eq(deviceCodes.deviceCodeHash, codeHash),
  });

  if (!record) {
    return Response.json({ error: 'invalid_grant' }, { status: 400 });
  }

  if (record.expiresAt < new Date()) {
    return Response.json({ error: 'expired_token' }, { status: 400 });
  }

  if (!record.verifiedAt) {
    return Response.json({ error: 'authorization_pending' }, { status: 400 });
  }

  // Verified! Issue tokens
  const accessToken = await issueAccessToken(record.userId);
  const refreshToken = await issueRefreshToken(record.userId, record.id);

  // Mark device code as used (prevent reuse)
  await db.delete(deviceCodes).where(eq(deviceCodes.id, record.id));

  return Response.json({
    access_token: accessToken,
    token_type: 'Bearer',
    expires_in: 3600,
    refresh_token: refreshToken,
  });
}
```

---

## Security Considerations

### 1. Rate Limiting
Each endpoint has a specific rate limit:
- **Issue:** 5/min per IP (low; users don't issue many codes)
- **Verify:** 10/min per IP (medium; user-typed, rare)
- **Poll:** 30/min per IP (higher; CLI polls every 5 sec)

### 2. Failed Verification Tracking
Track failed verifications as abuse signals. An attacker might brute-force
8-character user codes. 8 chars from 31-char alphabet = 31^8 ≈ 8.5 × 10^11
combinations. At 30 req/min with rate limit, brute force is infeasible, but
detection helps catch anomalies.

### 3. Code Expiry
Device codes expire after 15 minutes. User codes also expire with them (they
share the same record).

### 4. Single-Use Codes
After successful token exchange, delete the device code. Prevents reuse.

### 5. IP Hashing for Forensics
Store only the HASH of the IP, not the raw IP, for GDPR compliance but
retaining forensic capability.

### 6. Token Storage on the CLI Side
The CLI stores tokens on disk. Use platform-specific secure storage:
- **macOS:** Keychain (`security` command)
- **Linux:** Secret Service API (`libsecret`)
- **Windows:** Credential Manager

Fallback to filesystem with 0600 permissions in home directory.

```bash
# CLI token storage convention
~/.config/your-cli/auth.json  # mode 0600
```

### 7. Token Format Identifier
CLI tokens should be distinguishable from other tokens:
```
jsm_ci_<40-byte-base64url>
```

The `jsm_` prefix (your product) + `ci_` subtype helps:
- GitHub secret scanning can recognize and alert on leaks
- Server-side can detect wrong token types
- Audit logs can filter by type

### 8. Token Hashing in Storage
Store only the SHA-256 hash of tokens server-side:
```typescript
function hashToken(token: string): string {
  return crypto.createHash('sha256').update(token).digest('hex');
}

// When a token is presented:
const presentedHash = hashToken(bearerToken);
const record = await db.query.tokens.findFirst({
  where: eq(tokens.hash, presentedHash),
});
```

If the DB is breached, attackers have hashes, not tokens.

---

## Token Lifecycle

### Token Refresh
```typescript
// POST /api/cli/token/refresh
export async function POST(req: Request) {
  // Rate limit: 30/min per IP
  const rl = await checkRateLimit(req, 'token-refresh');
  if (!rl.allowed) return Response.json({ error: 'Rate limited' }, { status: 429 });

  const { refresh_token } = await req.json();
  const refreshHash = hashToken(refresh_token);

  const tokenRecord = await db.query.refreshTokens.findFirst({
    where: eq(refreshTokens.hash, refreshHash),
  });

  if (!tokenRecord || tokenRecord.revokedAt || tokenRecord.expiresAt < new Date()) {
    return Response.json({ error: 'invalid_grant' }, { status: 400 });
  }

  // Rotate: issue new tokens, revoke old
  const newRefresh = generateRefreshToken();
  const newAccess = await issueAccessToken(tokenRecord.userId);

  await db.transaction(async (tx) => {
    await tx.update(refreshTokens)
      .set({ revokedAt: new Date(), replacedBy: newRefresh.id })
      .where(eq(refreshTokens.id, tokenRecord.id));

    await tx.insert(refreshTokens).values({
      id: newRefresh.id,
      hash: hashToken(newRefresh.token),
      userId: tokenRecord.userId,
      familyId: tokenRecord.familyId,  // Same family, new token
      createdAt: new Date(),
      expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),  // 30 days
    });
  });

  return Response.json({
    access_token: newAccess,
    refresh_token: newRefresh.token,
    expires_in: 3600,
  });
}
```

### Token Revocation
```typescript
// POST /api/cli/token/revoke
export async function POST(req: Request) {
  const { token, token_type_hint } = await req.json();

  if (token_type_hint === 'access_token') {
    const tokenHash = hashToken(token);
    await db.update(accessTokens)
      .set({ revokedAt: new Date() })
      .where(eq(accessTokens.hash, tokenHash));
  } else if (token_type_hint === 'refresh_token') {
    const tokenHash = hashToken(token);
    const record = await db.query.refreshTokens.findFirst({
      where: eq(refreshTokens.hash, tokenHash),
    });
    if (record) {
      // Revoke entire family (all tokens derived from this chain)
      await db.update(refreshTokens)
        .set({ revokedAt: new Date() })
        .where(eq(refreshTokens.familyId, record.familyId));
    }
  }

  // ALWAYS return 200 (RFC 7009 - prevent enumeration)
  return Response.json({});
}
```

### Last-Used Tracking
Track when tokens were last used, for:
- Dormant token detection ("token not used in 90 days")
- Compromise detection ("token used from 2 countries")
- Analytics

```typescript
// Debounced update (don't hit DB on every request)
const LAST_USED_UPDATE_INTERVAL_MS = 60 * 60 * 1000; // 1 hour

async function validateBearerToken(token: string): Promise<User | null> {
  const tokenHash = hashToken(token);
  const record = await db.query.accessTokens.findFirst({
    where: eq(accessTokens.hash, tokenHash),
  });

  if (!record || record.revokedAt || record.expiresAt < new Date()) return null;

  // Debounced update
  if (!record.lastUsedAt || Date.now() - record.lastUsedAt.getTime() > LAST_USED_UPDATE_INTERVAL_MS) {
    after(async () => {
      await db.update(accessTokens)
        .set({ lastUsedAt: new Date() })
        .where(eq(accessTokens.id, record.id));
    });
  }

  return getUserById(record.userId);
}
```

---

## The User Experience

### CLI Flow
```bash
$ your-cli login
Opening https://app.example.com/cli?code=ABCD-1234 in your browser...

Please confirm the code: ABCD-1234
Waiting for authentication... ⠏
✓ Authenticated as user@example.com
Token stored in macOS Keychain.
```

### Web Flow
1. User navigates to `https://app.example.com/cli`
2. Pre-fills with `?code=ABCD-1234` if provided
3. User confirms code matches what CLI shows (prevents phishing)
4. User logs in if not already
5. User clicks "Authorize CLI access"
6. Confirmation shown, CLI can now proceed

### Phishing Protection
The user must confirm the code matches what their CLI displayed. This prevents
phishing where:
1. Attacker gets their own device code on `/api/cli/device-code`
2. Attacker tricks user into authorizing it
3. Attacker gets the token

The code confirmation step means the user must see "ABCD-1234 shown by your
CLI" in the browser, and match it to what the CLI printed. Mismatch = attack.

---

## Audit Checklist

### Code generation
- [ ] Device codes are 40+ bytes of crypto random
- [ ] User codes use safe alphabet (no 0/O/I/l/1)
- [ ] Rejection sampling for uniform distribution
- [ ] 15 min expiry
- [ ] Rate limited (5/min per IP)

### Verification
- [ ] Atomic update prevents race condition
- [ ] Normalization (uppercase, strip non-alphanumeric) before check
- [ ] Normalization applied to BOTH validation and lookup
- [ ] Failed verifications tracked as abuse signals
- [ ] Rate limited (10/min per IP)

### Polling
- [ ] Returns proper RFC 8628 error codes (`authorization_pending`, `slow_down`, `expired_token`)
- [ ] Rate limited (30/min per IP)
- [ ] Device code deleted after successful token exchange (prevents reuse)

### Token management
- [ ] Tokens hashed in storage (SHA-256)
- [ ] Token format includes identifiable prefix (`jsm_ci_`)
- [ ] Refresh tokens rotated on each use
- [ ] Rotation uses token family for reuse detection
- [ ] Revocation endpoint returns 200 regardless of validity
- [ ] Last-used tracking with debouncing

### Client-side storage
- [ ] CLI uses platform secure storage (Keychain, libsecret, Credential Manager)
- [ ] Fallback to 0600 permissions in home dir
- [ ] Token prefix makes GitHub secret scanning effective

### UX
- [ ] Phishing prevention via code confirmation step
- [ ] Clear user consent ("Authorize CLI access")
- [ ] Revocation UI in user dashboard

---

## See Also

- [AUTH.md](AUTH.md)
- [SESSION-MANAGEMENT.md](SESSION-MANAGEMENT.md)
- [RATE-LIMITING.md](RATE-LIMITING.md)
- [COOKBOOK.md](COOKBOOK.md)
- RFC 8628: https://tools.ietf.org/html/rfc8628
- RFC 7009: https://tools.ietf.org/html/rfc7009 (token revocation)
