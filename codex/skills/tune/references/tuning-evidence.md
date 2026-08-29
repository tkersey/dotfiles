# Tuning evidence

Load this reference only when `$tune` needs to diagnose intended-versus-observed
behavior, reconstruct historical use, or separate attribution from outcome.

## Source classes

### Current

Evidence visible in the active interaction: user feedback, prompt wording,
assistant behavior, current tool output, and observed worktree behavior.

Useful for immediate routing and narrow correction. It does not prove recurrence
or historical rates.

### Provided

User-supplied reports, logs, transcripts, screenshots, diffs, or observed output.

Preserve provenance and selection limits. Provided evidence may be stale,
partial, or missing counterevidence.

### Historical

Prior sessions and tool traces. Use Seq as the passive adapter.

Historical evidence can establish recurrence, missed or false activation, and
repeated workarounds. It requires a bounded selector set and cannot turn
co-occurrence into causality.

### Worktree

The current skill package, Git state, and validation output.

Worktree evidence is required for mutation and publication, but package text
alone does not prove user-facing behavior.

### Mixed

Use when current or provided evidence must be combined with history or worktree
proof. Keep each source's limits separate before synthesis.

Record:

```text
kind
locator
scope and window
access method
denominator
privacy constraint
what the source establishes
what it cannot establish
```

## Evidence strength

Use the strongest available class without collapsing weaker evidence into it:

```text
1. structured decision receipt tied to the target contract
2. explicit statement tying the skill to a decision
3. explicit skill use plus a contract-aligned route
4. skill use plus downstream outcome without route attribution
5. co-occurrence or raw mention
```

Only levels 1 and 2 strongly establish a skill-caused decision delta. Levels 3
and 4 support alignment or association. Level 5 is candidate evidence only.

Decision-effect classes:

```text
explicit-route-change | prevented-action | narrowed-scope
added-or-changed-proof | escalated-or-blocked | reinforced-existing-choice
no-visible-delta | contrary-to-contract | trigger-missed
false-activation | ceremonial-activation | unknown
```

Ceremonial activation means the skill was loaded or declared but exercised no
consequential clause and changed no route, scope, proof, or lifecycle state.
Ceremony becomes a tuning gap only when recurrent or materially costly.

## Canonical Seq observation

Before the first native Ledger command in a workflow, load `$ledger` and complete
its ensure step once.

Historical or multi-session evidence:

```bash
seq observe \
  --definition <tune-skill-root>/definitions/seq/skill-decision-audit.json \
  --projection evidence \
  --root <sessions-root> \
  --last <duration> \
  --repo <repo> \
  --param exclude_session_id=<current-session-id> \
  --param needle=<skill> \
  --format json

seq observe \
  --definition <tune-skill-root>/definitions/seq/skill-decision-audit.json \
  --projection tools \
  --root <sessions-root> \
  --last <duration> \
  --repo <repo> \
  --param exclude_session_id=<current-session-id> \
  --param needle=<skill-or-tool-pattern> \
  --format json
```

One watched session:

```bash
seq observe \
  --definition <tune-skill-root>/definitions/seq/skill-decision-audit.json \
  --projection evidence \
  --root <sessions-root> \
  --session-id <session> \
  --param needle=<skill> \
  --format json
```

Use `--repo`, `--since`, `--until`, `--last`, or explicit sessions only when the
question requires them. Record the exact selector set. Do not silently replace
an arbitrary-history request with a default recent window.

For root scans, bind `exclude_session_id` to the current `CODEX_THREAD_ID` so the
audit cannot count its own prompt or invocation. Treat returned rows as
candidates until Tune classifies user activation, assistant declaration,
injected skill text, skill-file read, decision receipt, route statement,
outcome, and raw mention.

The default `tools` projection excludes raw payloads. Use `tools-raw` only when
the user explicitly requests raw tool payloads and the selected evidence is safe
to disclose.

Use stable `source_event_id`, session, path, line, and turn fields as provenance.
Use narrow physical follow-ups only for a specific unresolved question, such as
session detail, turn boundaries, tool lifecycle, or session graph.

When a recurring observation is missing, change the owning passive definition.
Request a native Seq operator only when the operation is genuinely
domain-independent and cannot be expressed with equivalent bounds.

## Episode analysis

For each material episode preserve:

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

Do not infer alternatives that were never observed. Do not count a later
successful session as proof that the skill caused success.

Before selecting a change, ask:

- Would the observed action plausibly have happened without the skill?
- Did the skill alter the route or merely describe it?
- Did compliance improve the outcome?
- Did missed activation cause the failure?
- Does another skill own the effect?
- What denominator and counterexamples constrain the claim?

If sources disagree, report the conflict. Prefer inspection or a narrow,
reversible intervention unless current evidence is independently dispositive.
