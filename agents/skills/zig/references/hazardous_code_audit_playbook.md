# Zig hazardous code and Illegal Behavior

Use for a concrete low-level uncertainty or an explicitly requested hazard audit.
Zig has no Rust-style `unsafe` marker: correctness can depend on invariants not
fully enforced by types, runtime safety or the ABI. A hazardous token locates a
question, not a defect. Preserve a valid implementation when its argument holds.

Establish the relevant invariant, who guarantees it, all paths that rely on it,
and the consequence of violation. Repair an unsupported boundary when authorized.
The useful outcome is correct code and a defensible argument, not a classification
packet. Existing types, caller contracts, source arguments and tests can supply
evidence without duplicating them into a new report.

## Source anchors

Use the selected compiler's language reference and stdlib. For the bundled 0.17
baseline, consult [Illegal Behavior and builtins](https://ziglang.org/documentation/0.17.0/)
and [release changes](https://ziglang.org/download/0.17.0/release-notes.html).
[Migration](zig_0_17_migration.md) covers logical `@bitCast`, reflection and removed
C-import facilities; [build/toolchain](build_toolchain_playbook.md) owns commands
and translation dependencies. An older project pin still governs that project.

## Hazard surfaces

| Surface | Questions that can matter |
| --- | --- |
| Safety checks and impossible states | `unreachable`, `catch unreachable`, optional unwraps, exact arithmetic, shifts and invalid enum/error conversions: is invalid input actually excluded? |
| Raw pointers and projection | `@ptrCast`, `@ptrFromInt`, `@alignCast`, `@fieldParentPtr`, address-space/qualifier casts, many-item/C pointers: what establishes provenance, extent, alignment, initialization and lifetime? |
| Initialization | Can output buffers, partially initialized aggregates, self-references, logging or cleanup observe `undefined` values before assignment? |
| Layout, ABI and logical bits | Are size, offsets, padding, valid representations and endian assumptions appropriate for this target and this operation? |
| C, foreign calls and assembly | Are nullability, lengths, ownership domains, calling convention, callbacks, status mapping, reentrancy and panic/unwind boundaries sound? |
| MMIO and volatile | Does the device permit this width, ordering and read/write sequence? Are packed-field accesses causing forbidden read-modify-write? |
| Atomics and concurrency | What synchronizes shared state, protects reclamation, satisfies progress and handles cancellation/deinit races? |
| Allocation and lifetime | Who releases each allocation, which mutations invalidate borrows, and does failure preserve the advertised guarantee? |
| Vectors and optimized loops | Are tails, alignment, CPU features and bounds correct, and is the claimed benefit measured? |

A nested expression such as `@ptrCast(@alignCast(bytes.ptr))` carries multiple
obligations. Group related sites by their invariant owner when that reveals the
actual repair boundary; do not force separate wrappers for each syntax token.

## Disposition lenses

These distinctions can help compare designs; they are not exhaustive or mandatory
labels. The A/B/C names remain available for an audit consumer that uses them.

| Lens | Useful action |
| --- | --- |
| A: irreducible boundary | FFI, MMIO, assembly, allocator internals or mandated layout may require low-level operations. Keep the necessary core small and establish its caller/callee contract. |
| B: performance or footprint choice | Compare the safe/reference formulation with the retained fast path under the actual budget, target and correctness guard. Mark unmeasured benefits as unmeasured. |
| C: removable hazard | Delete, simplify, validate or use an owner-bound witness when this genuinely removes an unsupported assumption. Preserve API, ownership and timing requirements. |

Challenge a claimed irreducible operation when an alternative meets the same
requirements; there is no quota of rejected alternatives. A wrapper or a type name
is not proof: construction, mutation, copying and projection must preserve its
invariant. Do not add a decorative witness where the existing interface already
establishes the property. A valid fast path need not be rewritten merely to change
its classification.

## Comprehensive audits

When the request calls for a full inventory, cover the specified source, generated
code, translated C, dependencies, target conditions and public reachability.
Declare inspected scope and gaps. A read-only scan such as
`sh "$zig_skill_root/scripts/zig_hazard_audit_rg.sh" .` can help locate candidates;
inspect its exclusions and supplement it for generated or custom package paths.
Resolve `zig_skill_root` from the loaded skill rather than a hard-coded install
location. Neither an empty scan nor a list of token hits establishes completeness.

A useful inventory can associate a stable site/location with the operation,
invariant owner, public reachability, relevant modes/targets, evidence and
proposed disposition. Adapt [the site template](hazardous_site_template.md) or
[FFI template](ffi_contract_template.md) when the requested artifact benefits.
Report unsupported assumptions, retained boundaries, measurements, commands and
coverage gaps in the user's format. Preserve requested detail and enumeration;
optional templates do not make a requested comprehensive audit optional.

A focused implementation or review need not emit this inventory, traverse phases,
assign every label or repeat classification passes. Investigate further when a
new counterexample or unresolved obligation justifies it. An audit-only request
does not authorize source remediation.

## Pattern-specific reasoning

### Safety-disabled scopes and arithmetic

For `@setRuntimeSafety(false)`, establish that all reachable callers satisfy the
preconditions of every unchecked operation. Keep the scope small. Passing a
`debug` test is not proof that input bounds, overflow, shifts, optional unwraps or
closed-world assumptions hold with checks disabled. A private helper still needs
valid internal callers; visibility alone cannot establish an invariant.

`@import("builtin").mode.runtimeSafety()` describes the selected module mode,
not every local scope's override. Use the repository's actual optimize modes;
0.17 names are `debug`, `safe`, `fast` and `small`. Select modes that discriminate
the risk rather than automatically running all four for every edit.

Ordinary resource or input failures should return appropriate errors, not become
`catch unreachable`. For arithmetic bounds, use overflow-safe checks such as
`offset <= len` followed by `size <= len - offset`; proving an already-overflowed
`offset + size` is too late.

### Projection and sentinel contracts

Validate the properties required by a projection before using the resulting view:
length, alignment, valid destination representation, provenance, sentinel,
lifetime and mutation constraints as applicable. A runtime check can turn an
untrusted condition into a recoverable error; a safety-checked cast alone may trap
or become unchecked in another mode. See [boundary design](unsafe_boundary_playbook.md).

Keep the witness bound to the same buffer/owner and extent it validated. Offsets
checked against one buffer cannot justify projection from a shorter replacement.
Sentinel storage must exist at the promised position and remain valid during use;
converting an unbounded foreign pointer is not a bounded validation strategy.

### Initialization and cleanup

Identify what must be initialized before each observation, including formatting,
hashing, equality and error cleanup. `undefined` can be appropriate for output
storage, but every observed field must have been assigned. Track which resources
were acquired when construction fails partway, and avoid cleanup of uninitialized
owners. An explicit builder or initialized representation is useful when it
simplifies that state, not as a mandatory replacement for every scratch buffer.

### Layout and foreign boundaries

Check sizes, alignments and offsets against independent ABI/format expectations,
not constants copied from the implementation under test. Ordinary structs are
not foreign layout promises. Packed-field pointers have alignment/bit-offset
restrictions. Logical `@bitCast` in 0.17 is not a host-memory or wire-endian view;
extern aggregates are not a mechanical cast replacement. Native padding is not a
canonical serialized or hashed identity. Use [layout/ABI](layout_abi_playbook.md).

At a C/assembly boundary, resolve the defining symbol/header, build linkage,
nullable pointer/length pairing, allocator/free domain, borrowed lifetime,
status/errno translation, callback thread and reentrancy assumptions. Prevent
panic/unwind crossing an unsupported ABI boundary. Test the relevant wrapper;
translated declarations alone do not establish ownership or error semantics.
In 0.17 `@cImport` is removed; use a compatible pinned translator through the build
integration rather than restoring an obsolete import recipe.

### MMIO

Volatile preserves side-effecting access, not inter-thread synchronization.
Whole-register access avoids some packed-field hazards but is not universally
safe: write-one-to-clear bits and read-side effects can prohibit read-modify-write.
Use device-specified width, address, reserved-bit policy and barriers. `allowzero`
is justified only where address zero is actually mapped for the operation.

### Concurrency and lifetime

Publication requires both ordering and a lifetime/reclamation argument. Identify
which write a reader can observe and why the payload remains live; acquire/release
names alone do not establish that relationship. Account for compare-exchange
failure ordering, ABA, contention, cancellation and shutdown. Stress tests can
find failures but cannot prove a progress guarantee. Use [concurrency](atomics_concurrency_playbook.md)
without replacing a required nonblocking design merely because a template is
unfilled.

### Fast paths and vectors

Retain sufficiently independent correctness evidence for optimized paths. A scalar
reference is useful, as are mathematical expectations, protocol vectors and other
oracles appropriate to the contract. Compare empty/short inputs, width boundaries,
supported unaligned views, extreme values, tails and relevant CPU features.
`@prefetch` is a performance hint, not memory validation. Measure under controlled
conditions before claiming speed/footprint benefit; use [performance](performance_engineering_playbook.md).

## Evidence and completion

Honor the requested scope and required repository checks. Add allocation-failure,
semantic mutation, compile-fail, target, cancellation, differential or benchmark
checks for the obligations they actually test. In 0.17 migrations, include semantic
changes that do not produce compiler errors. Keep source-level arguments, real
compiler results, native execution and unavailable checks distinct. A successful
skill example suite is not a test of the user's changed code.

For authorized implementation, complete the selected repair and relevant checks.
For review, return concrete findings or a supported no-finding outcome. Report
remaining risk and unavailable evidence without manufacturing a universal proof
or treating missing paperwork as a defect.
