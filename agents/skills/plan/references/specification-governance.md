# Specification Governance

A supplied specification is candidate evidence. Preserve its useful decisions while
correcting unsupported authority, repository mismatch, drift, hidden architecture,
and proof-shaped omissions. Do not preserve its organization merely because prose
already exists.

## Authority and evidence

User requirements govern intended behavior. Repository artifacts establish current
facts and existing obligations, not a veto against explicitly authorized changes.
Accepted public contracts, compatibility, and migration constraints still matter;
resolve a real conflict instead of either blindly preserving or discarding them.
Candidate mechanisms remain proposed means unless accepted authority fixes them.

Inspect the objective and explicit decisions, relevant repository state, existing
contracts, tests/schemas/migrations, operational evidence, candidate specification,
and the exact prior specification when revising. For substantial or reconstructed
work, surface only an evidence brief that changes a decision: current behavior,
relevant surfaces, constraints, proof available, unverified facts, and missing user
judgment. Do not emit a fixed inventory of empty fields.

Ask 1-3 atomic, bounded questions per round only for material judgment that artifacts
cannot resolve. Prefer a justified recommendation. When no question is needed,
proceed; keep the reason internal. A default has an owner, consequence, and
invalidator, and is not a locked user decision.

## Disposition and drift

```text
adopt        decision-complete and source-consistent
repair       sound direction with bounded invalid or missing sections
reconstruct  unsound authority, organization, scope, or proof basis
block        unavailable judgment or authority prevents an honest specification
```

Even `adopt` receives the invariant challenge and final source reread. Repair only
implicated sections and every dependent derivation. Reconstruct the means without
erasing valid required behavior or failed evidence.

Compare the result against the authoritative objective, target, scope/non-goals,
public behavior, compatibility, authorized effects, proof bar, rollback, and truly
source-fixed architecture. Unapproved drift blocks with the concrete difference.
Do not turn the repository's incumbent mechanism or the planner's selected means
into a new required outcome.

## Decision completeness

Establish the goal, intended user/maintainer, scope, non-goals, fixed decisions,
primary invariant, required-valid domain, acceptance, proof bar, compatibility,
rollout/rollback, and consequential seam dispositions. Use
architectonic-specification.md only when the boundary is a live semantic choice.

Every material open question needs an owner, consequence, default or blocker, and
invalidator. Every evidence-conditioned implementation choice needs its admissible
alternatives, exact deciding observations, forbidden outcomes, and safe stop/default.
An empirical choice may remain conditional. Missing authority cannot be hidden in
an observation branch. A deferred item affecting the done-state blocks completion.

Decision-complete means no material decision is unowned. Selected means may change
within their source-bounded or delegated local envelope; required outcomes and hard
constraints may not. Preserve this distinction in the emitted plan.

## Derive the specification

Include the following semantics, combining headings when that removes duplication:

```text
objective and current state
scope and non-goals
fixed decisions, selected means, and explicit defaults
requirements and compatibility
architecture, owners, laws, falsifiers, and invalidators
implementation approach and dependency-ordered work
requirement -> owner -> factor -> enforcement -> implementation -> proof
migration, retirement, risks, rollback/abort, and binary done-state
non-blocking open/deferred items
```

For a consequential construction, use action-contract.md to bind the supported
invalid family, preserved valid domain, admission/ownership/transition mechanism,
independently derived coverage, preselected discriminator, and claim strength.
Do not confuse a test command or a checked type name with proof of family exclusion.
Plan prepares these obligations; execution establishes them on actual code.

Each action establishes, transports, migrates, retires, proves, or removes a bypass
for a factor. Re-derive work that realizes a superseded factor or bypasses its owner.
The specification and execution sequence are one result; do not maintain parallel
spec-level and EPG-level task inventories in human-only planning.

## Readiness and stop

The result must state what is being built, for whom, by changing what, explicitly
excluding what, under which fixed constraints, with which completion evidence.
Block only affected synthesis for unavailable material judgment, conflicting
source authority, objective drift, an obstructed seam, an inoperable proof bar, or
an unowned compatibility/rollback consequence. Report the missing authority or
observation. Do not certify partial output or create a governance receipt.
