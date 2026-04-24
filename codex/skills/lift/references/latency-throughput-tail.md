# Latency, Throughput, and Tail Behavior

## Core Relationships

Latency and throughput are coupled through queueing. As utilization approaches
saturation, queues grow and tail latency can explode. Use Little's Law,
`L = lambda * W`, to reason about work in system, arrival rate, and wait time.

## Tail Latency Drivers

- variance in service time
- head-of-line blocking
- lock convoying
- GC pauses and page faults
- cold starts and cache misses
- retry storms and network jitter
- unbounded queues and oversized batches
- noisy neighbors or resource saturation

## Queueing and Utilization

- Keep critical services below saturation.
- Measure queue depth, wait time, service time, and utilization separately.
- Distinguish arrival bursts from slow service.
- Bound queues so overload fails predictably instead of thrashing.

## Variance Reduction

- Remove outlier work from the common path.
- Split slow and fast paths.
- Propagate cancellation to avoid wasted work.
- Use timeouts for external dependencies.
- Avoid global locks and blocking operations in request paths.
- Normalize batch sizes when large batches create p99 spikes.

## Admission Control and Backpressure

- Shed load when SLOs cannot be met.
- Apply backpressure at queue boundaries.
- Prefer graceful degradation to unbounded latency.
- Make overload behavior explicit in the performance contract.

## Batching and Pipelining

Batching improves throughput when it amortizes overhead, but it can hurt tail
latency. Bound batch size and max wait time. Pipeline stages when idle time or
sequential dependency dominates, but measure queueing between stages.

## Tail Experiment Checklist

- Compare p50, p95, p99, max, and variance.
- Capture queue depth and service time histograms.
- Check retries, timeouts, and cancellation counts.
- Measure under representative concurrency.
- Ensure the fix does not just shift tail to another subsystem.
