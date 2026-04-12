# Idempotency Patterns

Idempotent operations can be safely retried. Non-idempotent operations cause
double-credits, double-charges, data corruption, and billing bugs when retried.
Most SaaS systems have many non-idempotent operations that SHOULD be idempotent
but aren't.

This file covers: distributed locking, idempotency keys, request coalescing,
heartbeat-based claim takeover, and the full production patterns.

---

## Why Idempotency Matters in SaaS

Every mutating operation in a SaaS can be retried by:
- The client (on network error)
- Load balancer (on failed health check)
- Payment provider (webhook retries for 24+ hours)
- Cron reconciliation
- Manual admin intervention
- Attackers (deliberate)

If retry causes duplicate effects, you get: double-charges, double-credits,
double-emails, double-notifications, double-webhooks, double-processing.

---

## Level 1: Simple Idempotency Keys

**The pattern:** Client sends a unique key. Server remembers the key + response.
On retry, returns the cached response.

```typescript
const idempotencyKey = req.headers.get('idempotency-key');

if (idempotencyKey) {
  const existing = await db.query.idempotencyRecords.findFirst({
    where: eq(idempotencyRecords.key, idempotencyKey),
  });
  if (existing) {
    return new Response(existing.response, { status: existing.statusCode });
  }
}

// Perform operation
const result = await performOperation();

// Store for idempotent replay
if (idempotencyKey) {
  await db.insert(idempotencyRecords).values({
    key: idempotencyKey,
    response: JSON.stringify(result),
    statusCode: 200,
    expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000),
  }).onConflictDoNothing();
}

return Response.json(result);
```

**Gotchas:**
- If request body changes but key stays same → security issue (see Level 3)
- Expiry must be long enough to catch all retry attempts
- Race condition: two concurrent requests with same key can both pass the check

---

## Level 2: Tenant-Scoped Idempotency Keys

**The bug:** If User A uses key `abc` and User B also uses key `abc`, User B
might get User A's cached response.

```typescript
// VULNERABLE: global idempotency key
const key = req.headers.get('idempotency-key');

// FIXED: scope to tenant + user
function buildKey(userId: string, apiKey: string | null, orgId: string, clientKey: string): string {
  const scope = [userId, apiKey, orgId].filter(Boolean).sort().join('|');
  return `${scope}::${clientKey}`;
}
```

This ensures User A's key `abc` and User B's key `abc` are different.

---

## Level 3: Request Body Fingerprinting

**The bug:** Attacker uses the same idempotency key with different bodies to
"replay" a successful operation with different effects.

**Example attack:**
1. Legitimate request: `POST /api/transfer` with idempotency key `xyz`, body
   `{to: "alice", amount: 10}`. Success.
2. Attacker replays: `POST /api/transfer` with same key `xyz`, body
   `{to: "attacker", amount: 10}`. If the server only checks the key, it might
   cache the new body but return the old success response, or vice versa.

**The fix:** Fingerprint the body alongside the key.

```typescript
import { createHash } from 'crypto';

function fingerprintRequest(method: string, path: string, body: string): string {
  return createHash('sha256')
    .update(`${method}:${path}:${body}`)
    .digest('hex')
    .slice(0, 16);
}

async function handleRequest(req: Request) {
  const key = req.headers.get('idempotency-key');
  const body = await req.text();
  const fingerprint = fingerprintRequest(req.method, new URL(req.url).pathname, body);

  if (key) {
    const existing = await db.query.idempotencyRecords.findFirst({
      where: eq(idempotencyRecords.key, key),
    });

    if (existing) {
      if (existing.fingerprint !== fingerprint) {
        return Response.json(
          { error: 'IDEMPOTENCY_KEY_MISMATCH', message: 'Key reused with different body' },
          { status: 422 }
        );
      }
      return new Response(existing.response, { status: existing.statusCode });
    }
  }

  // ... rest of flow
}
```

---

## Level 4: In-Flight Request Coalescing

**The pattern:** If two concurrent requests arrive with the same idempotency
key, don't execute both — have the second wait on the first.

```typescript
const pendingRequests = new Map<string, Promise<Response>>();

async function handleRequest(req: Request) {
  const key = req.headers.get('idempotency-key');
  const body = await req.text();
  const fingerprint = fingerprintRequest(req.method, new URL(req.url).pathname, body);

  if (key) {
    // Check if there's a pending request with this key
    const pending = pendingRequests.get(key);
    if (pending) {
      // Wait for the first request to complete
      return await pending;
    }

    // Check DB for completed requests
    const existing = await db.query.idempotencyRecords.findFirst({
      where: eq(idempotencyRecords.key, key),
    });
    if (existing) {
      return new Response(existing.response, { status: existing.statusCode });
    }

    // Start a new request, track it
    const promise = doActualWork(req, body)
      .finally(() => {
        // Clean up after 5 minutes (in case of stuck promises)
        setTimeout(() => pendingRequests.delete(key), 5 * 60 * 1000);
      });
    pendingRequests.set(key, promise);
    return await promise;
  }

  return await doActualWork(req, body);
}
```

**Note:** This pattern has the same "in-memory state in serverless" problem as
rate limiters. In serverless, use Redis-backed coordination instead.

**Note:** Only cache 2xx and 4xx responses (stable errors). Don't cache 5xx
(transient). On 5xx, reject the pending promise so retries can happen.

---

## Level 5: Database Advisory Locks

For operations that must be serialized (like webhook processing for a specific
subscription), use Postgres advisory locks.

```typescript
async function processWebhookEvent(eventId: string) {
  return await db.transaction(async (tx) => {
    // Hash the event ID into two integers for pg_advisory_xact_lock
    const lockKey = `webhook:${eventId}`;
    await tx.execute(sql`select pg_advisory_xact_lock(hashtext(${lockKey}))`);

    // Now we hold the lock for the duration of the transaction.
    // Other workers will block here until we commit/rollback.

    // Check if already processed
    const existing = await tx.query.webhookEvents.findFirst({
      where: eq(webhookEvents.eventId, eventId),
    });
    if (existing?.processedAt) {
      return { alreadyProcessed: true };
    }

    // Process
    await actuallyProcessEvent(tx, eventId);

    // Mark processed
    await tx.update(webhookEvents)
      .set({ processedAt: new Date() })
      .where(eq(webhookEvents.eventId, eventId));

    return { processed: true };
  });
}
```

**Advantages:**
- No separate lock table
- Automatic release on transaction commit/rollback
- Fast (no disk I/O)

**Disadvantages:**
- Postgres-specific
- Can't survive transaction failures (lock released on rollback)

---

## Level 6: Claim-Based Processing with Heartbeat + Takeover

For long-running operations that can't hold a transaction open, use claim-based
processing with heartbeats.

```typescript
type EventProcessingState =
  | { state: 'new' }
  | { state: 'claimed'; workerId: string; claimedAt: Date; lastHeartbeat: Date }
  | { state: 'processing'; workerId: string; lastHeartbeat: Date }
  | { state: 'processed'; completedAt: Date };

async function claimEvent(eventId: string, workerId: string): Promise<boolean> {
  return await db.transaction(async (tx) => {
    const event = await tx.query.webhookEvents.findFirst({
      where: eq(webhookEvents.eventId, eventId),
    });

    if (!event) {
      // New event — claim it
      await tx.insert(webhookEvents).values({
        eventId,
        state: 'claimed',
        workerId,
        claimedAt: new Date(),
        lastHeartbeat: new Date(),
      });
      return true;
    }

    if (event.state === 'processed') {
      return false; // Already done
    }

    if (event.state === 'claimed' || event.state === 'processing') {
      const staleThreshold = new Date(Date.now() - 10 * 60 * 1000);
      if (event.lastHeartbeat < staleThreshold) {
        // Previous worker is stuck — take over
        await tx.update(webhookEvents)
          .set({
            workerId,
            claimedAt: new Date(),
            lastHeartbeat: new Date(),
            state: 'claimed',
          })
          .where(eq(webhookEvents.eventId, eventId));

        logger.warn({ eventId, previousWorker: event.workerId, newWorker: workerId },
          'Took over stale webhook claim');
        return true;
      }
      return false; // Active claim by another worker
    }

    return false;
  });
}

async function processWithHeartbeat(eventId: string, workerId: string) {
  // Start heartbeat
  const heartbeatInterval = setInterval(async () => {
    await db.update(webhookEvents)
      .set({ lastHeartbeat: new Date() })
      .where(and(
        eq(webhookEvents.eventId, eventId),
        eq(webhookEvents.workerId, workerId) // Only update if we still own it
      ));
  }, 30_000);

  try {
    await actuallyProcessEvent(eventId);
    await db.update(webhookEvents)
      .set({ state: 'processed', completedAt: new Date() })
      .where(eq(webhookEvents.eventId, eventId));
  } finally {
    clearInterval(heartbeatInterval);
  }
}
```

**Critical:** The heartbeat update must include `workerId` in the WHERE clause.
Otherwise, if another worker has taken over, the original worker's heartbeat
would silently overwrite the new claim.

---

## Level 7: Nested Side-Effect Idempotency

**The bug:** Even if the main webhook handler is idempotent, side effects
(emails, analytics, external API calls) might not be.

**Example:** Webhook processes subscription activation. Handler is idempotent
(checks event ID). But the handler also sends a "welcome email." If the webhook
retries (claim takeover, etc.), the email is sent twice.

**The fix:** Nested idempotency tracking for each side effect.

```typescript
async function emitSideEffectOnce(
  eventId: string,
  sideEffect: string,
  action: () => Promise<void>
): Promise<void> {
  const key = `${eventId}:${sideEffect}`;
  const result = await db.insert(sideEffectLog).values({
    key,
    emittedAt: new Date(),
  }).onConflictDoNothing().returning();

  if (result.length === 0) {
    // Already emitted
    return;
  }

  try {
    await action();
  } catch (err) {
    // Remove the record so a retry can attempt again
    await db.delete(sideEffectLog).where(eq(sideEffectLog.key, key));
    throw err;
  }
}

// Usage in webhook handler
await emitSideEffectOnce(event.id, 'welcome_email', async () => {
  await sendWelcomeEmail(user);
});

await emitSideEffectOnce(event.id, 'analytics_event', async () => {
  await posthog.capture({ event: 'subscription_created', userId: user.id });
});
```

Each side effect is tracked separately. A retry skips already-emitted side
effects but retries failed ones.

---

## Level 8: The Full Production Webhook Handler

Combining all levels into a single production pattern:

```typescript
export async function POST(req: Request) {
  // 1. Signature verification
  const body = await req.text();
  const sig = req.headers.get('stripe-signature');
  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(body, sig!, webhookSecret);
  } catch (err) {
    return new Response('Invalid signature', { status: 401 });
  }

  // 2. Account verification (prevents metadata attacks)
  if (event.account !== EXPECTED_STRIPE_ACCOUNT_ID) {
    return new Response('Wrong account', { status: 400 });
  }

  // 3. Claim the event with advisory lock + state tracking
  const workerId = `${process.env.VERCEL_REGION}-${crypto.randomUUID()}`;
  const claimed = await claimEvent(event.id, workerId);
  if (!claimed) {
    return new Response('Event already claimed or processed', { status: 200 });
  }

  // 4. Process with heartbeat
  try {
    await processWithHeartbeat(event.id, workerId, async () => {
      // 5. Idempotent per-side-effect emission
      await emitSideEffectOnce(event.id, 'update_subscription', async () => {
        await updateSubscriptionFromEvent(event);
      });

      await emitSideEffectOnce(event.id, 'send_email', async () => {
        await sendSubscriptionEmail(event);
      });

      await emitSideEffectOnce(event.id, 'analytics', async () => {
        await trackSubscriptionEvent(event);
      });
    });
  } catch (err) {
    logger.error({ err, eventId: event.id }, 'Processing failed');
    // Return 200 so Stripe doesn't retry; reconciliation cron will catch
    return new Response('Processing error', { status: 200 });
  }

  return new Response('OK', { status: 200 });
}
```

This pattern handles: forgery, wrong account, concurrent delivery, stuck
workers, and partial side-effect failures.

---

## Testing Idempotency

```typescript
describe('Webhook idempotency', () => {
  it('processes the same event twice without side effects', async () => {
    const event = makeTestEvent();
    const res1 = await sendSignedWebhook(event);
    const res2 = await sendSignedWebhook(event); // Same event

    expect(res1.status).toBe(200);
    expect(res2.status).toBe(200);

    // Verify only one side effect
    const emails = await getEmailsSent();
    expect(emails.filter(e => e.eventId === event.id).length).toBe(1);
  });

  it('handles concurrent delivery of same event', async () => {
    const event = makeTestEvent();
    const [res1, res2, res3] = await Promise.all([
      sendSignedWebhook(event),
      sendSignedWebhook(event),
      sendSignedWebhook(event),
    ]);

    // One should succeed, others should get "already claimed"
    const statuses = [res1.status, res2.status, res3.status];
    expect(statuses.filter(s => s === 200).length).toBeGreaterThanOrEqual(1);

    // Verify only one side effect
    const emails = await getEmailsSent();
    expect(emails.filter(e => e.eventId === event.id).length).toBe(1);
  });

  it('recovers from stuck worker via stale claim takeover', async () => {
    // Simulate a stuck worker
    await db.insert(webhookEvents).values({
      eventId: 'stuck_event',
      state: 'claimed',
      workerId: 'dead_worker',
      claimedAt: new Date(Date.now() - 15 * 60 * 1000),
      lastHeartbeat: new Date(Date.now() - 15 * 60 * 1000),
    });

    // New worker should take over
    const event = makeTestEvent({ id: 'stuck_event' });
    const res = await sendSignedWebhook(event);
    expect(res.status).toBe(200);
  });
});
```

---

## Idempotency Audit Checklist

### Every mutating API endpoint
- [ ] Accepts an Idempotency-Key header
- [ ] Stores key + fingerprint + response for 24h
- [ ] Returns cached response on retry with same key
- [ ] Rejects with 422 if same key + different body

### Webhook handlers
- [ ] Advisory lock or state machine to prevent concurrent processing
- [ ] Event ID deduplication (unique constraint on eventId)
- [ ] Idempotent side effects (per-side-effect tracking)
- [ ] Heartbeat + stale claim takeover for long-running processing

### Background jobs
- [ ] Jobs are idempotent (can be retried safely)
- [ ] Or: job has a unique ID + dedup table
- [ ] Retries use exponential backoff
- [ ] Max retry count with DLQ

### Testing
- [ ] Test: same request twice → same response, no duplicate effects
- [ ] Test: concurrent same requests → only one executes
- [ ] Test: stuck worker recovery
- [ ] Test: partial failure + retry (e.g., email sent but DB write failed)

---

## See Also

- [BILLING.md](BILLING.md) — webhook idempotency requirements
- [COOKBOOK.md](COOKBOOK.md) Pattern 1 — Stripe webhook handler
- [THIRD-PARTY.md](THIRD-PARTY.md) — provider-specific idempotency
- [FAIL-OPEN-PATTERNS.md](FAIL-OPEN-PATTERNS.md) — don't fail open on idempotency check errors
