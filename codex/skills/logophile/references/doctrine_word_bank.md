# Doctrine Word Bank

Use these as defaults, not mandates. Pick words for procedural gain, not prestige.

## Failure-mode words
- `unsound`: reject unsupported inferences; surface missing premises and invalid guarantees.
- `unwitnessed`: a guarantee lacks a concrete witness: invariant, check, construction, type restriction, or test.
- `ill-typed`: the representation admits states, transitions, or values that do not fit the claimed domain.
- `illegal inhabitant`: an impossible state is representable.
- `partial`: an eliminator, handler, or case split only works for part of the intended domain.
- `non-total`: a required path can fail to produce a legal continuation.
- `incoherent`: layers disagree about what an abstraction, state, or protocol means.
- `non-compositional`: behavior works locally but fails when combined with adjacent paths.
- `ill-founded`: retries, recursion, dependency chains, or state transitions lack a terminating/progress-preserving structure.
- `vacuous`: reject empty, tautological, or content-free claims.
- `spurious`: challenge accidental patterns and misleading correlations.
- `pathological`: hunt edge cases and weird failure surfaces.
- `ill-posed`: question whether the task is specified tightly enough.
- `confounded`: look for mixed causes or ambiguous attribution.
- `hazard-seeking`: hunt misuse traps and foot-guns.
- `fail-closed`: prefer safe refusal over silent permissive failure.

## Reasoning-mode words
- `mechanistic`: explain causal chains, not symptoms.
- `falsifiable`: frame claims as testable and disprovable.
- `canonical`: prefer standard forms and primary paths.
- `compositional`: break the task into parts with explicit interfaces.
- `parsimonious`: minimize assumptions and moving parts.
- `adversarial`: try to break the first plausible answer.
- `source-disciplined`: prefer primary and authoritative evidence.
- `calibrated`: match confidence to evidence.
- `synthetic`: compress many signals into a concise comparative frame.
- `constructive`: prefer explicit witnesses and constructions over vibes.
- `coherent`: ensure definitions, behavior, and layers agree globally.

## Type-theoretic / soundness words
- `witness-bearing`: every guarantee has a visible witness.
- `preservation-aware`: transformations preserve the promised invariant.
- `progress-aware`: valid states can keep moving without getting stuck.
- `refinement-first`: lower-level representations preserve higher-level contracts.
- `total`: handlers and eliminators cover the intended domain.
- `inhabitance-aware`: ask what states are newly possible and whether they should be.
- `constructor/eliminator-aware`: check both what creates a state and what consumes it.
- `well-founded`: recursion, retries, and state transitions have a terminating or progress-preserving shape.

## Scope / execution words
- `accretive`: prefer additive, reviewable change.
- `surgical`: minimize blast radius and irrelevant edits.
- `orthogonal`: keep concerns separated.
- `reversible`: leave a low-cost path to back out or isolate.
- `idempotent`: make repeated application safe.
- `deterministic`: control hidden state, time, and randomness.
- `hermetic`: reduce ambient dependencies and hidden context.
- `surface-area-minimizing`: keep interfaces and complexity small.
- `contract-first`: define success and invariants before editing.
- `seam-conscious`: choose the smallest stable boundary that can carry the fix.

## Verification / reporting words
- `traceable`: tie claims to evidence, diffs, tests, or sources.
- `exhaustive`: cover all material branches, not just the happy path.
- `invariant-preserving`: preserve named truths across change.
- `auditable`: make the review path legible to others.
- `reproducible`: make the result checkable by rerunning.
- `fixed-point`: stop only when a fresh pass finds no material change.
- `saturating`: keep iterating while new material findings still appear.

## Weak words unless made operational
- `smart`
- `deep`
- `insightful`
- `nuanced`
- `thoughtful`
- `sophisticated`
- `elegant`

Only keep these if the surrounding doctrine block turns them into explicit checks or constraints.
