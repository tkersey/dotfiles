# Zig engineering contracts and Tiger Style adaptation

Use for consequential resource, assertion, control-flow, or systems-design
questions, and for explicit Tiger Style review. Do not turn every edit into a
resource inventory. Preserve repository-enforced style and limits.

Priorities remain safety and semantic correctness, then predictable performance
and bounded resource use, then developer experience and maintainability. Prefer
representations and ownership boundaries that establish invariants structurally.

## Bounded work

For work that can grow, wait, retry, recurse, allocate, or fan out, identify the
relevant input/structural bound, admission limit, deadline/cancellation contract,
or resource budget and its terminal outcome. A deliberately long-lived service
loop needs a liveness/shutdown contract, not an arbitrary iteration cap. Avoid
silently changing semantics by inserting unexplained limits.

General CLIs may allocate after startup when aggregate memory is bounded,
ownership is clear, and allocation failure is handled. Long-lived services and
hot data planes should prefer startup allocation, fixed-capacity pools, and
bounded admission when they fit the workload. Budget exhaustion is an operating
error unless a real precondition makes it impossible; do not hide it with
`catch unreachable`.

## Invariants and assertions

Use independent assertion pairs for safety-relevant invariants where they catch
different failure modes: before/after transitions, producer/consumer boundaries,
or positive/negative space. Repeating the same predicate twice is not independent
assurance. An invariant made unrepresentable does not require redundant runtime
checks solely to fill an assertion inventory. Document subtle preconditions and
exceptions where the code or reviewer needs them, not in obligatory empty forms.

Distinguish programmer bugs from domain, resource, and environment errors. The
advertised failure guarantee governs rollback; see [transitions](atomic_transition_playbook.md).

## Control flow and size

Target at most 70 physical lines for new/growing functions and 100 Unicode code
points for changed lines unless repository convention requires otherwise. These
are review signals, not correctness predicates or mandatory refactoring quotas.
Do not split a coherent operation into worse abstractions merely to satisfy a
metric. Existing debt should not grow silently; explain a consequential exception.

Use a network/disk/memory/CPU sketch when it informs a design or performance
decision. Do not manufacture a non-applicability report for a local syntax change.
Benchmark performance claims rather than inferring them from stylistic conformity.

## Hazardous boundaries

Zig has no Rust-style `unsafe` keyword. Runtime safety, ABI, and ownership
assumptions still matter for raw casts/pointers, `undefined`, `unreachable`,
`@setRuntimeSafety(false)`, packed/extern layout, FFI, MMIO, atomics, arithmetic,
and SIMD. A token match locates a site; it does not establish a defect.

Distinguish irreducible boundaries (shrink and validate the wrapper contract),
performance/footprint alternatives (retain a reference and measure), and hazards
that can be replaced with checked witnesses. Preserve valid fast paths when their
contracts and evidence hold. Use the detailed [hazard audit](hazardous_code_audit_playbook.md)
and [boundary playbook](unsafe_boundary_playbook.md) selectively.
