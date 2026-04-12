# Prompt Archetypes — 5 Audit Modes

Different audit needs require different prompt framings. This file has 5 
copy-paste prompts, each optimized for a specific audit mode.

---

## Archetype 1: The Comprehensive Pre-Launch Audit

**Use when:** Preparing a SaaS application for public launch.
**Time:** 4-6 hours.
**Output:** Full security report, severity-ranked findings, remediation plan.

```
# Comprehensive Security Audit: [Project Name]

You are conducting a full security audit of a SaaS application with billing
before its public launch. Apply the security-audit-for-saas skill end-to-end.

## Phase 1: Preparation (20 min)
1. Fill in the threat model template from references/THREAT-MODELING.md
2. Enumerate ALL attack surfaces (API routes, webhooks, crons, admin, CLI, OG
   images, health checks, telemetry, old API versions)
3. Map data flows across trust boundaries

## Phase 2: Kernel Check (15 min)
Apply each of the 10 axioms from references/KERNEL.md to the codebase.
For each axiom, report:
- Does it hold?
- If not, which file/line violates it?
- Severity if violated?

## Phase 3: 15-Domain Sweep (3 hours)
Work through each domain in SKILL.md, in priority order:
1. Billing (highest priority — revenue impact)
2. Auth & authorization
3. Entitlement enforcement
4. Secrets management
5. Database access control (RLS)
6. Web security
7. Infrastructure
8. Rate limiting & abuse detection
9. Multi-tenant isolation
10. Third-party integration
11. Data security & privacy
12. API security
13. LLM security (if applicable)
14. Audit logging
15. Incident response readiness

For each domain, produce:
- Checklist compliance
- Specific findings (file:line)
- Positive observations (things done well)

## Phase 4: Operator Chains (1 hour)
Apply the 17 cognitive operators from references/OPERATORS.md:
- ⊘ Surface-Transpose on every feature
- ⟂ Fail-Open Probe on every dependency
- ⊙ Identity-Chain Trace on every auth flow
- ≡ Invariant-Extract on every security mechanism
- ✂ Parser-Diverge on every shared input
- ⊕ Creative-Transposition (5 attacker personas)

## Phase 5: Creativity Triggers (30 min)
Walk through references/CREATIVITY-TRIGGERS.md. For any "huh, actually..."
moment, investigate immediately.

## Phase 6: Validation (15 min)
For each finding: can you PROVE it's exploitable? Discard false positives.
Recalibrate severity against actual impact.

## Phase 7: Report (30 min)
Generate structured report using the output template in SKILL.md.
Create beads for each finding. For CRITICAL findings, recommend immediate
escalation.

Focus areas: billing bypass, webhook integrity, auth gaps, entitlement staleness,
secrets exposure, RLS coverage.
```

---

## Archetype 2: The Incident Response Audit

**Use when:** A security incident has been detected or is suspected.
**Time:** 30 min (initial) to 4 hours (deep).
**Output:** Containment plan + forensic timeline + post-mortem draft.

```
# Incident Response Audit: [Incident Description]

An incident has been detected: [brief description]. Apply the security-audit-for-saas
skill in incident response mode.

## Phase 1: Triage (10 min)
Consult references/INCIDENT-RESPONSE.md decision tree.
Classify: P0 / P1 / P2 / P3
Declare incident if P0 or P1.

## Phase 2: Containment (20 min)
Based on the incident type, apply the matching containment playbook:
- Credential leak → Rotation playbook
- Active exploitation → Feature flag off, block IPs
- Compromised account → Disable + revoke sessions
- Data breach → Snapshot + preserve evidence

## Phase 3: Forensics (30 min - 2 hours)
Use forensic queries from references/INCIDENT-RESPONSE.md:
- Find all users affected
- Compute timeline of events
- Identify blast radius
- Check audit logs for actor
- Look for pre-incident reconnaissance
- Verify containment is complete

## Phase 4: Root Cause (30 min - 1 hour)
Apply operator ≡ Invariant-Extract to find the broken assumption.
Trace the code path. Find the specific bug.
Verify the bug is in-scope (not a red herring).

## Phase 5: Recovery (30 min - 1 hour)
- Fix the bug (hotfix branch, deploy)
- Reconcile affected state (refunds, data restoration)
- Verify fix with a targeted test
- Monitor for recurrence

## Phase 6: Post-Mortem (30 min)
Use the post-mortem template from references/INCIDENT-RESPONSE.md.
Include: timeline, impact, root cause, detection gap, prevention actions.

Produce: incident ticket, post-mortem doc, customer communication draft,
prevention action items as beads.
```

---

## Archetype 3: The Targeted Billing Security Audit

**Use when:** Pre-launch of a new billing feature, or concerned about a specific
billing edge case.
**Time:** 1-2 hours.
**Output:** Focused report on billing security only.

```
# Billing Security Audit: [Feature]

You are auditing a specific billing feature or flow. Apply the security-audit-for-saas
skill with focus on billing and entitlement.

## Scope
- Focus on: payment bypass, webhook integrity, entitlement enforcement
- Exclude: general web security (unless directly affecting billing)

## Checklist (from references/BILLING.md)

### Webhook signature verification
- [ ] Stripe: constructEvent with raw body
- [ ] PayPal: API verification with all 5 headers
- [ ] Missing signature → reject + abuse signal
- [ ] Invalid signature → reject + abuse signal
- [ ] Return 200 on processing errors (no retry storms)

### Idempotency
- [ ] Event deduplication via DB unique constraint
- [ ] Event timestamp validation (reject stale)
- [ ] Duplicate events return 200 without re-processing

### Race conditions (TOCTOU)
- [ ] Checkout creation uses FOR UPDATE or advisory lock
- [ ] Seat count read inside transaction
- [ ] maxSeats enforced on member addition (not just checkout)

### Identity validation
- [ ] PayPal custom_id validated against stored customerId
- [ ] Stripe metadata.userId cross-checked with authenticated user
- [ ] Subscription updates verify payer identity

### State management
- [ ] Pending checkout cleared on completion
- [ ] Cache invalidated synchronously (not in after() callback)
- [ ] Unknown provider statuses logged (not silently ignored)

### Entitlement enforcement
- [ ] Server actions check premium tier
- [ ] Subscription status endpoint handles org-only users
- [ ] Grace period uses correct currentPeriodEnd
- [ ] Suspended users denied regardless of other flags

## Operator chains to apply
- ⊙ Identity-Chain Trace on every webhook handler
- ⟂ Fail-Open Probe on subscription check
- ⊘ Surface-Transpose: are there other ways to access premium?

## Red team scenarios
- Scenario A1: $0 Premium via Stripe Metadata
- Scenario A2: PayPal custom_id Hijacking
- Scenario A3: Refund-and-Use
- Scenario A5: Seat Count Bypass

Report: top 5 findings with severity and fix. Under 100 lines.
```

---

## Archetype 4: The Multi-Tenant Isolation Audit

**Use when:** Preparing for enterprise customers, SOC2, or after adding
tenant-scoped features.
**Time:** 2-3 hours.
**Output:** Tenant isolation report + remediation plan.

```
# Multi-Tenant Isolation Audit: [Project Name]

Apply the security-audit-for-saas skill with focus on multi-tenant boundary
enforcement.

## Setup
Spin up a test environment with 2 tenants:
- Tenant A: "Acme Corp" with user `alice@acme.test`
- Tenant B: "Widget Inc" with user `bob@widget.test`
- Each has sample data (users, resources, settings, billing)

## Phase 1: RLS Coverage (30 min)
1. Run scripts/rls-coverage.sql — find tables without RLS policies
2. For each table, verify:
   - RLS enabled
   - Policies cover SELECT, INSERT, UPDATE, DELETE
   - Subqueries don't reference tables with conflicting RLS
   - WITH CHECK present on mutations
   - Service role has explicit separate policy

## Phase 2: App-Layer Checks (45 min)
Grep for `requireOrgRole`, `requireOrgPermission`, `checkOrgAccess`.
For each route:
1. Does it call the check?
2. Does it check against the EXACT resource's orgId (not session default)?
3. Is the check inside a transaction with the operation?

## Phase 3: Cross-Tenant Attack Attempts (1 hour)
As Alice (Tenant A), try to:
1. Read Bob's data via direct API call
2. Read Bob's data via Supabase anon key + raw query
3. Modify Bob's data via PATCH
4. Delete Bob's data via DELETE
5. List Bob's resources via search
6. Infer Bob's data via aggregate queries
7. Access Bob's cached data via shared cache
8. Read Bob's files via S3 or similar

For each attempt: DOCUMENT the status code, response body, and whether the attack
succeeded.

## Phase 4: Shared Resources (30 min)
- Templates, skill packs, public profiles
- Each must have explicit `visibility` field
- Verify: public → visible to all; org → visible to org only; private → visible
  to author only

## Phase 5: Aggregate Queries (30 min)
- Every public dashboard query
- Does it leak other-tenant data by inference?
- Can it be polled to extract growth rate, user count, etc.?

## Phase 6: Deletion Cascade (15 min)
- Delete Tenant A
- Verify ALL Tenant A data removed from ALL tables
- Verify external services cleaned up

## Report
- Tables without RLS
- Routes without app-layer checks
- Successful cross-tenant attacks
- Aggregate inference vectors
- Missing deletion cascades
- Recommendation: fix before enterprise launch
```

---

## Archetype 5: The Creative Red Team Exercise

**Use when:** Regular checklist audits aren't finding anything new. You want to
find the novel, non-obvious vulnerabilities.
**Time:** 4-8 hours.
**Output:** Novel attack chains + creative remediation.

```
# Creative Red Team Exercise: [Project Name]

Apply the security-audit-for-saas skill in pure creative mode. Skip the
checklists. Use the operators and creativity triggers to find non-obvious bugs.

## Phase 1: Creative Priming (20 min)
Read references/CREATIVITY-TRIGGERS.md start to finish. For each prompt, jot
a 1-line note on what might apply to this project. Don't investigate yet.

## Phase 2: Impossible Questions (30 min)
Write 20 questions you believe have no answer about this system. Examples:
- Can a deleted user still receive webhooks?
- Can the OG-image endpoint leak user data?
- Can a free user's subscription status flip to active without a payment event?
- Can an admin accidentally demote the owner and lock out the org?

For each, search the code for the answer. Trust the code, not your belief.

## Phase 3: Attacker Personas (1 hour)
Apply operator ⊕ Creative-Transposition. Re-audit from 5 personas:
1. Bored user — what edge cases?
2. Financial fraudster — how to get free service?
3. Competitor — how to exfiltrate?
4. Disgruntled ex-employee — what backdoors?
5. Nation-state — what persistence?

For each persona, pick the top 3 attacks you'd try. Actually try them.

## Phase 4: Operator Chains (1 hour)
Apply compound operator chains:
1. ⊘ Surface-Transpose → ⟂ Fail-Open Probe
2. ⊙ Identity-Chain → ≡ Invariant-Extract
3. ≡ Normalize-First → ✂ Parser-Diverge
4. ⊘ Shadow-Codebase → ⊙ Tenant-Leak
Each finds bugs neither operator alone would.

## Phase 5: The Trust Assumption Inversion (30 min)
List every "this is safe because X" assumption. For each X:
- What if X is wrong?
- Who could make X wrong?
- How easy is it?

## Phase 6: Attack Chain Composition (30 min)
Take any LOW/MEDIUM findings (existing or new). For each pair, ask:
- Does bug A enable bug B?
- Compose into an attack chain
- Could a chain become CRITICAL even though each bug alone is MEDIUM?

## Phase 7: The Meta-Questions (15 min)
- What would make the security team cry?
- What did the developer forget?
- What's "too obvious to check"?
- What breaks if the infrastructure is adversarial?

## Phase 8: Document (30 min)
For each novel finding:
- Attack scenario (step-by-step)
- Required preconditions
- Proof of exploitability
- Remediation
- Detection (how would you know if this happened?)

The goal is not a checklist report. The goal is 3-5 novel, non-obvious
vulnerabilities that a checklist would never find.
```

---

## When to Use Which Archetype

| Situation | Archetype |
|-----------|-----------|
| First time auditing this project | 1 (Comprehensive) |
| Preparing for public launch | 1 (Comprehensive) |
| Active security incident | 2 (Incident Response) |
| New billing feature rolled out | 3 (Billing-Focused) |
| Pre-enterprise / SOC2 | 4 (Multi-Tenant) |
| Regular audits finding nothing | 5 (Creative Red Team) |
| Post-incident "what else is broken" | 5 (Creative Red Team) |
| Quarterly security review | Mix: Archetypes 4 + 5 |
| Weekly PR review | Targeted parts of Archetype 1 |

---

## Customizing Prompts

Each archetype is a starting point. Customize by:
- Replacing [Project Name] with the real name
- Adding domain-specific checks (e.g., HIPAA for healthcare)
- Narrowing scope if time is limited
- Adding project-specific test fixtures or credentials

The prompts are designed to be copy-paste into a Claude Code session at the
start of an audit. They reference other files in the skill; Claude will read
them on demand.
