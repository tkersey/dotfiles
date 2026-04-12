# Honeypots & Deception Technology for SaaS

Active defense. While most security audits focus on prevention (block the
attack) and detection (spot the attack), deception takes the fight to the
attacker by planting fake targets that reveal intruders the moment they touch
them.

For SaaS, deception is uniquely powerful because:
- Attackers don't know which endpoints are real vs canary
- Zero false positives (no legitimate user touches honeypots)
- Early warning before real damage
- Costs almost nothing to deploy

---

## The Four Deception Layers

### 1. Database honeypots (canary rows)
### 2. Endpoint honeypots (fake routes)
### 3. Credential honeypots (canary tokens)
### 4. Document honeypots (canary files)

Each catches a different kind of attacker.

---

## Database Honeypots

### The Pattern
Insert "canary rows" that no legitimate query should ever return. Monitor for
any access.

```sql
-- Insert a honeypot user
INSERT INTO users (id, email, is_honeypot, created_at)
VALUES (
  gen_random_uuid(),
  'canary-honeypot-do-not-query@internal.example.com',
  true,
  now()
);

-- Create a trigger that fires on any read
CREATE OR REPLACE FUNCTION honeypot_read_alert()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.is_honeypot = true THEN
    -- Write to alert table (separate from audit_log to survive tampering)
    INSERT INTO security_alerts (type, severity, details, created_at)
    VALUES (
      'honeypot_accessed',
      'CRITICAL',
      jsonb_build_object(
        'table', TG_TABLE_NAME,
        'row_id', NEW.id,
        'session_user', session_user,
        'application_name', current_setting('application_name', true)
      ),
      now()
    );
    -- Could also raise NOTICE or NOTIFY to wake a listener
    PERFORM pg_notify('security_alert', 'HONEYPOT_READ');
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Variants
- **Honey record** — a fake "admin" user record
- **Honey column** — a column that's never supposed to be selected
- **Honey table** — an entire table named `secret_passwords` (empty, logged on any query)
- **Honey row in every table** — catches blind SQL injection / exfiltration

### Attack patterns they catch
- SQL injection (attacker dumps table, hits the canary)
- Credential stuffing + data exfiltration
- Insider threats (employee running unusual queries)
- Compromised service accounts

---

## Endpoint Honeypots

### The Pattern
Create fake API endpoints that should never be called in legitimate use.

```typescript
// /api/admin/_internal-debug/route.ts
//
// HONEYPOT: This endpoint does not exist in any documentation.
// No legitimate user should ever call it.
// Any hit here is a probe/attacker.
export async function GET(req: Request) {
  await recordHoneypotHit({
    endpoint: '/api/admin/_internal-debug',
    ip: getClientIp(req),
    userAgent: req.headers.get('user-agent'),
    headers: Object.fromEntries(req.headers.entries()),
  });

  // Pretend to be real — return a 403 (looks protected) instead of 404
  return new Response(JSON.stringify({ error: 'Unauthorized' }), {
    status: 403,
    headers: { 'Content-Type': 'application/json' },
  });
}
```

### Where to place them
- `/api/admin/debug` — sounds legitimate but isn't
- `/api/v0/*` — fake old API version
- `/api/internal/*` — sounds internal
- `/api/backup` — sounds valuable
- `/.env`, `/.git/config` — classic scan targets
- `/api/graphql` — common attacker probe (if you don't use GraphQL)
- `/wp-admin` — catches opportunistic scanners
- `/phpMyAdmin` — catches opportunistic scanners

### What to log
- Full request (headers, body, query, method)
- Client IP and geo
- TLS fingerprint (JA3 hash)
- User agent
- Previous requests from same IP (context)

### What to do after a hit
- **Low severity:** Track the IP; correlate with future requests
- **Medium:** Block the IP at WAF for 24h
- **High (privileged endpoint touched):** Alert security team, investigate
- **Critical (canary credential used):** Full incident response

---

## Credential Honeypots (Canary Tokens)

### The Pattern
Plant fake credentials in places attackers look. Anyone who uses them is by
definition compromised.

### Where to plant them

**In source code (never checked in):**
```typescript
// HONEYPOT: Fake API key. Never use this.
// Any HTTP request with Authorization: Bearer jsm_ci_HONEYPOT_xxxxxx
// is an attacker using a leaked secret.
const HONEYPOT_TOKEN = 'jsm_ci_HONEYPOT_a3f8c2d9e1b4f7a6d5c3';
```

**In environment variables:**
```bash
# .env.example contains a fake secret
HONEYPOT_STRIPE_KEY=sk_test_HONEYPOT_a3f8c2d9e1b4f7a6d5c3
```

Any request using this key alerts because the fake key doesn't exist in
Stripe, so validation will fail — and the attempt signal is the alert.

**In documentation / wiki:**
```markdown
## Example API usage

curl -H "Authorization: Bearer example_token_HONEYPOT_abc123" ...
```

**In Slack messages / internal docs:**
Plant a fake token in a "mistake I fixed" comment. Attackers grep for tokens
in Slack exports.

### The detection logic
For each honeypot credential, create a signature check:

```typescript
const HONEYPOTS = new Set([
  'jsm_ci_HONEYPOT_a3f8c2d9e1b4f7a6d5c3',
  'sk_test_HONEYPOT_a3f8c2d9e1b4f7a6d5c3',
  // ...
]);

export async function middleware(req: Request) {
  const auth = req.headers.get('authorization');
  const token = auth?.replace(/^Bearer /, '');

  if (token && HONEYPOTS.has(token)) {
    await triggerHoneypotAlert({
      token: token.slice(0, 20) + '...',
      ip: getClientIp(req),
      path: new URL(req.url).pathname,
      userAgent: req.headers.get('user-agent'),
    });
    // Return realistic-looking response
    return new Response('{"error":"Invalid credentials"}', { status: 401 });
  }
  // ...
}
```

---

## Document Honeypots

### The Pattern
Create documents that phone home when opened.

**PDF with tracker:**
- Create `top_secret_salaries.pdf`
- Embed a 1px image from `https://canary.example.com/hit?doc=salaries`
- Opening the PDF triggers an HTTP request
- Alert security team on any hit

**Word doc with auto-execute macro:**
- Macro fetches tracking URL on open
- Works in corporate environments that open Word docs

**ZIP file as bait:**
- Name it `passwords.zip` or `customer_export.zip`
- Contents trigger on extract

### Where to place them
- Sharepoint / Google Drive folders
- Admin dashboard "download samples"
- Internal wiki attachments
- S3 buckets with "valuable-sounding" names

---

## Thinkst Canary / Custom Solutions

**Commercial:** Thinkst Canary (thinkst.com/canary) — drop-in honeypot tokens,
docs, AWS keys, etc. Easy to deploy.

**Open source:**
- **CanaryTokens.org** — free canary token generator (PDF, DNS, AWS keys, etc.)
- **OpenCanary** — Python-based honeypot framework
- **HoneyDB** — honeypot network data

**DIY:**
- Custom endpoints, as shown above
- Database triggers
- Alert routing to Slack/PagerDuty

---

## The Alerting Stack

Deception is only useful if alerts reach the right people fast.

### Alert severity
- **INFO:** Honeypot hit from unknown IP
- **WARN:** Honeypot hit from internal IP range
- **CRITICAL:** Honeypot credential used for auth

### Alert destinations
- **Slack:** `#security-alerts` channel
- **PagerDuty:** for CRITICAL only
- **Email:** digest of WARN daily
- **SIEM:** all events for historical analysis

### Alert payload
Include:
- Which honeypot was triggered
- Source IP + geo
- User agent + TLS fingerprint
- Timestamp
- Previous activity from same source
- Suggested response actions

---

## False Positive Management

Honeypots should have ZERO false positives. If legitimate traffic hits them:
- Something's wrong with the placement
- A scanner you run yourself is probing
- Your own monitoring is checking liveness

Configure exemptions:
```typescript
const SCANNER_IPS = new Set([
  '10.0.0.10', // internal scanner
  '35.208.123.45', // Datadog synthetic
]);

if (SCANNER_IPS.has(getClientIp(req))) {
  return; // Skip alert
}
```

Document every exemption with justification.

---

## Legal Considerations

### Is deception legal?
- **Yes for private systems** (your own servers)
- **Caution for tracking real humans** (privacy implications)
- **Document collection tracker**: make sure you're not violating privacy laws

### Ethical considerations
- Deception is defensive, not offensive
- Don't retaliate (hack-back is illegal in most jurisdictions)
- Don't plant honeypots in ways that could harm legitimate users
- Log what you collect; don't use it for non-security purposes

---

## Audit Checklist

### Deployment
- [ ] Database honeypot rows in at least: users, subscriptions, organizations
- [ ] Endpoint honeypots at: /api/admin/debug, /api/v0/*, /api/internal/*
- [ ] Credential honeypot tokens in env files
- [ ] Document honeypots in admin-accessible folders
- [ ] All honeypots logged and alertable

### Alerting
- [ ] Alerts routed to security channel
- [ ] CRITICAL alerts page on-call
- [ ] False positive exemptions documented
- [ ] Weekly review of honeypot hits

### Testing
- [ ] Test honeypot firing monthly (manual trigger)
- [ ] Verify alert arrives
- [ ] Verify response procedures

### Rotation
- [ ] Rotate honeypot credentials quarterly (fresh bait)
- [ ] Move endpoint honeypots periodically
- [ ] Add new honeypots when new features ship

---

## See Also

- [OBSERVABILITY.md](OBSERVABILITY.md) — alerting patterns
- [INCIDENT-RESPONSE.md](INCIDENT-RESPONSE.md) — what to do after a hit
- [AUDIT-LOGGING.md](AUDIT-LOGGING.md) — logging honeypot hits
