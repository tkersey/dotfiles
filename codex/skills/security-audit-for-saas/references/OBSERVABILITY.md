# Observability for Security

What you can't see, you can't defend. This file covers monitoring, alerting, and
observability specifically for SaaS security — what to log, what to measure, and
what to alert on.

---

## The Security Observability Pyramid

```
┌─────────────────┐
│   Alerts        │  Page on-call (P0), notify team (P1-P2)
├─────────────────┤
│   Dashboards    │  Daily monitoring, incident response
├─────────────────┤
│   Metrics       │  Counters, gauges, histograms
├─────────────────┤
│   Logs          │  Structured events with context
├─────────────────┤
│   Traces        │  Distributed request flows
└─────────────────┘
```

---

## Metrics to Track

### Authentication
| Metric | Type | Purpose |
|--------|------|---------|
| `auth_login_success_total` | Counter | Baseline activity |
| `auth_login_failure_total` | Counter | Brute force detection |
| `auth_login_latency_seconds` | Histogram | Timing oracle detection |
| `auth_session_refresh_total` | Counter | Refresh abuse detection |
| `auth_token_revoke_total` | Counter | Revocation activity |
| `auth_2fa_fail_total` | Counter | 2FA attack detection |

### Authorization
| Metric | Type | Purpose |
|--------|------|---------|
| `authz_denied_total{resource, action}` | Counter | Unexpected denials = bugs |
| `authz_role_change_total{from_role, to_role}` | Counter | Escalation tracking |
| `authz_admin_action_total{action}` | Counter | Admin activity monitoring |

### Rate Limiting
| Metric | Type | Purpose |
|--------|------|---------|
| `rate_limit_hit_total{tier, endpoint}` | Counter | Abuse or legitimate traffic |
| `rate_limit_redis_error_total` | Counter | Fail-open detection |
| `rate_limit_cooldown_active_gauge` | Gauge | Number of cooldowns in effect |

### Webhook
| Metric | Type | Purpose |
|--------|------|---------|
| `webhook_received_total{provider, type}` | Counter | Baseline |
| `webhook_signature_fail_total{provider}` | Counter | Forgery attempts |
| `webhook_duplicate_total{provider}` | Counter | Idempotency verification |
| `webhook_processing_duration_seconds` | Histogram | Performance |
| `webhook_processing_error_total{provider, type}` | Counter | Reconciliation needed |

### Billing
| Metric | Type | Purpose |
|--------|------|---------|
| `subscription_created_total` | Counter | Revenue tracking |
| `subscription_canceled_total` | Counter | Churn |
| `subscription_status_change_total{from, to}` | Counter | Lifecycle visibility |
| `checkout_initiated_total` | Counter | Funnel |
| `checkout_abandoned_total` | Counter | Funnel |

### Abuse Detection
| Metric | Type | Purpose |
|--------|------|---------|
| `abuse_signal_total{signal, source}` | Counter | Attack intensity |
| `abuse_cooldown_total{signal}` | Counter | Actor bans |
| `rls_denial_total{table}` | Counter | RLS violations |

---

## Alerting Rules

### P0 (Page On-Call)

```yaml
# Prometheus-style rules

- alert: AuthFailureSpike
  expr: rate(auth_login_failure_total[5m]) > 10 * avg_over_time(rate(auth_login_failure_total[5m])[1d])
  for: 2m
  severity: p0
  description: "Auth failure rate >10x baseline — possible brute force"

- alert: WebhookSignatureFailure
  expr: rate(webhook_signature_fail_total[5m]) > 5
  for: 1m
  severity: p0
  description: "Webhook signature failures spiking — possible forgery attack"

- alert: RedisDown
  expr: up{job="redis"} == 0
  for: 1m
  severity: p0
  description: "Redis unavailable — rate limiting degraded, check fail-closed behavior"

- alert: SubscriptionBypassSuspected
  expr: increase(authz_denied_total{resource="premium"}[5m]) > 100
  for: 2m
  severity: p0
  description: "Spike in premium access denials — possible active attack"

- alert: RLSDenialSpike
  expr: rate(rls_denial_total[5m]) > 5 * avg_over_time(rate(rls_denial_total[5m])[1d])
  for: 5m
  severity: p0
  description: "RLS denials spiking — possible cross-tenant attack"
```

### P1 (Notify Team)

```yaml
- alert: UnusualAdminActivity
  expr: increase(authz_admin_action_total[1h]) > 50
  for: 10m
  severity: p1
  description: "Admin activity much higher than baseline"

- alert: SubscriberRateLimitHit
  expr: rate(rate_limit_hit_total{tier="subscriber"}[5m]) > 0
  for: 1m
  severity: p1
  description: "Subscribers should never hit rate limits — bug or attack"

- alert: AbuseCooldownHighVolume
  expr: rate_limit_cooldown_active_gauge > 0.01 * active_users_gauge
  for: 10m
  severity: p1
  description: ">1% of users in abuse cooldown — possible false positive or attack"

- alert: WebhookProcessingSlow
  expr: histogram_quantile(0.99, rate(webhook_processing_duration_seconds_bucket[5m])) > 10
  for: 10m
  severity: p1
  description: "Webhook p99 >10s — reconciliation lag, possible attack load"

- alert: OAuthProviderDown
  expr: up{job="oauth_provider"} == 0
  for: 2m
  severity: p1
  description: "OAuth provider unreachable — verify fail-closed behavior"
```

### P2 (Slack Notification)

```yaml
- alert: NewAdminUser
  expr: increase(authz_role_change_total{to_role="admin"}[1h]) > 0
  severity: p2
  description: "New admin role assigned"

- alert: StaleSession
  expr: session_age_gauge > 86400 * 30
  severity: p2
  description: "Session older than 30 days"

- alert: DependencyVulnerability
  expr: dependency_vuln_high_count > 0
  severity: p2
  description: "New high-severity dependency vulnerability"
```

---

## Dashboards

### The Security Overview Dashboard
Top panel: **Traffic overview**
- Requests per second (total, by tier)
- Auth success/failure rate
- Webhook received rate (Stripe, PayPal)

Middle panel: **Security signals**
- Abuse signal rate by type
- Rate limit hit rate by tier
- RLS denial rate
- CSRF rejection rate

Bottom panel: **Incidents**
- Active P0/P1 alerts
- Recent admin actions
- Recent role changes
- Recent subscription state changes

### The Billing Security Dashboard
- Webhook signature failure rate by provider
- Webhook duplicate rate (idempotency check)
- Checkout initiation vs completion rate
- Subscription state distribution
- Refund rate

### The Auth Dashboard
- Login success/failure ratio
- Login latency distribution (detect timing oracles)
- Session lifetime distribution
- Token refresh rate
- 2FA usage rate

### The Abuse Detection Dashboard
- Signal rate heatmap (signal type × time)
- Top 10 IPs by abuse signal count
- Top 10 users by abuse signal count
- Cooldown count over time

---

## Structured Logging

Every log event must have these fields:

```typescript
logger.info({
  timestamp: new Date().toISOString(),
  level: "info",
  event: "user_login",
  request_id: req.headers.get("x-request-id"),
  user_id: user.id,
  ip: getClientIp(req),
  user_agent: req.headers.get("user-agent"),
  duration_ms: Date.now() - startTime,
  result: "success",
  // Domain-specific fields:
  tier: user.tier,
  mfa_used: true,
}, "User logged in");
```

### Log Levels

- **DEBUG:** Verbose, only in dev / on demand
- **INFO:** Normal business events (login, checkout, etc.)
- **WARN:** Unexpected but handled (rate limit hit, validation failed)
- **ERROR:** Something is broken (signature verification failed, DB error)
- **FATAL:** Service cannot continue

### What to Log
- Every authentication event
- Every authorization decision
- Every webhook received (before and after processing)
- Every rate limit decision
- Every admin action
- Every abuse signal
- Every secret access (by the secret manager)

### What NOT to Log
- Passwords (even hashed)
- Full credit card numbers
- JWT tokens (log the `sub` claim only)
- Session tokens
- API keys (log prefix only)
- Request bodies with PII

### Log Sampling for High-Volume Events

For events that fire thousands of times per second:
```typescript
// Sample 1% of successful auth events, 100% of failures
if (result === "success" && Math.random() > 0.01) return;
logger.info({ /* ... */ });
```

---

## Distributed Tracing

Each user-facing request should have a trace that spans:
- Proxy/middleware
- Route handler
- DB queries
- External API calls
- Webhook dispatch

### Trace Fields

```typescript
import { trace } from "@opentelemetry/api";

const span = trace.getActiveSpan();
span?.setAttributes({
  "user.id": userId,
  "tenant.id": orgId,
  "auth.tier": tier,
  "billing.status": subscriptionStatus,
});
```

### Security-Specific Spans
- `auth.verify` (JWT verification, with duration)
- `authz.check` (permission check, with resource)
- `csrf.validate` (CSRF check)
- `rate_limit.check` (rate limit decision)
- `webhook.verify_signature` (signature verification)
- `db.query` (DB query, with query hash)

---

## Incident Detection Heuristics

Beyond threshold-based alerts, look for behavioral patterns:

### Pattern: "Slow and Low" Brute Force
- Multiple accounts with 1 login attempt each
- Same IP or ASN
- Over hours, not minutes

Query:
```promql
count by (ip_address) (
  rate(auth_login_failure_total[1h]) > 0
) > 50
```

### Pattern: "Credential Stuffing"
- Many different usernames
- Single IP
- High ratio of failures

### Pattern: "Account Takeover"
- Password change shortly after new device login
- Email change shortly after password change
- Email + password change within 5 minutes

### Pattern: "Subscription Bypass"
- Premium feature access for user with no active subscription
- Sudden increase in premium feature access by free users
- User's `subscription_status` differs between cache and DB

### Pattern: "Admin Compromise"
- Admin login from new country
- Admin access outside business hours
- Multiple admin actions in rapid succession
- Admin accessing data they don't usually access

---

## The Honeypot Pattern

Plant tripwires that no legitimate user should trigger:

### Database Honeypots
```sql
-- Insert fake "honeypot" row that no real query should return
INSERT INTO users (email, is_honeypot) VALUES ('honeypot@internal.example.com', true);

-- Alert if anything reads it
CREATE TRIGGER honeypot_alert AFTER SELECT ON users
  WHEN NEW.is_honeypot = true
  FOR EACH ROW EXECUTE FUNCTION notify_security_team();
```

### Endpoint Honeypots
```typescript
// Endpoint not in docs, not linked from anywhere
export async function GET(req: Request) {
  // Anyone who calls this is an attacker probing
  await notifySecurityTeam({
    event: "honeypot_hit",
    ip: getClientIp(req),
    path: "/api/admin/internal-debug",
    user_agent: req.headers.get("user-agent"),
  });
  return new Response("Not found", { status: 404 });
}
```

### Secret Honeypots
- Plant a "decoy" API key in the codebase (looks real, doesn't work)
- Anyone who uses it is exfiltrating secrets
- Any failed auth with this key triggers an alert

---

## Audit Checklist

### Metrics
- [ ] Auth metrics tracked (success, failure, latency)
- [ ] Authz metrics tracked (denials, role changes)
- [ ] Rate limit metrics tracked
- [ ] Webhook metrics tracked
- [ ] Billing metrics tracked
- [ ] Abuse detection metrics tracked

### Alerts
- [ ] P0 alerts for brute force, webhook forgery, Redis down
- [ ] P1 alerts for unusual admin activity, subscriber rate limits
- [ ] P2 alerts for new admin, dependency vulns
- [ ] Alerts delivered to appropriate channels (PagerDuty, Slack)

### Dashboards
- [ ] Security overview dashboard
- [ ] Billing security dashboard
- [ ] Auth dashboard
- [ ] Abuse detection dashboard

### Logs
- [ ] Structured logging with required fields
- [ ] Log sampling for high-volume events
- [ ] PII redacted from logs
- [ ] Log retention matches compliance

### Tracing
- [ ] Security-critical operations have spans
- [ ] Trace includes tenant and user context
- [ ] Traces integrated with logs via trace_id

### Behavioral detection
- [ ] Slow-brute heuristic implemented
- [ ] Credential stuffing heuristic implemented
- [ ] Account takeover heuristic implemented
- [ ] Subscription bypass heuristic implemented
- [ ] Admin compromise heuristic implemented

### Honeypots
- [ ] At least 1 database honeypot
- [ ] At least 1 endpoint honeypot
- [ ] Alerts wired to security team
