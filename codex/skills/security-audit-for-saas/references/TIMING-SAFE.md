# Timing-Safe Comparisons

Timing attacks are side channels where response time leaks information. For
secret comparison, non-constant-time comparison can reveal individual bytes
of the secret. This file covers timing-safe patterns for SaaS.

---

## Why Timing Matters

### The Classical Attack
`strcmp("password", userInput)` exits on the first mismatched character. By
measuring response time:
- If first character is wrong: fast response (1 byte compared)
- If first character matches: slower (more bytes compared)

At scale (millions of requests), the timing differences become statistically
significant even over the internet. A patient attacker can extract the secret
byte-by-byte.

### The Modern Attack
Modern CPUs have branch prediction and cache effects that make even "equal
length" comparisons timing-dependent. You must use constant-time primitives
from cryptographic libraries.

---

## The Three Variants

### Variant A: Length-Padded Pre-Compare

**Use when:** Inputs may have different lengths.

```typescript
import { timingSafeEqual } from 'crypto';

export function timingSafeEqualPadded(a: string, b: string): boolean {
  const bufA = Buffer.from(a);
  const bufB = Buffer.from(b);
  const maxLen = Math.max(bufA.length, bufB.length);

  // Pad both to max length
  const paddedA = Buffer.alloc(maxLen);
  const paddedB = Buffer.alloc(maxLen);
  bufA.copy(paddedA);
  bufB.copy(paddedB);

  // Compare the padded buffers (this is the constant-time part)
  const equal = timingSafeEqual(paddedA, paddedB);

  // Return false if lengths differed, even if padded comparison "matched"
  return equal && bufA.length === bufB.length;
}
```

**Key insight:** Call `timingSafeEqual` BEFORE returning false for length
mismatch. Otherwise, the length check itself is a timing oracle.

### Variant B: Hash-Both-Sides

**Use when:** You want to avoid thinking about lengths entirely.

```typescript
import { createHash, timingSafeEqual } from 'crypto';

export function timingSafeCompareHashed(a: string, b: string): boolean {
  // Hash both inputs to 32 bytes (SHA-256)
  const hashA = createHash('sha256').update(a).digest();
  const hashB = createHash('sha256').update(b).digest();

  // Now both buffers are always 32 bytes, guaranteed
  return timingSafeEqual(hashA, hashB);
}
```

**Tradeoffs:**
- Pro: Foolproof — can't screw up length handling
- Pro: Length of inputs doesn't leak via timing
- Con: Hash computation time is proportional to input length (but still constant-
  time for fixed-length inputs)
- Con: Not suitable if you need to fail fast on length mismatch

### Variant C: Length-Pre-Check (After Buffer Creation)

**Use when:** Inputs should always be the same length (e.g., HMAC digests).

```typescript
import { timingSafeEqual } from 'crypto';

export function verifyHmac(payload: string, signature: string, secret: string): boolean {
  const expectedPrefix = 'sha256=';
  if (!signature.startsWith(expectedPrefix)) return false;

  const providedSig = signature.slice(expectedPrefix.length);
  const expectedSig = computeHmac(payload, secret);

  const providedBuf = Buffer.from(providedSig, 'hex');
  const expectedBuf = Buffer.from(expectedSig, 'hex');

  // If lengths differ, it's definitely not a valid signature
  // (This early-return is acceptable for fixed-length crypto outputs)
  if (providedBuf.length !== expectedBuf.length) return false;

  return timingSafeEqual(providedBuf, expectedBuf);
}
```

**Why this is safe:** For cryptographic outputs, the expected length is fixed
and public knowledge. An attacker knowing "the signature is 32 bytes" doesn't
help them. The early return on length mismatch leaks nothing useful.

**When to use:** HMAC signatures, hash outputs, keys with known fixed lengths.

---

## Where to Apply Timing-Safe Comparison

### ALWAYS timing-safe
- [ ] API key / bearer token comparison
- [ ] Webhook signature verification (HMAC)
- [ ] JWT signature verification (the library should handle this)
- [ ] CSRF token comparison
- [ ] OAuth state parameter validation
- [ ] SAML `InResponseTo` validation
- [ ] Password hash verification (use bcrypt's built-in)
- [ ] Cron secret verification
- [ ] Admin API key comparison
- [ ] Magic link token comparison
- [ ] Password reset token comparison
- [ ] Session ID validation (when comparing against DB)
- [ ] Device code verification

### Sometimes timing-safe
- Username/email lookup (to prevent enumeration timing): use dummy bcrypt
- Promo code validation: acceptable to be fast if error is constant

### Never timing-safe (waste of CPU)
- Public data comparison
- Integer comparison for IDs (already constant-time)
- Enum value comparison

---

## Real-World Failures to Avoid

### Failure 1: The `===` Trap
```typescript
// BAD
if (req.headers.get('x-api-key') === process.env.API_KEY) { /* ... */ }
```

String equality in JavaScript is NOT constant-time. V8 may use SIMD for short
strings (fast) or character-by-character (slow on mismatch).

### Failure 2: The `startsWith` Trap
```typescript
// BAD
if (userInput.startsWith(prefix)) { /* ... */ }
```

`startsWith` exits early on mismatch. Don't use for secret prefix checks. Use
constant-time comparison of the prefix portion.

### Failure 3: The Length-First Trap
```typescript
// BAD — length check leaks info
if (input.length !== expected.length) return false;
return timingSafeEqual(input, expected);
```

The length check tells the attacker "your guess has the wrong length" before
they waste time guessing. Use Variant A (padded) or Variant B (hashed).

**Exception:** For cryptographic outputs with publicly-known fixed length, the
early length check is acceptable (Variant C).

### Failure 4: The Early-Return Trap
```typescript
// BAD
function verify(token: string): boolean {
  const decoded = decodeToken(token);
  if (!decoded) return false;  // early return on parse failure
  if (decoded.expired) return false;  // early return on expiry
  return timingSafeEqual(decoded.sig, expectedSig);
}
```

Each early return has a different timing profile. Attackers can distinguish
"parse failed" from "expired" from "bad signature" based on response time.

**Fix:** Perform all checks unconditionally, then combine the results at the
end.

```typescript
function verify(token: string): boolean {
  const decoded = decodeTokenSafely(token); // Always returns a decoded object
  const parseOk = decoded !== null;
  const notExpired = !parseOk ? false : !decoded.expired;
  const sigMatches = !parseOk ? false : timingSafeEqual(decoded.sig, expectedSig);
  return parseOk && notExpired && sigMatches;
}
```

### Failure 5: The Language Quirk Trap

Different languages have different defaults:
- Node.js `crypto.timingSafeEqual()` — correct
- Node.js `===` — not safe
- Python `hmac.compare_digest()` — correct
- Python `==` — not safe
- Go `subtle.ConstantTimeCompare()` — correct
- Go `==` — not safe
- Rust `constant_time_eq` crate — correct
- Rust `==` — not safe

---

## Timing-Safe Beyond Strings

### Database Lookup Timing
```sql
-- BAD: fast when user doesn't exist, slow when they do
SELECT * FROM users WHERE email = ? AND password_hash = ?;
```

The SELECT is faster when the email doesn't match (index seek, no rows) than
when it matches (bcrypt compare required).

**Fix:** Always run bcrypt, even for non-existent users.

```typescript
const user = await db.query.users.findFirst({ where: eq(users.email, email) });
const hashToCheck = user?.passwordHash ?? DUMMY_BCRYPT_HASH; // Always run bcrypt
const passwordOk = await bcrypt.compare(password, hashToCheck);

if (!user || !passwordOk) {
  // Same error regardless of which failed
  return { error: 'Invalid credentials' };
}
```

### HTTP Response Timing
```typescript
// BAD: different error messages have different JSON encoding time
if (!user) return Response.json({ error: 'User not found' });
if (!user.emailVerified) return Response.json({ error: 'Email not verified' });
if (!passwordOk) return Response.json({ error: 'Wrong password' });
```

Each response has different length → different TLS overhead → timing oracle.

**Fix:** Constant-length responses for auth endpoints.

```typescript
const GENERIC_ERROR = { error: 'Invalid credentials' };
if (!user || !user.emailVerified || !passwordOk) {
  return Response.json(GENERIC_ERROR, { status: 401 });
}
```

### Query Timing
```typescript
// BAD: unused WHERE clause may leak whether the user exists
await db.query.users.findFirst({
  where: and(eq(users.email, email), eq(users.tenantId, tenantId))
});
```

Two-level lookups can leak info. For sensitive lookups, use constant-time
DB patterns or add artificial delays to normalize timing.

---

## Testing for Timing Leaks

### Local Testing
```typescript
import { performance } from 'perf_hooks';

async function measureTiming(fn: () => Promise<void>, iterations = 10000) {
  const times: number[] = [];
  for (let i = 0; i < iterations; i++) {
    const start = performance.now();
    await fn();
    times.push(performance.now() - start);
  }
  times.sort((a, b) => a - b);
  return {
    p50: times[Math.floor(iterations * 0.5)],
    p95: times[Math.floor(iterations * 0.95)],
    p99: times[Math.floor(iterations * 0.99)],
    mean: times.reduce((a, b) => a + b) / iterations,
  };
}

test('login timing is constant for valid vs invalid user', async () => {
  const validTiming = await measureTiming(async () => {
    await login('real@user.com', 'wrong-password');
  });
  const invalidTiming = await measureTiming(async () => {
    await login('fake@user.com', 'wrong-password');
  });

  // Expect means to be within 10% of each other
  const ratio = Math.abs(validTiming.mean - invalidTiming.mean) / validTiming.mean;
  expect(ratio).toBeLessThan(0.1);
});
```

### Remote Testing
Timing attacks work over the internet, but with much noisier measurements. Use
statistical tests:
- Run thousands of measurements
- Compute confidence intervals
- Use Mann-Whitney U test to check if distributions differ

Tools: `dudect` (https://github.com/oreparaz/dudect), custom scripts.

---

## The "Good Enough" Defense

Perfect constant-time is hard. For most SaaS, "good enough" is:

1. Use library primitives (`timingSafeEqual`, `bcrypt.compare`)
2. Always run the expensive operation (bcrypt for non-existent users)
3. Return constant-shape errors
4. Add a random jitter for extra safety (0-50ms)

```typescript
async function loginWithJitter(email: string, password: string) {
  const user = await db.query.users.findFirst({ where: eq(users.email, email) });
  const hashToCheck = user?.passwordHash ?? DUMMY_HASH;
  const passwordOk = await bcrypt.compare(password, hashToCheck);

  // Add random jitter to normalize timing
  await new Promise(r => setTimeout(r, Math.random() * 50));

  if (!user || !passwordOk) {
    return { error: 'Invalid credentials' };
  }
  return { user };
}
```

Jitter is not a substitute for constant-time primitives. It's a defense-in-
depth layer.

---

## Audit Checklist

### Grep for unsafe patterns
```bash
# Direct string equality on secrets
rg -n '(token|secret|key|hash|password)\s*===' --type ts
rg -n '==\s*(token|secret|key|hash|password)' --type ts

# Early return on length mismatch (before timing-safe check)
rg -n 'length\s*!==?\s*\w+\.length[^;]*return' --type ts

# jwt.decode without verify
rg -n 'jwt\.decode\(' --type ts
```

### Review each hit
For each match, ask:
1. Is the value on the right side of `==` a secret?
2. Is the comparison used for an access decision?
3. Could an attacker time this operation remotely?

If any yes: convert to `timingSafeEqual`.

### Test timing behavior
For each critical auth endpoint, measure timing for:
- Valid user + correct password
- Valid user + wrong password
- Invalid user (doesn't exist)
- Invalid user (doesn't exist) with correct-format password

If the timing distributions differ significantly, you have a leak.

---

## See Also

- [AUTH.md](AUTH.md) — timing-safe comparisons section
- [COOKBOOK.md](COOKBOOK.md) Pattern 6 — production timing-safe implementation
- [FIELD-GUIDE.md](FIELD-GUIDE.md) Story 20 — birthday collision from truncation
- [CRYPTO-FUNDAMENTALS.md](CRYPTO-FUNDAMENTALS.md)
