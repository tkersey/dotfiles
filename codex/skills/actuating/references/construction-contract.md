# Construction Contract

Read this reference before initial material mutation and before resolving an
accepted Counterexample.

## One adjudication

`construction-contract/v1` is the sole architecture-selection artifact. It
selects the canonical owner, architecture, representation or machine,
interpreter or handler, proof strategy, retirements, and execution scope for one
material construction.

Downstream coordinators, work views, operation envelopes, executors, Ledger
transitions, and Ship project the selected decision. They do not reconsider it.
A Universalist plan may contain candidates and rejected routes, but it is
supporting reasoning and never grants mutation.

## Required payload

~~~yaml
payload:
  goal_contract_ref:
  mode: initial | realization-repair | architecture-repair | ablation-repair

  subject:
    repository:
    base_artifact_digest:

  boundary:
    boundary_key:
    source_worlds: []
    target_worlds: []
    carriers: []
    operations: []
    observations: []

  architecture:
    governing_law_refs: []
    canonical_owner:
    selected_construction:
    representation_or_machine:
    interpreter_or_handler:
    residual_assumptions: []

  falsified_predecessor_claims: []
  preserved_predecessor_claims: []
  invalid_states_eliminated: []
  counterexample_class_refs: []
  preserved_observations: []

  proof_obligations:
    - obligation_id:
      law_ref:
      statement:
      proof_mode:
      adequacy_reason:
      verifier: {argv: []}
      falsifier: {argv: []}
      proof_kind: implementation | review | acceptance | ship

  retirements:
    - retirement_id:
      dominated_construct:
      disposition: collapse | delegate | retire | replace
      replacement_ref:
      verifier: {argv: []}

  execution:
    allowed_paths: []
    owner_boundary:
    operation_effects: [inspect, edit, verify]
    completion: complete | ready-to-ship
~~~

The Construction must reference the current Goal, stay within its paths and
compatibility authority, cover every Goal law and required proof kind, and
bind every current accepted Counterexample class. It never grants mutation by
itself. `architecture.canonical_owner` and `execution.owner_boundary` must be
identical; execution projects the selected owner and cannot introduce another
one.

`execution.allowed_paths` is a duplicate-free canonical literal repository
path set under the same grammar as the Goal scope. A broader Goal scope does
not authorize a noncanonical operation path. The `.git` root and
`.ledger/actuation/artifact-kernel` control root, including slash descendants,
are reserved under ASCII case-folding; prefix-like siblings remain valid. A
broader scope, including `.`, cannot re-admit either root.

For every cited accepted class, the Construction's `boundary.boundary_key`
must equal the class `boundary_key`. The canonical owner may remain the class
`owner_boundary`. Moving that owner is legal only in `architecture-repair`,
with a retirement whose `dominated_construct` is the class owner and whose
`replacement_ref` is the new canonical owner. `realization-repair` and
`ablation-repair` cannot relabel or move the owner.

## Proof observation roles

For an implementation or acceptance obligation, the base `obligation_id` is
the verifier observation reference and the derived
`<obligation_id>#falsifier` reference selects its falsifier. Discharge requires
independent passing operations for both exact argv roles on the current
subject. One operation cannot cite both roles for the same obligation, and an
argv selected for one role cannot substitute for the other. A material subject
change invalidates both observations.

Review and Ship obligations remain projections of their external owners; their
Construction argv is never executable by the operation handler. A retirement
has only its declared verifier and does not acquire a derived falsifier role.
This dual-observation law applies only to `artifact-kernel-v1` implementation
and acceptance obligations. Frozen `legacy-actuating-v1` lineages retain their
historical base-verifier fold, and the two semantics never mix within a goal.

## Optional High/Critical example-proof exception

Omit `extensions` for every ordinary Construction. Its absence preserves the
strict base `construction-contract/v1` shape. An empty extension object, an
unknown extension name, or an extra field fails closed.

Only a non-initial successor may carry this exact versioned extension when a
Critical or High authority, state-machine, identity, persistence, or
concurrency Counterexample cannot feasibly receive a stronger direct proof:

~~~yaml
payload:
  extensions:
    high-critical-example-proof-exception/v1:
      exceptions:
        - counterexample_class_ref:
          example_obligation_ref:
          compensating_obligation_ref:
          stronger_proof_infeasibility_reason:
~~~

The extension is an exception binding, not a fifth artifact family, event,
command, state machine, or mutation authority. Its shape is exact:

- `exceptions` is nonempty and contains at most one entry for each named
  `counterexample_class_ref`, which must also appear in the Construction's
  `counterexample_class_refs`;
- `example_obligation_ref` names a distinct `example-regression`
  implementation or acceptance obligation whose ordinary `adequacy_reason`
  remains nonblank and whose law appears in
  `architecture.governing_law_refs`;
- `compensating_obligation_ref` names an implementation or acceptance
  obligation using `representation`, `total-transition`, `exhaustive-model`,
  `static-refinement`, `property-law`, or `differential` proof;
- the compensating obligation proves a different governing law from the
  example obligation; and
- `stronger_proof_infeasibility_reason` states why a stronger direct proof is
  infeasible. If a direct strong implementation or acceptance proof already
  exists for the example's law, the exception is redundant and invalid.

Pure validation establishes only this exact shape and the internal obligation
joins. It does not establish severity, infeasibility, semantic adequacy, or
accepted-risk authority. Runtime admission requires an exact matching
`counterexample_class_ref`, eligible `law_family`, and example-obligation
`law_ref` in the current Goal's
`high-critical-example-proof-risk-authority/v1` extension, then joins the same
class and law to a current or inherited High/Critical Counterexample. The Goal
authorization's exact family must be `authority`, `state-machine`, `identity`,
`persistence`, or `concurrency`. The Construction cannot supply or copy
authority. Its `goal_contract_ref` and the exception tuple consume the
Goal-owned grant. Both named obligations must still be discharged before
closure.

Keep exceptions forbidden on an initial Construction. If explicit risk
acceptance arrives after Goal creation, the immutable Goal cannot be amended:
open a fresh Goal from the revised source and register K0, then re-author a
current Counterexample Set from the still-applicable witness evidence before K1
consumes the grant. Block when applicability to the fresh Goal, K0, and subject
cannot be established. Review credit never carries.

K0 may expose the authorized law through an example proof so that inspect and
verify operations can establish the current witness, but that does not consume
the grant. Ledger derives pending risk-authority debt from the Goal and current
Construction and blocks edits and closure until either K0 carries a direct
strong same-law proof or a current Counterexample plus K1 exception consumes
the grant. This debt is derived state, not another artifact or event.

Before registration, set the semantic-owner Construction draft's `artifact_id`
to JSON `null`, run `ledger materialize construction-contract --input DRAFT`,
persist the emitted canonical document, and validate it with `ledger validate
construction-contract --input FILE|-`. Materialization stores nothing and
grants no mutation authority.

## Initial construction

Create `K0` before material mutation. Use a compact Construction when the
existing owner is exact, no competing material construction exists, no new
boundary or mechanism is introduced, and no abstraction is displaced. Use a
supporting Universalist plan for consequential selection.

An initial Construction has no predecessor and both
`falsified_predecessor_claims` and `preserved_predecessor_claims` are empty.

Select the smallest non-dominated construction. Candidate `A` dominates `B`
when it satisfies and preserves at least everything `B` does, excludes at
least the same Counterexamples, introduces no more independent law owners,
parallel representations, bypasses, mechanisms, residue, or unjustified
resource burden, and is strictly better in at least one dimension. If no unique
non-dominated candidate exists, prove `separate-laws` or block.

## Successor construction

Every material repair creates an immutable successor `K(n+1)` that names:

- the current predecessor Construction;
- the Counterexample Sets that falsified it;
- falsified and preserved predecessor claims;
- each accepted class excluded by the successor;
- preservation obligations for still-valid behavior;
- the changed or preserved canonical owner and architecture;
- every bypass, duplicate owner, predecessor representation, adapter, flag,
  validator, fallback, and proof path that must be retired;
- stronger executable proof where feasible.

Choose the repair mode from evidence:

- `realization-repair`: architecture stays valid; implementation failed to
  realize it. Preserve owner and construction, delegate the bypassing caller,
  and strengthen realization proof.
- `architecture-repair`: predecessor architecture was wrong or insufficient.
  Select a new lawful construction and retire the dominated predecessor.
- `ablation-repair`: replacement architecture is valid but residue remains.
  Preserve the construction and complete its retirement obligations.

Every successor names at least one falsified predecessor claim.
`realization-repair` and `ablation-repair` also name at least one preserved
predecessor claim so that a purported repair cannot silently discard the
construction it claims to preserve.

An inherited High/Critical exception and both referenced obligations remain
byte-identical in every successor until a direct strong implementation or
acceptance proof discharges the example's same law. The exception does not
select the repair mode; choose that mode from the actual architecture delta.
Removing the exception always requires one retirement whose
`dominated_construct` is
`high-critical-example-proof-exception/v1:<counterexample_class_ref>`, whose
`disposition` is `retire`, and whose `replacement_ref` names that direct strong
proof. Rewriting, silently dropping, or retaining the exception beside a direct
strong same-law proof blocks registration.

No new abstraction is justified solely by a finding. No example-level patch is
legal when the witnessed class exposes a law, representation, transition,
owner, projection, interpreter, compatibility, proof, or ablation defect.

## Bug-to-law compiler

For each accepted class, compile:

~~~text
witnessed counterexample
-> intended law
-> canonical owner
-> selected construction
-> strongest feasible proof mode
-> executable obligation and falsifier
-> retirement of the bypassing or incorrect construction
-> independent review falsification
~~~

Preserve already-valid observations. Exclude the class rather than only its
example. A class remains unresolved until the successor realizes its bound
proof and retirement obligations on a materially current subject.

## Proof-mode ladder

Prefer, in order:

~~~text
representation
> total-transition
> exhaustive-model
> static-refinement
> property-law
> differential
> example-regression
~~~

A weaker feasible mode requires an explicit adequacy reason. Match common law
families to at least these expected modes:

| Law family | Expected proof |
|---|---|
| State machine/lifecycle | representation + total transition; exhaustive model when bounded |
| Authority/capability/replay | representation or static contract + adversarial transitions |
| Identity/canonicalization | property law + corpus; differential when available |
| Parser/serializer/codec | round trip + malformed-input corpus |
| Persistence/event fold | hash-chain replay + model/property tests |
| Idempotency/ordering/quotient | property laws, including permutation or repetition |
| Compatibility/migration | golden corpus + before/after differential proof |
| Concurrency | explicit state/ownership model + stress or model check |
| Public API/CLI | contract fixtures + footgun review |

For a Critical or High authority, state-machine, identity, persistence, or
concurrency class, example-only proof is insufficient unless the Construction
explains why stronger proof is infeasible, adds a compensating invariant proof,
and records explicit accepted-risk authority.

## Ablation law

A replacement is incomplete while a dominated predecessor, duplicate owner,
bypass, representation, validator, adapter, flag, fallback, or proof path
remains live. Each retirement needs an executable absence or delegation
verifier and an independent Evidence Ledger observation before closure.

## Mutation gate

Admit an effect only when all are current and mutually consistent:

~~~text
Goal Contract authority
+ Construction Contract selection
+ repository subject
+ execution scope and owner
+ Ledger-issued capability
~~~

Review prose, a Counterexample Set, a Construction Contract, a validator pass,
or a suggested repair alone cannot authorize mutation.
