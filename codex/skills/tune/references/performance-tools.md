# Optional performance utilities

Load only when selecting, using, or maintaining `bench_stats` or `perf_report`.
Tune's performance procedure owns acceptance, preservation, authority, and
reporting. These utilities do not constitute another optimizer or a prerequisite
for ordinary software or agent work. Prefer existing project tooling when it
already answers the question.

## Identity and compatibility

The Zig implementations live in
[skills-zig/apps/lift](https://github.com/tkersey/skills-zig/tree/main/apps/lift).
The distribution remains
[homebrew-tap/Formula/lift.rb](https://github.com/tkersey/homebrew-tap/blob/main/Formula/lift.rb),
installed as `tkersey/tap/lift`. Removing the skill does not rename this app,
formula, release family, or the installed `bench_stats` and `perf_report` binaries.

Resolve the executable and verify its provenance through the known installation
or source/release before running it; a matching name or help string is not a
trust check. For each selected, trusted binary, require successful version/help
output and verify the options needed for that invocation:

```bash
command -v bench_stats && bench_stats --version && bench_stats --help
command -v perf_report && perf_report --version && perf_report --help
```

Run only the line for the selected helper. Inspect
[bench_stats.zig](https://github.com/tkersey/skills-zig/blob/main/apps/lift/scripts/bench_stats.zig)
and
[perf_report.zig](https://github.com/tkersey/skills-zig/blob/main/apps/lift/scripts/perf_report.zig)
at the installed revision when resolving a mismatch. Current help identifies
`bench_stats` / `perf_report` and their options; do not require the obsolete
`bench_stats.zig` / `perf_report.zig` help markers. If provenance, help, version,
or required options cannot be established, do not use that invocation. Continue
with existing project tools or report the specific missing capability. Never
silently substitute an unrelated same-name executable or auto-install a helper.

## Sample statistics

Supply one raw numeric observation per line, with the sample unit, population,
work performed, and baseline/candidate conditions recorded. Do not feed a CSV
summary, timestamps, or arbitrary log text merely because it contains numbers.
`--unit` labels values; it does not convert them. Convert both datasets explicitly
or use `--scale` only after confirming that option and the required factor.

Examples after checking the installed options; set `BASELINE_SAMPLES` and
`CANDIDATE_SAMPLES` to existing authorized files containing values in milliseconds:

```bash
bench_stats --input "${BASELINE_SAMPLES:?baseline samples required}" --unit ms
bench_stats --input "${BASELINE_SAMPLES:?baseline samples required}" \
  --compare "${CANDIDATE_SAMPLES:?candidate samples required}" --unit ms --json
```

Compare mode is optional; older installations lacking `--compare` must use
separate summaries or the existing comparison tool. Retain raw sample count,
variation, and uncertainty. Percentiles or bootstrap intervals from this helper
do not establish service p99, independent samples, an adequate experiment,
behavioral equivalence, or a performance win by themselves.

## Requested report files

Prefer the native [performance report template](../assets/perf-report-template.md)
for a requested standalone/full report. `perf_report` is an optional scaffold,
not a collector of measurement evidence or the reporting-policy owner.

The generator writes a file and may overwrite its output; its default is
`perf-report.md` in the current directory. Before invocation, verify write
authority and select a new, session-owned absolute output path in an authorized
directory. Do not run it under a no-file request or infer overwrite authority
from the existence of a report. After establishing those conditions:

```bash
perf_report --title "Performance comparison" --owner "team" --system "component" \
  --output "${REPORT_PATH:?authorized new absolute report path required}"
```

Fill the output from actual evidence, omit inapplicable fields, and adapt it to
Tune's report. A generated legacy "Lift Compliance" section, `lift_compliance`
footer, score field, or proof label is not a governing rule. Remove such
boilerplate without dropping substantive evidence; do not manufacture a second
compliance report or treat generated placeholders as validation.

## Authorized provisioning and maintenance

Using existing helpers does not authorize installation, rebuilding, release,
or changes to another repository. When provisioning is explicitly authorized,
inspect the current formula/source requirements and use the supported Homebrew
or source-build path for the actual platform and pinned toolchain. Check the
repository's current build targets and output names rather than assuming a
blanket root build is necessary. Recheck the selected installed CLI afterward.

For an authorized helper change, source/build/test ownership remains in
`skills-zig` (`$HOME/workspace/tk/skills-zig` is a conventional checkout, not an
assumption); formula/checksum propagation belongs to `homebrew-tap`
(`$HOME/workspace/tk/homebrew-tap`). Coordinate the affected CLI docs, tests,
release artifacts, and formula under existing publication authority. If that
authority is absent, report the pending propagation instead of releasing.
A skill-only optimization or documentation change does not trigger this workflow.
