# Zig Implicit Trigger Taxonomy

Use `$zig` when the repository or task is Zig-specific even if the user does not
type `$zig`.

## Direct Zig cues

```text
.zig
build.zig
build.zig.zon
zig build/test/run/fmt/ast-check/fetch
zlinter
zls
zig-pkg
.zig-cache / zig-cache / zig-out
ZIG_GLOBAL_CACHE_DIR
--cache-dir / --global-cache-dir
TigerStyle / Tiger Style / ZTS-v1
```

## Version and migration cues

```text
std.Io
std.process.Init
@cImport / addTranslateC
removed @Type
std.meta.Int / Tuple
std.Thread.Pool
std.testing.Smith
--test-timeout
Zig 0.16
```

## Comptime and generation cues

```text
comptime
anytype
@typeInfo
@FieldType
@hasDecl / @hasField
inline for
generated types
schema/format derivation
specialization
@compileError / @setEvalBranchQuota
```

## Low-level and hazard cues

```text
allocator ownership
errdefer
raw pointers/slices/sentinels/alignment
@ptrCast / @alignCast / @ptrFromInt
undefined / unreachable / @setRuntimeSafety
extern / packed
FFI/C ABI/MMIO
atomics/concurrency
ReleaseFast/ReleaseSmall
```

## Tiger Style cross-cutting cues

These activate the Tiger Style contract only when the repository or changed
surface is already known to be Zig.

```text
while (true)
recursion / recursive descent
retry / polling / fixed point
timeout / deadline
queue / worklist / fanout
maximum bytes / maximum items
assert / assertion density / paired assertions
positive and negative space
catch unreachable / empty catch
function over 70 lines
line over 100 columns
implicit options / default options
control plane / data plane
network disk memory CPU sketch
startup allocation / fixed-capacity pool
```

Do not infer a violation from a cue alone. The cue starts boundedness,
assertion-pair, error-class, control-flow, and performance-sketch review.

## Contextual semantic-family cues

These trigger `$zig` only when the repository or changed surface is already
known to be Zig.

### Claim binding

```text
fingerprint receipt certificate proof evidence ref cursor manifest
checkpoint replay passed verify attestation
```

### Lifetime escape

```text
parsed JSON decoded bytes arena snapshot report returned slice deinit refresh
```

### Atomic transition

```text
append commit put stage rollback transfer ledger journal outbox event pair
```

### Verifier completeness

```text
parser decoder verifier inspector WASM binary protocol opcode section LEB metadata stack
```

### Repository closure

```text
golden expected compile-fail path registry generated artifact source manifest
```

### Proof context

```text
stale proof wrong head dirty tree commit/push after tests fork dependency cache permission
```

## Routing discipline

Do not trigger an extreme workflow from an adjacent generic word alone.

Once `$zig` is active:

```text
classify work surface
classify semantic failure family
emit ZSR-v1 for material changes
emit ZTS-v1 for material code or state a concrete non-material reason
```

Combine with repository invariant or verification skills only when their
independent trigger is genuinely met. `$zig` owns Zig-specific routing,
toolchain checks, proof context, semantic-family contracts, and the cross-cutting
Tiger Style adaptation.
