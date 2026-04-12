# SaaS Security Audit Report

**Project:** [name]
**Date:** [YYYY-MM-DD]
**Auditor:** [name]
**Audit type:** Comprehensive / Targeted / Incident Response / Red Team
**Duration:** [hours]

---

## Executive Summary

[One paragraph: top 3 risks, overall posture, key recommendation]

**Total findings:** X (Critical: N, High: N, Medium: N, Low: N)
**Top risk:** [one sentence]
**Recommendation:** [Ship / Ship after P0 fixes / Do not ship]

---

## Scope

### In scope
- [component / feature / endpoint]
- ...

### Out of scope
- [component / feature]
- ...

### Environment
- Production / Staging / Local
- Version audited: [commit hash]
- Test data: [description]

---

## Methodology

- [ ] Threat model (references/THREAT-MODELING.md)
- [ ] 10-axiom kernel check (references/KERNEL.md)
- [ ] 15-domain sweep (SKILL.md)
- [ ] 17 cognitive operators (references/OPERATORS.md)
- [ ] Creativity triggers (references/CREATIVITY-TRIGGERS.md)
- [ ] Red team scenarios (references/ATTACK-SCENARIOS.md)
- [ ] Scripts run (scripts/)
- [ ] Subagents dispatched (subagents/)

---

## Findings

### Critical (N)

#### F-1: [Title]
- **Location:** file.ts:42
- **Severity:** CRITICAL
- **ATT&CK:** [technique]
- **OWASP SaaS Top 10:** S01 / S02 / ...
- **Kernel Axiom violated:** #1 / #2 / ...
- **Compliance mapping:**
  - SOC 2: CC6.1
  - GDPR: Art. 32
  - PCI-DSS: 3.5
- **Attack vector:** [how an attacker exploits this]
- **Impact:** [revenue loss / data breach / privilege escalation / DoS]
- **Evidence:** [code snippet or log excerpt]
- **Fix:** [specific code change]
- **Estimated effort:** [hours]

#### F-2: [Title]
...

### High (N)
...

### Medium (N)
...

### Low (N)
...

---

## Positive Findings

Things done well (reinforce these):

1. [Finding]
2. [Finding]
3. [Finding]

---

## Domains Audited

| Domain | Status | Findings |
|--------|--------|----------|
| Billing | ⚠ | 3 H, 1 M |
| Auth | ✓ | 1 L |
| Entitlements | ⚠ | 1 C |
| Secrets | ✓ | 0 |
| Database | ⚠ | 2 H |
| Web | ✓ | 1 L |
| Infrastructure | ✓ | 1 M |
| Rate limiting | ✓ | 0 |
| Multi-tenant | ✓ | 0 |
| Third-party | ⚠ | 1 H |
| Data security | ✓ | 1 L |
| Incident response | ✓ | 0 |
| Audit logging | ✓ | 0 |
| LLM security | N/A | - |
| API security | ⚠ | 2 M |

---

## Remediation Roadmap

### Immediate (< 24 hours)
- [ ] F-1: Fix [title]
- [ ] F-2: Fix [title]

### This week
- [ ] F-3: Fix [title]
- [ ] F-4: Fix [title]

### This sprint
- [ ] F-5, F-6, F-7: ...

### Next sprint
- [ ] Medium findings

### Backlog
- [ ] Low findings
- [ ] Best practice improvements

---

## Regression Prevention

For each critical/high finding, a regression test is required:

| Finding | Regression test | Location |
|---------|----------------|----------|
| F-1 | [describe test] | [file] |
| F-2 | [describe test] | [file] |

---

## Appendices

### Appendix A: Tools Used
- Static analysis: [tool]
- Fuzzing: [tool]
- Manual review: [hours]
- Scripts: [list]

### Appendix B: Test Accounts
- Tenant A: [email]
- Tenant B: [email]
- Admin: [email]
- (deleted after audit)

### Appendix C: References
- [links to specific code commits, docs, etc.]

### Appendix D: Sign-off
- Auditor: [name, date]
- Reviewer: [name, date]
- Engineering lead: [name, date]
- Security lead: [name, date]

---

## Next Audit

- **Recommended date:** [Q+1]
- **Focus areas:** [areas that deserve follow-up]
- **Continuous monitoring:** [metrics to track]
