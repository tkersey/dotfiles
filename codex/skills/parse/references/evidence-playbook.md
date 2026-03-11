# Evidence Playbook

Use this playbook when static structure alone is not enough to justify the final architecture memo.

## Static-First Checklist

Start with the collector script, then inspect only the strongest evidence paths it returns across code structure, build graph, tests/examples, runtime or deploy surfaces, and docs/ADRs:

- manifests and dependency files
- top-level entrypoints and runnable surfaces
- dependency-direction hints and focus-slice observations
- public package roots, examples, benchmarks, or contract tests in `library-sdk` repos
- command registries, provider registries, generated boundaries, or workflow definitions when present
- architecture docs or ADRs
- folders that imply delivery, domain, persistence, adapters, services, jobs, or plugins
- framework-specific organization markers
- deployment or orchestration files that reveal runtime boundaries

Prefer concrete paths and dependency direction clues over folder-name aesthetics.

## Target Slice First When You Have One

If the caller already knows the target files or subsystem, pass them as `focus_paths` to the collector and compare slice-local evidence with repo-wide evidence.

- Use repo-wide signals to understand the dominant story.
- Use `focus_paths` to see whether the target slice is a meaningful exception.
- If the slice differs materially, say so in `Major Subsystems / Coexisting Patterns`, `Repo-Fit Advice`, and `Agent Handoff`.

## Weak-Signal Recovery

If the initial repo-wide `parse-arch collect` pass is thin, do one focused collector rerun before broader manual inspection.

- Choose 2-4 likely architecture-defining paths from the first pass or from obvious ownership seams. Include at least one path that should confirm the current dominant read and, when plausible, one that could falsify it or surface a coexisting pattern:
  - build/manifests
  - entrypoints or public package roots
  - the dominant runtime/core module
  - plugin or provider registries, workflow/job definitions, generated-code roots, or read/write split directories when those are plausible competing patterns
  - docs/tests/examples only when they materially define the contract
- Rerun `parse-arch collect` with repeatable `--focus-path` flags for those slices.
- Compare repo-wide versus focus-path evidence explicitly:
  - which signal classes stayed thin
  - which subsystem boundaries or coexisting patterns only became visible in the focused pass
  - whether the focused pass changed the dominant label or only clarified subsystem exceptions or secondary patterns
- Only after that focused rerun should you lean heavily on direct source/doc inspection.

## Coexisting Pattern Sweep

Once a dominant label candidate emerges, do one short sweep for up to 2 directly evidenced secondary patterns.

- Look first at surfaces most likely to encode subtle patterns:
  - feature-local package trees or repeated capability modules
  - handlers, commands, queries, or read-model directories
  - public package roots plus examples/tests-as-contract
  - plugin/provider registries or extension contracts
  - workflow, activity, or durable-execution definitions
  - generated directories and authoritative schemas
  - translation layers around external or legacy systems
- For each candidate pattern, record:
  - strongest evidence path
  - scope: `repo-wide modifier`, `slice-local variant`, or `near-miss`
  - why it stays secondary instead of replacing the dominant label
- If no candidate clears the threshold, write `none observed` rather than stretching the taxonomy.

## Investigative Mode

Escalate beyond static inspection only when the architecture is unclear or contradictory.

Safe probes:
- `make test`, `npm test`, `cargo test`, `go test`, `zig build test`, or equivalent non-mutating checks
- help or dry-run commands for local CLIs
- dependency listing commands
- local build commands that write only build artifacts or caches

Stop when:
- the command would edit tracked files
- the command requires secrets or credentials
- the command only becomes meaningful with network-only truth
- the command starts infrastructure or external services you cannot verify safely

## Confidence Rubric

- `high`: structure, dependency direction, and runtime boundaries all align on the same dominant architecture
- `medium`: the best-fit label is clear, but one major boundary or subsystem remains ambiguous
- `low`: the skill can still choose a best fit, but key evidence is missing, contradictory, or unusually thin

Always explain what evidence would raise or lower confidence.

## Advice Gating

- `high`: give clear repo-fit hints about seams, ownership, and what shape of change is most compatible.
- `medium`: give repo-fit hints, but include at least one explicit caveat or alternate interpretation when the slice is mixed.
- `low`: keep advice advisory-only, emphasize `do_not_assume`, and avoid strong claims about the right seam unless the evidence is direct.

## Docs Weighting

- Docs can seed hypotheses quickly.
- Docs do not override implementation.
- If the repo says "clean architecture" but adapters reach directly into persistence or framework layers, record that as drift and classify the implemented shape instead.

## Caveat Wording

- Prefer caveats like "repo-wide collector signals were thin on dependency direction, so I inspected `build.zig`, `src/core`, and `test/` directly" over generic caveats about the installed binary version.
- Mention the binary version only when the CLI behavior itself blocked a needed flag or output mode.
- If the collector under-read the repo, say what it still got right and what evidence classes required compensation.

## Memo Template

Use this exact section order:

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

Keep the memo usable for both humans and agents:

- Start with the conclusion, not the evidence dump.
- Cite concrete paths or surfaces, and when evidence is mixed, say why the nearest competing label or coexisting pattern lost.
- Keep subsystem and coexisting-pattern notes short unless they materially change the interpretation.
- Keep critique lightweight and descriptive.
- Keep `Repo-Fit Advice` current-state-only; do not slide into redesign guidance.
- In `Agent Handoff`, emit one fenced `yaml` block with stable keys: `repo_kind`, `dominant_architecture`, `confidence`, `focus_scope`, `major_subsystems`, `coexisting_patterns`, `architecture_drift`, `repo_fit_hints`, `do_not_assume`, and `evidence_paths`.
