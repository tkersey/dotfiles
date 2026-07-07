# Refactor-Kernel Receipts

## Purpose

A refactor-kernel is a workflow route, not a patch style. Use it when several
accepted findings share one owner boundary, invariant, state transition, proof
surface, or missing abstraction.

The failure this prevents:

```text
many accepted liabilities
-> broad owner-boundary patch burst
-> local proof improves
-> no refactor-kernel decision
-> no outcome accounting
```

The required shape:

```text
review-fold dispositions
-> resolution fold finds repeated accepted liabilities
-> AER-v1 decision selects refactor-kernel before mutation
-> material work runs under FUSION-v1 or ALSR/HYL/HSR
-> proof/review folds current evidence
-> RKO-v1 records coverage, new liabilities, and governance state
-> ATCG-v1 decides completion
```

## Decision gate

Before the first mutation that follows a refactor-kernel decision, validate the
AER-v1 receipt:

```bash
uv run python codex/skills/actuating/tools/actuation_refactor_kernel_gate.py \
  check-decision \
  --receipt .ledger/actuating/<run-id>/aer-v1.json
```

For refactor-kernel, AER-v1 must have:

```text
selected_route = refactor-kernel
next_resolution_mode = refactor-kernel
owner_boundary named
accepted_liabilities nonempty and joinable to review-fold refs
alternatives_considered records minimal-fix, branch-race, and remediation-plan
verifier nonempty
current_artifact_scope branch/head_sha/target_fingerprint present
```

AER-v1 is not mutation authority. FUSION-v1 or ALSR/HYL/HSR still governs the
material change.

## Outcome receipt

After proof and review evidence is folded, emit RKO-v1:

```yaml
refactor_kernel_outcome:
  version: RKO-v1
  issued_at:
  run_id:
  decision_ref: AER-v1:<run_id>
  owner_boundary:
  head_before:
  head_after:
  patch_calls:
  files_changed:
  covered_liabilities:
  local_proof:
    passed: []
    failed: []
  review_after:
    new_liabilities:
    clean_runs:
    blocked_reason:
  closure_state: local-proof-only|ready-for-ship|pushed|cas-blocked|complete|regressed|blocked|unknown
  assessment: effective|overbroad|underfit|blocked|unknown
  governance:
    graph_bypass: yes|no
    mutations_without_graph_control_receipt: 0
```

Validate it with:

```bash
uv run python codex/skills/actuating/tools/actuation_refactor_kernel_gate.py \
  check-outcome \
  --outcome .ledger/actuating/<run-id>/rko-v1.json \
  --decision .ledger/actuating/<run-id>/aer-v1.json
```

`governance.graph_bypass: yes` or a nonzero
`mutations_without_graph_control_receipt` is a failed outcome, even if local
proof passed.

## Effectiveness score

The gate reports:

```text
effectiveness_score = covered_liabilities
  - new_liabilities_after_kernel
  - unresolved_terminal_blocker
  - graph_bypass_penalty
```

The score is a local diagnostic, not a global causal claim.

## Falsifier

```text
true_actuation graph_bypass sessions with refactor-kernel language -> 0
selected_route: refactor-kernel without AER-v1 decision gate -> 0
refactor-kernel outcomes with graph_bypass=yes and assessment=effective -> 0
RKO-v1 outcomes joinable to AER-v1 decisions -> all refactor-kernel runs
```
