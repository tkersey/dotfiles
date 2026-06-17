---
name: context-bounded-verification
description: "Use for nontrivial code changes, refactors, bug fixes, PR reviews, AI-generated edits, blast-radius analysis, verification planning, regression tests, rollout/rollback, closure/readiness claims, handoffs, or correctness under incomplete context/hidden constraints. Not for textual edits or trivial formatting unless risk analysis is requested. Alias: context-bound-verification."
---

# Context-Bounded Verification

## Purpose

Convert an unbounded software-correctness question into a bounded, reviewable, testable, and observable claim about the current artifact state.

The goal is not global proof. The goal is to reduce the verification gap by making scope, artifact state, assumptions, blast radius, evidence, validation, and residual risk explicit enough that a human can audit the next action.

## Core rule

Never claim arbitrary code is globally "correct", "safe", "ready", or "done". Make a bounded claim:

> Given the current artifact state `[artifact_state_id]`, the inspected evidence `[evidence refs]`, the stated scope `[scope]`, and the checks actually run `[commands/results]`, this appears to satisfy `[specific property]`. Remaining uncertainty: `[specific gaps]`.

A claim is not actionable merely because it is plausible. A finding, fix, review comment, test result, subagent packet, or prior-session memory becomes actionable only when it is bound to the current artifact state and current workflow objective.

## Non-negotiable distinctions

Always separate these dimensions before implementation, handoff, closure, or a pass/fail decision:

| Dimension | Meaning | Anti-laundering rule |
| --- | --- | --- |
| Claim validity | The claim may be true. | Validity alone does not authorize code changes or closure. |
| Actionability | The current workflow should act on the claim now. | Requires current-state evidence, scope fit, and a permitted route. |
| Evidence | Concrete artifact, command, test, diff, log, or manual inspection. | Reviewer authority, intuition, memory, and prior sessions are not proof by themselves. |
| Artifact state | The exact tree/diff/PR/checkout that was inspected. | Old-tree evidence cannot prove the delivered tree after edits. |
| Direction/scope fit | The claim advances the current objective and does not violate non-goals. | Locally correct work is blocked if it pursues the wrong objective. |
| Criticality/severity | The accepted materiality after evidence review. | Asserted severity, CAS labels, or reviewer pressure do not auto-escalate to implementation. |
| Proof/validation | Checks that can confirm or falsify the claim. | Green unrelated checks are not proof for the changed behavior. |
| Closure/readiness | A bounded decision that enough proof exists for the next step. | Closure is not actual correctness; it must state residual risk. |
| Material findings | Issues that can change correctness, safety, compatibility, or closure. | Preference-only or review-closure-only concerns do not become implementation work. |
| Root authority | Decisions owned by the primary agent. | Subagents provide evidence, not final permission. |

## Triage gate

Classify before implementation, review closure, handoff, or broad validation.

Default to the lowest tier that honestly fits the evidence. Escalate when the change touches public contracts, persisted data, auth, billing, infrastructure, migrations, async jobs, scheduled work, irreversible behavior, customer-visible semantics, proof/certificate surfaces, generated artifacts, or cross-repo compatibility.

| Tier | Shape | Required output |
| --- | --- | --- |
| Tier 0: Mechanical | Formatting, comment cleanup, compiler-supported rename, dead-code removal with no behavioral surface. | One compact verification note. No full packet unless closure/handoff is requested. |
| Tier 1: Local behavioral | Small bug fix, single-function behavior, isolated UI/parser logic, narrow test repair. | Compact Verification Note; include callers/tests checked and residual risk. |
| Tier 2: System-affecting | API/schema/serialization/proof/generator/checker/queue/cache/cron/authz/billing-adjacent/runtime behavior, broad PR review, readiness/merge claims. | Full Verification Packet and mechanical gate before closure or implementation handoff. |
| Tier 3: High-risk or irreversible | Security controls, permissions, data deletion, privacy/compliance, payments, irreversible migrations, production infra, public contract breakage. | Plan first. Require explicit authorization before destructive or production-affecting implementation. Full packet plus owner questions/approval points. |

Tier is root-owned. A subagent may recommend escalation or de-escalation, but the root must declare the final tier and rationale.

## Invocation behavior

When this skill is active:

1. Bind work to the current artifact state before making a proof, readiness, or handoff claim.
2. State the current workflow objective, semantic change, in-scope set, out-of-scope set, and done condition.
3. Treat absent context as risk, not permission.
4. Inspect dependency surfaces, not only the edited or reviewed file.
5. Keep changes minimal and aligned with the stated objective.
6. Separate validation-only work, proof-only closure, no-change outcomes, and implementation work.
7. Add or identify tests that encode material invariants when the tier warrants it.
8. Run relevant checks when practical; never say tests passed unless they actually ran and passed.
9. Gate Tier 2/Tier 3 closure, readiness, and implementation handoff with the checker packet.
10. End with output scaled to tier, but never compress away state, evidence, blockers, or residual risk.

## Root-owned authority

The root agent owns and cannot delegate:

- current workflow objective and scope boundary;
- tier declaration and escalation/de-escalation rationale;
- artifact-state acceptance after edits or checkout changes;
- destructive, security-sensitive, billing-sensitive, or production-affecting authorization checks;
- final readiness/closure/pass decision;
- final implementation or workflow handoff route;
- whether a subagent packet matches the current artifact state and scope.

Subagents may supply bounded evidence packets. A subagent packet can clear a narrow uncertainty, veto a route, or mark an issue unresolved. It cannot authorize implementation, broaden scope, close the task, or waive missing proof.

## Authority fanout

Use read-only subagents only when parallelization or authority separation materially improves the decision. Do not spawn generic reviewers. Use bounded roles:

- `context_evidence_authority`: confirms whether claims are grounded in current artifacts and current evidence.
- `context_scope_direction_authority`: checks current objective fit, non-goals, and stale/wrong-objective plan pressure.
- `context_blast_radius_authority`: maps contract, operational, downstream, and rollback surfaces.
- `context_closure_authority`: audits proof adequacy, residual risk, and closure/readiness consistency.

Fanout is recommended for Tier 2/Tier 3 work when any of these are true:

- a closure/readiness claim spans multiple files, generated artifacts, proof surfaces, or runtime contracts;
- a review or CAS finding could become implementation work but its scope/evidence is contested;
- prior-session, memory, or stale plan state is influencing the route;
- proof success might be unrelated to the changed behavior;
- blast radius is wider than the edited file.

Fanout is not needed for routine Tier 0/Tier 1 work with direct evidence and low residual risk. If fanout is used, the final packet must include each accepted subagent packet and all vetoes/unresolved items.

## Workflow

### 1. Verification preflight

Before editing or declaring readiness, establish:

```yaml
verification_preflight:
  packet_version: CBV-GATE-v1
  mode: implementation | review | closure | verification | validation-only | no-change | handoff | audit
  artifact_state_id: "commit/diff/checksum/PR/head/base or explicit current-tree label"
  current_workflow_objective: "..."
  semantic_change: "..."
  tier: tier0 | tier1 | tier2 | tier3
  scope_fit: aligned | partial | conflicting | unknown
  proof_route: tests | typecheck | build | manual-diff | runtime-observation | validation-only | blocked
  gate_required: yes | no
```

`gate_required` is `yes` for Tier 2/Tier 3, for any implementation handoff, for closure/readiness/pass claims, for review findings promoted into changes, and whenever current-state evidence is materially contested.

### 2. Gather local context

Inspect the surrounding implementation before changing or closing:

- target files and adjacent modules;
- direct callers/callees and public entry points;
- tests covering target behavior and invariants;
- package/build/test scripts;
- type definitions, schemas, serializers, generated files, fixtures;
- docs, comments, ADRs, runbooks, migration notes;
- recent relevant commits/PR notes when available;
- companion workflow outputs only after freshness and objective fit are checked.

Use repository evidence (`rg`, language references, package scripts, test discovery, diff/commit/PR inspection) over prompt-only assumptions.

### 3. Map blast radius

For each proposed claim or change, check affected surfaces:

- public API shape, status codes, headers, request/response schemas;
- database schemas, migrations, constraints, indexes, backfills;
- serialized formats, snapshots, generated clients, source maps, certificates;
- caches, queues, retries, idempotency, scheduled jobs, webhooks;
- authn/authz, permissions, secrets, security boundaries;
- billing, payments, metering, entitlements, quotas;
- localization, formatting, time zones, currency, dates;
- mobile clients, SDKs, CLIs, downstream services;
- observability: logs, metrics, traces, alerts, dashboards;
- performance, concurrency, race conditions, memory use;
- feature flags, environment-specific behavior, deployment order;
- backward compatibility and rollback behavior.

If blast radius is unknown and material, do not close as pass. Narrow, validate, or block.

### 4. Surface tacit constraints

Look for constraints not encoded in the local code path:

- comments explaining odd behavior;
- incident references, hotfix markers, customer-specific branches;
- runbooks and deployment notes;
- old tests preserving strange behavior;
- feature flags with operational meaning;
- business rules, date/time restrictions, compliance language;
- staging-vs-production differences.

If organizational context is unavailable, list human questions rather than inventing answers.

### 5. Choose the smallest safe route

Allowed routes:

| Route | Use when | Required evidence |
| --- | --- | --- |
| `implement` | A current-state, in-scope defect/change is actionable now. | Current artifact evidence, scope fit, proof route, no blocking veto. |
| `validate-only` | Claim is plausible but not yet actionable. | Specific falsifiable validation step and expected decision delta. |
| `proof-only` | Artifact already changed or issue is already fixed, but closure proof is needed. | Current-state proof target and no mutation agenda. |
| `no-change` | Concern is unsupported, out of scope, stale, preference-only, or defeated by current artifacts. | Evidence or explicit missing-evidence rationale. |
| `defer` | Valid concern belongs outside current objective or requires owner decision. | Owner/condition needed before action. |
| `blocked` | Safe action cannot proceed without missing context, authorization, or proof. | Concrete blocker and required unblock condition. |

Do not use a valid concern to launder a wrong fix, broad refactor, unrelated cleanup, or premature closure.

### 6. Implement with traceability

While editing:

- keep the patch focused;
- avoid unrelated formatting churn;
- avoid speculative fixes;
- preserve generated-file workflows;
- record material assumptions;
- check `git diff` before finalizing;
- rerun required proof after any checkout or patch change;
- update fixtures/examples/runtime artifacts that construct the same proof surface.

For generated artifacts, certificates, source maps, quota counters, policy switches, allowlists, capability gates, and verifier/checker changes, verify the exact evidence surface carried by the delivered artifact. Presence-only witnesses, caller-provided override hashes, unrelated summary counts, broad allow flags, or cardinality-only checks are not proof of identity, ownership, route position, target coordinate, or policy support.

When verifier strength is the finding, a green suite is insufficient by itself. Re-read the changed predicate and add or identify a negative fixture that would fail the too-weak version.

### 7. Verify with evidence

Use the strongest practical evidence available:

- failing repro before fix and passing regression after fix;
- targeted tests for changed behavior;
- tests for invariants that must not change;
- type checks, lint, build, formatting;
- integration/e2e checks for cross-boundary changes;
- runnable examples or generated commands that construct the same artifact/proof surface;
- migration dry-runs or schema validation;
- manual diff review for public contracts and side effects;
- runtime/log/metric observation for operational behavior.

If tests cannot be run, state exactly why and downgrade closure to `validation-only`, `defer`, or `blocked` unless manual evidence is genuinely sufficient for the tier.

### 8. Mechanical gate

For Tier 2/Tier 3, implementation handoff, closure/readiness/pass, or contested evidence, emit or save a `verification_packet` and run:

```bash
python codex/skills/context-bounded-verification/tools/context_verification_gate.py path/to/packet.md
```

The checker validates output shape, current-state binding, evidence/actionability separation, direction fit, blast-radius coverage, validation proof, authority packet handling, closure consistency, and handoff safety. It cannot prove semantic correctness; it blocks laundering weak or stale claims into pass, implementation, or handoff.

## Output contracts

### Tier 0 compact note

```markdown
Verified: checked current diff `[artifact_state_id]`; no behavioral files changed. Remaining risk: low, limited to review oversight.
```

### Tier 1 compact verification note

```markdown
## Compact Verification Note

- Artifact state: `[current tree/diff/commit]`
- Intended change: `[specific behavior]`
- Scope checked: `[files/callers/tests]`
- Verification performed: `[commands/tests/manual checks]`
- Actionability: `implement | validate-only | proof-only | no-change | defer | blocked`
- Remaining risk: `[specific residual risk]`
```

### Tier 2/Tier 3 verification packet

Use this shape for gated outputs. YAML or JSON is acceptable.

```yaml
verification_packet:
  packet_version: CBV-GATE-v1
  skill: context-bounded-verification
  mode: implementation | review | closure | verification | validation-only | no-change | handoff | audit
  objective:
    current_workflow_objective: "..."
    semantic_change: "..."
    done_condition: "..."
  artifact_state:
    state_id: "commit/diff/checksum/PR/head/base/current-tree label"
    source: current-tree | current-diff | pull-request | supplied-snippet | prior-session | unknown
    freshness: current | stale | superseded | unknown
    dirty_state: clean | dirty | unknown | not-applicable
    evidence_refs: []
  tier:
    declared: tier0 | tier1 | tier2 | tier3
    drivers: []
    rationale: "..."
  scope:
    in_scope: []
    out_of_scope: []
    must_not_change: []
  direction_fit:
    current_objective_fit: aligned | partial | conflicting | unknown
    direction_source: user-current-instruction | plan | pr-body | issue | repo-convention | current-artifact | unknown
    stale_or_wrong_objective_pressure: []
  evidence_ledger:
    - id: E1
      claim: "..."
      claim_type: validity | actionability | scope | risk | proof | closure
      evidence_kind: current-artifact | current-diff | current-test | current-ci | current-command | manual-inspection | runtime-observation | prior-session | memory | reviewer-claim | none
      evidence_ref: "file:line, command, test, log, diff, or concrete artifact ref"
      artifact_state_match: yes | no | unknown
      supports: yes | partial | no | unknown
      actionability: implement | validate-only | proof-only | no-change | defer | blocked | closure-pass | none
  blast_radius:
    surfaces_checked:
      - name: "public-api | schema | serialization | generated-artifact | auth | billing | queue | cache | rollout | rollback | ..."
        status: checked | not-applicable | unchecked | unknown
        evidence_ref: "..."
    unchecked_material_surfaces: []
  validation:
    commands:
      - command: "..."
        result: pass | fail | not-run | skipped
        evidence_ref: "..."
        artifact_state_match: yes | no | unknown
    tests_added_or_updated: []
    negative_or_counterexample_checks: []
    proof_surface_changed: yes | no | unknown
    test_gap_reason: "..."
  authority:
    root_owned:
      - tier-decision
      - scope-boundary
      - artifact-state-acceptance
      - final-readiness
      - implementation-authorization
      - handoff-routing
    fanout:
      required: yes | no
      reason: "..."
    subagent_packets: []
  closure:
    readiness: pass | pass-with-residual-risk | validate-only | proof-only | no-change | defer | blocked
    closure_claim: "..."
    blockers: []
    remaining_risk: []
    next_action: "..."
  handoff:
    allowed: yes | no
    target: none | accretive-implementer | fixed-point-driver | review-adjudication | verification-closure | human-owner | other
    agenda: []
    must_not_do: []
```

## Review mode

When reviewing an existing diff or PR, do not rewrite immediately. First produce:

1. current artifact state and diff/PR basis;
2. intended behavior inferred from the diff;
3. files/contracts touched;
4. likely blast radius;
5. missing tests or weak evidence;
6. suspicious behavior changes;
7. human questions;
8. minimal patch or validation route, if any.

Focus review comments on semantic risk, proof weakness, and contract drift, not style preferences. A finding may be material but still `validate-only`, `proof-only`, `no-change`, `defer`, or `blocked`.

## Human-question template

```markdown
Before this is safe to merge, a human owner should answer:
1. Does any downstream system depend on [contract/format/side effect]?
2. Is [odd existing behavior] intentional or historical accident?
3. Are there deployment windows, customer commitments, or compliance rules for this path?
4. Are staging fixtures representative of production for [edge case]?
5. Who owns rollback if [failure mode] appears after deploy?
```

## Pause / block conditions

Pause, block, or provide only a plan when the requested action would:

- delete or migrate production data irreversibly;
- weaken authentication, authorization, audit, privacy, or compliance controls;
- alter billing, payments, entitlements, quotas, or metering;
- change public API contracts without compatibility guidance;
- bypass tests or safety checks to ship faster;
- require secrets, credentials, or privileged production actions;
- close a task using stale, prior-session, memory-only, reviewer-only, or wrong-objective evidence;
- hand off implementation without current-state evidence and scope fit.

## Success criteria

A successful use leaves the user with:

- a narrow implementation, review result, validation route, no-change decision, or explicit block;
- current artifact state and scope boundaries;
- visible blast-radius reasoning;
- concrete evidence and checks actually run;
- named unknowns rather than hidden assumptions;
- residual risk stated at the same granularity as the claim;
- a mechanically checkable packet whenever the result gates implementation, closure, readiness, or handoff.

## Resources

- [gate-contract.md](references/gate-contract.md)
- [verification-output-contract.md](references/verification-output-contract.md)
- [authority-model.md](references/authority-model.md)
- [example-invocations.md](references/example-invocations.md)
- [adversarial-eval-seeds.md](references/adversarial-eval-seeds.md)
