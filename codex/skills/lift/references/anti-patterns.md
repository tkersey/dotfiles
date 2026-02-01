# Performance Anti-Patterns

## Table of contents

1. Measurement failures
2. Optimization failures
3. Benchmark failures
4. Shipping failures

## 1. Measurement failures

- Optimize without a baseline.
- Report only averages for skewed distributions.
- Ignore warmup and steady state.
- Compare runs with different environments.

## 2. Optimization failures

- Micro-optimize before algorithmic fixes.
- Optimize the wrong layer or wrong code path.
- Merge multiple changes without isolating effects.
- Trade correctness or determinism for speed without approval.

## 3. Benchmark failures

- Use unrealistic datasets or tiny inputs.
- Benchmark code that the compiler removes.
- Compare noisy results without significance checks.
- Ignore tail latency and variance.

## 4. Shipping failures

- Ship without a regression guard.
- Ignore memory or latency regressions in other metrics.
- Fail to document trade-offs and observed risk.
