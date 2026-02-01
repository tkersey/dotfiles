# Latency, Throughput, and Tail Behavior

## Table of contents

1. Core relationships
2. Tail latency drivers
3. Queueing and utilization
4. Controlling variance
5. Admission control and backpressure
6. Batching and pipelining

## 1. Core relationships

- Treat throughput and latency as coupled via queueing.
- Keep utilization below saturation to protect tail latency.
- Use Little's Law: L = lambda * W to reason about queues.

## 2. Tail latency drivers

- Variance in service time.
- Head-of-line blocking and lock convoying.
- GC pauses, page faults, and context switches.
- Network jitter and cross-zone latency.

## 3. Queueing and utilization

- Expect tail latency to explode near high utilization.
- Keep critical services below a safe utilization threshold.
- Use load shaping to reduce burstiness.

## 4. Controlling variance

- Reduce per-request variance and outliers.
- Use timeouts and cancelation for stragglers.
- Apply hedged requests only when it reduces overall latency.

## 5. Admission control and backpressure

- Shed load when SLOs cannot be met.
- Apply backpressure to avoid unbounded queues.
- Favor graceful degradation over thrashing.

## 6. Batching and pipelining

- Batch to improve throughput when latency budgets allow it.
- Pipeline stages to reduce idle time and increase utilization.
- Bound batch size to avoid tail spikes.
