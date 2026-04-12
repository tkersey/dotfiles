# Data Security & Privacy

This file covers data classification, encryption, retention, GDPR compliance, and
privacy-by-design for SaaS applications.

---

## Data Classification

Every data element belongs to a class. Handle each class differently.

| Class | Examples | Handling |
|-------|----------|----------|
| **Public** | Marketing content, public profile fields | No special controls |
| **Internal** | User preferences, activity timestamps | Auth required |
| **Personal** | Email, name, IP address | Auth + consent + GDPR |
| **Sensitive** | Health data, financial data, SSNs | Encrypted at rest + access logged |
| **Secret** | Passwords, API keys, tokens | Hashed/encrypted + never logged |

### The Classification Audit

For each column in the database, document the class:

```sql
COMMENT ON COLUMN public.users.email IS 'class: personal, gdpr: yes';
COMMENT ON COLUMN public.users.password_hash IS 'class: secret';
COMMENT ON COLUMN public.users.last_login_ip IS 'class: personal, retention: 90 days';
COMMENT ON COLUMN public.users.stripe_customer_id IS 'class: internal';
COMMENT ON COLUMN public.subscriptions.card_last4 IS 'class: sensitive';
```

Query to find undocumented columns:

```sql
SELECT table_name, column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND NOT EXISTS (
    SELECT 1 FROM pg_description d
    JOIN pg_class c ON d.objoid = c.oid
    WHERE c.relname = table_name AND d.objsubid > 0
  );
```

---

## Encryption at Rest

### Disk-Level Encryption (Table Stakes)

Providers like Supabase, AWS RDS, and Vercel storage encrypt disks by default.
Verify it's on; document where the keys are stored.

### Column-Level Encryption (For Sensitive Fields)

For PII that doesn't need to be queried:

```typescript
import { createCipheriv, createDecipheriv, randomBytes } from "crypto";

const ENCRYPTION_KEY = Buffer.from(env.ENCRYPTION_KEY_BASE64, "base64"); // 32 bytes

function encryptField(plaintext: string): string {
  const iv = randomBytes(16);
  const cipher = createCipheriv("aes-256-gcm", ENCRYPTION_KEY, iv);
  const encrypted = Buffer.concat([cipher.update(plaintext, "utf8"), cipher.final()]);
  const authTag = cipher.getAuthTag();
  // Store: iv + authTag + ciphertext, base64 encoded
  return Buffer.concat([iv, authTag, encrypted]).toString("base64");
}

function decryptField(ciphertext: string): string {
  const buf = Buffer.from(ciphertext, "base64");
  const iv = buf.subarray(0, 16);
  const authTag = buf.subarray(16, 32);
  const encrypted = buf.subarray(32);
  const decipher = createDecipheriv("aes-256-gcm", ENCRYPTION_KEY, iv);
  decipher.setAuthTag(authTag);
  return Buffer.concat([decipher.update(encrypted), decipher.final()]).toString("utf8");
}
```

### Searchable Encryption (Hard Problem)

If you need to query encrypted data, you have trade-offs:
- **Deterministic encryption:** same plaintext → same ciphertext. Enables exact
  match queries but leaks frequency info.
- **Blind indexing:** store a keyed hash of the plaintext in a separate column.
  Query by hashing the search term.
- **Homomorphic encryption:** Slow. Only for very specific use cases.

Rule of thumb: if you can avoid searching encrypted data, don't do it.

### Key Management

- Encryption keys: stored in a separate secret store (AWS KMS, Vault, Vercel env)
- Never in the same DB as the encrypted data
- Rotation: create new key, re-encrypt data, retire old key
- Key access: logged, 2-person-rule for retrieval

---

## Encryption in Transit

### TLS Everywhere

- All external connections use HTTPS
- HSTS header set with `max-age=31536000; includeSubDomains`
- HTTPS redirect on port 80
- TLS 1.3 preferred, TLS 1.2 minimum
- Weak ciphers disabled

### Certificate Validation

```typescript
// Don't disable cert validation, even in dev
const response = await fetch(url, {
  // BAD: const agent = new https.Agent({ rejectUnauthorized: false });
});
```

---

## PII Handling

### The PII Inventory

Maintain a list of every place PII flows:
1. Database columns (from classification audit)
2. Logs (application, audit, access)
3. Analytics events
4. Error tracking (Sentry, etc.)
5. Customer support tools (Intercom, Zendesk)
6. Email queues
7. Backup files
8. Cache (Redis)
9. Search indexes

Each location needs:
- Purpose
- Retention period
- Deletion process
- Access control

### PII in Logs

**Vulnerable:**
```typescript
logger.info({ user }, "User logged in");
// user contains email, IP, name, etc.
```

**Safe:**
```typescript
logger.info({
  userId: user.id,  // Internal ID, not PII
  // No email, no name, no IP
}, "User logged in");
```

For correlation, use internal IDs, not PII.

### PII in Error Messages

**Vulnerable:**
```typescript
throw new Error(`Failed to charge ${user.email}: ${stripeError.message}`);
// Email ends up in Sentry, stack traces, customer support
```

**Safe:**
```typescript
throw new Error(`Failed to charge user: ${stripeError.message}`);
// Log userId separately for correlation:
logger.error({ userId: user.id, error: stripeError }, "Charge failed");
```

---

## Data Retention & Deletion

### Retention Policies by Class

| Class | Retention | Rationale |
|-------|-----------|-----------|
| Public | Indefinite | No privacy concern |
| Internal | 2 years | Operational need |
| Personal | Until deletion request + 30-day grace | GDPR |
| Sensitive | 7 years (financial) | SOX, tax compliance |
| Secret | As long as active; delete on rotation | Minimize blast radius |
| Audit logs | 7 years | SOC2, regulatory |

### Scheduled Deletion Crons

```typescript
// cron: daily
async function purgeExpiredData() {
  // Session tokens older than 30 days
  await db.delete(sessions).where(lt(sessions.expiresAt, subDays(new Date(), 30)));

  // Audit logs older than retention
  await db.delete(auditLog).where(lt(auditLog.createdAt, subYears(new Date(), 7)));

  // Soft-deleted users after grace period
  await hardDeleteUsers({
    where: and(
      not(isNull(users.deletedAt)),
      lt(users.deletedAt, subDays(new Date(), 30))
    ),
  });
}
```

### Soft Delete Pattern

```sql
-- Users aren't hard-deleted immediately (allows "undo")
UPDATE users SET deleted_at = now(), email = NULL, /* ... */ WHERE id = $1;

-- Hard delete after grace period via cron
DELETE FROM users WHERE deleted_at < now() - INTERVAL '30 days';
```

### The Deletion Sweep (GDPR Right to be Forgotten)

When a user requests deletion, you must remove their data everywhere:

```typescript
async function deleteUserData(userId: string): Promise<DeletionReport> {
  const report: DeletionReport = {};

  // 1. Primary data
  report.db = await db.transaction(async (tx) => {
    await tx.delete(userPreferences).where(eq(userPreferences.userId, userId));
    await tx.delete(activityLog).where(eq(activityLog.userId, userId));
    await tx.delete(subscriptions).where(eq(subscriptions.userId, userId));
    await tx.delete(users).where(eq(users.id, userId));
    return "ok";
  });

  // 2. Third parties
  report.stripe = await stripe.customers.del(user.stripeCustomerId).catch(e => e.message);
  report.posthog = await posthog.delete({ distinctId: userId }).catch(e => e.message);

  // 3. Storage
  report.s3 = await s3.deleteObjects({ Prefix: `users/${userId}/` }).catch(e => e.message);

  // 4. Cache
  report.cache = await redis.del(`user:${userId}:*`).catch(e => e.message);

  // 5. Search
  report.search = await algolia.deleteObject(userId).catch(e => e.message);

  // 6. Audit log: anonymize but retain (compliance obligation)
  report.audit = await db.update(auditLog)
    .set({ actor_email: "[deleted]" })
    .where(eq(auditLog.actor_id, userId));

  // 7. Generate certificate of deletion
  return report;
}
```

Store the `DeletionReport` for regulatory proof. If any step fails, retry with
backoff. Alert on repeated failures.

---

## Data Minimization

### Collect Less

Every field you collect is a liability. Before adding a new field:
- Do you have a clear purpose?
- Is it required or optional?
- Could you use a derived/anonymized form?
- How long will you keep it?

### Example: IP Addresses

Instead of storing full IPs:
- Store city-level geolocation (via IP lookup at collection time)
- Discard the full IP
- Loses some fraud signal; gains GDPR compliance

### Example: Email Addresses

If email is only for login:
- Store a hash (SHA-256 of lowercase + normalized)
- Compare hashes for login
- Cannot recover original email (acceptable for some use cases)

---

## Backup Security

### Encryption

- Backups encrypted at rest with a key NOT in the same cloud account
- Backup encryption key rotation schedule documented

### Access Control

- Backup restoration is a privileged operation
- 2-person-rule for production restores
- All restoration events audit-logged
- Backup enumeration (listing backups) also logged

### Testing

- Restore a backup to a staging environment quarterly
- Verify data integrity after restoration
- Time the restoration; is it within RTO?

### Retention

- Incremental backups: 30 days
- Full weekly backups: 90 days
- Monthly archives: 1 year
- Annual archives: 7 years (or compliance-driven)

---

## Privacy Impact Assessment (PIA)

Before launching a new feature that touches personal data, run through:

1. **What data is collected?** (Be specific: fields, types, volumes)
2. **Why?** (Business purpose, legal basis)
3. **Who can see it?** (Access controls, sharing with third parties)
4. **How long?** (Retention period, deletion trigger)
5. **Where?** (DB, logs, analytics, backups, third parties)
6. **What if it leaked?** (Blast radius, notification obligations)
7. **Consent?** (Opt-in, opt-out, implied)
8. **User controls?** (View, download, delete, correct)
9. **Cross-border transfer?** (GDPR adequacy decisions)
10. **Minor data?** (Age verification, COPPA compliance)

If any answer is uncomfortable, redesign the feature.

---

## Audit Checklist

### Classification
- [ ] Every DB column has a classification comment
- [ ] Undocumented columns flagged
- [ ] Classification consistent across related columns

### Encryption
- [ ] Disk-level encryption enabled
- [ ] Column-level encryption for sensitive fields
- [ ] Encryption keys in separate secret store
- [ ] TLS 1.3 preferred; weak ciphers disabled
- [ ] HSTS header set

### PII handling
- [ ] PII inventory maintained
- [ ] Logs don't contain PII
- [ ] Error messages don't contain PII
- [ ] Analytics events don't contain PII (use IDs)

### Retention
- [ ] Retention policy documented per data class
- [ ] Scheduled deletion crons running
- [ ] Soft delete with grace period for users
- [ ] Hard delete after grace period

### GDPR
- [ ] User deletion sweep implemented
- [ ] Deletion cascades to third parties
- [ ] Deletion report stored for compliance
- [ ] Data export (DSAR) implemented

### Backups
- [ ] Backup encryption at rest
- [ ] Backup key in separate account
- [ ] 2-person-rule for restores
- [ ] Restoration tested quarterly
- [ ] Retention policy documented

### Privacy
- [ ] PIA completed for new features touching PII
- [ ] Data minimization principles applied
- [ ] User consent recorded where required
