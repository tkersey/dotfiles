# Bug Bounty Programs

A bug bounty program pays external researchers to find security bugs. Run
well, it's a force multiplier for your security team. Run poorly, it creates
noise, legal issues, and reputation damage.

---

## When to Start a Bug Bounty

**Too early:**
- You have <5 engineers
- You have <3 months of security hardening
- You haven't run internal audits yet
- You can't respond to reports within 24h

**Right time:**
- Internal security audit complete
- SOC 2 Type I completed or underway
- Dedicated security engineer (even part-time)
- Leadership supportive
- Budget for payouts (min $10K/year)

**Overdue:**
- Customers asking about it in security questionnaires
- You have >10K users
- Critical findings reaching you via customer support

---

## Platform Choice

### Public platforms
- **HackerOne** — largest, most researcher reach
- **Bugcrowd** — good alternative, cheaper
- **Intigriti** — European, strong in Europe
- **YesWeHack** — European, open source friendly

### Private vs public
- **Private:** invite-only, smaller researcher pool, less noise
- **Public:** anyone can participate, more signal but more noise
- **Start private, go public** after 6-12 months

### Self-managed
Host your own `/security` page with reporting email. Cheap but:
- No payment infrastructure
- No researcher reputation
- You handle all triage
- Legal risk you manage yourself

---

## Program Scope

### What's in scope
- Main production domain + subdomains
- APIs (REST, GraphQL)
- Customer-facing applications
- Mobile apps (if any)

### What's out of scope
- Third-party services you don't control
- DoS/DDoS attacks
- Social engineering of employees
- Physical attacks
- Beta/staging environments (optional)
- Domains you don't own
- Rate limit bypasses that are informational only

### Scope document template
```markdown
## Scope

### In scope
- https://app.example.com and all subdomains (*.example.com)
- https://api.example.com
- iOS and Android apps (com.example.app)

### Out of scope
- https://marketing.example.com (static site)
- https://vendor.example.com (third-party)
- Third-party libraries and services
- Email, DNS (except misconfiguration of our records)
- DDoS / volumetric attacks
- Social engineering of employees or customers
- Physical security of our offices
- Tests that affect production users (do not phish real users)
```

---

## Payout Structure

### Severity tiers
Use CVSS 3.1 or similar:

| Severity | Payout range |
|----------|--------------|
| Critical (9.0-10.0) | $5,000 - $25,000 |
| High (7.0-8.9) | $1,500 - $5,000 |
| Medium (4.0-6.9) | $500 - $1,500 |
| Low (0.1-3.9) | $100 - $500 |
| Informational | Recognition only |

Adjust based on:
- Company stage (startup: less; enterprise: more)
- Impact specific to your business
- Chain-based exploits (more for complex chains)
- First-time researcher bonus

### What gets paid what

**Critical:** (example)
- RCE on production server
- SQL injection with DB dump
- Authentication bypass affecting all users
- Subscription bypass with financial impact
- Cross-tenant data read/write

**High:**
- IDOR to other users' data
- Stored XSS in admin context
- SSRF to internal services
- Significant privilege escalation

**Medium:**
- Stored XSS in user context
- CSRF on sensitive actions
- Cache poisoning
- Bypass of CSP/SRI

**Low:**
- Reflected XSS (not easily exploitable)
- Open redirect
- Click-jacking on low-value page
- Missing security headers

---

## Triage Workflow

### 1. Intake
Reports come in via platform or `security@example.com`.

### 2. Initial response (within 24h)
```
Hi [researcher],

Thank you for your report. We've received it and assigned ID BB-2026-0042.

We'll triage within 3 business days and respond with our assessment.

Best regards,
[Name], Security Team
```

### 3. Triage (within 3 days)
- Reproduce the issue
- Assess severity
- Assign to engineering for fix

### 4. Fix
- Track fix in internal issue tracker
- Don't disclose details until fixed

### 5. Verification
- Re-test the fix
- Confirm with researcher it's resolved

### 6. Payout
- Assess final severity based on actual impact
- Issue payment

### 7. Disclosure (with researcher consent)
- Publish write-up with researcher credit
- Add to Hall of Fame

---

## Common Problems

### 1. Noise / invalid reports
- Bots reporting nonsense
- Script kiddies running scanners
- "I found your email address" (not a vulnerability)

**Solution:**
- Clear scope document
- First-pass triage (auto-reject obvious junk)
- Experienced triager
- Reputation-based access (require X karma before access)

### 2. Duplicate reports
- Multiple researchers find the same bug
- Only the first gets paid

**Solution:**
- Fast triage
- Transparent communication
- Consolation payment for valuable duplicates

### 3. Disputed severity
- Researcher claims Critical, you see Medium
- Researcher pushes back

**Solution:**
- Public severity rubric
- Explain reasoning clearly
- Offer to re-assess if new info emerges
- Sometimes the researcher is right — be willing to upgrade

### 4. Legal threats
- Researcher threatens to go public if you don't pay
- Gray-hat behavior

**Solution:**
- Safe Harbor language in program
- Engage legal counsel early
- Public disclosure policy

### 5. Scope creep
- Researcher goes out of scope
- Tests affect production users

**Solution:**
- Clear out-of-scope list
- Firm but professional enforcement
- Temporary ban for repeat violations

---

## Safe Harbor / Legal Protection

Every program needs a safe harbor clause:

```markdown
## Safe Harbor

If you make a good-faith effort to comply with this policy during your security
research, we will consider your research to be authorized, we will work with
you to understand and resolve the issue quickly, and we will not recommend or
pursue legal action related to your research.

Should legal action be initiated by a third party against you, we will make
this authorization known.
```

Based on disclose.io template (https://disclose.io).

---

## Response Time SLAs

Publish and honor SLAs:

| Metric | SLA |
|--------|-----|
| First response | 24 hours |
| Triage decision | 3 business days |
| Critical fix | 7 days |
| High fix | 14 days |
| Medium fix | 30 days |
| Payout after fix | 7 days |

Missing SLAs damages your reputation with researchers.

---

## Hall of Fame

Publicly credit researchers (with their permission):

```markdown
# Security Hall of Fame

Thank you to these researchers for making our platform safer:

## 2026
- **CriticalFindings:** Jane Doe (@janedoe) - BB-2026-0001
- **HighFindings:** John Smith (@johnsmith) - BB-2026-0015
- ...

## 2025
...
```

Researchers love recognition. It's free and powerful.

---

## Metrics to Track

- **Reports received:** per month
- **Valid reports:** % of total
- **Mean time to triage:** hours
- **Mean time to fix:** days by severity
- **Payouts:** total and average per severity
- **Duplicate rate:** %
- **Out-of-scope rate:** %
- **Researcher retention:** % returning

### Healthy program signals
- Triage SLA consistently met
- Valid report rate >20%
- Researchers return (not just one-and-done)
- Payouts feel fair to researchers
- Engineering integrates fixes promptly

### Warning signals
- Triage SLA missed often
- Valid report rate <10% (noise too high)
- Public complaints from researchers
- Engineering ignores findings
- Payouts feel unfair

---

## Internal Process Requirements

Before launching bug bounty, you need:
- [ ] Security team (even 1 person)
- [ ] Engineering on-call for fixes
- [ ] Finance process for international payouts
- [ ] Legal review of program terms
- [ ] Internal tracking system (Jira, Linear)
- [ ] Communication templates
- [ ] Payment infrastructure (platform handles this)
- [ ] Disclosure policy
- [ ] Public `security.txt` file

---

## security.txt File

Host `/.well-known/security.txt`:

```
Contact: mailto:security@example.com
Contact: https://example.com/security
Preferred-Languages: en
Canonical: https://example.com/.well-known/security.txt
Policy: https://example.com/security/policy
Acknowledgments: https://example.com/security/hall-of-fame
Hiring: https://example.com/careers
Expires: 2027-01-01T00:00:00.000Z
```

Standard: https://securitytxt.org/

---

## Bug Bounty vs Pentesting

| | Bug Bounty | Pen Test |
|---|-----------|---------|
| **Cost** | Pay per finding ($$-$$$$) | Fixed fee ($$$$) |
| **Breadth** | Unlimited (crowd) | Limited (team) |
| **Depth** | Variable | Systematic |
| **Time** | Continuous | 1-2 weeks |
| **Compliance** | Doesn't count for most audits | Counts for SOC 2 etc. |
| **Results** | Noise + gems | Structured report |

**Use both:** Pen tests for compliance + depth. Bug bounty for continuous.

---

## Audit Checklist

### Pre-launch
- [ ] Internal security posture strong enough for external testing
- [ ] Scope clearly defined
- [ ] Payout budget allocated
- [ ] Response team identified
- [ ] Legal review of program terms
- [ ] security.txt file published

### Ongoing
- [ ] Triage SLA met
- [ ] Fixes tracked and closed
- [ ] Payouts issued promptly
- [ ] Metrics tracked
- [ ] Program page kept updated
- [ ] Hall of Fame maintained

### Annual review
- [ ] Payout ranges vs industry
- [ ] Scope expansion (new features)
- [ ] Policy updates
- [ ] Researcher feedback incorporated

---

## See Also

- [INCIDENT-RESPONSE.md](INCIDENT-RESPONSE.md)
- [SECURITY-MATURITY.md](SECURITY-MATURITY.md)
- [reporting-sensitive-encrypted-gh-issues](../../reporting-sensitive-encrypted-gh-issues/)
- https://disclose.io/
- https://securitytxt.org/
