# Performance Checklists

## Table of contents

1. Pre-flight checklist
2. Baseline checklist
3. CPU-bound checklist
4. Memory-bound checklist
5. I/O-bound checklist
6. Lock-bound checklist
7. Tail-latency checklist
8. Shipping checklist

## 1. Pre-flight checklist

- Define the target metric and percentile.
- Define the dataset and load shape.
- Define the environment and runtime flags.
- Confirm correctness tests are passing.

## 2. Baseline checklist

- Warm up to steady state.
- Collect enough samples.
- Report p50, p95, p99, and max.
- Record environment and dataset.

## 3. CPU-bound checklist

- Reduce algorithmic complexity.
- Improve data locality.
- Reduce branch mispredictions.
- Vectorize or batch work.

## 4. Memory-bound checklist

- Reduce allocation rate.
- Shrink working set.
- Avoid pointer chasing.
- Fix false sharing.

## 5. I/O-bound checklist

- Reduce bytes and round trips.
- Batch or buffer I/O.
- Remove redundant serialization.
- Use async I/O where safe.

## 6. Lock-bound checklist

- Reduce lock scope and frequency.
- Shard state to reduce contention.
- Replace blocking with lock-free when safe.
- Eliminate global locks on hot paths.

## 7. Tail-latency checklist

- Reduce variance and outliers.
- Add timeouts and cancelation.
- Apply admission control and backpressure.
- Limit batch sizes and queue lengths.

## 8. Shipping checklist

- Add a regression guard or budget.
- Record before and after metrics.
- Document trade-offs and risks.
