# Zig error-set and failure-path engineering playbook

Use this playbook when designing fallible APIs, reviewing `try`/`catch`, avoiding `anyerror`, adding `errdefer`, mapping C/system errors, or proving cleanup.

## Expert objective

A Zig error contract should state:

1. the precise error set where feasible;
2. which errors are domain errors, resource errors, environmental errors, or programmer bugs;
3. how cleanup happens after each failure;
4. which errors propagate unchanged and which are translated;
5. which tests prove success, expected failure, allocation failure, and cleanup-after-failure.

## Error taxonomy

| Category | Examples | Preferred handling |
| --- | --- | --- |
| Domain/protocol | `error.InvalidHeader`, `error.UnsupportedVersion` | Precise error set; switch at caller. |
| Resource | `error.OutOfMemory`, `error.NoSpaceLeft` | Propagate, test via failing allocator/storage. |
| Environment | `error.FileNotFound`, permission, network unavailable | Surface with context at integration boundary. |
| Programmer bug | impossible state, invalid internal invariant | `assert`/`unreachable` only with strong proof. |
| Foreign/system | errno, Win32 errors, C library statuses | Translate once in boundary module. |

Do not turn domain errors into panics. Do not turn bugs into vague error sets.

## Precise error sets

Prefer named or inferred precise error sets inside libraries. Avoid `anyerror` except at high-level integration boundaries or when truly unavoidable.

```zig
const ParseError = error{
    Empty,
    InvalidChar,
    Overflow,
};

pub fn parseId(s: []const u8) ParseError!u32 {
    if (s.len == 0) return error.Empty;
    // ...
}
```

Benefits:

- callers can switch exhaustively;
- documentation is clearer;
- accidental error widening becomes visible;
- tests can cover every domain error.

## `try`, `catch`, and `errdefer`

Review every `try` in context:

- Is propagation correct, or should the error be mapped to a domain-specific error?
- Is there acquired state that needs rollback before propagation?
- Would a `catch` block swallow useful information?
- Is `catch unreachable` backed by proof, or is it hiding a real failure?

Use `errdefer` for rollback in constructors and multi-step mutation:

```zig
pub fn addEntry(self: *Table, key: []const u8, value: Value) !void {
    const owned_key = try self.allocator.dupe(u8, key);
    errdefer self.allocator.free(owned_key);

    try self.map.put(owned_key, value);
    // ownership transferred to map after successful put
}
```

## Error mapping at boundaries

For C or OS boundaries, convert raw statuses once:

```text
raw errno/status -> boundary-specific error set -> Zig core logic
```

Keep mappings centralized and documented. Include unknown/unsupported statuses if the foreign API can return values outside the documented range.

## Failure-path tests

Test at four levels:

1. success path;
2. expected domain failures;
3. resource failures, especially allocation failure;
4. cleanup after partial failure.

For parsers, every named domain error should have at least one fixture. For allocation-heavy APIs, use `checkAllAllocationFailures` or a deterministic failing allocator.

## Reporting discipline

When reviewing or implementing, report:

- exact error set before/after the change;
- whether `anyerror` was narrowed or widened;
- new cleanup path and `errdefer` placements;
- failure tests added or unavailable;
- any remaining `catch unreachable` and why it is sound.

## Review checklist

- Error set is precise unless high-level integration justifies widening.
- `error.OutOfMemory` is propagated, not swallowed.
- Boundary errors are translated once, not scattered.
- `catch unreachable` has a written proof or is removed.
- `errdefer` protects partial initialization and mutation.
- Domain errors have fixtures.
- Allocation failure has coverage for allocation-using APIs.
- Cleanup-after-failure is tested.
