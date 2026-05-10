---
name: fixed-point-driver
description: Use this skill to drive exhaustive build-review-improve-verify workflows toward a material fixed point across accretive-implementer, adversarial-reviewer, review-adjudication, verification-closure, a routine default-on negative-ledger pass, and learnings-backed durable evidence. Trigger when a coding task needs full de novo re-litigation, proof-gated review closure, repeated build-review-improve loops, explicit negative-evidence pruning, optional read-only specialist subagents, signal-aware routing by soundness invariants foot-guns and complexity, a mandatory pre-closure one-change challenge, and a canonical closure handoff packet. Trigger for requests like harden this patch exhaustively, address PR reviews to closure, keep re-reviewing from scratch, find all impactful changes, adjudicate then implement accepted review work, drive this changeset to a fixed point, or avoid repeating failed routes. Do not trigger for trivial one-step tasks or when the user explicitly wants only a single narrow phase.
---

# Fixed-Point Driver

This skill coordinates the whole workflow until the artifact set reaches a **material fixed point**.

Companion skills:
- `review-adjudication` for deciding which review comments actually matter
- `accretive-implementer` for implementation and remediation
- `adversarial-reviewer` for full-scope challenge
- `verification-closure` for decisive proof and gating
- `negative-ledger` for routine query, map, capture, reopen, handoff, and negative-evidence pruning
- `learnings` for durable evidence-backed lessons and the preferred persistent source for reusable negative evidence

## Output modes
- **Standard**: full workflow state.
- **Fast**: only the route, current state, negative-ledger result, open gates, and exact next action.

## CLI-tail-weighted reporting
- Keep ledgers terse.
- End with **Final State** and **Do Next**.
- **Do Next** must be the last section.
- If the report is long, compress evidence before compressing the negative-ledger result, closure state, or exact next action.

## Global doctrine
Every phase inherits **UNSOUND**, **WITNESS-BEARING**, **PRESERVATION-AWARE**, **PROGRESS-AWARE**, **REFINEMENT-AWARE**, **MECHANISTIC**, **ACCRETIVE**, and **TRACEABLE** standards.

Additional orchestration pressure: **EXHAUSTIVE**, **DE NOVO**, **ADVERSARIAL**, **SATURATING**, **MATERIAL**, **FIXED-POINT**, **PARSIMONIOUS**, **INVARIANT-GRADED**, **HAZARD-SEEKING**, **CANONICAL**, **LEDGERIZED**, **HISTORY-AWARE**, **NEGATIVE-EVIDENCE-AWARE**, and **REOPENABLE**.

## Optional review-adjudication intake

If the user provides review comments or a prior adjudication result, you may start with **review-adjudication** before any implementation.

Rules:
- Treat adjudicated `Act On` items as routed work, not as unquestionable truth.
- Treat `Rebut`, `Defer / Out of Scope`, and `Need Evidence` as explicit workflow inputs.
- Only re-adjudicate if the rationale is stale, contradictory, or the artifact state has materially changed.
- If review-adjudication materially shapes the route, keep it visible in the Companion Skill Ledger through closure.

## Negative-ledger posture

`negative-ledger` is no longer rare or merely optional inside this workflow. For every non-trivial fixed-point run, perform a root-owned **Negative Ledger Pass** at routing preflight and refresh it before closure.

Default behavior:
- Run a root-owned negative-ledger `query`/`map` pass during routing preflight.
- Check current-run witnesses, fixed-point ledgers, review comments, `$learnings`, and repo history when available.
- Normalize any candidate failed attempt into the Negative Evidence Ledger.
- Mark negative evidence as `active`, `stale`, `superseded`, `reopened`, `unknown`, or `need-evidence`.
- Convert only active, witness-bearing, current-state-applicable entries into narrow exclusion rules.
- Emit a `no-applicable-negative-evidence` result when nothing applies; this still counts as a completed pass.
- Capture newly witnessed failed attempts, no-effect changes, regressions, reverts, review rejections, and strategy pivots when they are decision-shaping.
- Run a pre-closure `handoff` summary even when there are no active exclusions.

`negative-ledger` is advisory, not a veto authority. It may block closure only when active negative evidence binds the current artifact state and the route reused the disconfirmed path without satisfying reopening criteria.

## Routing preflight

Every Standard run must establish this compact preflight before implementation, fanout, or closure:

```yaml
routing_preflight:
  task_shape: narrow-review-comment | review-batch | implementation | remediation | hardening | audit | optimization | migration | unknown
  fixed_point_lane: direct-closure | targeted | expanded-targeted | swarm
  subagent_mode: off | targeted | swarm
  specialist_budget:
    planned: 0 | 1 | 2 | 3 | 4 | "5+"
    reason: "..."
  negative_ledger_required: yes
  negative_ledger_initial_mode: query | map | reopen | handoff
  companion_stack:
    review_adjudication: used | not-needed | root-equivalent | unavailable
    accretive_implementer: used | root-equivalent | not-needed | unavailable
    adversarial_reviewer: used | root-equivalent | not-needed | unavailable
    verification_closure: used | root-equivalent | not-needed | unavailable
    negative_ledger: queried | mapped | captured | handoff | no-applicable-evidence | unavailable
    learnings: recalled | captured | not-material | unavailable
  stop_go_gate:
    proceed: yes | no
    blocking_reason: "none | ..."
```

Rules:
- `root-equivalent` means the root performed the stage's doctrine without a distinct auditable skill invocation.
- `used` means the stage was explicitly invoked or its required output packet was consumed.
- `not-needed` must be justified by task shape, not convenience.
- `unavailable` must include the exact registry, path, or tooling reason.
- `negative_ledger_required` is `yes` for every non-trivial fixed-point run, but the result may be `no-applicable-evidence`.
- If `$negative-ledger` tooling is unavailable, keep an in-session Negative Evidence Ledger and record `negative_ledger: unavailable`.

## Canonical ledgers

Maintain and refresh these ledgers after every meaningful pass:
- Findings Ledger
- Soundness Ledger
- Invariant Ledger
- Foot-Gun Register
- Complexity Ledger
- Verification Ledger
- Negative Ledger Pass
- Negative Evidence Ledger
- One-Change Challenge Ledger
- Companion Skill Ledger
- Specialist Briefing Ledger
- Specialist Value Receipts
- Residual Uncertainty
- Review Comment Ledger (optional, when review-adjudication is in the workflow)

Every meaningful pass must stamp the current `artifact_state_label`.
Every negative-ledger query, map, capture, reopen, or handoff must stamp the current `artifact_state_id`.

## Negative Ledger Pass

Use this root-owned shape at preflight, after material failed/remediated loops, and before closure:

```yaml
negative_ledger_pass:
  phase: preflight | post-remediation | post-review | pre-closure | capture | handoff
  mode: query | map | capture | reopen | handoff | none
  artifact_state_id: "..."
  topical_query: "4-8 task-defining terms"
  sources_checked:
    current_run: yes | no
    fixed_point_ledgers: yes | no
    learnings: yes | no
    repo_history: yes | no
    review_comments: yes | no
    user_context: yes | no
  result:
    active_exclusions: []
    stale_or_superseded: []
    reopened_candidates: []
    need_evidence: []
    no_applicable_negative_evidence_reason: "..."
    safest_next_frontier: "..."
  durable_capture: appended | duplicate-skip | not-material | unavailable | not-attempted
```

Preflight query terms should include the component, failure surface, benchmark/test when known, review-comment theme, hypothesis family, and invariant/hazard class.

When a compatible `learnings` CLI is available, run read-only recall before meaningful `query` or `map`:

```bash
run_learnings_tool recall --query "<component failure-surface test-or-benchmark hypothesis-family>" --limit 8 --drop-superseded
```

Treat recall/query hits as candidate evidence. A hit becomes active negative evidence only after its evidence anchors and current-state applicability are checked.

## Negative capture decision

After any failed check, no-effect attempt, benchmark regression, revert, review rejection, or strategy pivot, decide whether to capture:

```yaml
negative_capture_decision:
  witnessed_event: failed-test | no-effect | benchmark-regression | revert | review-rejection | strategy-pivot | none
  hypothesis: "..."
  attempted_change: "..."
  evidence_anchor: "command | log | benchmark | failing test | revert | review rationale | trace | diff | learning id"
  decision_shaping: yes | no
  transferable: yes | no
  counterfactual_value: yes | no
  capture: yes | no
  durable_writeback: append | duplicate-skip | not-material | unavailable | not-attempted
  reason: "..."
```

Capture only decision-shaping negative evidence. Do not record unevidenced hunches or one-off inconvenience as a reusable exclusion.

## Companion Skill Ledger

Every Standard run must include a companion ledger:

| Companion | Status | Evidence |
|---|---|---|
| `review-adjudication` | `used` / `not-needed` / `root-equivalent` / `unavailable` | one phrase |
| `accretive-implementer` | `used` / `root-equivalent` / `not-needed` / `unavailable` | one phrase |
| `adversarial-reviewer` | `used` / `root-equivalent` / `not-needed` / `unavailable` | one phrase |
| `verification-closure` | `used` / `root-equivalent` / `not-needed` / `unavailable` | one phrase |
| `negative-ledger` | `queried` / `mapped` / `captured` / `handoff` / `no-applicable-evidence` / `unavailable` | one phrase |
| `learnings` | `recalled` / `captured` / `not-material` / `unavailable` | one phrase |

Status rules:
- Do not mark a companion `used` unless there is an invocation, output packet, or contract-shaped section.
- Do not mark `not-needed` without a task-shape reason.
- Do not use `root-equivalent` for `negative-ledger`; use the negative-ledger statuses above.
- If a user explicitly asks for a named companion, `root-equivalent` is not enough unless the named skill is unavailable and the unavailability is recorded.

## Lane and subagent budget

Subagent mode is `off`, `targeted`, or `swarm`.
The root-owned Negative Ledger Pass does not count against specialist budget. `negative-ledger-mapper` does count.

Declare the current `fixed_point_lane` before launching specialists:

| Lane | Trigger | Specialist budget | Default subagent mode |
|---|---|---:|---|
| `direct-closure` | One narrow comment/change, obvious proof lane, no material route uncertainty | 0 | `off` |
| `targeted` | A read-heavy uncertainty could materially change the route | 1-2 | `targeted` |
| `expanded-targeted` | Coupled invariants, multi-surface proof, or two independent uncertainty classes | 3-4 | `targeted` |
| `swarm` | Broad/high-risk/exhaustive request, audit carryover, or explicit independent coverage | 5+ | `swarm` |

Rules:
- Default lane is `direct-closure` for narrow review-comment remediation.
- Escalate from `direct-closure` only when uncertainty is route-changing.
- Escalate from `targeted` to `expanded-targeted` only when the third specialist covers a distinct uncertainty class.
- Use `swarm` only when the task itself asks for exhaustive independent coverage or artifact risk justifies it.
- If actual specialist count exceeds the declared budget, record `budget_exception` with the material reason.
- Do not launch multiple specialists for the same uncertainty class unless the first packet was stale, transport-invalid, wrong-scope, or materially incomplete.
- Prefer root-owned negative-ledger query/map before launching `negative-ledger-mapper`.

## Budget exception gate

Before launching a specialist that would exceed the current lane budget, record:

```yaml
budget_exception:
  requested_extra_role: "..."
  current_lane: direct-closure | targeted | expanded-targeted | swarm
  current_specialist_count: 0
  budget_limit: 0
  distinct_uncertainty_class: yes | no
  why_root_cannot_resolve_locally: "..."
  expected_decision_delta: route | finding | proof | risk-retirement | negative-evidence-frontier | none
  approved: yes | no
```

Rules:
- If `expected_decision_delta: none`, do not launch the extra specialist.
- If `distinct_uncertainty_class: no`, do not launch the extra specialist unless replacing a stale or invalid packet.
- If `current_lane: direct-closure`, any specialist launch must first reclassify the lane.

## Negative-ledger-mapper escalation

Run `negative-ledger-mapper` from `$negative-ledger` when root-owned query/map finds material history pressure that would benefit from read-heavy mapping, including:
- multiple candidate failed routes
- stale or conflicting learnings
- benchmark regressions or optimization dead ends
- recurring review rejections
- repeated dead-end hypotheses
- search-heavy debugging, optimization, migration, or flaky-test terrain

The mapper may use read-only `learnings recall`, `learnings query`, or `learnings recent` as a source when available. Treat it as a read-only pruning specialist, not as a veto authority. The root still decides applicability, active exclusions, reopening criteria, and final closure.

## Swarm specialists

Use `swarm` only when justified by the lane rules. When custom agents are available, prefer:
- `evidence_mapper`
- `negative-ledger-mapper`
- `soundness_auditor`
- `invariant_auditor`
- `hazard_hunter`
- `complexity_auditor`
- `verification_auditor`

Do not use specialist work to run final proof gates. Specialists may map evidence, pressure-test soundness, classify negative evidence, and recommend focused/full proof lanes. Root owns authoritative fmt/lint/build/test commands and final verdict.

## Shared specialist packet contract

All specialist prompts, packets, rejections, waits, and closure handoffs must follow the shared contract at `../references/specialist-packet-contract.md`.

The root must assign an `artifact_state_id`, `artifact_state_label`, and exact `scope` before launch. An accepted packet must be packet-native, scoped to the assignment, evidence-bearing, current for the assigned artifact state, and free of transport wrappers, queued prompts, instruction acknowledgements, and root-only `Echo:` text.

Reject acknowledgement-only packets as `low-value`. Reject late packets as `stale` or `superseded` when the artifact state changed before they arrived. Close stale workers and continue with local proof when the assigned uncertainty has been resolved locally or is no longer route-changing.

## Specialist value receipt

For every specialist packet, accepted or rejected, record a value receipt:

```yaml
specialist_value_receipt:
  role: verification_auditor | hazard_hunter | evidence_mapper | soundness_auditor | invariant_auditor | complexity_auditor | negative-ledger-mapper | other
  packet_status: accepted | stale | transport-invalid | wrong-scope | timeout | superseded | low-value
  artifact_state_id_match: yes | no | unknown
  scope_match: yes | no | unknown
  uncertainty_class: evidence | soundness | invariant | hazard | complexity | verification | negative-evidence | other
  route_changed: yes | no
  finding_added: yes | no
  proof_changed: yes | no
  risk_retired: yes | no
  value: positive | neutral | negative
  used_for: evidence-mapping | negative-evidence-pruning | soundness-pressure | invariant-pressure | hazard-pressure | complexity-pressure | verification-planning | none
  reason: "one sentence"
```

Acceptance rules:
- `accepted` requires `artifact_state_id_match: yes` and `scope_match: yes`.
- `accepted` requires at least one scoped material signal with an artifact reference.
- `value: positive` requires at least one of `route_changed`, `finding_added`, `proof_changed`, or `risk_retired` to be `yes`.
- `risk_retired: yes` requires a plausible material hazard or negative-evidence route to have been ruled out.
- Rejected packets still appear in the Specialist Briefing Ledger and Specialist Value Receipts.

## Artifact state identity

Every meaningful pass must carry an `artifact_state_id` in addition to `artifact_state_label`.

`artifact_state_id` must include enough current-state evidence to make stale packets obvious:
- branch name when available
- `HEAD` or comparable revision
- diff hash or changed-file digest
- touched path set
- phase label, such as `prepatch`, `postpatch`, `post-fixture-refresh`, or `closure-candidate`

Any material edit, fixture regeneration, dependency update, proof-surface change, or negative-ledger reopening event invalidates older specialist packets. Close or supersede pre-edit specialists before using post-edit evidence. If specialist input is still needed, spawn fresh specialists with the new `artifact_state_id`.

## Specialist packet validation

Require exactly one packet-native specialist output from every specialist, using the shared packet contract fields:
- `artifact_state_id`
- `artifact_state_label`
- `scope`
- `top_material_signals` with artifact references
- `unresolved_signals`
- `agreement_pressure`
- `stale`
- `final_call`

Validate every specialist packet before reading it as evidence:
- exactly one specialist packet is present
- no raw `<subagent_notification>`, `<hook_prompt`, `Echo:`, instruction acknowledgement, or queued prompt content is relayed as evidence
- all required fields are present
- `artifact_state_id` matches the current root state exactly
- `scope` matches the assigned scope
- at least one scoped answer has an artifact reference

If validation fails, mark the packet `transport-invalid`, `wrong-scope`, `stale`, `superseded`, `timeout`, or `low-value`, record the rejection reason in the Specialist Briefing Ledger, add a Specialist Value Receipt, and continue locally or relaunch one narrow specialist only when the missing uncertainty remains route-changing. Do not repeatedly respawn broad swarms for the same artifact state.

## One-change challenge as local falsifier

Run this challenge after a candidate material fixed point and before every final closure attempt. Also use it before escalating from `direct-closure` or `targeted` to a broader specialist lane.

```yaml
one_change_challenge:
  candidate_extra_change: "..."
  materiality: material | non-material | unknown
  proof_needed: "..."
  negative_ledger_checked: queried | mapped | handoff | no-applicable-evidence | unavailable
  matched_negative_ids: []
  reopening_criteria_satisfied: yes | no | n/a
  decision: apply | reject | defer | escalate-to-specialist | no-impactful-change
  reason: "..."
```

Rules:
- If the challenge produces no material candidate and proof lanes are obvious, do not fan out.
- If the challenge identifies one bounded uncertainty, prefer one specialist over a swarm.
- If the challenge identifies multiple independent uncertainty classes, reclassify to `expanded-targeted`.
- If the selected move matches active negative evidence, choose a different move or prove reopening criteria are satisfied.
- After any implemented one-change improvement, rerun full de novo review before closure.

## Negative evidence closure gate

Closure cannot be `ready` while this gate is open:

```yaml
negative_evidence_closure_gate:
  status: satisfied | open | blocked | unavailable
  active_exclusions_count: 0
  repeated_failed_route_used: yes | no
  reopening_criteria_satisfied: yes | no | n/a
  learnings_hits_applicability_checked: yes | no | n/a
  reason: "..."
```

Gate rules:
- `satisfied`: no active applicable negative evidence blocks the current route, or reopening criteria are satisfied with proof.
- `open`: active applicable negative evidence conflicts with the current route and has not been reopened.
- `blocked`: evidence exists but cannot be checked due to missing logs, inaccessible learnings, or unavailable repo history.
- `unavailable`: `$negative-ledger`/`learnings` tooling is unavailable, and an in-session ledger could not check the relevant source. Explain the limit.
- Passing checks do not close this gate if a known disconfirmed route was repeated without a new witness.

## Orchestration algorithm

1. Establish entry state, `artifact_state_id`, and `artifact_state_label`.
2. If unresolved PR comments exist and relevance is unclear, start with `review-adjudication`.
3. Run Routing Preflight, including the first root-owned Negative Ledger Pass.
4. Choose initial phase path and fixed-point lane.
5. Choose subagent mode (`off`, `targeted`, or `swarm`) and run only justified read-only specialist scopes. Prefer root-owned negative-ledger query/map first; run `negative-ledger-mapper` only when material history pressure is read-heavy.
6. Run the saturation loop:
   - implement or remediate with `accretive-implementer` or root-equivalent doctrine
   - review with `adversarial-reviewer` or root-equivalent doctrine
   - normalize findings, soundness, invariants, hazards, complexity, verification, negative evidence, and comment adjudication into ledgers
   - after failed/no-effect/regression/revert/rejection/pivot events, run Negative Capture Decision
   - capture decision-shaping negative evidence through `$negative-ledger`, with durable writeback through `$learnings` when transferable
   - rerun full-scope review after any material validation or remediation
7. Reach a **candidate material fixed point** only when no unresolved material finding, material soundness gap, unbounded critical invariant, material foot-gun, material complexity hazard, or open negative-evidence closure gate remains.
8. Run the pre-closure Negative Ledger Handoff.
9. Run the pre-closure one-change challenge, using the Negative Evidence Ledger before selecting a change.
10. Compile the closure handoff packet, including accepted/rejected/stale specialist packets, value receipts, and negative-ledger handoff.
11. Run `verification-closure` or root-equivalent closure gates.
12. If closure reopens the loop, route the highest-value next move and continue.
13. Stop only in a justified terminal state.

## Output contract

### Standard

Use concise sections in this order:
- Workflow
- Entry State
- Routing Preflight
- Upstream Intake (only when review-adjudication materially shaped the route)
- Companion Skill Ledger
- Negative Ledger Pass
- Subagent Mode and Budget
- Specialist Value Receipts (only when specialists ran)
- Routing Summary
- One-Change Challenge
- Closure Handoff Packet
- Residual Risks
- Final State
- Do Next

### Fast

Use concise sections in this order:
- Entry State
- Negative Ledger Pass
- Routing Summary
- Final State
- Do Next

## Do Next

The final section must say:
- `owner`: skill | user | none
- `action`: exact next phase, stop action, or `none`
- `why`: one sentence
- `state`: ready | conditionally ready | needs remediation | needs-decision | blocked

## Hard rules

- Never impose an arbitrary maximum number of loops.
- Never start a non-trivial fixed-point run without a root-owned Negative Ledger Pass.
- Never treat `no-applicable-negative-evidence` as proof that a route is novel.
- Never let negative evidence suppress a route unless it has witness-bearing applicability to the current artifact state.
- Never let active applicable negative evidence disappear before closure; mark it remediated, stale, superseded, reopened, accepted-risk, or still open.
- Never let a `learnings` hit become an exclusion rule without checking its evidence and current-state applicability.
- Never append negative evidence to durable learnings unless it is decision-shaping, transferable, and counterfactually useful.
- Never launch specialists before declaring `fixed_point_lane` and specialist budget.
- Never exceed the lane budget without a recorded `budget_exception`.
- Never count a specialist as value-positive without a Specialist Value Receipt.
- Never omit rejected, stale, superseded, timeout, wrong-scope, transport-invalid, or low-value specialist packets from the Specialist Briefing Ledger.
- Never let stale specialist briefings masquerade as current evidence.
- Never let specialist packets without a matching `artifact_state_id` enter the closure verdict.
- Never let specialists own final proof commands or the final pass/fail verdict.
- Never mark a companion skill `used` unless its explicit output packet, invocation, or contract-shaped section is present.
- Never mark a companion skill `not-needed` without a task-shape reason.
- Never let review-adjudication quietly disappear once it materially shaped the route.
- Never declare a candidate fixed point while a material soundness gap remains unresolved.
- Never declare a candidate fixed point while the negative evidence closure gate is open.
- Never skip the pre-closure Negative Ledger Handoff.
- Never skip the pre-closure one-change challenge before a final closure attempt.

## Resources
- [negative-ledger skill](../negative-ledger/SKILL.md)
- [negative-ledger-mapper](../negative-ledger/agents/negative-ledger-mapper.md)
- [negative-ledger contract](../negative-ledger/references/negative-ledger-contract.md)
- [negative-ledger pass](references/negative-ledger-pass.md)
- [lane-and-specialist-budget.md](references/lane-and-specialist-budget.md)
- [companion-skill-ledger.md](references/companion-skill-ledger.md)
- [specialist-value-receipt.md](references/specialist-value-receipt.md)
- [closure-handoff-contract.md](references/closure-handoff-contract.md)
- [closure-handoff-template.md](references/closure-handoff-template.md)
- [one-change-challenge.md](references/one-change-challenge.md)
- [example-invocations.md](references/example-invocations.md)
- [common-soundness.md](references/common-soundness.md)
- [common-ledgers.md](references/common-ledgers.md)
- [common-cli-reporting.md](references/common-cli-reporting.md)
- [common-routing-vocabulary.md](references/common-routing-vocabulary.md)
- [specialist-packet-contract.md](../references/specialist-packet-contract.md)
