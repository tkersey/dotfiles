---
name: resolve
description: "Intent-closed counterexample-guided review synthesis with fail-closed authority gates. Use for `$resolve`, material branch review/fix/prove/push/closure, repeated CAS/PR findings, review-driven growth, semantic-surface conservation, MBK/RC realization, or deciding exactly which review observations may change code. Raw review text is never executable: mutation requires RAC-v1 from claim to AC/CEX/RB/CEB/MBK/RC/proof/realization, and closure requires terminal closure-gate proof. Not for one-shot review, PR creation, merge/land, or isolated implementation."
metadata:
  version: "9.0.0"
  activation_cost: high
  default_depth: full
---
# Resolve
## Mission
`$resolve` is the **Intent-Closed Counterexample Synthesis Compiler**.
```text
source intent
-> sealed observation language
-> bounded falsification batches
-> minimal distinguishing counterexamples
-> counterexample quotient
-> minimum behavioral kernel
-> one realization
-> conformance falsification
-> terminal holdout
-> delivery closure
```
The unit of review is a minimal distinguishing experiment. The unit of
resolution is a counterexample equivalence class. The unit of implementation is
a kernel transition.
## Governing invariant
```text
Raw review text is not mutation authority.
```
A review-originated edit is legal only when the active finding has a current
`resolve_authority_chain / RAC-v1` from review claim to AC law, CEX disposition,
sealed batch, CEB class, MBK/RC transition, proof obligation, and realization
target.
If the chain is incomplete, the only legal actions are:
```text
adjudicate the claim
seal or repair the batch
compile or repair CEB/MBK/RC
rebase AC
create a follow-up
reject the finding
block
```
Patch, commit, push, and closure language are forbidden until the relevant gate
passes.
## Governing problem
Repeated whole-diff review creates a positive feedback loop:
```text
larger diff -> broader review search -> more valid adjacent findings
-> more local patches -> larger review search
```
A finding may be real, branch-liable, and diff-local while still being outside
the intended change. Therefore:
```text
diff relevance is not mutation authority
validity is not intent entailment
additional witness is not a new code distinction
useful review prose is not executable input
```
## Protocol profile
```text
intent-closed-cegis-v2
```
Primary artifacts:
```text
AC-v2    sealed acceptance contract and observation language
RB-v1    bounded review batch
RAP-v1   targeted review aperture
CEX-v1   minimal distinguishing counterexample
CEB-v2   sealed, quotiented counterexample basis
MBK-v1   minimum behavioral kernel, intent-bound
RC-v1    reduction certificate
RAC-v1   review authority chain from claim to realization authority
PHI-v1   controller-derived review potential
MBKC-v1  campaign certificate and delivery gate
```
## Controller requirement
Canonical controller:
```bash
resolve-c3
```
Before material work:
```bash
python3 codex/skills/resolve/tools/controller_preflight.py
```
Required capability profile:
```text
acceptance_contract_v2
sealed_review_horizon_v1
review_batch_v1
review_aperture_v1
counterexample_v1
counterexample_basis_v2
minimum_behavioral_kernel_v1
reduction_certificate_v1
resolve_authority_chain_v1
mutation_gate_v1
closure_gate_v1
review_potential_v1
intent_closed_conformance_v1
terminal_holdout_v1
physical_apply
physical_commit
physical_push
closure_horizon_v1
```
If unavailable:
```text
analysis, adjudication, AC/CEX/CEB/MBK/RC/RAC drafting allowed
delivery mutation, commit, push, and closure forbidden
```
Reference compatibility tools:
```bash
python3 codex/skills/resolve/tools/resolve_authority_chain_gate.py rac.yaml
python3 codex/skills/resolve/tools/resolve_mutation_gate.py --chain rac.yaml
python3 codex/skills/resolve/tools/resolve_closure_gate.py --summary summary.json --runs runs.jsonl
```
## RAC-v1
`RAC-v1` is the smallest authority object that proves a review finding has been
compiled into legal mutation or legal non-mutation.
A mutation-authorizing RAC requires:
```text
chain_version = RAC-v1
current artifact state
review claim ID
AC contract, horizon, and law refs
in-horizon acceptance relation
confirmed CEX with minimal trace
sealed RB-v1
CEB class
MBK/RC transition
proof obligation
realization.allowed = true
gate.current_artifact_state = yes
gate.complete_chain = yes
gate.mutation_allowed = yes
```
A legal non-mutation RAC may authorize follow-up, proof-only update, AC rebase,
rejection, or block; it cannot authorize code mutation.
Full schema and native CLI spec: `references/cli-specs/01-rac-v1-and-authority-chain.md`.
## Mutation gate
Before any review-originated mutation, require:
```bash
python3 codex/skills/resolve/tools/resolve_mutation_gate.py --chain rac.yaml
```
Native target:
```bash
resolve-c3 mutation-gate --chain rac.yaml --format json
```
Fail closed on:
```text
uncompiled_review_text
missing_acceptance_contract
missing_or_stale_horizon
missing_or_invalid_cex
unsealed_review_batch
missing_ceb_class
missing_mbk_or_rc
missing_proof_obligation
artifact_state_stale
outside_horizon
rejected_or_refuted_claim
blocked_or_unknown_intent
```
When blocked, do not patch around the gate. Legal next actions are adjudication,
sealing, compression, AC rebase, follow-up creation, rejection, or block.
Full spec: `references/cli-specs/02-mutation-gate.md`.
## Closure gate
Before completion language, delivery closure, commit/push closure, or PR-thread
closure, require:
```bash
python3 codex/skills/resolve/tools/resolve_closure_gate.py \
  --summary /tmp/seq-resolve-summary.json \
  --runs /tmp/seq-resolve-runs.jsonl
```
Native target:
```bash
resolve-c3 closure-gate --summary SUMMARY --runs RUNS --format json
```
A material run is not closed when any are true:
```text
c3_required=true and c3_closed=false
compression_state=NONE
batches_total=0 for a finding-bearing workflow
delivery_closed=true while terminal_closed=false
potential.strict_progress=0 for a material campaign
orphan_code_constructs > 0
unmapped_proof_actions > 0
wound_specific_tests > 0 unless class-mapped
semantic_surface_delta > 0 without explicit AC rebase
```
A healthy material closure row has:
```text
c3_required=true
c3_entered=true
c3_closed=true
compression_state != NONE
batches_total > 0
kernel.accepted=true
potential.strict_progress > 0
delivery_closed=true
terminal_closed=true
orphan_code_constructs=0
unmapped_proof_actions=0
semantic_surface_delta <= 0 unless AC rebased
```
Full spec: `references/cli-specs/03-closure-gate.md`.
## Core laws
### 1. No review-to-code edge
```text
review claim
-> CEX-v1 adjudication
-> sealed batch
-> CEB/MBK/RC
-> RAC-v1
-> selected design
-> realization
```
Never:
```text
review claim -> patch
```
### 2. Intent closes before synthesis
AC-v2 defines:
```text
MUST       required behavior and compatibility obligations
MUST NOT   forbidden states/transitions
MAY        permitted but not mutation-justifying behavior
OUTSIDE    behavior not authorized in this campaign
```
After sealing, the observation language cannot expand without an explicit AC
rebase. `RAC-v1` must cite the active AC/horizon before mutation.
### 3. Review batches are mutation barriers
While any discovery, conformance, or holdout batch is open:
```text
delivery mutation = forbidden
```
Batch all planned apertures, classify every result, quotient duplicates, build
or update RAC-v1, then mutate once.
### 4. No counterexample without a minimal trace
Every actionable CEX identifies accepted law/obligation, minimal trace or
witness, expected observation, actual observation, and current artifact state.
Generic suspicion is not a counterexample.
### 5. No new implementation distinction for another witness
```text
new class                   -> kernel may refine
new witness, existing class -> proof may strengthen
duplicate                   -> no semantic action
outside horizon             -> follow-up or AC rebase
```
An additional witness cannot create another branch/helper/state/test family.
### 6. Implementation review is conformance review
After kernel acceptance, allowed review outputs are:
```text
existing-law nonconformance
missing law proof
orphan realization construct
stale artifact state
novel in-horizon CEX
outside-horizon proposal
clean
```
Generic feature discovery cannot directly authorize mutation.
### 7. Same-class recurrence invalidates realization
```text
same accepted class recurs after realization
-> candidate failed
-> invalidate realization
-> no local append patch
```
A novel in-horizon class returns to kernel synthesis. An outside-horizon class
returns to AC authority or follow-up.
### 8. Review potential must decrease
Each realized cycle emits PHI-v1:
```text
U = unclassified in-horizon counterexamples
L = unsatisfied accepted laws
C = open counterexample classes
O = orphan realization constructs
S = hard semantic-surface vector
P = unmapped/missing proof debt
```
Require:
```text
(U,L,C,O)_after <lex (U,L,C,O)_before
S_after componentwise <= S_before unless AC is explicitly rebased
P_after <= P_before
strict_progress = yes
```
Local comment silence is not progress.
### 9. One campaign-wide kernel
All batches refine one kernel rooted at `campaign_base_sha`. A prior tuple-local
closure head is not a new compiler base.
### 10. No orphan code or proof
Every surviving construct maps to accepted law, counterexample class, canonical
owner, and proof obligation.
Targets:
```text
orphan_code_constructs = 0
wound_specific_test_families = 0 unless class-mapped witness fixtures
unmapped_proof_actions = 0
```
### 11. No quotient without congruence
Every accepted operation, transition, and observation respects the quotient.
Unknown congruence blocks realization.
### 12. No normal form without recomposition
Every accepted law and required observation recomposes from retained factors
after quotienting and ablation.
## Lifecycle
### DISCOVER
- Bind campaign/base/baseline/current head/PR/proof.
- Compile AC-v2 from plan, PR intent, compatibility, non-goals, and proof bar.
- Run one broad discovery batch.
- Mutation forbidden.
### SEAL
- Adjudicate every claim as CEX-v1 or rejection.
- Seal AC-v2 and the discovery RB-v1.
- Quotient accepted CEX into CEB-v2.
- Unknown intent relation blocks.
### SYNTHESIZE
- Compile MBK-v1 and RC-v1 from AC-v2 + CEB-v2.
- Review the kernel/certificate, not prospective patches.
- Plan targeted review apertures.
- Select one realization design.
- Predict a non-worsening semantic surface.
### AUTHORIZE
- Emit RAC-v1 for each review-originated realization target or legal non-mutation.
- Validate RAC-v1.
- Run the mutation gate before implementation.
- If blocked, return to adjudication, sealing, compression, AC rebase, follow-up, or rejection.
### REALIZE
- Create a campaign-base-pinned realization worktree.
- Hand one accepted kernel/design/RAC to `$fixed-point-driver`.
- Capture/map/measure/verify the whole realization.
- No raw finding may enter the implementer.
### CONFORM
- Open a conformance RB-v1 against explicit RAP-v1 apertures.
- Reviewers attempt to falsify named laws at named owners/transitions.
- Seal the batch before any new mutation.
- Existing-class recurrence invalidates realization.
- Novel class returns to kernel.
- Outside horizon routes to follow-up or AC rebase.
### HOLDOUT
- After targeted conformance is clean, run one broad terminal holdout.
- Holdout has no direct mutation authority.
- In-horizon novelty returns to kernel.
- Contract-invalidating evidence returns to AC.
- Outside-horizon findings are deferred or explicitly rebased.
### CLOSE
Require current AC/horizon, no open review batch, no unclassified in-horizon CEX,
current CEB/MBK/RC, current RAC-v1 chains for every review-originated mutation,
no novel conformance/holdout CEX, terminal strict PHI, all laws proved, all
constructs/proof mapped, conserved or explicitly rebased semantic surface,
current-head proof, PR thread sweep, commit/push currency, and passing closure
gate.
## Entry modes
### Clean current-head review
If no finding-bearing campaign exists:
```text
current proof
thread sweep
tuple-bound closure
```
Do not manufacture AC/MBK/RAC machinery.
### Isolated conformance correction
Allowed only when exactly one confirmed branch-liable existing-law violation has
current AC/kernel, a passing RAC-v1 mutation gate, no new semantic distinction,
nonincreasing semantic surface, proof extending an existing law family, and one
sealed conformance batch. Still emit compact CEX/MBKC/PHI/RAC evidence.
### Material review
Use full lifecycle when any apply:
```text
two or more branch-liable findings
same-family recurrence
new semantic distinction
positive hard-surface pressure
public/compatibility/fallback pressure
thread reopening
finding proposes new behavior
whole-diff review discovers adjacent scope
```
## Workflow
1. Preflight controller and gate capabilities.
2. Bind campaign tuple.
3. Compile and validate AC-v2.
4. Open/run/seal discovery RB-v1.
5. Use `$review-adjudication` to produce CEX-v1 or rejection.
6. Use `$review-compression-compiler` to produce CEB-v2 + MBK-v1 + RC-v1.
7. Audit quotient, recomposition, proof basis, and initial PHI.
8. Emit and validate RAC-v1 for each legal realization target.
9. Run mutation gate before any review-originated patch.
10. Select one design and create realization worktree.
11. Use `$fixed-point-driver` for one bounded realization.
12. Capture/map/measure/verify realization.
13. Run/seal targeted conformance batches.
14. Invalidate/return rather than append-patch on new evidence.
15. Certify strict PHI progress.
16. Run/seal one terminal holdout.
17. Run closure gate.
18. Apply/commit/push through controller only after closure gate permits.
19. Close only against current AC/kernel/batches/RAC/PHI/proof/PR tuple.
## CLI spec ordering
Implement specs in this order:
1. `references/cli-specs/01-rac-v1-and-authority-chain.md`
2. `references/cli-specs/02-mutation-gate.md`
3. `references/cli-specs/03-closure-gate.md`
4. `references/cli-specs/04-seq-projection.md`
The mutation gate consumes RAC-v1. The closure gate consumes controller and seq
projection fields, including RAC/mutation-gate outcomes. The seq projection spec
comes last because it reports the first three surfaces.
## Validation
```bash
python3 codex/skills/resolve/tools/acceptance_contract_gate.py acceptance.json
python3 codex/skills/review-adjudication/tools/counterexample_gate.py cex.json
python3 codex/skills/resolve/tools/review_batch_gate.py batch.json
python3 codex/skills/review-compression-compiler/tools/counterexample_basis_gate.py basis.json
python3 codex/skills/resolve/tools/kernel_lint.py kernel.json
python3 codex/skills/resolve/tools/resolve_authority_chain_gate.py rac.yaml
python3 codex/skills/resolve/tools/resolve_mutation_gate.py --chain rac.yaml
python3 codex/skills/resolve/tools/review_potential_gate.py potential.json
python3 codex/skills/resolve/tools/resolve_closure_gate.py --summary summary.json --runs runs.jsonl
python3 codex/skills/resolve/tools/mbkc_gate.py mbkc.json --terminal
```
## Final report
```text
Resolve:
- Campaign / tuple:
- AC / horizon:
- Review batches:
- CEX classes:
- CEB / MBK / RC:
- RAC-v1 chains:
- Mutation gate:
- Realization:
- Conformance:
- Holdout:
- PHI:
- Semantic surface:
- Closure gate:
- Commit / push / PR sweep:
- Remaining uncertainty:
```
Do not use completion, closed, resolved, landed, or ready language when the
closure gate blocks.
## Hard rules
- Raw review text is not executable.
- No review-originated mutation without current RAC-v1 and passing mutation gate.
- No review claim may reach an implementer as raw prose.
- No completion language without passing closure gate.
- Valid does not mean branch-liable.
- Branch-liable does not mean intent-entailed.
- Diff-local does not mean in-horizon.
- Additional witness does not create a code distinction.
- No mutation while a discovery, conformance, or holdout batch is open.
- No quotient without congruence.
- No normal form without recomposition.
- No orphan code, wound-specific proof surface, or unmapped proof action at closure.
- Strict PHI progress is required for material campaigns.
- Semantic surface must not grow unless AC is explicitly rebased.
- Controller receipts and gates outrank summary prose.
