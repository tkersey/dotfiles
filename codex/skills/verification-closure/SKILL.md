---
name: verification-closure
description: Use this skill for targeted validation and final readiness decisions when a coding task needs direct evidence, explicit closure gates, and a canonical Closure Handoff Packet from fixed-point-driver carrying the latest findings invariants hazards complexity verification and specialist ledgers. Trigger for requests like verify this patch is actually ready, run closure gates, resolve material verification gaps, or decide if the artifact set reached a material fixed point. Do not trigger for broad redesign or general code review without a closure question.
---

# Verification Closure

Use this skill for **proof and gating**, not for broad redesign or de novo architecture work. The goal is to decide whether the current artifact set is actually ready by consuming a canonical handoff, running the narrowest decisive checks, and assigning grounded closure states.

## Global doctrine

Operate in **UNSOUND**, **MECHANISTIC**, **TRACEABLE**, **MATERIAL**, **FIXED-POINT**, **CANONICAL**, and **LEDGER-AWARE** mode.

- **UNSOUND**: do not upgrade claims beyond the evidence.
- **MECHANISTIC**: verify the claimed failure mechanism and the actual changed path, not just nearby symptoms.
- **TRACEABLE**: tie every closure call to concrete checks, outputs, files, or ledgers.
- **MATERIAL**: close consequential gates; do not turn closure into style review.
- **FIXED-POINT**: decide whether the artifact set has actually stopped yielding unresolved material closure pressure.
- **CANONICAL**: prefer the fixed handoff schema over ad hoc summaries.
- **LEDGER-AWARE**: consume and preserve distinctions among findings, invariants, hazards, complexity, verification, and specialist signals.

## CLI-tail-weighted reporting

Assume the user may only see the last screenful of terminal output.

- Keep evidence sections terse and specific.
- Put the merge / no-merge decision at the end.
- End every report with **Reopen Trigger** and **Closure Bottom Line**.
- **Closure Bottom Line** must restate readiness, fixed-point status, and the single next check or `none`.

## Canonical handoff intake

If a **Closure Handoff Packet** is present, read it first. Use the schema in `references/closure-handoff-contract.md`.

Packet intake rules:

1. Validate the packet headings and order.
2. Record **Handoff Contract Status** as:
   - `complete`
   - `incomplete`
   - `stale`
3. Treat packet fields as structured claims, not proof.
4. Seed the **Closure Gate Ledger** from the packet's ledgers.
5. If a required field is missing, reconstruct the missing part from context if possible and mark the contract `incomplete`.
6. If a specialist briefing's `artifact_state_label` differs from the packet's current state label, mark it stale and do not treat it as current proof.
7. If the packet is absent, reconstruct the minimum viable intake from context and mark the contract `incomplete`.

## Closure Gate Ledger

Always produce these gate statuses:

- `direct_changed_path`: `satisfied` | `open` | `blocked` | `conflicting`
- `claimed_failure_mechanism`: `satisfied` | `open` | `blocked` | `conflicting`
- `regression_surface`: `satisfied` | `open` | `blocked` | `conflicting`
- `critical_invariants`: `preserved` | `strained` | `broken` | `unknown`
- `material_foot_guns`: `bounded` | `unbounded` | `unknown` | `accepted-risk`
- `material_complexity_hazards`: `bounded` | `unbounded` | `unknown` | `residual-design-risk`
- `briefing_agreement`: `aligned` | `mixed` | `conflicting`
- `external_blockers`: `none` | `present`

## Operating procedure

1. Read the packet and current task context.
2. Build the **Closure Gate Ledger** from:
   - the packet
   - direct code or artifact inspection
   - tests, commands, logs, and outputs
   - reviewer output
   - specialist briefings
3. Build a minimal evidence plan in this priority order:
   - direct changed-path proof
   - highest-tier unresolved invariant
   - highest-confidence material verification gap
   - material foot-gun or misuse path that can be directly exercised or bounded
   - plausible regression surface
   - broader integration checks only if narrower checks cannot close the open gates
4. Execute verification in tiers:
   - **Tier 0: intake and reconciliation**
     - validate the packet
     - identify stale or conflicting specialist inputs
     - design the smallest resolving check when briefings disagree materially
   - **Tier 1: direct proof**
     - exercise the changed behavior or claimed bug fix directly
   - **Tier 2: contract and invariant proof**
     - run the narrowest checks that support or falsify unresolved critical invariants or regression claims
   - **Tier 3: hazard bounding**
     - test or otherwise bound any material foot-gun on a likely misuse, default, retry, rollback, migration, or operational path when feasible
   - **Tier 4: broader confidence**
     - run broader suite, integration, or environment validation only if earlier tiers leave material uncertainty
5. Make two separate judgments:
   - **Fixed-Point Test**
     - `appears reached` only if no unresolved material gate remains
     - `not reached` if any unresolved material gate remains
     - `indeterminate` if evidence is missing, contradictory, or too environment-dependent for a grounded call
   - **Readiness**
     - `ready` if direct behavior is verified, material gates are closed, and no unexplained failures remain
     - `conditionally ready` if core behavior is verified but bounded non-material gaps or accepted risks remain
     - `not ready` if any material gate remains open or failed
     - `indeterminate` if the evidence base is contradictory or insufficient for a grounded call
6. If readiness is not `ready` or `conditionally ready`, say which gate should reopen the fixed-point-driver loop.

### Closure Bottom Line
Use 3-5 lines max:
- `readiness`: ready | conditionally ready | not ready | indeterminate
- `fixed_point`: appears reached | not reached | indeterminate
- `merge_call`: merge | do-not-merge | hold
- `next_check`: exact next check or `none`

## Specialist briefings

Specialist briefings are high-signal inputs. They are not proof by themselves.

Use them to answer:
- which critical invariant is still open,
- which material foot-gun is still unbounded,
- which complexity concern is a real closure blocker versus a residual design risk,
- which single next check has the highest closure value.

If briefings materially conflict and no resolving check was run, use `indeterminate` rather than averaging them away.

## Hard rules

- Never say `verified` or `ready` if the direct changed path was not exercised, unless a concrete blocker is stated and readiness is therefore not granted.
- Never treat the packet as proof without supporting evidence.
- Never hide failed, flaky, skipped, blocked, stale, or contradictory checks.
- Never let unrelated green tests substitute for missing direct evidence.
- Never call a critical invariant preserved without naming the supporting evidence.
- Never ignore a material foot-gun just because happy-path tests pass.
- Never dismiss a material complexity hazard unless you can explain why it is bounded or non-blocking.
- Never say fixed point reached when any material gate remains open.
- Never broaden into redesign or implementation unless explicitly asked.
- Never silently repair an incomplete handoff contract; report the missing pieces.

## Definition of done

A closure pass is done only when:
1. **Handoff Contract Status** was assigned,
2. the **Closure Gate Ledger** was produced,
3. the direct changed behavior was exercised or a concrete blocker was identified,
4. at least one regression, contract, or critical-invariant check was run or explicitly justified,
5. material foot-guns and material complexity hazards were explicitly adjudicated,
6. both a **Fixed-Point Test** and a **Readiness** state were assigned,
7. exact next checks or reopen conditions were stated when closure was not granted.

## Response shape

Use concise sections in this order:

- Handoff Contract Status
- Verification Target
- Evidence Inputs
- Closure Gate Ledger
- Evidence Run
- Results
- Residual Risks
- Fixed-Point Test
- Readiness
- Reopen Trigger
- Closure Bottom Line
