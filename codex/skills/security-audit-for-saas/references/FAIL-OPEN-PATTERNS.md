# Fail-Open Patterns Catalog

Every fail-open is a DoS pivot. This catalog documents the fail-open bugs we've
found in production, organized by category. Use it as a checklist AND as a library
of attack patterns for red team exercises.

**Axiom (from [KERNEL.md](KERNEL.md)):** Every fail-open is a DoS pivot. If a
dependency fails, does the code fail-closed (deny) or fail-open (allow)? The
attacker's first move is to break the dependency, not the auth logic.

---

## Pattern 1: Rate Limiter Fails Open on Redis Outage

**Vulnerable code:**
```typescript
async function checkRateLimit(key: string): Promise<boolean> {
  try {
    const result = await redis.eval(...);
    return result.allowed;
  } catch (err) {
    // "Don't break the site on Redis failure"
    return true; // FAIL OPEN
  }
}
```

**Attack:** DoS the Upstash instance (easy if you can enumerate the endpoint) or
wait for a natural outage. Rate limiter returns `true` for every request →
unlimited brute-force on login, unlimited promo code probing, unlimited signup
spam.

**Fix:**
```typescript
async function checkRateLimit(key: string, endpoint: string): Promise<boolean> {
  try {
    const result = await redis.eval(...);
    return result.allowed;
  } catch (err) {
    // Fail behavior depends on endpoint sensitivity
    if (AUTH_ENDPOINTS.has(endpoint) || BILLING_ENDPOINTS.has(endpoint)) {
      return false; // FAIL CLOSED for sensitive endpoints
    }
    return true; // Fail open for regular API (accept risk)
  }
}
```

**Real case:** jeffreysprompts_premium rate limiter. Found via "what happens if I
DoS Redis?" question during red team exercise.

---

## Pattern 2: Subscription Check Fails Open

**Vulnerable code:**
```typescript
async function canAccessPremium(userId: string): Promise<boolean> {
  try {
    const sub = await db.query.subscriptions.findFirst({
      where: eq(subscriptions.userId, userId),
    });
    return sub?.status === "active";
  } catch (err) {
    // "Customer-first: don't lock out paying users during DB blip"
    return true; // FAIL OPEN — CATASTROPHIC
  }
}
```

**Attack:** DoS the DB or trigger a slow query that causes timeout. All users
suddenly have premium access. Cascade: premium features hit the DB harder, causing
more failures, causing more bypass.

**Fix:**
```typescript
async function canAccessPremium(userId: string): Promise<boolean> {
  try {
    const sub = await db.query.subscriptions.findFirst({
      where: eq(subscriptions.userId, userId),
    });
    return sub?.status === "active";
  } catch (err) {
    logger.error({ err, userId }, "Subscription check failed");
    return false; // FAIL CLOSED: deny access on error
  }
}
```

**Real case:** jeffreys-skills.md subscription helper. Found via grep for `catch.*return true`.

---

## Pattern 3: JWT Verification "Graceful" Fallback

**Vulnerable code:**
```typescript
async function getUserFromToken(token: string) {
  try {
    const decoded = await jwt.verify(token, publicKey);
    return getUserById(decoded.sub);
  } catch (err) {
    // "At least try to get the user ID for logging"
    const decoded = jwt.decode(token); // UNVERIFIED
    return { id: decoded?.sub, unverified: true };
  }
}
```

**Attack:** Craft a JWT with any `sub` claim, no signature. The "unverified"
fallback returns a user object. Downstream code may forget to check `unverified`
flag.

**Real case:** jeffreysprompts_premium token revocation endpoint. Unverified decode
used "so we can at least revoke expired tokens." Allowed revoking arbitrary users'
tokens.

**Fix:** Remove the fallback. If verification fails, the token is garbage. Return
null or throw. Never touch the claims.

---

## Pattern 4: Feature Flag Check Defaults to Enabled

**Vulnerable code:**
```typescript
async function isFeatureEnabled(feature: string, userId: string) {
  try {
    return await featureFlagClient.getBooleanValue(feature, userId);
  } catch (err) {
    // "Don't break UX when flag service is down"
    return true; // FAIL OPEN
  }
}
```

**Attack:** For a feature that's in beta/gated (e.g., "dangerous_operation" flag),
DoS the flag service → all users get the beta feature. If the beta feature has
bugs or higher cost, this causes incidents.

**Fix:** Default to CLOSED for gated/beta features. Default to open only for
cosmetic/optional features.

```typescript
const DEFAULT_VALUES = {
  "dangerous_operation": false, // gated, default closed
  "new_button_color": false,     // cosmetic, safe to default closed
  "legacy_feature_removal": true, // removal, default on (reverse gate)
};
```

---

## Pattern 5: CORS "Allow-All" on Error

**Vulnerable code:**
```typescript
async function handleCors(request: Request) {
  const origin = request.headers.get("origin");
  try {
    const isAllowed = await checkAllowedOrigin(origin);
    return isAllowed ? origin : null;
  } catch (err) {
    return "*"; // Fail open to "allow any origin"
  }
}
```

**Attack:** DoS the allowed-origin lookup (DB or external config). CORS falls back
to `*`, allowing any origin to make credentialed requests with cookies.

**Fix:** Fail CLOSED on CORS — return null (no origin allowed). Browsers will
block the request, user may see an error, but the credential exfiltration vector
is closed.

---

## Pattern 6: "Lockout Prevention" Auto-Reopens Account

**Vulnerable code:**
```typescript
async function checkLockout(userId: string): Promise<boolean> {
  try {
    const lockout = await db.query.lockouts.findFirst({
      where: eq(lockouts.userId, userId),
    });
    if (!lockout) return false;

    const expired = lockout.expiresAt < new Date();
    if (expired) {
      await db.delete(lockouts).where(eq(lockouts.userId, userId));
      return false;
    }
    return true;
  } catch (err) {
    // "Don't lock users out forever if DB has issues"
    return false; // FAIL OPEN
  }
}
```

**Attack:** During DB instability, all account lockouts are lifted. Attacker can
brute-force any account that was previously locked out.

**Fix:** Fail CLOSED — treat all users as locked out during DB errors. Better to
have brief UX friction than to unlock attackers.

---

## Pattern 7: CSRF "Best Effort" on Unparseable Origin

**Vulnerable code:**
```typescript
function validateCsrf(request: Request): boolean {
  const origin = request.headers.get("origin");
  if (!origin) return true; // "Some legitimate clients don't send Origin"

  try {
    const url = new URL(origin);
    return ALLOWED_ORIGINS.has(url.hostname);
  } catch (err) {
    return true; // "Best effort — don't break legitimate clients"
  }
}
```

**Attacks:**
- Send request with no `Origin` header → bypass CSRF
- Send malformed `Origin` header → bypass CSRF
- Send `Origin: null` (legitimate for sandboxed iframes) → may bypass

**Fix:** For state-changing requests (POST, PUT, DELETE, PATCH), require a valid
`Origin` or `Referer` header. If missing or malformed, REJECT.

```typescript
function validateCsrf(request: Request): boolean {
  if (!isStateChangingMethod(request.method)) return true;

  const origin = request.headers.get("origin") || request.headers.get("referer");
  if (!origin) return false; // REJECT state changes without origin

  try {
    const url = new URL(origin);
    return ALLOWED_ORIGINS.has(url.hostname);
  } catch (err) {
    return false; // REJECT malformed
  }
}
```

---

## Pattern 8: Signature Verification "Skip on Missing"

**Vulnerable code:**
```typescript
async function verifyWebhookSignature(req: Request) {
  const signature = req.headers.get("stripe-signature");
  if (!signature) {
    // "Old Stripe versions don't send this header"
    return true; // FAIL OPEN
  }
  return stripe.webhooks.constructEvent(await req.text(), signature, SECRET);
}
```

**Attack:** Send a POST to the webhook endpoint with no signature header and a
forged payload. Handler accepts it, "activates" subscription for target user.

**Fix:** Missing signature → REJECT. Stripe always sends the signature header.
"Old versions" is a myth; all current Stripe API versions send it.

---

## Pattern 9: Email Verification "Skip on Failure"

**Vulnerable code:**
```typescript
async function isEmailVerified(userId: string): Promise<boolean> {
  try {
    const user = await db.query.users.findFirst({ where: eq(users.id, userId) });
    return user?.emailVerified === true;
  } catch (err) {
    // "Don't block users during DB issues"
    return true; // FAIL OPEN
  }
}
```

**Attack:** DoS DB → all unverified users can access verified-only features.

**Fix:** Fail CLOSED.

---

## Pattern 10: Authorization "Default Allow"

**Vulnerable code:**
```typescript
function canUserEdit(user: User, resource: Resource): boolean {
  switch (resource.type) {
    case "post":
      return user.id === resource.authorId;
    case "comment":
      return user.id === resource.authorId;
    default:
      return true; // "New resource types default to editable"
  }
}
```

**Attack:** When a new resource type is added but the switch is forgotten, it
defaults to editable by anyone. Silent vulnerability.

**Fix:** Default to DENY. New resource types require explicit permission logic.

```typescript
function canUserEdit(user: User, resource: Resource): boolean {
  switch (resource.type) {
    case "post":
      return user.id === resource.authorId;
    case "comment":
      return user.id === resource.authorId;
    default:
      logger.error({ type: resource.type }, "Unknown resource type in canUserEdit");
      return false; // Default DENY
  }
}
```

---

## Pattern 11: Feature Enabled Check on `isProduction`

**Vulnerable code:**
```typescript
export async function handleDebugEndpoint(req: Request) {
  if (process.env.NODE_ENV === "production") {
    return new Response("Not available", { status: 404 });
  }
  // Debug endpoint that dumps DB, exposes secrets, etc.
  return new Response(JSON.stringify(dumpDatabase()));
}
```

**Attack:** `NODE_ENV` misconfigured in production (accidentally set to "development"
or empty) → debug endpoint becomes live.

**Fix:** Positive assertion for allowed environments, not negative for blocked.

```typescript
export async function handleDebugEndpoint(req: Request) {
  if (process.env.NODE_ENV !== "development") {
    return new Response("Not available", { status: 404 });
  }
  // ...
}
```

OR: remove debug endpoints from production builds entirely (via conditional imports).

---

## Pattern 12: "Maintenance Mode" Off By Default

**Vulnerable code:**
```typescript
async function isMaintenanceMode(): Promise<boolean> {
  try {
    const flag = await redis.get("maintenance_mode");
    return flag === "true";
  } catch (err) {
    return false; // "Don't show maintenance page if Redis is the thing that's down"
  }
}
```

**Attack:** DoS Redis → site bypasses maintenance mode checks. If you're in
maintenance to handle a security incident, you're back online during the incident.

**Fix:** Fail CLOSED on maintenance check — if you can't verify, assume maintenance
is ON. Better to show a maintenance page than to expose a known-broken system.

---

## Pattern 13: Permission Cache with Allow-on-Miss

**Vulnerable code:**
```typescript
async function hasPermission(userId: string, perm: string): Promise<boolean> {
  const cached = await redis.get(`perm:${userId}:${perm}`);
  if (cached !== null) return cached === "1";

  // Cache miss — fetch from DB
  try {
    const result = await fetchFromDb(userId, perm);
    await redis.set(`perm:${userId}:${perm}`, result ? "1" : "0", { ex: 300 });
    return result;
  } catch (err) {
    // "Don't deny on cache miss if DB is slow"
    return true; // FAIL OPEN
  }
}
```

**Attack:** DoS DB → cache misses → all permission checks default to allow.

**Fix:** Fail CLOSED. Additionally: pre-warm the cache, use a circuit breaker, or
have a stale-while-revalidate strategy that serves slightly outdated permissions
rather than no permissions.

---

## Pattern 14: "Safety" Timeout Returns Success

**Vulnerable code:**
```typescript
async function verifyCaptcha(token: string): Promise<boolean> {
  try {
    const result = await Promise.race([
      fetch(`https://captcha.example.com/verify?token=${token}`),
      new Promise((_, reject) => setTimeout(() => reject(new Error("timeout")), 5000)),
    ]);
    return (await result.json()).success;
  } catch (err) {
    // "Don't block users if CAPTCHA service is slow"
    return true; // FAIL OPEN
  }
}
```

**Attack:** DoS the CAPTCHA service (or any request that takes >5s). CAPTCHA check
skipped. Bot signup / brute force / abuse enabled.

**Fix:** Fail CLOSED. Short-lived CAPTCHA issues are acceptable UX friction.

---

## Pattern 15: Input Validation "Skip Unknown"

**Vulnerable code:**
```typescript
const updateSchema = z.object({
  name: z.string(),
  email: z.string().email(),
}).passthrough(); // "Allow extra fields for forward compatibility"

async function updateUser(req: Request) {
  const body = updateSchema.parse(await req.json());
  await db.update(users).set(body).where(eq(users.id, session.userId));
}
```

**Attack:** Send request body with extra fields: `{ name, email, isAdmin: true,
role: "owner", stripeCustomerId: "cus_victim" }`. `passthrough()` allows them.
Drizzle update spreads them into the SET clause. Mass assignment vulnerability.

**Fix:** Use `.strict()` to reject unknown fields. Or use explicit column allowlist.

```typescript
const updateSchema = z.object({
  name: z.string(),
  email: z.string().email(),
}).strict(); // Reject extra fields

// Even better: explicit allowlist
const ALLOWED_FIELDS = ["name", "email"] as const;
const filteredBody = Object.fromEntries(
  Object.entries(body).filter(([k]) => ALLOWED_FIELDS.includes(k as any))
);
```

---

## How to Audit for Fail-Opens

### Grep patterns
```bash
# Boolean returning true in catch
rg -n 'catch[^}]*return true' --type ts

# Fallback to allow
rg -n '\|\| true\b' --type ts
rg -n '\?\? true\b' --type ts

# Sensitive operations wrapped in try-catch
rg -n -A 5 'async function.*(canAccess|isAllowed|hasPermission|isAuthenticated|checkRateLimit)'

# JWT decode without verify
rg -n 'jwt\.decode\(' --type ts

# "Default to allow" comments
rg -ni 'default.*allow|fail.*open|best effort|don.t block' --type ts
```

### Questions to ask
For every `try/catch` around a security check:
1. What exception class does this catch?
2. What does it return in the catch?
3. If the return is "allow," can an attacker trigger the exception?
4. If yes: is the dependency exploitable (DoS-able)?
5. If yes: CRITICAL finding.

### Red team exercise
"DoS Day" — simulate dependency failures and observe bypass:
1. Block Upstash Redis at the network level
2. Block the database
3. Block the OAuth provider
4. Block CAPTCHA/bot detection
5. Block feature flag service
6. For each: enumerate what security checks become bypassed

---

## The Meta-Lesson

Developers write fail-open code because they optimize for **site uptime during
dependency failures**. This is the wrong optimization for security-critical paths.

**The right framing:**
- For rendering UX: fail-open is OK (show cached data, show a "might be stale" banner)
- For security decisions: fail-closed is MANDATORY (deny access, show a retry page)

The art is drawing the line correctly. Every security check is on the wrong side
of that line until proven otherwise.
