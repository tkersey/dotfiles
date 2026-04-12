# Audit Logging & Compliance

If you can't answer "who did what, when, from where, why" for any action in your
system, you're failing SOC2, GDPR, and incident response. Audit logs are not
optional for SaaS.

---

## The Audit Log Schema

Every audit event has these fields (minimum):

```sql
CREATE TABLE public.audit_log (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at  timestamptz NOT NULL DEFAULT now(),

  -- Actor
  actor_id    uuid REFERENCES users(id),
  actor_email text,         -- Denormalized for deleted-user queries
  actor_type  text NOT NULL, -- "user" | "admin" | "system" | "cron" | "api_key"

  -- Action
  action      text NOT NULL, -- "user_login" | "subscription_created" | etc.
  resource_type text,         -- "user" | "subscription" | "organization"
  resource_id text,

  -- Context
  org_id      uuid,           -- Tenant scope, for filtering
  ip_address  inet,
  user_agent  text,
  request_id  text,           -- Correlates with application logs

  -- Result
  result      text NOT NULL,  -- "success" | "denied" | "error"
  error_code  text,

  -- Structured metadata (redacted PII)
  metadata    jsonb,

  -- Integrity
  hash        text,           -- Chain hash for tamper detection
  previous_hash text
);

CREATE INDEX audit_log_actor_idx ON audit_log (actor_id, created_at DESC);
CREATE INDEX audit_log_resource_idx ON audit_log (resource_type, resource_id, created_at DESC);
CREATE INDEX audit_log_org_idx ON audit_log (org_id, created_at DESC);
CREATE INDEX audit_log_action_idx ON audit_log (action, created_at DESC);
CREATE INDEX audit_log_ip_idx ON audit_log (ip_address, created_at DESC);
```

---

## What to Log

### Always Log
- Authentication events: login, logout, failed login, session refresh
- Authorization events: permission grants, role changes, denials
- Data access: viewing sensitive data (PII, billing)
- Data modification: create, update, delete on any tenant-scoped resource
- Administrative actions: user suspension, role assignment, billing changes
- Financial events: checkout, subscription change, refund, dispute
- Security events: abuse signal triggered, RLS denial, rate limit hit
- API key lifecycle: issue, revoke, use
- Export/import operations

### Never Log
- Passwords (even hashed)
- Full credit card numbers
- API keys (log prefix only)
- JWT tokens (log subject only)
- Session tokens
- Personal messages / DM content
- File contents (log filename only)

### Log Carefully (with redaction)
- Email addresses (hash for queries, store last 4 chars + domain for display)
- User-provided search queries (may contain PII)
- Error messages (may contain secrets from stack traces)

---

## The Non-Blocking Write Pattern

Audit log writes must NEVER block the primary operation. If the audit log fails,
the operation still completes, but the failure is alerted.

**Vulnerable:**
```typescript
async function loginUser(email: string, password: string) {
  const user = await authenticate(email, password);
  await db.insert(auditLog).values({ /* ... */ }); // Blocks login
  return user;
}
```

If the audit log table is down or slow, all logins hang.

**Safe:**
```typescript
async function loginUser(email: string, password: string) {
  const user = await authenticate(email, password);

  // Fire-and-forget, but tracked
  after(async () => {
    try {
      await db.insert(auditLog).values({ /* ... */ });
    } catch (err) {
      // Audit log failure is itself an incident
      metrics.increment("audit_log_write_failed");
      logger.error({ err }, "Audit log write failed");
    }
  });

  return user;
}
```

### Even Better: Queue-Based Writes

```typescript
// Write to an in-memory queue, flush in background
const auditQueue: AuditEvent[] = [];

async function logEvent(event: AuditEvent) {
  auditQueue.push(event);
  if (auditQueue.length > 100) await flushAuditQueue();
}

async function flushAuditQueue() {
  const events = auditQueue.splice(0);
  if (events.length === 0) return;
  try {
    await db.insert(auditLog).values(events);
  } catch (err) {
    // Re-queue on failure
    auditQueue.unshift(...events);
    metrics.increment("audit_log_flush_failed");
  }
}

// Flush every 5 seconds
setInterval(flushAuditQueue, 5000);
```

---

## Immutability

Audit logs must be append-only. UPDATE and DELETE operations should be blocked.

### Database Triggers

```sql
CREATE OR REPLACE FUNCTION prevent_audit_log_mutation()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'audit_log is append-only';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_audit_log_update
BEFORE UPDATE ON public.audit_log
FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_mutation();

CREATE TRIGGER prevent_audit_log_delete
BEFORE DELETE ON public.audit_log
FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_mutation();
```

### Retention vs Deletion

Compliance may require deletion after a retention period (GDPR: don't keep PII
forever). Handle via a privileged cron that bypasses the trigger:

```sql
-- Privileged role only
CREATE OR REPLACE FUNCTION purge_expired_audit_logs()
RETURNS void AS $$
BEGIN
  ALTER TABLE audit_log DISABLE TRIGGER prevent_audit_log_delete;
  DELETE FROM audit_log WHERE created_at < now() - INTERVAL '7 years';
  ALTER TABLE audit_log ENABLE TRIGGER prevent_audit_log_delete;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

Only runs as cron, only deletes older than retention period.

---

## Tamper Detection via Hash Chaining

```sql
-- Each row has a hash of (this row + previous row's hash)
UPDATE audit_log SET hash = sha256(
  id::text || created_at::text || actor_id::text || action || metadata::text || COALESCE(previous_hash, '')
)
WHERE hash IS NULL;
```

### Verification Query

```sql
-- Detect tampering by recomputing the chain
WITH recomputed AS (
  SELECT id,
         sha256(id::text || created_at::text || actor_id::text || action || metadata::text || COALESCE(LAG(hash) OVER (ORDER BY created_at), '')) as computed_hash,
         hash as stored_hash
  FROM audit_log
)
SELECT id FROM recomputed WHERE computed_hash != stored_hash;
-- Should return 0 rows if no tampering
```

---

## Sensitive Data Redaction

### Email Hashing for Queries

```typescript
const emailHash = crypto.createHash('sha256').update(email.toLowerCase()).digest('hex');
await logEvent({
  actor_email_hash: emailHash, // Query by hash
  actor_email_display: email.slice(0, 3) + "***@" + email.split("@")[1], // Display
});
```

### Metadata Sanitization

```typescript
function sanitizeMetadata(input: Record<string, unknown>): Record<string, unknown> {
  const SENSITIVE_KEYS = ["password", "token", "secret", "key", "authorization"];
  const result: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(input)) {
    if (SENSITIVE_KEYS.some(s => key.toLowerCase().includes(s))) {
      result[key] = "[REDACTED]";
    } else if (typeof value === "string" && value.length > 500) {
      result[key] = value.slice(0, 500) + "...";
    } else {
      result[key] = value;
    }
  }
  return result;
}
```

---

## Compliance Queries

### GDPR: Export All Data for User

```sql
-- Returns all audit events for a specific user, for DSAR (data subject access request)
SELECT * FROM audit_log
WHERE actor_id = $user_id
   OR resource_id = $user_id::text
ORDER BY created_at;
```

### SOC2: Activity Report for Period

```sql
-- All admin actions in the last quarter
SELECT actor_id, action, COUNT(*) as count
FROM audit_log
WHERE created_at BETWEEN $start AND $end
  AND actor_type = 'admin'
GROUP BY actor_id, action
ORDER BY count DESC;
```

### Incident Response: Reconstruct a Suspicious Session

```sql
-- All actions from a specific IP in a time window
SELECT *
FROM audit_log
WHERE ip_address = $suspicious_ip
  AND created_at BETWEEN $start AND $end
ORDER BY created_at;
```

### Anomaly Detection: Activity Outside Business Hours

```sql
-- Admin actions between 11pm and 6am
SELECT *
FROM audit_log
WHERE actor_type = 'admin'
  AND EXTRACT(HOUR FROM created_at AT TIME ZONE 'UTC') NOT BETWEEN 6 AND 23
  AND created_at > now() - INTERVAL '30 days'
ORDER BY created_at DESC;
```

---

## Admin Actions in a Separate Table

Admin actions are high-value targets for tampering. Store them in a separate table
with stricter access controls:

```sql
CREATE TABLE public.admin_audit_log (
  -- Same schema as audit_log
  -- Plus:
  admin_session_id uuid,
  justification text,
  approved_by uuid REFERENCES users(id), -- For 2-person-rule operations
  ticket_id text -- Link to support/ops ticket
);

-- Even stricter access
REVOKE ALL ON admin_audit_log FROM authenticated;
GRANT SELECT ON admin_audit_log TO service_role;
```

---

## The 4 Questions Your Audit Log Must Answer

For any action X at time T:

1. **Who initiated X?** (actor_id + actor_email + actor_type)
2. **From where?** (ip_address + user_agent + request_id)
3. **What changed?** (resource_type + resource_id + metadata.before/after)
4. **Why?** (justification field for admin actions, or business context)

If any question can't be answered, your log schema is incomplete.

---

## Audit Checklist

### Schema
- [ ] Every table has the required fields (actor, action, resource, timestamp, IP, result)
- [ ] Indexes support common queries (by actor, by resource, by org, by IP)
- [ ] Immutability enforced via triggers
- [ ] Retention policy documented and scripted
- [ ] Admin actions in separate table with stricter access

### Write path
- [ ] Audit writes are non-blocking (after() or queue)
- [ ] Audit write failures are alerted (not silent)
- [ ] Sensitive metadata is redacted before storage

### Read path
- [ ] GDPR DSAR query implemented
- [ ] SOC2 activity report query implemented
- [ ] Incident response queries documented
- [ ] Anomaly detection queries running

### Compliance
- [ ] Retention period matches regulatory requirements
- [ ] Audit logs are included in backup strategy
- [ ] Audit log access itself is audited
- [ ] Tamper detection (hash chain) in place
- [ ] Non-privileged users cannot read audit logs for other users

### Operational
- [ ] Dashboard shows audit log health (rows per hour, failure rate)
- [ ] Alerts on audit log write failures
- [ ] Alerts on unusual access patterns (bulk reads, deletes)
