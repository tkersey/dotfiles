# Task Pressure Map

Infer pressures from the task first. Use these defaults only when the task underspecifies them.

## Bug fix / regression / review response

Dominant pressures:
- unsound diagnosis
- hidden invariant break
- oversized fix
- missing verification

Default stack candidates:
- `unsound`
- `mechanistic`
- `accretive`
- `traceable`

Artifacts:
- Soundness Ledger
- Chosen Cut
- proof receipt

## Feature implementation / planned code

Dominant pressures:
- architecture drift
- scope creep
- unnecessary complexity
- weak verification

Default stack candidates:
- `canonical`
- `accretive`
- `invariant-preserving`
- `traceable`

Artifacts:
- contract / invariant row
- implementation seam
- verification receipt

## Plan-to-PR / execution workflow

Dominant pressures:
- analysis without movement
- stale plan graph
- missing proof before ship
- incomplete task closure

Default stack candidates:
- `actuating`
- `fixed-point`
- `proof-gated`
- `traceable`

Artifacts:
- Actuation Receipt
- `$st` task graph / completion receipts
- closure gate

## Code review / adversarial audit

Dominant pressures:
- local blindness
- untested assumptions
- regression risk
- misuse hazards

Default stack candidates:
- `adversarial`
- `exhaustive`
- `hazard-seeking`
- `traceable`

Artifacts:
- candidate inventory
- strongest countercase
- change agenda

## Review adjudication / should we act?

Dominant pressures:
- over-acceptance
- reviewer authority bias
- local-validity trap
- additive mutation from comments

Default stack candidates:
- `discriminative`
- `rebuttal-first`
- `invariant-seeking`
- `ablative`
- `evidence-weighted`

Artifacts:
- resolve-selection map
- no-change countercase
- governing invariant candidate
- ablation activation receipt

## Soundness / invariant review

Dominant pressures:
- unwitnessed guarantees
- illegal inhabitants
- partial eliminators
- broken preservation/progress
- incoherent abstractions

Default stack candidates:
- `unsound`
- `unwitnessed`
- `ill-typed`
- `total`
- `preservation-aware`
- `progress-aware`

Artifacts:
- Soundness Ledger
- totality table
- witness receipt

## Abstraction teardown / technical debt / deletion

Dominant pressures:
- addition bias
- duplicate truth surfaces
- vestigial scaffolding
- accidental-rhyme merges
- over-preservation

Default stack candidates:
- `ablative`
- `winnowing`
- `quotienting`
- `normalizing`
- `refinement-preserving`

Artifacts:
- Ablation Ledger
- Reduction Certificate
- quotient relation
- recomposition proof

## Simplification with strict behavior preservation

Dominant pressures:
- behavior drift
- bad DRY merges
- hidden side effects
- proof weakness

Default stack candidates:
- `isomorphic`
- `clone-classified`
- `abstraction-laddered`
- `traceable`

Artifacts:
- Isomorphism Card
- duplication map
- LOC / surface delta

## Knowledge extraction / session archaeology

Dominant pressures:
- memory/provenance drift
- noisy hits
- shallow summaries
- unsupported causality

Default stack candidates:
- `forensic`
- `cartographic`
- `provenance-preserving`
- `triangulating`
- `saturating`

Artifacts:
- Provenance Map
- source stratification
- contradiction ledger
- saturation stop rule

## Systems thinking / intervention design

Dominant pressures:
- local optimization
- missed feedback loops
- second-order effects
- wrong control point

Default stack candidates:
- `cybernetic`
- `cartographic`
- `leverage-seeking`
- `actuating`

Artifacts:
- Cybernetic Map
- control-point receipt
- proof of movement

## Reset / stale state / workflow restart

Dominant pressures:
- stale proof
- outdated branch/head/session memory
- invalidated assumptions
- inherited route errors

Default stack candidates:
- `rebaselining`
- `stale-proof`
- `reconciling`
- `canonicalizing`

Artifacts:
- Baseline Receipt
- stale artifact list
- current authority map

## Hidden behavior / callbacks / defunctionalization

Dominant pressures:
- opaque higher-order control flow
- scattered handlers
- missing totality
- weak inspectability

Default stack candidates:
- `reifying`
- `closed-world`
- `totalizing`
- `inspectable`
- `algebraic`

Artifacts:
- behavior algebra
- constructors / payloads
- total interpreter
- preservation proof

## Security review

Dominant pressures:
- permissive failure
- hidden attack surfaces
- unsafe defaults
- unproved mitigations

Default stack candidates:
- `fail-closed`
- `adversarial`
- `hazard-seeking`
- `traceable`

Artifacts:
- threat/hazard ledger
- mitigation proof
- fail-closed decision

## Research memo / market scan

Dominant pressures:
- weak sourcing
- overclaiming
- shallow synthesis
- bloated prose

Default stack candidates:
- `source-disciplined`
- `calibrated`
- `adversarial`
- `synthetic`

Artifacts:
- source ledger
- confidence map
- counterclaim table

## Planning / strategy

Dominant pressures:
- ill-posed goals
- hidden assumptions
- missing tradeoffs
- false certainty

Default stack candidates:
- `ill-posed`
- `calibrated`
- `parsimonious`
- `tractabilizing`
- `traceable`

Artifacts:
- governing question
- option table
- dominant move

## Naming / policy wording / contracts

Dominant pressures:
- semantic drift
- obligation drift
- vague scope
- overloaded terminology
- weak doctrine grammar

Default stack candidates:
- `precise`
- `scoped`
- `obligation-preserving`
- `distinctive`
- `operator-aligned`

Notes:
- `precise`, `scoped`, `obligation-preserving`, and `operator-aligned` are task-local descriptive labels.
- Use them only if they produce an actual gain in the doctrine block.
- Replace generic defaults with sharper domain terms whenever the task supports them.
