---
name: context-bounded-verification
description: "Use for nontrivial code changes, refactors, bug fixes, PR reviews, AI-generated edits, blast-radius analysis, verification planning, regression tests, rollout/rollback, or correctness under incomplete context/hidden constraints. Do not use for textual edits or trivial formatting unless risk analysis is requested."
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
- Treat verification evidence as bound to the exact tree it inspected. If the
  checkout changes after a check starts or before you report it, rerun the
  required proof on the new tree; old-tree output may explain confidence, but it
  is not proof for the delivered change.
- For generator/verifier or certificate/proof changes, trace the exact evidence
  surface carried by the delivered artifact. Do not validate route-specific
  target semantics by reusing stale source fields when the artifact lacks the
  data needed to replay the generator; require an explicit witness field or
  choose a fail-closed predicate that the artifact can honestly prove. A
  presence-only optional witness is not proof when the invariant needs a
  specific target ref, fingerprint, protocol operation, route position, or site
  coordinate. For mapping or provider-support witnesses, bind the full selected
  relation: selected plan, selected provider/offer/program refs, route or offer
  occurrence, mapping fingerprint, effect-shape proof, declared request/result
  mapping, and policy support as applicable.
- When a certificate, proof, or generated artifact binds a compiled plan hash,
  residual id, normalized artifact hash, or dependency fingerprint, recompute it
  from the artifact that owns that value. Do not accept caller-provided override
  hashes as proof of compiled output identity unless a separate verified path
  ties the override to the actual compiled artifact.

### 7. Verify with evidence

Use the strongest practical evidence available:

- targeted regression tests for the changed behavior
- tests for invariants that must not change
- type checks, lint, build, and formatting checks
- integration or end-to-end tests for cross-boundary changes
- runnable examples, demos, or generated commands that construct the same
  artifact or proof surface
- migration dry-runs or schema validation where applicable
- manual diff review for public contracts and risky side effects

When fixing a bug, prefer to demonstrate the bug with a failing test first, then show that the test passes after the fix.

When a proof, witness, schema, or certificate contract changes, update every
checked example or runtime fixture that constructs the same artifact, not only
unit tests. If those examples are part of the repository's proof surface, run
their commands and verify their observable output.

When a review finding is about verifier strength, a green suite is not enough
by itself. Re-read the changed predicate and add or identify a negative fixture
that would fail the too-weak version, especially for "exists" checks that should
prove equality, ownership, or route-specific support.

If the new regression trips an upstream precondition, do not weaken the
invariant being reviewed. Adjust only the orthogonal fixture coordinate needed
to satisfy that precondition, then keep the target proof strict and rerun the
same proof path.

For policy limits, quotas, counters, and thresholds, verify the measured
dimension, not just the numeric comparison. A depth limit, count limit,
fanout limit, retry limit, byte limit, or occurrence limit should have fixtures
that distinguish the dimensions it can be confused with, such as wide-shallow
versus deep-narrow structures. If the metric is recursive or derived, compute
and test the same traversal, coordinate space, and ownership rule that defines
the policy; a boolean "has children" proxy is not a depth proof. When a
certificate, source map, proof, or generated artifact must enforce that metric,
the artifact must carry a metric witness or recomputable evidence surface;
do not validate one metric from an unrelated summary count.

For policy allowlists or capability gates, verify the authority-bearing identity,
not only an allow flag, enum tag, or object kind. Host-intrinsic, provider,
world-port, ACL, entitlement, and feature-policy checks should require the
domain-owned ref or capability the policy is meant to authorize, with a negative
fixture proving a same-kind but wrong-domain/wrong-ref object is rejected.

For fail-closed policy switches, verify that partial, blocker, audit-only, or
best-effort paths cannot bypass the switch unless the same policy object owns an
explicit exception. A flag such as "fail on unsupported" must be checked before
accepting a partial certificate/blocker artifact, with a negative fixture that
proves the partial path still rejects when the fail-closed switch is enabled.

For generated artifacts with summaries, counters, source maps, or certificates,
verify the projections too. Counts should come from the emitted disposition in
the delivered artifact, not from an earlier selected route category that may be
lowered, blocked, residualized, or redirected before emission.
For partial or blocked artifacts, unsupported/blocked counts must match the
actual emitted blocked source-map entries they claim to summarize. Do not use a
total report blocker count, overcount tolerance, or unrelated summary field as
proof for source-map blocker evidence; add an overcount regression when tightening
this check. Keep source-shape map entries, blocked entries, unsupported blocked
source shapes, and direct/root blockers as separate dimensions unless one is
explicitly derived from another by the artifact contract. Do not infer "not a
source effect" solely from a missing shape ref when the emitted disposition, such
as a lowered world-port entry, still represents a source effect; reserve
domain/ref discrimination for the entry classes that actually require it. When
the primary shape/effect ref is absent and the entry has no static-plan owner,
bind the entry to the owning fallback evidence ref used by generation, such as
the world-port ref, and verify the certificate checker uses the same fallback.
For static-plan-owned morphism entries, verify the target shape and plan binding
instead of forcing the direct world-port fallback.

When a generated projection merges multiple source collections, verify
completeness across all of them. A nonempty primary collection such as static
plans, selected routes, or generated entries must not suppress independent
report-level, nested, provider, residual, or blocker entries. De-duplicate only
items that are actually represented by another emitted entry, and add or
identify a mixed-source regression fixture.

When a generated-artifact test expectation changes while the generator,
reporter, or certificate checker is still being repaired, treat the new
expectation as diagnostic until the root cause is fixed. Before delivery,
re-check that the final assertion proves the intended semantic projection:
cardinality-only checks are insufficient for identity-bearing refs unless an
adjacent checker proves exact membership, ownership, or target coordinate.

When a verifier fix changes route semantics, audit sibling branches in the same
predicate family. A target-shape rule fixed for shape-only lowering can still be
missing from host-intrinsic, pipeline, provider-program, or blocker paths that
reuse the older source-shape assumption.

When adding or validating a shortcut, early return, lowering bypass, or
shape-only/world-port path, verify it still executes the proof obligations owned
by the selected route semantics before it skips the normal path. A route lowered
to a simpler emitted form may still need morphism, adapter, provider, mapping,
or dependency evidence to prove that lowering is authorized.

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
