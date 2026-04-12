# Security Finding

## Metadata
- **ID:** F-XXXX
- **Title:** [concise, action-oriented]
- **Reporter:** [auditor name]
- **Date found:** YYYY-MM-DD
- **Project:** [name]
- **Commit audited:** [SHA]
- **Status:** Open / In Progress / Fixed / Won't Fix / Duplicate

## Classification
- **Severity:** Critical / High / Medium / Low / Informational
- **Confidence:** Confirmed / Likely / Possible / Unconfirmed
- **Category:** [Billing bypass / Auth / RLS / Secret exposure / ...]

## Framework Mapping
- **OWASP SaaS Top 10:** S01-S10
- **ATT&CK:** Txxxx (technique ID)
- **Kernel Axiom violated:** #1-#10
- **CWE:** CWE-XXX (if applicable)
- **Compliance:**
  - SOC 2: [criterion]
  - GDPR: [article]
  - PCI-DSS: [requirement, if in scope]
  - HIPAA: [rule, if in scope]
  - ISO 27001: [control]

## Location
- **Primary:** `path/to/file.ts:42-58`
- **Related:** `path/to/other.ts:100`
- **Configuration:** `config/file.json`

## Description
[What's wrong, in technical detail. 2-4 paragraphs.]

## Attack Vector
[Step-by-step how an attacker exploits this]

1. Attacker starts with [X capability]
2. They do [action] at [endpoint/file]
3. System responds with [result]
4. Attacker now has [new capability]
5. They use it to [achieve goal]

## Proof of Concept
```
[Minimal reproduction — curl command, SQL query, code snippet]
```

## Impact
- **Revenue impact:** $[amount or range]
- **Data at risk:** [user count, data types, sensitivity]
- **Privilege escalation:** [from role] → [to role]
- **Downtime risk:** [duration or N/A]
- **Customers affected:** [count]
- **Reputation risk:** [description]

## Preconditions
- Attacker needs: [capabilities]
- System state: [required state]
- Timing: [if timing-sensitive]

## Fix
**Short-term:** [immediate mitigation, e.g., feature flag off]
**Long-term:** [proper fix with code]

```typescript
// Before (vulnerable)
[code]

// After (fixed)
[code]
```

**Files to change:**
- [file1]
- [file2]

**Estimated effort:** [hours]

## Regression Test
[How to verify the fix + prevent regression]

```typescript
// tests/security/regression-F-XXXX.test.ts
test('F-XXXX: [title]', async () => {
  // Setup
  // Attempt the attack
  // Verify it fails
});
```

## Detection
If this had been exploited, would we have known?

- **Detected by:** [alert / log / manual / not detectable]
- **Detection gap:** [if any]
- **Detection improvement:** [new alert or dashboard]

## References
- [Related CVE or breach case study]
- [Documentation linked]
- [Tickets / PRs related]

## Verification
After fix is deployed:
- [ ] Regression test added and passing
- [ ] Original reproduction no longer works
- [ ] Related findings checked (maybe same bug class elsewhere?)
- [ ] Detection in place
- [ ] Documentation updated
- [ ] Stakeholders notified

## Post-Mortem (if exploited)
- Exploit date: [date if known]
- Discovery date: [when we found it]
- Dwell time: [duration]
- Users affected: [count]
- Containment actions: [list]
- Lessons: [what we learned]
