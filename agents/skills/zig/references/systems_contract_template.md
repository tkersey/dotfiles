# Low-level Zig systems contract template

Use this template in reviews and implementation reports for memory-, pointer-, ABI-, I/O-, concurrency-, or performance-sensitive Zig code.

| Contract area | Answer |
| --- | --- |
| Zig version |  |
| Target/optimize modes validated |  |
| Ownership model |  |
| Allocator model |  |
| Cleanup/deinit path |  |
| Failure/error set |  |
| Pointer/slice/sentinel/alignment assumptions |  |
| Layout/ABI/endian assumptions |  |
| I/O/effect capabilities |  |
| Concurrency/atomic ordering |  |
| Comptime/generated-code contract |  |
| Tests/fuzz/allocation-failure coverage |  |
| Benchmark/profiler evidence |  |
| Remaining risk |  |

## Short-form report skeleton

```text
Version: Zig ...
Active hazard classes: ...
Ownership: ...
Allocator: ...
Failure contract: ...
Unsafe/layout contract: ...
Comptime contract: ...
Commands run:
- ...
Results:
- ...
Unavailable proof lanes:
- ...
Remaining risk:
- ...
```
