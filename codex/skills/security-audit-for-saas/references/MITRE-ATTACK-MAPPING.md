# MITRE ATT&CK Mapping for SaaS

MITRE ATT&CK is the industry-standard framework for describing adversary
behavior. This file maps SaaS-specific vulnerabilities to ATT&CK techniques,
enabling:

- Detection engineering with standardized terminology
- Mapping findings to known-exploited techniques
- Red team exercise planning with ATT&CK scenarios
- Compliance reporting that references ATT&CK

Reference: https://attack.mitre.org/matrices/enterprise/

---

## Tactic: Initial Access (TA0001)

The attacker's first step into the SaaS environment.

### T1078 — Valid Accounts
**SaaS manifestation:**
- Credential stuffing against SaaS login endpoint
- Leaked employee credentials from previous breach
- Session tokens from developer laptops

**Detection:**
- Failed login rate anomalies (abrupt spikes = credential stuffing)
- Geographic anomaly: login from country the user never visits
- Impossible travel: two logins from distant locations within minutes
- New device/user-agent for high-privilege accounts

**Prevention:**
- MFA required for all accounts, enforced at session creation
- Passwordless / passkey migration
- Detect known compromised passwords (HIBP Pwned Passwords)
- Device fingerprinting with risk-based auth

**Related SaaS Top 10:** S06 (Broken Auth)

### T1566 — Phishing (sub: T1566.001 Spearphishing Attachment, T1566.002 Link)
**SaaS manifestation:**
- Attacker sends spearphishing email with link to fake SaaS login page
- Support/admin staff phished to reveal customer data

**Detection:**
- Email security gateway (MS Defender, Proofpoint)
- Monitor for lookalike domains (`company.c0m`, `company-support.io`)

**Prevention:**
- Security awareness training
- FIDO2/WebAuthn (phishing-resistant MFA)

### T1199 — Trusted Relationship
**SaaS manifestation:**
- Third-party integration (SSO provider, support tool) compromised → attacker
  pivots into SaaS

**Detection:**
- Audit log actions attributed to integration service accounts
- Unusual activity from third-party IPs

**Prevention:**
- Scope third-party integrations to minimum permissions
- Separate audit logs for integration actions
- Quarterly vendor access review

**Historical:** Okta 2022 (Sitel contractor compromise)

### T1195 — Supply Chain Compromise (sub: T1195.001 Software Dependencies)
**SaaS manifestation:**
- Compromised npm/pip package → malicious code in production
- Compromised CI tool (Codecov pattern)

**Detection:**
- Dependency scanning (Socket.dev, Snyk, Dependabot)
- Lock file integrity checks
- Build reproducibility verification

**Prevention:** See [THIRD-PARTY.md](THIRD-PARTY.md)

---

## Tactic: Persistence (TA0003)

Maintaining access after initial compromise.

### T1098 — Account Manipulation
**SaaS manifestation:**
- Attacker adds their email to admin whitelist
- Attacker creates a new admin user
- Attacker elevates existing low-privilege account

**Detection:**
- Alert on any role change to admin/owner
- Alert on new admin account creation
- Alert on email whitelist modification

**Prevention:**
- Require 2-person approval for admin creation
- Audit log all role changes with actor + target + reason

**Related SaaS Top 10:** S04 (Admin Console Compromise)

### T1556 — Modify Authentication Process (sub: T1556.009 Conditional Access Policies)
**SaaS manifestation:**
- Attacker disables MFA for their account
- Attacker modifies SSO configuration to add their IdP
- Attacker creates API tokens with long expiry

**Detection:**
- Alert on MFA disable
- Alert on SSO config change
- Alert on long-lived API token creation

### T1078.004 — Cloud Accounts
**SaaS manifestation:**
- Attacker creates OAuth app with broad scopes
- Attacker registers a service account

**Detection:**
- Audit OAuth apps with `offline_access` scope
- Alert on service account creation

### T1136 — Create Account
**SaaS manifestation:**
- Attacker creates a backdoor user with admin privileges
- Attacker creates a "test" account that's actually persistent

**Detection:**
- Review new admin accounts weekly
- Alert on admin account creation outside normal onboarding flow

---

## Tactic: Privilege Escalation (TA0004)

Gaining higher privileges than initially obtained.

### T1078.004 — Valid Accounts: Cloud Accounts
**SaaS manifestation:**
- Attacker starts with read-only access → escalates to write via RBAC bug
- TOCTOU race in permission check during role change

**Detection:**
- Alert on role changes for accounts that don't usually initiate them
- Alert on operations using a role newly acquired

**Prevention:** See [AUTH.md](AUTH.md) TOCTOU section,
[ADMIN-ESCALATION-PATHS.md](ADMIN-ESCALATION-PATHS.md)

### T1134 — Access Token Manipulation
**SaaS manifestation:**
- Forged JWT with elevated claims (if HS256 key compromised)
- Session cookie modified to add admin flag (if trusted client-side)

**Detection:**
- JWT signature verification failures
- Alert on unusual claim combinations

### Not in ATT&CK: Self-Heal-Up Escalation
ATT&CK doesn't capture this pattern well. Add to your detection:
- Auto-promotion logic that re-adds admin flag based on email whitelist
- Reconciliation crons that elevate role based on stale data

**See:** [KERNEL.md](KERNEL.md) Axiom 4

---

## Tactic: Defense Evasion (TA0005)

Avoiding detection.

### T1070 — Indicator Removal
**SaaS manifestation:**
- Attacker deletes audit log entries
- Attacker modifies logs to remove their actions
- Attacker disables logging before acting

**Detection:**
- Audit log immutability via triggers
- Detect `DELETE FROM audit_log` events
- Off-host log replication (attackers can't reach)

**Prevention:** See [AUDIT-LOGGING.md](AUDIT-LOGGING.md) immutability section

### T1562 — Impair Defenses
**SaaS manifestation:**
- Attacker disables rate limiting
- Attacker disables MFA enforcement
- Attacker disables alert rules

**Detection:**
- Alert on changes to security config
- Monitor alert rule deletion events

---

## Tactic: Credential Access (TA0006)

Stealing credentials for lateral movement or persistence.

### T1555 — Credentials from Password Stores
**SaaS manifestation:**
- Extract API keys from CI secrets
- Extract credentials from developer laptops
- Extract OAuth tokens from browser storage

**Detection:**
- Alert on secret store enumeration
- Honeypot credentials that alert on any use

### T1552 — Unsecured Credentials
**SaaS manifestation:**
- Secrets in git history
- Secrets in CI logs
- Secrets in error messages
- Secrets in client bundles

**Detection:**
- Git history scanning (gitleaks, trufflehog)
- Secret scanning in CI logs
- Honeypot secrets in `.env.example`

**See:** [KEY-MANAGEMENT.md](KEY-MANAGEMENT.md)

### T1040 — Network Sniffing
**SaaS manifestation:**
- MITM on non-HTTPS traffic (rare in modern SaaS)
- ARP spoofing in shared dev environments
- WiFi sniffing at conferences

**Prevention:** HSTS, TLS 1.3, certificate pinning where possible

### T1110 — Brute Force (sub: T1110.001 Password Guessing, T1110.003 Password Spraying, T1110.004 Credential Stuffing)
**SaaS manifestation:**
- T1110.001: Guess passwords for known user
- T1110.003: Try common password across many users (avoids lockout)
- T1110.004: Use leaked credential database

**Detection:**
- Rate limiting on login with per-email + per-IP buckets
- Failed login anomaly detection
- Integration with HIBP Pwned Passwords

**Prevention:** See [RATE-LIMITING.md](RATE-LIMITING.md)

**Historical:** Snowflake 2024 (~165 organizations via credential stuffing)

---

## Tactic: Discovery (TA0007)

Learning about the environment.

### T1087 — Account Discovery
**SaaS manifestation:**
- User enumeration via login error messages
- User enumeration via password reset responses
- User enumeration via timing side channels

**Detection:**
- Monitor for systematic username probing
- Constant-time response on auth endpoints

**Prevention:** See [AUTH.md](AUTH.md) enumeration prevention

### T1482 — Domain Trust Discovery (SaaS equivalent: Tenant Discovery)
**SaaS manifestation:**
- Enumerate tenants via subdomain scanning (`acme.company.com`, `beta.company.com`)
- Probe for internal subdomains

**Detection:**
- WAF rules for subdomain enumeration
- DNS monitoring

---

## Tactic: Collection (TA0009)

Gathering data for exfiltration.

### T1530 — Data from Cloud Storage
**SaaS manifestation:**
- Query database for all user records
- Export customer data via admin tool
- Download S3 bucket contents

**Detection:**
- Alert on bulk read operations
- Alert on data export over X records
- Audit log queries against sensitive tables

### T1213 — Data from Information Repositories
**SaaS manifestation:**
- Access shared knowledge bases
- Download team wikis

**Detection:** Same as above, plus content-based monitoring

---

## Tactic: Exfiltration (TA0010)

Moving stolen data out of the environment.

### T1567 — Exfiltration Over Web Service
**SaaS manifestation:**
- Attacker uploads stolen data to Dropbox/Google Drive
- Attacker posts data to pastebin
- Attacker uses DNS tunneling

**Detection:**
- Egress monitoring for known exfil destinations
- Unusual outbound connection patterns
- DLP on outbound email

### T1537 — Transfer Data to Cloud Account
**SaaS manifestation:**
- Attacker copies S3 bucket to their own account
- Attacker syncs database to their RDS instance

**Detection:**
- Cross-account activity alerts
- S3 replication rule changes

---

## Tactic: Impact (TA0040)

Causing damage or disruption.

### T1485 — Data Destruction
**SaaS manifestation:**
- Attacker deletes customer data
- Attacker truncates database tables
- Attacker deletes backups

**Detection:**
- Backup immutability (S3 Object Lock, WORM)
- Alert on bulk DELETE operations
- Snapshot-based recovery point objective

### T1486 — Data Encrypted for Impact (Ransomware)
**SaaS manifestation:**
- Attacker encrypts customer data and demands ransom
- Particularly dangerous for SaaS without offsite backups

**Detection:**
- File modification rate anomalies
- Unusual I/O patterns
- Canary files that alert on modification

### T1498 — Network Denial of Service
**SaaS manifestation:**
- DDoS against public endpoints
- Application-layer DoS (Slowloris, slow POST)
- Resource exhaustion (unbounded query)

**Detection:**
- Traffic rate anomalies
- Request duration anomalies

**Prevention:** See [RATE-LIMITING.md](RATE-LIMITING.md),
[PERFORMANCE-DOS-VECTORS.md](PERFORMANCE-DOS-VECTORS.md)

---

## SaaS-Specific Patterns Not in ATT&CK

ATT&CK was designed for traditional enterprise environments. These SaaS-specific
patterns don't map cleanly:

### 1. Entitlement Bypass
There's no ATT&CK technique for "user accesses paid features without paying."
This is a pure business logic flaw unique to SaaS.

### 2. Webhook Forgery
Closest ATT&CK technique is T1556 (Modify Authentication Process), but webhook
forgery is more about forged cross-service trust than authentication.

### 3. Self-Healing Privilege Escalation
Reconciliation logic that undoes revocations is a unique SaaS pattern that no
ATT&CK technique captures.

### 4. Cache Poisoning for Entitlement
Corrupting subscription cache to grant access is business-logic-specific.

### 5. Trial Reset Abuse
Gaming the trial system to get unlimited free access is fraud, not a technical
compromise — ATT&CK doesn't model fraud.

---

## Using ATT&CK for SaaS Audits

### In audit reports
Tag each finding with the relevant ATT&CK technique ID:

```markdown
## Finding: Missing MFA on admin accounts
- ATT&CK: T1078 (Valid Accounts), T1566 (Phishing)
- Severity: HIGH
- ...
```

This allows security leadership to aggregate findings across audits and track
coverage.

### In detection engineering
For each ATT&CK technique, ask:
1. Do we have a detection rule for this?
2. What's the false positive rate?
3. What's the mean time to detect?
4. Do we have a runbook for response?

### In red team exercises
Pick 5-10 ATT&CK techniques per exercise. Attempt them against your environment.
Document whether each was detected and within what time window.

---

## Coverage Matrix Template

For each tactic, score your coverage:

| Tactic | Techniques Monitored | Rule Count | Avg Detection Time | Gaps |
|--------|---------------------|------------|-------------------|------|
| Initial Access | T1078, T1566, T1195 | 8 | 2 min | T1199 trusted relationship |
| Persistence | T1098, T1556, T1136 | 5 | 5 min | T1098.003 additional email |
| Privilege Escalation | T1078.004, T1134 | 3 | 10 min | Self-heal escalation |
| ... | ... | ... | ... | ... |

Aim for: >80% technique coverage, <15 min avg detection time.

---

## References

- **ATT&CK Enterprise Matrix:** https://attack.mitre.org/matrices/enterprise/
- **ATT&CK for SaaS:** https://attack.mitre.org/matrices/enterprise/cloud/saas/
- **D3FEND (defensive counterpart):** https://d3fend.mitre.org/
- **SIGMA detection rules:** https://github.com/SigmaHQ/sigma
