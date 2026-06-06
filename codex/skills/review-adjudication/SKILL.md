---
name: review-adjudication
description: >-
  Discriminately adjudicate PR review comments before implementation. Treat each
  comment as a claim to test, preserve raw comment identity and input inventory,
  bind decisions to artifact state, build the strongest no-change countercase,
  separate valid concerns from valid proposed fixes, recover PR rationale with
  explicit `$seq` when needed, and emit a stale-proof gated ledger,
  resolve-selection map, adversarial action matrix, ablative/isomorphic counterproposal,
  resolution warrants, and surface budgets that decide what to address, validate
  only, resolve with proof only, rebut, defer, investigate, delete/collapse, or
  route. Trigger for `$review-adjudication`, review the review, adjudicate PR
  comments, are these comments relevant, which comments matter, should we act on
  these comments, gate review comments before implementation, refine this list to
  just those worth resolving, or select review comments to resolve. Not for
  implementing fixes, writing rebuttals only, or final merge closure.
---

# Review Adjudication

## Intent

Decide which PR review comments should change code, which should be rebutted,
which are stale or out of scope, which require validation only, which should be
resolved with proof only, and which should be reframed as a governing invariant
instead of handled as isolated local fixes.

This skill is **discriminative**, not deferential. A reviewer comment is an input
claim, not an obligation. `act` is a conclusion that must be earned from current
artifact evidence, a defeated no-change countercase, an ablative surface check,
and explicit adversarial clearance for the downstream action.

## Default mode

Use **Surface-Budgeted Ablative-Isomorphic v8** mode whenever the input contains real review
comments. This mode is mandatory because automation needs:

- stable raw comment identity
- complete input-comment inventory coverage
- artifact-state identity for stale-handoff detection
- explicit decision tests for every comment
- evidence-grade and evidence-reference separation
- resolve-selection mapping for implementation, validation, proof-only thread
  resolution, no-change, blocked outcomes, and deletion/collapse/canonicalization
- adversarial action coverage for every selected downstream action
- parallelism calibration so adversarial effort is spent where it can change the
  route, proof, owner, or budget
- proof refs and route rationale for every downstream selection
- resolve countercases so "worth resolving" is challenged separately from concern
  validity
- selection-skew auditing so "all are worth resolving" cannot pass silently
- handoff-agenda consistency checks so selected work is not broadened later
- separate implementation, validation, and reply handoff permissions
- Resolution Warrants that act as scoped, expiring downstream permissions
- Surface Budget Ledger entries that force subtractive-first solution search and
  cap additive semantic surface
- Ablative Counterproposals that prove deletion, collapse, reuse, privatization,
  or canonicalization was considered before additive mutation is licensed
- Ablative Isomorphism Cards that prove behavior preservation before deletion,
  collapse, reuse, or canonicalization is licensed
- Clone-classification and abstraction-ladder checks before merging, extracting,
  or introducing shared abstractions

Other modes are allowed only when they still satisfy the completion gate:

- **Standard**: expanded reasoning plus the full Surface-Budgeted Ablative-Isomorphic v8 tail.
- **Fast**: bucket-only output plus the completion gate; allowed for exploratory
  triage or synthetic comments, not for implementation handoff unless the gate
  passes.

## Doctrine

Operate in **DISCRIMINATIVE**, **REBUTTAL-FIRST**, **ADVERSARIAL-BY-DEFAULT**,
**PARALLEL-WHEN-MATERIAL**, **INVARIANT-SEEKING**, **ABLATIVE**,
**ISOMORPHIC**, **CLONE-CLASSIFIED**, **ABSTRACTION-LADDERED**,
**CANONICALIZING**, **DOMINANCE-TESTED**, **ANTI-RUBBER-STAMP**,
**EVIDENCE-WEIGHTED**, **STALE-PROOF**, and **FAIL-CLOSED** mode.

- **DISCRIMINATIVE**: separate true concerns from irrelevant, stale, unsupported,
  preference-only, misdiagnosed, or misframed comments.
- **REBUTTAL-FIRST**: for each comment, construct the strongest no-change
  countercase before deciding to act.
- **ADVERSARIAL-BY-DEFAULT**: every selected downstream action must have an
  adversarial response that tries to defeat that action, downgrade it, reroute it,
  narrow it, or block it.
- **PARALLEL-WHEN-MATERIAL**: run independent adversarial lanes in parallel when
  parallel challenge can reduce elapsed time without compromising current-state
  grounding or single-writer safety.
- **INVARIANT-SEEKING**: look for the governing invariant behind repeated local
  comments; avoid fixing the same invariant piecemeal.
- **ABLATIVE**: when a comment is valid, prefer removing accumulated surface,
  collapsing duplicate paths, privatizing exposed internals, canonicalizing
  ownership, or deleting/decommissioning vestigial scaffolding before licensing
  additive code.
- **ISOMORPHIC**: deletion, collapse, merge, reuse, and canonicalization require
  an explicit behavior-preservation proof, not a cleanliness intuition.
- **CLONE-CLASSIFIED**: classify apparent duplication before merging it; exact,
  parametric, and bounded gapped clones are candidates, while semantic clones and
  accidental rhymes require proof or rejection.
- **ABSTRACTION-LADDERED**: do not create or climb abstractions before the callsite
  count, axes of variance, and proof burden justify the rung.
- **CANONICALIZING**: collapse duplicate truth surfaces into one owner, one
  representation, one path, or one proof surface where the live contract permits.
- **DOMINANCE-TESTED**: mark a proposed additive fix as dominated when a lower
  surface route preserves the same contract with better ownership, proof, or
  maintainability.
- **ANTI-RUBBER-STAMP**: do not let plausibility, politeness, reviewer authority,
  parallel consensus, or ease of implementation become acceptance evidence.
- **EVIDENCE-WEIGHTED**: rank current artifacts above memories, memories above
  intuition, and direct proof above consensus.
- **STALE-PROOF**: bind adjudication to branch/head/diff/comment-set state so
  downstream handoffs can detect stale or contradictory agendas.
- **FAIL-CLOSED**: if adjudication, adversarial clearance, ablation clearance, or
  warrant contract is incomplete, block implementation handoff rather than guessing.

## Contract

- Review comments are claims to test, not truths to obey.
- `act` is a conclusion, not the default.
- Current artifact state outranks reviewer intuition.
- Prefer current-session artifacts over memories.
- Use memories as secondary rationale support and provenance, not as the sole
  basis for acting.
- Distinguish concern validity from proposed-fix validity.
- Separate relevance from actionability.
- Preserve raw comment identity; do not let summaries replace comment IDs,
  reviewers, excerpts, locations, or input inventory.
- Preserve artifact-state identity; do not let a handoff become stale invisibly.
- Tail-weight outputs for CLI use.
- Do not implement fixes here.
- Do not create an implementation handoff unless the Adjudication Gate passes,
  `implementation_handoff_allowed: yes`, every `address` row has adversarial
  clearance, and every mutation-capable row has ablative-surface clearance.
- Do not collapse adjudication into "all comments are worth resolving"; emit the
  resolve-selection map before implementation or thread-resolution handoff.
- Do not let `address` mean "add code". Every mutation-capable warrant must carry
  a surface budget, deletion/reuse/refactor/canonicalization probe obligation,
  and expansion-warrant rule before downstream implementation.
- Do not license deletion, collapse, merge, or canonicalization without an
  Ablative Isomorphism Card or an explicit `validate-first` route.
- Do not merge semantic clones or accidental rhymes merely because they look alike;
  prove equivalence across invariants, error semantics, ordering, and side effects.
- Do not introduce a new helper, adapter, interface, base class, generic, macro,
  flag, or wrapper without an abstraction-ladder check.
- Validation-only handoff is not implementation permission.
- Proof-only thread resolution is not implementation permission.
- Reply handoff is not implementation permission.
- No downstream mutation, validation-only probe, thread resolution, or
  rebuttal/defer handoff is licensed unless a matching active Resolution Warrant
  exists.
- No selected downstream action is licensed unless the Adversarial Action Matrix
  has a row for the raw claim and that row clears, preserves, or blocks the action
  consistently with the selected route.

## Dependency

This skill expects `$seq` to be installed when PR rationale recovery is needed.
If `$seq` is unavailable, proceed only from current artifacts and mark PR
rationale fields as `unknown` instead of inventing intent.


## Ablation activation receipt

Because prior usage tended to be root-equivalent or mention-only, this skill must
make ablation visible whenever it could affect the route.

Emit an ablation activation receipt for every real comment batch:

```md
Ablation Activation Receipt:
- trigger: additive-proposal | local-fix-pileup | duplicate-truth-surface | questionable-keep-surface | fixed-point-handoff | none
- custom authority used: review_ablative_surface_authority | root-equivalent | not-required
- scoped comment ids:
- selected lower-surface routes:
- additive routes cleared:
- vetoed or unresolved additive routes:
- isomorphism cards required:
- implementation handoff impact:
```

Rules:
- If `trigger` is not `none`, the receipt must be reflected in `Ablative Counterproposal Ledger`, `Resolution Warrants`, and `Adjudication Bottom Line`.
- If `trigger: none`, give the evidence-backed reason; do not omit the receipt.
- Root-equivalent adjudication is allowed only when it emits the same receipt and clearance fields as the custom authority lane.
- `address` without an ablation activation receipt is not implementation permission.


## Parallel adversarial action

Every row in `Resolve Selection` must receive one adversarial response. The
response is not decorative; it is a clearance attempt against the selected action.
It must either clear the action, preserve the no-change/defer decision, or block
handoff.

Adversarial responses should be parallelized when dimensions are independent and
read-only. Use parallel lanes to reduce elapsed time for material batches, but keep
final adjudication and all downstream writes single-rooted.

### Required adversarial dimensions by action

| selected action | adversarial response must challenge |
|---|---|
| `address` | no-change, validate-first, wrong-fix, scope/ownership, surface-budget, ablative route, isomorphism proof, fixed-point over-routing |
| `validate-only` | mutate-now, no-validation-value, wrong probe, production-mutation escape |
| `resolve-thread-only` | still-material, stale-proof insufficiency, proof-ref weakness, hidden implementation need |
| `do-not-address` | materiality, review-closure value, proof-only alternative, user/non-goal mismatch |
| `delete-collapse-canonicalize` | live contract loss, compatibility risk, missing isomorphism proof, wrong canonical owner, semantic-clone/accidental-rhyme merge |
| `blocked` | whether a narrower safe validation, reply, proof-only route, or user question can unblock |

### Parallelism modes

Use exactly one `parallelism mode` per row in the Adversarial Action Matrix:

- `root-equivalent`: root performed the adversarial challenge inline; allowed for
  obvious narrow-local, proof-only, synthetic, or no-change rows.
- `targeted-parallel`: one or two independent read-only lanes challenged the row
  or invariant cluster.
- `full-fanout`: evidence, scope/ownership, criticality, no-change, validation
  value, fix-shape, ablative-surface, and isomorphism/proof lanes were assigned in parallel.
- `swarm`: six or more specialists were needed because the batch is large,
  contentious, P2+, invariant-coupled, likely to reopen, deletion-sensitive, or behavior-preservation-sensitive.
- `not-required`: only for rows with `resolve decision: blocked` and no safe
  downstream action to challenge; the missing evidence must be named.

Use full fanout or swarm when any of these are true:

- any P2+ row might be selected as `address`
- every substantive row would otherwise be selected as `address` or `validate-only`
- any CAS/Codex finding is invariant-framed and would mutate code
- the no-change countercase is weak, generic, or reviewer-authority-shaped
- validation-only is rejected for an unproven but plausible finding
- implementation would route to `$fixed-point-driver`
- several comments share a likely governing invariant
- the selected action would add a helper, flag, branch, adapter, public symbol,
  state variant, fallback, compatibility path, or duplicate truth surface

Do not parallelize lanes that need writes, mutate fixtures, alter review threads,
or depend on each other's outputs. Parallel adversaries are read-only evidence
producers; the root adjudicator integrates them.

## Required input context

When possible, build a compact context pack before adjudication:

```md
Review comments:
- raw id/thread:
- reviewer:
- file/location:
- exact excerpt:
- reviewer-suggested fix, if any:

Current artifacts:
- artifact_state_id:
  - branch:
  - base:
  - head:
  - diff_digest:
  - comment_set_digest:
  - ci_state:
- branch/diff summary:
- touched files:
- relevant tests:
- CI/local proof status:
- PR description or stated goal:

Rationale recovery:
- current-session plan/artifacts:
- `$seq` search used: yes/no
- memory support used: yes/no
- missing rationale:
```

## Resolve Selection

Emit a stable row for every raw comment.

```md
| id/thread | reviewer | excerpt | concern validity | proposed-fix validity | freshness | materiality | governing invariant candidate | resolve decision | handoff action | proof ref |
|---|---|---|---|---|---|---|---|---|---|
```

Allowed `resolve decision` values:

- `address`
- `validate-only`
- `resolve-thread-only`
- `do-not-address`
- `delete-collapse-canonicalize`
- `blocked`

Allowed `handoff action` values:

- `mutate-code`
- `add-validation-only`
- `resolve-thread`
- `draft-reply`
- `defer`
- `none`

## Resolve Countercases

For every raw comment, construct the strongest countercase to the selected route.

```md
| id/thread | selected route | strongest countercase | countercase status | evidence ref | route impact |
|---|---|---|---|---|---|
```

Allowed `countercase status` values:

- `defeated`
- `preserved-no-change`
- `preserved-validate-first`
- `preserved-proof-only`
- `unresolved`
- `blocked`

## Ablative Counterproposal Ledger

For every `address` or `delete-collapse-canonicalize` row, emit an Ablative
Counterproposal before issuing a mutation-capable warrant.

```md
| id/thread | valid concern | additive proposal | delete candidate | collapse/reuse candidate | canonical owner candidate | privatization candidate | clone classification | abstraction-ladder check | lower-surface route | why insufficient or selected | ablative clearance | isomorphism status | proof ref |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
```

Allowed `lower-surface route` values:

- `delete`
- `collapse`
- `reuse`
- `canonicalize`
- `privatize`
- `decommission`
- `validate-first`
- `proof-only`
- `none`

Allowed `clone classification` values:

- `exact-clone`
- `parametric-clone`
- `gapped-clone`
- `semantic-clone`
- `accidental-rhyme`
- `not-applicable`
- `unknown`

Allowed `abstraction-ladder check` values:

- `not-needed`
- `rung-valid`
- `rung-skipped`
- `too-few-cases`
- `too-many-variance-axes`
- `proof-missing`
- `unknown`

Allowed `isomorphism status` values:

- `pass`
- `validate-first`
- `missing`
- `not-required`


Allowed `ablative clearance` values:

- `clear-additive`
- `select-ablative-route`
- `validate-first`
- `veto-additive`
- `unresolved`
- `not-required`

`address` with `mutate-code` is illegal unless `ablative clearance` is
`clear-additive` or `select-ablative-route` and the Resolution Warrant records the
selected route.

## Ablative Isomorphism Card

For every selected deletion, collapse, merge, reuse, or canonicalization route,
emit a compact behavior-preservation card before handoff. This is the lightweight
import from `$simplify-and-refactor-code-isomorphically`: prove behavior identical
before removing or merging surface.

```md
Ablative Isomorphism Card:
- id/thread:
- surface:
- proposed action: delete | collapse | reuse | canonicalize | privatize | decommission
- behavior preserved:
- public contract preserved:
- error semantics preserved:
- ordering / side effects preserved:
- clone classification:
- abstraction-ladder check:
- compatibility risk: none | low | medium | high
- proof signal:
- deletion/collapse witness:
- card status: pass | validate-first | missing | not-required
```

If any relevant row cannot be filled, select `validate-first` or block handoff.


## Surface Budget Ledger

Every mutation-capable warrant must include a surface budget. See
`references/surface-budget-warrants.md`.

```md
| warrant id | mode | target net loc | max positive loc | max new public symbols | max new files | max new helpers | max new flags/knobs | max new state variants | max new branches | duplicate path budget | ablative probes required | expansion warrant required | expansion status | proof required | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
```

Default mode for `mutate-code` warrants is `ablative-first`.
Deletion/collapse/canonicalization warrants must carry an Ablative Isomorphism Card unless the selected route is `validate-first`.

## Adversarial Action Matrix

Emit after `Resolve Countercases` and before `Resolution Warrants`.

```md
| id/thread | primary resolve decision | adversarial lanes | parallelism mode | strongest adversarial response | veto status | clearance | proof ref | decision impact |
|---|---|---|---|---|---|---|---|---|
```

Allowed `veto status` values:

- `cleared`
- `preserved-no-change`
- `unresolved`
- `vetoed`
- `blocked`
- `not-required`

Allowed `clearance` values:

- `cleared`
- `preserved`
- `rerouted`
- `downgraded`
- `blocked`

Rules:

- `address` requires `veto status: cleared`, `clearance: cleared`, and a concrete
  proof ref that defeats the strongest no-change / validate-first / wrong-fix /
  scope / budget / ablative alternative.
- `validate-only` requires `veto status: cleared`, `clearance: cleared` or
  `downgraded`, and proof that validation is the correct next action instead of
  mutation or no action.
- `resolve-thread-only` requires `veto status: cleared` or
  `preserved-no-change`, `clearance: preserved`, and a proof ref that makes code
  mutation unnecessary.
- `do-not-address` requires `veto status: preserved-no-change` or `cleared`,
  `clearance: preserved`, and a proof/ref explaining why no downstream action is
  selected.
- `delete-collapse-canonicalize` requires live-contract preservation evidence and
  an ablative clearance packet.
- `blocked` requires `veto status: blocked` or `unresolved`, `clearance: blocked`,
  and a missing-evidence proof ref.
- A vetoed or unresolved adversarial response must block implementation handoff
  unless the row is rerouted to a stricter non-mutating action with a matching
  warrant.

## Authority fanout

Use custom read-only Codex agents when available. The package includes the
runnable authority panel under `codex/agents/`:

- `review_evidence_authority`
- `review_direction_ownership_authority`
- `review_criticality_authority`
- `review_no_change_advocate`
- `review_validation_value_authority`
- `review_fix_shape_authority`
- `review_ablative_surface_authority`

If custom agents are unavailable, emit root-equivalent packets with the same role
names and schema. Root-equivalent packets must be evidence-bearing and are not a
license to skip the clearance matrix or veto ledger.

## Resolution Warrants

Resolution Warrants are scoped, expiring permissions. They are not general task
instructions.

```yaml
resolution_warrant:
  warrant_id: "..."
  raw_comment_ids: []
  artifact_state_id: "..."
  permitted_action: mutate-code | add-validation-only | resolve-thread | draft-reply | defer | none
  selected_route: address | validate-only | resolve-thread-only | do-not-address | delete-collapse-canonicalize | blocked
  permitted_scope: []
  forbidden_actions: []
  proof_required: "..."
  surface_budget:
    mode: ablative-first | additive-authorized | proof-only | validation-only | not-applicable
    ablative_clearance: clear-additive | select-ablative-route | validate-first | veto-additive | unresolved | not-required
    lower_surface_routes_defeated: []
    clone_classification: exact-clone | parametric-clone | gapped-clone | semantic-clone | accidental-rhyme | not-applicable | unknown
    abstraction_ladder_check: not-needed | rung-valid | rung-skipped | too-few-cases | too-many-variance-axes | proof-missing | unknown
    isomorphism_status: pass | validate-first | missing | not-required
    expansion_warrant_required: yes | no
  expires_when: "artifact_state changes, comment set changes, or proof ref becomes stale"
```

## Completion gate

Before final handoff, emit:

```md
Adjudication Gate:
- raw_comment_inventory_complete: pass/fail
- artifact_state_bound: pass/fail
- resolve_selection_complete: pass/fail
- resolve_countercases_complete: pass/fail
- adversarial_action_coverage: pass/fail
- ablation_activation_receipt: pass/fail/not-required
- ablative_counterproposals_complete: pass/fail
- ablation_isomorphism_cards_complete: pass/fail/not-applicable
- clone_classification_complete: pass/fail/not-applicable
- abstraction_ladder_checks_complete: pass/fail/not-applicable
- authority_clearance_complete: pass/fail
- surface_budgets_complete: pass/fail/not-applicable
- resolution_warrants_current: pass/fail
- implementation_handoff_allowed: yes/no
- validation_handoff_allowed: yes/no
- reply_handoff_allowed: yes/no
```

## Tail output contract

End with these sections, in this order:

1. `Act On`
2. `Validate Only`
3. `Delete / Collapse / Canonicalize`
4. `Rebut / Do Not Address`
5. `Need Evidence / Blocked`
6. `Handoff Agenda`
7. `Adjudication Bottom Line`

`Adjudication Bottom Line` must be the final section and must include:

- decisive route
- ablation activation status: triggered / not-required, with the receipt id
- highest-value ablative route, if any
- highest-value isomorphic collapse/deletion route, if any
- whether implementation handoff is allowed
- the single next action

## Hard rules

- Never use reviewer authority as evidence.
- Never convert `valid concern` into `add code` without an ablation activation receipt and ablative clearance.
- Never issue `mutate-code` permission from a stale artifact state.
- Never hide comment identity behind summaries.
- Never let every comment become `address` without an all-action skew audit.
- Never let multiple local comments hide one governing invariant.
- Never let an additive fix bypass deletion, reuse, collapse, canonicalization, or
  privatization probes.
- Never delete, collapse, or merge behavior without an isomorphism card or
  validate-first route.
- Never climb the abstraction ladder merely to satisfy a review comment.

## Resources

- [authority-fanout.md](references/authority-fanout.md)
- [surface-budget-warrants.md](references/surface-budget-warrants.md)
- [ablative-clearance.md](references/ablative-clearance.md)
- [isomorphic-ablation.md](references/isomorphic-ablation.md)
- [CODEX_SUBAGENTS.md](references/CODEX_SUBAGENTS.md)
- [ablation-activation.md](references/ablation-activation.md)
