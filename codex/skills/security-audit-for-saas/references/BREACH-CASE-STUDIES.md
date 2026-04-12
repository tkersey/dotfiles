# Breach Case Studies — Learning from Real Incidents

The best security education comes from studying how real breaches happened.
This file documents 15 famous SaaS/cloud breaches with: what happened, root
cause, detection gap, what an audit would have caught, and lessons.

Use this for:
- Training new security reviewers
- Tabletop exercises
- Threat model calibration ("could this happen to us?")
- Red team scenario design
- Explaining risk to leadership

---

## Case 1: Uber (September 2022)

**What happened:** An attacker compromised an Uber contractor's credentials via
social engineering, then used MFA fatigue (spamming push notifications) to
bypass MFA. Once inside the VPN, they found PowerShell scripts with hardcoded
admin credentials for a Privileged Access Management (PAM) system. Full
compromise of Slack, HackerOne, AWS, and internal systems.

**Root cause:** (1) MFA fatigue allowed bypass of push-based MFA. (2) Hardcoded
admin credentials in scripts stored on a network share.

**Detection gap:** No anomaly detection on repeated MFA prompts. No secret
scanning on internal network shares.

**What a security audit would have caught:**
- Grep internal shares for credential patterns → finds hardcoded creds
- MFA configuration review → identifies push-only (no number matching)
- Access review → broad VPN access for contractors

**Lessons:**
1. **Push MFA is weak.** Use number matching, WebAuthn, or hardware keys
2. **Secrets in scripts are ubiquitous.** Scan everywhere, not just git
3. **Contractors need tighter access.** Just-in-time provisioning
4. **Internal network != trusted network.** Zero trust inside the perimeter

---

## Case 2: Okta (March 2022 — Sitel Compromise)

**What happened:** Lapsus$ compromised a support engineer's workstation at
Sitel, Okta's customer support contractor. The engineer's laptop had access to
Okta's SuperUser application, which allowed customer-impacting actions (password
resets, MFA resets). Attackers took screenshots during a 5-day access window.

**Root cause:** (1) Third-party contractor had privileged access to customer
data. (2) Okta's incident detection didn't catch the intrusion for weeks after
it ended.

**Detection gap:** No real-time monitoring of SuperUser actions. No alerting on
unusual geographic access patterns. Sitel's own security was weaker than Okta's.

**What a security audit would have caught:**
- Vendor security assessment → Sitel's controls were weaker than required
- Access review → SuperUser powers were too broad
- Session monitoring → repeated password resets would have alerted

**Lessons:**
1. **Your security is your weakest vendor.** Assess them rigorously.
2. **Contractor access needs stronger controls** than employee access
3. **Sensitive admin actions must be real-time audited** with alerting
4. **Incident detection must work** — detect the intrusion, not the aftermath

---

## Case 3: LastPass (August & December 2022)

**What happened:** Two-stage attack. August: attacker compromised a developer's
account via token theft, stole source code and internal docs. December: using
info from the first breach, attacker targeted a DevOps engineer by exploiting a
vulnerability in their Plex Media Server, obtained master password, accessed
AWS, and exfiltrated customer vault backups.

**Root cause:** (1) Developer's Plex server had a known unpatched CVE. (2)
Customer vault encryption used PBKDF2 with insufficient iterations for older
accounts (5000 iterations). (3) Vault backups accessible with compromised
credentials.

**Detection gap:** No detection of the 5-day data exfiltration. No monitoring
of the DevOps engineer's personal devices (understandable but relevant).

**What a security audit would have caught:**
- Iteration count review → legacy users with weak KDF
- Backup access control review → backups shouldn't be directly accessible
- Separation of concerns → one engineer shouldn't have full backup access

**Lessons:**
1. **KDF iterations must increase over time.** 5000 was fine in 2012, not 2022
2. **Backups are the crown jewel.** Access control them like production
3. **Personal devices can compromise work.** Consider managed endpoints
4. **A two-stage attack is the rule, not the exception.** Plan for it.

---

## Case 4: Twitter (July 2020)

**What happened:** Attackers social-engineered Twitter employees to access an
internal admin tool ("Gods View"). Used the tool to tweet from ~130 high-profile
accounts (Obama, Musk, Biden, Apple) promoting a Bitcoin scam. Also accessed
DMs of 36 accounts.

**Root cause:** Internal admin tool had broad capabilities with no audit,
rate limiting, or 2-person rule for sensitive actions.

**Detection gap:** No anomaly detection on unusual use of the admin tool. No
alerting on large numbers of tweets from a single admin session.

**What a security audit would have caught:**
- Admin tool review → "Why can one tool reset any account's password?"
- Rate limit review → no limits on internal admin actions
- 2-person rule review → no requirement for high-impact actions

**Lessons:**
1. **Internal admin tools are higher-risk than public APIs.** They have more power.
2. **Rate limit admin actions** like any other action
3. **2-person rule** for irreversible high-impact operations
4. **Phishing resistance** via FIDO2 — PUSH-based MFA wasn't enough

---

## Case 5: Equifax (2017)

**What happened:** Attackers exploited Apache Struts CVE-2017-5638 in a public-
facing web app. Equifax had been notified of the CVE 2 months before exploitation
but hadn't patched. Attackers had 76 days of undetected access. 147 million US
consumers' data exfiltrated.

**Root cause:** (1) Unpatched CVE (Struts). (2) Expired IDS certificate meant
network monitoring was broken and nobody noticed.

**Detection gap:** Expired cert on the network monitoring system. Nobody noticed
until 76 days of exfiltration had occurred.

**What a security audit would have caught:**
- Dependency scanning → unpatched Struts CVE
- Monitoring stack review → expired certificates
- Network monitoring verification → regular "does it still work?" tests

**Lessons:**
1. **Patch management is THE most important control.** Most breaches exploit
   known CVEs
2. **Monitor your monitoring.** Detection that's silently broken is worse than
   no detection
3. **Dwell time matters.** 76 days is a LOT of exfiltration
4. **Compliance != security.** Equifax was PCI-DSS compliant

---

## Case 6: Capital One (July 2019)

**What happened:** Former AWS employee exploited a misconfigured WAF to obtain
IAM credentials via the EC2 metadata service (SSRF). Used credentials to list S3
buckets and exfiltrate customer data. 106M customers affected. First major
cloud-native breach.

**Root cause:** (1) WAF misconfiguration allowed SSRF. (2) EC2 metadata service
v1 didn't require auth (no IMDSv2). (3) Over-permissive IAM role on the instance.

**Detection gap:** S3 GetObject and ListBucket calls from unusual sources
weren't flagged. The attacker had 5 months of access.

**What a security audit would have caught:**
- SSRF test → WAF gaps
- IMDS version check → should be v2 with hop limit 1
- IAM review → role had more than needed
- CloudTrail / S3 access log review

**Lessons:**
1. **SSRF against metadata services is the #1 cloud attack pattern**
2. **Use IMDSv2 with hop limit 1** on all EC2 instances
3. **Least privilege IAM.** This instance shouldn't have listed all buckets
4. **Monitor S3 access patterns** — unusual sources should alert

---

## Case 7: Slack Token Leaks (Multiple Incidents)

**What happened:** Multiple Slack customers leaked OAuth tokens in public
GitHub repositories. Attackers automated scanning of new commits, extracted
tokens, accessed Slack workspaces.

**Root cause:** Developer mistakes (committing `.env` files, hardcoded tokens).
Slack's token format was easy to identify via regex.

**Detection gap:** Slack's own secret scanning detected some but not all leaks.
GitHub didn't have secret scanning at the time.

**What a security audit would have caught:**
- Secret scanning config → `.gitleaks.toml`, pre-commit hooks
- Git history scan → existing leaks

**Lessons:**
1. **Secret scanning is not optional.** Pre-commit + CI + history scanning
2. **Short-lived tokens > long-lived tokens.** Leaks matter less if they expire
3. **Detect leaks even when developers make mistakes.** Assume they will
4. **Identifiable token formats help defenders AND attackers.** Trade-off

---

## Case 8: Zoom E2E Claims (2020)

**What happened:** Zoom claimed end-to-end encryption but actually used
transport encryption (server could decrypt). Settled with FTC for $85M.
Also: ability of Zoom employees to join calls, route calls through China.

**Root cause:** Marketing claims exceeded technical reality. Encryption
architecture not aligned with user expectations.

**Detection gap:** Not a technical breach — a compliance/representation failure.

**What an audit would have caught:**
- Marketing claim vs technical implementation review
- "We claim X; does the code actually do X?" verification

**Lessons:**
1. **Cryptographic claims must match implementation exactly**
2. **Marketing security = legal liability**
3. **Third-party audits of cryptographic claims** are worth the money
4. **"End-to-end encryption" has a specific technical meaning** — use it precisely

---

## Case 9: Codecov (April 2021)

**What happened:** Attackers modified Codecov's Bash Uploader script to
exfiltrate environment variables from CI runs. Codecov customers' CI secrets
were silently stolen for ~2 months. Downstream victims: HashiCorp, Rapid7, etc.

**Root cause:** Weak initial credential on Codecov's Docker image creation
process allowed attacker to modify the uploader script. No integrity check on
the script itself.

**Detection gap:** Script change not detected by Codecov. Customers couldn't
detect because the change was subtle.

**What a security audit would have caught:**
- Build pipeline integrity review
- CI secret scoping (should secrets be exposed to third-party uploads?)
- Script integrity verification (SHA256 pinning)

**Lessons:**
1. **Supply chain attacks via CI are high-impact.** Your CI has ALL your secrets
2. **Pin third-party scripts by hash**, not just version
3. **Scope CI secrets** — don't expose them to all steps
4. **Detect changes to third-party code** you depend on

---

## Case 10: SolarWinds SUNBURST (2020)

**What happened:** Russian state actors compromised SolarWinds' build
infrastructure. Inserted malicious code into SolarWinds Orion updates.
Distributed to 18,000 customers over 6-9 months. 100+ high-value targets
(US federal, Microsoft, FireEye) then selectively exploited.

**Root cause:** SolarWinds' build system was compromised via a test server with
weak credentials (`solarwinds123`). Build system had no code integrity checks.

**Detection gap:** SolarWinds didn't detect the build system intrusion.
Customers had no way to detect because the signed updates were authentic.

**What a security audit would have caught:**
- Build system access review → test server with weak password
- Build integrity review → no reproducible builds
- Supply chain visibility → customers had no SBOM

**Lessons:**
1. **Reproducible builds** detect build system compromise
2. **SBOM + attestation** (SLSA framework) lets customers verify
3. **Build systems are as sensitive as production**
4. **Nation-state supply chain attacks are real**

---

## Case 11: GitHub OAuth App Compromise (April 2022)

**What happened:** Attackers compromised Heroku's and Travis CI's GitHub OAuth
app tokens. Used those tokens to clone private repositories from affected users,
including npm's internal repos and Dropbox's.

**Root cause:** OAuth app tokens were stored by Heroku/Travis without encryption
at rest. Compromise of their infrastructure exposed all tokens.

**Detection gap:** GitHub detected unusual activity via heuristics, but only
after significant exfiltration.

**What a security audit would have caught:**
- Vendor security review → how does your OAuth partner store tokens?
- Scope minimization → did you really need `repo` scope?

**Lessons:**
1. **OAuth tokens are bearer tokens.** Treat them like passwords.
2. **Minimize OAuth scopes** to only what's needed
3. **Rotate tokens** periodically
4. **Detect unusual repo access patterns** via GitHub audit log

---

## Case 12: SendGrid / Mailchimp Incidents (Multiple)

**What happened:** Multiple incidents where attackers compromised email service
customers' accounts, sent phishing or spam through their platforms. Sometimes
involved social engineering of email service support.

**Root cause:** Account takeover of customers, weak MFA enforcement on customer
accounts, support social engineering.

**Lessons:**
1. **Customer accounts are attack surface** for SaaS providers
2. **Enforce strong MFA** for business accounts, not just offer it
3. **Support processes need security** — prevent takeover via social engineering
4. **Monitor customer sending patterns** for anomalies

---

## Case 13: MOVEit / Cl0p Ransomware (May 2023)

**What happened:** Cl0p ransomware group exploited a zero-day SQL injection in
Progress Software's MOVEit Transfer product. Used it to exfiltrate data from
~2,600 organizations including government agencies, banks, universities. Total
affected: ~90 million people.

**Root cause:** SQL injection vulnerability in the product. Many orgs hadn't
patched quickly enough after disclosure.

**Detection gap:** Mass exploitation before widespread detection.

**Lessons:**
1. **0-day in widely-deployed products** creates mass breach events
2. **Patch management urgency** for critical vulnerabilities in file transfer
3. **Data minimization** — MOVEit is a transfer tool, not storage. Files shouldn't
   have been there long
4. **Threat intel** — know when your products are being attacked in the wild

---

## Case 14: Snowflake (June 2024, UNC5537)

**What happened:** Attackers used credentials from infostealer malware (stolen
from customer laptops years earlier) to log in to Snowflake accounts that
weren't protected by MFA. Exfiltrated data from ~165 organizations including
AT&T, Santander, Ticketmaster.

**Root cause:** (1) Customer credentials leaked via infostealer malware over
years. (2) Snowflake didn't enforce MFA by default. (3) Customers didn't turn
on MFA.

**Detection gap:** Snowflake's detection focused on technical exploits, not
credential stuffing. Customers weren't monitoring their Snowflake access.

**What an audit would have caught:**
- MFA enforcement review → not enforced at Snowflake level, optional for customers
- Access from unusual locations → attackers logged in from new IPs

**Lessons:**
1. **MFA enforcement should be default for business accounts** — don't rely
   on customer configuration
2. **Infostealer malware** is a real and growing threat
3. **Credential stuffing against SaaS** is the #1 attack vector
4. **Monitor login locations** for business accounts

---

## Case 15: Microsoft Storm-0558 (May-July 2023)

**What happened:** Chinese state actors (Storm-0558) obtained a Microsoft
consumer signing key. Used it to forge authentication tokens for Microsoft 365
Exchange Online. Accessed email of ~25 organizations including US government
agencies.

**Root cause:** (1) Signing key exposure via a crash dump containing the key
that was sent to a debugging environment. (2) Token validation didn't correctly
enforce the key's intended scope (consumer vs enterprise).

**Detection gap:** Microsoft didn't detect the key exposure. Token forgery went
undetected until unusual mail access patterns were noticed.

**What an audit would have caught:**
- Crash dump content review → keys shouldn't end up in debug dumps
- Token validation logic review → key scope should be enforced

**Lessons:**
1. **Key isolation is critical.** Signing keys must never leave their secure enclave
2. **Token validation logic is a complex attack surface** — fuzz it
3. **Debug data can leak secrets** — sanitize crash dumps
4. **Nation-state actors have patience and resources** — your defenses must
   match

---

## Consolidated Lessons Across All Cases

### The "why" behind breaches
1. **Supply chain is fragile** (Cases 9, 10, 11) — your vendors are your weakest link
2. **Social engineering beats technology** (Cases 1, 2, 4) — humans are targeted
3. **Patches matter** (Cases 5, 13) — unpatched CVEs dominate
4. **Credential compromise is the #1 vector** (Cases 1, 6, 14)
5. **Detection gaps enable long dwell time** (Cases 5, 10, 11)
6. **Admin tools are high-value targets** (Cases 2, 4)
7. **Cloud misconfigurations are common** (Case 6) — IMDSv1, overly broad IAM

### Technical controls that would have helped
1. **FIDO2/WebAuthn** (prevents Cases 1, 4, 6 phishing)
2. **Just-in-time privileged access** (prevents Cases 2, 4)
3. **IMDSv2 with hop limit 1** (prevents Case 6)
4. **Secret scanning in CI + pre-commit** (prevents Case 7)
5. **SBOM + reproducible builds** (prevents Case 10)
6. **Backup access controls** (prevents Case 3)
7. **Rate limiting on admin actions** (prevents Case 4)
8. **MFA enforcement by default** (prevents Case 14)

### Organizational controls that would have helped
1. **Tabletop exercises** (finds detection gaps)
2. **Red team exercises** (finds hidden attack paths)
3. **Vendor security assessments** (prevents Case 2)
4. **Patch SLAs** (prevents Case 5)
5. **Incident response playbooks** (speeds recovery)
6. **Security awareness training** (partially prevents social engineering)

### What an audit catches vs what it doesn't
**Audits catch:**
- Unpatched CVEs
- Missing MFA enforcement
- Overly permissive IAM
- Missing audit logging
- Weak password policies
- Secret sprawl

**Audits don't catch:**
- Active intrusions in progress
- Novel 0-days
- Social engineering vulnerability
- Trust decisions (vendor choice)
- Future supply chain compromise

Audits are one layer. Combine with: detection engineering, threat intelligence,
incident response readiness, security culture.

---

## How to Use These Case Studies

### For threat modeling
For each feature, ask: "Could a case study happen here?" Case 4 (Twitter) is
particularly relevant if you have an admin tool. Case 14 (Snowflake) if you
have customer login without enforced MFA.

### For tabletop exercises
Pick a case. Run the scenario against your environment. Document: detection
time, containment effectiveness, recovery time.

### For training
New hires study 3 case studies per week. Discussion questions:
- Could this happen to us?
- What's the earliest detection we'd have?
- What's our response playbook?

### For audit prioritization
Work backward from case studies to audit priorities:
- Cases involving MFA fatigue → audit MFA method
- Cases involving admin tool abuse → audit admin tool logging
- Cases involving supply chain → audit dependency management

### For executive communication
Case studies make risk concrete. "We could have a LastPass-scale incident if our
iteration count is insufficient" lands better than "cryptographic parameters
need review."

---

## References

- **Verizon DBIR:** https://www.verizon.com/business/resources/reports/dbir/
- **CrowdStrike Global Threat Report:** https://www.crowdstrike.com/global-threat-report/
- **Mandiant M-Trends:** https://www.mandiant.com/m-trends
- **HackerNews incident archive:** various
- **Krebs on Security:** https://krebsonsecurity.com/
