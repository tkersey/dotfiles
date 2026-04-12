# The Security Cookbook — Real Production Code

This file contains **positive examples** — real, load-bearing production patterns
from jeffreys-skills.md and other audited SaaS projects. Each snippet is
anonymized (domain names genericized) but otherwise verbatim.

Use these as:
- Templates when implementing security features
- Reference when reviewing existing code ("does ours match this?")
- Test cases ("our implementation should handle what this handles")

---

## 1. Stripe Webhook Handler (Signature + Idempotency + Abuse Tracking)

```typescript
// src/app/api/stripe/webhook/handler.ts

export async function handleStripeWebhook(request: Request) {
  // 1. Read raw body BEFORE any parsing (signature verification requires raw bytes)
  const body = await request.text();
  const signature = request.headers.get("stripe-signature");

  // 2. Missing signature → abuse signal + reject
  if (!signature) {
    await trackAbuseSignal({
      signal: "webhook_signature_failed",
      request,
      route: "/api/stripe/webhook",
      source: "system",
      metadata: { provider: "stripe", reason: "missing_signature" },
    });
    return NextResponse.json(
      { error: "SIGNATURE_INVALID", message: "Missing signature" },
      { status: 400 }
    );
  }

  // 3. Verify signature → reject with abuse signal on failure
  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
  } catch (err) {
    await trackAbuseSignal({
      signal: "webhook_signature_failed",
      request,
      route: "/api/stripe/webhook",
      source: "system",
      metadata: {
        provider: "stripe",
        reason: "invalid_signature",
        error: (err as Error).message,
      },
    });
    return NextResponse.json(
      { error: "SIGNATURE_INVALID", message: "Invalid signature" },
      { status: 401 }
    );
  }

  // 4. Idempotency: record event, return early if already processed
  const recorded = await recordWebhookEvent({
    provider: "stripe",
    eventId: event.id,
    eventType: event.type,
    payload: event,
  });
  if (!recorded.isNew) {
    return NextResponse.json({ received: true, duplicate: true });
  }

  // 5. Process — but always return 200 on processing errors
  // (prevents retry storms; reconciliation cron is the safety net)
  try {
    await processEvent(event);
    return NextResponse.json({ received: true });
  } catch (err) {
    logger.error({ err, eventId: event.id }, "Stripe webhook processing failed");
    // IMPORTANT: still return 200. The event is recorded; reconciliation will retry.
    return NextResponse.json({ received: true, processing_error: true });
  }
}
```

**Why each piece matters:**
- Raw body: JSON parsing mutates the buffer; signature no longer validates
- Abuse signal: repeated signature failures may indicate an attacker
- Idempotency: Stripe retries on any non-200 AND occasionally duplicates on success
- 200 on processing errors: prevents exponential retry storm from Stripe

---

## 2. PayPal Webhook Signature Verification (API-based)

```typescript
// src/app/api/paypal/webhook/route.ts

async function verifyPayPalWebhook(
  headers: Headers,
  event: unknown,
  webhookId: string
): Promise<boolean> {
  // Extract all 5 required PayPal headers
  const transmissionId = headers.get("paypal-transmission-id");
  const transmissionTime = headers.get("paypal-transmission-time");
  const transmissionSig = headers.get("paypal-transmission-sig");
  const certUrl = headers.get("paypal-cert-url");
  const authAlgo = headers.get("paypal-auth-algo");

  if (!transmissionId || !transmissionTime || !transmissionSig || !certUrl || !authAlgo) {
    return false; // Fail-closed on missing headers
  }

  try {
    const accessToken = await getPayPalAccessToken();
    const verifyResponse = await fetch(
      `${getPayPalBaseUrl()}/v1/notifications/verify-webhook-signature`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          transmission_id: transmissionId,
          transmission_time: transmissionTime,
          transmission_sig: transmissionSig,
          cert_url: certUrl,
          auth_algo: authAlgo,
          webhook_id: webhookId,
          webhook_event: event,
        }),
        signal: AbortSignal.timeout(10_000),
      }
    );
    if (!verifyResponse.ok) return false;
    const result = await verifyResponse.json();
    return result.verification_status === "SUCCESS";
  } catch (err) {
    logger.error({ err }, "PayPal webhook verification failed");
    return false; // Fail-closed on any error
  }
}
```

**Notes:**
- 10-second timeout prevents hanging on PayPal outages
- Fail-closed on missing headers AND on verification failure
- Reconciliation cron must handle the case where legitimate events were rejected
  during PayPal API outages

---

## 3. PayPal custom_id Validation (Subscription Hijacking Defense)

```typescript
// src/lib/paypal/validation.ts

export async function validatePayPalUserId(
  customId: string | undefined,
  payerId: string,
  subscriptionId: string
): Promise<string | undefined> {
  if (!customId) return undefined;

  // 1. Verify user exists
  const user = await db.query.users.findFirst({
    where: eq(users.id, customId),
    columns: { id: true, customerId: true },
  });
  if (!user) return undefined;

  // 2. First-time linking: user has no payment customer yet
  if (!user.customerId) return customId;

  // 3. PayPal customerId matches → allowed
  if (user.customerId === payerId) return customId;

  // 4. Cross-provider switch (Stripe → PayPal): allowed but defense-in-depth
  if (user.customerId.startsWith("cus_")) {
    // Ensure no concurrent active PayPal subscription exists
    const existingPaypalSub = await db.query.subscriptions.findFirst({
      where: and(
        eq(subscriptions.userId, customId),
        eq(subscriptions.provider, "paypal"),
        ne(subscriptions.externalId, subscriptionId)
      ),
    });
    if (existingPaypalSub && existingPaypalSub.status !== "cancelled") {
      logger.error({
        customId, payerId, subscriptionId,
        existingSubId: existingPaypalSub.id,
      }, "PayPal cross-provider switch rejected: user already has active PayPal subscription - potential hijacking");
      return undefined;
    }
    return customId;
  }

  // 5. Mismatch → potential hijack, reject + log
  logger.error({
    customId,
    payerId,
    subscriptionId,
    storedCustomerId: user.customerId,
  }, "PayPal webhook custom_id mismatch - potential subscription hijacking attempt");
  return undefined;
}
```

---

## 4. Rate Limiter with Subscriber Short-Circuit + Exponential Backoff

```typescript
// src/lib/rate-limit.ts

const RATE_LIMIT_TIERS = {
  anonymous:    { requests: 60,   window: "1 m" },
  authenticated:{ requests: 120,  window: "1 m" },
  subscriber:   { requests: 1200, window: "1 m" }, // Mostly bypassed; safety cap
  cli:          { requests: 600,  window: "1 m" },
};

const STRICT_ENDPOINT_LIMITS: Record<string, { requests: number; window: string }> = {
  "/api/v1/auth/cli-login": { requests: 600, window: "1 m" },
  "/api/stripe/create-checkout": { requests: 30, window: "1 m" },
  "/api/paypal/create-checkout": { requests: 30, window: "1 m" },
  "/api/stripe/webhook": { requests: 1_000, window: "1 m" },
  "/api/paypal/webhook": { requests: 1_000, window: "1 m" },
  "/api/auth/sso/oidc/callback": { requests: 600, window: "1 m" },
};

let consecutiveFailures = 0;
let cooldownUntil = 0;
const MAX_COOLDOWN_MS = 5 * 60 * 1000;

export async function checkRateLimit(
  request: Request,
  tier: Tier,
  endpoint: string
): Promise<RateLimitResult> {
  // CRITICAL: subscribers and admins short-circuit BEFORE Redis
  if (tier === "subscriber" || tier === "admin") {
    return { allowed: true, tier, remaining: Infinity };
  }

  // Check cooldown from prior failures
  if (cooldownUntil > Date.now()) {
    return handleRedisUnavailable(endpoint);
  }

  const redis = getRedis();
  if (!redis) {
    return handleRedisUnavailable(endpoint);
  }

  try {
    const config = STRICT_ENDPOINT_LIMITS[endpoint] ?? RATE_LIMIT_TIERS[tier];
    const limiter = new Ratelimit({
      redis,
      limiter: Ratelimit.slidingWindow(config.requests, config.window),
    });
    const result = await limiter.limit(`${tier}:${endpoint}`);
    handleRedisSuccess();
    return {
      allowed: result.success,
      tier,
      remaining: result.remaining,
      reset: result.reset,
    };
  } catch (err) {
    handleRedisFailure();
    logger.error({ err, endpoint }, "Rate limit check failed");
    return handleRedisUnavailable(endpoint);
  }
}

function handleRedisFailure() {
  consecutiveFailures++;
  const cooldown = Math.min(1000 * Math.pow(2, consecutiveFailures - 1), MAX_COOLDOWN_MS);
  cooldownUntil = Date.now() + cooldown;
}

function handleRedisSuccess() {
  consecutiveFailures = 0;
  cooldownUntil = 0;
}

function handleRedisUnavailable(endpoint: string): RateLimitResult {
  // Fail-closed for auth and billing; fail-open for regular API
  const FAIL_CLOSED_PATTERNS = [
    /^\/api\/auth\//,
    /^\/api\/.*\/checkout/,
    /^\/api\/.*\/webhook/,
  ];
  const shouldFailClosed = FAIL_CLOSED_PATTERNS.some(p => p.test(endpoint));

  return {
    allowed: !shouldFailClosed,
    tier: "unknown",
    remaining: 0,
    fallback: true,
  };
}
```

---

## 5. CSRF Validation with Defense in Depth

```typescript
// src/lib/csrf.ts

const WEBHOOK_PATHS = [
  "/api/stripe/webhook",
  "/api/paypal/webhook",
  "/api/webhooks/github",
];

export async function validateCsrf(request: Request): Promise<CsrfResult> {
  // Only check state-changing methods
  if (!["POST", "PUT", "PATCH", "DELETE"].includes(request.method)) {
    return { valid: true, reason: "Safe method" };
  }

  // Webhook endpoints are exempt — they use signature verification
  const url = new URL(request.url);
  if (WEBHOOK_PATHS.some(path => url.pathname.startsWith(path))) {
    return { valid: true, reason: "Webhook endpoint" };
  }

  // CRITICAL: only exempt CLI tokens if there's NO session cookie
  // Otherwise attacker could combine their CLI token with victim's session
  const authHeader = request.headers.get("authorization");
  const apiKey = request.headers.get("x-api-key");
  const sessionCookie = extractSupabaseSessionCookie(request.headers.get("cookie"));
  const hasCookieUser = Boolean(sessionCookie);
  const hasCliToken = isCliTokenValue(authHeader) || isCliTokenValue(apiKey);

  if (hasCliToken && !hasCookieUser) {
    return { valid: true, reason: "CLI token present (no cookie session)" };
  }

  // Validate Origin/Referer against allow-list
  const origin = request.headers.get("origin") || request.headers.get("referer");
  if (!origin) {
    return { valid: false, reason: "Missing Origin/Referer on state-changing request" };
  }

  try {
    const url = new URL(origin);
    const allowedHosts = getAllowedHosts(); // Includes www. variants
    if (!allowedHosts.has(url.hostname)) {
      return { valid: false, reason: `Origin ${url.hostname} not in allow-list` };
    }
  } catch {
    return { valid: false, reason: "Malformed Origin header" };
  }

  return { valid: true, reason: "Origin validated" };
}
```

---

## 6. Timing-Safe Comparison (Hash-Both-Sides Pattern)

```typescript
// src/lib/crypto.ts

import { createHash, timingSafeEqual } from "crypto";

/**
 * Compare two strings in constant time.
 *
 * Uses hash-both-sides so the comparison time does not leak information
 * about the input length.
 */
export function timingSafeCompare(a: string, b: string): boolean {
  const hashA = createHash("sha256").update(a).digest();
  const hashB = createHash("sha256").update(b).digest();
  return timingSafeEqual(hashA, hashB);
}

/**
 * Direct buffer comparison with explicit length guard.
 * Use when the inputs are already known to be fixed-length (e.g., HMAC signatures).
 */
export function verifySignature(
  payload: string,
  signature: string,
  secret: string
): boolean {
  const expectedPrefix = "sha256=";
  if (!signature.startsWith(expectedPrefix)) return false;

  const providedSignature = signature.slice(expectedPrefix.length);
  const expectedSignature = generateSignature(payload, secret);

  const providedBuf = Buffer.from(providedSignature, "utf8");
  const expectedBuf = Buffer.from(expectedSignature, "utf8");

  // Length check BEFORE timingSafeEqual (it throws on length mismatch)
  if (providedBuf.length !== expectedBuf.length) return false;
  return timingSafeEqual(providedBuf, expectedBuf);
}
```

---

## 7. Comprehensive RLS Policy Pattern

```sql
-- supabase/migrations/20260201000001_comprehensive_rls_fix.sql

-- PART 1: Enable RLS on every table (idempotent)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;
-- ... every table

-- PART 2: Drop existing policies for a clean slate
DROP POLICY IF EXISTS users_select_own ON public.users;
-- ... every policy

-- PART 3: Recreate with consistent naming

-- Users: own-row access + service role bypass
CREATE POLICY users_select_own ON public.users
  FOR SELECT TO authenticated
  USING (auth.uid() = id);

CREATE POLICY users_update_own ON public.users
  FOR UPDATE TO authenticated
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

CREATE POLICY users_all_service ON public.users
  FOR ALL TO service_role
  USING (true);

-- Subscription-gated content
CREATE POLICY skills_select_subscriber ON public.skills
  FOR SELECT TO authenticated
  USING (
    is_jeffreys = true
    AND EXISTS (
      SELECT 1 FROM public.users
      WHERE id = auth.uid()
      AND subscription_status = 'active'
    )
  );

-- Insert with ownership constraint
CREATE POLICY skills_insert_own ON public.skills
  FOR INSERT TO authenticated
  WITH CHECK (owner_id = auth.uid());

-- Nested access via parent
CREATE POLICY skill_versions_select ON public.skill_versions
  FOR SELECT TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM public.skills s
      WHERE s.id = skill_id
      AND (
        s.is_public = true
        OR s.owner_id = auth.uid()
        OR (s.is_jeffreys = true AND EXISTS (
          SELECT 1 FROM public.users u
          WHERE u.id = auth.uid() AND u.subscription_status = 'active'
        ))
      )
    )
  );

-- Service-role-only tables (payment events)
CREATE POLICY payment_events_all_service ON public.payment_events
  FOR ALL TO service_role
  USING (true);

-- PART 4: Lock down anon role completely
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon;
```

---

## 8. Abuse Detection Signals with Atomic Redis Operations

```typescript
// src/lib/services/abuse-detection.ts

export type AbuseSignal =
  | "download_denied"
  | "webhook_signature_failed"
  | "upload_rejected"
  | "auth_failed"
  | "sequential_enumeration"
  | "scraping_pattern";

const ABUSE_THRESHOLDS: Record<AbuseSignal, { max: number; windowSeconds: number; severe: boolean }> = {
  download_denied:          { max: 30,  windowSeconds: 600,  severe: false },
  webhook_signature_failed: { max: 10,  windowSeconds: 600,  severe: true  },
  upload_rejected:          { max: 15,  windowSeconds: 3600, severe: false },
  auth_failed:              { max: 20,  windowSeconds: 300,  severe: true  },
  sequential_enumeration:   { max: 50,  windowSeconds: 60,   severe: true  },
  scraping_pattern:         { max: 150, windowSeconds: 300,  severe: false },
};

export async function trackAbuseSignal(params: {
  signal: AbuseSignal;
  request: Request;
  route: string;
  source: "user" | "system" | "admin";
  actorId?: string;
  metadata?: Record<string, unknown>;
}): Promise<void> {
  // Never throttle admins or system source (e.g., Stripe/PayPal IPs)
  if (params.source === "admin" || params.source === "system") {
    await recordEvent(params); // Still record for forensics
    return;
  }

  const key = buildAbuseKey(params);
  const threshold = ABUSE_THRESHOLDS[params.signal];
  const redis = getRedis();

  if (!redis) {
    await recordEvent(params);
    return;
  }

  // Atomic INCR + EXPIRE via Lua
  const script = `
    local c = redis.call('incr', KEYS[1])
    local t = redis.call('ttl', KEYS[1])
    if t == -1 then
      redis.call('expire', KEYS[1], ARGV[1])
    end
    return c
  `;
  const count = (await redis.eval(script, [key], [threshold.windowSeconds])) as number;

  // Record event (non-blocking via after())
  after(async () => {
    await recordEvent({ ...params, count });
  });

  // If over threshold, apply cooldown + alert once per window (SET NX EX)
  if (count > threshold.max) {
    const cooldownKey = `abuse:cooldown:${params.actorId || getIp(params.request)}`;
    await redis.set(cooldownKey, "1", { ex: threshold.windowSeconds });

    if (threshold.severe) {
      // Dedupe alerts: only fire once per window per actor
      const alertKey = `abuse:alert:${params.signal}:${params.actorId || getIp(params.request)}`;
      const alertResult = await redis.set(alertKey, "1", {
        ex: threshold.windowSeconds,
        nx: true,
      });
      if (alertResult) {
        await sendSlackAlert({ ...params, count });
      }
    }
  }
}
```

---

## 9. SSRF-Safe Webhook URL Validation

```typescript
// src/lib/webhooks/custom.ts

const BLOCKED_HOSTNAMES = new Set([
  "localhost",
  "metadata.google.internal",
]);

const BLOCKED_SUFFIXES = [".local", ".internal", ".corp", ".lan", ".home", ".intranet"];

function isPrivateIpLiteral(addr: string): boolean {
  const { address, kind } = parseIpAddress(addr);
  if (!address) return true; // Fail closed on unparseable

  if (kind === 4) {
    const [a, b] = address.split(".").map(Number);
    return (
      a === 0 || a === 10 || a === 127 ||
      (a === 100 && b >= 64 && b <= 127) || // CGNAT
      (a === 169 && b === 254) ||           // link-local / AWS metadata
      (a === 172 && b >= 16 && b <= 31) ||
      (a === 192 && b === 168) ||
      (a === 198 && (b === 18 || b === 19))  // benchmarking
    );
  }
  if (kind === 6) {
    return (
      address === "::1" ||                    // loopback
      address.startsWith("fc") ||             // ULA
      address.startsWith("fd") ||             // ULA
      address.startsWith("fe80:")             // link-local
    );
  }
  return true;
}

export async function validateWebhookDeliveryTarget(url: URL): Promise<ValidationResult> {
  // 1. HTTPS only
  if (url.protocol !== "https:") {
    return { blocked: true, reason: "HTTPS required" };
  }

  // 2. Hostname blocklist
  const hostname = url.hostname.toLowerCase();
  if (BLOCKED_HOSTNAMES.has(hostname)) {
    return { blocked: true, reason: "Hostname blocked" };
  }
  if (BLOCKED_SUFFIXES.some(s => hostname.endsWith(s))) {
    return { blocked: true, reason: "Hostname suffix blocked" };
  }

  // 3. If hostname is an IP literal, check it directly
  if (isIpAddress(hostname)) {
    if (isPrivateIpLiteral(hostname)) {
      return { blocked: true, reason: "Private IP literal" };
    }
  }

  // 4. DNS-aware validation (defeats DNS rebinding)
  try {
    const { lookup } = await import("dns/promises");
    const addresses = await lookup(hostname, { all: true, verbatim: true });
    if (addresses.length === 0) {
      return { blocked: true, reason: "Hostname did not resolve", retryable: true };
    }
    if (addresses.some(({ address }) => isPrivateIpLiteral(address))) {
      return { blocked: true, reason: "Resolved to private IP", retryable: false };
    }
  } catch {
    return { blocked: true, reason: "DNS lookup failed", retryable: true };
  }

  return { blocked: false };
}

// Runtime fetcher also uses redirect: "manual" to block 3xx to private IPs
export async function deliverWebhook(url: URL, payload: unknown): Promise<Response> {
  const validation = await validateWebhookDeliveryTarget(url);
  if (validation.blocked) throw new Error(`Blocked: ${validation.reason}`);

  return fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    redirect: "manual", // Block redirects (could be to private IP)
    signal: AbortSignal.timeout(10_000),
  });
}
```

---

## 10. env.ts Centralized Secret Access

```typescript
// src/env.ts

import { createEnv } from "@t3-oss/env-nextjs";
import { z } from "zod";

// Obfuscated prefix constants to avoid secret-scanner false positives
const STRIPE_SECRET_PREFIX = "sk" + "_";
const STRIPE_WEBHOOK_PREFIX = "whs" + "ec_";
const STRIPE_PUBLISHABLE_PREFIX = "pk" + "_";

export const env = createEnv({
  server: {
    DATABASE_URL: z.string().url(),
    JWT_SECRET: z.string().min(32),
    STRIPE_SECRET_KEY: z.string().startsWith(STRIPE_SECRET_PREFIX).trim(),
    STRIPE_WEBHOOK_SECRET: z.string().startsWith(STRIPE_WEBHOOK_PREFIX).trim(),
    PAYPAL_CLIENT_ID: z.string().min(1),
    PAYPAL_CLIENT_SECRET: z.string().min(1),
    PAYPAL_WEBHOOK_ID: z.string().min(1),
    SUPABASE_SERVICE_ROLE_KEY: z.string().min(1),
    UPSTASH_REDIS_URL: z.string().url().optional(),
    UPSTASH_REDIS_TOKEN: z.string().optional(),
    // CRITICAL: production requires cron secret
    CRON_SECRET: z.string().min(16).optional().refine(
      (value) => process.env.NODE_ENV !== "production" || Boolean(value),
      "CRON_SECRET is required in production"
    ),
    // E2E test domain guard
    E2E_ALLOW_TEST_AUTH_IN_PRODUCTION: z.enum(["true", "false"]).optional()
      .refine(
        (value) => process.env.NODE_ENV !== "production" || value !== "true",
        "E2E_ALLOW_TEST_AUTH_IN_PRODUCTION must not be 'true' in production"
      ),
  },
  client: {
    NEXT_PUBLIC_SUPABASE_URL: z.string().url(),
    NEXT_PUBLIC_SUPABASE_ANON_KEY: z.string().min(1),
    NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: z.string().startsWith(STRIPE_PUBLISHABLE_PREFIX),
    NEXT_PUBLIC_APP_URL: z.string().url(),
  },
  emptyStringAsUndefined: true,
  skipValidation: !!process.env.SKIP_ENV_VALIDATION,
});

// IMPORTANT: Never read process.env directly except in this file.
// All code must import from @/env instead.
```

---

## 11. TOCTOU-Safe Subscription Update with Advisory Lock

```typescript
// src/lib/webhooks/inbound.ts

export async function updateSubscriptionStatus(params: {
  provider: "stripe" | "paypal";
  externalSubscriptionId: string;
  status: SubscriptionStatus;
  customerId: string;
  currentPeriodEnd: Date;
  eventTimestamp: Date;
}) {
  // Refuse to write "none" status (would create corrupt state)
  if (params.status === "none") {
    logger.error({ params }, "Refusing to update subscription to 'none' status");
    return { rejected: true, reason: "invalid_status" };
  }

  return await db.transaction(async (tx) => {
    // Advisory lock per external subscription — serializes concurrent updates
    const lockKey = `${params.provider}:${params.externalSubscriptionId}`;
    await tx.execute(sql`select pg_advisory_xact_lock(hashtext(${lockKey}))`);

    // Read existing state INSIDE the lock
    const existing = await tx.query.subscriptions.findFirst({
      where: and(
        eq(subscriptions.provider, params.provider),
        eq(subscriptions.externalId, params.externalSubscriptionId)
      ),
    });

    // Cancelled → past_due guard: cancelled subs don't resurrect
    if (existing?.status === "cancelled" && params.status === "past_due") {
      return { rejected: true, reason: "cancelled_cannot_become_past_due" };
    }

    // Out-of-order webhook guard: compare timestamps
    if (existing?.lastEventAt && existing.lastEventAt > params.eventTimestamp) {
      return { rejected: true, reason: "out_of_order_event" };
    }

    // Email-based user lookup with customerId cross-reference
    // (prevents hijacking via stale email matches)
    const user = await findUserByCustomerId(tx, params.customerId, params.provider);
    if (!user) {
      return { rejected: true, reason: "no_user_found" };
    }

    // Upsert
    await tx.insert(subscriptions).values({
      userId: user.id,
      provider: params.provider,
      externalId: params.externalSubscriptionId,
      status: params.status,
      customerId: params.customerId,
      currentPeriodEnd: params.currentPeriodEnd,
      lastEventAt: params.eventTimestamp,
    }).onConflictDoUpdate({
      target: [subscriptions.provider, subscriptions.externalId],
      set: {
        status: params.status,
        currentPeriodEnd: params.currentPeriodEnd,
        lastEventAt: params.eventTimestamp,
        updatedAt: new Date(),
      },
    });

    // Recalculate aggregate status across ALL user subscriptions
    const bestStatus = await computeBestStatusForUser(tx, user.id);
    await tx.update(users)
      .set({ subscriptionStatus: bestStatus })
      .where(eq(users.id, user.id));

    return { rejected: false, previousStatus: existing?.status, currentStatus: params.status };
  });
}
```

---

## 12. RBAC with Numeric Role Hierarchy

```typescript
// src/lib/auth/rbac.ts

type OrgRole = "owner" | "admin" | "member" | "viewer";
type OrgPermission = "manage_billing" | "invite_members" | "remove_members" | /* ... */;

const ROLE_HIERARCHY: Record<OrgRole, number> = {
  owner: 4,
  admin: 3,
  member: 2,
  viewer: 1,
};

// CRITICAL: billing requires OWNER, not admin
const PERMISSION_MATRIX: Record<OrgPermission, OrgRole> = {
  manage_billing: "owner",     // ← CRITICAL: not "admin"
  invite_members: "admin",
  remove_members: "admin",
  change_roles: "admin",
  configure_sso: "admin",
  view_all_telemetry: "admin",
  view_own_telemetry: "member",
  push_to_library: "member",
  download_team_skills: "viewer",
  download_premium_skills: "member",
  access_team_admin: "admin",
};

export function hasMinRole(actual: OrgRole, required: OrgRole): boolean {
  return ROLE_HIERARCHY[actual] >= ROLE_HIERARCHY[required];
}

export function canChangeRole(
  actorRole: OrgRole,
  targetRole: OrgRole,
  newRole: OrgRole
): boolean {
  // Rule 1: Nobody modifies owner
  if (targetRole === "owner") return false;
  // Rule 2: Nobody creates an owner via role change (must be via ownership transfer)
  if (newRole === "owner") return false;
  // Rule 3: Actor must have higher privilege than target's current role
  if (ROLE_HIERARCHY[actorRole] <= ROLE_HIERARCHY[targetRole]) return false;
  // Rule 4: Actor must have higher privilege than target's new role
  if (ROLE_HIERARCHY[actorRole] <= ROLE_HIERARCHY[newRole]) return false;
  // Rule 5: Actor must have permission to change roles at all
  if (!hasMinRole(actorRole, PERMISSION_MATRIX["change_roles"])) return false;
  return true;
}

// Usage inside transaction for TOCTOU safety:
export async function changeRole(params: {
  orgId: string;
  actorUserId: string;
  targetUserId: string;
  newRole: OrgRole;
}) {
  return await db.transaction(async (tx) => {
    // Lock both rows
    const [actor] = await tx.select().from(organizationMembers)
      .where(and(eq(orgId, params.orgId), eq(userId, params.actorUserId)))
      .for("update");
    const [target] = await tx.select().from(organizationMembers)
      .where(and(eq(orgId, params.orgId), eq(userId, params.targetUserId)))
      .for("update");

    if (!actor || !target) throw new RBACError("NOT_FOUND");
    if (!canChangeRole(actor.role, target.role, params.newRole)) {
      throw new RBACError("FORBIDDEN");
    }

    await tx.update(organizationMembers)
      .set({ role: params.newRole })
      .where(and(
        eq(organizationMembers.orgId, params.orgId),
        eq(organizationMembers.userId, params.targetUserId)
      ));
  });
}
```

---

## 13. SSO Provisioning with Seat Lock

```typescript
// src/lib/auth/sso-provisioning.ts

export async function provisionSsoUser(params: {
  orgId: string;
  ssoUserId: string;
  email: string;
}) {
  return await db.transaction(async (tx) => {
    // Lock org row to prevent concurrent seat bypass
    const [lockedOrg] = await tx.select({
      id: organizations.id,
      maxSeats: organizations.maxSeats,
      subscriptionStatus: organizations.subscriptionStatus,
    })
    .from(organizations)
    .where(eq(organizations.id, params.orgId))
    .for("update");

    if (!lockedOrg) return { error: "org_not_found" };
    if (lockedOrg.subscriptionStatus !== "active") return { error: "subscription_inactive" };

    // Count seats INSIDE the locked transaction
    const memberCount = await tx.$count(organizationMembers, eq(orgId, params.orgId));
    const pendingInvites = await tx.$count(organizationInvites, and(
      eq(organizationInvites.orgId, params.orgId),
      eq(organizationInvites.status, "pending")
    ));
    const billableSeats = memberCount + pendingInvites;

    if (billableSeats >= lockedOrg.maxSeats) {
      return { error: "seat_limit_reached" };
    }

    // Upsert user
    const user = await tx.insert(users).values({
      email: params.email,
      ssoSubject: params.ssoUserId,
    }).onConflictDoUpdate({
      target: users.email,
      set: { ssoSubject: params.ssoUserId, updatedAt: new Date() },
    }).returning();

    // Insert membership (idempotent)
    await tx.insert(organizationMembers).values({
      orgId: params.orgId,
      userId: user[0].id,
      role: "member",
    }).onConflictDoNothing();

    return { success: true };
  });
}
```

---

## Usage Guidance

- **Don't copy-paste blindly.** Each pattern has assumptions (schema, tools, environment).
  Read the full reference file for the corresponding domain before adapting.
- **Verify the pattern still reflects current best practice.** Security moves; some of
  these patterns will age. Cross-check against upstream library docs.
- **Use as conversation starters, not as final answers.** When a team says "our auth
  is fine," compare their code against Pattern 5 line-by-line. Any divergence is a
  discussion.
