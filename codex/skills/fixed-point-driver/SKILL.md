---
name: fixed-point-driver
description: "Drive exhaustive build-review-improve-verify loops to Truth-Owner Normal Form: one canonical owner per material invariant, no duplicate truth surfaces, no unresolved review counterexamples, no unretired additive scaffolding, and proof-gated closure. Trigger when coding needs de novo re-litigation, PR review closure, repeated review/fix loops, invariant repair, proof-surface hardening, negative-evidence pruning, CAS/Codex review resolution, optional architecture fingerprint preflight, or when agents risk adding local patches instead of deleting/refactoring/canonicalizing. Do not use for trivial one-step tasks or when the user wants one narrow phase."
---

# Fixed-Point Driver

This skill coordinates implementation, review, adjudication, reduction, verification, and closure until the artifact set reaches **Truth-Owner Normal Form**.

## The single rule

Drive toward this state:

> Every material invariant has exactly one canonical owner, every witness points back to that owner, every review finding is either discharged or represented as a counterexample, every additive scaffold has been promoted/collapsed/deleted, and no duplicate truth surface remains merely because it helped satisfy an intermediate review loop.

A fixed point is not “review is clean.” A fixed point is a normal form of the code and proof system.

## Why this skill exists
Frontier coding agents are good at adding code and addressing review comments. They are weaker at noticing that the best fix is to delete a path, collapse duplicate owners, privatize a surface, or tighten the one boundary that should have owned the invariant from the start.

This skill converts review churn into an ownership-normalization problem.

## Doctrine alpha driver

This skill owns the conversion from doctrine-rich pressure into normal-form artifacts.

Use doctrine only when it changes the route:

- `fixed-point` creates a reopenable material fixed-point gate, not a long review loop by default.
- `invariant` creates or updates a Truth Unit and owner edge.
- `canonical` selects one owner/representation and retires, privatizes, or justifies shadow owners.
- `witness` creates proof receipts tied to current head/artifact state.
- `adversarial` / `de novo` creates candidate inventory and no-finding countercases.
- `unwitnessed guarantee` / `illegal inhabitant` creates Soundness Ledger rows.

### Overprocessing guard

Do not use this skill for simple bounded tasks where ordinary direct execution plus one focused check fully closes the state space. If the run stays active, the reason must be a material open truth unit, stale proof, unresolved counterexample, shadow owner, addition escrow, or route-changing architecture uncertainty.

### Local-validity trap breaker

When several findings are each locally valid, ask whether they are all counterexamples to the same truth unit. If yes, prefer one owner-level rewrite over multiple local patches.

## Companion skills

- `review-adjudication` decides which review comments matter, but this skill decides whether selected work preserves Truth-Owner Normal Form.
- `accretive-implementer` performs implementation/remediation when the selected rewrite is narrow and owned.
- `adversarial-reviewer` challenges the current artifact state and should report normal-form violations, not just bugs.
- `verification-closure` performs decisive proof and closure gating.
- `logophile` may sharpen PR-facing summaries, names, and doctrine stacks, but does not own operational policy.

## Entry conditions
Use this skill when any of these are true:
- review/fix loops are repeating
- a PR has multiple coupled comments
- review comments are locally valid but may share one governing invariant
- closure proof keeps becoming stale
- a local patch may be inferior to a delete/collapse/canonicalize move
- additive scaffolding remains after satisfying intermediate review pressure
- the user asks to drive a branch/changeset to closure or find all impactful issues

Do not use this skill for simple bounded tasks with an obvious check.

## Workflow

1. **Frame**
   - user goal
   - artifact state
   - current review/adjudication inputs
   - explicit non-goals
   - proof bar

2. **Truth Unit extraction**
   - material invariant / contract / semantic fact
   - canonical owner
   - witnesses
   - duplicate or shadow truth surfaces
   - counterexamples / review findings

3. **Adjudication intake**
   - consume `review-adjudication` output when present
   - do not redo adjudication unless stale or contradictory
   - promote coupled local comments into a Governing Invariant Candidate

4. **Route selection**
   - validate-first
   - accretive implementation
   - owner-level rewrite
   - delete/collapse/canonicalize
   - proof-only / no-change
   - blocked / needs decision

5. **Implementation pass**
   - delegate mutation to `accretive-implementer`
   - keep writes single-threaded
   - subagents may gather read-only evidence

6. **De novo adversarial review**
   - use `adversarial-reviewer`
   - require candidate inventory, no-finding countercases, Soundness Ledger, and Change Agenda

7. **One-change challenge**
   Ask:
   > If you could change one thing about this changeset, what would you change?

   If the answer is an impactful accretive improvement, route it to `accretive-implementer`, then rerun de novo review.

8. **Material fixed-point test**
   A candidate fixed point exists only when:
   - no open material findings remain
   - no unresolved material soundness rows remain
   - no duplicate truth owner remains unretired
   - no additive scaffold remains without explicit justification
   - no review counterexample remains unresolved
   - proof receipts are tied to current artifact state

9. **Verification closure**
   Hand off to `verification-closure` with a closure packet.
   If closure reopens a gate, resume at route selection.

## Closure handoff packet
Before invoking `verification-closure`, compile:

```yaml
closure_handoff_packet:
  artifact_state_id: "..."
  goal: "..."
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
  soundness_ledger:
    open_rows: []
    closed_rows: []
  proof_receipts:
    - command_or_check: "..."
      result: "..."
      artifact_state_match: yes | no
  one_change_challenge:
    answer: "..."
    routed: yes | no
    reason: "..."
```

## Output contract
Use tail-weighted sections:

1. Goal / Artifact State
2. Truth Units
3. Route Selection
4. Work Performed / Routed
5. Review and Soundness Results
6. Proof Receipts
7. Fixed-Point Test
8. Closure Handoff
9. Final State
10. Do Next

`Do Next` must be the final section.

## Resources
- [doctrine-alpha.md](references/doctrine-alpha.md)
- [tail-proof.md](references/tail-proof.md)
- [truth-owner-normal-form.md](references/truth-owner-normal-form.md)
- [one-change-challenge.md](references/one-change-challenge.md)
