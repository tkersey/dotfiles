# Specialist Packet Contract

Use this contract whenever a Codex-native skill asks a specialist, subagent, mapper, auditor, or explorer to return evidence that may shape routing, adjudication, implementation, or closure.

Specialists provide signals. The root agent owns synthesis, final proof commands, pass/fail decisions, publication, and user-facing conclusions.

## Required Packet

Every accepted specialist response must contain exactly one packet-native answer with these fields:

```yaml
artifact_state_id: "branch=<name> head=<sha-or-id> diff=<digest-or-path-set> phase=<phase>"
artifact_state_label: "<short human label>"
scope: "<assigned files, domains, comments, or question>"
top_material_signals:
  - signal: "<finding, risk, fact, or proof recommendation>"
    evidence_ref: "<file:line, command, log, transcript id, memory id, PR thread id, or other artifact ref>"
unresolved_signals:
  - signal: "<open uncertainty or none>"
    evidence_ref: "<artifact ref or none>"
agreement_pressure: "confirms | challenges | narrows | conflicts | none"
stale: false
final_call: "<one-line decision or recommendation>"
```

An accepted packet must have at least one scoped answer and at least one artifact reference. Artifact references may be source paths, line numbers, command names, logs, session ids, review thread ids, memory ids, or explicit "not inspected" references for unresolved signals. A packet with no concrete evidence reference is an acknowledgement, not evidence.

## Artifact State

`artifact_state_id` binds a packet to the code or artifact shape the root assigned. Include enough identity to make stale packets obvious:

- branch or checkout identifier when available
- `HEAD`, commit, or comparable revision
- diff hash, changed-file digest, or touched path set
- phase label such as `prepatch`, `postpatch`, `post-fixture-refresh`, `spec-pre-gate`, `post-spec`, or `closure-candidate`

Any material edit, fixture regeneration, dependency update, proof-surface change, or reopened negative evidence invalidates older packets. Mark older packets `stale`, `superseded`, or `timeout` before closure; do not silently carry them forward.

## Validation

Before using a packet as evidence, validate all of these:

1. Exactly one packet-native answer is present.
2. No raw transport wrapper is present, including `<subagent_notification>`, `<hook_prompt`, queued prompts, instruction acknowledgements, or root-only `Echo:` text.
3. All required fields are present.
4. `artifact_state_id` exactly matches the current assigned state.
5. `scope` matches the assigned specialist scope.
6. `top_material_signals` contains a scoped answer with an evidence reference.
7. `stale` is false.

If any check fails, reject the packet as `transport-invalid`, `wrong-scope`, `stale`, `superseded`, `timeout`, or `low-value`, then continue locally or relaunch one narrow replacement only when the missing uncertainty is still route-changing.

## Value Receipt

Record one value receipt for every specialist packet, accepted or rejected:

```yaml
specialist_value_receipt:
  role: "<specialist role>"
  packet_status: accepted | stale | transport-invalid | wrong-scope | timeout | superseded | low-value
  artifact_state_id_match: yes | no | unknown
  scope_match: yes | no | unknown
  uncertainty_class: evidence | soundness | invariant | hazard | complexity | verification | negative-evidence | other
  route_changed: yes | no
  finding_added: yes | no
  proof_changed: yes | no
  risk_retired: yes | no
  value: positive | neutral | negative
  used_for: "<evidence mapping, review pressure, verification planning, negative-evidence pruning, none>"
  reason: "<one sentence>"
```

`value: positive` requires at least one material decision delta: route changed, finding added, proof changed, or risk retired. A valid but unsurprising packet is neutral. Malformed, stale, wrong-scope, timeout, acknowledgement-only, or wrapper-leaking output is negative.

## Wait And Progress Bounds

Wait for packets only while the wait is producing progress. A progress-bound wait has one of these outcomes:

- a valid packet arrives and is recorded
- a packet arrives but is rejected with a value receipt
- the assigned uncertainty is resolved locally
- the root closes stale workers and continues with local proof
- one narrow replacement is launched for a still route-changing uncertainty

Do not wait indefinitely for broad swarms. Do not respawn multiple specialists for the same uncertainty class unless the previous packet was stale, transport-invalid, wrong-scope, timeout, or materially incomplete.

## Closure Rules

Closure may proceed only after the root has:

- recorded accepted, rejected, stale, superseded, timeout, wrong-scope, transport-invalid, and low-value specialist packets that shaped routing
- verified that no stale packet is being used as current evidence
- treated specialist signals as planning input, not proof commands or pass/fail verdicts
- run root-owned verification for the changed behavior
- documented residual uncertainty and any rejected specialist value receipts
- emitted `subagent_receipt` when a spec pipeline spawned specialists

Passing specialist output never replaces local build, lint, test, review, or proof gates.
