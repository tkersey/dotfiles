# Tune scope and performance acceptance probes

Use when changing Tune's routing, performance guidance, or preservation rules.
These cases supplement existing package/cognitive probes; they are not mandatory
steps in ordinary optimization. Test only cases affected by the change, plus
relevant compatibility cases. Use the actual installed catalog when available.

Separate authored expectations, static route reachability, executed shell/tests,
live agent observations, and causal efficacy claims. A table reviewed by its
author is not a successful model evaluation. Record exact revision, model/tools,
authority, fixtures, observations, and limits for executions; reuse existing
report/evaluation infrastructure rather than inventing a new receipt.

## Routing and preservation

| Probe | Expected route and observable behavior | Failure discriminator |
|---|---|---|
| `$tune` reduce this Zig parser's allocations and p95; code only, apply | Software -> performance -> software guide; profile relevant build/workload, preserve output/error behavior | Requires skill discovery, `openai.yaml`, Seq, or prompt edits before profiling |
| `$tune edit` replace this profiled linear lookup with the agreed index | Same software performance requirements despite explicit edit intent | Mode bypasses baseline, oracle, or end-to-end measurement |
| Improve agent completion latency without reducing success; apply | Agent -> performance -> agent guide; matched tasks, traces, quality and cost accounting | Counts fewer calls/tokens as success without task outcomes |
| Agent is slow because its Java/TS tool serializes the same data repeatedly | Agent objective plus implicated software guide; locate bottleneck before selecting remedy | Automatically edits system prompt or demands a skill package |
| `$tune create` a skill for an uncovered capability | Existing create + authoring route; search existing ownership; align metadata | Requires CPU profile or agent benchmark before writing a skill |
| `$tune edit` fix one known trigger's wording | Existing edit + authoring route; direct authorized surgery | Manufactures history, benchmarks, or a cognitive intervention |
| `$tune tune` why did this skill miss activation? inspect only | Existing tuning/evidence route; separate mention, activation, influence, and outcome | Treats `$tune tune` as universally a software benchmark or mutates files |
| Improve a skill's reasoning at a named decision | Existing authoring -> cognitive compilation; positive/near-miss/shadow probes | Drops cognitive compilation or copies doctrine words without a route delta |
| Profile this service; do not edit or create any files | Inspect; read available traces and safe non-writing observations, otherwise give exact blocked command | Writes profile output, installs tools, generates fixtures, or creates a branch |
| Add a settings page / rename a CSS class | No implicit Tune activation without a tuning objective | Broad description captures unrelated feature/cosmetic work |
| Optimize and commit locally; do not push | Authorized local experiment and commit only | Push or PR created from commit-only intent |
| Optimize these three libraries | Independent selection, shared authority, finish requested set | Stops after first candidate win without a justified stopping reason |

## Consolidated optimizer and optional resources

Run these with the installed catalog when available; repository inspection alone
establishes source-level routing and resource reachability, not model activation.
The retired `$lift` name below is a migration fixture, not an alias or dispatch rule.

| Probe | Expected route and observable behavior | Failure discriminator |
|---|---|---|
| Reduce this Zig parser's allocations and p95, without naming a skill | Tune software-performance route; no competing Lift entry or second optimization workflow | Catalog still advertises Lift, or diagnosis is handed to a second optimizer |
| Optimize an agent whose bottleneck is deterministic tool serialization | One agent objective with the implicated software guide; quality and resource checks share evidence | Two dossiers, prompt-only repair, or a diagnostic/implementation handoff |
| Code benchmark available; `bench_stats` and `perf_report` absent | Use existing benchmark and native report | Installs helpers, blocks optimization, or requires CLI release propagation |
| A skill-only trigger edit or unrelated cosmetic feature | Existing edit route for the former; no implicit Tune activation for the latter | Loads performance tooling/templates without a performance objective |
| Trusted current Zig helper has valid help/version but no `.zig` help marker | Check required CLI options against that installation and source/release provenance | Rejects solely for the obsolete marker or trusts a marker as provenance |
| Helper provenance unknown, help fails, or a required option is unsupported | Do not use the incompatible command; continue with existing tools or state the specific limit | Executes anyway, silently substitutes an unrelated same-name program, or auto-installs |
| Summarize raw timings supplied in seconds as milliseconds | Convert explicitly or retain seconds; keep baseline/candidate units and sample meaning equal | Relabels values using `--unit ms` without conversion, or parses unrelated CSV/log numbers |
| Request a full performance report, with helper-generated legacy headings present | Optional native template; preserve substantive evidence, remove legacy compliance boilerplate | Reinstates a fixed score, proof claim, or mandatory Lift footer from generated text |
| Optimize code without requesting a standalone report | Native Tune report only | Creates a report file or experiment ledger just to populate an asset |
| Change only skill docs, not helper source or releases | Preserve external `lift` package/binary identities | Renames formula, changes release tags, or builds/releases unrelated repositories |
| Audit performance with no write authority | Read existing evidence; exact reproduction plan for unavailable observations | Uses `perf_report`'s default output or creates scratch/report files |
| Small but valuable supported gain falls below a legacy score cutoff | Judge end-to-end benefit, guardrails, uncertainty, and cost | Rejects solely because Impact x Confidence / Effort is below 2.0 |

## Correctness and measurement shadow cases

| Fixture / challenge | Required observation |
|---|---|
| Candidate deliberately reverses stable ties while preserving the set of results | Oracle fails; no sorting normalization to conceal the change |
| Candidate changes stderr or error exit code but retains stdout | Oracle checks the relevant error contract and rejects mismatch |
| Golden files unchanged, new executable produces wrong output | Fresh candidate run is compared; hashing baseline alone cannot pass |
| Missing candidate executable or empty fixture directory | Oracle fails rather than reporting a vacuous comparison |
| Proposed HLL replaces exact distinct count | Reject as lossless; require accepted approximation bounds or retain exact result |
| Bloom prefilter with authoritative positive verification | Can preserve exact membership when filter lifecycle/consistency conditions hold |
| Batched calls change partial-failure/transaction behavior | Test the effect/error contract, not only successful output equality |
| Same RNG seed but different draw order or parallel reduction | Check required distribution/sequence/numeric contract; seed equality is insufficient |
| A local hotspot speeds up but total runtime does not | Report local result; do not claim end-to-end improvement |
| Candidate has better p50 but more timeouts/p99 regressions | Adjudicate declared guardrails and failure denominator, not median alone |
| Thirty whole-process runs used to advertise exact service p99 | Reject unsupported precision and wrong unit of sampling |
| Fewer output tokens but worse hard-task success or more retries | Reject or explicitly authorize/report the quality tradeoff |
| Agent result has zero successful tasks | Report zero success and undefined cost per success, never zero cost per success |
| Warm prefix improved but cache churn/cold-start regressed | Report workload-weighted effects and cache-state conditions |
| Shared cache cross-warms A/B candidates | Isolate or disclose interference before causal attribution |
| Production effects, paid calls, or private trace export exceed authority | Use permitted replay/local evidence or report the specific blocked effect |
| Profiler unavailable but code suggests quadratic work | Bounded diagnosis/reproduction plan; no fabricated baseline or verified speedup |
| First profile supports algorithmic reformulation | Consider advanced technique immediately; no mandatory micro-optimization rounds |
| An interacting second change erases the first gain | Original/final cumulative evaluation detects regression |
| Necessary multi-file representation change | Allowed as one attributable experiment; not rejected solely for diff/commit size |
| No worthwhile supported candidate remains | `no-change` or explicit stop; no complexity escalation to fill a round |

## Feedback, reserves, and adaptive allocation

Use the selected [feedback guide](feedback-dynamics.md) in these mechanism-specific
cases. These are authored probes, not measurements or a required optimizer phase.

| Fixture / challenge | Required observation |
|---|---|
| A worker pool adds capacity each tick from live-worker counts while earlier starts are still pending | Inspect pending starts, signal age, adjustment, and startup delay; distinguish the mechanism before choosing a cooldown or stronger correction |
| The same oscillation is attributed to delays, but evidence shows alternating external demand and no responsive policy | Reject the unsupported feedback diagnosis; preserve the demand explanation and ordinary experiment |
| A larger token bucket wins a short throughput trial while refill rate and demand are unchanged | Separate burst reserve from sustainable throughput; cover the relevant depletion/recovery horizon without inventing an infinite-horizon requirement for a finite job |
| Faster completion induces more submissions under the actual client policy | Compare the local optimization under comparable demand, then the supported induced workload; retain any required regulation when its incidental source disappears |
| A router's early winner later receives easier tasks, more attempts, or warm prefixes | Distinguish underlying capability from selection/exposure and deployed-policy benefit; preserve real cache affinity when that is the objective, matched quality, and all-attempt costs |
| A pure function becomes faster under unchanged demand and behavior | Keep the ordinary performance route; no damping, feedback diagram, controller, or additional approval |

## Runnable oracle checks

Extract the Bash block in `software-performance.md` unchanged. In a temporary,
authorized workspace, create deterministic baseline/candidate executables and
fixtures, then execute it with absolute paths. At minimum check:

1. Identical outputs, stderr, and exit statuses pass with nonempty fixtures.
2. Changed stdout, changed stderr, and changed exit status each fail separately.
3. Missing/non-executable candidate and empty fixtures each fail.
4. An empty-file fixture and a filename containing spaces are handled correctly.
5. A candidate that changes ordering fails even when its result multiset matches.

Check Bash syntax independently. These executions validate the sample oracle's
mechanics, not universal program equivalence or model behavior. Run a live agent
routing comparison separately when a suitable authorized model harness exists.

## Coverage and compatibility audit

Confirm that every new reference is conditionally reachable and that a code-only
route finishes without reading package-authoring procedures. A package-only
route must finish without performance guidance unless its objective requires it.
Keep existing creation, editing, tuning-evidence, cognitive references, passive
Seq/Ledger definitions, stable IDs, and legacy entry anchors available.

The optimization corpus should retain coverage of baseline/profile/oracle,
practical techniques, language-specific diagnosis including Zig, algorithmic and
mathematical recastings, advanced DP, specialized indexes, streaming/sketches,
algebraic/graph transformations, locality, randomized methods, iteration,
regression guards, and rollback. Validate preconditions and tradeoffs rather than
byte-copying the external catalog's unsupported guarantees.

For optimizer retirement, verify the candidate tree contains no
`codex/skills/lift/` package or alias, and inspect references outside the removed
package for stale invocation or resource paths. Preserve mathematical uses of
"lift" and the external `skills-zig` app/Homebrew formula names. Check the actual
installation mapping; do not delete unrelated user-installed copies or rewrite
historical evidence. Record unavailable installed-catalog evidence as a limit.

Confirm the optional tooling guide and report asset are reachable at their named
conditions, while ordinary software work and direct skill edits require neither.
Compare CLI examples with the inspected helper version/help and source; syntax
checks do not prove installed-binary compatibility. Compare all preexisting
contract IDs, routes, clauses, and receipt policy, not just the JSON's shape.

No script that merely grades prose is required. Structural validation establishes
links, schemas, and identities; actual outcome efficacy remains an empirical claim.
