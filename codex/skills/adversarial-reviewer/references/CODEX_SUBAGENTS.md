# Specialist Workers for Adversarial Reviewer

Use the version-neutral worker model in `../../references/codex-specialist-worker-model.md`. Do not depend on one runtime's subagent invocation syntax or install path.

Recommended repository workers under `codex/agents/`:

| Role | Worker |
|---|---|
| evidence authority | `adv_review_evidence_authority` |
| soundness authority | `adv_review_soundness_authority` |
| invariant/scope authority | `adv_review_invariant_scope_authority` |
| hazard/foot-gun authority | `adv_review_hazard_footgun_authority` |
| complexity/remediation authority | `adv_review_complexity_remediation_authority` |
| verification authority | `adv_review_verification_authority` |
| no-finding advocate | `adv_review_finding_skeptic` |

If worker execution is unavailable, the root may emit same-schema authority packets for narrow reviews. Broad or implementation-bound reviews should block handoff when required authority coverage is missing.
