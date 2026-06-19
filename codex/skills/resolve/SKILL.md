---
name: resolve
description: "Resolve review findings through C³, the Counterexample Compression Compiler. Reviews may add only verified counterexamples; candidate implementations are disposable; delivery receives one lexicographically minimal, ablated patch regenerated from an immutable base and authorized by MRPC-v1. Use for `$resolve`, branch review/fix/prove/push/PR-sweep closure, repeated CAS findings, review-induced code growth, candidate tournaments, semantic-cost minimization, counterexample compression, or minimal patch certification. Not for one-shot review, PR creation, merge/land, or an isolated implementation task."
metadata:
  version: "5.0.0"
  activation_cost: high
  default_depth: full
---

# Resolve

## Mission

`$resolve` is the **C³ Counterexample Compression Compiler**.

```text
The specification grows.
Candidates die.
Only the smallest proven patch survives.
```

The monotone object is the counterexample basis:

```text
C₀ ⊆ C₁ ⊆ C₂ ...
```

Candidate code is disposable:

```text
Pᵢ = compile(immutable_base, Cᵢ)

new branch-liable counterexample c
-> invalidate Pᵢ
-> add c to Cᵢ
-> regenerate from immutable_base
```

Never incrementally patch a candidate after a new branch-liable review finding.

## The causal break

The forbidden edge is:

```text
review finding -> direct delivery mutation
```

The required path is:

```text
review finding
-> verified counterexample
-> liability decision
-> compressed counterexample family
-> independent repair candidates
-> common verification
-> lexicographic semantic-cost selection
-> edit-atom ablation
-> independent holdout
-> exact application to delivery
-> current proof
-> commit/push/PR closure
```

## Canonical durable controller

Use:

```bash
python3 codex/skills/resolve/tools/review_compile.py ...
```

Canonical repo-local state:

```text
.resolve-c3/
  state.json
  events.jsonl
  candidates/
  mrpc.json
```

`.resolve-c3/` is local-excluded by default.

`MRPC-v1` is the one canonical workflow artifact. It evolves through:

```text
collecting
selected
apply-certified
applied
final-certified
committed
pushed
closed
```

Do not manually author MRPC. The controller emits it.

## Activation boundary

Use `$resolve` when the user wants current-branch review resolution through proof, push, and PR sweep.

Do not use for:

- review only;
- PR creation: `$ship`;
- merge and cleanup: `$land`;
- selected implementation only: `$fixed-point-driver` or `$accretive-implementer`;
- claim adjudication only: `$review-adjudication`;
- final proof only: `$verification-closure`.

## Entry modes

### Clean review

When the initial current-head review is clean, no compiler run is required. Complete current proof and PR sweep.

### Isolated finding waiver

One narrow finding may use a one-candidate tournament only when all are true:

```text
exactly one branch-liable finding
no recurrence
no helper/wrapper/new state dimension
no public or compatibility surface
no new proof family
zero or negative production net, or a trivial bounded edit
```

Even this route uses MRPC. Record a tournament waiver:

```bash
review_compile.py tournament-waiver --reason "..."
```

### Material review

Any of these require the full tournament:

```text
two or more branch-liable findings
same-cluster or same-family recurrence
new helper/wrapper/state dimension
positive production surface
public/compatibility/fallback surface
PR thread reopening
uncertain liability
a candidate route previously failed
```

## Phase 1: immutable base

After the first branch-liable finding, initialize C³ before any review-derived delivery edit:

```bash
python3 codex/skills/resolve/tools/review_compile.py begin \
  --root . \
  --acceptance .resolve-c3/acceptance.json \
  --lab ../<repo>-resolve-lab
```

`begin` requires a clean delivery worktree and records:

```text
delivery root
branch
immutable base SHA
acceptance contract
lab worktree
run id
```

Once active, delivery is frozen. The configured PreToolUse hook blocks direct delivery edits, raw commit/amend, and raw push.

The lab may mutate. Delivery may not.

## Phase 2: review claims become counterexamples

Use `$review-adjudication` and evidence discipline.

A review claim contributes only:

```yaml
counterexample:
  id:
  observed_behavior:
  required_behavior:
  liability:
    introduced_by_current_diff |
    exposed_and_required_by_current_acceptance |
    preexisting_but_blocks_current_invariant |
    adjacent_preexisting |
    reviewer_preference |
    unknown
  reproduction_or_proof:
  suspected_owner:
  source_refs: []
```

Only the first three liability classes enter the branch-liable basis.

A valid adjacent defect is captured as a follow-up, not absorbed into delivery scope.

Register findings:

```bash
review_compile.py add-counterexample --input counterexample.json
```

## Phase 3: compress to a basis

Use `$review-compression-compiler`.

Raw findings are often several witnesses for one missing rule. Compile them into the smallest independent basis that still distinguishes incorrect implementations.

```yaml
counterexample_basis:
  basis_version: CEB-v1
  branch_liabilities: []
  non_branch_liabilities: []
  families:
    - family_id:
      governing_rule:
      independent_witnesses: []
      subsumed_findings: []
      canonical_owner_candidates: []
      proof_obligations: []
  original_acceptance: []
  gate:
    all_findings_classified: pass | fail
    every_branch_liability_covered: pass | fail
    non_branch_liabilities_excluded: pass | fail
```

Store it:

```bash
review_compile.py set-basis --input basis.json
```

No candidate selection without a passing basis.

## Phase 4: candidate tournament

Generate deliberately different route families from the same immutable base and complete basis.

Default tournament:

```text
no-change or proof-only control
subtractive/delete-collapse-canonicalize
existing-owner normalization
representation repair
boundary/protocol redesign
local-guard baseline
```

Do not generate all six mechanically. Generate at least three candidate records, at least two distinct route classes, and include a no-change or local-baseline control unless a tournament waiver explains why impossible.

Candidate construction belongs in disposable worktrees or scratch trees.

Create additional candidate worktrees through the controller:

```bash
review_compile.py candidate-worktree   --candidate-id cand-subtractive   --path ../<repo>-cand-subtractive
```

Recommended specialists:

```text
$reduce                    subtractive candidate
$accretive-implementer     existing-owner/local baseline candidate
$universalist              representation/boundary candidate
$fixed-point-driver        candidate verification and normal-form challenge
```

Register each candidate:

```bash
review_compile.py register-candidate \
  --input candidate.json \
  --worktree /path/to/candidate-worktree
```

Candidate hard constraints:

```text
all branch-liable counterexamples pass
original acceptance passes
regressions pass
proof is current to candidate patch
active negative-route exclusions are not reused
forbidden scope is absent
```

Invalid candidates remain in the tournament as defeated routes.

## Phase 5: semantic-cost dominance

Select by lexicographic semantic cost, not persuasive prose and not one weighted score.

Canonical cost order:

```yaml
semantic_cost:
  new_truth_owners:
  new_public_symbols:
  new_state_variants:
  new_fallback_or_compatibility_paths:
  new_protocol_cases:
  new_control_flow_branches:
  new_helpers_or_wrappers:
  new_proof_obligations:
  retained_retirable_surfaces:
  owners_modified:
  files_modified:
  ast_edit_count:
  production_net_lines:
  test_net_lines:
```

Lower is better in the order shown.

Selection means:

```text
minimum among generated valid candidates
```

Never claim global program optimality.

Run:

```bash
review_compile.py select
```

The tournament record must show every candidate, validity, negative-route state, cost vector, and rejection reason.

## Phase 6: delta-ablate the winner

Before delivery application, attack every edit atom in the selected candidate:

```text
hunk
helper
branch
predicate
state field
fallback
compatibility case
wrapper
public symbol
test
file
```

Try delete/collapse/merge/privatize/table-drive/remove.

For every survivor, record the counterexample or acceptance obligation that fails when removed.

```yaml
ablation:
  ablation_version: ABL-v2
  candidate_id:
  edit_atoms:
    - edit_id:
      kind:
      result: removed | survived
      obligations: []
      failure_witness:
      proof_ref:
  removed: []
  survived: []
  orphan_edit_atoms: []
  one_minimal: yes | no
```

Run ablation through the controller:

```bash
review_compile.py ablate \
  --candidate-id cand-existing-owner \
  --input ablation-plan.json
```

Each edit atom supplies a lab-only `remove_command`; a surviving atom also supplies a `restore_command`. The controller removes the atom, runs the common counterexample/acceptance/regression set, and restores it only when removal produces a failure witness.

`record-ablation` remains an external-import compatibility surface but cannot authorize `certify-apply`.

Target:

```text
orphan_edit_atoms = 0
```

## Phase 7: independent candidate holdout

Run one broad adversarial holdout against the ablated candidate.

Classify every result:

```text
new branch-liable counterexample
subsumed witness
adjacent preexisting follow-up
reviewer preference
clean
```

Record:

```bash
review_compile.py record-holdout \
  --stage candidate \
  --input candidate-holdout.json
```

A new branch-liable counterexample invalidates the selected candidate. Add it to the basis and regenerate from the immutable base.

Do not patch the selected candidate.

## Phase 8: apply certificate

When basis, tournament, ablation, and candidate holdout pass:

```bash
review_compile.py certify-apply
```

This emits MRPC with:

```yaml
gate:
  apply_allowed: yes
  commit_allowed: no
  push_allowed: no
```

Only the controller may apply the patch:

```bash
review_compile.py apply
```

The controller verifies the delivery head and worktree, applies the exact selected patch, and checks its fingerprint.

No cherry-pick of exploratory commits by default.

## Phase 9: current delivery proof and holdout

Run current delivery proof through the controller:

```bash
review_compile.py run-proof --input proof-plan.json
```

`record-proof` remains a compatibility/import surface but cannot authorize final certification; final MRPC requires controller-run proof.

Run final current-head holdout and PR sweep:

```bash
review_compile.py record-holdout \
  --stage delivery \
  --input delivery-holdout.json
```

If a new branch-liable counterexample appears:

```text
certificate invalid
candidate dead
delivery patch reversed with reset-delivery
counterexample added
tournament rerun from immutable base
```

Adjacent findings become follow-ups.

## Phase 10: final certificate, commit, push, closure

```bash
review_compile.py certify-final
review_compile.py commit --message "..."
review_compile.py push --remote origin
review_compile.py close --input pr-sweep.json
review_compile.py cleanup-labs --confirm
```

Raw `git commit`, `git commit --amend`, and `git push` are blocked while C³ is active.

If the post-push PR sweep reveals a new branch-liable counterexample, do not amend the pushed commit. Abort the current run as reopened, then begin a new C³ run from the pushed head:

```bash
review_compile.py abort --confirm --reason "post-push PR sweep reopened"
review_compile.py begin --root . --acceptance /path/to/acceptance.json --lab ../<repo>-resolve-lab-next
```

The controller archives the prior terminal run under `.resolve-c3/archive/`.

## MRPC-v1

The canonical certificate contains:

```yaml
minimal_review_patch_certificate:
  certificate_version: MRPC-v1
  stage:
  immutable_base:
  acceptance_contract:
  counterexample_basis:
  candidate_tournament:
  selected_candidate:
  negative_routes:
  ablation:
  obligation_to_edit_map:
  proof:
  holdout:
  delivery:
  metrics:
  gate:
    apply_allowed:
    commit_allowed:
    push_allowed:
    closure_allowed:
```

The file is:

```text
.resolve-c3/mrpc.json
```

A transcript summary may render the same fields. The durable JSON is authoritative.

## Negative-ledger rule

Every falsified route family is captured through `$negative-ledger`.

A tournament candidate must include:

```yaml
negative_route:
  status: allowed | active_exclusion | reopened | stale | superseded | unknown
  refs: []
```

An active excluded route is invalid.

Cluster equality alone is not an exclusion.

## Candidate-worker boundary

Raw review findings may not be handed to implementation skills.

A candidate handoff contains:

```yaml
candidate_handoff:
  run_id:
  immutable_base:
  candidate_id:
  route_class:
  counterexample_basis:
  forbidden_scope: []
  semantic_cost_budget:
  negative_route_refs: []
  worktree:
```

Workers return a candidate patch and evidence. They do not edit delivery.

## Holdout boundary

The final broad review is not a work queue.

It may:

```text
invalidate candidate with a new branch-liable counterexample
add another witness to an existing family
capture adjacent follow-up
reject preference
pass
```

It may not directly authorize a delivery patch.

## Reporting

Final `$resolve` output includes the MRPC id and:

```yaml
resolve_c3_report:
  run_id:
  immutable_base:
  raw_findings:
  independent_families:
  candidates_evaluated:
  candidates_discarded:
  selected_route:
  semantic_cost:
  edit_atoms_before_ablation:
  edit_atoms_removed:
  edit_atoms_survived:
  orphan_edit_atoms:
  lab_surface_discarded:
  delivery_production_net:
  delivery_test_net:
  followups_captured:
  holdout_recompilations:
  commit:
  push:
  pr_sweep:
  outcome:
```

The core metric is:

```text
independent branch-liable counterexamples discharged
-----------------------------------------------------
semantic surface cost of delivery patch
```

## Fast failure rules

Stop when:

- delivery is dirty at `begin`;
- basis is incomplete;
- fewer than required candidates exist without waiver;
- all candidates fail hard constraints;
- selected candidate reuses an active excluded route;
- ablation has an orphan edit atom;
- candidate holdout adds a branch-liable counterexample;
- delivery patch fingerprint differs from selected candidate;
- current proof fails;
- final holdout adds a branch-liable counterexample;
- MRPC is stale;
- raw delivery mutation bypasses the controller.

## Hook behavior

The drop-in extends the existing configured `$st` SessionStart, PreToolUse, and Stop hooks.

When `.resolve-c3/state.json` is active:

- SessionStart injects current C³ phase and required next action.
- PreToolUse blocks direct delivery mutation and raw commit/push.
- Stop blocks a resolved/done claim until the run is closed or explicitly aborted.

The lab remains writable.

## Hard rules

- Reviews append constraints, not patches.
- Candidate implementations are disposable.
- No branch-liable finding bypasses the basis.
- No single-candidate default for material review.
- No active negative route in the tournament winner.
- No direct delivery edit after C³ begins.
- No incremental patching after a new counterexample.
- No survivor without a failure witness.
- No orphan edit atoms.
- No holdout finding automatically expands scope.
- No global-optimality claim beyond generated candidates.
- No commit/push outside the controller while active.
- No resolved claim without final MRPC-v1.

## Resources

- [c3-model.md](references/c3-model.md)
- [counterexample-basis.md](references/counterexample-basis.md)
- [candidate-tournament.md](references/candidate-tournament.md)
- [semantic-cost.md](references/semantic-cost.md)
- [ablation-minimality.md](references/ablation-minimality.md)
- [holdout-policy.md](references/holdout-policy.md)
- [mrpc-schema.md](references/mrpc-schema.md)
- [controller.md](references/controller.md)
