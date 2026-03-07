---
name: parse
description: Analyze a local codebase and infer the architecture it is actually using, including dominant style, major subsystem variants, confidence, and declared-vs-implemented drift. Use when prompts ask what architecture a repo uses, whether it is layered, MVC, MVVM, clean, hexagonal, onion, modular monolith, microservice, event-driven, pipeline-oriented, or plugin-based, how major subsystems differ, or whether the documented architecture matches the implementation.
---

# Parse

## Overview

Identify the architecture a repository is using right now from code-first evidence. Produce one best-fit dominant architecture label, note meaningful subsystem variants, and call out architecture drift when docs and implementation disagree.

Keep the skill focused on identification. Do not turn the result into redesign advice, refactoring steps, or adjacent-skill routing.

## Workflow

1. Establish the repo kind before naming the architecture.
   - Distinguish between application/service, library/SDK, CLI/tooling, monorepo/platform, infra/ops, data/pipeline, or plugin/extension repo shapes.
   - Use repo kind to avoid forcing app-centric labels onto thin libraries or infrastructure repos.

2. Collect static signals first.
   - Run `python3 codex/skills/parse/scripts/collect_architecture_signals.py <repo-path>`.
   - Use the JSON output to inspect manifests, entrypoints, framework hints, dependency-direction hints, service boundaries, architecture-doc claims, and subsystem candidates.
   - Treat the script as evidence collection only. Do not let it choose the final architecture label for you.

3. Map the evidence to the curated taxonomy.
   - Read [references/taxonomy.md](references/taxonomy.md).
   - Pick one dominant architecture label from the curated set.
   - If major slices differ materially, keep the dominant label and add subsystem variants instead of flattening the whole repo into one story.
   - Prefer common labels plus explicit hybrid wording over inventing niche names.

4. Escalate only when static evidence is weak or contradictory.
   - Read [references/evidence-playbook.md](references/evidence-playbook.md) before running investigative commands.
   - Use safe, non-mutating probes only when they add meaningful evidence: builds, tests, dependency inspection, or local command help.
   - Stop if the only available probe mutates tracked files, requires secrets, or depends on network-only truth.

5. Produce the memo.
   - Choose one best-fit dominant architecture label even when confidence is low.
   - State confidence and what evidence is missing.
   - Include architecture drift when documentation and implementation diverge.
   - Keep critique lightweight: mention mismatches or ambiguity, but do not prescribe a new target architecture.

## Output Contract

Return these sections in order:

1. `Repo Kind`
2. `Dominant Architecture`
3. `Confidence`
4. `Why This Best Fits`
5. `Major Subsystems`
6. `Evidence`
7. `Architecture Drift`
8. `Caveats`

For each section:
- `Repo Kind`: Name the repo shape and why it matters for interpretation.
- `Dominant Architecture`: Give one best-fit label from the curated taxonomy.
- `Confidence`: Use `high`, `medium`, or `low` and explain what would change the score.
- `Why This Best Fits`: Cite the strongest evidence paths, framework clues, or runtime topology clues.
- `Major Subsystems`: List major slices only when they materially differ from the dominant architecture.
- `Evidence`: Prefer concrete paths, module names, entrypoints, and signal summaries over general impressions.
- `Architecture Drift`: Compare docs and implementation when both exist; write `none observed` when there is no meaningful drift.
- `Caveats`: State uncertainty, missing evidence, or overclaim boundaries.

## Guardrails

- Keep code and runtime evidence above docs when they conflict.
- Do not claim specialized patterns such as CQRS, event sourcing, or DDD without direct repo evidence.
- Do not confuse framework choice with architecture by default; explain whether the framework is shaping or merely hosting the design.
- Do not collapse a mixed monorepo into one label without naming important exceptions.
- Do not suggest migrations, modernizations, or follow-up skills unless the user explicitly asks for that next step.

## Quick Heuristics

- `layered` / `n-tier`: controllers, services, repositories, models, or handlers arranged in dependency order.
- `mvc` / `mvvm` / component-driven UI: clear presentation-model/controller boundaries in UI-heavy repos.
- `clean` / `hexagonal` / `onion` / `ports-and-adapters`: domain or application core separated from adapters, infrastructure, or delivery layers.
- `modular monolith`: one deployable codebase with clear internal module boundaries.
- `microservice` / service-oriented: multiple independently shaped services with network or message boundaries.
- `event-driven`: explicit publishers, consumers, brokers, or async event flows dominate control flow.
- `pipeline` / job-oriented: DAGs, jobs, workflows, ETL stages, or scheduled data processing dominate the system.
- `plugin` / extension-based: hosts, hooks, plugins, extensions, or adapter registries are first-class architecture surfaces.

## Trigger Examples

- "What architecture is this repo using?"
- "Figure out whether this codebase is actually hexagonal or just layered."
- "Analyze this monorepo and tell me the dominant architecture plus subsystem exceptions."
- "Does the documented clean architecture match what the code implements?"

## Resources

- Taxonomy rules: [references/taxonomy.md](references/taxonomy.md)
- Evidence escalation and memo guidance: [references/evidence-playbook.md](references/evidence-playbook.md)
- Static signal collection: `python3 codex/skills/parse/scripts/collect_architecture_signals.py <repo-path>`
