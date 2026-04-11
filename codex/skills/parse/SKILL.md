---
name: parse
description: Analyze a local codebase and infer the architecture it is actually using, including repo kind, best-fit dominant architecture, directly evidenced coexisting patterns, major subsystem exceptions, confidence, docs-vs-code drift, and repo-fit hints for downstream agents. Use when prompts ask what architecture a repo uses, whether it is really hexagonal or just layered, what subtle patterns shape a repo or slice, how a target slice fits a hybrid monorepo, whether documented architecture matches implementation, or when `$tk` needs a repo-dialect preflight before making a minimal change.
---

# Parse

## Overview

Identify the architecture a repository is using right now from code-first evidence. Produce one best-fit dominant architecture label, note meaningful subsystem variants, capture up to two directly evidenced coexisting patterns when they materially shape seams or contracts, call out architecture drift when docs and implementation disagree, and give narrow repo-fit hints that help downstream agents fit a change to the repo that already exists.

Keep the advice narrow. Describe how to work within the current repo's seams, ownership boundaries, and dialect; do not prescribe target architectures, migrations, or adjacent-skill routing.

## Purpose Boundary

Use `parse` to classify the repo's current-state architecture and produce narrow repo-fit hints. Do not expand it into broad onboarding notes, full architecture reports, or domain-specific audits. Keep the memo architecture-focused and current-state-only.

## Execution Spine

`parse` is a collector-first classification workflow, not a generic license to "read the repo and think about architecture." The required order for a normal run is:

1. run the helper,
2. do the required focused rerun when the helper reports `thin_repo_wide` or mixed signals,
3. only then do the smallest manual trace needed to close the remaining gap,
4. emit the parse memo.

If `parse` is paired with another skill, `parse` still owns this architecture pass. Do not let the companion skill swallow the collector step or replace the parse memo with freeform repo research.

## Zig CLI Iteration Repos

When iterating on the Zig-backed `parse-arch` helper CLI, use these two repos:

- `skills-zig` (`/Users/tk/workspace/tk/skills-zig`): source for the `parse-arch` binary, build/test wiring, release tags, and eval fixtures.
- `homebrew-tap` (`/Users/tk/workspace/tk/homebrew-tap`): Homebrew formula updates and checksum bumps for released `parse-arch` binaries.

## Quick Start

```bash
/Users/tk/.dotfiles/codex/skills/parse/scripts/run_parse_collect.sh /path/to/repo --focus-path src --focus-path test
/Users/tk/.dotfiles/codex/skills/parse/scripts/run_parse_collect.sh --repo-path /path/to/repo --json
```

Use the helper first during normal `$parse` runs. It bootstraps a compatible `parse-arch`, accepts the same paved repo selectors agents actually try (`<repo_path>`, `--repo-path`, `--repo`, `--json`, `--format json`), and always emits JSON.
On repo-wide runs without explicit `--focus-path`, the helper also reports `read_depth_verdict`, `thin_signal_classes`, and `suggested_focus_paths`. Treat `read_depth_verdict: thin_repo_wide` as a required second-pass trigger, not a suggestion.

If you need raw CLI access for release or validation work, use this bootstrap wrapper:

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
  if command -v parse-arch >/dev/null 2>&1 && parse-arch --help 2>&1 | grep -q "parse-arch collect --repo-path <repo_path>"; then
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

  if command -v parse-arch >/dev/null 2>&1 && parse-arch --help 2>&1 | grep -q "parse-arch collect --repo-path <repo_path>"; then
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

## Run Modes

- `quick`: repo kind, dominant architecture, confidence, runner-up line, decisive evidence, and caveats. Use for repo-dialect preflight or fast orientation.
- `standard`: full output contract. Default.
- `deep`: full output contract plus a required focused rerun when repo-wide signals are thin or mixed, and 3-5 decisive `file:line` citations from direct inspection when available.

## Prompt Shortcuts

### Repo-Wide Parse

```
Analyze this repo with `parse`.

Return the full parse memo with repo kind, one dominant architecture label, directly evidenced coexisting patterns, architecture drift, repo-fit advice, and evidence.
Use the helper first. If repo-wide signals are thin or mixed, do the required focused rerun before finalizing the label.
```

### Focused Slice Parse

```
Analyze this repo with `parse`, but optimize for these focus paths:
- <path>
- <path>

Keep one repo-wide dominant label if warranted, but say explicitly when these focus paths are materially different from the repo-wide story.
```

### Drift Check Parse

```
Run `parse` and focus on whether the documented architecture matches the implementation.
Call out docs-vs-code drift explicitly and keep repo-fit advice narrow and current-state-only.
```

## Workflow

1. Establish the repo kind before naming the architecture.
   - Distinguish between application/service, library/SDK, CLI/tooling, monorepo/platform, infra/ops, data/pipeline, or plugin/extension repo shapes.
   - Use repo kind to avoid forcing app-centric labels onto thin libraries or infrastructure repos.

2. Collect static signals first.
   - Run the helper first: `/Users/tk/.dotfiles/codex/skills/parse/scripts/run_parse_collect.sh <repo_path>`.
   - Pass `--focus-path` for each target slice when `focus_paths` are available.
   - Treat the helper command as a required proof artifact for normal parse runs. The final `Evidence` section should name the repo-wide helper command shape you used and, when applicable, the focused rerun command shape too.
   - Use the JSON output to inspect manifests, entrypoints, dependency-direction hints, runtime-boundary hints, architecture-doc claims, scan coverage, subsystem candidates, focus-path observations, `read_depth_verdict`, `thin_signal_classes`, and `suggested_focus_paths`.
   - Treat the helper/collector as evidence collection only. Do not let it choose the final architecture label for you.
   - Do not narrate the parse pass as "now I'm reading source paths" before the helper result is in hand. Manual source inspection is the escalation step after the helper pass, not the substitute for it.
   - The raw collector now supports three repo selectors openly: positional `repo_path`, `--repo-path`, and `--repo`. It also accepts `--json` and `--format json` as no-op compatibility flags because output is always JSON.
   - If the repo-wide helper pass reports `read_depth_verdict: thin_repo_wide`, rerun the helper immediately with its `suggested_focus_paths` before broader manual inspection. Do not stop at the repo-wide JSON just because one architecture signal has a non-zero score.
   - If the helper does not emit usable `suggested_focus_paths`, do one targeted second pass yourself: choose 2-4 likely architecture-defining paths, including at least one path that should confirm the current read and, when plausible, one that could falsify it or surface a coexisting pattern (for example entrypoints, build manifests, the main runtime/core module, public package roots, provider registries, workflow definitions, generated boundaries, or a contract-heavy docs/test slice) and rerun the helper with `--focus-path` for each.
   - When the helper still leaves the repo under-determined, use one named trace instead of ad hoc browsing:
     - `entrypoint -> flow -> boundaries` for application/service, monorepo/platform, and plugin/extension repos: start at `main`, route tables, command registries, workflow definitions, or host/plugin registries; follow one representative request/job/command into orchestration/core modules; end at storage, network, queue, file, or generated boundaries.
     - `public contract -> examples/tests -> core` for `library-sdk` and `cli-tooling` repos: start at exported package roots, public command registries, manifests, or provider/plugin interfaces; follow examples, golden tests, or integration tests that define the contract; end at the implementation modules that actually enforce the seam.
     - `job spec -> stage graph -> sinks` for `data/pipeline` and `infra/ops` repos: start at DAGs, workflow manifests, build/deploy entrypoints, or task registries; trace stage ordering and handoff seams; end at sinks, state stores, providers, or execution adapters.
   - Compare what the repo-wide pass saw with what the focus-path pass surfaced. Use that delta in `Major Subsystems / Coexisting Patterns`, `Repo-Fit Advice`, and `Caveats`.

3. Map the evidence to the curated taxonomy and coexisting-pattern sweep.
   - Read [references/taxonomy.md](references/taxonomy.md).
   - Pick one dominant architecture label from the curated set.
   - Do not lock the dominant label from one cue such as folder names, one framework, or a single collector score. Confirm it across at least 3 distinct evidence surfaces chosen from: entrypoints/runtime wiring, dependency direction, public contract roots, repeated module seams, integration or storage boundaries, configuration/runtime topology, tests/examples-as-contract, or deploy/workflow shape.
   - Name the strongest plausible runner-up label or coexisting pattern and the decisive evidence that kept it secondary.
   - Capture up to 2 directly evidenced coexisting patterns when they materially shape seams, contracts, or control flow. Mark each as `repo-wide modifier`, `slice-local variant`, or `near-miss`, and state why it stays secondary. Promote a pattern to `repo-wide modifier` only when it recurs across at least 3 slices or across 2 independent seam types (for example package layout plus runtime registry, or examples/tests plus generated boundaries). Otherwise keep it `slice-local variant` or `near-miss`.
   - If major slices differ materially, keep the dominant label and add subsystem variants instead of flattening the whole repo into one story.
   - For `library-sdk` and `cli-tooling` repos, positively inspect exported API roots, examples/tests as contract, command registries, provider/plugin seams, and staged passes before defaulting to app-centric labels.
   - Prefer common labels plus explicit hybrid wording over inventing niche names.

4. Derive repo-fit advice.
   - Translate the dominant architecture, coexisting patterns, major subsystems, and any `focus_paths` into narrow advice about seams, ownership, and where a change probably belongs.
   - Keep the advice implementation-fitting: tell downstream agents what to align with, what boundaries to respect, and what not to assume.
   - If confidence is `low`, downshift from positive directives to conservative `do_not_assume` warnings.

5. Escalate only when static evidence is weak or contradictory.
   - Read [references/evidence-playbook.md](references/evidence-playbook.md) before running investigative commands.
   - If the collector feels weak, name the missing signal classes precisely first. Prefer the helper's `thin_signal_classes` when present; otherwise derive them directly from the JSON evidence summary.
   - Use the focused rerun to test both the current dominant read and the strongest plausible competing label or coexisting pattern before broader manual inspection.
   - If another skill is also active, finish the parse-specific escalation first and hand the resulting architecture memo or packet to the companion skill. Do not collapse the parse phase into mixed narration that hides whether the helper and focused rerun actually happened.
   - For `library-sdk` and `cli-tooling` repos, do not accept a repo-wide helper pass as "good enough" when `read_depth_verdict` is thin. Contract surfaces, public roots, staged passes, examples, tests, and docs often carry the architecture-defining seams.
   - Do not jump straight from one weak repo-wide collector pass to "manual inspection." First prove that a focused collector rerun still leaves the architecture under-determined.
   - If the helper or collector path fails, continue with source-first manual inspection only after you state the exact failed command path and the specific signal classes the collector did not supply. Do not fall back to vague “couldn’t use the scripts” language.
   - Use safe, non-mutating probes only when they add meaningful evidence: builds, tests, dependency inspection, or local command help.
   - Stop if the only available probe mutates tracked files, requires secrets, or depends on network-only truth.

6. Produce the memo.
   - Choose one best-fit dominant architecture label even when confidence is low.
   - State confidence and what evidence is missing.
   - Start `Why This Best Fits` with a `Runner-Up:` line naming the strongest competing label or pattern and the decisive reason it lost.
   - Support the load-bearing claims with 3-5 decisive `file:line` citations when direct source inspection was possible. When a claim stays helper-derived, cite the concrete path or signal summary and say so.
   - Include coexisting patterns only when they are directly evidenced, and say why they remain secondary.
   - Include architecture drift when documentation and implementation diverge.
   - Keep critique lightweight: mention mismatches or ambiguity, but do not prescribe a new target architecture.
   - When `focus_paths` materially differ from the repo-wide story, say so explicitly and carry that distinction into the advice.
   - When evidence is mixed, explain why the nearest competing label or coexisting pattern did not win.

## Output Contract

Return these sections in order:

1. `Repo Kind`
2. `Dominant Architecture`
3. `Confidence`
4. `Why This Best Fits`
5. `Major Subsystems / Coexisting Patterns`
6. `Repo-Fit Advice`
7. `Agent Handoff`
8. `Evidence`
9. `Architecture Drift`
10. `Caveats`

For each section:
- `Repo Kind`: Name the repo shape and why it matters for interpretation.
- `Dominant Architecture`: Give one best-fit label from the curated taxonomy.
- `Confidence`: Use `high`, `medium`, or `low` and explain what would change the score.
- `Why This Best Fits`: Start with `Runner-Up: <label or pattern> — <decisive reason it lost>`. Then cite the strongest evidence paths, framework clues, or runtime topology clues. Support the load-bearing claims with 3-5 decisive `file:line` citations when direct source inspection was possible; otherwise cite the concrete helper-derived paths and signal summaries you relied on. When evidence is mixed, say why the nearest competing label or coexisting pattern stayed secondary.
- `Major Subsystems / Coexisting Patterns`: List major slices only when they materially differ from the dominant architecture. Also list 0-2 directly evidenced coexisting patterns when they shape seams, contracts, or control flow. For each coexisting pattern, state its scope (`repo-wide modifier`, `slice-local variant`, or `near-miss`) and why it does not replace the dominant label. Only use `repo-wide modifier` when the pattern recurs across at least 3 slices or across 2 independent seam types; otherwise keep it `slice-local variant` or `near-miss`.
- `Repo-Fit Advice`: Give 3-5 bullets that help a downstream agent fit work to the repo as it exists now. Include likely seams, ownership boundaries, and `do_not_assume` warnings when confidence is weak.
- `Agent Handoff`: Emit one fenced `yaml` block with stable keys: `repo_kind`, `dominant_architecture`, `confidence`, `focus_scope`, `major_subsystems`, `coexisting_patterns`, `architecture_drift`, `repo_fit_hints`, `do_not_assume`, and `evidence_paths`.
- `Evidence`: Separate decisive evidence from supporting evidence. Show at least 3 distinct evidence surfaces for the dominant label. Prefer concrete paths, `file:line` citations when available, module names, entrypoints, signal summaries, the helper's `thin_signal_classes` when present, and the exact collector command shapes you used over general impressions. Say when a focus-path rerun materially changed the read or surfaced a coexisting pattern.
- `Architecture Drift`: Compare docs and implementation when both exist; write `none observed` when there is no meaningful drift.
- `Caveats`: State uncertainty, missing evidence, or overclaim boundaries. Tie caveats to specific missing signals and the compensating paths you inspected, and name plausible but unproven competing labels or patterns explicitly. Avoid generic version-centric caveats unless the binary behavior itself is the issue.

## Guardrails

- Keep code and runtime evidence above docs when they conflict.
- Keep repo-fit advice descriptive and current-state-only; do not turn it into redesign advice.
- If confidence is `low`, keep the advice advisory and make the uncertainty explicit.
- Do not report more than 2 coexisting patterns.
- Do not treat folder names, framework brand names, or one collector score as sufficient proof of the dominant label.
- Do not call a dominant architecture `high` confidence unless it is backed by at least 3 distinct evidence surfaces.
- Do not promote a secondary pattern to dominant unless it changes repo-wide runtime topology, ownership seams, or control flow.
- Do not promote a pattern to `repo-wide modifier` from one interesting file or one slice.
- Do not claim specialized patterns such as CQRS, event sourcing, DDD, anti-corruption layers, or workflow engines without direct repo evidence.
- Do not confuse framework choice with architecture by default; explain whether the framework is shaping or merely hosting the design.
- Do not collapse a mixed monorepo into one label without naming important exceptions or `focus_paths` caveats.
- Do not let a repo-wide label override a slice-local signal when `focus_paths` clearly point at a materially different subsystem.
- Do not use `parse-arch` version strings as stock caveats. If the collector under-read the repo, say which evidence classes were thin and which concrete paths you inspected to compensate.
- Do not suggest migrations, modernizations, or follow-up skills unless the user explicitly asks for that next step.
- Do not present `parse` as a freeform source-reading exercise. If the helper ran, say that it ran; if the helper under-read, say that and show the focused rerun before broader manual inspection.
- Do not let a companion skill such as `liminal`, `codebase-report`, or `codebase-archaeology` absorb the parse workflow. `parse` must still produce an explicit architecture classification pass with collector-backed evidence.

## Quick Heuristics

- `layered` / `n-tier`: controllers, services, repositories, models, or handlers arranged in dependency order.
- `mvc` / `mvvm` / component-driven UI: clear presentation-model/controller boundaries in UI-heavy repos.
- `clean` / `hexagonal` / `onion` / `ports-and-adapters`: domain or application core separated from adapters, infrastructure, or delivery layers.
- `modular monolith`: one deployable codebase with clear internal module boundaries.
- `microservice` / service-oriented: multiple independently shaped services with network or message boundaries.
- `event-driven`: explicit publishers, consumers, brokers, or async event flows dominate control flow.
- `pipeline` / job-oriented: DAGs, jobs, workflows, ETL stages, or scheduled data processing dominate the system.
- `plugin` / extension-based: hosts, hooks, plugins, extensions, or adapter registries are first-class architecture surfaces.
- `library-sdk` / `cli-tooling` repo kinds: exported API roots, examples/tests-as-contract, command registries, provider/plugin seams, or staged passes can matter more than app-style entrypoints.
- `coexisting patterns`: package-by-feature, vertical slices, command/query separation, functional-core/imperative-shell, generated-code boundaries, and plugin seams often refine the read without replacing the dominant label.
- Treat helper-reported `thin_repo_wide` results as an under-read warning even when the top architecture score is non-zero. The second pass is about deepening the evidence, not rewording the same thin read.

## Validation

- `uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py codex/skills/parse`
- `/Users/tk/.dotfiles/codex/skills/parse/scripts/run_parse_collect.sh "$PWD" --focus-path codex/skills/parse/SKILL.md`
- `/Users/tk/.dotfiles/codex/skills/parse/scripts/run_parse_collect.sh /Users/tk/workspace/tk/shift --json | jq -e '.read_depth_verdict == "thin_repo_wide" and (.suggested_focus_paths | index("src"))'`
- `/Users/tk/.dotfiles/codex/skills/parse/scripts/run_parse_collect.sh /Users/tk/.dotfiles --json | jq -e '.read_depth_verdict == "thin_repo_wide" and (.suggested_focus_paths | length > 0)'`
- `run_parse_arch_tool eval --suite "$HOME/workspace/tk/skills-zig/apps/parse-arch/references/eval/suite.yaml"`
- `run_parse_arch_tool doctor --suite "$HOME/workspace/tk/skills-zig/apps/parse-arch/references/eval/suite.yaml" --repo-path "$PWD"`

## Resources

- Taxonomy rules: [references/taxonomy.md](references/taxonomy.md)
- Evidence escalation and memo guidance: [references/evidence-playbook.md](references/evidence-playbook.md)
- Eval suite: `"$HOME/workspace/tk/skills-zig/apps/parse-arch/references/eval/README.md"`
- Static signal collection: `parse-arch collect`
