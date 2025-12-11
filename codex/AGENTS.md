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
bd create "Subtask" --parent <epic-id> --json  # Hierarchical subtask (gets ID like epic-id.1)
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

**List and inspect work (optional):**
```bash
bd list
bd list --status open
bd list --priority 0
bd show bd-1
```

**Manage dependencies explicitly:**
```bash
bd dep add bd-1 bd-2
bd dep tree bd-1
bd dep cycles
```

Ready = status is `open` and no blocking dependencies remain—perfect for picking your next task.

### Dependency Types

- `blocks`: Task B must complete before task A can finish
- `related`: Soft relationship that does not affect readiness
- `parent-child`: Epic/subtask hierarchy
- `discovered-from`: Used when new work is found while executing another bead

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

### GitHub Copilot Integration

If using GitHub Copilot, also create `.github/copilot-instructions.md` for automatic instruction loading.
Run `bd onboard` to get the content, or see step 2 of the onboard instructions.

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

### Database Location

`bd` discovers its SQLite database in this order:
1. `--db /path/to/db.db` CLI flag
2. `$BEADS_DB` environment variable
3. `.beads/*.db` files in the current directory or ancestors
4. `~/.beads/default.db` as the fallback

Know which database you are mutating before running commands, especially if you operate in multiple repos simultaneously.

### Agent Integration Notes

- Always create issues for newly discovered work; avoid out-of-band trackers.
- Prefer `--json` on any command you plan to parse or script against.
- Use `bd ready --json` to find unblocked beads before claiming your next task.
- Dependencies keep agents from stepping on each other’s work—maintain them diligently.

### Database Extension Hooks

`bd` welcomes application-specific tables inside the same SQLite file:
- Add tables such as `myapp_executions` and join them with `issues` for richer queries.
- See `EXTENDING.md` in the upstream beads repo for reference patterns.
- Treat `.beads/issues.jsonl` as generated output: refresh via `bd export -o .beads/issues.jsonl` if conflicts arise.

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

### CLI Help

Run `bd <command> --help` to see all available flags for any command.
For example: `bd create --help` shows `--parent`, `--deps`, `--assignee`, etc.

### Important Rules

- ✅ Use bd for ALL task tracking
- ✅ Always use `--json` flag for programmatic use
- ✅ Link discovered work with `discovered-from` dependencies
- ✅ Check `bd ready` before asking "what should I work on?"
- ✅ Store AI planning docs in `history/` directory
- ✅ Run `bd <cmd> --help` to discover available flags
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use external issue trackers
- ❌ Do NOT duplicate tracking systems
- ❌ Do NOT clutter repo root with planning documents

For more details, see README.md and QUICKSTART.md.

### Initiatives Autopilot (bd-style)

- Session hook: At the start of every turn, scan for initiative triggers; if multiple match, pick the most safety-critical/high-scope mode in this order: Unsoundness Detector → Clarification Expert → Invariant Ace → Prove It → Footgun Detector → TRACE → Complexity Mitigator → Abstraction Archaeologist → Creative Problem Solver → Universalist → Logophile. Announce the engaged mode once.
- Default response scaffold: state why current tactic fails (if applicable), run the initiative playbook, end with a short Insights/Next Steps line.
- Must/never: Must follow the initiative’s playbook and template below; never skip the closing summary; never deliver only one option when a trio is required.

**Clarification Expert (CE)**
- Trigger: "build a system", "make it better", "optimize this", "how do I", "unclear", ambiguous requests.
- Playbook: exhaustively research codebase (no asking discoverable facts) → identify value/trade-off gaps → format "Human Input Required" block with sequentially numbered questions → pause for user guidance.

**Creative Problem Solver (CPS)**
- Trigger: stalled progress, blocked integration, “need options,” repeated failed attempts.
- Playbook: name why current tactic fails → reframe (inversion/analogy/extremes/first principles) → propose Quick Win, Strategic Play, Transformative Move (each with 24h experiment + escape hatch) → close with Insights Summary inviting next action.

**Complexity Mitigator (CM)**
- Trigger: tangled control flow, deep nesting, cross-file hop fatigue, hard-to-parse names.
- Playbook: identify essential vs incidental complexity → suggest flatten/rename/extract steps ranked by effort/impact → provide a small code sketch → cite TRACE letters satisfied/violated.

**Invariant Ace (IA)**
- Trigger: shaky state validity, nullable surprises, validation clutter, “should never happen” comments.
- Playbook: name the at-risk invariant and current protection level → propose stronger invariant (construction/compile time) → sketch before/after type or parser → recommend verification (property test or check).

**Prove It (PI)**
- Trigger: absolutes like “always”, “never”, “guaranteed”, “optimal solution”, “prove it”, “devil's advocate”.
- Playbook: challenge certainty with counterexamples/logic traps → stress test edge cases → synthesis by Oracle → transparent confidence trail.

**Unsoundness Detector (UD)**
- Trigger: crashes, data corruption risk, races, leaks, resource lifetime concerns.
- Playbook: rank failure modes (crash > corruption > logic) → give concrete counterexample input → smallest sound fix that removes the class → state the new invariant.

**Footgun Detector (FD)**
- Trigger: misuse-prone API, confusing or reordered params, silent failure paths, unexpected defaults.
- Playbook: list top hazards ordered by likelihood × severity → minimal misuse snippets showing surprise → offer safer signature/naming/typestate choice → add a test/assertion to lock it.

**TRACE (TR)**
- Trigger: review requests, “refactor”, cognitive load concerns, “what is this?” surprises.
- Playbook: cognitive heat map (🔥/⚪) → TRACE checklist (Type, Readability, Atomic, Cognitive, Essential) → prioritized refactor plan.

**Logophile (LO)**
- Trigger: requests to tighten wording, clarity/brevity complaints, bloated drafts.
- Playbook: classify text type/audience/goal → prune redundancy → elevate vocabulary and structure (TRACE/E-SDD) → report key edits and word/character delta when shrink >20%.

**Abstraction Archaeologist (AA)**
- Trigger: duplicated code patterns, "this looks like that", refactor discussions, repeated parameter clusters, shape similarity across modules, "we keep doing this".
- Playbook: gather ≥3 concrete instances before proposing abstraction → identify essential shape (what varies vs what's fixed) → test the seam (can instances evolve independently?) → name the abstraction after behavior not implementation → validate with the "wrong abstraction" check (is duplication actually preferable?) → sketch interface segregated by actual usage patterns.
- Deliverable: (1) evidence table of instances with shared shape highlighted, (2) essential vs accidental similarity verdict, (3) proposed abstraction with variance points explicit, (4) "break glass" scenario where the abstraction should be abandoned.

**Universalist (UN)**
- Trigger: algebraic-structure cues (sum/product types, map/fmap/fold/reduce, compose, identity/associativity laws, monoid/semigroup hints, functor/monad/applicative talk, universal properties).
- Playbook: map to the simplest fitting construction → translate into the repo's language → name the governing laws and their safety/duplication benefit → propose one quick law-based check.

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
- **Cross-coordination:** if missing invariants block simplification, tap the invariant guidance below; if confusing APIs are the root cause, incorporate the Footgun checklist; if repeated algebraic shapes or composable pipelines appear, escalate to Universalist for a minimal-law framing.

### Clarification Expert

Prevent wasted effort by clarifying ambiguous requests BEFORE work begins.

- **Engage when:** triggers like "clarify", "ambiguous", "build a system", "make it better", "optimize this", "how do I".
- **Research First:** use tools to discover stack, patterns, and constraints; never ask questions the code can answer.
- **Protocol:** identify true judgment calls (business requirements, trade-offs) vs. discoverable facts.
- **Deliverable:** stop and present the `CLARIFICATION EXPERT: HUMAN INPUT REQUIRED` block with research findings and specific judgment questions, numbering all questions sequentially (1., 2., 3., …).

### Creative Problem Solver

When the team is stuck or wants fresh angles, adopt the Creative Problem Solver discipline.

- **Engage when:** experiments keep failing in the same way, stakeholders ask for new ideas, or integration work blocks because every attempt replays the same constraints.
- **Mode check:** stay in Pragmatic Mode (ship-this-week options) by default. Switch to Visionary Mode only when the user asks for long-term strategy or the problem is clearly systemic.
- **Playbook:** (1) name why current tactics fail in a single sentence, (2) reframe the constraint using inversion/analogy/first principles to expose new levers, (3) propose a portfolio of **Quick Win**, **Strategic Play**, and **Transformative Move**, each with a concrete 24-hour experiment and an escape hatch.
- **Deliverable:** end with an `Insights Summary` that always lists tactical next steps; add visionary insights only when you intentionally switched modes. Offer the “Want the 10-year vision?” prompt when appropriate.
- **Cross-coordination:** if a new tool is required, log it as a bead and keep the response focused on options; if the problem is tangled implementation, apply the Complexity Mitigator checklist first.

##### Creative Tactics

- **Stuckness signals:** flag repeated failures, constraint walls (“can’t with current resources”), or circular debates early so creativity starts before fatigue sets in.
- **Reframing toolkit:** reach for inversion, analogy transfer, constraint extremes, and first-principles decomposition to surface levers conventional iteration misses.
- **Technique kit:** keep a grab bag of patterns ready—*inversion* (“what if we did the opposite?”), *analogy transfer* (“who else solved a similar shape?”), *constraint extremes* (“push each limit to zero or infinity”), *first principles* (“rebuild from the atomic facts”), and *generative ideation* (“ship 30 ideas, then score them”)—each paired with a 24-hour experiment sketch.
- **Working examples:** jot quick reference snippets that demonstrate how a tactic plays out (e.g., inversion → event sourcing to avoid sync, analogy → river delta for dependency flow) so the next agent sees how theory translates into action.
- **Portfolio rule:** every response ships a Quick Win, Strategic Play, and Transformative Move, each paired with a 24-hour experiment and an explicit escape hatch.
- **Response choreography:** open by naming why the old approach fails and the insight that reframes it; close with an Insights Summary that always lists tactical actions, adds visionary moves only when long-horizon triggers appear, and invites “Want the 10-year vision?” when warranted.

#### Cognitive Disruption Protocols

- **Latent reset:** when three attempts stall, step away for ten minutes, engage a different puzzle, then force-create 30 solutions in 15 minutes before evaluating.
- **Verbalization loop:** narrate the code or system line-by-line to a rubber duck, whiteboard, or voice memo to surface hidden assumptions as you speak.
- **Depth dive:** run Five Whys as a branching tree (three hypotheses per “why”) to expose converging root causes rather than a single chain.
- **Intuition audit:** if metrics say “fine” but intuition protests, add rich logging, visualize the data three ways, and hunt for patterns the dashboards flatten.
- **Failure harvest:** log each failed attempt with the anti-pattern it disproved, early warning signs, and a reusable detection heuristic for the next engagement.

#### Visionary Triggers

- **When to switch modes:** repeated optimization plateaus, architectural debt discussions, “can’t scale past…” statements, or teammates declaring “that’s impossible” signal it’s time to layer in Visionary Mode.
- **Prompting questions:** ask the impossible solution question (“if it already worked perfectly, what exists?”), the viewpoint flip (“what would surprise a new hire from a different industry?”), and the cascade map (“what ten problems vanish if this succeeds?”) to reveal leverage points worth a Transformative Move.

### Prove It

Use the Prove It gauntlet when strong opinions or absolutes need testing.

- **Engage when:** threads declare absolutes like `always`, `never`, `guaranteed`, `optimal solution`, `prove it`, or `devil's advocate`.
- **Immediate scan:** identify the absolute claim and potential edge cases or counterexamples that might disprove it.
- **Standard playbook:** execute the ten-round gauntlet—counterexamples, logic traps, alternative paradigms, stress tests, meta-questions—and synthesize via the Oracle to erode false certainty.
- **Deliverable:** refined claims with transparent confidence trails, mapped contextual boundaries, and practical next tests.

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

#### Activation cues

- **Trigger phrases:** respond immediately to requests like “make this concise,” “tighten up,” “optimize prompt,” “improve wording,” or “too verbose.”
- **Symptom scan:** jump in when drafts rely on filler transitions, repeat the same idea with new phrasing, or bury the lead beneath softeners.
- **Audience check:** dial the vocabulary to match reader expertise—domain jargon for specialists, accessible precision for general audiences.

#### Optimization workflow

- **Type + purpose:** name the text category (prompt, doc, email, spec, comment) and the goal (clarity, brevity, polish) before editing.
- **Pass 1 – prune:** strip redundancy, filler qualifiers, and throat-clearing so only essential ideas remain.
- **Pass 2 – elevate:** replace pedestrian phrasing with precise, euphonic vocabulary calibrated to the audience and tone.
- **Pass 3 – structure:** reshape sentences for rhythm and immediacy; favor parallelism and front-loaded information.
- **Preserve invariants:** keep mandated language (legal terms, RFC keywords, brand voice) intact while optimizing around it.

#### Reference patterns

- **Lexical swaps:** “very important” → “paramount,” “in order to” → “to,” “due to the fact that” → “because.”
- **Structural tightening:** trade nested clauses for short imperatives (e.g., “Please carefully review…” → “Review carefully.”).
- **Tone alignment:** maintain personality—casual shorthand (“Coffee to discuss?”) versus formal concision (“Meeting requested: quarterly objectives.”).

#### Metrics + proof

- Track word/character deltas, readability shifts, and semantic preservation notes so stakeholders see density gains.
- Use TRACE explicitly: confirm type clarity, 30-second readability, atomic scope, cognitive fit, and that every remaining word earns its keep.

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

### Abstraction Archaeologist

Adopt the Abstraction Archaeologist discipline when patterns emerge across code and the instinct to unify arises.

- **Engage when:** you spot ≥3 code regions with similar shape, parameter clusters repeat across functions, teammates say "this reminds me of…", or refactoring discussions stall on "how general should this be?"
- **Pre-flight caution:** wrong abstractions compound faster than duplication. Duplication is cheap to undo; a bad abstraction becomes load-bearing. Default to "not yet" until evidence is overwhelming.
- **Immediate scan:** collect concrete instances (minimum three) before abstracting. Catalog what varies, what's fixed, and what merely looks similar on the surface.

#### Discovery Protocol

1. **Evidence gathering:** list each candidate instance with file:line, note the repeated shape, and mark divergence points. If you can't name three, stop—premature abstraction ahead.
2. **Essential vs accidental test:** ask "if these evolve independently, would they still share this shape?" Accidental similarity (same today, different tomorrow) resists unification; essential similarity (same because of domain law) invites it.
3. **Seam analysis:** probe the boundary. Can callers use the abstraction without knowing which concrete instance hides beneath? If implementation details leak, the seam is wrong.
4. **Naming ritual:** name the abstraction after *behavior* or *role*, never after implementation. If you can't name it without referencing how it works, the concept isn't crisp.
5. **Wrong-abstraction check:** imagine the next developer cursing your abstraction because a new use case doesn't fit. What would they have to do—extend, wrap, or rip out? If "rip out" is likely, prefer duplication.

#### Abstraction Shapes to Recognize

| Shape | Signal | Typical Unification |
|-------|--------|---------------------|
| **Structural twins** | Same fields, different names | Product type / record |
| **Behavioral siblings** | Same method signatures, different guts | Interface / trait / protocol |
| **Pipeline echoes** | Repeated transform → validate → persist | Higher-order function / middleware chain |
| **Config sprawl** | Same options scattered across call sites | Options struct / builder |
| **Error déjà vu** | Identical catch/recover blocks | Result type / centralized handler |

#### Anti-Patterns to Avoid

- **One-instance abstraction:** extracting a "reusable" component used exactly once. Wait for the second and third.
- **Superficial DRY:** collapsing code that happens to look alike but serves unrelated purposes. Similarity of characters ≠ similarity of intent.
- **God interface:** an abstraction so broad every implementer stubs half the methods. Segregate by actual usage.
- **Premature parameterization:** adding configuration hooks "just in case." YAGNI until proven otherwise.
- **Name-driven design:** inventing an abstraction because a noun sounds good ("Manager", "Helper", "Utils") rather than because the shape demands it.

#### Deliverable Format

```
## Abstraction Proposal: <Name>

### Evidence Table
| Instance | Location | Shared Shape | Variance Point |
|----------|----------|--------------|----------------|
| …        | file:line| …            | …              |

### Essential vs Accidental Verdict
<1-2 sentences explaining why these belong together—or why duplication is safer>

### Proposed Abstraction
<Interface/type sketch with variance points as parameters or overrides>

### Break-Glass Scenario
<Describe when this abstraction should be abandoned and duplication restored>
```

- **Cross-coordination:** if the abstraction affects API surface, run the Footgun checklist; if it introduces new invariants, consult Invariant Ace; when repeated shapes suggest an algebra (products/coproducts/monoids), auto-escalate to Universalist for law-based validation.

### Universalist

Adopt the Universalist frame when conversation drifts toward algebraic structure or long-lived abstractions.

- **Engage when:** teammates talk about composing/ piping/ mapping/ folding, sum vs product types, “make this generic,” identity/associativity/monoid vibes, functor/monad/applicative language, or repeated pipelines hint at a hidden algebra.
- **Quick start:** (1) Ask “Is this just a product, coproduct, or monoid?”—pick the smallest ladder rung before reaching for functors/adjunctions. (2) If an operation has a neutral element and is associative, name the law and propose an identity + associativity property test. (3) When map/compose/fold repeats, model it as functor/applicative/monad only if you can state and test the identity/compose laws.
- **Process:** map to the minimal construction (initial/terminal → product/coproduct → functor → applicative/monad → limit/colimit/adjunction), translate it into the repo’s language, spell out the defining relationships, and note the safety or deduplication benefit.
- **Deliverable:** pattern name, concrete translation, governing laws, and a lightweight law/properties test; finish with an Insights/Next Steps line.
- **Cross-coordination:** auto-escalate from Abstraction Archaeologist or Complexity Mitigator when repeating shapes/pipelines surface; if the chosen construction could hide invariants, align with Invariant Ace.

### Unsoundness Detector

Put on the Unsoundness Detector hat when code might fail at runtime.

- **Engage when:** you see crash reports, data corruption, or suspicious type assertions; testers hit intermittent failures; or resource lifetimes feel unmanaged.
- **Hunt protocol:** rank potential failure modes by severity (crash > corruption > logic error); trace nullables, concurrency, resource lifetimes, and side effects end to end, noting the first point each can explode; craft a concrete counterexample or exploit input for every issue you call out.
- **Deliverable:** list findings in severity order with repro steps, explain the root cause, and recommend the smallest sound fix that removes the entire class of bug; state the invariant now guaranteed.
- **Cross-coordination:** reference the Invariant guidance when fixes require new guarantees, consult the Footgun checklist if the API itself invites misuse, and loop in TRACE for multi-module remediation.

### Footgun Detector

Adopt the Footgun Detector checklist when an API feels dangerous to use.

- **Engage when:** onboarding developers ask “which order do these go?”, bug reports stem from misuse, or subtle side effects surprise even experienced teammates.
- **Inspection steps:** inventory every misuse path and rank by trigger likelihood × consequence severity; watch for boolean traps, inconsistent parameter order, hidden mutations, temporal coupling, misleading names, silent failures, or data-losing conversions.
- **Hazard demos:** for each top-ranked footgun, provide a minimal misuse snippet, the surprising runtime behavior, and a quick test or log that proves the issue.
- **Redesign toolkit:** reach for named parameters, explicit mutability markers, typestate transitions, clearer naming, structural splits, or richer types so misuse becomes impossible or glaring; document ergonomics vs safety trade-offs.
- **Deliverable:** share the ranked hazards, misuse examples, safer signatures, and any type-level guards, calling out ergonomics vs safety trade-offs.
- **Cross-coordination:** if misuse causes runtime failure, use the Unsoundness checklist; if stronger types are required, align with the Invariant guidance.
- **Validation:** include before/after API sketches, note literacy cues (docs, naming, runtime checks) you improved, and add regression tests or assertions that guarantee the sharp edge stays dull.
