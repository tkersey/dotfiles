---
name: resolve
description: "Intent-closed counterexample-guided review synthesis. Use for `$resolve`, material branch review/fix/prove/push/closure, repeated CAS/PR findings, review-driven growth, MBK/RC realization, semantic-surface conservation, or determining exactly which review observations may change code. Seal AC-v2, run bounded review batches, admit only minimal in-horizon CEX-v1 counterexamples, quotient them into one campaign kernel, realize one design, require strict review-potential progress, then close through targeted conformance and one terminal broad holdout. Not for one-shot review, PR creation, merge/land, or isolated implementation."
metadata:
  version: "8.0.0"
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

The unit of review is a minimal distinguishing experiment.

The unit of resolution is a counterexample equivalence class.

The unit of implementation is a kernel transition.

## Governing problem

Repeated whole-diff review creates a positive feedback loop:

```text
larger diff
-> broader review search
-> more valid adjacent findings
-> more local patches
-> larger review search
```

A finding may be real, branch-liable, and diff-local while still being outside the intended change.

Therefore:

```text
diff relevance is not mutation authority
validity is not intent entailment
additional witness is not a new code distinction
```

## Protocol profile

```text
intent-closed-cegis-v1
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
review_potential_v1
intent_closed_conformance_v1
terminal_holdout_v1
authority_chain_rac_v1
mutation_gate_rac_v1
closure_gate_v1
physical_apply
physical_commit
physical_push
closure_horizon_v1
```

If unavailable:

```text
analysis, adjudication, AC/CEX/CEB/MBK/RC drafting allowed
delivery mutation, commit, push, and closure forbidden
```

## Core laws

### 1. No review-to-code edge

```text
review claim
-> CEX-v1 adjudication
-> sealed batch
-> CEB/MBK/RC
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

After sealing, the observation language cannot expand without an explicit AC rebase.

### 3. Review batches are mutation barriers

While any discovery, conformance, or holdout batch is open:

```text
delivery mutation = forbidden
```

Batch all planned apertures, classify every result, quotient duplicates, then mutate once.

### 4. No counterexample without a minimal trace

Every actionable CEX identifies:

```text
accepted law/obligation
minimal trace or witness
expected observation
actual observation
current artifact state
```

Generic suspicion is not a counterexample.

### 5. No new implementation distinction for another witness

```text
new class                  -> kernel may refine
new witness, existing class -> proof may strengthen
duplicate                  -> no semantic action
outside horizon            -> follow-up or AC rebase
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

### 7. Same-class recurrence invalidates the realization

```text
same accepted class recurs after realization
-> candidate failed
-> invalidate realization
-> no local append patch
```

A novel in-horizon class returns to kernel synthesis.

An outside-horizon class returns to AC authority or follow-up.

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

All batches refine one kernel rooted at `campaign_base_sha`.

A prior tuple-local closure head is not a new compiler base.

### 10. No orphan code or proof

Every surviving construct maps to:

```text
accepted law
counterexample class
canonical owner
proof obligation
```

Targets:

```text
orphan_code_constructs = 0
wound_specific_test_families = 0
unmapped_proof_actions = 0
```

### 11. No quotient without congruence

Every accepted operation, transition, and observation respects the quotient.

Unknown congruence blocks realization.

### 12. No normal form without recomposition

Every accepted law and required observation recomposes from retained factors after quotienting and ablation.

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

### REALIZE

- Create a campaign-base-pinned realization worktree.
- Hand one accepted kernel/design to `$fixed-point-driver`.
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

Require:

```text
AC/horizon current
no open review batch
no unclassified in-horizon CEX
CEB/MBK/RC current
no novel conformance/holdout CEX
PHI terminal and strictly improved
all laws proved
all constructs/proof mapped
semantic surface conserved or explicitly rebased
current-head proof passed
PR threads swept
commit/push current
```

## Review modes

```text
discovery
  one broad pre-kernel sensing pass

kernel_review
  AC/CEB/MBK/RC only; no delivery code

conformance
  targeted RAP-v1 laws/owners/transitions/proof; whole-diff review forbidden

terminal_holdout
  one broad final challenge; no direct mutation authority
```

Every mode emits a sealed RB-v1 before mutation or closure.

## Entry modes

### Clean current-head review

If no finding-bearing campaign exists:

```text
current proof
thread sweep
tuple-bound closure
```

Do not manufacture AC/MBK machinery.

### Isolated conformance correction

Allowed only when:

```text
exactly one confirmed branch-liable existing-law violation
AC and kernel current
no new class/owner/state/protocol/public/fallback distinction
semantic surface componentwise nonincreasing
proof extends an existing law family
one sealed conformance batch
```

Still emit compact CEX/MBKC/PHI evidence.

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

1. Preflight controller.
2. Bind campaign tuple.
3. Compile and validate AC-v2.
4. Open/run/seal discovery RB-v1.
5. Use `$review-adjudication` to produce CEX-v1.
6. Use `$review-compression-compiler` to produce CEB-v2 + MBK-v1 + RC-v1.
7. Audit quotient, recomposition, proof basis, and initial PHI.
8. Select one design and create realization worktree.
9. Use `$fixed-point-driver` for one bounded realization.
10. Capture/map/measure/verify realization.
11. Run/seal targeted conformance batches.
12. Invalidate/return rather than append-patch on new evidence.
13. Certify strict PHI progress.
14. Run/seal one terminal holdout.
15. Apply/commit/push through controller.
16. Close only against current AC/kernel/batches/PHI/proof/PR tuple.

## Validation

```bash
python3 codex/skills/resolve/tools/acceptance_contract_gate.py acceptance.json
python3 codex/skills/review-adjudication/tools/counterexample_gate.py cex.json
python3 codex/skills/resolve/tools/review_batch_gate.py batch.json
python3 codex/skills/review-compression-compiler/tools/counterexample_basis_gate.py basis.json
python3 codex/skills/resolve/tools/kernel_lint.py kernel.json
python3 codex/skills/resolve/tools/review_potential_gate.py potential.json
python3 codex/skills/resolve/tools/mbkc_gate.py mbkc.json --terminal
```

## Decision observability

Emit SDR-v1-compatible decisions for:

```text
AC seal/rebase
CEX admission/disposition
CEX class merge/split
kernel acceptance
design selection
realization invalidation
return-to-kernel/contract
PHI gate
terminal closure
```

Decision contract: [decision-contract.yaml](references/decision-contract.yaml).

## Final report

```text
Resolve:
- campaign / base / baseline / head:
- AC / horizon:
- review batches / apertures:
- raw claims / valid CEX / novel classes / duplicate witnesses:
- MBK / RC / selected design:
- realization result:
- PHI before / after:
- conformance / holdout:
- proof / PR threads / delivery:
- deferred outside-horizon findings:
- residual risk:
```

End with:

```text
Resolve Bottom Line:
- intent horizon:
- novel accepted counterexamples:
- kernel transition:
- strict review-potential progress:
- realization:
- proof:
- closure:
- blocker / rebase / follow-up:
```

## Hard rules

- Never mutate from raw review prose.
- Never mutate while a review batch is open.
- Never admit an observation without AC or kernel-law anchors.
- Never let `MAY` or `OUTSIDE` behavior justify code.
- Never create a distinction for an additional witness.
- Never run generic whole-diff review during conformance.
- Never append-patch after same-class recurrence.
- Never accept a cycle without strict PHI progress.
- Never close with empty acceptance, empty finding-bearing basis, stale horizon, open batch, orphan construct/proof, or stale delivery tuple.
- Never merge or land.
