---
name: parse
description: Analyze a local codebase and infer the architecture it is actually using, including repo kind, best-fit dominant architecture, major subsystem exceptions, confidence, docs-vs-code drift, and repo-fit hints for downstream agents. Use when prompts ask what architecture a repo uses, whether it is really hexagonal or just layered, how a target slice fits a hybrid monorepo, whether documented architecture matches implementation, or when `$tk` needs a repo-dialect preflight before making a minimal change.
---

# Parse

## Overview

Identify the architecture a repository is using right now from code-first evidence. Produce one best-fit dominant architecture label, note meaningful subsystem variants, call out architecture drift when docs and implementation disagree, and give narrow repo-fit hints that help downstream agents fit a change to the repo that already exists.

Keep the advice narrow. Describe how to work within the current repo's seams, ownership boundaries, and dialect; do not prescribe target architectures, migrations, or adjacent-skill routing.

## Zig CLI Iteration Repos

When iterating on the Zig-backed `parse-arch` helper CLI, use these two repos:

- `skills-zig` (`/Users/tk/workspace/tk/skills-zig`): source for the `parse-arch` binary, build/test wiring, release tags, and eval fixtures.
- `homebrew-tap` (`/Users/tk/workspace/tk/homebrew-tap`): Homebrew formula updates and checksum bumps for released `parse-arch` binaries.

## Quick Start

```bash
run_parse_arch_tool() {
  install_parse_arch_direct() {
    local repo="${SKILLS_ZIG_REPO:-$HOME/workspace/tk/skills-zig}"
    if ! command -v zig >/dev/null 2>&1; then
      echo "zig not found. Install Zig from https://ziglang.org/download/ and retry." >&2
      return 1
    fi
    if [ ! -d "$repo" ]; then
      echo "skills-zig repo not found at $repo." >&2
      echo "clone it with: git clone https://github.com/tkersey/skills-zig \"$repo\"" >&2
      return 1
    fi
    if ! (cd "$repo" && zig build build-parse-arch -Doptimize=ReleaseFast); then
      echo "direct Zig build failed in $repo." >&2
      return 1
    fi
    if [ ! -x "$repo/zig-out/bin/parse-arch" ]; then
      echo "direct Zig build did not produce $repo/zig-out/bin/parse-arch." >&2
      return 1
    fi
    mkdir -p "$HOME/.local/bin"
    install -m 0755 "$repo/zig-out/bin/parse-arch" "$HOME/.local/bin/parse-arch"
  }

  local os="$(uname -s)"
  if command -v parse-arch >/dev/null 2>&1 && parse-arch --help 2>&1 | grep -q "parse_arch.zig"; then
    parse-arch "$@"
    return
  fi

  if [ "$os" = "Darwin" ]; then
    if ! command -v brew >/dev/null 2>&1; then
      echo "homebrew is required on macOS: https://brew.sh/" >&2
      return 1
    fi
    if ! brew install tkersey/tap/parse-arch; then
      echo "brew install tkersey/tap/parse-arch failed." >&2
      return 1
    fi
  elif ! (command -v parse-arch >/dev/null 2>&1 && parse-arch --help 2>&1 | grep -q "parse_arch.zig"); then
    if ! install_parse_arch_direct; then
      return 1
    fi
  fi

  if command -v parse-arch >/dev/null 2>&1 && parse-arch --help 2>&1 | grep -q "parse_arch.zig"; then
    parse-arch "$@"
    return
  fi

  echo "parse-arch binary missing or incompatible after install attempt." >&2
  if [ "$os" = "Darwin" ]; then
    echo "expected install path: brew install tkersey/tap/parse-arch" >&2
  else
    echo "expected direct path: SKILLS_ZIG_REPO=<skills-zig-path> zig build build-parse-arch -Doptimize=ReleaseFast" >&2
  fi
  return 1
}
```

## Inputs

- `repo_path`: required root path for the repository under inspection.
- `focus_paths`: optional repo-relative files or directories for the slice the caller cares about. Use these when a downstream agent already knows the target files or subsystem.

## Workflow

1. Establish the repo kind before naming the architecture.
   - Distinguish between application/service, library/SDK, CLI/tooling, monorepo/platform, infra/ops, data/pipeline, or plugin/extension repo shapes.
   - Use repo kind to avoid forcing app-centric labels onto thin libraries or infrastructure repos.

2. Collect static signals first.
   - Run the Zig collector via `parse-arch collect`.
   - Pass `--focus-path` for each target slice when `focus_paths` are available.
   - Use the JSON output to inspect manifests, entrypoints, dependency-direction hints, runtime-boundary hints, architecture-doc claims, scan coverage, subsystem candidates, and focus-path observations.
   - Treat the script as evidence collection only. Do not let it choose the final architecture label for you.

3. Map the evidence to the curated taxonomy.
   - Read [references/taxonomy.md](references/taxonomy.md).
   - Pick one dominant architecture label from the curated set.
   - If major slices differ materially, keep the dominant label and add subsystem variants instead of flattening the whole repo into one story.
   - Prefer common labels plus explicit hybrid wording over inventing niche names.

4. Derive repo-fit advice.
   - Translate the dominant architecture, major subsystems, and any `focus_paths` into narrow advice about seams, ownership, and where a change probably belongs.
   - Keep the advice implementation-fitting: tell downstream agents what to align with, what boundaries to respect, and what not to assume.
   - If confidence is `low`, downshift from positive directives to conservative `do_not_assume` warnings.

5. Escalate only when static evidence is weak or contradictory.
   - Read [references/evidence-playbook.md](references/evidence-playbook.md) before running investigative commands.
   - Use safe, non-mutating probes only when they add meaningful evidence: builds, tests, dependency inspection, or local command help.
   - Stop if the only available probe mutates tracked files, requires secrets, or depends on network-only truth.

6. Produce the memo.
   - Choose one best-fit dominant architecture label even when confidence is low.
   - State confidence and what evidence is missing.
   - Include architecture drift when documentation and implementation diverge.
   - Keep critique lightweight: mention mismatches or ambiguity, but do not prescribe a new target architecture.
   - When `focus_paths` materially differ from the repo-wide story, say so explicitly and carry that distinction into the advice.

## Output Contract

Return these sections in order:

1. `Repo Kind`
2. `Dominant Architecture`
3. `Confidence`
4. `Why This Best Fits`
5. `Major Subsystems`
6. `Repo-Fit Advice`
7. `Agent Handoff`
8. `Evidence`
9. `Architecture Drift`
10. `Caveats`

For each section:
- `Repo Kind`: Name the repo shape and why it matters for interpretation.
- `Dominant Architecture`: Give one best-fit label from the curated taxonomy.
- `Confidence`: Use `high`, `medium`, or `low` and explain what would change the score.
- `Why This Best Fits`: Cite the strongest evidence paths, framework clues, or runtime topology clues.
- `Major Subsystems`: List major slices only when they materially differ from the dominant architecture.
- `Repo-Fit Advice`: Give 3-5 bullets that help a downstream agent fit work to the repo as it exists now. Include likely seams, ownership boundaries, and `do_not_assume` warnings when confidence is weak.
- `Agent Handoff`: Emit one fenced `yaml` block with stable keys: `repo_kind`, `dominant_architecture`, `confidence`, `focus_scope`, `major_subsystems`, `architecture_drift`, `repo_fit_hints`, `do_not_assume`, and `evidence_paths`.
- `Evidence`: Prefer concrete paths, module names, entrypoints, and signal summaries over general impressions.
- `Architecture Drift`: Compare docs and implementation when both exist; write `none observed` when there is no meaningful drift.
- `Caveats`: State uncertainty, missing evidence, or overclaim boundaries.

## Guardrails

- Keep code and runtime evidence above docs when they conflict.
- Keep repo-fit advice descriptive and current-state-only; do not turn it into redesign advice.
- If confidence is `low`, keep the advice advisory and make the uncertainty explicit.
- Do not claim specialized patterns such as CQRS, event sourcing, or DDD without direct repo evidence.
- Do not confuse framework choice with architecture by default; explain whether the framework is shaping or merely hosting the design.
- Do not collapse a mixed monorepo into one label without naming important exceptions or `focus_paths` caveats.
- Do not let a repo-wide label override a slice-local signal when `focus_paths` clearly point at a materially different subsystem.
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

## Validation

- `uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py codex/skills/parse`
- `run_parse_arch_tool eval --suite "$HOME/workspace/tk/skills-zig/apps/parse-arch/references/eval/suite.yaml"`
- `run_parse_arch_tool doctor --suite "$HOME/workspace/tk/skills-zig/apps/parse-arch/references/eval/suite.yaml" --repo-path "$PWD"`

## Resources

- Taxonomy rules: [references/taxonomy.md](references/taxonomy.md)
- Evidence escalation and memo guidance: [references/evidence-playbook.md](references/evidence-playbook.md)
- Eval suite: `"$HOME/workspace/tk/skills-zig/apps/parse-arch/references/eval/README.md"`
- Static signal collection: `parse-arch collect`
