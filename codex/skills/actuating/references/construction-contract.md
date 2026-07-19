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
itself.

## Initial construction

Create `K0` before material mutation. Use a compact Construction when the
existing owner is exact, no competing material construction exists, no new
boundary or mechanism is introduced, and no abstraction is displaced. Use a
supporting Universalist plan for consequential selection.

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
