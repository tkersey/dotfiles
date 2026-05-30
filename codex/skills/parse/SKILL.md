---
name: parse
description: >-
  Classify a local codebase's current architecture from collector-backed,
  code-first evidence. Use for prompts asking what architecture a repo or slice
  actually uses, whether it is layered/hexagonal/MVC/plugin/pipeline/etc., what
  the strongest runner-up is, which coexisting patterns are directly evidenced,
  whether docs match implementation, or when an implementation agent needs a
  narrow repo-dialect preflight. Do not use for broad repo onboarding, layer
  removal, structural redesign, domain algebra, invariant design, implementation
  specs, or execution planning.
---

# Parse — Architecture Fingerprint

## Mission

`parse` is a narrow architecture classifier.

It identifies the architecture a repository is using **right now** from
code-first evidence. It produces a compact architecture fingerprint: repo kind,
one dominant architecture label, confidence, runner-up/near-miss, material
subsystem variants, up to two directly evidenced coexisting patterns,
docs-vs-code drift, narrow repo-fit hints, and an agent handoff packet.

`parse` is not an architecture designer, codebase onboarding guide,
simplification reviewer, invariant gate, spec generator, or execution planner.
It should leave the user or downstream agent knowing what architecture is
present, not what architecture should replace it.

## Purpose Boundary

Use `parse` when the main question is classification:

- What architecture does this repo use?
- Is this layered, hexagonal, MVC, plugin-based, pipeline-oriented, event-driven,
  modular-monolith, library/SDK, CLI-tooling, or something hybrid?
- What is the strongest runner-up label, and why did it lose?
- Are the architecture docs consistent with the implementation?
- Does this target slice follow the repo-wide architecture or a local variant?
- What repo dialect should a small downstream change respect?

Do not use `parse` when the main question is exploration, redesign, removal,
invariant enforcement, spec writing, or planning. Use the routing boundary below
to decide before starting.

## Routing Boundary

These boundaries are for deciding whether `parse` is the right skill. Do not
turn them into follow-up recommendations in the final parse memo unless the user
explicitly asks what to do next.

| User intent | Use instead |
|---|---|
| "Explain how this repo works", onboarding, entrypoints, domain model, data flow, integrations, tests | `codebase-archaeology` |
| "This is over-engineered", "what can we delete", remove framework/DI/codegen/ORM/GraphQL/infra layers | `reduce` |
| Boundary redesign, repeated validation/policy branching, protocol/state-machine drift, generated provenance loss, callback/effect boundary, explicit IR/law tests | `universalist` |
| Domain algebra, operations/laws, denotational/combinator model, event/workflow algebra, interpreters/law tests | `algebra-driven-design` |
| Source-of-truth, owned invariant, impossible state, validation sprawl, idempotency/retry/order drift, witness parity, enforcement boundary | `invariant-ace` |
| Decision-complete implementation spec, readiness gate, spec lint, invariant challenge before planning | `spec-pipeline` |
| Dependency-ordered execution campaign, rollout/rollback sequencing, task waves | `plan` / `st` / `mesh` |

When `parse` is paired with another skill, `parse` still owns the architecture
fingerprint. Run the collector-first classification pass, emit the parse memo,
and let the companion skill consume the handoff packet. Do not let companion
source exploration swallow the explicit classification step.

## Inputs

Resolve these from the prompt and repository context:

| Input | Default | Notes |
|---|---:|---|
| `repo_path` | current repository | Required root path for inspection. |
| `focus_paths` | none | Repo-relative files/directories when the user names a slice or downstream change target. |
| `mode` | `standard` | `quick`, `standard`, or `deep`. |
| `drift_check` | false | True when the user asks whether docs match implementation. |

## Run Modes

- `quick`: repo kind, dominant architecture, confidence, runner-up line,
  decisive evidence, repo-fit hints, and caveats. Use for repo-dialect preflight
  or fast orientation.
- `standard`: full output contract. Default.
- `deep`: full output contract plus mandatory focused rerun on thin/mixed
  repo-wide signals, and 3-5 direct `file:line` citations when source inspection
  is available.

## CLI Contract

`parse` is a CLI-backed collector-first workflow. A normal run starts with
`parse-arch collect`.

```bash
parse-arch collect /path/to/repo --json
parse-arch collect /path/to/repo --focus-path src --focus-path tests --json
parse-arch collect --repo-path /path/to/repo --json
parse-arch collect --repo /path/to/repo --format json
```

The collector always emits JSON. It should expose these read-depth fields on
repo-wide runs:

```bash
parse-arch collect "$PWD" --json |
  jq -e 'has("read_depth_verdict") and has("thin_signal_classes") and has("suggested_focus_paths") and has("followup_hint")'
```

Treat `read_depth_verdict: thin_repo_wide` as a required second-pass trigger, not
as a warning you can ignore.

If the collector contract check fails, stop the normal parse path and install or
build a compatible collector before finalizing if possible:

```bash
brew install tkersey/tap/parse-arch
brew upgrade tkersey/tap/parse-arch
# or, for local iteration:
(cd "$HOME/workspace/tk/skills-zig" && zig build build-parse-arch -Doptimize=ReleaseFast)
```

If the collector is unavailable and no install/build path is allowed, continue
only after naming the exact failed command and the missing signal classes. The
manual fallback must be conservative and must not pretend to have collector
coverage.

## Execution Spine

Follow this order. Do not reorder it unless the collector is unavailable and you
explicitly record that fallback.

### 1. Establish repo kind before architecture label

Classify the repository shape first:

- `application-service`
- `web-frontend`
- `full-stack-app`
- `library-sdk`
- `cli-tooling`
- `monorepo-platform`
- `infra-ops`
- `data-pipeline`
- `plugin-extension`
- `mixed/other`

Repo kind prevents app-centric architecture labels from being forced onto thin
libraries, tooling repos, generated packages, infrastructure repos, and data
pipelines.

### 2. Collect static signals first

Run the collector before manual source inspection.

- Use `parse-arch collect <repo_path> --json` for repo-wide classification.
- Add one `--focus-path` per target path when `focus_paths` are available.
- Record the exact collector command shape for the `Evidence` section.
- Inspect manifests, entrypoints, dependency-direction hints, runtime-boundary
  hints, public contract roots, architecture-doc claims, scan coverage,
  subsystem candidates, focus-path observations, `read_depth_verdict`,
  `thin_signal_classes`, `suggested_focus_paths`, and `followup_hint`.
- Treat collector output as evidence, not as an oracle. The final architecture
  label is a judgment over evidence surfaces.

Do not narrate a manual source-reading pass before the collector result exists.
Manual inspection is the escalation step after collector evidence, not a
replacement for it.

### 3. Rerun when repo-wide evidence is thin or mixed

Immediately run a focused collector pass when any of these is true:

- `read_depth_verdict == "thin_repo_wide"`;
- the top architecture signal is non-zero but based on only one evidence class;
- two plausible labels are close and unresolved;
- the repo-wide result is dominated by docs or folder names rather than code;
- the user provided `focus_paths` and they may differ from the repo-wide story.

Use the collector's `suggested_focus_paths` when available.

If suggestions are missing, choose 2-4 architecture-defining paths yourself:

- at least one path that should confirm the current read;
- when plausible, one path that could falsify it or expose a coexisting pattern;
- likely candidates: entrypoints, build manifests, runtime/core modules, public
  package roots, command registries, provider/plugin registries, workflow/DAG
  definitions, generated boundaries, docs that claim architecture, and
  tests/examples that define public contracts.

### 4. Escalate to one named manual trace only when needed

If focused collection still leaves the architecture under-determined, perform one
named trace. Keep it narrow.

- `entrypoint -> flow -> boundaries`: for application/service, full-stack,
  monorepo/platform, and plugin/extension repos. Start at `main`, route tables,
  command registries, job/workflow definitions, or host/plugin registries. Follow
  one representative request/job/command into orchestration/core modules. End at
  storage, network, queue, file, generated, or adapter boundaries.
- `public contract -> examples/tests -> core`: for library/SDK and CLI/tooling
  repos. Start at exported API roots, command registries, manifests, or
  provider/plugin interfaces. Follow examples, golden tests, or integration tests
  that define the contract. End at implementation modules that enforce the seam.
- `job spec -> stage graph -> sinks`: for data/pipeline and infra/ops repos.
  Start at DAGs, workflow manifests, build/deploy entrypoints, or task
  registries. Trace stage ordering and handoff seams. End at sinks, state stores,
  providers, deploy targets, or execution adapters.

Use safe, non-mutating probes only when they add meaningful evidence: local help,
build/test discovery, dependency inspection, or read-only scripts. Stop if the
only useful probe mutates tracked files, requires secrets, or depends on
network-only truth.

### 5. Map evidence to the taxonomy

Read `references/taxonomy.md` before final classification when available.

Pick one dominant architecture label from the curated taxonomy. Prefer common
labels plus explicit hybrid wording over invented niche names.

Do not lock the label from one cue. Confirm the dominant label across at least
three distinct evidence surfaces when possible:

- entrypoints/runtime wiring;
- dependency direction;
- public contract roots;
- repeated module seams;
- integration/storage boundaries;
- configuration/runtime topology;
- tests/examples-as-contract;
- deploy/workflow shape;
- architecture docs, when consistent with code.

Name the strongest runner-up label or coexisting pattern and the decisive evidence
that kept it secondary.

### 6. Classify coexisting patterns conservatively

Capture at most two coexisting patterns, and only when they materially shape
seams, contracts, or control flow.

For each pattern, use one scope:

- `repo-wide modifier`: recurs across at least three slices or across two
  independent seam types, such as package layout plus runtime registry or
  examples/tests plus generated boundary.
- `slice-local variant`: real in the named slice but not architecture-defining
  for the whole repo.
- `near-miss`: plausible but missing decisive evidence or subordinate to the
  dominant label.

Do not claim specialized patterns such as CQRS, event sourcing, DDD,
anti-corruption layers, workflow engines, or hexagonal architecture without
direct repo evidence at the appropriate seams.

### 7. Derive repo-fit hints, not redesign advice

Translate the dominant architecture, coexisting patterns, subsystem variants, and
focus-path deltas into narrow implementation-fit hints:

- where similar changes probably belong;
- which seams and ownership boundaries to respect;
- what dependency direction to preserve;
- what not to assume when confidence is low;
- how a focus slice differs from the repo-wide story.

Do not recommend migrations, modernization, layer removal, new abstractions,
invariant enforcement, or follow-up skills unless the user explicitly asks for
next steps.

## Confidence Rubric

Use `high`, `medium`, or `low`.

`high` requires:

- collector coverage is repo-wide OK or focused evidence compensates for thin
  repo-wide coverage;
- at least three distinct evidence surfaces support the dominant label;
- the strongest runner-up has a clear losing reason;
- docs, if present, do not materially contradict implementation.

`medium` applies when:

- the dominant label is well supported but one major signal class is thin;
- the focus slice differs from the repo-wide pattern but the boundary is clear;
- the runner-up is plausible but secondary evidence is insufficient to promote it.

`low` applies when:

- collector coverage is thin and focused rerun/manual trace cannot close the gap;
- only one or two evidence surfaces are available;
- docs and code conflict and code evidence is sparse;
- multiple labels remain plausible after focused inspection.

Low confidence still requires choosing one best-fit label, but all repo-fit hints
must be advisory and include `do_not_assume` warnings.

## Output Contract

Return these sections in order for `standard` and `deep` modes.

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

### 1. Repo Kind

Name the repo shape and why it matters for interpretation. Do not force service
labels onto libraries, tooling, infra, data, plugin, or generated-artifact repos.

### 2. Dominant Architecture

Give one best-fit label from the curated taxonomy. Use hybrid wording only when
both halves are evidenced and one remains dominant.

### 3. Confidence

Use `high`, `medium`, or `low`. Explain what evidence would raise or lower the
score.

### 4. Why This Best Fits

Start with exactly this line:

```text
Runner-Up: <label or pattern> — <decisive reason it lost>
```

Then explain the dominant label using the strongest code-first evidence. Support
load-bearing claims with 3-5 decisive `file:line` citations when direct source
inspection was possible. When a claim is collector-derived, cite concrete paths,
module names, signal summaries, or collector fields and say that it is
collector-derived.

When evidence is mixed, say why the nearest competing label or pattern stayed
secondary.

### 5. Major Subsystems / Coexisting Patterns

List major subsystem variants only when they materially differ from the dominant
architecture.

List 0-2 directly evidenced coexisting patterns. For each:

- `pattern`;
- `scope`: `repo-wide modifier`, `slice-local variant`, or `near-miss`;
- `evidence`;
- `why_secondary`.

If there are no material coexisting patterns, write `none material`.

### 6. Repo-Fit Advice

Give 3-5 bullets that help a downstream agent fit work to the repo as it exists
now. Keep them descriptive and current-state-only.

Include `do_not_assume` warnings when confidence is weak or a focus slice differs
from the repo-wide story.

### 7. Agent Handoff

Emit one fenced YAML block with exactly these stable top-level keys:

```yaml
repo_kind:
dominant_architecture:
confidence:
focus_scope:
runner_up:
major_subsystems:
coexisting_patterns:
architecture_drift:
repo_fit_hints:
do_not_assume:
evidence_paths:
collector_commands:
missing_signal_classes:
classification_only: true
```

Keep values concise and parseable. Do not include implementation tasks or
migration recommendations.

### 8. Evidence

Separate decisive evidence from supporting evidence.

Required fields:

- `collector_commands`: exact command shapes used;
- `read_depth`: repo-wide/focused verdicts and any thin signal classes;
- `decisive_evidence`: at least three distinct evidence surfaces when available;
- `supporting_evidence`: docs, tests, config, package layout, generated artifacts,
  or framework clues that support but do not decide the label;
- `focus_delta`: how focused rerun changed or did not change the repo-wide read.

Prefer concrete paths, file:line citations, module names, entrypoints, signal
summaries, and exact collector fields over general impressions.

### 9. Architecture Drift

Compare docs and implementation when both exist.

Use one of:

- `none observed`;
- `docs overstate architecture`;
- `docs understate architecture`;
- `docs stale or contradictory`;
- `not assessed` with reason.

Keep drift critique lightweight. Do not prescribe a new target architecture.

### 10. Caveats

State uncertainty, missing evidence, and overclaim boundaries. Tie each caveat to
specific missing signals and the compensating paths inspected. Name plausible but
unproven competing labels or patterns explicitly.

Avoid generic version-centric caveats unless the collector binary behavior itself
is the issue.

## Quick Output Mode

For `quick`, return only:

```markdown
## Repo Kind

## Dominant Architecture

## Confidence

## Runner-Up

## Decisive Evidence

## Repo-Fit Hints

## Caveats
```

Still run the collector first unless unavailable.

## Guardrails

- Code and runtime evidence outrank docs when they conflict.
- `parse-arch collect` is the normal first move, not optional decoration.
- Do not present `parse` as freeform source-reading.
- Do not report more than two coexisting patterns.
- Do not call confidence `high` without at least three distinct evidence surfaces.
- Do not treat folder names, framework brands, or a single collector score as
  sufficient proof.
- Do not confuse framework choice with architecture; explain whether the
  framework shapes or merely hosts the design.
- Do not promote a secondary pattern to dominant unless it changes repo-wide
  runtime topology, ownership seams, or control flow.
- Do not promote a `repo-wide modifier` from one interesting file or one slice.
- Do not collapse mixed monorepos into one flat label without naming material
  exceptions or focus-path caveats.
- Do not let a repo-wide label override a focus slice that clearly follows a
  materially different architecture.
- Do not claim CQRS, event sourcing, DDD, anti-corruption layers, workflow
  engines, hexagonal architecture, clean architecture, or ports-and-adapters
  without direct seam evidence.
- Do not use parse-arch version strings as stock caveats. If the collector
  under-read the repo, say which signal classes were thin and which paths you
  inspected to compensate.
- Do not recommend migrations, modernization, layer removal, new abstractions, or
  follow-up skills unless the user explicitly asks for next steps.
- Do not let `codebase-archaeology`, `reduce`, `universalist`,
  `algebra-driven-design`, `invariant-ace`, `spec-pipeline`, or `plan` absorb the
  parse memo when `parse` is active.

## Label Heuristics

Use these as hints, not proof.

- `layered` / `n-tier`: controllers, handlers, services, repositories, models,
  or adapters arranged in dependency order.
- `mvc` / `mvvm` / component-driven UI: explicit presentation-model/controller
  boundaries in UI-heavy repos.
- `clean` / `hexagonal` / `onion` / `ports-and-adapters`: application/domain core
  protected from delivery/infrastructure adapters by explicit ports, interfaces,
  dependency inversion, or adapter registries.
- `modular monolith`: one deployable codebase with meaningful internal module
  boundaries and local calls rather than network/service decomposition.
- `microservice` / service-oriented: multiple independently shaped services with
  network, message, deploy, or ownership boundaries.
- `event-driven`: explicit publishers, consumers, brokers, async event flows, or
  event contracts dominate control flow.
- `pipeline` / job-oriented: DAGs, staged jobs, workflows, ETL phases, scheduled
  tasks, or artifact handoffs dominate the system.
- `plugin` / extension-based: hosts, hooks, plugins, extensions, providers,
  capability registries, or adapter registries are first-class architecture
  surfaces.
- `library-sdk`: exported API roots, public contracts, examples/tests, generated
  clients, and provider seams matter more than app entrypoints.
- `cli-tooling`: command registries, staged passes, file/artifact boundaries,
  stdout/stderr contracts, and golden tests matter more than web/service labels.
- `infra-ops`: desired-state config, deploy graphs, provider modules, CI/CD,
  policy gates, and environment overlays dominate the architecture.
- `data-pipeline`: job specs, stage graphs, schemas, sinks, lineage, and scheduled
  execution dominate the architecture.
- Coexisting patterns such as package-by-feature, vertical slices,
  command/query separation, functional-core/imperative-shell, generated-code
  boundaries, and plugin seams may refine the read without replacing the
  dominant label.

Treat `thin_repo_wide` as an under-read warning even when a top score is non-zero.
The second pass is about deepening evidence, not rewording the same thin read.

## Prompt Shortcuts

### Repo-Wide Architecture Fingerprint

```text
Use $parse to classify this repo's current architecture.
Return the full parse memo. Run parse-arch collect first, rerun focused collection
if repo-wide signals are thin or mixed, choose one dominant label, name the
runner-up, call out coexisting patterns only when directly evidenced, and keep
repo-fit advice current-state-only.
```

### Focused Slice Fingerprint

```text
Use $parse for this repo, focused on:
- <path>
- <path>

Keep one repo-wide dominant label if warranted, but say explicitly whether these
paths follow the repo-wide architecture or a material slice-local variant.
```

### Docs-vs-Code Drift Check

```text
Use $parse to classify the implementation architecture and compare it with the
docs' architecture claims. Keep the result current-state-only; do not prescribe a
migration.
```

### Repo-Dialect Preflight

```text
Use $parse quick mode as a repo-dialect preflight for a small downstream change.
Return the dominant architecture, confidence, runner-up, decisive evidence, and
3-5 repo-fit hints. Do not expand into onboarding or redesign advice.
```

## Validation

Run these when editing this skill or the collector contract:

```bash
uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py codex/skills/parse
parse-arch collect "$PWD" --focus-path codex/skills/parse/SKILL.md --json | jq -e '.read_depth_verdict == "focused"'
parse-arch collect "$HOME/workspace/tk/shift" --json | jq -e 'has("read_depth_verdict") and has("suggested_focus_paths") and has("thin_signal_classes") and has("followup_hint")'
parse-arch collect "$HOME/.dotfiles" --json | jq -e '.read_depth_verdict == "thin_repo_wide" and (.suggested_focus_paths | length > 0)'
parse-arch eval --suite "$HOME/workspace/tk/skills-zig/apps/parse-arch/references/eval/suite.yaml"
parse-arch doctor --suite "$HOME/workspace/tk/skills-zig/apps/parse-arch/references/eval/suite.yaml" --repo-path "$PWD"
```

## Resources

- Taxonomy rules: `references/taxonomy.md`
- Evidence escalation and memo guidance: `references/evidence-playbook.md`
- Collector source and eval suite: `$HOME/workspace/tk/skills-zig/apps/parse-arch`
- Static signal collection: `parse-arch collect`
