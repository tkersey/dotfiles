# Zig Tiger Style Playbook

## Purpose

This playbook adapts
[TigerBeetle's TigerStyle](https://raw.githubusercontent.com/tigerbeetle/tigerbeetle/refs/heads/main/docs/TIGER_STYLE.md)
to `$zig` work across libraries, command-line tools, build logic, protocol code,
agent tooling, and long-lived services.

The adaptation is deliberate rather than literal. TigerBeetle is a
safety-critical database with a tightly controlled runtime. A general Zig
repository may be a short-lived CLI, a build tool, a library, or a daemon.
Apply the same design priorities while making the resource model explicit for
the actual product.

## Priority order

Evaluate every design choice in this order:

```text
1. safety and semantic correctness
2. predictable performance and bounded resource use
3. developer experience and maintainability
```

A faster or prettier change does not justify a weaker invariant. A safe change
that creates avoidable operational unpredictability is not finished. A safe and
predictable design should still be made easy to understand, review, operate,
and extend.

## Relationship to the semantic router

Tiger Style is a cross-cutting contract, not a seventh semantic failure family.

The existing `ZSR-v1` route answers:

```text
what work surface is active?
what semantic failure family owns the change?
```

The companion `ZTS-v1` contract answers:

```text
what work is bounded?
where are invariants asserted twice?
which errors are operating errors versus programmer errors?
what control-flow and resource-shape obligations apply?
what performance assumptions were sketched before implementation?
```

For a material code change, emit `ZTS-v1` before the first material edit unless
the repository already has an equivalent, stronger artifact. Non-material work
must state a concrete non-applicability reason.

## ZTS-v1

A compact JSON example:

```json
{
  "zig_tiger_style": {
    "style_version": "ZTS-v1",
    "artifact_state": {
      "repository_root": "/repo",
      "head": "0123456789abcdef",
      "dirty_fingerprint": "sha256:...",
      "zig_version": "0.16.0"
    },
    "material": true,
    "priority_order": [
      "safety",
      "performance",
      "developer-experience"
    ],
    "bounds": [
      {
        "operation": "read request body",
        "resource": "bytes",
        "limit": "4 MiB",
        "failure": "error.InputTooLarge"
      }
    ],
    "bounds_not_applicable_reason": null,
    "assertion_pairs": [
      {
        "invariant": "persisted sequence increases by one",
        "positive_site": "before append",
        "negative_site": "after reload"
      }
    ],
    "assertions_not_applicable_reason": null,
    "control_flow": {
      "recursion": "none",
      "unbounded_loops": false,
      "function_growth_reviewed": true
    },
    "errors": {
      "operating_errors_handled": true,
      "programmer_errors_asserted": true,
      "best_effort_sites": []
    },
    "performance_sketch": {
      "network": "none",
      "disk": "one bounded read and one atomic rename",
      "memory": "at most 8 MiB transient",
      "cpu": "one linear scan"
    },
    "performance_not_applicable_reason": null,
    "exceptions": [],
    "gate": {
      "classified_before_first_edit": true,
      "mutation_allowed": true
    }
  }
}
```

Validate the artifact:

```bash
python3 codex/skills/zig/scripts/zig_tiger_style_gate.py validate zts.json
```

Audit changed Zig source:

```bash
python3 codex/skills/zig/scripts/zig_tiger_style_gate.py audit \
  --root . \
  --base main \
  --head WORKTREE
```

The source audit is a ratchet. It is not a substitute for human review, the
repository's compiler/linter, or semantic proof.

## Bound everything that can grow or wait

A resource is bounded only when the code and failure behavior make the bound
observable.

Inventory at least:

| Resource | Examples | Required evidence |
| --- | --- | --- |
| Input bytes | files, stdin, protocol frames, archive members | numeric limit and oversize error |
| Collection size | arrays, maps, queues, worklists, diagnostics | maximum items and insertion failure |
| Iterations | retries, polling, graph traversal, fixed points | counter/deadline and terminal failure |
| Time | child processes, locks, waits, network calls | timeout source and timeout result |
| Memory | arenas, caches, scratch buffers, retained receipts | maximum footprint or bounded owner |
| Output | logs, JSON, generated code, captured stderr | maximum size and truncation policy |
| Concurrency | threads, tasks, subprocesses, lanes | maximum fanout and admission policy |
| Recursion depth | parsers, trees, dependency graphs | replace with an explicit bounded stack |

A loop over a bounded slice is structurally bounded. A loop that depends on an
external state transition still needs a retry, time, or progress bound.

Avoid production recursion for work that must terminate predictably. Prefer an
explicit stack or queue whose capacity and exhaustion behavior are reviewable.

Permanent event loops are a special case. State that they are intentionally
non-terminating and prove that work admitted per iteration remains bounded.

## Assertions and error handling

### Separate programmer errors from operating errors

Programmer errors violate an invariant the implementation controls. Assert them
and fail loudly.

Operating errors are expected environmental or input outcomes such as:

```text
out of memory
file not found
permission denied
short read
invalid input
lock contention
timeout
child failure
network loss
```

Represent and handle operating errors. Do not turn them into assertions or
`unreachable` merely because they are inconvenient.

### Pair assertions

For every important invariant, seek two independent enforcement sites. Common
pairs include:

```text
before persistence  + after reload
before serialization + after parsing
caller boundary      + callee boundary
producer              + consumer
state transition      + folded projection
length calculation    + final slice construction
compile-time constant + runtime observation
```

The two checks should fail for different implementation mistakes. Duplicating
the same expression in adjacent lines is not an independent pair.

### Check positive and negative space

Test and assert both:

```text
the values that must be accepted
and
the nearest values that must be rejected
```

Boundary mutations are especially valuable: zero, one, maximum, maximum plus
one, missing final element, duplicate element, wrong predecessor, stale epoch,
wrong target, and valid syntax with invalid semantics.

### Assertion shape

Prefer one invariant per assertion. Split:

```zig
assert(index < items.len);
assert(items[index].state == .ready);
```

instead of hiding independent facts in a compound boolean.

Use implication-shaped control flow when it reads more directly:

```zig
if (record.committed) assert(record.commit_digest != null);
```

## Control-flow shape

Use simple and explicit control flow. The parent function should own branching
and state transitions; leaf helpers should compute or validate focused facts.

A useful decomposition rule is:

```text
push conditionals toward the orchestration boundary
push loops toward focused leaf helpers
keep state mutation centralized
keep validation and derivation as pure as practical
```

Avoid deeply nested compound conditions. Name intermediate predicates when they
represent domain facts. Prefer positive invariants such as `index < count` over
negated inversions when both are equivalent.

### Function and line ratchets

For new or materially changed code:

```text
function target: at most 70 physical lines
line target: at most 100 Unicode code points
```

These are reviewability constraints, not permission for mechanical churn.
Existing larger functions may be reduced incrementally. Do not grow a function
that is already over the limit without a narrow, reasoned exception.

A split is successful when it exposes owners and invariants. Moving arbitrary
chunks into helpers while preserving hidden shared state is not an improvement.

## Types, units, and names

Use fixed-width integers for persisted, wire, protocol, ABI, and cross-process
contracts. Use `usize` for in-memory indexing and allocator interfaces where it
is the natural machine type, then validate before converting to a fixed-width
contract field.

Include units and qualifiers in names:

```text
bytes_max
latency_ms_max
retry_count
sequence_next
buffer_offset
```

Prefer complete domain nouns and verbs over abbreviations. Names should remain
clear in logs, documentation, tests, and review discussion.

Use options structs when same-typed positional arguments can be swapped or when
`null` would be ambiguous. At safety-relevant library call sites, spell out
options rather than relying on defaults that may change upstream.

## Allocation model

TigerBeetle's fixed-memory runtime is stronger than most general Zig programs.
Choose and state the repository-appropriate model.

### Long-lived services and hot data planes

Prefer startup allocation, fixed-capacity pools, bounded queues, and explicit
admission failure. Avoid allocator activity in latency-sensitive steady-state
paths unless measurement and ownership proof justify it.

### Short-lived CLIs and build tools

Post-startup allocation is acceptable when:

```text
the input and aggregate allocation are bounded
the owner and deinit path are explicit
allocation failure is propagated or deliberately translated
the algorithm does not repeatedly allocate in an avoidable hot loop
```

Arenas reduce cleanup complexity but do not replace a memory bound.

## External observations and effects

Do not let an external event directly mutate authoritative state. Use a staged
sequence:

```text
observe
-> validate
-> normalize
-> admit
-> apply one transition
-> reload or rederive
-> assert the resulting invariant
```

This applies to files, Git state, subprocess output, app-server events, network
responses, persisted ledgers, generated artifacts, and review receipts.

Persistence should be checked on both sides of the boundary. Validate the value
before writing and validate the reloaded or folded value afterward.

Best-effort cleanup is allowed only when failure cannot invalidate the primary
result. Name the site, explain why it is non-authoritative, and preserve a
signal when the cleanup failure matters operationally.

## Performance sketch

Before implementing a performance-sensitive design, sketch the four resources:

| Resource | Questions |
| --- | --- |
| Network | How many round trips and bytes? Can work be batched? |
| Disk | How many reads, writes, renames, and sync points? |
| Memory | Peak retained and transient bytes? Allocation count? |
| CPU | Complexity, passes, branch shape, copies, and cache behavior? |

The sketch may be brief, but it must name the dominant term and the expected
scale. Follow it with measurement when the change claims a performance result.

Separate control plane from data plane. Control-plane validation can be rich
and assertion-heavy; data-plane work should be predictable, batched, and easy
for the compiler and reviewer to inspect.

Extract hot loops into focused functions with primitive inputs when that makes
redundant work and register use easier to reason about. Do not optimize by
making invariants implicit.

## Dependencies and tooling

Prefer the Zig standard library and repository-owned tooling. Every dependency
adds supply-chain, compatibility, operational, and review cost.

When a dependency is justified:

```text
pin an immutable version or commit
record the source and integrity value
name the owner and update policy
keep the imported surface narrow
```

Prefer Zig for repository tooling when it materially improves portability,
type safety, or shared maintenance. Do not rewrite a proven tool solely to
satisfy a language preference.

## Exceptions

Source-audit exceptions use this exact form:

```zig
// tiger-style: allow(loop) reason=The process event loop is intentionally permanent and each iteration admits one bounded message.
while (true) {
    // ...
}
```

Supported classes are:

```text
loop
recursion
catch-unreachable
best-effort
function-lines
implicit-options
assertions
```

An exception must:

```text
name one narrow rule
state a concrete reason
identify the bounded or proof-bearing alternative
remain adjacent to the affected code
```

A broad file-level waiver, placeholder reason, or untracked external promise is
not valid.

## Review checklist

Before closure, answer:

```text
[ ] What can grow, wait, retry, fan out, or recurse?
[ ] Where is every bound enforced and what is the failure?
[ ] Which invariants have independent paired checks?
[ ] Which failures are operating errors and which are programmer errors?
[ ] Did any function over 70 lines grow?
[ ] Did any changed line exceed 100 columns without a justified URL exception?
[ ] Are library options explicit at safety-relevant call sites?
[ ] Is external state validated before admission and after application?
[ ] What are the network, disk, memory, and CPU sketches?
[ ] Does final proof belong to the final artifact state and toolchain context?
```
