---
name: negative-ledger
description: "Capture, query, map, compact, reopen, and hand off evidence-backed failed hypotheses, falsified review-resolution routes, reverted approaches, no-effect repairs, benchmark regressions, public-bypass failures, scar-tissue exclusions, and strategy pivots so future work avoids repeated dead ends while stale evidence remains reopenable. Trigger for `$negative-ledger`, negative evidence, negative route memory, NREC-v1, failed attempts, same-cluster recurrence, repeated review decisions, what have we already tried, avoid retrying dead ends, public bypass counterexample, scar tissue, before another optimization, route ratchet, search-space pruning."
---

# Negative Ledger

`negative-ledger` preserves disconfirmed hypotheses so future work does not repeat dead ends.

## Core upgrade

For review workflows:

```text
A repeated review decision is a falsified hypothesis.
```

Negative evidence should not merely be a note that something happened. It should become a narrow route exclusion with reopening criteria.

## Modes

- `capture`: record a newly witnessed failed or disconfirmed attempt.
- `query`: retrieve relevant negative evidence before new work.
- `map`: convert prior evidence into current routing constraints and next-search hints.
- `route-memory`: map falsified review-resolution routes into negative route exclusion cards.
- `reopen`: decide whether stale negative evidence is eligible again.
- `compact`: dedupe repeated failed attempts into route-family exclusions.
- `handoff`: summarize active exclusions, stale/reopened entries, and promising frontier.

## Review-resolution trigger cues

Use this skill when any are true:

- same cluster reappears after repair;
- selected normal form was falsified;
- `universalist_check.decision: not-needed` was falsified;
- add-surface route failed or became unsound;
- public bypass, fallback, compatibility path, parser tolerance, or proof matrix choice caused a CAS/review/validation counterexample;
- review lab scar tissue must be discarded or distilled;
- one-change candidate resembles a prior failed route;
- Review Distillation Mode is active;
- route-wave artifact has `negative_evidence.pass_status: fail`.

## Negative Route Exclusion Card

Use this compact card when negative evidence should shape routing:

```yaml
negative_route_exclusion_card:
  card_version: NREC-v1
  neg_id: "NEG-..."
  card_id: "NREC-..."
  artifact_state_id: "..."
  cluster_id: "..."
  excluded_route: no-change-proof | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | universalist-not-needed | proof-matrix | commit-boundary | distill-from-lab
  hypothesis: "..."
  attempted_change_or_decision: "..."
  falsifying_evidence:
    - kind: cas-review | validation | pr-comment | route-wave | rcp | rdp | commit | learning | lab | test | diff
      ref: "..."
      summary: "..."
  applicability:
    current_status: active | stale | superseded | reopened | unknown
    conditions: []
  exclusion_rule: "..."
  reopening_test: "..."
  next_allowed_routes:
    - delete-collapse-canonicalize
    - refactor-existing-owner
    - use-universalist
    - distill-from-lab
    - blocked
  confidence: high | medium | low | unknown
```

## Route ratchet

Before implementation handoff on a repeated route:

```yaml
negative_route_gate:
  prior_route_checked: yes | no
  active_exclusion_match: yes | no
  if_match:
    neg_id: "..."
    selected_route: "..."
    exclusion_rule: "..."
    status: reopened | superseded | stale | blocked
  handoff_allowed: yes | no
```

If `active_exclusion_match: yes` and status is not `reopened`, `superseded`, or `stale`, implementation is blocked.

## Capture requirements

A negative ledger entry is usable only if it has:

- narrow hypothesis;
- concrete attempted change or decision;
- evidence anchor;
- observed outcome;
- failure class;
- applicability conditions;
- current status;
- exclusion rule;
- reopening criteria;
- confidence;
- next-search hint.

Do not turn one failed implementation into a blanket ban on a broad strategy family.

## Query templates for review resolution

Use compact topical queries:

```text
<repo> <cluster_id> <owner> <route_kind> <failure_surface>
```

Examples:

```bash
run_learnings_tool recall --query "world actuation public bypass validation repair compatibility tolerance" --limit 8 --drop-superseded
run_learnings_tool recall --query "world continuity same-cluster mutate-existing-owner CAS recurrence proof matrix" --limit 8 --drop-superseded
run_learnings_tool recall --query "review compression universalist not-needed boundary artifact recurrence" --limit 8 --drop-superseded
```

## Compaction

When the same exclusion family appears three or more times, compact:

```yaml
negative_compaction:
  compacted_card_id: "NREC-FAMILY-..."
  hypothesis_family: "..."
  excluded_route_family: "..."
  evidence_refs: []
  current_applicability: active | stale | superseded | reopened | unknown
  reopening_test: "..."
  safest_next_frontier: "..."
```

## Durable writeback policy

Do not flood `.learnings.jsonl`.

```yaml
negative_writeback_policy:
  in_wave_only:
    - one-off same-session route failure
    - low confidence
    - unclear applicability
  route_wave_artifact:
    - same-cluster recurrence
    - proof matrix gap
    - failed selected normal form
  durable_learnings:
    - repeated across sessions
    - generalizable to future branches
    - benchmark/regression/revert/public-bypass pattern
    - current proof anchors exist
```

Use `learnings append` only when transferable and decision-shaping.

## Output contract

```yaml
negative_evidence_ledger:
  - neg_id: NEG-001
    hypothesis: "..."
    attempted_change: "..."
    source_refs:
      - kind: benchmark | test | revert | review | trace | diff | learning | user-context | ledger | rcp | rdp | route-wave | lab
        ref: "..."
        summary: "..."
    learning_source_ids: []
    evidence: []
    observed_outcome: "..."
    failure_class: no-effect | local-regression | global-regression | unsound | too-complex | stale | unknown
    applicability_conditions: []
    current_status: active | stale | superseded | reopened | unknown
    exclusion_rule: "..."
    reopening_criteria: []
    confidence: high | medium | low | unknown
    next_search_hint: "..."
negative_route_exclusion_cards: []
negative_evidence_closure_gate:
  active_exclusions_checked: pass | fail
  selected_route_violates_active_exclusion: yes | no
  capture_required_entries_handled: pass | fail
  durable_writeback_decision: appended | duplicate-skip | not-attempted | unavailable
  closure_allowed: yes | no
```

Then add:

```md
### Negative Ledger Handoff
- active_exclusions:
- stale_or_superseded:
- reopened:
- need_evidence:
- safest_next_frontier:
- route_exclusion_cards:
- durable_capture:
```

## Guardrails

- Do not record unevidenced hunches as negative evidence.
- Do not use a learning hit as an exclusion rule until evidence and applicability are checked.
- Do not use absence of a negative entry as proof that a route is novel.
- Do not suppress adjacent approaches with an overbroad exclusion.
- Do not append to `.learnings.jsonl` by hand; use the CLI when durable writeback is appropriate.
- Do not make negative evidence final proof; it prunes routes and defines reopening tests.

## Resources

- [review-resolution-integration.md](references/review-resolution-integration.md)
- [negative-route-exclusion-card.md](references/negative-route-exclusion-card.md)
- [negative-evidence-compaction.md](references/negative-evidence-compaction.md)
- [review-distillation-scar-tissue.md](references/review-distillation-scar-tissue.md)
- [fixed-point-integration.md](references/fixed-point-integration.md)
