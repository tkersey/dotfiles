---
name: fixed-point-driver
description: "Drive exhaustive build-review-improve-verify loops to Truth-Owner Normal Form: one canonical owner per material invariant, no duplicate truth surfaces, no unresolved review counterexamples, no unresolved adversarial vetoes, no unretired additive scaffolding, and proof-gated closure. Trigger when coding needs de novo re-litigation, PR review closure, repeated review/fix loops, invariant repair, proof-surface hardening, negative-evidence pruning, CAS/Codex review resolution, parallel adversarial action, optional architecture fingerprint preflight, or when agents risk adding local patches instead of deleting/refactoring/canonicalizing. Do not use for trivial one-step tasks or when the user wants one narrow phase."
---

# Fixed-Point Driver

This skill coordinates implementation, review, adjudication, reduction,
verification, parallel read-only adversarial challenge, and closure until the
artifact set reaches **Truth-Owner Normal Form**.

## The single rule

Drive toward this state:

> Every material invariant has exactly one canonical owner, every witness points
> back to that owner, every review finding is either discharged or represented as
> a counterexample, every adversarial veto is cleared, accepted as risk, or
> routed, every additive scaffold has been promoted/collapsed/deleted, and no
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

This skill converts review churn into an ownership-normalization problem and
converts adversarial pressure into time-efficient, read-only clearance packets.

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

### Overprocessing guard

Do not use this skill for simple bounded tasks where ordinary direct execution
plus one focused check fully closes the state space. If the run stays active, the
reason must be a material open truth unit, stale proof, unresolved counterexample,
unresolved adversarial veto, shadow owner, addition escrow, route-changing
architecture uncertainty, or active warrant that requires fixed-point handling.

### Local-validity trap breaker

When several findings are each locally valid, ask whether they are all
counterexamples to the same truth unit. If yes, prefer one owner-level rewrite
over multiple local patches.

## Parallel adversarial action

This skill is **parallel-adversarial by default** for material actions, but
single-writer for all mutation.

Every material action must have an adversarial response:

| phase/action | adversarial response |
|---|---|
| warrant intake | Is the warrant stale, expired, overbroad, or incompatible with current artifact state? |
| truth-unit extraction | Is the invariant split incorrectly? Is the canonical owner wrong? Are there shadow owners? |
| route selection | Is delete/reuse/refactor/no-change/validate-first better than mutation? |
| implementation | Does the patch exceed warrant scope or surface budget? Does it add duplicate truth surfaces? |
| validation | Does proof exercise the real failure mechanism and current artifact state? |
| de novo review | Are there unlisted counterexamples, illegal inhabitants, or unretired scaffolds? |
| one-change challenge | Is there one remaining impactful change before closure? |
| closure handoff | Are proof receipts current and all adversarial vetoes cleared or explicitly routed? |

Parallelism modes:

- `root-equivalent`: root performs the adversarial response inline for narrow,
  bounded, already-proof-bearing work.
- `targeted-parallel`: one or two independent read-only lanes challenge distinct
  uncertainty classes.
- `expanded-targeted`: three or four lanes for coupled truth units, stale proof,
  negative evidence, or surface-budget risk.
- `swarm`: five or more lanes for large, contentious, P2+, invariant-coupled, or
  likely-to-reopen runs.
- `not-required`: no safe action exists; block and name missing evidence.

Parallel adversaries may gather evidence, inspect surfaces, challenge proofs,
map hazards, and test invariants conceptually. They must not edit code, alter
fixtures, resolve threads, or draft final replies. The root coordinator integrates
packets and keeps writes single-threaded.

## Companion skills

- `review-adjudication` decides which review comments matter and issues warrants;
  this skill decides whether selected work preserves Truth-Owner Normal Form.
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
- a local patch may be inferior to a delete/collapse/canonicalize move
- additive scaffolding remains after satisfying intermediate review pressure
- a Resolution Warrant routes `address` or `validate-only` to `$fixed-point-driver`
- an Adversarial Action Matrix selects full-fanout, swarm, contentious,
  invariant-level, structural, validation-only, or likely-to-reopen work
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
   - preserve permitted action (`mutate-code` vs `add-validation-only`)
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
   - do not broaden beyond active warrants or cleared adversarial actions

5. **Adversarial preflight**
   - run read-only challengers in the calibrated parallelism mode
   - challenge owner, route, proof, scope, surface budget, and no-change cases
   - reject stale, wrong-scope, wrapper-leaking, acknowledgement-only, or
     no-evidence packets
   - block, reroute, or narrow on unresolved/vetoed material findings

6. **Route selection**
   - validate-first
   - accretive implementation
   - owner-level rewrite
   - delete/collapse/canonicalize
   - proof-only / no-change
   - blocked / needs decision

7. **Implementation pass**
   - delegate mutation to `accretive-implementer` when the selected rewrite is
     narrow and owned
   - root may perform root-equivalent edits only with an active `mutate-code`
     warrant, current adversarial clearance, and passing Surface Budget Preflight
   - keep writes single-threaded
   - subagents may gather read-only evidence
   - emit Surface Delta Receipts after material patch groups

8. **De novo adversarial review**
   - use `adversarial-reviewer` or root-equivalent challenge
   - require candidate inventory, no-finding countercases, Soundness Ledger, and
     Change Agenda
   - record adversarial findings in the Adversarial Action Ledger

9. **One-change challenge**
   Ask:

   > If you could change one thing about this changeset, what would you change?

   If the answer is an impactful accretive improvement, route it to
   `accretive-implementer`, then rerun de novo review. If it is structural and
   outside constraints, mark `needs-decision` or `blocked`. If no impactful
   remaining change exists, proceed to verification closure.

10. **Material fixed-point test**
    A candidate fixed point exists only when:
    - no open material findings remain
    - no unresolved material soundness rows remain
    - no unresolved adversarial vetoes remain
    - no duplicate truth owner remains unretired
    - no additive scaffold remains without explicit justification
    - no review counterexample remains unresolved
    - surface budgets are satisfied or expansion is explicitly granted
    - proof receipts are tied to current artifact state

11. **Verification closure**
    Hand off to `verification-closure` with a closure packet.
    If closure reopens a gate, resume at route selection.

## Required ledgers

### Warrant Intake / Parallelism Plan

```md
| warrant id | claim id | permitted action | permitted scope | expiry check | surface budget | adversarial plan | parallelism mode | intake status |
|---|---|---|---|---|---|---|---|---|
```

Rules:

- `intake status` is `active`, `stale`, `blocked`, `consumed`, or `not-applicable`.
- Active `mutate-code` warrants must have surface budget and adversarial clearance.
- Active `add-validation-only` warrants must forbid production mutation.
- Stale or blocked warrants may not be consumed for writes, validation, thread
  resolution, or replies.

### Truth Units

```md
| truth unit id | invariant | canonical owner | witnesses | duplicate/shadow owners | review/adversarial counterexamples | status | proof refs | next action |
|---|---|---|---|---|---|---|---|---|
```

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
      permitted_action: "mutate-code | add-validation-only | resolve-thread | draft-reply | defer | none"
      intake_status: "active | consumed | stale | blocked | not-applicable"
      adversarial_clearance: "cleared | preserved | rerouted | downgraded | blocked"
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
    no_change: []
    blocked: []
  adversarial_action_ledger:
    open_vetoes: []
    cleared_vetoes: []
    accepted_risks: []
  soundness_ledger:
    open_rows: []
    closed_rows: []
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
    routed: yes | no
    reason: "..."
  unresolved_adversarial_vetoes: []
```

## Output contract

Use tail-weighted sections:

1. Goal / Artifact State
2. Warrant Intake / Parallelism Plan
3. Truth Units
4. Route Selection
5. Work Performed / Routed
6. Adversarial Action Ledger
7. Review and Soundness Results
8. Surface Delta Receipts
9. Proof Receipts
10. Fixed-Point Test
11. Closure Handoff
12. Final State
13. Do Next

`Do Next` must be the final section.

## Fixed-Point Gate

Before closure handoff, emit a gate summary with these fields:

- `artifact_state_match`: `pass` / `fail`
- `warrant_intake`: `pass` / `fail`
- `parallelism_calibration`: `pass` / `fail`
- `adversarial_action_coverage`: `pass` / `fail`
- `open_truth_units`: `0` or named blockers
- `duplicate_truth_owners`: `0` or named blockers
- `open_review_counterexamples`: `0` or named blockers
- `unresolved_soundness_rows`: `0` or named blockers
- `unresolved_adversarial_vetoes`: `0` or named blockers
- `unretired_additive_scaffolds`: `0` or named blockers
- `surface_budget_status`: `pass` / `fail` / `not-applicable`
- `proof_receipts_current`: `pass` / `fail`
- `one_change_challenge_status`: `pass` / `fail`
- `verification_closure_ready`: `yes` / `no`

## Hard rules

- Do not mutate outside an active `mutate-code` warrant.
- Do not turn `add-validation-only` into production mutation.
- Do not let parallel adversaries write files, mutate fixtures, resolve threads,
  or draft final replies.
- Do not treat parallel agreement as proof; require current artifact evidence.
- Do not claim fixed point with unresolved material adversarial vetoes.
- Do not preserve duplicate truth owners unless they are explicitly justified.
- Do not leave additive scaffolding unretired merely because it helped pass an
  intermediate review loop.
- Do not hand off closure with stale proof receipts.
- Do not broaden beyond the permitted scope, forbidden actions, and surface budget
  consumed from review adjudication.

## Resources

- [doctrine-alpha.md](references/doctrine-alpha.md)
- [tail-proof.md](references/tail-proof.md)
- [truth-owner-normal-form.md](references/truth-owner-normal-form.md)
- [one-change-challenge.md](references/one-change-challenge.md)
- [common-ledgers.md](references/common-ledgers.md)
- [companion-skill-ledger.md](references/companion-skill-ledger.md)
- [closure-handoff-template.md](references/closure-handoff-template.md)
- [adversarial-parallelism.md](references/adversarial-parallelism.md)
