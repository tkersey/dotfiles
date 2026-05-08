# Auto Evidence Examples

Use these examples when classifying evidence for autonomous skill maintenance.

`auto` may propose or perform an autonomous optimization only for an ordinary, non-protected skill and only when at least one strong evidence class is present. Weak-only evidence is inventory, not authorization.

## Strong evidence classes

### `repeated_session_evidence`

Accept when multiple independent sessions show the same skill failure, routing gap, validation issue, or repeated workaround.

Good summary:

```text
repeated_session_evidence: In 4 sessions over 14 days, agents invoked $latent-diver for final selection even when the task required choosing among concrete candidates; two finals then handed off to accretive without dominance-style comparison.
```

Why accepted:

- repeated
- skill-specific
- behavior-specific
- no raw transcript text
- no private paths or user-identifying details

Reject:

```text
The user seemed annoyed in a private session and the transcript said "...".
```

Reason: raw transcript/private affect is not an acceptable summary.

### `explicit_user_feedback`

Accept when the user directly says a skill behavior is wrong, missing, too heavy, too light, confusing, or useful enough to codify.

Good summary:

```text
explicit_user_feedback: User asked for all must-have skill improvements rather than only top-three priorities, indicating previous output underfit the requested coverage and should preserve complete change sets.
```

Reject:

```text
User probably wanted X.
```

Reason: inference is not explicit feedback.

### `clear_validation_failure`

Accept when a command, validator, smoke test, loader, or self-check fails in a way tied to the skill.

Good summary:

```text
clear_validation_failure: quick_validate rejected codex/skills/example/SKILL.md because frontmatter lacked a closing --- delimiter; repairing frontmatter made the target validator pass.
```

Reject:

```text
The skill feels invalid.
```

Reason: no concrete validation proof.

### `clear_routing_failure`

Accept when a task routed to the wrong skill, failed to route to the right skill, or invoked a heavyweight workflow without sufficient trigger.

Good summary:

```text
clear_routing_failure: Absolute-claim verification request invoked ordinary verification instead of prove-it despite explicit "prove it" cue; final verdict was returned before the ten-round gauntlet.
```

Reject:

```text
Routing overlap exists between kan and ADD.
```

Reason: overlap alone is weak unless a concrete failure is observed.

## Weak evidence classes

Weak evidence may justify a TODO, human review, or manual refinement, but not autonomous optimization alone.

### `thin_usage_signal`

A skill is rarely used or frequently mentioned without enough context to prove a problem.

### `stale_metadata_signal`

Metadata looks old, incomplete, or mismatched, but no behavior failure has been observed.

### `trigger_overlap_signal`

Two skills have adjacent trigger language, but no actual misroute has been observed.

### `workflow_ambiguity_signal`

A workflow has ambiguous stages, but there is no concrete failed handoff or user complaint.

### `missing_validation_guidance`

A skill lacks explicit validation instructions, but no validation failure has occurred yet.

## Reject classes

Do not optimize autonomously when any of these is the only evidence:

- raw transcript excerpts
- raw memory text
- secrets or credentials
- sensitive local paths
- user-identifying private path fragments
- one-off vibes or style preference
- broad "improve this skill" with no target behavior
- protected target skill
- changes outside the target skill directory
- stale branch or stale bootstrap policy
- ambiguous evidence class
- evidence that requires product, legal, security, medical, or financial owner judgment

## Sanitized summary pattern

Use:

```text
<evidence_class>: <count/time/scope if available>; <observed behavior>; <skill-specific consequence>; <safe candidate improvement>.
```

Example:

```text
clear_routing_failure: 2 recent repo-opportunity prompts routed to latent-diver and produced creative frames without repository evidence; ideate should own repo-mined opportunity portfolios, while latent-diver should only support non-obvious frame exploration.
```

## PR body evidence pattern

Use compact, non-sensitive proof:

```text
Evidence:
- class: clear_routing_failure
- summary: Repo-opportunity prompts produced non-evidence-backed frame packets instead of an opportunity portfolio.
- target skill: ideate
- protected skill touched: no
- validation: corpus validator passed; target skill frontmatter valid.
```

Do not include:

- raw session lines
- private working directories
- secrets
- exact local usernames
- copied memory bodies
- screenshots
- unrelated diff summaries
