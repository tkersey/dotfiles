# Infrastructure Security Checklist

Operational patterns that introduce vulnerabilities in SaaS deployments.

---

## Serverless-Specific Issues

### Rate Limiting Must Use Shared State
In-memory rate limiters DON'T WORK in serverless because each invocation may be a different instance.

```typescript
// BAD - state lost between invocations
const rateLimiter = new Map<string, number[]>();

// GOOD - shared state via Redis
import { Ratelimit } from "@upstash/ratelimit";
const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, "10 s"),
});
```

Known example: `FeedbackRateLimiter` with in-memory state had unreachable code AND didn't work across instances.

### `after()` Callback Reliability
Vercel's `after()` callback is best-effort in serverless. If the worker suspends before the callback completes, it never runs.

- [ ] Cache invalidation is synchronous (not in `after()`)
- [ ] Subscription status updates don't depend on `after()` callbacks
- [ ] Background work that MUST complete should use a queue, not `after()`

---

## Webhook Handler Resilience

### Return 200 on Errors
```typescript
// CORRECT - prevents retry storms
try {
  await processWebhookEvent(event);
} catch (error) {
  console.error('Webhook processing failed:', error);
  // Still return 200 to prevent Stripe/PayPal retry storms
  // Reconciliation cron will catch missed events
  return new Response('OK', { status: 200 });
}
```

### Dead Letter Queue (DLQ)
- [ ] Exponential backoff on retries (not fixed interval)
- [ ] Max retry count (e.g., 5 attempts)
- [ ] Alerting on DLQ growth
- [ ] Reconciliation cron as safety net
- [ ] Timestamp validation: reject events older than tolerance window

---

## Batch Processing Safety

### Dunning/Cron Jobs
- [ ] Use cursor-based pagination (not `LIMIT 5000` + sequential processing)
- [ ] `maxDuration` budget accounts for per-item processing time
- [ ] Log warning if count approaches limit
- [ ] Silent truncation detected and alerted

### Example Fix
```typescript
// BAD - 5000 items * ~100ms each = 500 seconds > maxDuration of 300s
const overdue = await db.select().from(subscriptions)
  .where(eq(status, 'past_due')).limit(5000);
for (const sub of overdue) { await sendReminder(sub); }

// GOOD - cursor-based with budget tracking
let cursor: string | null = null;
const startTime = Date.now();
const BUDGET_MS = 240_000; // 80% of maxDuration
do {
  const batch = await db.select().from(subscriptions)
    .where(and(eq(status, 'past_due'), cursor ? gt(id, cursor) : undefined))
    .orderBy(asc(id)).limit(100);
  for (const sub of batch) {
    if (Date.now() - startTime > BUDGET_MS) {
      console.warn('Dunning budget exhausted, will resume next run');
      return;
    }
    await sendReminder(sub);
  }
  cursor = batch.length ? batch[batch.length - 1].id : null;
} while (cursor);
```

---

## Command Execution Safety

### Shell Command Construction
```go
// BAD - shell injection via concatenation
exec.Command("sh", "-c", "tmux send-keys -t " + sessionName + " 'echo hello' Enter")

// GOOD - separate arguments, no shell interpretation
exec.Command("tmux", "send-keys", "-t", sessionName, "echo hello", "Enter")
```

- [ ] `exec.Command` always uses separate arguments
- [ ] No `sh -c` with string concatenation
- [ ] Session names and user inputs sanitized before use in shell commands
- [ ] No backticks in command strings (shell interprets as command substitution)

---

## File System Security

### Path Traversal Prevention
```rust
// 1. Canonicalize target path
let canonical_target = fs::canonicalize(&target)?;
// 2. Verify it's under the base directory
let rel = canonical_target.strip_prefix(&canonical_base)?;
// 3. Check for symlinks before writing
let meta = fs::symlink_metadata(&target)?;
if meta.file_type().is_symlink() {
    return Err("Refusing to write through symlink");
}
```

- [ ] Paths canonicalized before base-directory comparison
- [ ] `symlink_metadata()` checked before file writes
- [ ] Writes through symlinks refused
- [ ] Fallback path normalization for non-existent paths

---

## Monitoring & Alerting

### Security-Relevant Signals to Monitor
- [ ] Webhook signature failure rate (spike = attack)
- [ ] Auth failure rate by IP (spike = brute force)
- [ ] DLQ depth growth (increase = missed events)
- [ ] RLS policy denial rate (unexpected denials = config issue)
- [ ] Subscription state inconsistencies (reconciliation cron findings)
- [ ] Admin API key usage patterns (unusual = compromise)

### Console Error Categories
In E2E tests, monitor console for security categories:
- CSP violations (`Refused to`)
- Mixed content warnings
- CORS errors
- Cookie security warnings
