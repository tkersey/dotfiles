---
name: negative-ledger
description: "Durably capture, query, gate, reopen, compact, and hand off evidence-backed failed hypotheses, falsified normal forms, and route-family exclusions from repo-local `.ledger/negative-ledger.jsonl`. Use for `$negative-ledger`, repeated review routes, same-family recurrence, normal-form falsification, route veto, route-family compaction, or `$resolve` negative-route gates."
metadata:
  version: "2.0.0"
---

# Negative Ledger

## Mission

Preserve disconfirmed hypotheses so future work cannot rename and repeat them.

Canonical durable store:

```text
.ledger/negative-ledger.jsonl
```

Use the `ledger` CLI. `.learnings.jsonl` may summarize promoted lessons but is not the primary route-exclusion store.

## Core rules

```text
A repeated same-family finding after a permitted route falsifies that route's closure hypothesis.
A falsified normal form must be captured before another mutation permit.
The next route must differ at the leverage level.
Same-cluster alone is related evidence, not automatically an exclusion.
```

## Preferred CLI

When hardened NRG-v2 commands exist:

```bash
ledger gate ...
ledger capture --json FILE
ledger reopen --id NEG-...
ledger stale --id NEG-...
ledger supersede --id NEG-... --by NEG-...
ledger compact ...
ledger handoff
ledger audit
```

Compatibility with the current CLI:

```bash
ledger map --route "$ROUTE" --cluster "$CLUSTER" --artifact "$ARTIFACT"
ledger show --id NEG-...
ledger capture --json FILE
ledger reopen --id NEG-...
ledger handoff
ledger doctor
```

If the current `map` reports a cluster-only exact match, inspect the record with `show`; do not treat cluster identity alone as a route-family exclusion.

## Negative route gate

```yaml
negative_route_gate:
  gate_version: NRG-v2 | compatibility-v1
  query_or_map: yes | no
  ledger_available: yes | no
  command:
  exit_code: 0 | 2 | 3
  records_scanned:
  current:
    cluster:
    counterexample_family:
    route:
    route_family:
    owner:
    artifact:
  nearest_prior_records: []
  active_exclusion_match: yes | no | unknown
  exclusion_id: "none | NEG-..."
  prior_normal_form_falsified: yes | no
  capture_required: yes | no
  capture_created: yes | no
  captured_neg_id: "none | NEG-..."
  eliminated_route_family:
  route_changed_at_leverage_level: yes | no
  handoff_allowed: yes | no
```

## Capture requirements

Capture when:

- same-family recurrence follows a permitted route;
- a normal form is falsified;
- a route family has failed to reduce recurrence;
- a public bypass/fallback/tolerance route is rejected;
- distillation eliminates a prior route family.

Minimum record:

```yaml
negative_evidence_record:
  record_version: NER-v1
  neg_id:
  cluster_id:
  counterexample_family:
  normal_form_id:
  route_id:
  route_family:
  hypothesis:
  attempted_change_or_decision:
  observed_outcome:
  failure_class:
  source_refs: []
  exclusion_scope: route | route_family | counterexample_family | cluster_wide | none
  exclusion_rule:
  reopening_criteria: []
  confidence:
  status: active | need-evidence | capture_candidate | non_exclusion_observation | reopened | stale | superseded | accepted-risk | blocked
```

## Falsification ratchet

After `prior_normal_form_falsified: yes`:

```text
capture_created = yes
route_changed_at_leverage_level = yes
```

Otherwise `handoff_allowed = no`.

A route-family change is not established by a new helper name or another predicate in the same owner.

## No-active-exclusion standard

`no active exclusion` is insufficient alone.

The gate must show:

- which records were considered;
- why each did not apply;
- whether a capture was created;
- whether current route differs from falsified route family;
- whether handoff is allowed.

## Guardrails

- Do not record hunches as active exclusions.
- Do not overblock adjacent approaches from cluster identity alone.
- Do not use stale evidence without applicability.
- Do not let an empty ledger masquerade as novelty.
- Do not permit a second same-family route without capture.
- Do not mark route change when leverage level is unchanged.
