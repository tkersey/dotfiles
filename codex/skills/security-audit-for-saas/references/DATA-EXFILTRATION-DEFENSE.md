# Data Exfiltration Defense

An attacker with code execution or valid credentials will eventually try
to extract data. This file covers how to detect, slow, and block
exfiltration — the last line of defense before data reaches the
attacker's infrastructure.

Related: [CANARY-TOKENS.md](CANARY-TOKENS.md), [AUDIT-LOGGING.md](AUDIT-LOGGING.md),
[OBSERVABILITY.md](OBSERVABILITY.md), [MULTI-TENANT.md](MULTI-TENANT.md).

---

## The exfiltration kill chain

```
1. Recon       → attacker maps what data exists
2. Stage       → copies data to an accessible location
3. Package     → compresses, encodes, or encrypts
4. Exfiltrate  → moves data out of your perimeter
5. Cleanup     → deletes logs, kills canaries
```

Each stage is a defense opportunity. Most SaaS teams defend only at
stage 4 (egress), and only imperfectly. Good programs defend at all 5.

---

## Stage 1: Detection during recon

The attacker needs to understand what data is accessible before they
exfiltrate. This shows up as:

- Wide-scope SELECTs without filters
- `SELECT *` when code normally selects specific columns
- Queries against `information_schema`, `pg_catalog`
- Enumeration of primary key ranges
- Large `COUNT(*)` or `LIMIT 1000000`
- First-time access to tables the user has never touched before

### Detection queries

**First access to a sensitive table:**
```sql
-- Run daily against query logs
SELECT user_id, table_name, MIN(query_time)
FROM query_audit_log
WHERE table_name IN ('customers', 'payment_methods', 'pii_*')
  AND query_time > now() - interval '1 day'
  AND user_id NOT IN (SELECT user_id FROM historical_table_access
                      WHERE table_name = query_audit_log.table_name)
GROUP BY user_id, table_name;
```

**Schema enumeration:**
```
grep 'information_schema\|pg_catalog\|sqlite_master\|sys.tables' /var/log/queries.log
```

This is almost always an attacker or an engineer doing exploratory
analysis. Alert and investigate.

---

## Stage 2: Staging detection

Exfiltration usually involves intermediate storage: a temp table, a
scratch file, an S3 bucket, a blob, a Redis key.

### Detection patterns

- **New CREATE TABLE statements** in production
- **Writes to /tmp, /var/tmp, or ephemeral storage** from services that
  normally don't write there
- **Large INSERT INTO new_table SELECT FROM real_table** patterns
- **Bucket creation in cloud APIs** from service accounts that
  shouldn't create buckets
- **Unexpected S3 PUT patterns** (single large upload to a new key)

### Controls

1. **Deny CREATE TABLE in production** except via migration tooling.
   Enforce at the DB role level.
2. **Read-only filesystem** for service containers. Writes go to
   explicit, tightly-scoped volumes.
3. **Explicit allowlist** of S3/GCS buckets. Service accounts can only
   write to their own bucket.
4. **Anomaly alerts** on storage API usage: sudden 10x increase in PUT
   volume from a service is an exfiltration signal.

---

## Stage 3: Packaging detection

Before exfiltration, data is often compressed or encoded to fit
bandwidth or bypass DLP.

### Signals

- `gzip`, `zstd`, `tar`, `zip` spawned from a service process that
  doesn't normally compress
- `base64` encoding of large payloads in request bodies
- Unusual content-type headers on egress (application/octet-stream when
  the service normally emits JSON)
- High entropy payloads (compressed/encrypted) on channels that should
  be plain text

### Tooling

- **eBPF process execution telemetry** — detect unexpected processes
  (e.g., `tar` in a stateless API pod)
- **Content scanning on egress** — flag high-entropy or compressed
  payloads
- **Protocol validation** — reject non-JSON on JSON-only endpoints

---

## Stage 4: Egress control (the perimeter)

This is the classic DLP problem. You cannot stop all exfiltration, but
you can make it loud and slow.

### Egress allowlisting

The default posture for SaaS workloads should be **deny all outbound**
except to an explicit list of destinations. Every outbound connection
not on the list is an incident.

Typical production allowlist:
- Your own API and storage
- Payment provider (stripe.com, paypal.com)
- Email provider (mailgun.org, sendgrid.net)
- Observability (datadoghq.com, honeycomb.io)
- Known CDNs and package registries (build-time only)

Not on the list:
- Pastebin, github gists, telegram, discord webhooks
- IPFS gateways
- DNS tunneling endpoints
- Random cloud storage (S3 buckets you don't own)

### Implementation patterns

**Kubernetes NetworkPolicy:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-egress-allowlist
spec:
  podSelector:
    matchLabels: {app: api}
  policyTypes: [Egress]
  egress:
  - to:
    - namespaceSelector: {matchLabels: {name: kube-system}}
    ports: [{port: 53, protocol: UDP}]  # DNS
  - to:
    - ipBlock: {cidr: 10.0.0.0/8}  # internal only
  # + explicit CIDR blocks for known partners
```

**Vercel / serverless:**

Serverless makes egress control harder — you usually can't install a
filter in front of the function. Options:
- Use a **fixed-IP egress proxy** (Squid, Fly.io, small VPC instance)
  and route all outbound traffic through it
- **Code-level allowlisting:** wrap the HTTP client, reject unknown
  hostnames. Not as strong but catches careless mistakes.

### DNS-based exfiltration

DNS is a classic exfiltration channel because everyone allows UDP/53
outbound. Data is encoded into subdomain labels:
`<base32-encoded-data>.attacker.com`

Defenses:
- **DNS over the egress proxy** — don't let services query public DNS
  directly
- **DNS query logging** — flag high entropy subdomains
- **TXT record scanning** — large volume of TXT queries is suspicious
- **Blocklist newly-registered domains** (see [DNS-SECURITY.md](DNS-SECURITY.md))

### Rate-limiting egress bandwidth

Even if an attacker finds a valid egress path, you can slow them down.
Hard cap outbound bandwidth per workload. An API service should need
<100KB/s outbound on average. 100MB/s is an incident.

```
# tc (Linux traffic control)
tc qdisc add dev eth0 root tbf rate 1mbit burst 32kbit latency 400ms
```

At 1Mbit/s it takes ~2 hours to exfiltrate 1GB — long enough for
detection to catch up.

---

## Stage 5: Cleanup detection

Attackers delete logs to cover their tracks. If you detect log
tampering, you know exfiltration happened.

### Log immutability

- **Ship logs off-box immediately** — to a SIEM, log lake, or
  append-only store
- **Signed log entries** — each line includes a hash chain so tampering
  is detectable (see [AUDIT-LOGGING.md](AUDIT-LOGGING.md))
- **Separate credentials for log writes** — the service can write but
  not delete; deletion requires an ops role
- **S3 Object Lock / WORM** on archived logs

### Detection

```sql
-- Gaps in expected log stream
SELECT minute, count(*)
FROM log_ingest
WHERE service = 'api' AND minute > now() - interval '1 day'
GROUP BY minute
HAVING count(*) < 100  -- api should emit >100 logs/min
ORDER BY minute;
```

A sudden dropout in logs — especially around the timestamp of another
alert — is often an attacker trying to cover their tracks.

---

## Data minimization: the most effective control

**You cannot exfiltrate data you don't have.** The biggest single
reduction in exfiltration risk comes from not storing data in the first
place.

### Practical wins

| Instead of... | Do... |
|---------------|-------|
| Storing full card numbers | Store Stripe payment method IDs |
| Logging request bodies | Log only redacted summary |
| Storing PII in production for analytics | Anonymize at ingestion |
| Copying prod data to staging | Synthesize fake data |
| Keeping old user data forever | Retention policy + hard delete |
| Session tokens in DB | Stateless JWTs + short TTL |

Every field you don't store is one you cannot leak.

### Column-level encryption

For fields you must store, encrypt at the column level with a key that
the database role cannot access. Even a full DB dump doesn't leak the
plaintext.

```sql
-- pgcrypto, key lives in application, not DB
INSERT INTO users (email_encrypted)
VALUES (pgp_sym_encrypt('user@example.com', '$app_key'));
```

Combine with envelope encryption (per-user data key wrapped by a master
key in KMS) to limit blast radius of a key compromise.

---

## Detection metrics that matter

| Metric | Target |
|--------|--------|
| Time to detect staging | <15 min |
| Time to detect egress to unknown destination | <5 min |
| % of egress going to allowlist | >99.5% |
| % of DB queries matching expected patterns | >99% |
| Canary token access alert latency | <1 min |

Track these as SLIs. Regression in any of them is a security event.

---

## Threat modeling exfiltration

For each sensitive data store, ask:

1. **Who can read it?** (direct users, service accounts, joined queries)
2. **How could they get large volumes out?** (network, backup, replication)
3. **What would the request look like?** (query shape, HTTP traffic)
4. **Where would they put it?** (internal buffer, external destination)
5. **What detection would fire?** (or wouldn't)
6. **How would they cover tracks?** (log deletion, timestamp manipulation)

If steps 1–6 don't each produce at least one detection or control, the
threat model is incomplete.

---

## Canary-driven exfiltration detection

See [CANARY-TOKENS.md](CANARY-TOKENS.md) for details. Key patterns:

- **Honey rows** in every sensitive table — a fake user_id that no real
  user has. Any query that returns it is an exfiltration attempt.
- **Honey files** in backup archives — attackers often dump backups;
  this catches it.
- **AWS canary credentials** in `.env` files — if they're used, the
  env file leaked.
- **Signed URLs with tracking** in exported files — exfiltrated files
  phone home when opened.

Canaries are the highest-signal, lowest-noise exfiltration detection
you can deploy. They should be everywhere.

---

## Insider-specific considerations

Insiders have legitimate access, so network controls help less. Defenses:

1. **Log every data export** — CSV download, API bulk export, backup
   access, replication slot
2. **Require justification** — force a reason/ticket for bulk exports
3. **Separate read-bulk from read-one** — most engineers need
   single-record access, not full-table access
4. **Watermark exports** — embed unique identifiers in each download so
   a leak can be traced
5. **Watch for off-hours access** — insiders planning to exfiltrate
   often do it on weekends

### Splunk/Datadog query for insider exfil

```
source=db_audit event=bulk_export
| stats count by user, table, sum(rows_returned)
| where sum > 10000 OR hour < 6 OR hour > 22
| sort -sum
```

---

## What to do when you catch it

1. **Do not tip off the attacker.** Don't block immediately if you
   can still observe them. Gather evidence first.
2. **Snapshot the evidence.** DB state, network flows, logs.
3. **Escalate to legal** before taking adverse action against an
   insider — you need chain of custody.
4. **Isolate the credential** — rotate the key/token, but watch for
   the attacker trying to use it from a different path.
5. **Notify counsel** about breach disclosure obligations.
6. **Run the post-mortem** (see [INCIDENT-RESPONSE.md](INCIDENT-RESPONSE.md)).

---

## Audit checklist

- [ ] Egress allowlist enforced at network level for every workload
- [ ] DNS queries from workloads logged and analyzed
- [ ] Egress bandwidth rate-limited per workload
- [ ] All bulk data exports logged with actor, reason, row count
- [ ] Canaries deployed in every sensitive table and file
- [ ] Logs ship off-box within 1 min of write
- [ ] Log immutability (hash chain or WORM) enforced
- [ ] Column-level encryption for PII and secrets
- [ ] Anomaly detection on query shape and volume
- [ ] First-time access to sensitive tables alerts
- [ ] Gaps in log stream alert
- [ ] IR playbook includes exfiltration scenario with defined roles

If you can't check every box, you have an exfiltration gap.
