# Canary Tokens & Tripwires

A canary token is a piece of data that should never be accessed legitimately.
When it is accessed, you know you've been breached. Canaries are high-signal,
low-noise detection — they don't produce false positives.

See [HONEYPOTS-AND-DECEPTION.md](HONEYPOTS-AND-DECEPTION.md) for the broader
deception playbook. This file zooms in on tokens specifically.

---

## The Core Idea

Real data is noisy. Fake data designed to be touched only by an attacker is
quiet. Any touch = alert.

```
Legitimate user:  Never touches canary (by design)
Attacker:          Touches canary (because they don't know it's fake)
Detection signal:  100% specific, 0 false positives
```

---

## Types of Canary Tokens

### 1. HTTP URL canaries
A URL that, when fetched, pings your alerting system.

```typescript
// In a fake admin comment
// INTERNAL_DOCS: https://docs.internal/admin-access-bypass-a3f8c9d2

// When attacker curls this URL, you get an alert
```

### 2. DNS canaries
A subdomain that resolves to your alerting system. Unique per placement.

```
db-backup-20260408.canary.example.com  → logs DNS query source
```

Useful because many attackers do passive recon (DNS lookups before HTTP).

### 3. AWS API key canaries
Fake AWS keys that log when used:
```
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7CANARY1
AWS_SECRET_ACCESS_KEY=canary_secret_that_logs_on_use
```

Services like canarytokens.org create these for free. When attacker tries
them, you get an email.

### 4. Document canaries
PDF/Word/Excel docs with embedded tracking pixels:
```
"2026_Q1_Financial_Summary.xlsx"
"SalaryDataAllEmployees.xlsx"
"customer_database_export.csv"
```

Open → phones home → alert with attacker IP.

### 5. Database row canaries
Fake rows in real tables that should never be read:
```sql
INSERT INTO users (email, password_hash, notes)
VALUES ('ceo_backup@example.com', 'bcrypt_hash', 'CANARY_DO_NOT_READ');
```

Monitor the audit log for reads of this row.

### 6. Environment variable canaries
Fake env vars that look valuable:
```bash
STRIPE_BACKUP_KEY=sk_live_canary_xxx
DATABASE_ADMIN_URL=postgres://canary.example.com:5432/admin
```

Any attempt to use them triggers alerts.

### 7. Credential file canaries
Fake `.env.backup`, `credentials.json`, `id_rsa` in tempting locations.

```
/home/app/.ssh/id_rsa_backup  (canary SSH key)
/var/www/.env.old              (canary env file)
/backups/database.sql.bak      (canary SQL dump)
```

### 8. Code snippet canaries
Fake comments with "TODO: remove before prod" URLs:
```typescript
// TODO(alice): internal debug endpoint — https://debug.canary.example.com/?token=xxx
// Remove before shipping to production
```

Attackers scanning source love these.

### 9. Git branch / tag canaries
Fake branches like `release/customer-data-export` that should never be checked
out.

```yaml
# .github/workflows/canary.yml
on:
  push:
    branches: [release/customer-data-export]
jobs:
  alert:
    runs-on: ubuntu-latest
    steps:
      - name: Alert
        run: curl https://canary.example.com/git-access-detected
```

### 10. Web page canaries
Hidden pages that only exist to be found:
```
/admin/backup (404 for humans, canary for scanners)
/debug/env (alerts on access)
/.git/ (never linked, triggers alert)
```

---

## Canary Placement Strategy

### On the attack path
Place canaries where an attacker will look:
- In backup files they'd grep
- In directory structures they'd list
- In API responses they'd enumerate
- In comments they'd read

### Not on legitimate paths
Canaries must be invisible to real users/processes:
- Not linked from anywhere
- Not indexed by search engines
- Not accessed by monitoring/cron jobs
- Not in production code paths

### Distributed across surfaces
One canary = one detection point. Many canaries = many detection points.

```
├─ S3 bucket with 3 canary files
├─ Database with 5 canary rows
├─ Source code with 10 canary URLs
├─ Git with 2 canary branches
├─ Env with 3 canary env vars
├─ Logs with 4 canary secrets
└─ Admin UI with 2 canary menu items
```

Each is a tripwire. Attacker hitting any one is a detection.

---

## Generating Canary Tokens

### canarytokens.org (Thinkst Canary)
Free, instant, many types. Sign up, get token, paste where needed.

### Self-hosted
```typescript
// Simple self-hosted canary
import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest, { params }: { params: { id: string } }) {
  const tokenId = params.id;
  const token = await db.canaryToken.findUnique({ where: { id: tokenId } });

  if (!token) return new NextResponse('Not found', { status: 404 });

  // Alert
  await sendAlert({
    tokenName: token.name,
    tokenLocation: token.placedAt,
    sourceIp: req.ip,
    userAgent: req.headers.get('user-agent'),
    timestamp: new Date(),
  });

  // Respond innocuously so attacker doesn't know
  return new NextResponse('', { status: 404 });
}
```

### Commercial
- **Thinkst Canary** (hardware + software honeypots)
- **TrapX DeceptionGrid** (enterprise)
- **Attivo Networks**
- **Rapid7 Deception Technology**

---

## Alerting on Canary Triggers

### Severity = CRITICAL
Canary triggers are always investigated immediately. No triage delay.

### Route to multiple channels
- PagerDuty (wake someone up)
- Slack #security-incidents
- Email security@
- SMS to on-call

### Enrich with context
```typescript
const alert = {
  canary_name: 'ceo_backup_user_row',
  canary_location: 'database:users_table:id=canary_1',
  triggered_at: new Date(),
  trigger_source: {
    query: 'SELECT * FROM users WHERE email LIKE \'%ceo%\'',
    user: 'db_user_42',
    ip: '10.0.0.42',
    session_id: 'sess_xyz',
  },
  severity: 'CRITICAL',
  response_playbook: 'runbooks/canary-triggered.md',
};
```

### Investigate every trigger
Canaries don't fire by accident. Every trigger = incident.

---

## The Canary Matrix

| Surface | Canary Type | Detection Signal |
|---------|-------------|------------------|
| Filesystem | `.env.old` file | File read alert |
| Database | Fake admin user row | Row read in audit log |
| Source code | Fake debug URL | HTTP fetch alert |
| Env vars | Fake API keys | API usage alert |
| S3 | Fake backup files | S3 GetObject log |
| Git | Fake release branch | Branch fetch/checkout |
| DNS | Fake subdomain | DNS query log |
| Documents | Fake financial spreadsheet | Open + phone-home |
| API | Fake admin endpoint | HTTP request alert |
| Logs | Fake credentials in logs | Log parser + alert |

---

## Testing Canary Triggers

Before deploying, verify canaries fire:
```bash
# Test HTTP canary
curl https://docs.internal/admin-access-bypass-a3f8c9d2
# Should arrive as alert within 1 minute

# Test database canary
psql -c "SELECT * FROM users WHERE email = 'ceo_backup@example.com'"
# Should trigger audit log alert

# Test AWS key canary
aws s3 ls --profile canary_key
# Should trigger canarytokens.org alert
```

---

## Operational Hygiene

### Document every canary
Otherwise operators will remove them thinking they're unused.

```
# Canary inventory
- canary_001: fake stripe key in src/billing/old.ts (DO NOT REMOVE)
- canary_002: fake user row in users table (id=canary_1, DO NOT TOUCH)
- canary_003: fake DNS subdomain db-backup-20260408.canary.example.com
```

### Rotate annually
Attackers who've seen canaries know to avoid them. Rotate placement yearly.

### Don't over-canary
Too many canaries → alert fatigue. Focus on high-value targets.

### Monitor canary health
If a canary stops responding, you might not detect breaches.
```
Canary heartbeat check:
- Every 24h, automated test triggers canary
- Verify alert arrives
- Fail if no alert within 5 minutes
```

---

## Advanced Canary Patterns

### Behavioral canaries
A canary that only fires on suspicious access:
```typescript
// Only alert if this row is read with a WHERE clause that
// looks like attacker enumeration
if (query.includes('WHERE email LIKE') && row.email.includes('ceo')) {
  alert();
}
```

### Honeytokens in encrypted data
Plant canaries in encrypted data. If decrypted, canaries fire.
```
encrypted_blob:
  - real_data
  - canary_token_that_phones_home_on_decrypt
```

### Staged canaries
Multiple canaries in a chain, each harder to trigger than the last:
1. Easy canary → initial intrusion detection
2. Medium canary → lateral movement detection
3. Hard canary → privileged access detection

Each level provides different signal.

### Canary files with embedded malware signatures
Canary files that legitimate antivirus would flag. If AV fires, you know
someone downloaded them.

---

## What Not to Do

### Don't put canaries in production code paths
If a legitimate request can reach the canary, you'll get false positives.

### Don't make canaries too obvious
"canary_dont_read_me" is useless. Make them look real.

### Don't document canaries in public
Customers, contractors, and former employees shouldn't know locations.

### Don't forget to test
A canary that doesn't fire is worse than no canary.

### Don't ignore alerts
Canary alerts are critical. Every one must be investigated.

---

## Canary Token Checklist

- [ ] At least 5 canaries deployed across different surfaces
- [ ] Each canary has unique identifier
- [ ] Each canary documented in private inventory
- [ ] Alerts route to PagerDuty/Slack
- [ ] Heartbeat test runs every 24h
- [ ] Canaries rotated annually
- [ ] Runbook for canary-triggered incidents
- [ ] Severity is CRITICAL for any trigger
- [ ] Canaries tested before deployment
- [ ] Legitimate processes cannot touch canaries

---

## See Also

- [HONEYPOTS-AND-DECEPTION.md](HONEYPOTS-AND-DECEPTION.md) — broader deception tech
- [INCIDENT-RESPONSE.md](INCIDENT-RESPONSE.md) — responding to triggers
- [AUDIT-LOGGING.md](AUDIT-LOGGING.md) — audit-based canaries
- https://canarytokens.org — free token generator
- https://canary.tools — Thinkst Canary (commercial)
