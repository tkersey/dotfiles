# Software performance: measurement and preservation

Use with [performance.md](../performance.md) for application, library, service,
build, runtime, and tool code. No skill-package metadata or session archaeology
is required. Read [profiling-tools.md](profiling-tools.md) when selecting platform
commands; verify the repository's pinned toolchain and available tools first.

## Measure the system that matters

Use optimized, production-representative builds with symbols where practical;
record compiler flags, CPU/OS, dependencies, allocator, input sizes, concurrency,
and cache state. Keep baseline/candidate build settings equal unless a build
setting is the declared intervention. Separate compilation/startup from steady
state when the objective requires it. Account for JIT warmup, GC, thermal drift,
background load, virtualization, and profiler overhead. Measure performance
without expensive instrumentation after profiling identifies the mechanism.

For a CLI, repeated wall-clock runs can measure completion latency. For a service,
measure request latency under a specified offered load and concurrency; record
throughput, errors, timeouts, queueing, and saturation together. A closed-loop
client can suppress offered load during stalls (coordinated omission); choose a
load model matching the question and retain request deadlines and failures.
Do not interpret a process benchmark's largest sample as a well-estimated p99.

Use microbenchmarks to test a mechanism, then verify end-to-end benefit. Consume
results so dead-code elimination cannot remove the work; isolate setup only when
setup is not part of the objective. Exercise small/large, skewed/uniform,
cold/warm, adversarial, and failing inputs when relevant. Keep denominators and
work performed constant. Allocation count, retained memory, and peak RSS answer
different questions; do not substitute one for another without explanation.

## State the preservation relation before changing code

Separate these three claims:

- **Argument:** Why the transformation preserves specified observations, with
  explicit assumptions and residual obligations.
- **Executed evidence:** Differential, property/metamorphic, golden, integration,
  stress, sanitizer, model-checking, or formal checks actually run.
- **Limit:** Inputs, schedules, environments, numerical cases, and assumptions
  not covered. A checklist or passing test suite is not an isomorphism proof.

Usually require observational equivalence on the supported domain. A refinement
or approximation must already be permitted or separately authorized. An invertible
representation mapping is neither universally necessary nor established by hashes.
Do not preserve an accidental defect as a requirement; obtain or establish the
intended contract and separate any behavior-changing fix from a speed claim.

Inspect the obligations implicated by the intervention:

| Surface | Preserve or explicitly bound |
|---|---|
| Results | Values, multiplicity, ordering, tie-breaking, stable identity, encoding/schema |
| Failure | Exit status, error categories, partial results, retries, cancellation, timeouts |
| Effects | Writes, transaction boundaries, visibility, exactly-once/idempotency expectations, resource cleanup |
| Numerical | Overflow, rounding, NaN/infinity, signed zero, tolerances, reduction order |
| State/concurrency | Ownership, lifetimes, aliasing, synchronization, atomicity, race freedom, progress/backpressure |
| Randomness | Required distribution and/or exact seeded sequence; equal seeds alone do not prove equivalence |
| Security | Authorization, isolation, validation, collision resistance where required, sensitive-data lifetime |

Do not delete safety checks, use fast-math, introduce unchecked memory access,
or weaken hashing/security merely to improve the measurement. A necessary safety
or numerical change is a separate contract decision, not a hidden optimization.
For concurrency, final output equality does not prove equivalent observable
histories, cancellation behavior, or failure timing.

## Differential and golden oracles

Keep a known baseline executable/revision and fixtures immutable. Generate fresh
candidate outputs into a separate location and compare them to the baseline.
Hashing old golden files only verifies their integrity, not the modified program.
Normalize nondeterministic fields only when the contract declares them irrelevant;
never sort outputs to hide an ordering regression.

A minimal Bash oracle for deterministic stdin/stdout/stderr CLIs follows. Supply
absolute `OLD_BIN`, `NEW_BIN`, and `FIXTURES` paths; both executables must terminate
and run without external effects. Use a fresh scratch directory with write
authority. Arguments, file/network effects, timeouts, nondeterminism, and isolation
need a project-specific adapter; this example does not validate those surfaces.

```bash
set -euo pipefail
: "${OLD_BIN:?absolute baseline executable required}"
: "${NEW_BIN:?absolute candidate executable required}"
: "${FIXTURES:?fixture directory required}"
test -x "$OLD_BIN"
test -x "$NEW_BIN"
test -d "$FIXTURES"
out="$(mktemp -d)"
mkdir "$out/baseline" "$out/candidate"
shopt -s nullglob
count=0
for input in "$FIXTURES"/*; do
  test -f "$input" || continue
  name="$(basename "$input")"
  count=$((count + 1))
  status=0
  "$OLD_BIN" < "$input" > "$out/baseline/$name.stdout" \
    2> "$out/baseline/$name.stderr" || status=$?
  printf '%s\n' "$status" > "$out/baseline/$name.status"
  status=0
  "$NEW_BIN" < "$input" > "$out/candidate/$name.stdout" \
    2> "$out/candidate/$name.stderr" || status=$?
  printf '%s\n' "$status" > "$out/candidate/$name.status"
  for stream in stdout stderr status; do
    cmp "$out/baseline/$name.$stream" "$out/candidate/$name.$stream"
  done
done
test "$count" -gt 0
printf 'Compared %s fixtures; evidence: %s\n' "$count" "$out"
```

For a library, compare old/reference and new implementations over the same
input/state corpus, including boundary and generated cases. Keep the oracle
independent of the optimized implementation. Test meaningful laws, not merely
`new(x) == new(x)`. Where no old implementation is available, use a simple
independent reference or an accepted specification and state its limits.

Useful probes include permutation invariance only when order is irrelevant,
round trips only where inverses are promised, conservation/accounting laws,
monotonicity under stated preconditions, and equivalence across partition sizes.
Retain minimized failing fixtures. Race detectors and sanitizers add evidence;
they neither prove all schedules safe nor provide comparable performance timings.

## Opportunity selection and closure

Use [optimization-techniques.md](optimization-techniques.md) for mechanisms and
[advanced-optimization.md](advanced-optimization.md) when structural reformulation
could dominate local tuning. Count preprocessing, maintenance, invalidation,
materialization, data transfer, memory, and deployment complexity in the benefit.
An average constant-time operation can still govern tail latency or memory;
amortized complexity is not a reason to ignore a measured problem.

Validate the original/final whole workload after the isolated experiment. Keep
reproduction commands, raw before/after results, coverage limits, and a regression
case in the existing project mechanism. Report acceptance, rejection, or an
inconclusive result; never claim speed from asymptotic reasoning alone.
