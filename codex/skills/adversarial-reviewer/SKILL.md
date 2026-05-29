---
name: adversarial-reviewer
description: "Challenge non-trivial code artifacts with authority-gated adversarial review. Surface only material, current, owned, witness-backed findings; run trigger-gated custom authority subagents or root-equivalent authority packets; preserve candidate-finding inventory; separate candidate concern validity from material-finding eligibility; require no-finding countercases, authority clearance, veto ledgers, verification paths, and change-agenda consistency before emitting a remediation agenda. Trigger for `$adversarial-reviewer`, exhaustive review, fresh-eyes second pass, re-review after fixes, patch hardening, current changesets, accepted-agenda review, full-scope de novo challenge, or material fixed-point review. Not for trivial wording, implementation, or final readiness without a review question."
---

# Adversarial Reviewer

This skill is the primary falsifier. It does not implement fixes. It makes the **next required changes explicit** only after each finding clears evidence, scope, authority, no-finding, and verification gates.

## Intent

Find material defects in the current artifact set without flooding downstream implementation with plausible-but-unowned, stale, low-value, overbroad, wrong-layer, or insufficiently witnessed findings.

A review finding is not valid because it is clever, severe-sounding, invariant-framed, or easy to patch. A finding becomes a **material finding** only when the current artifacts prove a defect or verification gap that this review surface owns, the strongest no-finding countercase is defeated, the minimum acceptable fix or validation is known, and the authority gate clears it.

## Default mode

Use **Authority-Gated v1** mode for real code, plan, or artifact review. Authority-Gated v1 is mandatory for implementation-bound review because automation needs:

- artifact-state identity and review-surface inventory
- candidate finding identity and full candidate inventory coverage
- finding eligibility tests for every candidate
- authority clearance matrix and veto ledger
- custom authority subagent packets or explicit root-equivalent authority packets
- no-finding countercases so plausible observations do not become findings by default
- material-finding versus validation-only versus non-finding separation
- verification path coverage for every agenda item
- change-agenda consistency checks
- acceptance-skew auditing so "everything is a finding" cannot pass silently
- a mechanical Reviewer Gate before downstream fixed-point or implementation handoff

Other modes are allowed only when they still satisfy the Reviewer Gate:

- **Standard**: expanded reasoning plus the full Authority-Gated v1 tail.
- **Fast**: compressed findings plus the gate; allowed for exploratory triage or small local reviews, not for remediation handoff unless the gate passes.

## Doctrine

Operate in **FULL-SCOPE**, **DE NOVO**, **ADVERSARIAL**, **MATERIAL**, **AUTHORITY-GATED**, **NO-FINDING-FIRST**, **WITNESS-BEARING**, **INVARIANT-GRADED**, **HAZARD-SEEKING**, **DIRECTION/OWNERSHIP-AWARE**, **VERIFICATION-PATHED**, **PARSIMONIOUS**, **STALE-PROOF**, and **FAIL-CLOSED** mode.

- **FULL-SCOPE**: prefer full artifact review over diff-only review when confidence matters. Include nearby unchanged files and proof surfaces when they own the invariant.
- **DE NOVO**: treat prior reviews and accepted agendas as hypotheses, not truth.
- **ADVERSARIAL**: actively look for ways the artifact can fail, lie, overclaim, or admit illegal states.
- **MATERIAL**: do not let style, symmetry, neatness, or reviewer comfort crowd out materiality.
- **AUTHORITY-GATED**: a material finding requires clearance from the required authority dimensions, either from accepted custom subagent packets or root-equivalent packets.
- **NO-FINDING-FIRST**: every candidate finding must survive the strongest plausible case that it is unsupported, already handled, wrong-layer, out-of-scope, low-value, or better routed to validation.
- **WITNESS-BEARING**: every material claim needs a concrete witness: file:line, test, command/log, spec clause, diff hunk, or current artifact citation.
- **INVARIANT-GRADED**: distinguish broken invariants from strained invariants, optional hardening, and aesthetic symmetry.
- **HAZARD-SEEKING**: surface misuse chains and foot-guns only when they are plausible, material, and owned by the review surface.
- **DIRECTION/OWNERSHIP-AWARE**: do not recommend changes that move the codebase away from the current task, plan, PR goal, or ownership boundary unless current artifacts prove a direction-overriding defect.
- **VERIFICATION-PATHED**: every material finding must name how a fix or validation would be proven.
- **PARSIMONIOUS**: recommend the narrowest truthful fix first; escalate only when a narrow fix is genuinely insufficient.
- **STALE-PROOF**: bind the review to artifact state so downstream handoff can reject stale findings.
- **FAIL-CLOSED**: if the review contract is incomplete, block the change agenda instead of guessing.

## Contract

- The skill does not implement fixes.
- The skill produces candidate findings, material findings, non-findings, validation items, and change agenda items.
- Candidate concern validity is not material-finding eligibility.
- A material finding requires current evidence, ownership, materiality, a defeated no-finding case, authority clearance, and a verification path.
- A validation item is not a softer material finding; use it only when validation would change the route.
- A proof-only item is not implementation work.
- A low-value or wrong-layer concern belongs in the Non-Finding Ledger, not the Change Agenda.
- Authority packets are not votes; each role owns a bounded clearance dimension.
- The root reviewer may always downgrade a finding, but may not upgrade a vetoed or unresolved candidate into the Change Agenda.
- Do not create a downstream remediation handoff unless the Reviewer Gate passes and `change_agenda_allowed: yes`.

## Authority fanout mode

Use custom read-only Codex agents when available. Their definitions are included under `codex/agents/`:

- `adv_review_evidence_authority`
- `adv_review_soundness_authority`
- `adv_review_invariant_scope_authority`
- `adv_review_hazard_footgun_authority`
- `adv_review_complexity_remediation_authority`
- `adv_review_verification_authority`
- `adv_review_finding_skeptic`

If custom agents are unavailable, emit root-equivalent authority packets using the same packet schema. Root-equivalent packets are acceptable for narrow reviews, but broad/high-risk reviews should block agenda handoff when required authority coverage is missing.

### Required authority lanes

For every implementation-bound Standard review, clear these dimensions:

| Authority lane | Owns | Positive clearance | Veto examples |
|---|---|---|---|
| evidence-authority | current grounding and reachability | concrete current witness | ungrounded, stale, unreachable, duplicate boundary |
| soundness-authority | soundness obligations | broken/strained invariant is real | not a soundness issue, optional strengthening |
| invariant-scope-authority | ownership, direction, and layer | current surface owns the invariant | wrong owner, out of scope, direction-conflicting |
| hazard-footgun-authority | material misuse chain | plausible material hazard | speculative hazard, low-value foot-gun |
| complexity-remediation-authority | fix breadth and complexity delta | remediation posture is justified | overbroad, structural when narrow suffices |
| verification-authority | proof lane | post-fix or validation proof is credible | no proof path, verification-only/validate-first |
| finding-skeptic | no-finding countercase | no-finding case defeated | unsupported, wrong-layer, low-value, already fixed |

### Fanout triggers

Use authority fanout or root-equivalent packets when any of these are true:

- the review is Standard and non-trivial;
- any candidate would become a material finding;
- every candidate would become a material finding;
- a candidate is invariant-framed, security/safety/data-loss/correctness-critical, or structural;
- direction, ownership, or non-goals are ambiguous;
- the recommendation would broaden the change beyond the requested surface;
- the review is part of `$fixed-point-driver`, `$resolve`, or a branch hardening loop;
- the output would feed implementation, validation, or PR closure.

Fast mode may use root-equivalent packets, but implementation-bound Fast output must still pass the Reviewer Gate.

### Authority packet contract

Each accepted authority packet must use this shape:

```yaml
authority_packet:
  role: evidence-authority | soundness-authority | invariant-scope-authority | hazard-footgun-authority | complexity-remediation-authority | verification-authority | finding-skeptic
  packet_id: "..."
  artifact_state_id: "..."
  review_surface_id: "..."
  scoped_candidate_ids: ["..."]
  artifact_state_match: yes | no
  scope_match: yes | no
  clearance:
    candidate_id: clear | veto | unresolved | not-needed | not-in-scope
  vetoes:
    - id: "..."
      class: "..."
      claim: "..."
      evidence_ref: "..."
      required_to_clear: "..."
  positive_evidence:
    - id: "..."
      evidence_ref: "..."
      claim: "..."
  packet_status: accepted | rejected | root-equivalent
  reason: "..."
```

Reject packets that are stale, wrong-scope, wrong-artifact-state, acknowledgement-only, wrapper-leaking, generic, or lacking evidence refs. Rejected packets must not be used as clearance.

## Required input context

When possible, build this compact context pack before review:

```md
Review request:
- user goal:
- requested mode: Standard | Fast
- likely downstream workflow: none | validation | implementation | fixed-point-driver | resolve | ship | unknown
- explicit non-goals:
- proof bar:

Artifact state:
- artifact_state_id:
  - branch:
  - base:
  - head:
  - diff_digest:
  - review_surface_digest:
  - ci_state:

Review surface:
- review_surface_id:
- artifact set:
- changed files:
- nearby unchanged owners:
- tests/proof surfaces:
- PR/plan/issue direction:
- ownership boundaries:

Candidate inventory seed:
- prior findings or accepted agenda, if any:
- known review comments, if any:
- known stale or resolved items:
```

Do not feed the whole repository by default. Expand only when it can change grounding, ownership, soundness, hazard reachability, remediation breadth, verification path, or fixed-point judgment.

## Artifact State Ledger

Bind the review to current artifact state:

```yaml
artifact_state_id:
  branch: "<branch or unknown>"
  base: "<base sha/ref or unknown>"
  head: "<head sha/ref or unknown>"
  diff_digest: "<hash, path set, or unknown>"
  review_surface_digest: "<hash/list of reviewed paths or unknown>"
  ci_state: "<pass/fail/pending/not-run plus timestamp if known>"
```

If fields are unavailable, name what is unavailable and why. Unknown state is not proof.

## Review Surface Inventory

Emit a review surface inventory before findings:

```md
- artifact_state_id:
- review_surface_id:
- artifact_set:
- changed_files:
- nearby_files_checked:
- proof_surfaces_checked:
- direction_sources_checked:
- limits_or_unavailable_evidence:
```

## Candidate Finding Inventory

For every real review, preserve candidate coverage:

```md
- candidate_count:
- material_finding_count:
- non_finding_count:
- validation_item_count:
- proof_only_count:
- candidate_ids:
- material_finding_ids:
- non_finding_ids:
- validation_item_ids:
- proof_only_ids:
- missing_candidate_ids:
- duplicate_candidate_ids:
```

Candidate IDs may be assigned by the reviewer, but once assigned they must be stable across all ledgers.

## Finding eligibility rule

A candidate may appear in `Material Findings` only if all are true:

1. Current artifacts ground the candidate.
2. The candidate is material to correctness, safety, security, compatibility, preservation/progress, proof integrity, owned invariant, or a direction-critical goal.
3. The candidate is current for the artifact state.
4. The reviewed surface owns the issue or the issue is direction-overriding.
5. The strongest no-finding countercase is defeated.
6. The recommended remedy is the narrowest truthful fix, or the agenda explicitly selects validation-first.
7. The verification path is concrete.
8. Every required authority lane is `clear`, `defeated`, `mutate-now`, `validate-first`, or `not-needed` as appropriate.
9. No unresolved authority veto remains.
10. The finding has concrete `evidence_of_defect` and `evidence_of_remedy` or `validation_probe` refs.

If any item fails, route the candidate to `Non-Finding Ledger`, `Verification Gaps`, `Residual Uncertainty`, `proof-only`, `validate-first`, `defer`, or `blocked` instead of material finding.

## No-finding countercase pass

For every candidate, construct the strongest no-finding case before accepting it.

A no-finding case may be:

- unsupported by current artifacts
- stale or already fixed
- plausible but unreachable
- duplicate of a stronger boundary
- wrong owner or wrong layer
- outside this PR/task direction
- low-value or review-comfort-only
- finding is real but recommended fix is wrong or overbroad
- validation should precede mutation
- proof-only resolution is sufficient
- complexity cost exceeds material value

`Material Findings` require the no-finding case to be defeated. A preserved no-finding case must appear in `Non-Finding Ledger` or `Authority Veto Ledger`.

## Finding classes

Use exactly one per material finding:

- `current-owned-defect`
- `proof-surface-false-positive`
- `broken-soundness-obligation`
- `illegal-state-admitted`
- `hazardous-footgun`
- `compatibility-break`
- `security-safety-risk`
- `data-loss-risk`
- `verification-gap`
- `complexity-regression`
- `direction-mismatch`

## Agenda decisions

Use exactly one per candidate in the authority matrix and change agenda:

- `change-now`
- `validate-first`
- `proof-only`
- `defer`
- `no-finding`
- `blocked`

`change-now` is legal only for candidates with `authority_status: cleared-for-finding`.
`validate-first` is legal only for candidates with `authority_status: cleared-for-validation`.
`proof-only`, `defer`, `no-finding`, and `blocked` must not be converted into remediation work.

## Authority statuses

Use exactly one per candidate:

- `cleared-for-finding`
- `cleared-for-validation`
- `proof-only`
- `defer`
- `no-finding`
- `blocked`

A candidate with `authority_status: blocked`, `no-finding`, `defer`, or `proof-only` must not appear as `change-now`.

## Remediation posture values

Use exactly one per material finding or agenda item:

- `validating-check-only`
- `accretive-remediation`
- `structural-remediation`
- `proof-only`
- `no-change`
- `blocked`

Structural remediation requires a concrete explanation why a narrower accretive fix is insufficient.

## Fresh-eyes reread pass

Before finalizing Standard output, run a fresh independent pass. Treat first-pass findings as hypotheses.

Re-check:

- changed files and nearby unchanged owners
- stated goals and non-goals
- artifact state and review scope
- tests and proof signals
- authority packet coverage
- material findings and non-finding countercases
- complexity, invariant, foot-gun, and verification ledgers
- change-agenda consistency

Ask:

- What did the first pass assume without evidence?
- Which finding might be overstated, stale, or wrong-layer?
- Which candidate should be validate-first rather than change-now?
- Which recommendation broadens too far?
- Which non-finding was accidentally omitted?
- Which proof path is too vague to support downstream work?

Record the result in `Residual Uncertainty` and `Fixed-Point Judgment`. Do not invent findings to prove the pass happened.

## Required output contract

### Authority-Gated v1 / Standard

Use this section order for real reviews:

```md
## Review Basis
## Review Surface Inventory
## Candidate Finding Inventory
## Material Findings
| id | severity | finding class | claim | agenda decision | evidence of defect | evidence of remedy | confidence | minimum acceptable fix | do not broaden into | remediation posture |
|---|---|---|---|---|---|---|---|---|---|---|
## Finding Eligibility Tests
| id | grounded | material | current | ownership | remedy-shaped | verification-path | no-finding defeated | eligible | min evidence to change mind |
|---|---|---|---|---|---|---|---|---|---|
## Authority Packet Receipts
| role | packet status | artifact state match | scope match | candidates covered | finding added | veto added | used for | reason |
|---|---|---|---|---|---|---|---|---|
## Authority Clearance Matrix
| id | evidence | soundness | invariant/scope | hazard/footgun | complexity/remediation | verification | finding skeptic | authority status | packet refs |
|---|---|---|---|---|---|---|---|---|
## Authority Veto Ledger
| id | veto source | veto class | veto claim | evidence ref | required to clear | final route |
|---|---|---|---|---|---|---|
## Soundness Ledger
## Complexity Delta
## Invariant Ledger
## Foot-Gun Register
## Non-Finding Ledger
## Verification Gaps
## Residual Uncertainty
## Change Agenda
| id | agenda decision | change | proof or validation required | next | remediation posture |
|---|---|---|---|---|---|
## Acceptance Skew Audit
## All-Candidate Accepted Justification
## Fixed-Point Judgment
## Reviewer Gate
## Reviewer Bottom Line
```

Omit `All-Candidate Accepted Justification` only when at least one candidate is not selected as a material finding or validation item. Still include `Acceptance Skew Audit`.

### Fast

Fast output may compress prose but must still include:

- Candidate Finding Inventory
- Material Findings
- Finding Eligibility Tests
- Authority Clearance Matrix
- Authority Veto Ledger
- Non-Finding Ledger
- Change Agenda
- Reviewer Gate
- Reviewer Bottom Line

If authority coverage, inventory, evidence refs, or change-agenda consistency is incomplete, Fast mode must block remediation handoff.

## Reviewer Gate

Before downstream validation or implementation, emit `## Reviewer Gate`:

| field | value | basis |
|---|---|---|
| artifact_state_coverage | pass/fail |  |
| review_surface_coverage | pass/fail |  |
| candidate_inventory_coverage | pass/fail |  |
| finding_eligibility_coverage | pass/fail |  |
| authority_packet_coverage | pass/fail |  |
| authority_clearance_coverage | pass/fail |  |
| authority_veto_coverage | pass/fail |  |
| evidence_ref_coverage | pass/fail |  |
| non_finding_coverage | pass/fail |  |
| verification_path_coverage | pass/fail |  |
| change_agenda_consistency | pass/fail |  |
| acceptance_skew_audit | pass/fail |  |
| fixed_point_judgment_coverage | pass/fail |  |
| reviewer_complete | pass/fail |  |
| change_agenda_allowed | yes/no |  |
| implementation_handoff_allowed | yes/no | must be no for this skill |
| validation_handoff_allowed | yes/no |  |

`reviewer_complete` may be `pass` only when every required gate field above it passes. `implementation_handoff_allowed` must be `no`; this skill may create an agenda, but it does not implement.

If any required field fails, the bottom line must include:

```md
Blocked: incomplete adversarial review. Do not route remediation yet.
```

## Hard rules

- Do not implement fixes.
- Do not promote a guess to a material finding.
- Do not recommend structural remediation without proving why a narrower fix is insufficient.
- Do not let a clever invariant phrase substitute for reachability, ownership, and proof.
- Do not treat verification gaps as code defects when the correct route is validation-first.
- Do not collapse all candidates into material findings without structured all-candidate justification.
- Do not let `Change Agenda` include candidates whose authority status is `no-finding`, `proof-only`, `defer`, or `blocked`.
- Do not route remediation if the Reviewer Gate fails.
- Do not allow `implementation_handoff_allowed: yes`; downstream implementation belongs to `$fixed-point-driver` or `$accretive-implementer` after separate intake.
- Do not hide no-finding cases; preserved countercases must be visible.

## Machine-check hook

When automation is available, run:

```bash
python codex/skills/adversarial-reviewer/tools/adversarial_review_gate.py review.md
```

A failed checker means the review is incomplete. Re-run review with missing ledgers instead of routing remediation.

## Resources

- [authority-fanout.md](references/authority-fanout.md)
- [adversarial-review-gate-contract.md](references/adversarial-review-gate-contract.md)
- [adversarial-review-output-template.md](references/adversarial-review-output-template.md)
- [grading-rubrics.md](references/grading-rubrics.md)
- [example-invocations.md](references/example-invocations.md)
- [common-soundness.md](references/common-soundness.md)
- [common-ledgers.md](references/common-ledgers.md)
- [common-cli-reporting.md](references/common-cli-reporting.md)
