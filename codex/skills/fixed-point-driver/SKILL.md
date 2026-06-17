---
name: fixed-point-driver
description: "Drive exhaustive build-review-improve-verify loops to Truth-Owner Ablative-Isomorphic Normal Form: canonical invariant owners, no duplicate truth surfaces, unresolved counterexamples, ablation vetoes, unretired scaffolding, or dominated surfaces without warrants, with behavior-preserving proof closure. Trigger for de novo coding review, PR review closure, repeated review/fix loops, invariant repair, proof-surface hardening, CAS/Codex review resolution, parallel adversarial action, or local-patch risk. Not for trivial one-step tasks or one narrow phase."
---

# Fixed-Point Driver

This skill coordinates implementation, review, adjudication, reduction,
verification, parallel read-only adversarial challenge, ablation challenge, and
closure until the artifact set reaches **Truth-Owner Ablative-Isomorphic Normal Form**.

## The single rule

Drive toward this state:

> Every material invariant has exactly one canonical owner, every witness points
> back to that owner, every review finding is either discharged or represented as
> a counterexample, every adversarial or ablation veto is cleared, accepted as
> risk, or routed, every additive scaffold has been promoted/collapsed/deleted,
> every dominated/subsumed/vestigial/non-canonical surface has been deleted,
> collapsed, privatized, decommissioned, or kept with an explicit warrant, and every deletion/collapse/canonicalization has a current behavior-preservation
> witness, and no
> duplicate truth surface remains merely because it helped satisfy an intermediate
> review loop.

A fixed point is not “review is clean.” A fixed point is a normal form of the
code and proof system.

## Why this skill exists

Frontier coding agents are good at adding code and addressing review comments.
They are weaker at noticing that the best fix is to delete a path, collapse
duplicate owners, privatize a surface, tighten the one boundary that should have
owned the invariant from the start, or let a parallel adversary invalidate the
local patch before time is spent implementing it.

This skill converts review churn into an ownership-normalization and
surface-ablation problem. It converts adversarial pressure into time-efficient,
read-only clearance packets and converts deletion pressure into witness-backed
Ablation Ledger rows.

## Doctrine alpha driver

This skill owns the conversion from doctrine-rich pressure into normal-form
artifacts.

Use doctrine only when it changes the route:

- `fixed-point` creates a reopenable material fixed-point gate, not a long review
  loop by default.
- `invariant` creates or updates a Truth Unit and owner edge.
- `canonical` selects one owner/representation and retires, privatizes, or
  justifies shadow owners.
- `witness` creates proof receipts tied to current head/artifact state.
- `adversarial` / `de novo` creates candidate inventory, challenger packets, and
  no-finding countercases.
- `parallel` creates independent read-only adversarial lanes when it can reduce
  elapsed time or prevent wrong action.
- `unwitnessed guarantee` / `illegal inhabitant` creates Soundness Ledger rows.
- `ablative` creates Ablation Ledger rows and prevents additive mutation until
  deletion, collapse, reuse, privatization, decommissioning, or canonicalization
  is defeated or selected.
- `isomorphic` creates Ablative Isomorphism Cards so deletion, collapse, merge,
  reuse, or canonicalization preserves observable behavior.
- `clone-classified` prevents accidental-rhyme or semantic-clone merges from being
  treated as safe simplification.
- `abstraction-laddered` prevents new helpers/interfaces/generics/wrappers from
  skipping the evidence rung.
- `dominated` creates a delete/collapse candidate when an existing path covers
  the obligation with lower complexity or stronger proof.
- `subsumed` creates an owner-canonicalization candidate when a local abstraction
  no longer owns a distinct obligation.
- `vestigial` creates a decommission/delete candidate when a surface only remains
  from a retired obligation.
- `uninhabited` creates a deletion/assertion candidate when a branch/state cannot
  legally occur under current constructors and invariants.

### Overprocessing guard

Do not use this skill for simple bounded tasks where ordinary direct execution
plus one focused check fully closes the state space. If the run stays active, the
reason must be a material open truth unit, stale proof, unresolved counterexample,
unresolved adversarial veto, unresolved ablation veto, unresolved isomorphism gap, shadow owner, addition
escrow, route-changing architecture uncertainty, or active warrant that requires
fixed-point handling.


### Ablation activation rule

Every fixed-point run must explicitly decide whether ablation is active. Use `ablation_activation_sentinel` when activation is ambiguous, root-equivalent, or any selected route could mutate, preserve, delete, collapse, canonicalize, privatize, or decommission code surface.

Set `ablation_activation` to one of:

- `required`: additive mutation, duplicate truth surface, questionable kept surface, local-fix pileup, or PR/review closure could change by deleting/collapsing/canonicalizing instead;
- `not-required`: the run is proof-only, validation-only, or has no mutation-capable / keep-surface decision;
- `blocked`: the artifact state is too stale or incomplete to judge ablation safely.

When `ablation_activation: required`, use `ablation_activation_sentinel` to stamp the activation decision when ambiguous, then use `ablation_auditor` or a root-equivalent
Ablation Packet before closure handoff. Root-equivalent is acceptable only when it
emits Ablation Ledger rows or a concrete no-candidate receipt. Do not let a
fixed-point run end with implicit ablation. If `ablation_activation: not-required`, include sentinel-shaped not-required evidence.


### Local-validity trap breaker

When several findings are each locally valid, ask whether they are all
counterexamples to the same truth unit. If yes, prefer one owner-level rewrite or
canonicalizing/ablative move over multiple local patches.

## Parallel adversarial and ablative action

This skill is **parallel-adversarial by default** for material actions and
**ablative-before-additive** for mutation routes, but single-writer for all code
changes.

Every material action must have an adversarial response:

| phase/action | adversarial response |
|---|---|
| warrant intake | Is the warrant stale, expired, overbroad, or incompatible with current artifact state? |
| truth-unit extraction | Is the invariant split incorrectly? Is the canonical owner wrong? Are there shadow owners? |
| route selection | Is delete/reuse/refactor/canonicalize/privatize/no-change/validate-first better than mutation? |
| implementation | Does the patch exceed warrant scope or surface budget? Does it add duplicate truth surfaces? |
| validation | Does proof exercise the real failure mechanism and current artifact state? |
| de novo review | Are there unlisted counterexamples, illegal inhabitants, or unretired scaffolds? |
| ablation pass | Are there dominated, subsumed, vestigial, uninhabited, pass-through, or non-canonical surfaces that should be removed or warranted? |
| one-change challenge | Is there one remaining impactful change before closure? |
| closure handoff | Are proof receipts current and all adversarial/ablation vetoes cleared or explicitly routed? |

Parallelism modes:

- `root-equivalent`: root performs the adversarial/ablative response inline for
  narrow, bounded, already-proof-bearing work.
- `targeted-parallel`: one or two independent read-only lanes challenge distinct
  uncertainty classes.
- `expanded-targeted`: three or four lanes for coupled truth units, stale proof,
  negative evidence, surface-budget risk, or ablation risk.
- `swarm`: five or more lanes for large, contentious, P2+, invariant-coupled,
  deletion-sensitive, or likely-to-reopen runs.
- `not-required`: no safe action exists; block and name missing evidence.

Parallel adversaries may gather evidence, inspect surfaces, challenge proofs, map
hazards, test invariants conceptually, and identify deletion/collapse candidates.
They must not edit code, alter fixtures, resolve threads, or draft final replies.
The root coordinator integrates packets and keeps writes single-threaded.

## Companion skills

- `review-adjudication` decides which review comments matter and issues warrants;
  this skill decides whether selected work preserves Truth-Owner Ablative Normal
  Form.
- `accretive-implementer` performs implementation/remediation when the selected
  rewrite is narrow, owned, and warrant-scoped.
- `adversarial-reviewer` challenges the current artifact state and should report
  normal-form violations, not just bugs.
- `verification-closure` performs decisive proof and closure gating.
- `logophile` may sharpen PR-facing summaries, names, and doctrine stacks, but
  does not own operational policy.

## Entry conditions

Use this skill when any of these are true:

- review/fix loops are repeating
- a PR has multiple coupled comments
- review comments are locally valid but may share one governing invariant
- closure proof keeps becoming stale
- a local patch may be inferior to a delete/collapse/canonicalize/privatize move
- additive scaffolding remains after satisfying intermediate review pressure
- a Resolution Warrant routes `address`, `delete-collapse-canonicalize`, or
  `validate-only` to `$fixed-point-driver`
- an Adversarial Action Matrix selects full-fanout, swarm, contentious,
  invariant-level, structural, validation-only, ablation-sensitive, or likely-to-reopen work
- the user asks to drive a branch/changeset to closure or find all impactful issues

Do not use this skill for simple bounded tasks with an obvious check.

## Workflow

1. **Frame**
   - user goal
   - artifact state
   - current review/adjudication inputs
   - active Resolution Warrants and Adversarial Action Matrix rows
   - explicit non-goals
   - proof bar

2. **Warrant intake / parallelism plan**
   - consume `review-adjudication` output when present
   - verify each warrant is active for the current artifact state
   - preserve permitted action (`mutate-code`, `delete-collapse-canonicalize`,
     `add-validation-only`, `proof-only`, `draft-reply`, or `none`)
   - record surface budget and forbidden actions
   - choose root-equivalent, targeted-parallel, expanded-targeted, swarm, or
     not-required mode for each material action

3. **Truth Unit extraction**
   - material invariant / contract / semantic fact
   - canonical owner
   - witnesses
   - duplicate or shadow truth surfaces
   - counterexamples / review findings / adversarial vetoes

4. **Adjudication intake**
   - consume `review-adjudication` output when present
   - do not redo adjudication unless stale or contradictory
   - promote coupled local comments into a Governing Invariant Candidate
   - preserve ablative clearance and surface-budget obligations
   - do not broaden beyond active warrants or cleared adversarial actions

5. **Ablative preflight**
   - identify surfaces that may be dominated, subsumed, vestigial, uninhabited,
     unreachable, pass-through, duplicate truth surfaces, non-canonical, additive
     scaffolds, or temporary proof scaffolds
   - run `ablation_auditor` or root-equivalent packet when a deletion/collapse route
     could materially change implementation or closure
   - classify candidates as delete, collapse, canonicalize, privatize,
     decommission, validate-first, or keep-with-warrant
   - compute Ablation Opportunity Scores for non-trivial candidates
   - classify clone/collapse candidates before merging or reusing them
   - run an abstraction-ladder check before introducing or expanding an abstraction
   - require an Ablative Isomorphism Card for selected deletion/collapse routes

6. **Adversarial preflight**
   - run read-only challengers in the calibrated parallelism mode
   - challenge owner, route, proof, scope, surface budget, ablative route, and
     no-change cases
   - reject stale, wrong-scope, wrapper-leaking, acknowledgement-only, or
     no-evidence packets
   - block, reroute, or narrow on unresolved/vetoed material findings

7. **Route selection**
   - validate-first
   - accretive implementation
   - owner-level rewrite
   - delete/collapse/canonicalize/privatize/decommission
   - proof-only / no-change
   - blocked / needs decision

8. **Implementation pass**
   - delegate mutation to `accretive-implementer` when the selected rewrite is
     narrow and owned
   - root may perform root-equivalent edits only with an active `mutate-code` or
     `delete-collapse-canonicalize` warrant, current adversarial clearance,
     current ablative clearance, and passing Surface Budget Preflight
   - keep writes single-threaded
   - subagents may gather read-only evidence
   - emit Surface Delta Receipts and Ablation Ledger rows after material patch groups
   - emit Ablative Isomorphism Cards for any deletion, collapse, merge, reuse,
     canonicalization, privatization, or decommissioning performed

9. **De novo adversarial review**
   - use `adversarial-reviewer` or root-equivalent challenge
   - require candidate inventory, no-finding countercases, Soundness Ledger, and
     Change Agenda
   - record adversarial findings in the Adversarial Action Ledger

10. **One-change challenge**
    Ask:

    > If you could change one thing about this changeset, what would you change?

    Then ask the ablative variant:

    > If you could delete, collapse, privatize, decommission, or canonicalize one
    > thing in this changeset without weakening the live contract, and with behavior-preservation proof, what would it be?

    If either answer is impactful and in-scope, route it to `accretive-implementer`
    or root-equivalent single-writer implementation, then rerun de novo review. If
    structural and outside constraints, mark `needs-decision` or `blocked`. If no
    impactful remaining change exists, proceed to verification closure.

11. **Material fixed-point test**
    A candidate fixed point exists only when:
    - no open material findings remain
    - no unresolved material soundness rows remain
    - no unresolved adversarial vetoes remain
    - no unresolved ablation vetoes remain
    - no duplicate truth owner remains unretired
    - no additive scaffold remains without explicit justification
    - no dominated, subsumed, vestigial, uninhabited, pass-through, or
      non-canonical surface remains without a keep warrant
    - no selected deletion, collapse, reuse, or canonicalization lacks an Ablative
      Isomorphism Card or explicit validate-first blocker
    - no semantic clone or accidental rhyme was merged without equivalence proof
    - no review counterexample remains unresolved
    - surface budgets are satisfied or expansion is explicitly granted
    - proof receipts are tied to current artifact state

12. **Verification closure**
    Hand off to `verification-closure` with a closure packet.
    If closure reopens a gate, resume at route selection.

## Required ledgers

### Warrant Intake / Parallelism Plan

```md
| warrant id | claim id | permitted action | permitted scope | expiry check | surface budget | adversarial plan | ablation plan | parallelism mode | intake status |
|---|---|---|---|---|---|---|---|---|---|
```

Rules:

- `intake status` is `active`, `stale`, `blocked`, `consumed`, or `not-applicable`.
- Active `mutate-code` warrants must have surface budget and adversarial clearance.
- Active `delete-collapse-canonicalize` warrants must have ablation proof or a
  validate-first gate.
- Active `add-validation-only` warrants must forbid production mutation.
- Stale or blocked warrants may not be consumed for writes, validation, thread
  resolution, or replies.

### Truth Units

```md
| truth unit id | invariant | canonical owner | witnesses | duplicate/shadow owners | review/adversarial counterexamples | status | proof refs | next action |
|---|---|---|---|---|---|---|---|---|
```

### Ablation Ledger

```md
| id | surface | kind | current obligation | obligation status | canonical owner | replacement path | action | deletion/collapse proof | keep warrant | status |
|---|---|---|---|---|---|---|---|---|---|---|
```

Allowed `kind` values:

- `dominated`
- `subsumed`
- `vestigial`
- `uninhabited`
- `unreachable`
- `pass-through`
- `duplicate-truth-surface`
- `non-canonical`
- `additive-scaffold`
- `temporary-proof-scaffold`

Allowed `obligation status` values:

- `live`
- `expired`
- `moved`
- `duplicate`
- `unproven`
- `unknown`

Allowed `action` values:

- `delete`
- `collapse`
- `canonicalize`
- `privatize`
- `decommission`
- `validate-first`
- `keep-with-warrant`

### Ablation Opportunity Matrix

```md
| id | candidate | kind | surface removed | confidence | ownership clarity | risk | score | decision | proof needed |
|---|---|---|---:|---:|---:|---:|---:|---|---|
```

Use:

```text
Ablation Score = (Surface Removed × Confidence × Ownership Clarity) / Risk
```

Do not let LOC savings dominate semantic-surface reduction. A small deletion can
score high when it removes a duplicate truth surface, obsolete flag, public symbol,
state variant, or proof obligation.

### Ablative Isomorphism Cards

```md
| card id | surface | action | behavior preserved | public contract preserved | error semantics preserved | ordering/side effects preserved | clone classification | abstraction-ladder check | compatibility risk | proof signal | status |
|---|---|---|---|---|---|---|---|---|---|---|---|
```

Allowed `status` values: `pass`, `validate-first`, `missing`, `not-applicable`.

### Adversarial Action Ledger

```md
| action id | phase | target | challenger lanes | parallelism mode | strongest adversarial finding | veto status | clearance | proof ref | decision impact |
|---|---|---|---|---|---|---|---|---|---|
```

Allowed `veto status` values: `cleared`, `preserved-no-change`, `unresolved`,
`vetoed`, `blocked`, `not-required`.

Allowed `clearance` values: `cleared`, `preserved`, `rerouted`, `downgraded`,
`blocked`.

### Surface Delta Receipts

```md
| receipt id | warrant id | patch/pass | production insertions | production deletions | net production loc | public symbols added | helpers added | duplicate paths added | budget status | proof ref |
|---|---|---|---|---|---|---|---|---|---|---|
```

If budget status is `expansion-needed` or `violation`, stop implementation until
an Expansion Warrant Request is granted or the patch is redesigned.

## Closure handoff packet

Before invoking `verification-closure`, compile:

```yaml
closure_handoff_packet:
  artifact_state_id: "..."
  goal: "..."
  warrant_intake:
    - warrant_id: "..."
      claim_id: "..."
      permitted_action: "mutate-code | delete-collapse-canonicalize | add-validation-only | resolve-thread | draft-reply | defer | none"
      intake_status: "active | consumed | stale | blocked | not-applicable"
      adversarial_clearance: "cleared | preserved | rerouted | downgraded | blocked"
      ablative_clearance: "clear-additive | select-ablative-route | validate-first | veto-additive | unresolved | not-required"
  parallelism_plan:
    lane: "root-equivalent | targeted-parallel | expanded-targeted | swarm | not-required"
    reason: "..."
    read_only: yes
    write_owner: root-or-delegate
  truth_units:
    - id: "TU1"
      invariant: "..."
      canonical_owner: "..."
      witnesses: ["..."]
      duplicate_truth_surfaces_retired: ["..."]
      open_counterexamples: []
  review_agenda:
    act_on: []
    validate_first: []
    proof_only: []
    delete_collapse_canonicalize: []
    no_change: []
    blocked: []
  ablation_ledger:
    open_candidates: []
    closed_candidates: []
    keep_warrants: []
    unresolved_ablation_vetoes: []
  ablation_opportunity_matrix:
    top_candidates: []
    rejected_candidates: []
  ablation_isomorphism_cards:
    - card_id: "..."
      surface: "..."
      action: "delete | collapse | reuse | canonicalize | privatize | decommission"
      behavior_preserved: "..."
      public_contract_preserved: "yes | no | unknown"
      error_semantics_preserved: "yes | no | unknown | not-applicable"
      ordering_side_effects_preserved: "yes | no | unknown | not-applicable"
      proof_signal: "..."
      status: "pass | validate-first | missing | not-applicable"
  adversarial_action_ledger:
    open_vetoes: []
    cleared_vetoes: []
    accepted_risks: []
  soundness_ledger:
    open_rows: []
    closed_rows: []
  ablation_activation_packet:
    activation: "required | not-required | blocked"
    authority: "ablation_activation_sentinel | root-equivalent"
    evidence: "..."
    trigger_surfaces: []
    required_next_packet: "ablation_auditor | root-equivalent-ablation-receipt | none | blocked"
  surface_delta_receipts:
    - warrant_id: "..."
      budget_status: "within-budget | expansion-needed | violation | not-applicable"
      proof_ref: "..."
  proof_receipts:
    - command_or_check: "..."
      result: "..."
      artifact_state_match: yes | no
  one_change_challenge:
    answer: "..."
    ablative_answer: "..."
    routed: yes | no
    reason: "..."
  unresolved_adversarial_vetoes: []
  unresolved_ablation_vetoes: []
```

## Output contract

Use tail-weighted sections:

1. Goal / Artifact State
2. Warrant Intake / Parallelism Plan
3. Ablation Activation Receipt
4. Truth Units
5. Ablation Ledger
6. Ablative Isomorphism Cards
7. Route Selection
8. Work Performed / Routed
9. Adversarial Action Ledger
10. Review, Soundness, and Ablation Results
11. Surface Delta Receipts
12. Proof Receipts
13. Fixed-Point Test
14. Closure Handoff
15. Final State
16. Do Next

`Do Next` must be the final section.

## Fixed-Point Gate

Before closure handoff, emit a gate summary with these fields:

- `artifact_state_match`: `pass` / `fail`
- `warrant_intake`: `pass` / `fail`
- `parallelism_calibration`: `pass` / `fail`
- `adversarial_action_coverage`: `pass` / `fail`
- `ablation_activation_receipt`: `pass` / `fail` / `not-required`
- `ablation_coverage`: `pass` / `fail` / `not-applicable`
- `ablation_isomorphism`: `pass` / `fail` / `not-applicable`
- `open_truth_units`: `0` or named blockers
- `duplicate_truth_owners`: `0` or named blockers
- `open_review_counterexamples`: `0` or named blockers
- `unresolved_soundness_rows`: `0` or named blockers
- `unresolved_adversarial_vetoes`: `0` or named blockers
- `unresolved_ablation_rows`: `0` or named blockers
- `unresolved_isomorphism_cards`: `0` or named blockers
- `dominated_surfaces`: `0` or named blockers
- `unwarranted_keep_surfaces`: `0` or named blockers
- `unretired_additive_scaffolds`: `0` or named blockers
- `surface_budget_status`: `pass` / `fail` / `not-applicable`
- `proof_receipts_current`: `pass` / `fail`
- `one_change_challenge_status`: `pass` / `fail`
- `ablative_one_change_challenge_status`: `pass` / `fail`
- `verification_closure_ready`: `yes` / `no`

## Hard rules

- Do not mutate outside an active `mutate-code` or `delete-collapse-canonicalize`
  warrant.
- Do not turn `add-validation-only` into production mutation.
- Do not let parallel adversaries or ablation auditors write files, mutate
  fixtures, resolve threads, or draft final replies.
- Do not treat parallel agreement as proof; require current artifact evidence.
- Do not claim fixed point with unresolved material adversarial vetoes.
- Do not claim fixed point with missing, implicit, or unresolved ablation activation when any ablation trigger is present.
- Do not claim fixed point with unresolved material ablation vetoes.
- Do not claim fixed point with unresolved or missing Ablative Isomorphism Cards
  for selected deletion, collapse, reuse, or canonicalization routes.
- Do not preserve duplicate truth owners unless they are explicitly justified.
- Do not leave additive scaffolding unretired merely because it helped pass an
  intermediate review loop.
- Do not keep dominated, subsumed, vestigial, uninhabited, pass-through, or
  non-canonical surfaces without a keep warrant.
- Do not hand off closure with stale proof receipts.
- Do not broaden beyond the permitted scope, forbidden actions, and surface budget
  consumed from review adjudication.

## Resources

- [doctrine-alpha.md](references/doctrine-alpha.md)
- [tail-proof.md](references/tail-proof.md)
- [truth-owner-normal-form.md](references/truth-owner-normal-form.md)
- [one-change-challenge.md](references/one-change-challenge.md)
- [ablation-ledger.md](references/ablation-ledger.md)
- [isomorphic-ablation.md](references/isomorphic-ablation.md)
- [lane-and-specialist-budget.md](references/lane-and-specialist-budget.md)
- [common-ledgers.md](references/common-ledgers.md)
- [ablation-activation.md](references/ablation-activation.md)
