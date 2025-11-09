# Repository Guidelines

## beads Agent Directive

All task coordination flows through `bd`; consult the quick-start below before kicking off new work.

## Issue Tracking with bd (beads)

**IMPORTANT**: This project uses **bd (beads)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

### Why bd?

- Dependency-aware: Track blockers and relationships between issues
- Git-friendly: Auto-syncs to JSONL for version control
- Agent-optimized: JSON output, ready work detection, discovered-from links
- Prevents duplicate tracking systems and confusion

### Quick Start

**Check for ready work:**
```bash
bd ready --json
```

**Create new issues:**
```bash
bd create "Issue title" -t bug|feature|task -p 0-4 --json
bd create "Issue title" -p 1 --deps discovered-from:bd-123 --json
```

**Claim and update:**
```bash
bd update bd-42 --status in_progress --json
bd update bd-42 --priority 1 --json
```

**Complete work:**
```bash
bd close bd-42 --reason "Completed" --json
```

### Issue Types

- `bug` - Something broken
- `feature` - New functionality
- `task` - Work item (tests, docs, refactoring)
- `epic` - Large feature with subtasks
- `chore` - Maintenance (dependencies, tooling)

### Priorities

- `0` - Critical (security, data loss, broken builds)
- `1` - High (major features, important bugs)
- `2` - Medium (default, nice-to-have)
- `3` - Low (polish, optimization)
- `4` - Backlog (future ideas)

### Workflow for AI Agents

1. **Check ready work**: `bd ready` shows unblocked issues
2. **Claim your task**: `bd update <id> --status in_progress`
3. **Work on it**: Implement, test, document
4. **Discover new work?** Create linked issue:
   - `bd create "Found bug" -p 1 --deps discovered-from:<parent-id>`
5. **Complete**: `bd close <id> --reason "Done"`
6. **Commit together**: Always commit the `.beads/issues.jsonl` file together with the code changes so issue state stays in sync with code state

### Auto-Sync

bd automatically syncs with git:
- Exports to `.beads/issues.jsonl` after changes (5s debounce)
- Imports from JSONL when newer (e.g., after `git pull`)
- No manual export/import needed!

### bd Daemon

Always launch the background service with:
```bash
bd daemon start --auto-commit --auto-push
```
Keep it running for the entire session so bd can commit and push issue updates automatically. Restart the daemon immediately if it stops or after switching branches.

### bd Configuration

Confirm the repository syncs metadata to the dedicated branch:
```bash
bd config get sync.branch
```
This must output `beads-metadata`. If it is unset or different, fix it immediately:
```bash
bd config set sync.branch beads-metadata --json
```

### JSONL Conflict Playbook

- Treat `.beads/issues.jsonl` as generated output; when conflicts or manual edits appear, re-export from the database (`bd export -o .beads/issues.jsonl`) instead of hand-editing.
- After any `bd` mutation, wait for the auto-export (or run `bd export -o .beads/issues.jsonl`) and commit the refreshed file with the related code so export hashes stay in sync across machines.
- If bd raises a hash mismatch or similar warning, run `bd validate` to surface drift, resolve findings, and re-export before pulling or pushing more changes.

### MCP Server (Recommended)

If using Claude or MCP-compatible clients, install the beads MCP server:

```bash
pip install beads-mcp
```

Add to MCP config (e.g., `~/.config/claude/config.json`):
```json
{
  "beads": {
    "command": "beads-mcp",
    "args": []
  }
}
```

Then use `mcp__beads__*` functions instead of CLI commands.

### Managing AI-Generated Planning Documents

AI assistants often create planning and design documents during development:
- PLAN.md, IMPLEMENTATION.md, ARCHITECTURE.md
- DESIGN.md, CODEBASE_SUMMARY.md, INTEGRATION_PLAN.md
- TESTING_GUIDE.md, TECHNICAL_DESIGN.md, and similar files

**Best Practice: Use a dedicated directory for these ephemeral files**

**Recommended approach:**
- Create a `history/` directory in the project root
- Store ALL AI-generated planning/design docs in `history/`
- Keep the repository root clean and focused on permanent project files
- Only access `history/` when explicitly asked to review past planning

**Example .gitignore entry (optional):**
```
# AI planning documents (ephemeral)
history/
```

**Benefits:**
- ✅ Clean repository root
- ✅ Clear separation between ephemeral and permanent documentation
- ✅ Easy to exclude from version control if desired
- ✅ Preserves planning history for archeological research
- ✅ Reduces noise when browsing the project

### Important Rules

- ✅ Use bd for ALL task tracking
- ✅ Always use `--json` flag for programmatic use
- ✅ Link discovered work with `discovered-from` dependencies
- ✅ Check `bd ready` before asking "what should I work on?"
- ✅ Store AI planning docs in `history/` directory
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use external issue trackers
- ❌ Do NOT duplicate tracking systems
- ❌ Do NOT clutter repo root with planning documents

For more details, see README.md and QUICKSTART.md.

### Review Loop Autopilot

- **Trigger phrase:** `revloop`
- **When to use:** The user has initiated `/review` on recently delivered work and then says `revloop`.
- **What to do:**
  1. **Wrap the reviewed work:** Address every review comment, close the active bead, pull the next highest-priority ready bead with `bd`, mark it `in_progress`, commit any follow-up changes, update the PR, monitor checks, squash-merge once green, then `git checkout v2`, `git fetch`, and `git reset --hard origin/v2` if the local branch lags.
  2. **Push the new bead forward:** Begin executing the newly claimed bead immediately, following any explicit next steps already on record.
  3. **Spin up the next delivery:** After honoring prior next-step suggestions, run the full test/lint/format/typecheck suite (skip only if it just ran), branch from a fresh topic branch for this bead, create and monitor the PR until it is green, and notify the user that it is ready for review.

## Tooling Standards

### GIT

- **Important:** Prefix both `git merge --continue` and `git rebase --continue` with `GIT_EDITOR=true` (for example, `GIT_EDITOR=true git merge --continue`) so the commands finish without waiting on an editor.

### GitHub CLI (gh)

`gh` is the expected interface for all GitHub work in this repo—authenticate once and keep everything else in the terminal.

- **Authenticate first**: run `gh auth login`, pick GitHub.com, select HTTPS, and choose the `ssh` protocol when asked about git operations. The device-code flow is quickest; once complete, `gh auth status` should report that both API and git hosts are logged in.
- **Clone and fetch**: `gh repo clone owner/repo` pulls a repository and configures the upstream remote; `gh repo view --web` opens the project page if you need to double-check settings.
- **Pull requests**: use `gh pr list --state open --assignee @me` to see your queue, `gh pr checkout <number>` to grab a branch, and `gh pr create --fill` (or `--web`) when opening a PR. Add reviewers with `gh pr edit <number> --add-reviewer user1,user2` instead of touching the browser.
- **Issues**: `gh issue status` shows what’s assigned to you, `gh issue list --label bug --state open` filters the backlog, and `gh issue view <number> --web` jumps to the canonical discussion when you need extra context.
- **Actions**: `gh run list` surfaces recent CI runs, while `gh run watch <run-id>` streams logs so you can keep an eye on builds without leaving the shell.
- **Quality-of-life tips**: install shell completion via `gh alias list`/`gh alias set` for shortcuts, and keep the CLI updated with `gh extension upgrade --all && gh update` so new subcommands (like merge queue support) are always available.
- **Gists**: list existing snippets with `gh gist list`, inspect contents using `gh gist view <id> --files` or `--filename <name>`, and update a gist file by supplying a local path via `gh gist edit <id> --add path/to/file`. Use `--filename` when you need to edit inline.

### Python

- **Use uv for everything**: favor `uv` over `python`, `pip`, or `venv` directly. `uv run …` executes scripts and tools inside the pinned Python environment, while `uv pip install` handles dependency changes and keeps lockfiles consistent.
- **Fast setup**: `uv sync` (or `uv init` for new projects) will resolve, lock, and install dependencies in one pass using uv’s resolver and cache. Skip `pip install -r requirements.txt`.
- **Tooling parity**: wrap test and lint invocations with `uv run`, e.g., `uv run pytest`, `uv run ruff check`, so contributors share the same interpreter and dependency graph.
- **Shebang helper**: when creating automation, prefer `#!/usr/bin/env uv run python` to ensure scripts execute with the managed toolchain.
- **Stay updated**: periodically run `uv self update` to pick up performance and compatibility fixes from Astral.

## Disciplines

### Complexity Mitigator

When the work feels tangled, step into the Complexity Mitigator mindset: keep essential complexity, vaporize the incidental.

- **Engage when:** a review stalls because readers can’t follow the flow, you spot >3 nested blocks or duplicated branching, or progress depends on mentally simulating state across files.
- **Immediate scan:** run a quick cognitive heat read—call out nesting depth, branch count, and cross-file hops. Identify what complexity is essential domain logic versus incidental implementation noise before recommending changes.
- **Standard playbook:** lead with guard clauses, split mixed responsibilities, convert boolean soups into data structures, and honor the Rule of Three before extracting abstractions. Sequence work as flatten → rename → extract.
- **Deliverable:** respond with (1) essential vs incidental verdict, (2) simplification options ranked by effort vs impact, (3) a short code sketch that illustrates the better structure, and (4) which TRACE letters were satisfied or violated.
- **Cross-coordination:** if missing invariants block simplification, tap the invariant guidance below; if confusing APIs are the root cause, incorporate the Footgun checklist before finalizing.

### Creative Problem Solver

When the team is stuck or wants fresh angles, adopt the Creative Problem Solver discipline.

- **Engage when:** experiments keep failing in the same way, stakeholders ask for new ideas, or integration work blocks because every attempt replays the same constraints.
- **Mode check:** stay in Pragmatic Mode (ship-this-week options) by default. Switch to Visionary Mode only when the user asks for long-term strategy or the problem is clearly systemic.
- **Playbook:** (1) name why current tactics fail in a single sentence, (2) reframe the constraint using inversion/analogy/first principles to expose new levers, (3) propose a portfolio of **Quick Win**, **Strategic Play**, and **Transformative Move**, each with a concrete 24-hour experiment and an escape hatch.
- **Deliverable:** end with an `Insights Summary` that always lists tactical next steps; add visionary insights only when you intentionally switched modes. Offer the “Want the 10-year vision?” prompt when appropriate.
- **Cross-coordination:** if a new tool is required, bring in the Provisioner guidance; if the problem is tangled implementation, apply the Complexity Mitigator checklist first.

#### Creative Tactics

- **Stuckness signals:** flag repeated failures, constraint walls (“can’t with current resources”), or circular debates early so creativity starts before fatigue sets in.
- **Reframing toolkit:** reach for inversion, analogy transfer, constraint extremes, and first-principles decomposition to surface levers conventional iteration misses.
- **Portfolio rule:** every response ships a Quick Win, Strategic Play, and Transformative Move, each paired with a 24-hour experiment and an explicit escape hatch.
- **Response choreography:** open by naming why the old approach fails and the insight that reframes it; close with an Insights Summary that always lists tactical actions, adds visionary moves only when long-horizon triggers appear, and invites “Want the 10-year vision?” when warranted.

### Invariant Ace

Slip into the Invariant Ace discipline whenever state validity feels shaky.

- **Engage when:** bugs trace back to unexpected nulls, runtime validators clutter hot paths, or reviewers flag that business rules live only in comments or tests.
- **Immediate scan:** name the invariant at risk and tag the current protection level (hope-based → runtime → construction-time → compile-time). Capture the concrete failure that could happen today.
- **Standard playbook:** swap validators for parsers that refine types, make illegal states unrepresentable via tagged unions or typestates, introduce smart constructors/phantom types for constrained values, and reinforce with property tests or proofs when stakes are high.
- **Deliverable:** explain (1) the risk scenario, (2) the stronger invariant and how it climbs the hierarchy, (3) a before/after code sketch highlighting the refined type, and (4) the verification you ran or recommend.
- **Cross-coordination:** lean on the Unsoundness checklist if broader failures emerge and reference the Footgun guardrails when stronger invariants might dent ergonomics.

### Logophile

Use the Logophile lens when text needs to say more with fewer words.

- **Engage when:** teammates struggle to parse directions, reviews note redundant phrasing, or you feel the draft drifting into filler rather than meaning.
- **Immediate diagnosis:** classify the text type (prompt, doc, email, spec), audience, tone, and the optimization goal (clarity, brevity, eloquence) before touching the draft.
- **Standard playbook:** apply the Enhanced Semantic Density Doctrine—swap generic phrases for precise vocabulary, collapse redundant clauses, keep euphony, and respect TRACE so the rewrite stays readable in under 30 seconds.
- **Deliverable:** share the refined passage, followed by the key edits you made (lexical lift, structural tightening, rhetorical tweak). When trimming >20%, explicitly note how you preserved meaning.
- **Cross-coordination:** check the relevant technical guidance (e.g., invariants, complexity) if accuracy depends on another domain before finalizing.

### Enhanced Semantic Density Doctrine (E-SDD)

> Precision through sophistication, brevity through vocabulary, clarity through structure, eloquence through erudition.

E-SDD is the Logophile's operating system: every edit must increase semantic weight while keeping language graceful. Anchor rewrites in four pillars:

- **Lexical elevation:** choose words that are both exact and euphonic; retire vague fillers.
- **Euphonic architecture:** shape sentences that sound intentional when read aloud, avoiding clunky rhythm.
- **Rhetorical sophistication:** deploy devices (parallelism, chiasmus, anaphora) when they sharpen persuasion or memorability.
- **Erudite precision:** surface domain insight without obscuring meaning; sophistication never compromises legibility.

Guardrails:

- Stay TRACE-compliant: keep the optimized text type-first, readable in 30 seconds, atomic, cognitively light, and strictly essential.
- Keep the Surgeon's Principle in mind—minimal incision, maximum precision. Cut fluff; preserve indispensable nuance.
- Offer metrics (word delta, readability shifts) when stakeholders need proof that density improved alongside clarity.

### TRACE

Invoke TRACE when you’re judging code quality through the Type-Readability-Atomic-Cognitive-Essential lens.

- **Engage when:** you’re reviewing a change, someone flags readability or cognitive load concerns, or the codebase shows signs of “what is this?” surprises.
- **Runbook:** (1) sketch a cognitive heat map with hotspots (🔥 vs ⚪) and log surprise events (misleading names, hidden side effects, sneaky complexity), (2) walk the TRACE checklist explicitly—Type-first, Readability in 30 seconds, Atomic scope, Cognitive budget, Essential-only—marking pass/fail, (3) monitor scope creep and call for new work items when fixes sprawl.
- **Deliverable:** report findings in severity order with file:line references, annotating each with the violated TRACE letters and a surgical fix; close with residual risks or required follow-up tests.
- **Cross-coordination:** pull in the Complexity playbook for structural rewrites, the Invariant guidance for type gaps, and the Unsoundness checklist when you pinpoint crashes.

#### TRACE Precision Playbook

- **Heat map legend:** Annotate friction inline—⚪⚪⚪ smooth flow, 🟡🟡⚪ pause-and-think, 🔥🔥🔥 mental compile—and refactor until only indispensable hotspots remain.
- **Surprise index triggers:** Record expectation breaks when names lie, return types surprise, hidden side effects surface, complexity spikes, or type assertions dodge guards.
- **Scope guardrails:** Trigger the scope creep alarm as soon as a surgical fix drifts; quarantine broader refactors so the primary branch stays minimal-incision.
- **Report essentials:** Summaries should surface TRACE grades, surprise index, debt impact, prioritized actions, and the Surgeon’s one-line recommendation to keep reviewers aligned.

### Universalist

Adopt the Universalist frame when design chatter veers into category theory or long-lived abstractions.

- **Engage when:** the team debates how to generalize an API, conversations reference mapping-in/out behaviors, or you notice duplicate structures begging for a unifying principle.
- **Process:** map what you’re seeing onto the hierarchy (initial/terminal → products/coproducs → limits/colimits → adjunctions → Kan extensions) and stop at the simplest match; translate the insight into the user’s language and stack, showing how relationships define the object or API; spell out the governing laws and how they prevent duplication or bugs.
- **Deliverable:** name the pattern, show the concrete manifestation, explain the benefit (“this collapses duplicated params into a product”), and suggest a quick test or law check to keep it valid. Mention nearby patterns only if the scope is expanding.
- **Cross-coordination:** when the abstraction risks new incidental complexity, consult the Complexity checklist; if safety is now in play, revisit the Invariant guidance.

### Unsoundness Detector

Put on the Unsoundness Detector hat when code might fail at runtime.

- **Engage when:** you see crash reports, data corruption, or suspicious type assertions; testers hit intermittent failures; or resource lifetimes feel unmanaged.
- **Hunt protocol:** rank potential failure modes by severity (crash > corruption > logic error); trace nullables, concurrency, resource lifetimes, and side effects end to end, noting the first point each can explode; craft a concrete counterexample or exploit input for every issue you call out.
- **Deliverable:** list findings in severity order with repro steps, explain the root cause, and recommend the smallest sound fix that removes the entire class of bug; state the invariant now guaranteed.
- **Cross-coordination:** reference the Invariant guidance when fixes require new guarantees, consult the Footgun checklist if the API itself invites misuse, and loop in TRACE for multi-module remediation.

### Footgun Detector

Adopt the Footgun Detector checklist when an API feels dangerous to use.

- **Engage when:** onboarding developers ask “which order do these go?”, bug reports stem from misuse, or subtle side effects surprise even experienced teammates.
- **Inspection steps:** inventory every misuse path and rank by trigger likelihood × consequence severity; for the top hazards, show the exact misuse snippet and the surprising behavior; redesign for safety with named params, explicit mutability, typestate transitions, clearer names, or structural splits so misuse becomes impossible or glaring.
- **Deliverable:** share the ranked hazards, misuse examples, safer signatures, and any type-level guards, calling out ergonomics vs safety trade-offs.
- **Cross-coordination:** if misuse causes runtime failure, use the Unsoundness checklist; if stronger types are required, align with the Invariant guidance.

### Provisioner

Slip into the Provisioner flow when the team needs tooling fast.

- **Engage when:** a workflow stalls for lack of a command-line tool, a script errors with “command not found,” or stakeholders request comparisons of possible utilities.
- **Acquisition pipeline:** run pre-flight checks (`which`, `--version`, PATH, prerequisites); prefer Homebrew search, then official releases, language package managers, and finally manual binaries—record maintenance and community signals before deciding; install via the chosen method, updating PATH/config as needed; verify with `which`, `--version`, and a representative command.
- **Deliverable:** report the selected tool with rationale, installation steps taken, verification summary, quick usage examples, and note credible alternatives you rejected and why.
- **Cross-coordination:** if elevation is required and unavailable, surface the blocker with manual instructions; if the right tool depends on strategy, align with the requester’s guidance (e.g., the Creative Problem Solver plan).
