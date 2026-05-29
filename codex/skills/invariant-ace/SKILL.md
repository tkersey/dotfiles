---
name: invariant-ace
description: "Turn should-never-happen into cannot-happen with authority-gated invariant design. Define owned inductive invariants, separate predicates from pre/postconditions and derived facts, require counterexample traces, owner/scope/source-of-truth proof, transition preservation, policy/exception authority, witness parity, enforcement-boundary choice, and verification. Use for invariants, impossible states, validation sprawl, cache/index drift, idempotency/versioning, retries/duplicates/out-of-order events, races, loop correctness, policy-owned exceptions, generator/validator parity, descriptor-vs-occurrence identity, certificate/proof witness drift, fixture precondition alignment, or invariant-first hardening. Not for generic refactors, broad architecture essays, or implementation without an invariant gate."
---

# Invariant Ace

## Mission

Turn "should never happen" into "cannot happen" with minimal, high-leverage changes: name the real state owner, define owned inductive predicates, prove a counterexample trace, choose the strongest cheap enforcement boundary, and attach verification that can falsify the invariant and the proposed enforcement.

This skill is **discriminative**, not decorative. An invariant proposal is a claim to adjudicate, not a mandate to add checks. A property may be true, useful, or reviewer-sounding and still be the wrong invariant, wrong owner, wrong scope, wrong phase, wrong witness, or wrong boundary.

## Default mode

Use **Authority-Gated v1** when invariant analysis can affect implementation, review adjudication, proof closure, validation, or downstream handoff.

Authority-Gated v1 requires:

- stable candidate invariant IDs;
- artifact and direction state identity;
- counterexample trace or explicit no-current-counterexample classification;
- owner/scope/source-of-truth proof;
- transition/induction coverage;
- enforcement-boundary selection with why-not-weaker/why-not-stronger reasoning;
- exception and policy ownership checks;
- generator/validator/witness parity checks;
- fixture precondition alignment;
- verification plan tied to predicates;
- authority packet receipts and veto handling when the task is non-trivial or consequential;
- an Invariant Gate before implementation, review-adjudication handoff, proof closure, or fixed-point routing.

Compact mode is allowed only for exploratory invariant sketches, and it must block implementation handoff unless the Invariant Gate passes.

## Core doctrine

Operate in **OWNER-FIRST**, **COUNTEREXAMPLE-DRIVEN**, **INDUCTIVE**, **AUTHORITY-GATED**, **SOURCE-OF-TRUTH-SEEKING**, **POLICY-OWNED**, **WITNESS-PARITY**, **FIXTURE-AWARE**, **FAIL-CLOSED**, **ACCRETIVE**, and **PROOF-BEARING** mode.

- **OWNER-FIRST**: if you cannot name the state owner and mutation boundary, you do not yet have an enforceable invariant.
- **COUNTEREXAMPLE-DRIVEN**: every accepted invariant needs a concrete bad trace, or an explicit proof-only reason why no current trace exists.
- **INDUCTIVE**: accepted invariants must hold initially and be preserved by every allowed transition in scope.
- **AUTHORITY-GATED**: consequential invariants require independent clearances; unresolved vetoes block `enforce-now`.
- **SOURCE-OF-TRUTH-SEEKING**: enforce at the owner/source of truth, not at downstream local shortcuts.
- **POLICY-OWNED**: exceptions must be encoded in the policy owner, allowlist, capability, ACL, flag, or protocol that owns the invariant.
- **WITNESS-PARITY**: validation, generation, projection, certificate, source-map, replay, and proof paths must use the same identity/witness semantics or a named stricter refinement.
- **FIXTURE-AWARE**: tests must satisfy upstream preconditions when targeting downstream invariants; otherwise they prove the wrong boundary.
- **FAIL-CLOSED**: unsupported, unmodeled, or unknown cases must block or validate before certificate/proof/artifact construction.
- **ACCRETIVE**: prefer the smallest truthful boundary repair that removes the illegal state without broadening the system.

## Contract

- Do not implement fixes here unless another skill explicitly owns implementation after this gate.
- Do not accept a candidate invariant without owner, scope, holds-when, source-of-truth, counterexample/trace status, transition coverage, enforcement boundary, and verification.
- Do not confuse invariants with preconditions, postconditions, liveness goals, local assertions, style rules, or reviewer preferences.
- Do not fix identity drift locally when the shared identity predicate belongs to another phase or owner.
- Do not add local explicit-input shortcuts around policy predicates.
- Do not trust generated, caller-provided, or fixture-typed witness fields when they should be recomputed or bound to an owning certificate/proof.
- Do not let stronger outer gates silently invalidate inner-invariant tests; choose whether to configure the outer gate to reach the inner failure or update the expected boundary deliberately.
- Do not route `validate-only`, `proof-only`, `defer`, `no-change`, or `blocked` invariant rows into implementation.
- Do not allow root to upgrade a vetoed or unresolved invariant to `enforce-now`; clear the veto or stay non-permissive.

## Use When (Signals)

- Null/shape surprises, runtime validation sprawl, scattered input decoding, or "unreachable" branches reached in logs.
- Redundant stored facts drift: cache/index/denormalized columns/certificates/source maps/summaries.
- Descriptor identity differs from occurrence/site/route multiplicity.
- Validation accepts by one identity rule while generation/projection/certificate paths select by another.
- Policy-owned exceptions are bypassed by local explicit-input, explicit-port, shortcut, or allow flag paths.
- Tests drift because an outer policy gate rejects before the inner invariant under test.
- Generator/validator parity, certificate witness, proof-object, replay-frame, source-map, or blocked-state accounting issues.
- Races, duplicate/out-of-order events, retries, stale writes, idempotency, linearization, or loop invariants.

## Authority fanout mode

For consequential invariant work, use custom Codex authority agents. They solve both bandwidth and authority: independent lanes gather evidence in parallel, and each lane owns a decision dimension.

Required lanes when an invariant can become implementation work or block closure:

| Role | Owns |
|---|---|
| `inv-counterexample-authority` | concrete bad trace, reachability, falsifier |
| `inv-owner-scope-authority` | state owner, scope, source of truth, same-objective fit |
| `inv-induction-authority` | transition set and preservation/induction closure |
| `inv-boundary-authority` | enforcement boundary and why local/stronger/weaker cuts are wrong |
| `inv-witness-parity-authority` | generator/validator/projection/certificate/fixture/witness parity |
| `inv-verification-authority` | proof signal tied to each predicate |
| `inv-skeptic-authority` | strongest no-invariant/no-enforce countercase |

Authority rules:

- Each required lane returns a packet; packets are not votes.
- Root remains the final synthesizer but may only downgrade without re-clearance.
- `enforce-now` requires all required authority lanes clear and the skeptic lane defeated.
- Any unresolved or veto packet blocks `enforce-now`.
- Missing authority packets require `blocked` unless a same-schema root-equivalent packet is emitted.
- Rejected packets are logged and cannot support accepted invariants.

See `references/authority-fanout.md` and `references/CODEX_SUBAGENTS.md`.

## Immediate scan

Before declaring an invariant, record:

```yaml
artifact_state_id:
  branch:
  base:
  head:
  diff_digest:
  proof_state:

direction_state_id:
  source:
  source_ref:
  same_objective:
  non_goals:
  compatibility_posture:
```

Then ask:

- State owner: where does truth live?
- Raw boundary: where does untrusted or derived state enter?
- Allowed transitions: which operations/events mutate the state?
- Failure today: what minimal trace reaches the bad state?
- Identity semantics: unique descriptor, occurrence, site, route, target, or witness?
- Exception owner: what policy/capability/allowlist authorizes exceptions?
- Witness owner: who proves downstream usability, not mere existence?
- Fixture preconditions: which upstream gates must be satisfied to test this boundary?
- Protection level: hope -> runtime -> construction-time -> type/compile-time -> persistence/protocol/atomicity.

## Candidate classification

Classify each candidate:

- `accepted`: owned, inductive, enforceable, currently material, and cleared by authority lanes.
- `candidate`: plausible but missing route-changing evidence.
- `downgraded`: useful property, but it is a pre/postcondition, liveness goal, derived check, test-only guard, or non-material convention.
- `rejected`: wrong owner, wrong scope, wrong identity rule, ungrounded, duplicate boundary, or direction-conflicting.
- `unresolved`: material uncertainty; validation or artifact search required.
- `blocked`: missing artifact state, direction state, authority packet, identity proof, or verification path prevents safe routing.

Allowed routes:

- `enforce-now`: implement/handoff allowed only after gate passes.
- `validate-only`: add proof/probe/test before mutation.
- `proof-only`: current artifacts already satisfy the invariant; only cite proof.
- `defer`: real invariant but wrong owner/timing/scope.
- `no-change`: reject/downgrade; no implementation work.
- `blocked`: fail closed.

## Output contract: Authority-Gated v1

Emit these sections, in order, for consequential runs:

1. `Review Basis`
2. `Candidate Invariant Inventory`
3. `Counterexample Ledger`
4. `Invariant Ledger`
5. `Owner and Scope Ledger`
6. `Transition / Induction Matrix`
7. `Enforcement Boundary Decision`
8. `Policy / Exception Ledger`
9. `Witness and Fixture Parity Ledger`
10. `Verification Plan`
11. `Authority Packet Receipts`
12. `Authority Clearance Matrix`
13. `Authority Veto Ledger`
14. `Accepted Invariants`
15. `Validate Only`
16. `Proof Only`
17. `Defer / No Change`
18. `Change Agenda`
19. `Acceptance Skew Audit`
20. `All-Invariant Accepted Justification` when every substantive candidate is `accepted` or `enforce-now`
21. `Invariant Gate`
22. `Ace Bottom Line`

### Candidate Invariant Inventory

```md
- candidate_count:
- accepted_count:
- validate_only_count:
- proof_only_count:
- defer_or_no_change_count:
- blocked_count:
- candidate_ids:
- accepted_ids:
- validate_only_ids:
- proof_only_ids:
- defer_or_no_change_ids:
- blocked_ids:
- missing_candidate_ids:
- duplicate_candidate_ids:
```

### Invariant Ledger

| id | predicate | owner | scope | holds when | source of truth | acceptance status | enforcement boundary | verification signal | evidence ref | route |
|---|---|---|---|---|---|---|---|---|---|---|

### Authority Clearance Matrix

| id | counterexample | owner/scope | induction | boundary | witness/parity | verification | skeptic | authority status | packet refs |
|---|---|---|---|---|---|---|---|---|---|

Allowed clearance values: `clear`, `veto`, `unresolved`, `not-needed`, `not-in-scope`. Skeptic values: `defeated`, `veto`, `unresolved`, `not-needed`. Authority status: `cleared-for-enforcement`, `cleared-for-validation`, `proof-only`, `defer`, `no-change`, `blocked`.

### Authority Veto Ledger

| id | veto source | veto class | veto claim | evidence ref | required to clear | final route |
|---|---|---|---|---|---|---|

Veto classes include: `no-counterexample`, `wrong-owner`, `wrong-scope`, `not-inductive`, `wrong-boundary`, `policy-bypass`, `identity-drift`, `witness-missing`, `fixture-precondition-mismatch`, `duplicate-boundary`, `validation-needed`, `proof-only`, `direction-conflicting`, `missing-packet`.

### Change Agenda

| id | route | change | proof or validation required | next | owner |
|---|---|---|---|---|---|

The Change Agenda must be an exact projection of `route` in the Invariant Ledger. It must not use broad words like `all` when explicit IDs are required.

## Invariant Gate

Required fields:

- `artifact_state_coverage`: `pass` / `fail`
- `candidate_inventory_coverage`: `pass` / `fail`
- `counterexample_coverage`: `pass` / `fail`
- `owner_scope_coverage`: `pass` / `fail`
- `induction_coverage`: `pass` / `fail`
- `boundary_decision_coverage`: `pass` / `fail`
- `policy_exception_coverage`: `pass` / `fail`
- `witness_fixture_parity_coverage`: `pass` / `fail`
- `verification_coverage`: `pass` / `fail`
- `authority_packet_coverage`: `pass` / `fail`
- `authority_clearance_coverage`: `pass` / `fail`
- `authority_veto_coverage`: `pass` / `fail`
- `change_agenda_consistency`: `pass` / `fail`
- `acceptance_skew_audit`: `pass` / `fail`
- `invariant_gate_complete`: `pass` / `fail`
- `implementation_handoff_allowed`: `yes` / `no`
- `validation_handoff_allowed`: `yes` / `no`
- `proof_only_handoff_allowed`: `yes` / `no`

`invariant_gate_complete` may be `pass` only when all preceding required gate fields pass. `implementation_handoff_allowed: yes` requires at least one `enforce-now` row whose authority status is `cleared-for-enforcement` and no unresolved veto exists for that ID.

## Machine check

When automation is available, run:

```bash
python codex/skills/invariant-ace/tools/invariant_ace_gate.py invariant-output.md
```

A failed checker means no implementation handoff.

## Hard rules

- Do not enforce a candidate invariant without a concrete owner and scope.
- Do not enforce a candidate invariant without transition/induction coverage.
- Do not accept identity equality as witness/capability/proof of downstream usability.
- Do not add policy exceptions outside the policy owner.
- Do not let generated self-checks substitute for validation of externally supplied artifacts.
- Do not let fixtures bypass or trip the wrong preconditions without an explicit fixture alignment decision.
- Do not trust a caller override for a field that must be recomputed from generated/compiled/selected artifacts.
- Do not route unresolved authority or vetoed invariants to implementation.
- Do not claim completion when validation/proof is still pending.

## Resources

- [authority-fanout.md](references/authority-fanout.md)
- [invariant-gate-contract.md](references/invariant-gate-contract.md)
- [invariant-output-template.md](references/invariant-output-template.md)
- [CODEX_SUBAGENTS.md](references/CODEX_SUBAGENTS.md)
- [adversarial-eval-seeds.yaml](evals/adversarial-eval-seeds.yaml)
