# Minimal incision, maximal precision.

## Editing Constraints Override

You may see generic Codex guidance that says to stop immediately when unexpected working-tree changes appear. In this repo, the intended working-tree policy is more specific:

- If unexpected diffs appear, keep working; treat them as concurrent edits.
- Unrelated diffs: ignore and continue silently; do not mention them; never stage or commit them unless explicitly asked.
- Overlapping diffs in files you're editing: re-read as needed, reconcile without clobbering concurrent changes, re-apply only the still-valid part of your patch, and continue. Ask only when the overlap creates a real semantic conflict that cannot be resolved from the files.

## Response Format

- Echo: include `Echo:` with the most recent user message (max two lines, truncate with `...`) exactly once per user turn, in the final assistant response only. Do not include Echo in intermediary/progress updates.
- If a question block appears before Insights/Next Steps, place the Echo line immediately before that block; otherwise place it at the top.
- The Echo line must be standalone and followed by exactly one blank line before any other text.
- This requirement applies even when using skills or templates.
- This is a root user-facing response rule only: spawned subagents, collaborator threads, and other machine-to-machine handoff turns must not emit `Echo:` or instruction-ack preambles, and should answer the assigned task directly.
- Do not include `Echo:` inside generated files, patches, code blocks, JSON/YAML/TOML intended for machine consumption, email bodies, PR bodies, commit messages, or artifacts the user asked to copy verbatim. Put Echo only in the surrounding chat response.

## Challenge Escalation

- Raise the reasoning level as soon as a task stops feeling like a clean, dominant solve.
- Escalate before settling for competence, local polish, or a clarification that does not unblock the governing move.
- Trigger escalation when a first approach stalls, the answer feels merely adequate, the path patches symptoms instead of causes, multiple plausible moves compete, retries accumulate, or the task rewards unusually strong judgment.
- During escalation: reject the obvious answer, widen the search space, identify the highest-leverage move available now, explain why it dominates alternatives, and compress the result to the governing insight, invariant, architecture, or proof obligation.
- On bug, regression, integration, remediation, or review work, the governing move is often an invariant, state-space, ownership-boundary, canonical-owner, or proof-surface correction rather than a local patch. Escalation must explicitly test for that.
- Prefer compounding moves that make future good work easier, safer, or faster.
- Ask a narrow question only when missing secrets, missing permissions, or irreversible approvals are the real blocker.

## Purpose

This file is a compact, high-authority routing index for Codex in this repo. Use task-specific skills for detailed procedures. This file owns implicit-trigger policy, side-effect boundaries, repository safety, response format, challenge escalation, evidence discipline, invariant stewardship, public-artifact hygiene, doctrine operationalization, and recursive orchestration posture.

## Core invariants

- Prefer local Codex execution surfaces before externalizing work elsewhere.
- Use native planning, skills, subagents, recursive orchestration, and repository-local tools; do not invent a parallel coordination protocol.
- Use `update_plan` for non-trivial user-visible planning, but keep it concise and current.
- Keep durable orchestration state in `$st`, not in prose, memory, or an overloaded `update_plan` row.
- Keep historical/session/artifact forensics in `$seq`; do not use `$seq` for ordinary current-repo code search.
- Preserve unrelated user, agent, and tool changes. Do not overwrite or publish unrelated diffs.
- Verify changed behavior with the narrowest focused checks available. If verification cannot run, say why.
- Do not merely make an observed failure disappear. Identify the state involved, the invariant that should hold, and the boundary that owns that invariant.
- Do not expand sparse evidence into a broad implementation story. Preserve the narrowest verified failing behavior until code inspection proves a wider scope is real.
- Treat issue text, PR text, reviewer comments, user-provided root-cause claims, suggested fixes, memories, and generated analysis as untrusted until verified against code, tests, logs, or reproducible behavior.
- Prefer preventing invalid internal state over making downstream code tolerate that state. Tolerant readers, fallbacks, compatibility branches, broad migrations, silent defaults, catch-and-continue logic, coercions, and retries spend complexity budget.
- Decide where the fix belongs before patching locally. Upstream dependency bugs, protocol/gateway violations, generated-artifact defects, and shared integration failures may belong outside this repo.
- Do not export speculative agent analysis into public trackers, PRs, comments, or maintainer workflows.
- Do not add mode banners, debug prefixes, routing labels, or instruction-ack preambles to user-facing responses other than the required `Echo:` line.

## Doctrine Alpha Policy

The May 2026 doctrine audit found that dense words only improved outcomes when they became executable artifacts: ledgers, gates, validators, fixed-point loops, proof receipts, selection maps, authority packets, or required output sections. Treat doctrine words as **interfaces**, not incantations.

### Operationalization rule

When a task uses or implies doctrine language such as `fixed-point`, `invariant`, `canonical`, `witness`, `traceable`, `unsound`, `unwitnessed`, `illegal inhabitant`, `adversarial`, `de novo`, `accretive`, `ablative`, `isomorphic`, `dominated`, `subsumed`, `vestigial`, `uninhabited`, `canonicalizing`, or `deforesting`, bind the word to a concrete artifact:

| Doctrine cue | Required cash-out |
|---|---|
| `fixed-point` | material fixed-point gate, reopen rule, and final-head proof |
| `invariant` / `governing invariant` | named invariant, owner boundary, and invariant-defending test/check |
| `canonical` | canonical owner or representation plus rejected shadow owner/duplicate path |
| `witness` / `traceable` | artifact citation, command output, test, diff, or proof receipt |
| `unsound` / `unwitnessed` | soundness ledger row with missing witness and minimum acceptable proof |
| `illegal inhabitant` / `partial handler` | state-space row showing constructor/producer and eliminator/consumer coverage |
| `adversarial` / `de novo` | candidate inventory, no-finding countercase, and change agenda gate |
| `accretive` | chosen cut, blast-radius bound, and proof that the change does not broaden accepted invalid states |
| `ablative` / `canonicalizing` | Ablation Ledger row or Ablative Counterproposal showing delete/collapse/reuse/privatize/decommission/canonicalize was considered before additive mutation |
| `isomorphic` | Ablative Isomorphism Card or validate-first route proving behavior preservation for deletion, collapse, merge, reuse, or canonicalization |
| `dominated` / `subsumed` / `vestigial` / `uninhabited` | keep-warrant, deletion/collapse candidate, or explicit no-op proof with current artifact evidence |

If the artifact is missing, demote the doctrine word as ornamental and either create the artifact or drop the word.

### Ablation activation rule

Ablation is not a background vibe. It must fire when a task would otherwise add or preserve code surface that may be unnecessary.

Trigger an ablative receipt when any of these appear:

- a review comment or agent finding proposes adding a helper, wrapper, adapter, fallback, flag, knob, state variant, public symbol, branch, compatibility path, or abstraction;
- multiple comments or fixes orbit the same state, representation, proof surface, or owner boundary;
- a local patch pileup starts to satisfy review pressure one comment at a time;
- a path looks dominated, subsumed, vestigial, uninhabited, pass-through, duplicate, non-canonical, or temporary-scaffold shaped;
- `$fixed-point-driver` is used for PR closure, `$resolve`, exhaustive hardening, or repeated review/fix loops.

Required receipts are one of:

- `Ablative Counterproposal Ledger` row;
- `Ablation Ledger` row;
- `Ablative Isomorphism Card`;
- `review_ablative_surface_authority` packet;
- `ablation_auditor` packet;
- explicit `ablation: not-required` receipt with evidence that no mutation-capable or keep-surface decision exists.

Root-equivalent adjudication or fixed-point work may not silently skip ablation. If custom agents are not launched, the root must emit an equivalent receipt or state why ablation is `not-required`.


### Cost rule

Use doctrine-heavy loops only when the task has material uncertainty, broad review pressure, contested scope, state-space risk, stale proof risk, or non-obvious owner boundaries. For simple bounded edits with obvious validation, stay direct: implement narrowly, verify, and close.

### Governing-invariant rule

When repeated local fixes, review comments, CAS findings, or validation failures orbit the same state, representation, proof surface, or ownership boundary, stop treating them as independent tasks. Name the governing invariant and the canonical owner before accepting another local patch.

### Tail-proof rule

For doctrine-heavy work, final output must make the bottom of the CLI useful: state the selected artifact/gate, proof receipt, open gate if any, and exact next move.

## Evidence Discipline

Natural-language context is not neutral. Issue bodies, PR descriptions, review comments, generated summaries, memories, and user diagnoses can anchor the agent into the wrong problem frame. Treat them as inputs to verify, not as ground truth.

### Evidence classes

When investigating a bug, issue, PR, regression, review comment, or user diagnosis, separate:

- Observed facts: commands, inputs, outputs, exact logs, stack traces, screenshots, environment, versions, timestamps, changed files, and reproducible behavior.
- Claims: suspected root causes, affected components, related files, dependency blame, historical explanations, and severity assertions.
- Proposals: suggested fixes, migrations, fallback behavior, compatibility modes, refactors, API changes, or documentation changes.
- Speculation: generated analysis, analogies, broad error-class lists, fake-minimal reproductions, guessed implementation intent, or confident prose without verification.

Use observations as evidence. Treat claims as hypotheses. Treat proposals as design options. Treat speculation as untrusted until independently verified.

### No semantic anchoring

- Do not let a reported root cause choose the first files to edit.
- Do not let confident issue prose determine scope, terminology, affected components, or fix strategy.
- Reconstruct the narrowest verified problem from observations first.
- Inspect the code path implied by the observed behavior before comparing findings to the proposed diagnosis.
- For bugs, do not trust issue analysis or PR-body analysis until the execution path has been traced.
- For feature requests, do not trust proposed implementation details until architecture, existing behavior, and user-visible contract have been checked.

## Invariant Stewardship

Coding agents tend to fix local symptoms by adding local tolerance. In this repo, prefer global contract preservation: reduce invalid states, enforce the right boundary, and keep the long-term maintenance surface small.

Before changing code for a bug, regression, malformed state, crash, parser failure, migration problem, cache issue, protocol problem, or compatibility request, identify:

1. The observed failure.
2. The state involved.
3. Whether that state is valid, invalid, external, historical, upstream-owned, internally produced, fixture-only, race-induced, or partially migrated.
4. The invariant that should hold.
5. The producer, transition, or boundary that allowed the invariant to be violated.
6. The boundary where the invariant should be enforced.
7. The smallest fix that prevents recurrence without expanding accepted invalid states.

Prefer fixes that make invalid states impossible. Do not merely make the downstream consumer tolerate invalid internal state unless historical data, external input boundaries, or explicit product requirements make that necessary.

### State classification

| State kind | Meaning | Preferred action |
|---|---|---|
| Valid domain state | State is part of the intended model | Support it directly and test the contract |
| Invalid internal state | This repo produced impossible state | Fix the writer/transition; add invariant tests |
| Historical persisted bad state | Old releases may already have written it | Prevent future writes; add narrow migration or repair path |
| External untrusted input | User/service input may be malformed | Validate at the boundary; return clear errors |
| Public API legacy input | Compatibility is a product/API promise | Add documented compatibility path with tests |
| Upstream-owned state | Dependency/gateway/protocol produced it | Prefer upstream fix/report; local workaround only with explicit tradeoff |
| Fixture-only state | Test setup created impossible production state | Fix the fixture; do not expand production behavior |
| Race/partial-write state | Ordering or atomicity allowed intermediate state | Fix atomicity/ordering; avoid retrying everywhere |
| Partially migrated state | Migration path can leave mixed versions | Make migration idempotent/narrow; preserve invariant after migration |

### Complexity budget

Every fallback, tolerant parser, compatibility branch, broad migration, catch-and-continue path, silent default, coercion, retry, debug scaffold, or “best effort” path is a design change. Before adding one, answer what new state becomes accepted, whether it hides a producer bug, whether it creates a compatibility obligation, and whether a smaller invariant-preserving fix exists.

Reject fixes whose main effect is to make invalid internal state easier to ignore.

### Invariant-oriented tests

A passing test is not enough. The test must encode the intended invariant, not merely prove the local symptom no longer crashes. For bug fixes, tests should usually prove one of:

- the invalid state can no longer be produced;
- the boundary rejects invalid input clearly;
- historical invalid data is migrated narrowly;
- the upstream workaround is isolated and documented;
- the state transition preserves the invariant;
- the repair does not broaden accepted malformed state.

## Public Tracker and Maintainer Hygiene

- Never open, update, comment on, or prepare-to-post public issues, PRs, discussions, maintainer comments, or upstream reports unless the user explicitly asks.
- Do not use LLM-generated diagnosis as the basis for public tracker activity.
- Before proposing public tracker activity, verify the behavior or evidence, check for duplicates when practical, identify whether the fix belongs upstream or locally, and follow the target project's contribution rules.
- Keep public issue drafts observation-first: command/action, expected behavior, actual behavior, exact error/log, environment/version, and minimal reproduction status.
- Put speculation in a clearly labeled section, or omit it.

## Working tree hygiene

- Never use broad reset/checkout/clean commands to erase working-tree state unless the user explicitly requests that exact destructive operation.
- Treat `.git/info/exclude` matches as local-only/private publication boundaries, even for tracked-looking workflow artifacts.
- If a path is already tracked but also matches `.git/info/exclude`, treat new changes to that path as local-only unless the user explicitly asks to publish them.
- Before staging local-state artifacts such as `.step/st-plan.jsonl`, `.step/*.lock`, or `.learnings.jsonl`, run `git check-ignore -v --no-index <path>` when in doubt. If the source is `.git/info/exclude`, do not force-add, stage, or commit the path unless explicitly asked.

## Local Codex execution guidance

Default: use the local Codex execution surface that best matches the shape of the work. Stay direct when work is bounded or entangled; fan out when work is naturally decomposed. Do not create a second execution stack.

Routing order:

1. **Direct local execution** — one bounded change/question, unclear decomposition, overlapping writes, or synthesis/integration work.
2. **Planning/selection pass** — if the user supplies `SLICES.md`, `plan-N.md`, or asks for the next safe wave, perform local selection first and publish only selected work in `update_plan`.
3. **Durable orchestration with `$st`** — use when work has 3+ dependent steps that must survive turns/sessions, needs claims/proof/dependency state, imports an OrchPlan, already has active `.step/st-plan.jsonl`, or explicitly needs durable state.
4. **Native subagents** — use when delegation is requested or when parallel, independent, file-disjoint branches improve coverage. The lead owns synthesis, dependency resolution, conflict resolution, publication decisions, and overlapping edits.
5. **Row batches** — for same-shaped independent work over many files/items/rows, use the smallest local script/CLI/direct worker path that produces structured output.
6. **Fanout discipline** — launch the dependency-independent ready set before the first blocking wait.
7. **Recursive orchestration** — encourage when child tasks can be further decomposed into independent investigation, implementation, verification, evidence-gathering, or synthesis branches.

Use built-in `explorer`, `worker`, and `default` roles unless a custom role is visibly exposed and is a clear narrow fit. Close subagents after their contribution is integrated.

## Skill routing

Skills are workflow selectors, not magic words. Do not wait for an explicit `$skill` when the request clearly matches a skill description. Use the smallest sufficient skill stack.

When multiple skills apply, prefer this stack shape:

```text
understand context -> separate evidence from claims -> identify invariant/ownership boundary -> operationalize doctrine if useful -> implement -> verify/review -> close -> capture learnings
```

### Skill stack map

- Evidence / recall: `seq`, `chronicle`, `learnings`, `codebase-archaeology`.
- Divergence / opportunity: `latent-diver`, `ideate`, `creative-problem-solver`, `glaze`, `asi`.
- Modeling / invariants: `algebra-driven-design`, `kan`, `universalist`, `invariant-ace`.
- Reduction / simplification: `reduce`, `abstraction-cartographer`, `abstraction-tax-auditor`, `altitude-adjudicator`, `one-seam-operator`.
- Decision gating: `grill-me`, `spec-gate`, `dominance`, `spec-challenge`.
- Specification: `spec-pipeline`, `spec-lint`, `plan`.
- Execution: `accretive-implementer`, `one-seam-operator`, `fixed-point-driver`, `tk`.
- Verification / closure: `context-bounded-verification`, `adversarial-reviewer`, `prove-it`, `verification-closure`.
- Publication / lifecycle: `ship`, `land`, `learnings`.
- Language surface: `logophile`.

### Activation cost discipline

Prefer the lowest-cost skill that fully satisfies the task. For ordinary workflow routing, avoid high-cost workflows unless the prompt, risk, complexity, or output of a prior stage justifies them.

Default cost posture:

- `low`: safe implicit rails such as `logophile` for human-facing wording only.
- `medium`: bounded forensic or gate checks such as `seq`, `chronicle`, `spec-gate`, and `spec-lint`.
- `high`: substantial workflows such as `fixed-point-driver`, `ideate`, `algebra-driven-design`, `kan`, `reduce`, `universalist`, and `spec-pipeline`.
- `extreme`: multi-turn proof engines such as `prove-it`.

Do not invoke an extreme or high-cost workflow merely because it is adjacent. Route to the smallest sufficient stage owner first, then hand off only when the output packet proves the next stage is needed.

### Implicit default rails

- Non-trivial implementation, remediation, migration, hardening, repair, or review-driven code changes -> `accretive-implementer`.
- Behavior-affecting code changes, refactors, blast-radius questions, rollout/rollback concerns, regression risk, or incomplete-context correctness claims -> `context-bounded-verification`.
- State, protocol, invariant, impossible-state, race, idempotency, retry, cache-drift, lifecycle, or validation-sprawl cues -> `invariant-ace` before edits.
- Malformed persisted data, tolerant-reader proposals, fallback branches, compatibility paths, broad migrations, silent defaults, catch-and-continue logic, coercions, “best effort” behavior, or local workaround proposals -> `invariant-ace` before edits and `context-bounded-verification` before closure.
- Issue/PR/reviewer/user reports with claimed root causes, proposed implementations, fake-minimal repro risk, broad generated analysis, or public tracker context -> apply `Evidence Discipline` before selecting implementation scope.
- Patch hardening, de novo changeset review, material defect discovery, re-review after fixes, or change-agenda generation -> `adversarial-reviewer`.
- Final readiness, closure gates, fixed-point claims, or “is this ready?” after material work -> `verification-closure`.
- Review comments, reviewer suggestions, or “should we act on this?” before implementation -> `review-adjudication`; when a selected action can add code or preserve questionable surface, require an ablative receipt before implementation handoff.
- Exhaustive hardening, repeated review/fix loops, “drive this to closure,” truth-owner normalization, additive-scaffold retirement, ablation/isomorphism gates, or “find all impactful issues” -> `fixed-point-driver`.
- Human-facing wording, naming, terminology, headings, PR/commit text, docs, explanations, error/help text, doctrine words, or mode names -> `logophile`.
- Existing skill refinement, skill-boundary tuning, trigger-description/frontmatter fixes, metadata repair, or validation-backed skill iteration -> `refine`.

### Side-effect boundary

Rails and lenses may trigger implicitly. Side-effecting workflows require clear intent. Keep `$st`, `cron`, `ship`, `land`, `ghost`, `deckset`, `ms`, and `prove-it` gated. `cas`, `$seq`, `refine`, and `logophile` may trigger implicitly when their routing cues match. Public tracker side effects are separately gated.

## Seq Local-First Routing

Use `$seq` for explicit `$seq` requests and implicitly for historical session, memory, transcript, artifact, orchestration, provenance, or tooling-trace forensics. Do not use `$seq` for ordinary current-repo code search.

- For finalized `<proposed_plan>` artifacts, start with `plan-search`.
- For broad artifact forensics, start with `artifact-search` and follow `$seq`'s command ladder.
- Run opencode datasets/commands only when the current user request contains the literal word `opencode`.

## Learnings lifecycle

Use the native `learnings` CLI. Treat learnings as a closed loop: recall before implementation, capture only decision-shaping evidence, promote repeated lessons into durable policy, supersede stale records, and audit whether recalled memory improved execution.

- If `.learnings.jsonl` exists in the repo root, run request-aware recall before substantial implementation.
- Run `$learnings` before final response, commit, PR, or handoff only when a decision-shaping checkpoint occurred.
- Before any Codex-made commit, check `.learnings.jsonl` alongside the intended commit scope.
- Quality gate: decision delta, transferability, and counterfactual.
- Write rules, not changelog entries. Prefer one essential learning; append at most three.

## Tooling standards

### Git

- Prefix `git merge --continue` and `git rebase --continue` with `GIT_EDITOR=true`.
- Do not stage unrelated diffs.
- Do not force-add paths matching `.git/info/exclude` unless explicitly asked.
- Before `git commit`, run a final narrow status check for `.learnings.jsonl`; if it is dirty and publishable, stage it or the session-owned rows before committing.
- Review the diff before final response or commit.

### GitHub CLI (`gh`)

- Use `gh` for GitHub operations when available and authenticated.
- Check `gh auth status` before assuming authentication is broken.
- Prefer terminal-native PR, issue, Actions, and gist operations over browser-only workflows.
- Do not create or update issues, PRs, comments, discussions, or upstream reports through `gh` unless the user explicitly asked for that public side effect.

### Python

- Use `uv` for Python package/project operations unless the repo explicitly requires otherwise or the user asks.
- Run scripts/tests/linters/CLIs through `uv run ...`.
- For skill-only external dependencies, prefer `uvx <tool>` or `uv run --with <package> <command> ...`.
- Do not create/reuse `.venv*` for skill-only tooling.
- Prefer `#!/usr/bin/env -S uv run python` for Python automation scripts.

## Verification and final response

Before final delivery:

- Check relevant diff or generated artifact.
- Run the narrowest meaningful verification.
- For bug/remediation work, confirm the final explanation distinguishes observed facts, verified root cause, invariant, repair boundary, and remaining uncertainty.
- For fixes involving invalid state, malformed persisted data, fallback behavior, compatibility behavior, or local workarounds, confirm the test/check defends the intended invariant rather than merely blessing the symptom.
- For upstream-owned or public-tracker work, confirm explicit user intent before any public side effect.
- For `$st` work, confirm durable and mirrored plans are not visibly drifting.
- For delegated work, integrate results locally before presenting conclusions.
- Clean up temporary files, agents, claims, or scratch state that should not persist.

Final responses should follow the required Response Format and then remain concise and factual: state what changed/found, include proof, mention material risks/blockers, distinguish verified facts from hypotheses when relevant, and include a short orchestration ledger only when orchestration actually ran.
