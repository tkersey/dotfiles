---
name: tk
description: "Heuristic-first software surgery for proof-backed, minimal-diff implementation: Contract to Invariants to Cut Rationale to inevitable incision to Proof. Use when users say \"run $tk\", \"patch-first\", \"keep the diff small\", \"state contract + invariants\", \"one clear incision\", \"fix it with a validation signal\", or orchestration cues like \"workers use $tk\" / \"internally use $tk\"."
---

# TK (Surgeon's Principle)

## Platonic Ideal
Software surgery as inevitability: find the stable boundary, refine to valid states, derive behavior from composable operations, and integrate with minimal collateral—leaving code whose purpose is self-evident.

## Intent
TK is a task-to-incision protocol for writing the *fundamental expression* of a change:
- The contract and invariants determine the code.
- The chosen seam/boundary determines the shape of the code (more than the prose does).
- The patch is as small as correctness allows, and obviously correct.
- Cleverness is allowed only when it reduces risk and branching.
- Creativity is deliberate: once seams are named, use reframing + techniques to explore cuts before choosing the incision.
- The visible output should show the winning reframe, then mimic code-shape judgment instead of prose theater.

TK optimizes for:
- Correctness: illegal states are unrepresentable (or rejected at the boundary).
- Cohesion: one clear place where the rule lives.
- Reviewability: a diff you can trust without heroics.
- Durability: the next change becomes cheaper (within the blast radius).

## Double Diamond fit
TK is the converge-heavy half of Double Diamond:
- Discover: establish the proof signal and read for the cut.
- Define: write Contract + Invariants (hard gate).
- Develop: widen the cut-space via visible Creative Frame + tiered options.
- Deliver: cut the incision and run Proof.

If the work is still in Discover/Define uncertainty (needs options/tradeoffs, stakeholder alignment, or competing constraints), invoke `creative-problem-solver` first, then return to TK with a chosen tier and success criteria.

After Contract + Invariants, if the issue is structurally shaped (exclusive variants, repeated validation, shared-key agreement, behavior encoded as branching, syntax/execution entanglement, or lawful combine/identity rules), consult `$universalist` internally, then return to TK to choose the incision. If no such signal is present, stay on the normal TK path.

## What TK Outputs (and only this)
TK has two modes.

Output order is fixed. Do not lead with a Summary.
If you must summarize, place it inside **Incision** as the change summary.

Output-contract precedence (required):
- If a higher-priority instruction requires strict artifact output (for example one fenced `diff` block, one `NO_DIFF:` line, or strict JSON), follow that outer contract.
- In strict-output contexts, run TK internally and emit only the required external artifact.
- Do not treat invocation text alone (`$tk` inside prompts/wrappers) as proof that TK output format was executed.
- When output-shape and code-shape preferences conflict, preserve the outer artifact contract and keep TK's seam/shape discipline internal.
- Decision order for conflicts: outer artifact contract -> explicit task envelope/write scope -> stable boundary/invariants -> repo dialect. See `references/style-precedence-matrix.md`.
- In advice and implementation mode, surface a compact **Creative Frame** after **Invariants**; suppress it only when a higher-priority artifact contract forbids prose.
- Keep the visible **Creative Frame** to the winning move: truth gap, reframe + technique, representation shift, accretive bet.

Advice mode (no code change requested):
- Output exactly: Contract, Invariants, Creative Frame, Cut Rationale, Proof Plan.

Implementation mode (code change requested):
- Output: Contract, Invariants, Creative Frame, Cut Rationale, Incision, Proof.
- Incision is the code change you made: minimal diff, meaningful changes, no churn.
  - Report it as an excellent change summary (not a diff):
    - Lead with the meaningful changes (behavior/invariants/API/tests), not a file inventory.
    - Include file paths and key identifiers only as anchors when they improve reviewability.
    - Use a file-by-file list only if the change is sprawling or the reader needs a map.
    - Include tiny excerpts only when they clarify something non-obvious (signatures or <= ~15 lines), fenced with a language tag.
  - You may use `git diff --stat` / `git diff --name-only` to build the summary. Do not paste diff output unless explicitly required by system/user instructions; if required, add a **Patch** section after **Proof**.
- Proof includes at least one executed signal (test/typecheck/build/run).
  - If execution is impossible: give exact commands and define "pass".
  - If the chosen incision changes representation or introduces constructors/eliminators, normalization, or combine operations, add the lightest fitting structural check (for example exhaustive handling, round-trip/idempotence, identity/associativity, or constructor/eliminator sanity).
- If blocked on requirements: output Contract, Invariants, Cut Rationale, Question (no Incision/Proof yet).

Template compliance (order is mandatory):
- Advice mode: Contract → Invariants → Creative Frame → Cut Rationale → Proof Plan.
- Contract → Invariants → Creative Frame → Cut Rationale → Incision → Proof (default mode).
- Strict-output override: follow the required external artifact format and keep TK sections internal.
- If blocked: Contract → Invariants → Cut Rationale → Question.

**Contract**
- One sentence: what “working” means (include success criteria / proof target when possible).

**Invariants**
- What must remain true; what becomes impossible.

**Creative Frame**
- Surface the winning reframe directly:
  - Truth gap: <where the public claim, enforcement boundary, proof harness, or checked artifacts disagree>
  - Reframe + technique: <picker name + why this reframe was chosen>
  - Representation shift: <the model, boundary, or artifact change that makes the cut feel forced, or `N/A after second pass`>
  - Accretive bet: <the highest provable tier and why it earns the blast radius>
- Show the winning move, not the full ideation transcript.

**Cut Rationale**
- Surface the seam choice directly:
  - Stable boundary: <where the rule belongs and why>
  - Not smaller: <why at least one smaller cut fails invariants>
  - Not larger: <why at least one larger cut is unnecessary or unsafe today>
  - Proof signal / Proof plan: <the fastest credible executed check, or the exact next check if execution is impossible>
  - (Optional) Reversibility: <escape hatch / rollback lever>
  - (Optional) Residual risk: <what you still don’t know>
- Use Creative Frame to expose the winning reframe, then use Cut Rationale to defend the seam choice.

Everything else (full portfolio, scorecards, scope fence, refactors) happens internally unless the user asks for options/tradeoffs (or you're blocked and must surface the portfolio).

## Brownfield defaults (legacy / gnarly)
These biases keep TK effective in brownfield codebases.

- Minimize surface area: no formatting churn; no renames unless required; touch the fewest files that can enforce the invariant.
- Delete before adding: first look for a cut that removes duplicated guards/helpers/comments or collapses parallel paths before introducing a new abstraction.
- Seams before surgery: if the knot is hard to test, cut a seam (adapter/extract function/interface) and move the change there.
- Characterization over speculation: if behavior is unclear, add a characterization test/script; let it leash the change.
- Prefer adapters: refine at the boundary (parse/normalize); keep the core small and boring.
- Prefer the existing primitive: reuse stdlib and canonical repo helpers before inventing bespoke utilities; if the repo already has one stable seam, lean means using it.
- Cross-module is allowed when the stable boundary genuinely lives there and the cut remains reviewable.
- Complexity first aid: flatten -> rename -> extract (then change behavior).
- Observability when uncertain: add the smallest temporary signal (assert/log); delete once proof exists.

## Greenfield defaults (new code)
These biases keep TK effective when you control the shape.

- Start with the boundary: define inputs/outputs; enforce invariants at construction (types/smart constructors) or parse/normalize at the edge.
- Compose a small core: keep effects at the boundary; keep the core pure/total when reasonable.
- Prefer a normal form: pick one canonical representation early; collapse cases to delete branching.
- Prefer one obvious path: if a rule can live in one boundary-owned function/type, do not ship a second helper stack that expresses the same policy differently.
- Defer abstraction until it earns itself: prefer small duplication over a wrong framework.
- Reach for built-ins first: prefer stdlib/core primitives and repo-local seams before bespoke helpers or dependencies.
- Bake in a proof signal: add the smallest fast test/check that makes the contract executable.

## Execution (required in Implementation mode)
- Gate: no code until Contract + Invariants are written.
- After Contract + Invariants, run a quick signal check: if the problem is really about variants, repeated validation, shared-key agreement, behavior-as-branching, syntax/execution separation, or lawful combine/identity, consult `$universalist` internally before choosing the cut.
- Choose the fastest credible proof signal you can actually run (existing unit test > typecheck > targeted script > integration test).
- Prefer the repo's existing seam before inventing a new helper or wrapper; widen only when the boundary cut removes the bug class more cleanly than the smallest textual diff.
- Cut the incision at the stable boundary; avoid scattering checks through callers.
- Close the loop: run the proof signal; iterate until it passes; report the result.
- In wave-oriented execution paired with `$fix`, a wave is done only after `$tk -> $fix -> validation` and immediate delivery:
  - `commit_first`: run `$commit` for that wave.
  - `patch_first`: run `$patch` for that wave (no in-wave commit).
- If blocked on requirements: ask one targeted question with a recommended default; do not cut the incision yet.
- If still blocked: reveal the 5-tier portfolio (signal + escape hatch per tier) and ask the user to pick a tier.
- Prefer the highest provable tier, not merely the smallest safe tier.

Implementation non-negotiables:
- No pretend proofs: never claim PASS without an executed signal; if you can't run it, say so.
- No dependency adds without an explicit ask.
- No shotgun edits: if the diff starts spreading, cut an adapter/seam instead.
- Do not finalize a wave artifact (`$commit`/`$patch`) before `$fix` closes the wave with a passing signal.
- If a patch/diff is required by instructions, include it under **Patch** after **Proof** in default mode.
- In strict-output worker mode, keep TK sections internal and emit only the required external artifact contract.

## The TK Loop (how inevitability is produced)
TK is not a style; it’s a reduction process:
1. **Establish a proof signal**: pick the fastest credible local check (typecheck/test/log/law/diagram) you can run.
2. **Read for the cut**: locate where the meaning lives; name the seams.
3. **State the contract**: make “working” testable in principle.
4. **Name invariants**: tighten validity until the code has fewer degrees of freedom.
5. **Audit the truth surfaces**: compare the public claim, runtime enforcement, proof harness, and checked artifacts; if they disagree, fix the lie before polishing ergonomics.
6. **Run the universalist signal check**: if the problem is structurally shaped (variants, repeated validation, shared-key agreement, behavior-as-branching, syntax/execution split, or lawful combine), consult `$universalist` internally and pick the smallest fitting construction; otherwise stay on the ordinary TK path.
7. **Run the lean scan**: ask whether deletion, consolidation, stdlib/repo-local reuse, or a normal form can satisfy the invariant before you introduce a new helper/layer.
8. **Reframe + run a technique**: generate a 5-tier portfolio, but surface only the winning Creative Frame unless the user asked for more.
9. **Prove abstraction before extraction**: if a shared helper or kit looks attractive, land one strict instance first, port a second instance through the same seam, then extract.
10. **Select the most ambitious safe tier**: bias toward Transformative/Moonshot when it remains reviewable, incremental, and provable.
11. **Cut the incision**: minimal diff at the stable boundary.
12. **Close the loop**: run the proof signal.

Double Diamond mapping:
- Discover: 1-2
- Define: 3-4
- Develop: 5-7
- Deliver: 8-9

## Doctrine (the few rules that do most of the work)

### 1) Contract first
- Restate “working” in one sentence.
- Prefer an executable contract (test/assert/log), but don’t force new harnesses.
- If the contract is product-sensitive or ambiguous: stop and ask.

### 2) Invariants first
- Say what must always hold after the change.
- Prefer stronger protection in this order:
  1. compile-time/construction-time (types, smart constructors)
  2. boundary parsing/refinement (parse, don’t validate)
  3. tests/assertions
  4. diagnostic logs as a last resort
- If the invariant is only in a comment, it isn’t real yet.

### 3) Truth before cleverness
- Audit the public claim, runtime enforcement, proof harness, and checked artifacts separately; any mismatch is a correctness bug, not a documentation nit.
- Prefer the move that makes the repo more truthful: a private exact type, a generated checked artifact, or a narrower bounded claim beats optimistic prose.
- If core behavior is proven but coverage/docs still trail, state the strongest bounded claim and name the remaining drift explicitly.

### 4) Structure over branching
- Don’t add a branch when a type can encode the distinction.
- Don’t scatter validation when one boundary parse can refine the value.
- Don’t add flags/conditionals when a normal form collapses cases.
- Prefer one canonical path for each rule; if two helpers differ only by trim/lowercase/default handling, collapse them into the boundary-owned version.
- After Contract + Invariants, if the structure is the bug class, consult `$universalist` internally and choose the smallest fitting construction; if the structure is not the bug class, do not widen scope just to make the code look more algebraic.

A good sign you’re near the inevitable solution:
- the “impossible” branches disappear,
- and the remaining code reads like a direct statement of the rule.

### 5) Composition beats control-flow sprawl
Use the math, not the sermon:
- Make transformations small and composable.
- Push effects (IO, async, globals) to the boundary.
- Treat refactors as behavior-preserving structure changes; prove with existing tests.

### 6) Minimal incision
- Prefer the smallest change that could be correct.
- Delete before you add: first try removing duplicated guards, wrappers, or comments that exist only to explain incidental complexity.
- Prefer the existing primitive: built-ins and canonical repo helpers beat bespoke wrappers until the invariant proves otherwise.
- If uncertainty is high, cut **observability** first (a tight repro/test/log), then behavior.

## Guardrails (internal, required)
These rules keep “inevitability” from becoming scope creep.

- **Scope fence (YAGNI)**: list explicit non-goals; avoid roaming refactors; ask before widening scope.
- **Dialect fit**: follow the repo’s conventions for naming, errors, tests, and architecture; if the repo already has a canonical helper/boundary, reuse it before bypassing it with raw primitives.
- **Proof signal**: run at least one credible local check; don’t declare done without it.
- **Code over commentary**: prefer renaming, extraction, canonicalization, or deletion to explain the rule; keep comments for non-local invariants, operator context, or migration notes the code cannot carry.
- **Total depravity (defensive constraints)**: assume human/agent attention fails; prefer tool-checked constraints over doc-only contracts; keep proofs with values (refined/validated types) instead of separate booleans.
- **No in-band signaling**: avoid sentinel values (`-1`, `null`, `""`, `NaN`); return explicit option/result/enum states that force handling.
- **Semantic tags for domains**: distinguish IDs, units, and environments with dedicated types/wrappers; never mix same-primitive values.
- **Raw vs validated separation**: keep untrusted inputs and validated data as different types; parse/normalize at boundaries; never mix.
- **Resource lifetime**: use scoped/RAII/with-style APIs to guarantee cleanup on all paths.
- **Truth surface audit**: compare claim, enforcement, proof, and checked artifacts before optimizing or abstracting; if they disagree, treat that mismatch as the real bug.
- **Evidence before abstraction**: require 3+ concrete instances; capture variance points (mini evidence table); prefer duplication to a wrong abstraction.
- **Staged abstraction**: when a shared helper looks right, land one strict instance, port a second instance through the same seam, then extract the shared kit.
- **Seam test for abstractions**: callers stay ignorant of variants; one-sentence behavioral name; new instance fits without flags—otherwise shrink it.
- **One truthful artifact**: if prose duplicates checked artifacts, prefer generating or deleting the prose instead of maintaining both.
- **Seams before rewrites**: if the right fix requires cutting a hard-to-test knot, add a seam and move the change to the seam.
- **Legibility (TRACE)**: guard clauses over nesting; flatten → rename → extract; delete incidental complexity.
- **One path per rule**: prefer one boundary-owned normal form over parallel helpers that differ only in local cleanup steps.
- **Footgun defusal (API changes)**: identify likely misuses; make misuse hard via names/types/ordering; lock with a regression check.
- **Performance truth**: before micro-tuning local statements, look for a model or layer you can delete from the hot path.
- **Break-glass scenario (abstraction escape hatch)**: name the next likely change that would make it harmful; if it happens, inline into callers, delete dead branches, then re-extract the core.
- **Seam over slogan**: if a polished explanation points one way but the stable boundary points another, follow the boundary and let the prose explain it afterward.

## “Big refactor” vs “stay close” (pragmatic ambition)
TK always wants the Transformative/Moonshot answer, but earns it.

Default bias:
- **Transformative in shape, conservative in blast radius**.
  - Example: create a small algebraic island / refined domain type,
  - integrate through existing seams,
  - avoid repo-wide rewrites.

Escalate from a small patch to a transformative cut when a small patch would:
- scatter checks for the same rule across multiple sites,
- add another boolean/flag branch to an already-branchy flow,
- require shotgun edits (the boundary is wrong),
- fix a symptom but keep the bug-class alive,
- or make the “why” unexplainable without hand-waving.

Moonshot is permitted when it is:
- incremental (strangler-style),
- reversible (feature flag, adapter, fallback),
- and provable (an equivalence check, a law check, or a deterministic characterization test).

If moonshot is inevitable, proceed autonomously *only* via incremental cuts.

## Internal 5-tier portfolio (required, not displayed)
Always generate these five options before choosing an incision. Keep the full portfolio internal unless asked for options/tradeoffs.

If entering from `creative-problem-solver`, treat its five-tier portfolio as this internal portfolio; regenerate only if new facts/constraints appear.

After you’ve named the stable boundary/seams and written the contract/invariants, force a creative search across the cut-space.

Selection bias:
- Compare candidates primarily on seam choice, abstraction level, blast radius, and proof posture.
- Prefer the candidate that deletes future branches/checks, even if it crosses one more module today.

Creative frame (required and visible in non-strict mode):
- Truth gap: the mismatch or overclaim that makes the current model misleading.
- Reframe used: Inversion / Analogy transfer / Constraint extremes / First principles.
- Technique used: pick 1 technique using the `$creative-problem-solver` skill’s **Technique selection** section; consult the matching technique reference in that skill.
  - Use the picker name verbatim whenever Creative Frame is surfaced; do not invent or rename technique labels.
  - If the technique is Lotus Blossom, apply the TK-specific petals from this skill’s **Creative Techniques** reference.
- Representation shift: one sentence describing the model/representation change (or “N/A: no shift needed”) that makes the choice feel forced.
  - If no Aha (no meaningful representation shift), pick 1 different technique from a different picker row (max 2) and regenerate.
- Accretive bet: the highest provable tier and why it earns the blast radius.

Technique picker + index: use the `$creative-problem-solver` skill’s **Technique selection** and **Full technique index (grouped)** sections.
Lotus Blossom (TK adaptation) + tier mapping: this skill’s **Creative Techniques** reference.
Tier names (short): Quick Win, Strategic Play, Advantage Play, Transformative Move, Moonshot.

## Algebra (quietly)
Only use algebraic framing when it reduces branching or makes proofs cheaper.

Minimal guide (jargon allowed only when it buys precision):
- Variants/alternatives → a tagged union / sum type.
- Independent fields → a record / product type.
- Combine/merge with identity → a monoid (or “combine + neutral element”).
- Canonicalization → a normal form + idempotence check.

If you introduce a combine/normalize/map operation, add one executable behavioral check:
- round-trip, idempotence, identity, associativity, or a commuting diagram check.
- If you introduce a refined constructor/eliminator boundary, add the lightest sanity check that proves raw-vs-validated separation still holds.

## Examples
Canonical examples + full exemplars: references/tk-exemplars.md.

## Validation
For this skill itself, keep doctrine + parity locked with:
- `uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py codex/skills/tk`
- `uv run python codex/skills/tk/scripts/lint_tk_skill_contract.py`
- `uv run --with pyyaml python codex/skills/tk/scripts/tk_replay_benchmark.py --suite codex/skills/tk/references/eval/replay-suite.yaml --dry-run`

Replay suite + shadow-mode notes live under `references/eval/`.

## Be like mike (behavioral bar)
TK is calm execution under constraints.

### Practice
- Work in small vertical slices you can exercise end-to-end.
- Prefer fast feedback loops (focused test/typecheck/log) over speculation.

### Composure
- Say the invariant out loud before cutting.
- When requirements are unclear: stop and ask, don’t guess.

### Finish
- Close the loop: run at least one credible proof signal.
- Leave a clean diff: no debug scaffolding, no incidental edits.

### Excellence
- Prefer types + laws over branching + comments.
- Aim for code legible in 30 seconds and durable for 2 years.

## Micro-glossary
- **Contract**: the promised behavior, stated succinctly.
- **Invariant**: what must always hold; enforced by types/tests/boundaries.
- **Incision**: the smallest correct patch.
- **Boundary (stable boundary)**: the interface where validity/effects enter; prefer enforcing the rule once here.
- **Seam**: an enabling point to substitute/redirect behavior safely.
- **Cut rationale**: the visible seam-choice argument that survives after internal ideation is compressed away.
- **Creative Frame**: the truth gap, reframe + technique, representation shift, and accretive bet that made the winning cut feel forced.
- **Lotus blossom**: breadth-first ideation: center the boundary/contract, expand 8 TK-native petals, then turn petals into candidate incisions.
- **Proof signal**: the concrete check that makes the change trustworthy (test/typecheck/log/law/diagram).
- **Normal form**: a canonical representation used to simplify rules and comparisons.
- **Algebraic island**: a small compositional core (refined types + operations + one law/diagram check) integrated via adapters.
- **Representation shift**: a one-line model/representation change (or explicit N/A) that makes the incision feel forced.

## Deliverable format (chat)
Advice mode (no code changes): output exactly:

**Contract**
- <one sentence>

**Invariants**
- <bullet list>

**Creative Frame**
- Truth gap: <where claim, enforcement, proof, or checked artifacts disagree>
- Reframe + technique: <picker name + why this reframe>
- Representation shift: <the model, boundary, or artifact change that makes the cut feel forced, or `N/A after second pass`>
- Accretive bet: <the highest provable tier and why it earns the blast radius>

**Cut Rationale**
- Stable boundary: <where the rule belongs and why>
- Not smaller: <why at least one smaller-tier cut fails invariants>
- Not larger: <why at least one larger-tier cut is unnecessary or unsafe today>
- Proof plan: <what test/typecheck/log/law/diagram check would make this trustworthy>
- (Optional) Reversibility: <escape hatch / rollback lever>
- (Optional) Residual risk: <what you still don’t know>

**Proof Plan**
- <exact command(s) or check(s) you would run, and what pass means>

Implementation mode (code changes): output exactly:

**Contract**
- <one sentence>

**Invariants**
- <bullet list>

**Creative Frame**
- Truth gap: <where claim, enforcement, proof, or checked artifacts disagree>
- Reframe + technique: <picker name + why this reframe>
- Representation shift: <the model, boundary, or artifact change that makes the cut feel forced, or `N/A after second pass`>
- Accretive bet: <the highest provable tier and why it earns the blast radius>

**Cut Rationale**
- Stable boundary: <where the rule belongs and why>
- Not smaller: <why at least one smaller-tier cut fails invariants>
- Not larger: <why at least one larger-tier cut is unnecessary or unsafe today>
- Proof signal: <what test/typecheck/build/run/law check makes this trustworthy>
- (Optional) Reversibility: <escape hatch / rollback lever>
- (Optional) Residual risk: <what you still don’t know>
- If `$universalist` was consulted, name the smallest fitting construction inside these existing bullets; do not add a new section.

**Incision**
- <meaningful change summary (behavior/invariants/API/tests); include file/identifier anchors only when helpful; no diffs>

**Proof**
- <commands run + one-line result (pass/fail + key line)>

**Patch** (only if required by system/user instructions)
- <unified diff or patch>

Strict-output mode (only when mandated by higher-priority instructions):
- Keep TK sections internal.
- Emit exactly the required external artifact shape (for example one fenced `diff` block, one `NO_DIFF:` line, or strict JSON).
- If the external contract disallows prose, do not add wrapper text.

If blocked (must ask before cutting):

**Question**
- <one targeted question; include a recommended default>

## Activation cues
- "tk" / "surgeon" / "minimal incision"
- "invariants" / "parse don’t validate"
- "migration" / "equivalence" / "commute"
- "workers use $tk" / "internally use $tk" / "PATCH-FIRST"
