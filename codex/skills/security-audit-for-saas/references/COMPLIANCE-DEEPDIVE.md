# Compliance Deep Dive — SOC 2, GDPR, PCI-DSS, HIPAA, ISO 27001

SaaS security audits exist in a compliance landscape. Findings must map to
regulatory requirements. This file provides deep coverage of the five most
important frameworks.

**How to use:**
- During audit: tag each finding with applicable frameworks
- During remediation: prioritize by compliance deadlines
- During sales: answer "are we SOC 2 / GDPR compliant?" honestly
- During breach: know your notification obligations

---

## SOC 2 Type II

Service Organization Control 2 is the dominant SaaS compliance framework for
B2B companies. It audits against the AICPA Trust Services Criteria (TSC).

### The Five Trust Services Criteria
1. **Security** — protection against unauthorized access (required)
2. **Availability** — operational availability as committed
3. **Processing Integrity** — processing is complete/valid/accurate
4. **Confidentiality** — designated information protected
5. **Privacy** — personal information handled per commitments

### Control Categories & SaaS Security Findings

#### CC1 — Control Environment
**Related findings:**
- Missing security training documentation
- No documented security policies
- Missing background checks for admin access

**Evidence auditors look for:**
- Security policy document (< 1 year old)
- Training records
- Org chart with security roles

#### CC2 — Communication and Information
**Related findings:**
- No security incident communication channel
- Stakeholders unaware of security commitments

**Evidence:** Incident response playbook, customer security documentation

#### CC3 — Risk Assessment
**Related findings:**
- No documented threat model
- No risk register
- Changes deployed without security review

**Evidence:** Annual risk assessment, threat model document, change management
records

**Mapping to this skill:** [THREAT-MODELING.md](THREAT-MODELING.md)

#### CC4 — Monitoring Activities
**Related findings:**
- No security metrics dashboard
- Audit log not queryable
- No alerting on auth failures

**Evidence:** Monitoring dashboards, alert rules, incident metrics

**Mapping:** [OBSERVABILITY.md](OBSERVABILITY.md), [AUDIT-LOGGING.md](AUDIT-LOGGING.md)

#### CC5 — Control Activities
**Related findings:**
- RLS missing on user data tables
- Admin operations without 2-person rule
- Changes to production without review

**Evidence:** RLS coverage report, access request forms, PR review logs

#### CC6 — Logical and Physical Access Controls
**Related findings:**
- Shared admin accounts
- No MFA on privileged accounts
- Orphaned accounts for ex-employees

**Evidence:** Access control policy, MFA enforcement logs, user lifecycle records

**Mapping:** [AUTH.md](AUTH.md), [ADMIN-ESCALATION-PATHS.md](ADMIN-ESCALATION-PATHS.md)

#### CC7 — System Operations
**Related findings:**
- No incident response plan
- Backups not tested
- Capacity not monitored

**Evidence:** Incident playbook, backup test results, capacity reports

**Mapping:** [INCIDENT-RESPONSE.md](INCIDENT-RESPONSE.md)

#### CC8 — Change Management
**Related findings:**
- Production changes without tests
- Emergency changes bypass review
- No rollback procedures

**Evidence:** CI/CD pipeline with gates, change request logs, rollback playbooks

#### CC9 — Risk Mitigation
**Related findings:**
- No vendor security assessment
- No business continuity plan
- Key vendor changes untracked

**Evidence:** Vendor risk register, DR plan, vendor list

### SaaS Audit → SOC 2 Mapping Cheat Sheet

| Audit Finding | TSC | Evidence Required |
|---------------|-----|-------------------|
| Missing MFA on admin accounts | CC6 | MFA enforcement screenshot |
| RLS missing on users table | CC5 | RLS coverage query |
| Webhook signature not verified | CC5 | Signature verification code |
| Audit log mutable | CC4 | Immutability controls |
| No incident response plan | CC7 | Playbook document |
| Secret in git history | CC5 | Secret scanning config |
| Rate limiter fails open | CC5, CC7 | Fail-closed code path |

### Type II vs Type I
- **Type I:** Point-in-time assessment (controls exist and designed well)
- **Type II:** Period-of-time assessment (controls operated effectively)

Most B2B customers require Type II. It requires a 6-12 month observation window.

### Common SOC 2 Audit Findings (From Real Audits)
1. Incomplete user access reviews
2. Missing segregation of duties
3. Inadequate change management
4. Insufficient vendor management
5. Incomplete incident response testing
6. Missing security awareness training
7. Inadequate backup testing
8. Insufficient access removal for terminated employees

---

## GDPR (EU General Data Protection Regulation)

GDPR applies to any SaaS processing EU residents' personal data, regardless of
the SaaS's location. Fines: up to 4% of global annual revenue or €20M.

### Key Articles and SaaS Application

#### Article 5 — Principles
- **Lawfulness, fairness, transparency:** Privacy policy matches actual practice
- **Purpose limitation:** Data used only for stated purposes
- **Data minimization:** Collect only what's needed
- **Accuracy:** Users can correct their data
- **Storage limitation:** Retention periods enforced
- **Integrity & confidentiality:** Encryption, access control
- **Accountability:** Demonstrate compliance

**Related audit findings:**
- Data collected beyond stated purpose (add to privacy policy or stop collecting)
- Indefinite retention (implement retention cron)
- No user data export (add DSAR endpoint)

#### Article 6 — Lawful Basis
For every data processing activity, identify the lawful basis:
- Consent
- Contract
- Legal obligation
- Vital interests
- Public task
- Legitimate interests

**Audit question:** For each data field, what's the lawful basis?

#### Article 7 — Consent
- Consent must be freely given, specific, informed, unambiguous
- Users can withdraw consent as easily as they gave it
- Records of consent must be kept

**Audit finding:** Cookie banner that doesn't allow reject = GDPR violation

#### Article 15 — Right of Access (DSAR)
Users can request a copy of all data you hold about them.

**Implementation:**
- API endpoint `/api/gdpr/export` that returns all user data
- Process manual requests within 30 days
- Include data from third parties (Stripe, analytics)

#### Article 17 — Right to Erasure (Right to be Forgotten)
Users can request deletion.

**Implementation:** See [DATA-SECURITY.md](DATA-SECURITY.md) deletion sweep

**Gotchas:**
- Must cascade to all third parties
- Backups can retain until rotation
- Legal obligations may preserve some data (financial records for 7 years)

#### Article 25 — Data Protection by Design and Default
Privacy must be built in from the start, not bolted on.

**Audit question:** How did you consider privacy when designing this feature?

#### Article 32 — Security of Processing
Technical and organizational measures to ensure security:
- Pseudonymization / encryption
- Confidentiality, integrity, availability
- Ability to restore after incident
- Regular testing

**Direct mapping:** All of this skill's technical content

#### Article 33 — Breach Notification to Regulator
- 72 hours from awareness
- Must include: nature, affected data, approximate number of records,
  likely consequences, mitigation

**Implementation:** Notification template pre-drafted in
[INCIDENT-RESPONSE.md](INCIDENT-RESPONSE.md)

#### Article 34 — Breach Notification to Data Subjects
- Required if high risk to rights and freedoms
- Must be "without undue delay"
- Plain language

#### Article 35 — Data Protection Impact Assessment (DPIA)
Required for high-risk processing. See [DATA-SECURITY.md](DATA-SECURITY.md) PIA.

### GDPR Article → SaaS Audit Cheat Sheet

| Article | Requirement | Audit Check |
|---------|------------|-------------|
| Art. 5 | Data minimization | Review each DB column |
| Art. 7 | Consent records | Consent audit log exists |
| Art. 15 | Right of access | DSAR endpoint works |
| Art. 17 | Right to erasure | Deletion sweep works |
| Art. 25 | Privacy by design | PIA exists for new features |
| Art. 32 | Security measures | All of this skill applies |
| Art. 33 | 72hr breach notification | Playbook + template exists |

### GDPR Fines Examples
- **Meta (2023):** €1.2 billion for unlawful data transfers to US
- **Amazon (2021):** €746 million for ad tracking without consent
- **British Airways (2019):** £20 million for payment page XSS leading to
  customer card theft

---

## PCI-DSS (Payment Card Industry Data Security Standard)

PCI-DSS applies if you store, process, or transmit cardholder data. For SaaS,
this usually applies if you're building a payment processor or if you're
handling customer cards directly (most SaaS use Stripe, which reduces scope).

### Scope Reduction Strategy
Most SaaS should aim to minimize PCI scope by:
- Using Stripe Checkout (hosted, Stripe handles card data)
- Using Stripe Elements (iframe isolation)
- NEVER receiving or storing raw card numbers

If done right, your PCI scope is minimal (SAQ A or SAQ A-EP).

### 12 Requirements (High Level)
1. Install and maintain firewalls
2. Don't use vendor-supplied defaults for passwords
3. Protect stored cardholder data (if any)
4. Encrypt transmission of cardholder data
5. Use and regularly update anti-virus
6. Develop and maintain secure systems (dev SDLC)
7. Restrict access on need-to-know
8. Assign unique ID to each person with access
9. Restrict physical access to cardholder data
10. Track and monitor all access to network resources
11. Regularly test security (pen tests, scans)
12. Maintain security policy

### New in v4.0 (2025 enforcement)
- **Requirement 6.4.3:** Script inventory for payment pages
- **Requirement 11.6.1:** Payment page tamper detection
- **Requirement 8.3.9:** 15-char passwords OR MFA (previously 7-char)
- **Customized approach:** Flexibility to meet intent via alternative methods

### SaaS PCI Audit Findings
| Finding | PCI-DSS Requirement | Scope |
|---------|--------------------|-------|
| Storing raw card number | 3.2, 3.4 | Catastrophic |
| Payment page modifiable by admin XSS | 6.4.3, 11.6.1 | High |
| TLS 1.0/1.1 still supported | 4.1 | High |
| Admin access without MFA | 8.3 | High |
| No quarterly vulnerability scans | 11.2 | Medium |

### Recommended: Avoid PCI Scope Entirely
Use Stripe Checkout. Never see card numbers. Your PCI obligations shrink to:
- TLS for the page that redirects to Stripe
- No embedding of card collection
- Annual self-assessment (SAQ A)

---

## HIPAA (Healthcare)

HIPAA applies if you handle Protected Health Information (PHI). If you're not a
healthcare SaaS, skip this section.

### The Three Rules
1. **Privacy Rule:** How PHI can be used/disclosed
2. **Security Rule:** Technical/administrative/physical safeguards
3. **Breach Notification Rule:** What to do after a breach

### Business Associate Agreement (BAA)
If your SaaS handles PHI on behalf of a covered entity (hospital, insurer), you
need a BAA. Major vendors (AWS, GCP, Azure) have HIPAA-compliant offerings with
BAAs available.

### Security Rule Controls (§164.308, §164.310, §164.312)

**Administrative:**
- Security officer designated
- Workforce training
- Access authorization procedures
- Incident response

**Physical:**
- Facility access controls
- Workstation use policies
- Device and media controls

**Technical:**
- Access control (unique user ID, automatic logoff, encryption)
- Audit controls
- Integrity controls
- Person/entity authentication
- Transmission security

### HIPAA-Specific Audit Findings
- PHI in error messages
- PHI in analytics events
- PHI in third-party integrations without BAA
- Missing access audit logs
- Unencrypted PHI at rest
- Missing workforce training records

### Breach Notification
- Patients notified within 60 days
- HHS notified (immediately if >500 records, annually if smaller)
- Media notified if >500 records in one state

### Fines
- Tiered from $100 to $50,000 per violation
- Annual cap: $1.5M per violation category
- Criminal penalties for willful neglect

---

## ISO 27001:2022

ISO 27001 is the international standard for information security management
systems (ISMS). Less prescriptive than SOC 2, more comprehensive than PCI-DSS.

### Annex A Controls (93 controls in 4 categories)

**A.5 Organizational (37 controls)** — policies, roles, etc.
**A.6 People (8 controls)** — HR, training
**A.7 Physical (14 controls)** — building access
**A.8 Technological (34 controls)** — the technical stuff

### Key Technological Controls for SaaS Audits

| Control | Description | Audit Mapping |
|---------|-------------|---------------|
| A.8.2 | Privileged access rights | [AUTH.md](AUTH.md) |
| A.8.3 | Information access restriction | [MULTI-TENANT.md](MULTI-TENANT.md) |
| A.8.5 | Secure authentication | [AUTH.md](AUTH.md) |
| A.8.8 | Management of technical vulnerabilities | [SECURITY-TESTING.md](SECURITY-TESTING.md) |
| A.8.9 | Configuration management | [INFRASTRUCTURE.md](INFRASTRUCTURE.md) |
| A.8.10 | Information deletion | [DATA-SECURITY.md](DATA-SECURITY.md) |
| A.8.12 | Data leakage prevention | [KEY-MANAGEMENT.md](KEY-MANAGEMENT.md) |
| A.8.15 | Logging | [AUDIT-LOGGING.md](AUDIT-LOGGING.md) |
| A.8.16 | Monitoring activities | [OBSERVABILITY.md](OBSERVABILITY.md) |
| A.8.20 | Networks security | — |
| A.8.21 | Security of network services | — |
| A.8.22 | Segregation of networks | [MULTI-TENANT.md](MULTI-TENANT.md) |
| A.8.23 | Web filtering | — |
| A.8.24 | Use of cryptography | [CRYPTO-FUNDAMENTALS.md](CRYPTO-FUNDAMENTALS.md) |
| A.8.25 | Secure development lifecycle | [SECURITY-TESTING.md](SECURITY-TESTING.md) |
| A.8.26 | Application security requirements | [API-SECURITY.md](API-SECURITY.md) |
| A.8.28 | Secure coding | All code-level references |
| A.8.29 | Security testing in development and acceptance | [SECURITY-TESTING.md](SECURITY-TESTING.md) |

### ISO 27001 vs SOC 2
- **ISO 27001:** Standard (prescriptive framework), international
- **SOC 2:** Audit report (attestation), US-centric
- Many enterprises require both
- Good news: 80%+ of controls overlap; effort can be shared

---

## Finding-to-Framework Cross-Walk

A single security finding often maps to multiple frameworks. Example:

**Finding:** Admin panel lacks MFA

| Framework | Control | Requirement |
|-----------|---------|-------------|
| SOC 2 | CC6.1, CC6.6 | Logical access controls |
| GDPR | Art. 32 | Security of processing |
| PCI-DSS | 8.3 | Multi-factor authentication |
| HIPAA | §164.312(d) | Person/entity authentication |
| ISO 27001 | A.8.2, A.8.5 | Privileged access, secure authentication |

Emit findings with all applicable framework tags so compliance teams can
aggregate across audits.

---

## Audit Finding Template with Framework Mapping

```markdown
## Finding: [Title]
- **Location:** file.ts:42
- **Severity:** HIGH
- **ATT&CK:** T1078 (Valid Accounts)
- **OWASP SaaS Top 10:** S06 (Broken Authentication)
- **Kernel Axiom:** #6 (Presence-only header checks)
- **Compliance:**
  - SOC 2: CC6.1, CC6.6
  - GDPR: Article 32
  - PCI-DSS: 8.3 (if in scope)
  - HIPAA: §164.312(d) (if in scope)
  - ISO 27001: A.8.2, A.8.5
- **Description:** ...
- **Fix:** ...
- **Evidence for compliance:** ...
```

This format supports regulatory reporting, audit preparation, and customer
security questionnaires.

---

## Common Questions from Compliance Auditors

### SOC 2 auditor asks: "Show me your access control policy"
- Have a written policy document
- Show evidence of enforcement (MFA logs, access reviews)
- Show evidence of remediation (access removed for ex-employees)

### GDPR auditor asks: "How do you handle data subject access requests?"
- Show DSAR endpoint / email
- Show SLA tracking (must be within 30 days)
- Show exported data sample

### PCI-DSS auditor asks: "How do you protect cardholder data?"
- Best answer: "We don't store it; Stripe does" (minimizes scope)
- If you do: encryption, access control, audit logs, quarterly scans

### HIPAA auditor asks: "Show me your BAAs"
- Every vendor that touches PHI must have a BAA
- Show BAA tracking spreadsheet
- Show vendor security assessments

### ISO 27001 auditor asks: "Where's your ISMS?"
- ISMS = documented management system
- Scope statement, risk assessment, SoA (Statement of Applicability), policies

---

## The Minimum Compliance Posture for Most SaaS

If you're a B2B SaaS selling to mid-market enterprises, aim for:

1. **SOC 2 Type II** (mandatory for most enterprise deals)
2. **GDPR compliant** (required for EU customers)
3. **No PCI-DSS scope** (use Stripe Checkout, never see cards)
4. **Not HIPAA** unless you're specifically in healthcare

Optional (but helpful):
5. **ISO 27001** (international, overlap with SOC 2)
6. **FedRAMP** (for US government customers, significantly more work)

Prioritize SOC 2 first. Use this skill to find and fix technical gaps. Engage
an external auditor 6 months before the observation window starts.
