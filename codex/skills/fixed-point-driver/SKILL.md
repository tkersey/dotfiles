---
name: fixed-point-driver
description: Use this skill to drive exhaustive build-review-improve-verify workflows toward a material fixed point across accretive-implementer, adversarial-reviewer, review-adjudication, and verification-closure when a coding task needs full de novo re-litigation, optional read-only specialist subagents, signal-aware routing by soundness invariants foot-guns and complexity, a mandatory pre-closure one-change challenge, and a canonical closure handoff packet. Trigger for requests like harden this patch exhaustively, address PR reviews to closure, keep re-reviewing from scratch, find all impactful changes, adjudicate then implement accepted review work, or drive this changeset to a fixed point. Do not trigger for trivial one-step tasks or when the user explicitly wants only a single narrow phase.
---

# Fixed-Point Driver

This skill coordinates the whole workflow until the artifact set reaches a **material fixed point**.

Companion skills:
- `review-adjudication` for deciding which review comments actually matter
- `accretive-implementer` for implementation and remediation
- `adversarial-reviewer` for full-scope challenge
- `verification-closure` for decisive proof and gating

## Output modes
- **Standard**: full workflow state.
- **Fast**: only the route, current state, open gates, and exact next action.

## CLI-tail-weighted reporting
- Keep ledgers terse.
- End with **Final State** and **Do Next**.
- **Do Next** must be the last section.

## Global doctrine
Every phase inherits **UNSOUND**, **WITNESS-BEARING**, **PRESERVATION-AWARE**, **PROGRESS-AWARE**, **REFINEMENT-AWARE**, **MECHANISTIC**, **ACCRETIVE**, and **TRACEABLE** standards.
Additional orchestration pressure: **EXHAUSTIVE**, **DE NOVO**, **ADVERSARIAL**, **SATURATING**, **MATERIAL**, **FIXED-POINT**, **PARSIMONIOUS**, **INVARIANT-GRADED**, **HAZARD-SEEKING**, **CANONICAL**, and **LEDGERIZED**.

## Optional review-adjudication intake
If the user provides review comments or a prior adjudication result, you may start with **review-adjudication** before any implementation.

Rules:
- Treat adjudicated `Act On` items as routed work, not as unquestionable truth.
- Treat `Rebut`, `Defer / Out of Scope`, and `Need Evidence` as explicit workflow inputs.
- Only re-adjudicate if the rationale is stale, contradictory, or the artifact state has materially changed.

## Canonical ledgers
Maintain and refresh these ledgers after every meaningful pass:
- Findings Ledger
- Soundness Ledger
- Invariant Ledger
- Foot-Gun Register
- Complexity Ledger
- Verification Ledger
- One-Change Challenge Ledger
- Specialist Briefing Ledger
- Residual Uncertainty
- Review Comment Ledger (optional, when review-adjudication is in the workflow)

Every meaningful pass must stamp the current `artifact_state_label`.

## Subagent swarm
When subagent mode is active and custom agents are available, prefer this read-only swarm:
- `evidence_mapper`
- `soundness_auditor`
- `invariant_auditor`
- `hazard_hunter`
- `complexity_auditor`
- `verification_auditor`

Require packet-native output from every specialist:
- `artifact_state_label`
- `scope`
- `top_material_signals`
- `unresolved_signals`
- `agreement_pressure`
- `stale`
- one-line final call

## Orchestration algorithm
1. Establish entry state.
2. If unresolved PR comments exist and relevance is unclear, start with `review-adjudication`.
3. Choose the initial phase path.
4. Optionally run the specialist swarm for read-heavy evidence collection.
5. Run the saturation loop:
   - implement or remediate with `accretive-implementer`
   - review with `adversarial-reviewer`
   - normalize findings, soundness, invariants, hazards, complexity, verification, and comment adjudication into ledgers
   - rerun full-scope review after any material validation or remediation
6. Reach a **candidate material fixed point** only when no unresolved material finding, material soundness gap, unbounded critical invariant, material foot-gun, or material complexity hazard remains.
7. Run the pre-closure one-change challenge.
8. Compile the closure handoff packet and run `verification-closure`.
9. If closure reopens the loop, route the highest-value next move and continue.
10. Stop only in a justified terminal state.

## Output contract
### Standard
Use concise sections in this order:
- Workflow
- Entry State
- Upstream Intake (only when review-adjudication materially shaped the route)
- Subagent Mode
- Routing Summary
- One-Change Challenge
- Closure Handoff Packet
- Residual Risks
- Final State
- Do Next

### Fast
Use concise sections in this order:
- Entry State
- Routing Summary
- Final State
- Do Next

## Do Next
The final section must say:
- `owner`: skill | user | none
- `action`: exact next phase, stop action, or `none`
- `why`: one sentence
- `state`: ready | conditionally ready | needs remediation | needs-decision | blocked

## Hard rules
- Never impose an arbitrary maximum number of loops.
- Never let stale specialist briefings masquerade as current evidence.
- Never let review-adjudication quietly disappear once it materially shaped the route.
- Never declare a candidate fixed point while a material soundness gap remains unresolved.
- Never skip the pre-closure one-change challenge before a final closure attempt.

## Resources
- [closure-handoff-contract.md](references/closure-handoff-contract.md)
- [closure-handoff-template.md](references/closure-handoff-template.md)
- [one-change-challenge.md](references/one-change-challenge.md)
- [example-invocations.md](references/example-invocations.md)
- [common-soundness.md](../../../references/common-soundness.md)
- [common-ledgers.md](../../../references/common-ledgers.md)
- [common-cli-reporting.md](../../../references/common-cli-reporting.md)
- [common-routing-vocabulary.md](../../../references/common-routing-vocabulary.md)
