# Negative Ledger Pass

`fixed-point-driver` treats negative evidence as a routine fixed-point input. A non-trivial run should not merely ask "what should we change?" It should also ask "what have we already learned not to try?"

The pass is root-owned by default. `negative-ledger-mapper` is an escalation specialist only when history mapping is read-heavy.

## Required pass points

Run a Negative Ledger Pass at:

1. **Preflight**: before selecting the first implementation or remediation route.
2. **Post-remediation / post-review**: after a failed attempt, no-effect change, regression, review rejection, or strategy pivot.
3. **Pre-closure**: before the one-change challenge and closure handoff.
4. **Capture**: when a newly witnessed failed route is decision-shaping, transferable, and counterfactually useful.

A pass that finds no applicable negative evidence still counts. Record `no-applicable-negative-evidence`.

## Pass shape

```yaml
negative_ledger_pass:
  phase: preflight | post-remediation | post-review | pre-closure | capture | handoff
  mode: query | map | capture | reopen | handoff | none
  artifact_state_id: "branch=... head=... diff=... phase=..."
  topical_query: "component failure-surface test-or-benchmark hypothesis-family"
  sources_checked:
    current_run: yes | no
    fixed_point_ledgers: yes | no
    learnings: yes | no
    repo_history: yes | no
    review_comments: yes | no
    user_context: yes | no
  result:
    active_exclusions:
      - "NEG-..."
    stale_or_superseded:
      - "NEG-..."
    reopened_candidates:
      - "NEG-..."
    need_evidence:
      - "NEG-..."
    no_applicable_negative_evidence_reason: "..."
    safest_next_frontier: "..."
  durable_capture: appended | duplicate-skip | not-material | unavailable | not-attempted
```

## Source order

Prefer sources in this order:

1. Current-run witnesses: commands, logs, benchmark output, failing/passing tests, diffs, traces, reverts.
2. Current campaign ledgers: Findings, Verification, Specialist Briefing, Specialist Value Receipts, and Negative Evidence Ledger.
3. Durable memory: `.learnings.jsonl` via `learnings recall/query/recent`.
4. Repository history: commits, reverts, PR comments, issue notes, benchmark history.
5. User context, marked as `user-context` until independently witnessed.

## Learnings preflight

When a compatible CLI exists:

```bash
run_learnings_tool recall --query "<component failure-surface test-or-benchmark hypothesis-family>" --limit 8 --drop-superseded
```

Use 4-8 terms. Include:
- component or module
- failure surface
- benchmark/test/fixture when known
- review-comment theme
- hypothesis family
- invariant or hazard class

Treat hits as candidate evidence. A hit only becomes active negative evidence after checking evidence anchors and applicability against the current artifact state.

## Active evidence requirements

A negative evidence entry is active only when it has:

- a narrow hypothesis
- a concrete attempted change or decision
- evidence anchors
- observed outcome
- failure class
- applicability conditions
- current status
- exclusion rule
- reopening criteria
- confidence
- next-search hint

Missing evidence means `need-evidence`, `unknown`, or `stale`, not active exclusion.

## Capture criteria

Capture newly witnessed negative evidence only if all three quality gates pass:

1. **Decision delta**: would this change what the next agent tries?
2. **Transferability**: does it apply beyond this exact incident?
3. **Counterfactual value**: would ignoring it predictably waste time, reintroduce unsoundness, or regress proof?

Use durable `$learnings` writeback when available and appropriate. Do not hand-edit `.learnings.jsonl`.

## Closure interaction

Pre-closure handoff must answer:

```yaml
negative_ledger_handoff:
  active_exclusions: []
  stale_or_superseded: []
  reopened: []
  need_evidence: []
  safest_next_frontier: "..."
  learnings_source_ids: []
  durable_capture: appended | duplicate-skip | not-material | unavailable | not-attempted
  closure_effect:
    blocks_closure: yes | no
    changes_one_change_challenge: yes | no
    changes_verification_plan: yes | no
```

Closure is not ready if active applicable negative evidence conflicts with the current route and reopening criteria are not satisfied.

## Guardrails

- Do not use a weak or stale learning as an exclusion rule.
- Do not convert one failed implementation into a blanket ban on a broad strategy family.
- Do not use absence of a negative entry as proof that a route is novel.
- Do not block closure merely because negative-ledger tooling is unavailable; report the evidence limit and decide whether the missing source is material.
- Do not let negative-ledger replace direct verification. It informs route selection and closure gates; it does not prove correctness.
