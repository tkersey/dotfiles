---
name: beads
description: bd (beads) issue-tracking workflow; use when `.beads/` exists or when running `bd` commands.
---

# Beads

## When to use
- A `.beads/` directory exists.
  - If unsure: `rg --files -g '.beads/**' --hidden --no-ignore`.
- The user asks for `bd` commands (`bd ready`, `bd create`, `bd close`, `bd sync`, …).
- The user wants beads to act as a **work ledger** (plan/progress/decisions recorded during implementation).

## Principle: bead as work ledger
- The active bead is the canonical place for **plan**, **progress**, **decisions**, and **verification**.
- Prefer recording facts into the bead over long chat narration; the bead must survive session resets.

## Molecules (workflow steps as beads)
A molecule is how beads turns “do this work” into a durable, stepwise workflow.

- **Formula**: workflow source file (discover via `bd formula list`).
- **Proto**: cooked template epic (solid phase).
- **Mol**: persistent instantiation of a proto (liquid phase) created by `bd mol pour`.
- **Wisp**: ephemeral instantiation (vapor phase) created by `bd mol wisp`.

In a mol, each step is a real bead, so “log per step” becomes natural.

## Per-step ledger contract (mol step beads)
For each step bead you complete:
1. Ensure `notes` has current Now/Next/Blockers/Verify.
2. Add exactly one Markdown **ChangeLog** comment (template below).
3. Close the step with an outcome-focused reason.

Recommended close reason:
- `bd close <step-id> --reason "Implemented: <one-line behavioral outcome>"`

## Workflow loop (implementation-aware)
1. Prime context: `bd prime`.
2. Pick the work:
   - `bd ready` (general)
   - `bd ready --mol <mol-id>` (within a molecule)
   - `bd mol current <mol-id>` (where am I in this molecule?)
   Then `bd show <id>`.
3. Start/claim: `bd update <id> --claim` (or `bd update <id> --status in_progress`).
4. Seed a mini-plan (rolling):
   - `bd update <id> --notes "$(cat <<'EOF'
## Status
- Now: …
- Next: …
- Blockers: …

## Verification
- [ ] <exact command>  # expected: <signal>
EOF
)"`
5. Implement in small slices; after each slice, add a durable log entry:
   - `bd comments add <id> "…"`
   - Update `--design` when you make a real decision.
   - Update `--acceptance` when you learn/clarify verification.
6. Close with an outcome-focused reason: `bd close <id> --reason "…"`.
7. Sync when appropriate: `bd sync`.

## What to record during implementation

### `notes` (rolling status board)
- Keep **short** and **current**; overwrite freely.
- Best for: Now/Next/Done, blockers, the current verification command(s).

### Comments (append-only timeline)
- Use comments for incremental planning and “what changed” snapshots.
- Recommended comment types:
  - **Checkpoint**: what you just did + next.
  - **Decision**: decision + rationale + alternatives.
  - **Patch summary**: paths changed + the behavioral delta.
  - **Verification**: command(s) run + success/failure signal.
  - **Handoff**: current state + what to do next.

Example:
```bash
bd comments add bd-123 "$(cat <<'EOF'
Checkpoint: tighten parser guardrails
- Changed: src/foo.rs (parse), src/foo_test.rs (cases)
- Decision: reject empty input early
- Verify: cargo test -p foo  # pass
EOF
)"
```

### `design` (durable decisions)
- Keep longer-lived architecture notes here so they don’t get lost in the scrollback.
- Update when a decision is made:
  - `bd update <id> --design "$(cat <<'EOF'
## Decisions
- …

## Alternatives
- …

## Invariants / gotchas
- …
EOF
)"`

### Discoveries (scope control)
- File newly discovered work as new beads, don’t silently expand scope.
  - `bd create "..." --type=task --priority=2`
- Link it back so it’s traceable:
  - `bd dep add <new-issue> <current-issue> -t discovered-from`

## Alternate uses (beyond tickets)

### Encode “what changed” without pasting diffs
- After any meaningful slice (or before handoff/close), add a **ChangeLog** comment.
- Goal: a new session can answer “what changed?” and “what’s left?” in 30 seconds.

Template (Markdown-only, high-signal, no diffs):
```bash
bd comments add <id> "$(cat <<'EOF'
ChangeLog
- Intent: <what this step was trying to accomplish>
- Files: <paths, short list>
- Behavior: <what is now true / user-visible change>
- Risk: <regressions to watch>
- Verify: <exact command>  # <pass/fail>
- Next: <next concrete action>
EOF
)"
```

Optional add-ons when they exist:
- `Commit: <sha>`
- `PR: <url>`

### Beads as agents (first-class workers)
Gas Town treats agents as beads so liveness/state is queryable and durable. You can adopt this pattern in any repo that uses beads.

**Conventions (so you can find these across repos):**
- Create one agent bead per durable identity.
- Always set labels that make lookup easy:
  - `agent` (broad)
  - `agent:<name>` (stable lookup key)
  - `role:<role>` (polecat/crew/witness/refinery/mayor/deacon)

Create:
```bash
bd create --type=agent --role-type=polecat --agent-rig <rig> \
  --labels agent,agent:<name>,role:polecat \
  --title "<name>"
```

Find later:
- `bd list --label agent:<name> --all`
- `bd search "agent:<name>"`

As the agent works, keep its state current:
- `bd agent state <agent-id> working|stuck|done`
- `bd agent heartbeat <agent-id>`

Track orthogonal operational dimensions (creates an event + caches label):
- `bd set-state <agent-id> health=healthy|failing --reason "..."`
- `bd set-state <agent-id> mode=normal|degraded --reason "..."`

Monitor progress across agents/issues in real time:
- `bd activity --follow` (add `--town` if you use routing)

## Command quick reference
- `bd prime` — load AI-optimized workflow context.
- `bd ready` — list unblocked work.
- `bd show <id>` — inspect issue details.
- `bd create "Title" --type=task --priority=2` — create a new issue.
- `bd update <id> --claim` — atomically claim and start work.
- `bd update <id> --notes ...` — update rolling status/plan.
- `bd comments add <id> ...` — append progress log entries.
- `bd update <id> --design ...` — update durable decisions.
- `bd update <id> --acceptance ...` — keep verification criteria correct.
- `bd dep add <id> <depends-on> -t discovered-from|blocks|tracks|related|...` — link issues.
- `bd lint [id...]` — check missing template sections.
- `bd set-state <id> <dimension>=<value> --reason "..."` — event + cached label state.
- `bd agent state <agent-id> <state>` — update agent state + last_activity.
- `bd agent heartbeat <agent-id>` — update last_activity only.
- `bd activity --follow` — watch live progress.
- `bd close <id> --reason "..."` — close with outcome + signal.
- `bd sync` — sync beads with git remote (typically end of session).

## Safety notes
- `bd hooks install`, `bd init`, `bd config set ...`, and `bd sync` mutate the repo (and/or git history); ask first unless explicitly requested.
