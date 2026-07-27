---
name: tune
description: "Tune an existing Codex skill by comparing its intended decision contract with observed decision episodes and outcomes. Use Tune's passive Seq observation and Ledger artifact definitions for `$tune`, intended-vs-observed behavior, missed/false/ceremonial activations, ignored clauses, wrong routes, outcome regressions, repeated workarounds, STE-v1 packets, skill-delta candidates, explicit `$refine` handoff, or commit/push authorization for skill-refinement changes. Stop at audit/proposal unless apply or skill-refinement publication is explicit. Commit/push only with explicit publish intent."
---

# Tune

## Mission

Improve a skill by finding the smallest evidence-backed change that alters future decisions for the better.

```text
activation evidence asks: was the skill present?
decision evidence asks: what changed because of it?
outcome evidence asks: was that change useful?
```

Ownership:

```text
$seq    reconstructs bounded session evidence under Tune's definition
Ledger validates Tune's authored SKDC/SDR/STE/SDC structures
$tune   diagnoses the gap and decides the refinement route
$refine owns in-place skill-package edits after the apply gate passes
```

## Canonical evidence

For historical or multi-session tuning, prefer:

```bash
seq observe \
  --definition <tune-skill-root>/definitions/seq/skill-decision-audit.json \
  --projection evidence \
  --root <sessions-root> \
  --last 30d \
  --repo <repo> \
  --param skill=<skill> \
  --format json
```

For one watched session, prefer:

```bash
seq observe \
  --definition <tune-skill-root>/definitions/seq/skill-decision-audit.json \
  --projection evidence \
  --root <sessions-root> \
  --session-id <session> \
  --param skill=<skill> \
  --format json
```

The Seq result is evidence, provenance, corpus scope, statistics, and
limitations. It is not an STE packet and grants no authority. Tune classifies
the evidence, compares it with the target contract, authors
`skill_tuning_evidence / STE-v1`, and validates that packet through:

```bash
ledger validate \
  --definition <tune-skill-root>/definitions/ledger/skill-tuning-evidence.json \
  --input evidence=<ste.json> \
  --format json
```

For watched-session deltas, compare stable `source_event_id` and line positions
with the prior cursor. If the definition lacks a needed observation, request a
passive observation-definition change or a genuinely domain-independent Seq
operator. Do not request a new skill-specific native command.

## Modes

Choose exactly one:

```text
audit-only
proposal-only
apply-with-refine
```

`audit-only`: explain what evidence supports and does not support; no edits.

`proposal-only`: default for "improve," "optimize," or "what should change?"; produce one bounded decision delta, terminal repeat state, or no-action decision; no edits.

`apply-with-refine`: use only when the user explicitly asks to edit, apply, patch, update, or publish an already-applied skill refinement now. Produce the diagnosis first, then hand a bounded brief to `$refine` or report the publication-only state. Apply means local file changes; it does not authorize commit or push.

## Target skill type

Classify the target before judging it:

```text
decision       route selection/rejection/narrowing/blocking/escalation
execution      handoff fidelity, surface budget, observed behavior, rework
evidence       coverage, precision, provenance, false positives/negatives
orchestration  phase correctness, handoff completeness, terminal states, loops
mixed          name the relevant dimensions; do not force route-change metrics
```

## Intended-use contract

Read the target package before judging usage:

```text
SKILL.md
agents/openai.yaml
references/decision-contract.json
scripts/
references/
assets/
```

Prefer `skill_decision_contract / SKDC-v1`. If absent, reconstruct only the minimum provisional contract needed for diagnosis and label it `contract_authority: inferred`. Do not pretend inferred clauses are stable historical identifiers.

Validate an authored contract through Tune's canonical passive definition:

```bash
ledger validate \
  --definition codex/skills/tune/definitions/ledger/skill-decision-contract.json \
  --input contract=<skill-root>/references/decision-contract.json \
  --format json
```

A passing result means only that the contract is structurally valid under the
reported definition digest. Tune retains interpretation and decision authority.

## Evidence hierarchy

Use the strongest available evidence and preserve weaker classes separately:

```text
1. SDR-v1 structured decision receipt
2. explicit assistant statement tying skill to a decision
3. explicit skill use plus contract-aligned route/action
4. skill use plus downstream outcome with no route attribution
5. co-occurrence or raw mention
```

Only levels 1-2 establish a strong skill-caused decision delta. Levels 3-4 support alignment or association, not causal proof. Level 5 is weak evidence.

Decision-effect classes:

```text
explicit_route_change | prevented_action | narrowed_scope
added_or_changed_proof | escalated_or_blocked | reinforced_existing_choice
no_visible_delta | contrary_to_contract | trigger_missed
false_activation | ceremonial_activation | unknown
```

Ceremonial activation means the skill was loaded or declared but no clause was exercised, no route/scope/proof/lifecycle state changed, and the work is indistinguishable from a no-skill path. Ceremony is not automatically harmful; it becomes a tuning gap when recurrent or costly.

## Gap classes

Classify the smallest useful gap:

```text
activation | interpretation | workflow | tooling | resource
metadata | boundary | source-scope | decision-contract | observability
outcome | ceremony | overconstraint
```

Examples: trigger present with no activation -> `activation`; clause loaded but wrong route selected -> `interpretation`; repeated manual workaround -> `tooling` or `workflow`; no stable clause IDs -> `decision-contract`; useful-looking skill with unrecoverable decision effect -> `observability`; compliant route repeatedly reopens -> `outcome`; repeated no-delta use -> `ceremony`.

## Decision episode analysis

For each material episode, preserve:

```yaml
decision_episode:
  decision_id:
  session_id:
  artifact_state:
  trigger:
  activation_evidence:
  question:
  alternatives_considered: []
  selected_route:
  rejected_routes: []
  clause_refs: []
  decision_effect:
  evidence_strength:
  downstream:
  counterevidence: []
```

Do not infer alternatives that were never observed. Do not count a later successful session as proof that a skill caused the success.

Before proposing a change, ask whether the observed action plausibly would have happened without the skill, whether the skill changed the route or merely described it, whether compliance improved the outcome, whether missed activation caused failure, and whether a companion skill owns the effect.

For high-impact or ambiguous tuning, use `skill_decision_provenance_auditor` and/or `skill_outcome_skeptic`.

## Canonical tune packet

Consume or emit `skill_tuning_evidence / STE-v1`. It must preserve target kind, contract authority, window, denominator, trigger quality, decision influence, clause compliance, outcomes, workarounds, exemplars, recurrent gaps, and limitations.

## Skill delta

Produce at most one dominant `skill_delta_candidate / SDC-v2` per cycle.

Required fields:

```text
target and type
source packet
gap signature/type
episode and clause refs
evidence class/recurrence/confidence
expected decision delta
smallest change
protected contracts
outcome-observation query
proposed action
publish authorization and commit/push state, when apply-mode is requested
```

If there is no expected decision delta, do not produce a long redesign.

Validate an authored candidate through Tune's canonical definition:

```bash
ledger validate \
  --definition <tune-skill-root>/definitions/ledger/skill-delta-candidate.json \
  --input candidate=<sdc.json> \
  --format json
```

A pass establishes only structural validity under the reported definition
digest. Tune retains change-selection authority.

## Repeat proposal ledger

Track proposal signature, first/last seen, repeat count, evidence delta, state, and next action. If the same proposal appears three times without new decision/outcome evidence, emit one terminal state:

```text
apply-blocked
final-brief
transferred-to-definition
retired
```

## Apply / publish gates

Apply-with-refine may edit files only when all hold:

- explicit user request to edit, apply, patch, update, or publish a skill refinement now;
- target, evidence source, and intended contract are identified;
- protected-skill restrictions are satisfied;
- decision/outcome gap is sufficiently evidenced and smallest change is known;
- stable clause IDs are preserved unless intentionally replaced;
- an outcome-observation query exists when the claimed effect requires later evidence.

Publishing is separate:

- commit only after explicit commit, publish, ship, or save-to-git intent exists;
- push only after commit succeeds and explicit push or remote-publish intent exists;
- otherwise report commit/push as `blocked:not-requested`.
- when publishing was requested but pre-commit or worktree checks fail,
  report the specific blocked state instead of collapsing it to `blocked:not-requested`.

If any required gate fails, stop at audit/proposal or report blocked publication.

## Handoffs

`$refine` handoff: use `REFINE-SKILL-v3`. The brief must bind source packet, target kind, gap/clause refs, expected delta, optimization boundary, intervention budget, forbidden changes, smallest-change hint, outcome-observation query, and publish authorization when relevant. Do not hand `$refine` raw transcripts when STE-v1 is available.

Missing observation handoff: identify the physical evidence, the owning passive
definition, the missing generic operator if any, bounds, and acceptance
examples. Never ask Seq to acquire Tune vocabulary or decision authority.

## Subagent policy

Default root-only for small, explicit gaps.

Use `skill_contract_modeler` when the target is decision-oriented and lacks SKDC-v1.

Use `skill_decision_provenance_auditor` when episodes are numerous or attribution is ambiguous.

Use `skill_outcome_skeptic` when compliance/outcome correlation could be mistaken for causation.

`$refine` owns authorized package optimization after `$tune` produces a bounded packet or brief. Do not delegate this to a system-managed optimizer.

## Outcome observation

Rerun the exact `seq observe` invocation named by the tuning packet when current
evidence can exist. Otherwise retain it as a future observation. A text edit
does not prove that behavior improved.

## Report

```text
Tuned:
- Target:
- Target kind:
- Mode:

Evidence:
- Source:
- Packet:
- Contract authority:
- Decision episodes:
- Limitations:

Diagnosis:
- Intended:
- Observed:
- Gap:
- Decision effect:
- Outcome signal:

Skill delta:
- From:
- To:
- Smallest change:
- Repeat state:

Handoff / action:
- <no action | refine brief | Seq definition gap | applied edit>
- Publication: <authorization | commit | push>

Outcome observation:
- Current evidence:
- Future query:

Remaining uncertainty:
```

## Hard rules

- Raw mentions are not activation.
- Activation is not decision influence.
- Decision influence is not outcome causality.
- A successful outcome is not proof of skill effectiveness by itself.
- A clause never observed may be unnecessary, untriggered, or merely unobservable; do not assume which.
- Preserve denominators.
- Preserve counterevidence.
- Prefer no edit over a weakly supported edit.
- No decision delta, no full cycle.
- No repeated proposal without terminal state.
- Apply/edit authority is not commit/push authority.
- No commit or push without explicit publish intent.
- No `$seq` CLI edit without a separate spec.
