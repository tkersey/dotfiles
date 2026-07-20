# Artifact Kernel Owner Map

Use this reference to locate the unique owner of each `artifact-kernel-v1`
decision. Do not restate an owner's schema or lifecycle law in a downstream
skill.

## Four authoritative per-goal families

| Family | Semantic owner | Irreducible question | Exact contract |
|---|---|---|---|
| `goal-contract/v3` | accepted source through `$goal-contract` | What must be true, remain true, and is authorized? | [Goal Contract v3](../../goal-contract/references/artifact-kernel-v1.md) |
| `counterexample-set/v1` | `$review-fold` | What witnessed behavior falsifies the current construction? | [Review Fold](../../review-fold/SKILL.md) |
| `construction-contract/v1` | `$actuating` using `$universalist` | What structure realizes the laws, excludes Counterexamples, and retires residue? | [Construction Contract](construction-contract.md) |
| `actuating-evidence-event/v1` | each event body's domain owner | What happened and what was independently observed? | [Ledger commands](kernel-commands.md) |

The Goal Contract is the sole per-goal semantic-authority artifact. The
Counterexample Set is the sole classified-bug artifact. The Construction
Contract is the sole architecture-selection artifact. The Evidence Ledger is
the sole mutable per-goal truth. Ledger owns canonical envelopes, content
identity, custody, append integrity, replay, validation, folds, and projections;
it does not take the semantic owner's authority.

## Exact downstream owners

- Goal shape, authority, exclusions, and common immutable envelope:
  [Goal Contract v3](../../goal-contract/references/artifact-kernel-v1.md).
- Counterexample shape, evidence, quotienting, stable class identity, and
  non-authority: [Review Fold](../../review-fold/SKILL.md).
- Architecture selection, proof modes, successor lineage, and retirements:
  [Construction Contract](construction-contract.md).
- Static 1+4 topology, recovery, reset, and five-clean convergence:
  [Review Contract](review-contract.md).
- Transient envelopes, capabilities, event admission, and replay commands:
  [Ledger commands](kernel-commands.md).
- Closure theorem and projections: [Derived Closure](closure.md).
- Public effects and `SHIP-v1`: [Ship](../../ship/SKILL.md).

These linked owners are normative. This map contributes no parallel schema or
mutable state.

Ledger's release registry projects the static Review Contract into runtime.
The Goal-bound digest must resolve to one exact frozen entry, including its
ordered lens roles and byte-exact lens contracts; future versions append
entries instead of revising v1. Registry validation and dispatch projection do
not transfer review-law authorship to Ledger.

## Evidence-specific law

The Evidence Ledger is append-only. Artifact bytes, verifier logs, and test
reports may be content-addressed Ledger attachments. CAS and Ship receipts
remain owner-issued external evidence referenced by digest; Actuating does not
copy their full schemas or create a peer custody protocol. Universalist plans
remain supporting reasoning. State, campaign status, clean streak, retirement
completion, WorkGraph, Proof Patch, and closure are discardable projections.

`operation_observation_reserved` is an irreducible causal event. Ledger appends
it immediately before verifier execution with body schema
`operation-observation-reserved/v1` and fields `step_id`, `effect`,
`idempotency_key`, `capability_digest`, `subject_digest`, and `verifier`. Only
the exactly matching `operation_observed` or an admitted `operation_aborted`
may follow. This prevents duplicate verifier effects under races, retries,
timeouts, or lost command output.

## Protocol admission and migration

Each registered goal has one immutable protocol fact in the canonical Evidence
Ledger. An unregistered Goal ID has no marker: its accepted execution route is
only a transient selector and must not create a peer pre-registration artifact.
After the complete Goal and K0 input passes `open`, `goal_contract_registered`
is the first durable `artifact-kernel-v1` fact. Legacy admission uses
`goal_protocol_registered` with `construction_ref: null`, the current repository
subject digest, and this exact canonical body:

~~~json
{"protocol":"legacy-actuating-v1","schema":"goal-protocol-registration/v1"}
~~~

Same-protocol admission is idempotent and conflicting admission fails closed.
Legacy `open` appends or confirms that marker before `run_opened`. Its selected
legacy store may still use arbitrary `--path`; the artifact Evidence path is
fixed at `.ledger/actuation/artifact-kernel/evidence.jsonl`, and artifact
`--path` is retired. A separate `protocol-bindings.jsonl` file is ignored
residue, never authority. Invalid legacy history blocks.

Production is Phase 4 opt-in: an explicit `--goal` admits a new
artifact-kernel goal, while the unqualified route remains frozen legacy
behavior. Retiring legacy writers or changing the default route still requires
an operator-authoritative complete inventory of historical custom legacy
stores, validation of each complete chain, and legacy protocol events for every
historical goal.

Historical artifacts remain readable through deterministic adapters; adapters
never authorize a new writer. Rollback changes only future admissions and never
reinterprets an existing goal.

### Mode-aware legacy cutover projection

`actuating-legacy-cutover-manifest/v3` remains frozen full-closeout
compatibility: it implies the complete bare route, requires all ten
digest-bound legacy/candidate sources, and answers all eight equivalence
questions. V4 adds exact root `legacy_mode`: `bare`, `implement`, `triage`,
`remediation-plan`, or `review-closeout`. Every one of the same ten source slots
must be tagged either `present` with path and expected digest or
`not-applicable`; missing input never implies non-applicability.

Every v4 mode requires the legacy Goal Contract and candidate Evidence. Bare
and review-closeout require every source and question. Implement additionally
requires legacy state, closure decision, and events, and answers subject
identity, implementation obligations, and closure verdict. Triage additionally
requires legacy RF, review policy, and CAS receipt, and answers subject
identity, review-request completeness, and standard clean count.
Remediation-plan additionally requires legacy RF and review resolution, and
answers subject identity, unresolved accepted findings, and retirement debt.
All eight join rows remain present; an inapplicable row has explicit
`legacy-mode-not-applicable` status, reason, and null observations.

A required `not-applicable` source, forbidden `present` source, digest or join
mismatch, or malformed source blocks. The v4 applicability refinement is an
intentional mode-aware qualification of the original all-question cutover law;
v3 preserves that law unchanged for full closeout. Neither version authorizes
mutation, mixes protocols, or writes a new Artifact Kernel goal. V2 remains
invalid.

Current successor admission is an irreducible ordered transition rather than a
new artifact family. Ledger-owned `open` appends exact `goal-superseded/v2` to
the current predecessor before fresh successor Goal/K0 registration, invalidates
that predecessor's pending operation and derived credit, and permits retry only
against the exact durable edge. Frozen lineage replay may still consume exact
read-only `goal-superseded/v1` Evidence; v1 cannot authorize a current event.

Current Artifact Kernel publication admission validates the complete exact
`SHIP-v1` owner envelope and requires a digest-shaped `actuation_run_id`.
Frozen migration readers may relax only that identity to a nonblank opaque
historical value. All validation, action/readiness, PR-state, URL, and subject
joins remain exact, and read compatibility never authorizes a current write.
Ledger projects publication currentness only while live HEAD, symbolic branch,
and Goal-base branch identity still match the receipt's `head_sha`, `branch`,
and `base_branch`; it does not infer a repository or base SHA absent from
`SHIP-v1`.

## Bankruptcy gate

Add no mandatory artifact unless it answers a new irreducible question, has a
named owner and consumer, cannot be derived, prevents a named failure, replaces
existing surface, and includes migration and retirement. An artifact whose only
purpose is coordinating other artifacts is prohibited.
