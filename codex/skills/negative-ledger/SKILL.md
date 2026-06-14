---
name: negative-ledger
description: "Capture, query, map, reopen, compact, and hand off evidence-backed failed hypotheses and falsified review routes. Use for `$negative-ledger`, negative evidence, negative route ratchet, repeated review decision, same-cluster recurrence, route already tried, no-effect repair, public-bypass failure, scar tissue, route veto, or search-space pruning."
---

# Negative Ledger

`negative-ledger` preserves disconfirmed hypotheses so future work does not repeat dead ends.

## Core rule for review workflows

```text
A repeated review decision is a falsified hypothesis.
```

When the same cluster reappears after a selected route, that route becomes negative evidence unless proven unrelated, stale, or superseded.

## Modes

- `query`: retrieve relevant negative evidence before route selection.
- `map`: convert evidence into current route constraints.
- `capture`: record a newly falsified route or failed attempt.
- `reopen`: decide whether evidence is stale/superseded/reopened.
- `compact`: merge repeated route-family failures.
- `handoff`: summarize active exclusions and safest next frontier.

## Negative Route Gate

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

If active exclusion matches and is not reopened/stale/superseded, implementation is blocked.

## Capture shape

```yaml
negative_evidence_ledger:
  - neg_id: NEG-001
    hypothesis: "..."
    attempted_change_or_decision: "..."
    source_refs:
      - kind: cas-review | validation | pr-comment | route-record | commit | learning | lab | test | diff
        ref: "..."
        summary: "..."
    observed_outcome: "..."
    failure_class: no-effect | local-regression | global-regression | unsound | too-complex | stale | unknown
    applicability_conditions: []
    current_status: active | stale | superseded | reopened | unknown
    exclusion_rule: "..."
    reopening_criteria: []
    confidence: high | medium | low | unknown
    next_search_hint: "..."
```

## Query templates

Use compact topical queries:

```text
<repo> <cluster_id> <owner> <route_kind> <failure_surface>
```

## Durable writeback policy

Do not flood `.learnings.jsonl`.

Use durable writeback only when evidence is:

- decision-shaping;
- transferable;
- counterfactually useful;
- anchored by current proof/review/revert/benchmark evidence.

One-off same-session route failures can stay in the route record.

## Guardrails

- Do not record hunches as negative evidence.
- Do not convert one failed implementation into a broad strategy ban.
- Do not use stale evidence without applicability explanation.
- Do not use absence of a negative entry as proof that a route is novel.
- Do not suppress adjacent approaches with an overbroad exclusion.

## Resources

- [review-route-ratchet.md](references/review-route-ratchet.md)
- [writeback-policy.md](references/writeback-policy.md)
