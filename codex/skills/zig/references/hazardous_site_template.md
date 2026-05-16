# Zig Hazard Site Template

Use one file per nontrivial hazard site or per tightly coupled cluster.

```text
# site-<id>: <file>:<line> <operation>

## Operation

- Syntax / builtin / API:
- Build condition / target condition:
- Public API reachability:
- Related sites:

## Invariant

State the exact invariant that must hold before the hazardous operation runs.

## Invariant owner

Who establishes the invariant?

- Caller:
- Validator / witness constructor:
- Build option / target gate:
- External ABI / hardware / OS contract:

## Failure mode

If the invariant is false, what happens?

- Safety-checked Illegal Behavior:
- Unchecked Illegal Behavior:
- ABI/layout mismatch:
- Lifetime/allocator/concurrency failure:
- Silent logic corruption:

## Classification

One of:

- `A/IRREDUCIBLE_BOUNDARY`
- `B/PERF_OR_FOOTPRINT_ONLY`
- `C/REFACTORABLE_TO_WITNESS`

Falsifiable justification:

```text
This is classified as <bucket> because ...
Alternatives considered:
1. ... fails because ...
2. ... fails because ...
3. ... fails because ...
```

## Proof obligations

- [ ] Pointer/provenance proof
- [ ] Alignment proof
- [ ] Length/sentinel proof
- [ ] Initialization/write-before-read proof
- [ ] Allocator ownership/deinit proof
- [ ] Layout/ABI/endian proof
- [ ] FFI contract proof
- [ ] Atomic/concurrency proof
- [ ] Build-mode proof: Debug / ReleaseSafe / ReleaseFast / ReleaseSmall
- [ ] Target matrix proof
- [ ] Fuzz/differential proof
- [ ] Benchmark/profile proof

## Remediation plan

For `A`: shrink boundary and harden safety comment.

For `B`: add safe/reference path and measurements.

For `C`: introduce witness or safe rewrite.

## Verification log

Commands:

```bash
zig version
zig fmt --check .
zig build test -Doptimize=Debug
zig build test -Doptimize=ReleaseSafe
zig build test -Doptimize=ReleaseFast
zig build test -Doptimize=ReleaseSmall
```

Results:

```text
<fill in exact outcomes>
```

## Residual risk

What remains unproven, and why?
```
