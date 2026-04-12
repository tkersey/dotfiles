# Incident Response & Forensics

When (not if) a security incident happens, you need a playbook. This file is the
SaaS-specific incident response runbook — detection, containment, forensics,
recovery, and post-mortem.

---

## The Decision Tree: Is This an Incident?

```
Security alert or suspicious activity
                │
                ▼
      Active exploitation?
           │
     ┌─────┴─────┐
     YES          NO
      │            │
      ▼            ▼
  INCIDENT    Gather data
  (below)         │
                  ▼
          Credible risk?
              │
         ┌────┴────┐
         YES       NO
          │         │
          ▼         ▼
      INCIDENT   Log, monitor,
      (below)    review later
```

### Signs of Active Exploitation
- Webhook signature failure rate > 5x baseline
- Auth failure rate > 10x baseline from a single IP or small IP range
- Impossible subscription status changes (free → active without Stripe event)
- Admin actions from unexpected IP / user agent
- Database query latency spike (possible injection or enumeration)
- Error rate spike on a specific endpoint
- Access to data that should require privilege the actor doesn't have

---

## Triage Matrix

| Severity | Definition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0 CRITICAL** | Active data breach OR ongoing financial loss | <15 min | All-hands, pause feature, customer comms |
| **P1 HIGH** | Exploitable bug, potentially active | <1 hour | Patch + investigate + monitor |
| **P2 MEDIUM** | Bug exists but no active exploitation | <24 hours | Patch in next release |
| **P3 LOW** | Defense-in-depth gap | Next sprint | Document + backlog |

### P0 Examples
- Stripe secret key leaked publicly
- Database dumped and on pastebin
- Admin account compromised
- Billing bypass allowing unlimited free access
- Customer PII exfiltrated

### P1 Examples
- Vulnerability with proof-of-concept, not yet exploited
- Admin account password reset via bug (no confirmed exploitation)
- Missing RLS discovered on sensitive table
- Webhook signature bypass possible

---

## The Containment Playbook

### If P0: Immediate Actions (first 15 minutes)

1. **Acknowledge the alert** in the incident channel
2. **Declare incident** — assign incident commander (IC)
3. **Page the on-call security lead**
4. **Freeze the blast radius:**
   - If CI/CD compromise suspected: disable auto-deploy
   - If data exfiltration suspected: block suspicious IPs at WAF
   - If specific endpoint abused: feature-flag it off
   - If credentials leaked: rotate them (see Rotation Playbook below)
5. **Preserve evidence** — snapshot DB, save logs, freeze the current deploy

### The Rotation Playbook (Credential Compromise)

Order matters. Rotate in this order to avoid cascading failures:

1. **Lock down access** first (prevent additional exposure)
2. **Rotate the leaked secret** (if Stripe key: via Stripe dashboard; if DB password:
   via provider console)
3. **Update the env var** (Vercel, AWS, wherever)
4. **Deploy** the new config
5. **Verify** the old secret no longer works
6. **Audit logs** for any use of the old secret after leak time
7. **Inform affected customers** if logs show exposure

### Rotation Checklist by Secret Type

#### Stripe Secret Key
- [ ] Generate new key in Stripe dashboard
- [ ] Update in Vercel env vars (production + preview + dev)
- [ ] Deploy to production
- [ ] Revoke the old key in Stripe dashboard
- [ ] Verify webhooks still work (test with Stripe CLI)
- [ ] Audit Stripe dashboard for any unusual activity during exposure window

#### Database Password
- [ ] Create new password in Supabase dashboard
- [ ] Update `DATABASE_URL` in Vercel env vars
- [ ] Deploy
- [ ] Rotate `SUPABASE_SERVICE_ROLE_KEY` as well (it's derived)
- [ ] Update `NEXT_PUBLIC_SUPABASE_ANON_KEY` if that was also exposed
- [ ] Check for unusual queries in audit log during exposure window

#### OAuth Client Secret
- [ ] Rotate in OAuth provider dashboard
- [ ] Update env var
- [ ] Deploy
- [ ] Verify OAuth flow still works
- [ ] Audit provider logs for unusual OAuth grants

#### GitHub Deploy Token
- [ ] Revoke old token
- [ ] Create new token with minimum scopes
- [ ] Update in CI/CD secret store
- [ ] Verify deploy still works

---

## Forensic Queries

These are copy-paste SQL queries for common forensic questions. Adapt to your schema.

### "Find all users who accessed premium without subscription"
```sql
SELECT DISTINCT u.id, u.email, u.created_at
FROM users u
LEFT JOIN subscriptions s ON s.user_id = u.id
WHERE (s.status IS NULL OR s.status NOT IN ('active', 'trialing', 'past_due'))
  AND EXISTS (
    SELECT 1 FROM audit_log
    WHERE actor_id = u.id
      AND action = 'premium_feature_access'
      AND created_at > $incident_start_time
  );
```

### "Compute refund owed due to bypass"
```sql
SELECT u.email,
       COUNT(DISTINCT DATE(al.created_at)) as days_accessed,
       COUNT(DISTINCT DATE(al.created_at)) * 3.33 as approx_refund_usd -- $99/mo ÷ 30
FROM users u
JOIN audit_log al ON al.actor_id = u.id
WHERE al.action = 'premium_feature_access'
  AND al.created_at BETWEEN $bypass_start AND $bypass_end
  AND NOT EXISTS (
    SELECT 1 FROM subscriptions s
    WHERE s.user_id = u.id AND s.status = 'active'
    AND s.current_period_start <= al.created_at
    AND s.current_period_end >= al.created_at
  )
GROUP BY u.email
ORDER BY days_accessed DESC;
```

### "Find all auth failures from a specific IP"
```sql
SELECT action, actor_id, result, created_at, user_agent
FROM audit_log
WHERE ip_address = $suspect_ip
  AND created_at > $incident_start_time
ORDER BY created_at;
```

### "Find all admin actions in the last 24 hours"
```sql
SELECT actor_id, action, resource_type, resource_id, created_at, ip_address
FROM audit_log
WHERE action LIKE 'admin_%'
  AND created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;
```

### "Find users who logged in from multiple countries within 1 hour"
```sql
WITH login_events AS (
  SELECT actor_id, created_at, ip_address,
         ip_to_country(ip_address) as country
  FROM audit_log
  WHERE action = 'login_success'
    AND created_at > NOW() - INTERVAL '7 days'
)
SELECT actor_id,
       COUNT(DISTINCT country) as country_count,
       array_agg(DISTINCT country) as countries
FROM login_events
GROUP BY actor_id
HAVING COUNT(DISTINCT country) > 1
  AND MAX(created_at) - MIN(created_at) < INTERVAL '1 hour';
```

### "Find RLS policy denials in the last hour"
```sql
-- Requires pg_stat_statements or application-level logging
SELECT query_text, count(*), MIN(created_at), MAX(created_at)
FROM pg_stat_statements
WHERE query_text LIKE '%permission denied for%'
  AND last_updated > NOW() - INTERVAL '1 hour'
GROUP BY query_text
ORDER BY count DESC;
```

### "Find subscriptions that activated without a payment event"
```sql
SELECT s.id, s.user_id, s.status, s.created_at, s.updated_at
FROM subscriptions s
WHERE s.status = 'active'
  AND s.created_at > $incident_start_time
  AND NOT EXISTS (
    SELECT 1 FROM payment_events pe
    WHERE pe.customer_id = s.customer_id
      AND pe.created_at BETWEEN s.created_at - INTERVAL '1 hour'
                             AND s.created_at + INTERVAL '1 hour'
  );
```

---

## Customer Communication Templates

### Template: Data Breach Notification

```
Subject: Important security update regarding your account

Dear [Name],

We are writing to inform you of a security incident that affected your account
on [date]. We identified the issue on [date] and immediately took action to
protect your data.

What happened: [one sentence]
What information was involved: [specific fields]
What we are doing: [steps taken]
What you can do: [specific actions]
For more information: [contact]

We take the security of your data very seriously. We apologize for this incident
and are implementing additional measures to prevent similar issues.

Sincerely,
[Company]
```

### Template: Service Disruption (Contained Incident)

```
Subject: Brief service disruption resolved

We experienced a service disruption on [date] lasting [duration]. The issue
has been resolved. No customer data was affected.

If you notice any unusual behavior, please contact support.
```

### Template: Billing Anomaly Notification

```
Subject: Billing correction for [period]

Due to a technical issue between [dates], your account may show incorrect
billing. We have identified and corrected the issue. Your next invoice will
include an adjustment of [amount].

No action required from you. For questions, contact [billing email].
```

---

## The Post-Mortem Template

After every P0 or P1, write a post-mortem within 48 hours.

```markdown
# Post-Mortem: [Incident Title]
## [Date]

## Summary
[One paragraph: what happened, when, impact]

## Timeline
- HH:MM — Alert triggered
- HH:MM — Incident declared
- HH:MM — Root cause identified
- HH:MM — Containment in place
- HH:MM — Recovery complete
- HH:MM — Customer notification sent

## Impact
- Customers affected: [count]
- Data exposed: [fields, count of rows]
- Revenue impact: $[amount]
- Downtime: [minutes]

## Root Cause
[Detailed technical explanation. Link to code, config, and commits.]

## Contributing Factors
- [Factor 1, e.g., "Missing test coverage for edge case X"]
- [Factor 2, e.g., "Alert threshold was too high to catch this early"]

## Detection
- How was it detected? [Automated alert / customer report / internal discovery]
- How long from start to detection? [Duration]
- How could detection have been faster? [Specific alert to add]

## Response
- What went well? [Effective containment, clear communication]
- What went poorly? [Confusion, delays, missing tools]

## Prevention
Action items to prevent recurrence (each is a beads issue):

| Action | Owner | Priority | Due |
|--------|-------|----------|-----|
| Add test for edge case X | [name] | P0 | 2026-04-15 |
| Lower alert threshold for Y | [name] | P1 | 2026-04-22 |
| Add runbook for this scenario | [name] | P2 | 2026-05-01 |

## Lessons Learned
1. [Insight 1]
2. [Insight 2]
3. [Insight 3]

## Customer Communication
- What was sent: [link to email template]
- To whom: [list or count]
- When: [timestamp]
- Any follow-up required: [yes/no + details]

## Regulatory Obligations
- GDPR notification required? [yes/no + jurisdiction]
- SOC2 audit impact? [yes/no]
- PCI-DSS impact? [yes/no]
- Timeline for regulatory notification: [dates]
```

---

## Rollback Procedures

### Scenario: Broken webhook handler causing revenue loss

1. **Identify the bad code** — commit hash, file, function
2. **Feature-flag it off** if possible (fast rollback)
3. **If not feature-flagged:**
   - Revert the commit in a hotfix branch
   - Deploy the revert
   - Verify webhooks now process correctly
4. **Reconcile missed events:**
   - Query Stripe for events in the affected window
   - Replay them through the (now fixed) handler
   - Verify each user's subscription state matches expected

### Scenario: Compromised admin account

1. **Disable the account** (set `active = false`)
2. **Revoke all sessions** for that account
3. **Audit all actions** taken by that account in the last 30 days
4. **Reverse unauthorized changes** from the audit log
5. **Reset password + enable 2FA** when returning access

### Scenario: Leaked service role key

1. **Generate new service role key** in Supabase dashboard
2. **Update env var** in production
3. **Deploy**
4. **Revoke old key** in Supabase dashboard
5. **Audit ALL operations** that may have used the old key during exposure window
6. **Reset any data** that looks suspicious (changed without explanation)

---

## Incident Response Readiness Checklist

Before an incident happens, ensure:

- [ ] Incident response channel exists (Slack, Discord)
- [ ] On-call rotation defined
- [ ] Contact list for key stakeholders (customers, legal, PR)
- [ ] Customer communication templates drafted
- [ ] Forensic query library ready (this file)
- [ ] Rotation playbooks documented per secret type
- [ ] Rollback procedures practiced
- [ ] Compliance notification timelines documented
- [ ] Backup and restore procedures tested
- [ ] Audit log queryable and preserved
- [ ] Alert thresholds tuned (not too sensitive, not too quiet)
- [ ] Post-mortem template in wiki
- [ ] "Assume breach" tabletop exercise run quarterly

---

## References

- **[OBSERVABILITY.md](OBSERVABILITY.md)** — What to monitor and alert on
- **[AUDIT-LOGGING.md](AUDIT-LOGGING.md)** — How to make logs queryable
- **[KEY-MANAGEMENT.md](KEY-MANAGEMENT.md)** — How to prevent secret leakage in the first place
- **[reporting-sensitive-encrypted-gh-issues](../../reporting-sensitive-encrypted-gh-issues/)** — How to report vulns encrypted
