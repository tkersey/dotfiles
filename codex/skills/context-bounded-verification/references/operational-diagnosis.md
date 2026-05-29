# Operational Diagnosis from Recent Usage Bundle

Bundle generated: 2026-05-29T06:05:54-0700.

## Corpus shape

- Direct audit summary: 9 mentions across 4 sessions.
- Success summary: 4 successful/used/called sessions; 2 sessions where the assistant explicitly mentioned the skill; 4 blocked sessions; 9 raw mentions.
- Workflow audit: 4 cohort sessions, 3372 signals.
- Dominant workflow signals: `exec_command` 1360, `write_stdin` 1102, proof outcomes 213 assistant-text signals, 98 `apply_patch` signals, 43 `update_plan` signals.
- Outcomes: proof 223/4 sessions, blocked 33/4, closure 32/4, commit 22/3, test 17/2, PR 11/2.
- Message search: 1369 rows across 1328 paths mentioning `context-bounded-verification`, dominated by implicit assistant activation statements for review, Zig, PR readiness, closure, CAS/resolve, and proof-evidence workflows.

## Representative sessions

- 2026-05-10: User investigated why the skill was reported as heavily used despite few explicit invocations. Assistant concluded explicit invocations were sparse and likely implicit/root-equivalent.
- 2026-05-17: User asked which tier was most common. Assistant found Tier 2 dominated only among explicitly labeled tier mentions, while most activations lacked tier labels.
- 2026-05-24/25: Tuning session modified the skill heavily, especially generated-artifact/proof-surface doctrine.
- 2026-05-28/29: User requested multi-skill usage reports including this skill.

## Successes observed

- The skill successfully appears in high-risk contexts: proof, closure, test, commit, and PR signals were present in every or most cohort sessions.
- It is commonly paired with Zig and review workflows where context-bounded verification is appropriate.
- Recent tuning already improved generated-artifact, certificate, source-map, policy, quota, and verifier-strength doctrine.

## Failure modes inferred from usage shape

The report corpus is sparse for full outcomes, so these are operational risks inferred from signal shape and representative messages rather than proven defects in every session.

1. Implicit activation without explicit tier/output packet.
   - Message search shows many activation statements but few explicit `Tier N` labels and only a few full `Verification Gap Report`-style outputs.
   - Risk: broad Tier 2 review/closure work can be treated as a lightweight rail.

2. Closure/readiness laundering.
   - Workflow outcomes include proof, closure, commit, test, and PR signals, but the existing skill lacked a mechanical gate.
   - Risk: stale or partial evidence can become a pass/readiness claim.

3. Evidence/actionability collapse.
   - Review/CAS/Zig workflows often combine reviewer findings, current code, proof, and implementation pressure.
   - Risk: plausible or severe claims become implementation work without current-state evidence and scope fit.

4. Stale-state failures.
   - The skill already contained exact-tree warnings, and usage frequently involved long sessions with many tool calls and patching.
   - Risk: proof run against an earlier tree is reused for a later delivered tree.

5. Direction/scope failures.
   - Coupling to resolve, review-adjudication, invariant-ace, CAS, and PR closeout means old plans and external review pressure can shape the route.
   - Risk: locally correct work violates the current objective or non-goals.

6. Validation/closure failures.
   - Proof signals were common, but only some sessions had test signals; full packet fields were absent from the old skill.
   - Risk: green unrelated checks or manual inspection are overstated.

7. Handoff/implementation laundering.
   - The skill sits between review/adjudication, implementation, fixed-point, and closure workflows.
   - Risk: handoffs lack current evidence, agenda boundaries, and `must_not_do` constraints.

8. Subagent/parallelism gap.
   - Broad PR and proof-surface reviews benefit from read-only authority separation, but the current skill had no custom subagents.
   - Risk: root mixes evidence, direction, blast radius, and closure authority into one permissive judgment.

## Hardening response

This drop-in adds:

- a stricter SKILL.md doctrine preserving bounded verification identity;
- `CBV-GATE-v1` packet contract;
- `context_verification_gate.py` mechanical checker;
- bounded read-only authority subagents;
- references for output, gate, and authority model;
- adversarial eval seeds targeting stale proof, severity laundering, wrong-objective work, proof-surface weakness, generated-artifact mismatch, handoff safety, memory-only closure, implicit Tier 2 readiness, unchecked blast radius, and valid Tier 3 blocks.
