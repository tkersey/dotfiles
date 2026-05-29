# Codex custom subagents for adversarial-reviewer

Codex discovers custom agents from:

- project agents: `.codex/agents/*.toml`
- user agents: `$HOME/.codex/agents/*.toml`

This drop-in package places agents under `codex/agents/` because this dotfiles repo symlinks `codex/agents` to `$HOME/.codex/agents`.

Available agents:

| Role | Agent |
|---|---|
| evidence authority | `adv_review_evidence_authority` |
| soundness authority | `adv_review_soundness_authority` |
| invariant/scope authority | `adv_review_invariant_scope_authority` |
| hazard/foot-gun authority | `adv_review_hazard_footgun_authority` |
| complexity/remediation authority | `adv_review_complexity_remediation_authority` |
| verification authority | `adv_review_verification_authority` |
| no-finding advocate | `adv_review_finding_skeptic` |

If custom agents are unavailable, the parent may emit root-equivalent authority packets for narrow reviews. Broad or implementation-bound reviews should block handoff when required authority coverage is missing.
