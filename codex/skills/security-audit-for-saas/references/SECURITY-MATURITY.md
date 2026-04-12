# Security Maturity Model for SaaS

Not every SaaS needs the same level of security. Security investment should
match company stage, data sensitivity, and customer expectations. This file
provides a maturity model from "garage startup" to "enterprise-ready."

---

## The Five Levels

### Level 1: Foundation (0-6 months, 1-5 engineers)

**Goal:** Don't embarrass yourself. Cover the basics.

**Requirements:**
- HTTPS everywhere
- Passwords hashed with bcrypt/argon2
- No hardcoded secrets in source
- `.env` in `.gitignore`
- SQL injection prevented (use ORM)
- XSS prevented (use React/framework)
- Session cookies are `HttpOnly` and `Secure`
- Basic rate limiting on login

**What you can skip:**
- MFA (nice to have, not required yet)
- SSO
- Detailed audit logging
- Incident response playbook
- Formal threat modeling
- Penetration testing

**Time investment:** 1-2 weeks of focused security work upfront.

**Sign you're at Level 1:** The checklist above is done, nothing more.

---

### Level 2: Operational (6-18 months, 5-20 engineers)

**Goal:** Handle real customers without major incidents.

**New additions:**
- MFA available (not enforced)
- Centralized audit logging
- Secret scanning in CI
- Dependency scanning
- Basic incident response playbook
- Environment variable management
- Staging environment separate from production
- Code review for security-sensitive changes
- RLS on user data tables

**Process additions:**
- Incident response channel (Slack)
- Security contact (security@ email)
- Vulnerability disclosure policy

**Time investment:** ~20% of one engineer's time, ongoing.

**Sign you're at Level 2:** You have a post-mortem template and have used it.

---

### Level 3: Compliance-Ready (18-36 months, 20-50 engineers)

**Goal:** Pass a customer security questionnaire without rewriting.

**New additions:**
- MFA enforced for all admin accounts
- SOC 2 Type II preparation underway
- Formal security policies (written down)
- Vendor security assessments
- Access reviews (quarterly)
- Encryption at rest for PII
- Data classification started
- Backup testing
- Tabletop incident exercises
- Security awareness training

**Process additions:**
- Security team (could be 1 person or 20% of engineering)
- Change management process
- Vulnerability management process
- Vendor risk management

**Time investment:** Dedicated security role emerging.

**Sign you're at Level 3:** You passed your first customer security questionnaire.

---

### Level 4: Mature (3-5 years, 50-200 engineers)

**Goal:** Security is a competitive advantage, not a cost center.

**New additions:**
- SOC 2 Type II report available
- ISO 27001 consideration
- External pen tests (annual)
- Bug bounty program
- Red team exercises (quarterly)
- Security reviews for new features (before launch)
- Formal threat modeling process
- Security metrics dashboard
- 24/7 security monitoring
- Incident response runbook for every scenario
- DLP (Data Loss Prevention) tools
- Privileged Access Management (PAM)
- Security champions program

**Process additions:**
- Dedicated security team (2-5 people)
- Security reviews in the SDLC
- CISO or security lead
- Regular board security updates

**Time investment:** Dedicated security team.

**Sign you're at Level 4:** Customers cite security as a reason they chose you.

---

### Level 5: Best-in-Class (5+ years, 200+ engineers)

**Goal:** Security innovation and thought leadership.

**New additions:**
- FedRAMP (for US gov customers)
- Multi-region with data residency
- HSM for key management
- Zero trust architecture implemented
- Formal verification for critical components
- Security research publication
- Open source security tool contributions
- Conference speaker roster
- SOC 3 (public-facing security report)
- Dedicated red team
- Purple team exercises
- Security architecture reviews
- Threat intelligence feeds
- MITRE ATT&CK-driven defense

**Process additions:**
- CISO with board reporting
- Security engineering team
- Application security team
- Security operations center (SOC)
- Threat intelligence team

**Time investment:** Large, dedicated security organization.

**Sign you're at Level 5:** You're influencing industry security standards.

---

## The Maturity Dimensions

Maturity isn't one-dimensional. Score separately across:

### Dimension 1: Technical Controls (1-5)
Network security, authentication, authorization, encryption, monitoring.

### Dimension 2: Process Maturity (1-5)
Policies, incident response, change management, vendor management.

### Dimension 3: Compliance Posture (1-5)
SOC 2, GDPR, PCI, HIPAA, ISO 27001 readiness.

### Dimension 4: Organizational Maturity (1-5)
Security team structure, executive support, culture.

### Dimension 5: Continuous Improvement (1-5)
Metrics, retrospectives, improvement velocity.

A company might be Level 3 technically but Level 1 organizationally. The
weakest dimension limits effective security.

---

## Moving Between Levels

### Level 1 → Level 2: The first $10 investment
- Add MFA option (free, low effort)
- Add audit logging (few hours of work)
- Add secret scanning (free, 1 hour setup)
- Write an incident playbook (1 day)

### Level 2 → Level 3: The compliance push
- Hire a security consultant for SOC 2 prep (~$20K)
- Engage an auditor (~$30-50K)
- 6-12 months of remediation work
- Total cost: $50-200K

### Level 3 → Level 4: The dedicated team
- Hire a security lead ($150-250K/year)
- Build security team (2-3 more people)
- Pen test engagement ($30-50K/year)
- Bug bounty program ($20-50K/year)
- Total cost: $500K-1M/year

### Level 4 → Level 5: The thought leadership
- Security engineering team
- Research and development
- Conference attendance and speaking
- Open source contributions
- Total cost: $2M+/year

---

## Maturity Audit

### For each level, ask:
1. Which requirements are met?
2. Which are missing?
3. Which is the biggest gap?
4. What would it cost to close the gap?
5. Is it worth closing now or later?

### Output:
```markdown
# Security Maturity Assessment: [Company]
# Date: 2026-04-09

## Current Level: 2 (Operational)

### Dimensions
- Technical: 2
- Process: 2
- Compliance: 1 (SOC 2 not started)
- Organizational: 1 (no security team)
- Continuous Improvement: 2

## Target Level: 3 (Compliance-Ready)
## Target Date: Q4 2026

## Gaps to Close
1. **SOC 2 preparation** (12 months, $100K)
2. **MFA enforcement** (1 week, $0)
3. **Access reviews** (ongoing, 10 hrs/quarter)
4. **Encryption at rest** (2 months, $0 with provider defaults)
5. **Data classification** (1 month, $0)

## Quick Wins
- MFA enforcement: 1 week, massive impact
- Access reviews: quarterly, prevents stale access

## Investments
- Security consultant for SOC 2: $20K (3 months)
- Auditor for SOC 2: $50K (12 months)
```

---

## The "Over-Investing" Trap

Common mistake: buying expensive enterprise security tools too early.

**Example:** A 10-engineer Series A startup buys an enterprise SIEM for $150K/year.
They have no data to put in it. They have no staff to monitor it. It becomes
shelfware.

**Better:** Spend that $150K on: engineer time for basic controls + SOC 2
prep + a security consultant. Higher ROI.

**Rule of thumb:** Don't buy tools until you've maxed out free/cheap controls.
MFA is free. Secret scanning is free. RLS is free. Most attacks are prevented
by free controls.

---

## The "Under-Investing" Trap

Common mistake: waiting until after a breach to invest in security.

**Example:** A growing SaaS with 10K paying customers has no audit logging.
An incident happens. They can't answer basic questions ("who accessed what?").
Customer trust evaporates. Refunds exceed the cost of implementing audit logs.

**Better:** Budget ~5% of engineering time for security, always. Grow
investment with customer count and data sensitivity.

**Rule of thumb:** Security debt compounds faster than financial debt.

---

## Maturity and Customer Expectations

Customers' expectations scale with their size:

| Customer Type | Expected Maturity |
|---------------|------------------|
| Individual consumer | Level 1 |
| Small business (< 50 employees) | Level 2 |
| Mid-market (50-500 employees) | Level 3 |
| Enterprise (500-5000 employees) | Level 4 |
| Fortune 500 | Level 4 with SOC 2 |
| Government, healthcare, finance | Level 5 with FedRAMP/HIPAA/PCI |

If you want to sell to enterprise, you must be at Level 3+ BEFORE the first
enterprise sales conversation. Waiting until they ask for SOC 2 means you'll
lose the deal.

---

## The Security Debt Ledger

Like technical debt, security debt accumulates. Track it:

```markdown
# Security Debt Ledger

| Item | Impact | Effort | Age | Priority |
|------|--------|--------|-----|----------|
| No MFA on admin | CRITICAL | 1 week | 18 mo | P0 |
| No SOC 2 | HIGH | 12 months | 12 mo | P1 |
| Some tables lack RLS | HIGH | 2 weeks | 6 mo | P1 |
| No access reviews | MEDIUM | 10 hrs/qtr | 12 mo | P2 |
| No backup testing | MEDIUM | 2 days | 6 mo | P2 |
| No tabletop exercises | LOW | 2 days | 12 mo | P3 |
```

Review this ledger quarterly. Pay down the highest-priority items first.

---

## See Also

- [COMPLIANCE-DEEPDIVE.md](COMPLIANCE-DEEPDIVE.md) — detailed compliance info
- [INCIDENT-RESPONSE.md](INCIDENT-RESPONSE.md) — operational maturity
- [OBSERVABILITY.md](OBSERVABILITY.md) — monitoring maturity
