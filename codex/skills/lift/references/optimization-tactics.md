# Optimization Tactics Catalog

## Table of contents

1. Algorithmic tactics
2. Data layout tactics
3. Concurrency tactics
4. I/O tactics
5. Memory tactics
6. Micro-architecture tactics
7. Runtime and compiler tactics

## 1. Algorithmic tactics

- Remove redundant work and repeated parsing.
- Replace nested loops with indexed lookups.
- Precompute and cache stable results.
- Use streaming to avoid materialization.

## 2. Data layout tactics

- Flatten object graphs into contiguous arrays.
- Reorder fields by access frequency.
- Use SoA for vectorizable operations.
- Reduce pointer chasing in hot paths.

## 3. Concurrency tactics

- Shard state by key to reduce contention.
- Use read-copy-update patterns for read-heavy paths.
- Batch work to reduce coordination overhead.
- Prefer message passing over shared mutation when feasible.

## 4. I/O tactics

- Reduce syscalls by batching and buffering.
- Use async I/O for latency hiding where appropriate.
- Eliminate redundant serialization or copies.

## 5. Memory tactics

- Reduce allocation rate and object churn.
- Use arenas for short-lived objects.
- Cap caches to avoid memory blowups.

## 6. Micro-architecture tactics

- Avoid unpredictable branches.
- Align hot data to cache lines.
- Use SIMD and vectorized libraries.
- Reduce instruction dependencies in tight loops.

## 7. Runtime and compiler tactics

- Enable profile-guided optimization where supported.
- Tune GC thresholds to reduce pause frequency.
- Remove dynamic dispatch in hot paths.
- Avoid reflection or dynamic allocation in tight loops.
