# Zig semantic lenses

Use these lenses to choose useful references for a live engineering question.
They are non-exhaustive and can overlap. They are not stages, required labels,
or a mutation gate. The root skill owns activation, scope, and completion.

## Construction as a first-class path

For new functionality, start from the desired behavior and its laws. Compare
representations when the choice is consequential: ordinary runtime values,
checked witnesses, tagged unions, generated types, comptime plans, or runtime
interfaces. Ask which information must remain static and which can be ordinary
data. Prefer making invalid states unrepresentable to repeatedly checking them.
Do not invent a defect, counterexample, owner dispute, or packet to justify work
under an already accepted design. A material change may need no named family.

## Lenses and discriminators

| Lens | Relevant question | Reference |
| --- | --- | --- |
| Claim binding | What authoritative bytes/facts does a receipt, ref, hash, or verifier result actually bind? What can be substituted or omitted? | [Claim binding](claim_binding_playbook.md) |
| Lifetime escape | Which backing owner remains alive, and what invalidates the borrow after return, reset, growth, or transfer? | [Ownership](memory_ownership_playbook.md) |
| Failure guarantees | Does failure preserve the API's strong, basic, partial-progress, or durable/recoverable guarantee? | [Transitions](atomic_transition_playbook.md) |
| Verifier completeness | Are both safe parsing and the promised semantic predicate established? Can well-encoded invalid values pass? | [Verifiers](verifier_completeness_playbook.md) |
| Repository closure | Which build, registry, generator, golden, or aggregate check owns a changed artifact? Is the review scope correct? | [Closure](repo_closure_playbook.md) |
| Evidence context | Do the relevant inputs and assumptions still match the validation being reused? | [Evidence](evidence_context_playbook.md) |

A generic word such as `proof`, `commit`, `report`, or `manifest` is not itself an
activation rule or a defect. Use its actual semantics in the Zig task. The same
applies to a pointer, allocation, loop, `anytype`, or long function.

## When uncertainty constrains action

Resolve consequential uncertainty before changing the boundary that depends on
it. Inspection, disposable probes, and focused tests may be the way to discover
the answer; a completed audit packet is not a prerequisite. A specific unsafe or
unauthorized action may be blocked while independent work continues.

A claimed defect needs a concrete failing case or a source-level argument,
clearly labeled if not executed. Unavailable tooling limits validation claims,
not unrelated analysis. Revisit the selected boundary when new evidence changes
it; do not repeat classification for its own sake.

## Optional structured handoff

Use ZSR-v1 only for an explicit structured audit or a known consuming interface.
There is no default file, store, validator, or required pre-edit emission. Honor
an existing consumer's required fields without inferring a new workflow gate.
For human handoffs, concise prose is ordinarily sufficient.

```yaml
zig_semantic_route:
  route_version: ZSR-v1
  artifact_state:
    repository_root:
    head:
    dirty_fingerprint:
    zig_version:
  task_surfaces: []
  material: yes | no
  active_families: []
  no_family_reason:
  owner:
  concrete_counterexample:
  selected_repair_boundary:
  forbidden_shortcuts: []
  required_proof: []
  family_contracts: {}
```

Outside a consumer requiring this exact shape, omit inapplicable fields. Use the
desired law rather than a fictional counterexample for constructive work. Empty
forms, absent family labels, and missing proof epochs do not block mutation.
Resources and evidence still need the real contracts described in the references.
