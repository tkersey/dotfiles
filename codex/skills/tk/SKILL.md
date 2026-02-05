---
name: tk
description: "Software surgery: contract → invariants → creative search → inevitable incision; minimal diff, compositional core, proof signal."
---

# TK (Surgeon's Principle)

## Platonic Ideal
Software surgery as inevitability: find the stable boundary, refine to valid states, derive behavior from composable operations, and integrate with minimal collateral—leaving code whose purpose is self-evident.

## Intent
TK is a task-to-incision protocol for writing the *fundamental expression* of a change:
- The contract and invariants determine the code.
- The patch is as small as correctness allows, and obviously correct.
- Cleverness is allowed only when it reduces risk and branching.
- Creativity is deliberate: once seams are named, use reframing + techniques to explore cuts before choosing the incision.

TK optimizes for:
- Correctness: illegal states are unrepresentable (or rejected at the boundary).
- Cohesion: one clear place where the rule lives.
- Reviewability: a diff you can trust without heroics.
- Durability: the next change becomes cheaper (within the blast radius).

## Double Diamond fit
TK is the converge-heavy half of Double Diamond:
- Discover: establish the proof signal and read for the cut.
- Define: write Contract + Invariants (hard gate).
- Develop: widen the cut-space via Creative Frame + (internal) tiered options.
- Deliver: cut the incision and run Proof.

If the work is still in Discover/Define uncertainty (needs options/tradeoffs, stakeholder alignment, or competing constraints), invoke `creative-problem-solver` first, then return to TK with a chosen tier and success criteria.

## What TK Outputs (and only this)
TK has two modes.

Output order is fixed. Do not lead with a Summary.
If you must summarize, place it inside **Incision** as the change summary.

Advice mode (no code change requested):
- Output exactly: Contract, Invariants, Creative Frame, Why This Solution.

Implementation mode (code change requested):
- Output: Contract, Invariants, Creative Frame, Why This Solution, Incision, Proof.
- Incision is the code change you made: minimal diff, meaningful changes, no churn.
  - Report it as an excellent change summary (not a diff):
    - Lead with the meaningful changes (behavior/invariants/API/tests), not a file inventory.
    - Include file paths and key identifiers only as anchors when they improve reviewability.
    - Use a file-by-file list only if the change is sprawling or the reader needs a map.
    - Include tiny excerpts only when they clarify something non-obvious (signatures or <= ~15 lines), fenced with a language tag.
  - You may use `git diff --stat` / `git diff --name-only` to build the summary. Do not paste diff output unless explicitly required by system/user instructions; if required, add a **Patch** section after **Proof**.
- Proof includes at least one executed signal (test/typecheck/build/run).
  - If execution is impossible: give exact commands and define "pass".
- If blocked on requirements: output Contract, Invariants, Creative Frame, Why This Solution, Question (no Incision/Proof yet).

Template compliance (order is mandatory):
- Contract → Invariants → Creative Frame → Why This Solution → Incision → Proof.
- If blocked: Contract → Invariants → Creative Frame → Why This Solution → Question.

**Contract**
- One sentence: what “working” means (include success criteria / proof target when possible).

**Invariants**
- What must remain true; what becomes impossible.

**Creative Frame**
- Reframe: <Inversion / Analogy transfer / Constraint extremes / First principles>
- Technique: <one named technique (e.g., Lotus blossom / SCAMPER / TRIZ)>
- Representation shift: <one sentence (or “N/A: no shift needed”)>

**Why This Solution**
- Argue inevitability: name the stable boundary, rule out at least one smaller and one larger tier, and state the proof signal.

Everything else (full portfolio, scorecards, scope fence, refactors) happens internally unless the user asks for options/tradeoffs (or you're blocked and must surface the portfolio).

## Brownfield defaults (legacy / gnarly)
These biases keep TK effective in brownfield codebases.

- Minimize surface area: no formatting churn; no renames unless required; touch the fewest files that can enforce the invariant.
- Seams before surgery: if the knot is hard to test, cut a seam (adapter/extract function/interface) and move the change there.
- Characterization over speculation: if behavior is unclear, add a characterization test/script; let it leash the change.
- Prefer adapters: refine at the boundary (parse/normalize); keep the core small and boring.
- Complexity first aid: flatten -> rename -> extract (then change behavior).
- Observability when uncertain: add the smallest temporary signal (assert/log); delete once proof exists.

## Greenfield defaults (new code)
These biases keep TK effective when you control the shape.

- Start with the boundary: define inputs/outputs; enforce invariants at construction (types/smart constructors) or parse/normalize at the edge.
- Compose a small core: keep effects at the boundary; keep the core pure/total when reasonable.
- Prefer a normal form: pick one canonical representation early; collapse cases to delete branching.
- Defer abstraction until it earns itself: prefer small duplication over a wrong framework.
- Bake in a proof signal: add the smallest fast test/check that makes the contract executable.

## Execution (required in Implementation mode)
- Gate: no code until Contract + Invariants are written.
- Choose the fastest credible proof signal you can actually run (existing unit test > typecheck > targeted script > integration test).
- Cut the incision at the stable boundary; avoid scattering checks through callers.
- Close the loop: run the proof signal; iterate until it passes; report the result.
- If blocked on requirements: ask one targeted question with a recommended default; do not cut the incision yet.
- If still blocked: reveal the 5-tier portfolio (signal + escape hatch per tier) and ask the user to pick a tier.

Implementation non-negotiables:
- No pretend proofs: never claim PASS without an executed signal; if you can't run it, say so.
- No dependency adds without an explicit ask.
- No shotgun edits: if the diff starts spreading, cut an adapter/seam instead.
- If a patch/diff is required by instructions, include it under **Patch** after **Proof**; never skip the TK sections.

## The TK Loop (how inevitability is produced)
TK is not a style; it’s a reduction process:
1. **Establish a proof signal**: pick the fastest credible local check (typecheck/test/log/law/diagram) you can run.
2. **Read for the cut**: locate where the meaning lives; name the seams.
3. **State the contract**: make “working” testable in principle.
4. **Name invariants**: tighten validity until the code has fewer degrees of freedom.
5. **Reframe + run a technique (Lotus blossom default, internal)**: generate a 5-tier portfolio (proof signals + escape hatches).
6. **Select the most ambitious safe tier**: bias toward Transformative/Moonshot, stay pragmatic.
7. **Cut the incision**: minimal diff at the stable boundary.
8. **Close the loop**: run the proof signal.

Double Diamond mapping:
- Discover: 1-2
- Define: 3-4
- Develop: 5-6
- Deliver: 7-8

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

### 3) Structure over branching
- Don’t add a branch when a type can encode the distinction.
- Don’t scatter validation when one boundary parse can refine the value.
- Don’t add flags/conditionals when a normal form collapses cases.

A good sign you’re near the inevitable solution:
- the “impossible” branches disappear,
- and the remaining code reads like a direct statement of the rule.

### 4) Composition beats control-flow sprawl
Use the math, not the sermon:
- Make transformations small and composable.
- Push effects (IO, async, globals) to the boundary.
- Treat refactors as behavior-preserving structure changes; prove with existing tests.

### 5) Minimal incision
- Prefer the smallest change that could be correct.
- If uncertainty is high, cut **observability** first (a tight repro/test/log), then behavior.

## Guardrails (internal, required)
These rules keep “inevitability” from becoming scope creep.

- **Scope fence (YAGNI)**: list explicit non-goals; avoid roaming refactors; ask before widening scope.
- **Dialect fit**: follow the repo’s conventions for naming, errors, tests, and architecture; don’t import a framework to prove a point.
- **Proof signal**: run at least one credible local check; don’t declare done without it.
- **Total depravity (defensive constraints)**: assume human/agent attention fails; prefer tool-checked constraints over doc-only contracts; keep proofs with values (refined/validated types) instead of separate booleans.
- **No in-band signaling**: avoid sentinel values (`-1`, `null`, `""`, `NaN`); return explicit option/result/enum states that force handling.
- **Semantic tags for domains**: distinguish IDs, units, and environments with dedicated types/wrappers; never mix same-primitive values.
- **Raw vs validated separation**: keep untrusted inputs and validated data as different types; parse/normalize at boundaries; never mix.
- **Resource lifetime**: use scoped/RAII/with-style APIs to guarantee cleanup on all paths.
- **Evidence before abstraction**: require 3+ concrete instances; capture variance points (mini evidence table); prefer duplication to a wrong abstraction.
- **Seam test for abstractions**: callers stay ignorant of variants; one-sentence behavioral name; new instance fits without flags—otherwise shrink it.
- **Seams before rewrites**: if the right fix requires cutting a hard-to-test knot, add a seam and move the change to the seam.
- **Legibility (TRACE)**: guard clauses over nesting; flatten → rename → extract; delete incidental complexity.
- **Footgun defusal (API changes)**: identify likely misuses; make misuse hard via names/types/ordering; lock with a regression check.
- **Break-glass scenario (abstraction escape hatch)**: name the next likely change that would make it harmful; if it happens, inline into callers, delete dead branches, then re-extract the core.

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
Always generate these five options before choosing an incision. Keep them internal unless asked for options/tradeoffs.

If entering from `creative-problem-solver`, treat its five-tier portfolio as this internal portfolio; regenerate only if new facts/constraints appear.

After you’ve named the stable boundary/seams and written the contract/invariants, force a creative search across the cut-space.

Creative frame (required):
- Reframe used: Inversion / Analogy transfer / Constraint extremes / First principles.
- Technique used: pick one technique (see references/creative-techniques.md) to generate non-obvious options.
- Representation shift: one sentence describing the model/representation change (or “N/A: no shift needed”) that makes the choice feel forced.
  - If still unclear: pick a different reframe + technique, then regenerate the portfolio.

Tier details, technique picker, and Lotus blossom expansion: references/creative-techniques.md.
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

## Examples
Canonical examples + full exemplars: references/tk-exemplars.md.

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
- **Creative Frame**: the reframe + technique + representation shift used to widen the cut-space after seams are named.
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
- Reframe: <Inversion / Analogy transfer / Constraint extremes / First principles>
- Technique: <one named technique (e.g., Lotus blossom / SCAMPER / TRIZ)>
- Representation shift: <one sentence (or “N/A: no shift needed”)>

**Why This Solution**
- Stable boundary: <where the rule belongs and why>
- Not smaller: <why at least one smaller-tier cut fails invariants>
- Not larger: <why at least one larger-tier cut is unnecessary or unsafe today>
- Proof signal: <what test/typecheck/log/law/diagram check makes this trustworthy>
- (Optional) Reversibility: <escape hatch / rollback lever>
- (Optional) Residual risk: <what you still don’t know>

Implementation mode (code changes): output exactly:

**Contract**
- <one sentence>

**Invariants**
- <bullet list>

**Creative Frame**
- Reframe: <Inversion / Analogy transfer / Constraint extremes / First principles>
- Technique: <one named technique (e.g., Lotus blossom / SCAMPER / TRIZ)>
- Representation shift: <one sentence (or “N/A: no shift needed”)>

**Why This Solution**
- Stable boundary: <where the rule belongs and why>
- Not smaller: <why at least one smaller-tier cut fails invariants>
- Not larger: <why at least one larger-tier cut is unnecessary or unsafe today>
- Proof signal: <what test/typecheck/build/run/law check makes this trustworthy>
- (Optional) Reversibility: <escape hatch / rollback lever>
- (Optional) Residual risk: <what you still don’t know>

**Incision**
- <meaningful change summary (behavior/invariants/API/tests); include file/identifier anchors only when helpful; no diffs>

**Proof**
- <commands run + one-line result (pass/fail + key line)>

**Patch** (only if required by system/user instructions)
- <unified diff or patch>

If blocked (must ask before cutting):

**Question**
- <one targeted question; include a recommended default>

## Activation cues
- "tk" / "surgeon" / "minimal incision"
- "invariants" / "parse don’t validate"
- "migration" / "equivalence" / "commute"
