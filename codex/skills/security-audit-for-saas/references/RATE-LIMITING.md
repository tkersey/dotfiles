# Rate Limiting & Abuse Detection for SaaS

Rate limiting is the first line of defense for auth, billing, and API abuse.
Done poorly, it's a DoS amplifier. Done well, it's invisible to paying users and
effective against attackers.

This file is the complete rate-limiting design guide based on real
production-tested patterns from jeffreys-skills.md and jeffreysprompts_premium.

---

## The Tiered Architecture

Rate limits must be tiered by authentication level AND by endpoint sensitivity.

### Tier Definitions

| Tier | Identifier | Limit | Scope |
|------|-----------|-------|-------|
| **Anonymous** | IP | 60 req/min | Public endpoints |
| **Authenticated** | User ID | 120 req/min | API endpoints |
| **Subscriber** | User ID (subscriber flag) | ∞ (short-circuit) | Premium access |
| **CLI** | API key hash | 600 req/min | CLI token tier |
| **Admin** | User ID (admin flag) | ∞ (bypass) | Admin operations |

**Critical rule:** Subscribers should NEVER be rate-limited on Redis lookups. Check
the subscriber flag first, return allow, bypass Redis entirely. This:
1. Reduces Redis load
2. Avoids ever accidentally limiting paying customers
3. Makes cost-per-subscriber predictable

### Strict Endpoint Overrides

Some endpoints need tighter limits regardless of tier:

| Endpoint Pattern | Limit | Reason |
|------------------|-------|--------|
| `/api/auth/login` | 10/min per email | Brute force prevention |
| `/api/auth/reset-password` | 3/hour per email | Email bombing + enumeration |
| `/api/auth/token/exchange` | 10/min per IP | Brute force authorization codes |
| `/api/auth/token/refresh` | 30/min per token family | Refresh token abuse |
| `/api/auth/token/revoke` | 30/min per user | Enumeration prevention |
| `/api/*/checkout` | 30/min per user | Duplicate checkout prevention |
| `/api/*/webhook` | 1000/min | Provider traffic only |
| `/api/sso/*/callback` | 600/min | OAuth/SSO callback volume |
| `/api/upload` | 10/min per user | Storage abuse |
| `/api/export` | 5/hour per user | Bulk exfiltration prevention |
| `/api/search` | 60/min per user | Enumeration via search |
| `/api/og/*` | 300/min per IP | Image generation is expensive |

### Glob Pattern Matcher

```typescript
function matchesEndpoint(pathname: string, pattern: string): boolean {
  if (!pattern.includes("*")) return pathname === pattern;
  // Escape regex special chars, then replace * with [^/]+
  const regexPattern = pattern
    .split("*")
    .map(segment => segment.replace(/[.+?^${}()|[\]\\]/g, "\\$&"))
    .join("[^/]+");
  return new RegExp("^" + regexPattern + "$").test(pathname);
}
```

**Critical:** Escape regex metacharacters in the literal segments. Failure to escape
means a path like `/api/users.json` could match a different pattern than intended.

---

## The Upstash Redis Pattern

Upstash is the canonical serverless-friendly Redis. Here's the production pattern:

### Initialization (Lazy, Fail-Silent)

```typescript
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

let redisClient: Redis | null = null;
let initAttempted = false;
let cooldownUntil = 0;

function getRedis(): Redis | null {
  if (cooldownUntil > Date.now()) return null; // In cooldown from prior failure
  if (!initAttempted) {
    initAttempted = true;
    if (process.env.UPSTASH_REDIS_URL && process.env.UPSTASH_REDIS_TOKEN) {
      try {
        redisClient = Redis.fromEnv();
      } catch (err) {
        console.error("Upstash init failed:", err);
        // Don't throw — just continue without rate limiting
      }
    }
  }
  return redisClient;
}
```

### Exponential Backoff on Redis Failure

```typescript
let consecutiveFailures = 0;
const MAX_COOLDOWN_MS = 5 * 60 * 1000; // 5 minutes max

function handleRedisFailure() {
  consecutiveFailures++;
  const cooldownMs = Math.min(
    1000 * Math.pow(2, consecutiveFailures - 1), // 1s, 2s, 4s, 8s...
    MAX_COOLDOWN_MS
  );
  cooldownUntil = Date.now() + cooldownMs;
}

function handleRedisSuccess() {
  consecutiveFailures = 0;
  cooldownUntil = 0;
}
```

### The Critical Question: Fail-Open or Fail-Closed?

**For auth endpoints: FAIL CLOSED.**
- Redis down → deny logins with 503
- Accept small amount of user friction during Redis outages
- Prevents attackers from DoS'ing Redis to unlock brute-force

**For regular API endpoints: FAIL OPEN.**
- Redis down → allow requests
- Prevents total site outage during Redis maintenance
- Accept risk of brief unlimited API during outage

**For billing endpoints: FAIL CLOSED.**
- Redis down → deny checkout creation
- Prevents race conditions and duplicate checkouts

Encode this decision per-endpoint, not globally.

### The Subscriber Short-Circuit

```typescript
export async function checkRateLimit(
  request: Request,
  config: RateLimitConfig
): Promise<RateLimitResult> {
  const tier = await detectTier(request);

  // CRITICAL: subscriber and admin short-circuit BEFORE Redis
  if (tier === "subscriber" || tier === "admin") {
    return { allowed: true, tier, remaining: Infinity };
  }

  // Only now do we hit Redis
  const redis = getRedis();
  if (!redis) {
    return handleRedisUnavailable(config); // fail-open or fail-closed
  }

  try {
    const result = await redis.eval(/* sliding window script */);
    handleRedisSuccess();
    return { allowed: result.allowed, tier, remaining: result.remaining };
  } catch (err) {
    handleRedisFailure();
    return handleRedisUnavailable(config);
  }
}
```

---

## The Sliding Window Algorithm (Atomic in Redis)

```lua
-- Sliding window rate limit via ZSET
-- KEYS[1] = rate limit key
-- ARGV[1] = now (ms)
-- ARGV[2] = window size (ms)
-- ARGV[3] = limit

local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])

-- Remove expired entries
redis.call('ZREMRANGEBYSCORE', key, 0, now - window)

-- Count current entries
local count = redis.call('ZCARD', key)

if count >= limit then
  -- Return reset time (oldest entry + window)
  local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
  local reset = tonumber(oldest[2]) + window
  return {0, count, reset}
end

-- Add current request
redis.call('ZADD', key, now, now .. '-' .. math.random())
redis.call('EXPIRE', key, math.ceil(window / 1000))

return {1, count + 1, now + window}
```

**Why sliding window not fixed window?** Fixed windows allow 2x burst at boundary
(full budget at end of window 1 + full budget at start of window 2). Sliding
prevents this.

**Why not token bucket?** Token bucket is fine too, but sliding window is simpler
to reason about for security-sensitive rate limits.

---

## Abuse Detection Signals

Rate limiting stops simple brute-force. Abuse detection catches sophisticated
patterns. Track multi-signal behavioral metrics.

### Signal Taxonomy

```typescript
type AbuseSignal =
  | "download_denied"         // User tried to download denied content
  | "webhook_signature_failed" // Forged webhook attempt
  | "upload_rejected"          // Malicious upload
  | "auth_failed"              // Login/token failure
  | "sequential_enumeration"   // Iterating over sequential IDs
  | "scraping_pattern"         // Rapid requests across unrelated resources
  | "promo_code_probe"         // Multiple promo code attempts
  | "trial_reset_attempt"      // Trying to get a fresh trial
  | "rate_limit_hit"           // Hit rate limit
  | "rls_denial";              // RLS policy denied query

const ABUSE_THRESHOLDS: Record<AbuseSignal, { max: number; windowSeconds: number }> = {
  download_denied:          { max: 30,  windowSeconds: 600 },
  webhook_signature_failed: { max: 10,  windowSeconds: 600 },
  upload_rejected:          { max: 15,  windowSeconds: 3600 },
  auth_failed:              { max: 20,  windowSeconds: 300 },
  sequential_enumeration:   { max: 50,  windowSeconds: 60 },
  scraping_pattern:         { max: 150, windowSeconds: 300 },
  promo_code_probe:         { max: 5,   windowSeconds: 600 },
  trial_reset_attempt:      { max: 3,   windowSeconds: 3600 },
  rate_limit_hit:           { max: 20,  windowSeconds: 300 },
  rls_denial:               { max: 10,  windowSeconds: 300 },
};
```

### Lua Script: Atomic Increment + TTL

```lua
-- KEYS[1] = signal counter key
-- ARGV[1] = window seconds

local count = redis.call('INCR', KEYS[1])
local ttl = redis.call('TTL', KEYS[1])
if ttl == -1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return count
```

### Sequential Enumeration Detection (ZSET)

```lua
-- Detect strictly monotonic numeric sequences
-- KEYS[1] = sequence tracking key
-- ARGV[1] = timestamp (ms)
-- ARGV[2] = requested id (numeric)
-- ARGV[3] = cutoff timestamp (ms - now - window)
-- ARGV[4] = TTL seconds

redis.call('ZADD', KEYS[1], ARGV[2], ARGV[2])
redis.call('ZREMRANGEBYSCORE', KEYS[1], 0, ARGV[3])
redis.call('EXPIRE', KEYS[1], ARGV[4])
-- Cap memory: keep only last 100 entries
redis.call('ZREMRANGEBYRANK', KEYS[1], 0, -101)
return redis.call('ZRANGE', KEYS[1], 0, -1)
```

Then in code, check if the returned IDs form a monotonic sequence with small
increments.

### Fail-Closed on Abuse Detection

**Critical:** Abuse detection checks must **fail-closed** on Redis errors. Unlike
regular rate limits (which may fail-open for UX), abuse signals are explicit
indicators of malicious intent. If Redis is down and an attacker is triggering
abuse signals, you cannot afford to let them through.

```typescript
async function checkAbuseSignal(signal: AbuseSignal, key: string): Promise<boolean> {
  const redis = getRedis();
  if (!redis) {
    // Fail-closed: if we can't check, deny
    logger.warn({ signal, key }, "Redis unavailable for abuse check, denying");
    return false;
  }

  try {
    const count = await incrementWithTTL(redis, `abuse:${signal}:${key}`, threshold.windowSeconds);
    return count <= threshold.max;
  } catch (err) {
    logger.error({ err, signal, key }, "Abuse check failed, denying");
    return false; // Fail-closed
  }
}
```

---

## User Enumeration Prevention

Timing-safe and shape-safe responses are required for rate-limited endpoints.

### Timing-Safe Login

```typescript
export async function login(email: string, password: string) {
  const user = await db.query.users.findFirst({
    where: eq(users.email, email.toLowerCase().trim()),
  });

  // CRITICAL: always run bcrypt, even if user is null
  // Use a pre-computed dummy hash
  const hashToCheck = user?.passwordHash ?? DUMMY_BCRYPT_HASH;
  const isValid = await bcrypt.compare(password, hashToCheck);

  if (!user || !isValid) {
    // Generic error, identical timing regardless of which failed
    return { error: "Invalid email or password" };
  }

  return { user };
}

// Pre-computed once at startup
const DUMMY_BCRYPT_HASH = await bcrypt.hash("dummy-password-not-used", 10);
```

### Constant-Response Password Reset

```typescript
export async function requestPasswordReset(email: string) {
  const user = await db.query.users.findFirst({
    where: eq(users.email, email.toLowerCase().trim()),
  });

  // ALWAYS return success. Send email only if user exists.
  if (user) {
    await sendPasswordResetEmail(user);
  }

  // Wait a constant duration regardless
  await setTimeoutPromise(randomBetween(100, 300));

  return {
    message: "If an account with that email exists, we've sent a reset link.",
  };
}
```

### Cookie Tier Spoofing Prevention

**Vulnerable pattern:**
```typescript
// BAD: tier based on cookie presence
function detectTier(request: Request): Tier {
  if (request.cookies.has("sub_session")) return "subscriber";
  return "anonymous";
}
```

**Safe pattern:**
```typescript
// GOOD: tier based on validated session
async function detectTier(request: Request): Promise<Tier> {
  const session = await validateSession(request); // Full JWT verification
  if (!session) return "anonymous";
  if (session.user.isAdmin) return "admin";
  if (session.user.subscriptionStatus === "active") return "subscriber";
  return "authenticated";
}
```

---

## Rate Limiting in Serverless (Critical Gotchas)

### In-Memory Rate Limiters DO NOT WORK

Serverless instances are ephemeral. State is lost between invocations. An
in-memory rate limiter:
- Has fresh state on each new instance
- Multiple instances run concurrently
- Attackers can hit each instance independently

**Detection:** Grep for `new Map()`, `const counts = {}`, `let buckets = []` in
rate limit code.

**Fix:** Use Redis (Upstash) or another external state store.

### The Cold-Start Burst

New serverless instance = empty state. First requests get through before the
limiter warms up. For sensitive endpoints, lazy-load Redis BEFORE the first
request processing, in the module initialization.

### IP Detection Caveats

On Vercel, `x-real-ip` is trustworthy (set by ingress). On other platforms, it may
be attacker-controlled. Document the deployment constraint.

```typescript
function getClientIp(request: Request): string {
  // Vercel: x-real-ip is trustworthy
  if (process.env.VERCEL) {
    return request.headers.get("x-real-ip") ?? "unknown";
  }
  // On other platforms, derive from the actual TCP connection
  // (requires a custom server or framework-specific method)
  return "unknown";
}
```

---

## The Admin & System Exemption

### Admin Bypass
Admins should bypass normal rate limits (but not abuse detection — admins can
still be compromised).

### System Source Exemption
Requests marked as `source: "system"` (e.g., Stripe IPs hitting webhooks) should
skip abuse cooldowns. Otherwise during a webhook retry storm, the Stripe IP can
accumulate enough failures to get banned, causing reconciliation failures.

```typescript
if (source === "system") {
  // Still track the signal, but don't apply cooldown
  await trackAbuseSignal({ signal, key, applyCooldown: false });
}
```

---

## Monitoring & Alerting

### Alerts to Set Up

| Metric | Threshold | Severity |
|--------|-----------|----------|
| Redis error rate > 5% over 1 min | P1 | Page on-call |
| Rate limit hit rate > 10x baseline | P2 | Slack notification |
| Auth failure rate > 10x baseline | P1 | Page on-call (possible brute force) |
| Webhook signature failures > 5/min | P1 | Page on-call (possible forgery) |
| Abuse cooldown active on >1% of users | P2 | Slack (possible false positive) |
| Subscriber rate limit hit (should never) | P2 | Slack (bug) |

### Dashboard Widgets

- Rate limit tier distribution over time
- Abuse signal rate by type
- Redis latency (p50, p99)
- Fail-open vs fail-closed decisions per hour
- Top IPs by rate limit hits
- Top users by abuse signal count

---

## Testing Rate Limits

```typescript
// tests/integration/security/rate-limit.test.ts
describe("Rate limiting", () => {
  it("blocks after tier limit exceeded", async () => {
    for (let i = 0; i < 60; i++) {
      const res = await fetch("/api/test", { headers: anonHeaders });
      expect(res.status).toBe(200);
    }
    const res = await fetch("/api/test", { headers: anonHeaders });
    expect(res.status).toBe(429);
  });

  it("short-circuits for subscribers (never hits Redis)", async () => {
    const subHeaders = await getSubscriberHeaders();
    for (let i = 0; i < 1000; i++) {
      const res = await fetch("/api/test", { headers: subHeaders });
      expect(res.status).toBe(200);
    }
  });

  it("fails closed for auth endpoints when Redis is down", async () => {
    await simulateRedisDown();
    const res = await fetch("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: "test@example.com", password: "pass" }),
    });
    expect(res.status).toBe(503);
  });

  it("fails open for regular endpoints when Redis is down", async () => {
    await simulateRedisDown();
    const res = await fetch("/api/test");
    expect(res.status).toBe(200);
  });
});
```

---

## See Also

- [FAIL-OPEN-PATTERNS.md](FAIL-OPEN-PATTERNS.md) — Catalog of fail-open bugs to avoid
- [AUTH.md](AUTH.md) — Auth-specific rate limiting requirements
- [OBSERVABILITY.md](OBSERVABILITY.md) — Monitoring and alerting details
- [COOKBOOK.md](COOKBOOK.md) — Full production code examples from jeffreys-skills.md
