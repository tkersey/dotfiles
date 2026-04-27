---
name: context-bounded-verification
description: Use for nontrivial code changes, refactors, bug fixes, PR reviews, AI-generated edits, blast-radius analysis, verification planning, regression testing, rollout/rollback planning, and any task where correctness depends on incomplete context or hidden system constraints. Do not use for purely textual edits or trivial formatting-only changes unless the user asks for risk analysis.
---

# Context-Bounded Verification

## Purpose

Convert an unbounded software-correctness question into a bounded, reviewable, testable, and observable change.

Use this skill whenever code behavior, system safety, or downstream compatibility could be affected by a proposed change. The goal is not to prove global correctness. The goal is to reduce the verification gap by defining scope, surfacing hidden assumptions, analyzing blast radius, adding evidence, and clearly reporting residual risk.

## Core rule

Never claim that arbitrary code is "correct" or "safe" in the global sense. Instead, make a bounded claim:

> "Given the inspected files, stated assumptions, tests run, and unchanged interfaces listed below, this change appears to satisfy [specific property]. Remaining uncertainty: [specific gaps]."

## Triage gate

Before using the full workflow, classify the change as Tier 0, Tier 1, Tier 2, or Tier 3. Default to the lowest tier that honestly fits the evidence. Escalate the tier when a change touches public contracts, persisted data, auth, billing, infrastructure, migrations, async jobs, scheduled work, irreversible behavior, or customer-visible semantics.

Scale effort and output to risk:

| Tier | Use full workflow? | Final output |
| --- | --- | --- |
| Tier 0: Mechanical | No. Inspect the diff and run obvious checks when practical. | One short verification note. No full Verification Gap Report. |
| Tier 1: Local behavioral | Partially. Inspect callers and focused tests. | Compact report: intended change, callers checked, tests run, remaining risk. |
| Tier 2: System-affecting | Yes. | Full Verification Gap Report with rollout/rollback notes. |
| Tier 3: High-risk or irreversible | Plan first. Do not implement irreversible, security-sensitive, billing-sensitive, or production-affecting changes without explicit authorization. | Full Verification Gap Report, plus owner questions or approval points. |

The skill should reduce uncertainty without turning low-risk edits into governance rituals.

## Invocation behavior

When this skill is active:

1. Prefer a scoped plan before editing unless the task is clearly Tier 0.
2. Keep changes minimal and aligned with the stated semantic goal.
3. Explicitly state what must not change.
4. Inspect the dependency surface, not only the edited file.
5. Treat absent context as risk, not as permission to assume.
6. Add or update tests that encode important invariants when the tier warrants it.
7. Run relevant checks when available.
8. End with an output scaled to the triage tier.

## Risk tiers

Classify the task before implementation or review.

### Tier 0: Mechanical

Examples: formatting, comment cleanup, rename with compiler support, dead-code removal with tests.

Expected behavior: proceed directly, check the diff, and avoid a full Verification Gap Report unless the user explicitly asks for one.

### Tier 1: Local behavioral

Examples: small bug fix, single-function change, isolated UI behavior, targeted parser change.

Expected behavior: inspect callers and tests; add or update focused tests; produce a compact report.

### Tier 2: System-affecting

Examples: API contract change, schema or migration work, queue/job behavior, caching, cron/scheduled jobs, authz/authn logic, billing-adjacent code, data import/export, feature flags, performance-sensitive paths.

Expected behavior: plan first, identify blast radius, preserve compatibility where possible, add regression tests, and provide a full Verification Gap Report with rollout/rollback notes.

### Tier 3: High-risk or irreversible

Examples: payments, billing, security controls, permissions, data deletion, privacy/compliance, production infrastructure, migrations that cannot be safely reversed, public API compatibility, customer-visible contractual behavior.

Expected behavior: do not silently proceed with destructive or irreversible edits. Produce a plan and identify owner questions or approval points. If explicitly authorized to implement, keep the patch narrow and include strong verification, monitoring, and rollback guidance.

## Workflow

Use the full workflow for Tier 2 and Tier 3 tasks. For Tier 0 and simple Tier 1 tasks, compress the workflow to the relevant checks and keep the response lightweight.

### 1. Define the semantic change

Before editing, write a short intent statement:

- What behavior should change?
- What behavior must remain unchanged?
- What files/components are in scope?
- What files/components are out of scope?
- What would count as completion?

If the user gives incomplete instructions, infer the smallest reasonable scope and mark assumptions explicitly.

### 2. Gather local context

Inspect the surrounding implementation before modifying code:

- target files and adjacent modules
- direct callers and callees
- tests covering the target behavior
- package/build/test scripts
- type definitions, schemas, serializers, config, generated files
- documentation, comments, TODOs, ADRs, runbooks, migration notes
- recent relevant commit messages or PR notes if available

Use search tools such as `rg`, language-aware references, package scripts, and test discovery. Do not rely only on the user prompt if repository evidence is available.

### 3. Map the blast radius

For each proposed change, ask what it might affect indirectly.

Check for impact on:

- public API shape, status codes, headers, request/response schemas
- database schemas, migrations, constraints, indexes, backfills
- serialized formats, snapshots, fixtures, generated clients
- caches, queues, retries, idempotency, scheduled jobs, webhooks
- authn/authz, permissions, secrets, security boundaries
- billing, payments, metering, entitlements, quotas
- localization, formatting, time zones, currency, dates
- mobile clients, SDKs, CLIs, downstream services
- observability: logs, metrics, traces, alerts, dashboards
- performance, concurrency, race conditions, memory use
- feature flags, environment-specific behavior, deployment order
- backward compatibility and rollback behavior

If the blast radius is unknown, say so and narrow the change.

### 4. Surface tacit constraints

Look for knowledge that may not be encoded in the code path:

- comments explaining ugly or surprising code
- incident references, hotfix markers, customer-specific branches
- runbooks and deployment notes
- old tests preserving strange behavior
- feature flags with operational meaning
- date/time restrictions, business rules, compliance language
- staging-vs-production differences

If external organizational context is unavailable, produce a concise "human questions" list instead of inventing answers.

### 5. Design the smallest safe change

Prefer changes that:

- preserve external contracts
- minimize touched files
- avoid opportunistic refactors
- preserve existing ordering, defaults, and side effects unless intentionally changed
- keep compatibility shims where needed
- add assertions or guards near the boundary of the change
- make hidden assumptions explicit in tests or comments

Do not upgrade dependencies, change broad architecture, rewrite unrelated modules, or alter public behavior merely because it seems cleaner.

### 6. Implement with traceability

While editing:

- keep the patch focused
- avoid unrelated formatting churn
- avoid speculative fixes
- preserve generated-file workflows
- record any assumption that materially shaped the change
- check `git diff` before finalizing

### 7. Verify with evidence

Use the strongest practical evidence available:

- targeted regression tests for the changed behavior
- tests for invariants that must not change
- type checks, lint, build, and formatting checks
- integration or end-to-end tests for cross-boundary changes
- migration dry-runs or schema validation where applicable
- manual diff review for public contracts and risky side effects

When fixing a bug, prefer to demonstrate the bug with a failing test first, then show that the test passes after the fix.

If tests cannot be run, state exactly why and what command should be run by a human.

Never say tests passed unless they actually ran successfully.

### 8. Produce proportionate output

Match the final output to the triage tier.

For Tier 0 tasks, use a single compact note:

```markdown
Verified: checked diff; no behavioral files changed. Remaining risk: low, limited to formatting/review oversight.
```

For Tier 1 tasks, use a compact report:

```markdown
## Compact Verification Note

- Intended change: [specific behavior changed]
- Scope checked: [files/callers/tests inspected]
- Verification performed: [commands/tests/manual checks]
- Remaining risk: [specific residual risk]
```

For Tier 2 and Tier 3 tasks, end with this full structure:

```markdown
## Verification Gap Report

### Intended change
- [Specific behavior changed]

### Scope boundaries
- In scope: [files/components]
- Out of scope: [files/components/behaviors intentionally untouched]

### Preserved invariants
- [Behavior or contract expected to remain unchanged]

### Blast-radius review
- Direct callers checked: [yes/no + details]
- Data/API contracts checked: [yes/no + details]
- Operational surfaces checked: [queues/cache/cron/logs/etc.]

### Tacit-context gaps
- [Unknowns, missing owner knowledge, docs not found, external constraints]

### Verification performed
- [Commands run and results]
- [Tests added/updated]
- [Manual inspections]

### Remaining risk
- [Concrete residual risks, not vague warnings]

### Rollout / rollback notes
- [Feature flags, deployment ordering, monitoring, rollback plan if relevant]
```

## Review mode

When reviewing an existing diff or PR, do not rewrite immediately. First produce:

1. Intended behavior inferred from the diff.
2. Files and contracts touched.
3. Likely blast radius.
4. Missing tests or weak evidence.
5. Suspicious behavior changes.
6. Questions for humans.
7. Recommended minimal patch, if any.

Focus review comments on semantic risk, not style preferences.

## Human-question template

Use when tacit context matters:

```markdown
Before this is safe to merge, a human owner should answer:
1. Does any downstream system depend on [contract/format/side effect]?
2. Is [odd existing behavior] intentional or historical accident?
3. Are there deployment windows, customer commitments, or compliance rules for this path?
4. Are staging fixtures representative of production for [edge case]?
5. Who owns rollback if [failure mode] appears after deploy?
```

## Refusal / pause conditions

Pause and ask for authorization, or provide only a plan, when the requested change would:

- delete or migrate production data irreversibly
- weaken authentication, authorization, audit, or privacy controls
- alter billing, payments, entitlements, quotas, or metering
- change public API contracts without compatibility guidance
- bypass tests or safety checks in order to ship faster
- require secrets, credentials, or privileged production actions

## Success criteria

A successful use of this skill leaves the user with:

- a narrow implementation or review
- explicit scope and non-goals
- visible blast-radius reasoning
- tests or verification evidence
- named unknowns rather than hidden assumptions
- a merge/deploy decision that is easier for a human to audit
