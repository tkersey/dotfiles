# Harness memory extension

Use this extension only during memory consolidation.

## What this source is

- This extension represents my evidence-backed harness guidance store.
- The canonical detailed records come from session-backed artifacts that capture guardrails, corrections, steering patterns, and interventions that improved coding-agent behavior or outcomes.
- Prefer `resources/harness_digest.md` as the primary input for this extension. Use raw per-session extracts only when the digest points to them or when the digest is missing a needed evidence detail.
- The raw evidence may come from mining prior Codex sessions (for example via my `seq` workflow), but this extension should consume the curated harness artifacts, not re-mine session history on its own.
- Never edit, append, or rewrite the underlying extracted session artifacts from the memory pipeline.

## Digest contract

When `resources/harness_digest.md` exists, treat it as the default consolidation source for this extension.

The digest should be optimized for memory consolidation, not for narrative reading. Favor compact structured markdown over prose.

### Expected digest shape

Use a structure close to this:

```md
# Harness digest

## Rollup
- generated_at:
- window:
- sessions_scanned:
- candidate_rules:
- repeated_themes:

## Promote now
### H-001 Short rule title
- normalized_rule:
- trigger:
- preferred_behavior:
- failure_avoided:
- verification_cue:
- scope: global | repo | path-family | task-family
- scope_anchor:
- target_hint: memory_summary | MEMORY | skill | none
- evidence_count:
- repetition_count:
- source_sessions:
- source_artifacts:
- rationale:
- confidence:

## Watchlist
### H-00x Short rule title
- why_not_yet:
- missing_evidence:
- next_confirmation_signal:

## Rejected / noise
### H-00y Short rule title
- rejection_reason:
```

The exact headings can vary, but every candidate rule should make the following explicit:

- the normalized reusable rule,
- the trigger or symptom that tells the future agent when to apply it,
- the preferred behavior,
- the failure mode it avoids,
- the verification cue or stop condition,
- the intended scope,
- the evidence strength.

### Candidate rule requirements

For each candidate, prefer fields with substance over verbose commentary:

- `normalized_rule`: one compact durable operating rule.
- `trigger`: what situation, smell, or request pattern activates the rule.
- `preferred_behavior`: what the agent should do.
- `failure_avoided`: what bad behavior, retry pattern, or correction this rule prevents.
- `verification_cue`: how to know the rule was applied correctly.
- `scope`: `global`, `repo`, `path-family`, or `task-family`.
- `scope_anchor`: repo slug, cwd fragment, path family, task family, or other retrieval anchor when needed.
- `target_hint`: best destination such as `memory_summary`, `MEMORY`, `skill`, or `none`.
- `evidence_count`: count of concrete supporting moments, not vague impressions.
- `repetition_count`: how often the same lesson recurred across distinct sessions.
- `source_sessions`: stable session identifiers.
- `source_artifacts`: links, filenames, or extract IDs that let the consolidator verify the claim.
- `rationale`: one short line on why the rule matters.
- `confidence`: `high`, `medium`, or `low` based on evidence quality.

### Digest authoring rules

- Separate `Promote now`, `Watchlist`, and `Rejected / noise` so the consolidator does not need to infer readiness from prose.
- Keep candidate titles short and retrieval-friendly.
- Prefer one rule per candidate. Split bundled advice into multiple candidates unless the parts are inseparable.
- Include just enough evidence metadata to verify the lesson later; do not paste long transcript excerpts.
- Quote exact wording only when the wording itself is the reusable asset.
- If a candidate is repo-specific, say so directly rather than letting it read as a global default.
- If the miner is unsure whether a lesson is durable, place it in `Watchlist` instead of overstating it.
- If a correction changed the trajectory but the underlying rule is still unclear, capture the failure pattern and missing evidence rather than forcing normalization.

### Preferred digest semantics

Interpret the digest as follows:

- `Promote now` means the miner believes the lesson is mature enough for memory consolidation.
- `Watchlist` means the pattern looks real but should usually stay out of memory until repetition or stronger evidence appears.
- `Rejected / noise` exists to document what was deliberately filtered out so the same weak signals are not repeatedly reconsidered.

When the digest and a raw extract disagree, prefer the raw extract only if it clearly shows the digest normalized the lesson incorrectly or dropped a crucial scope constraint.

## Goal

Distill durable harness knowledge into Codex memory.

Promote only information that will help future sessions:

- self-apply high-value guardrails before I have to restate them,
- choose the right operating mode, search pattern, or verification loop earlier,
- avoid recurring agent failure modes that previously triggered correction,
- preserve intervention patterns that reliably improved outcomes,
- route quickly to the right skill, artifact, or evidence source when a harness rule fires.

## What counts as harness signal

Treat the following as high-signal when evidence is concrete:

- direct user corrections about how the agent should operate, not just what it should build,
- guardrails that clearly changed a session trajectory for the better,
- reusable stop rules, escalation rules, and verification gates,
- constraints on search, planning, editing, testing, approvals, or output format,
- patterns where a failed first attempt was corrected by a more effective harness instruction,
- small behavioral defaults that recur and materially reduce retries or user steering.

Examples of the kind of rule worth preserving:

- `When the task is artifact-forensics, prefer session-backed proof over narrative recall.`
- `Inspect existing codepaths before inventing a new abstraction.`
- `Do not broaden scope; ship the minimal diff and verify it.`
- `When requirements are underspecified, produce a grounded first pass instead of stalling on clarification.`
- `For fast-changing or high-stakes facts, prefer official or primary sources first.`

## Promotion rules

Promote a harness learning into `MEMORY.md` or `memory_summary.md` only when at least one is true:

- the same steering theme appears repeatedly, especially across 2-3+ sessions,
- a direct correction clearly prevented or fixed a recurring failure mode,
- it captures a stable operating default rather than a one-off preference,
- it has a crisp trigger and an actionable preferred behavior,
- it would likely save future correction, retries, or wasted search/tool work,
- the normalized rule is reusable even after stripping away the original transcript wording.

Do not promote a correction merely because it happened once. Promote when the correction reveals a reusable operating rule.

## Signal weighting

- direct user corrections about agent behavior: highest priority,
- repeated harness prompts or reminders that consistently improved outcomes: high priority,
- post-hoc evidence from successful sessions showing that a specific guardrail mattered: high priority,
- one-off nudges with unclear reuse value: low priority,
- generic style requests or situational phrasing without durable behavioral content: do not promote on their own.

## Normalization rules

- Convert transcript-specific guidance into compact harness rules such as:
  - `When X, do Y before Z.`
  - `Avoid A; prefer B; verify with C.`
  - `If symptom S appears, stop and pivot to P.`
- Prefer behavior rules over prompt quotes. Quote only when the exact wording is itself the reusable asset.
- Separate the trigger, the desired behavior, the failure avoided, and the verification cue.
- Preserve only the minimum anchors needed for retrieval: repo slug, task family, exact failure string, tool, command, or artifact name when they materially help.
- Favor rules that a future agent can execute without reopening the original session.

## Scope rules

- Keep truly cross-repo harness defaults global.
- Keep repo-specific or task-family-specific harness guidance scoped with repo, cwd, path-family, or task cues.
- Do not let one repo's steering pattern become a global default unless the evidence clearly generalizes.
- When similar rules exist at multiple scopes, prefer the narrower scope in `MEMORY.md` and keep only the compact routing/default layer in `memory_summary.md`.

## Conflict rules

- Prefer newer evidence over older evidence when rules conflict.
- Prefer explicit user corrections over inferred harness lessons.
- Prefer stable operating defaults over one-session success anecdotes.
- When two rules are both valid but apply in different contexts, preserve both with sharp trigger cues instead of merging them into a vague compromise.

## Compression rules

- Summarize; do not copy transcript blocks, raw prompts, or long tool outputs.
- Do not preserve scolding, frustration, or conversational filler; preserve the operational rule underneath.
- Keep the memory focused on reusable harness behavior, not narrative chronology.
- Because `memory_summary.md` is always loaded, keep global harness notes especially terse and high-signal.
- If the rule cannot be stated concisely enough to be routable, it likely belongs in a richer `MEMORY.md` note or a skill, not in the summary.

## Artifact targeting

- Put small global defaults, trigger phrases, and routing rules in `memory_summary.md`.
- Put richer harness playbooks, failure shields, escalation ladders, and verification discipline in `MEMORY.md`.
- Create or update `skills/*` only when the harness guidance has become a repeatable operating procedure with:
  - clear trigger cues,
  - a compact ordered workflow,
  - a proven verification checklist,
  - evidence that it reliably improves outcomes.

## Skill threshold

Create or update a skill only when the harness lesson is more than "remember this preference" and is instead a reusable runbook, such as:

- how to triage a session before editing,
- how to verify a fix with the minimum decisive checks,
- how to do artifact-backed forensics,
- how to route between plan, spec, implementation, and review modes.

If the lesson is a default or failure shield rather than a full procedure, keep it as a concise `MEMORY.md` note instead of a skill.

## Non-goals

Do not use this extension to:

- duplicate the session transcript,
- store one-off reprimands or tone adjustments without operational value,
- preserve transient branch or session state,
- promote vague advice like `be more careful` or `reason better`,
- overfit to one project's local quirks as global harness policy,
- scan unrelated session history just to increase coverage.

If there is no meaningful durable harness signal, make no memory change.
