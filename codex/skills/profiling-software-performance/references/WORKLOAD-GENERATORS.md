# Realistic Workload Generators

> A bench is only as good as the workload. "Uniform random from 0 to 1000" is almost never what users actually do. This reference covers how to build load inputs that match reality.

## Contents

1. [Why synthetic workloads lie](#why-synthetic-workloads-lie)
2. [Distributions you need to know](#distributions-you-need-to-know)
3. [Key-access patterns (Zipfian, Pareto)](#key-access-patterns-zipfian-pareto)
4. [Arrival-rate patterns (Poisson, bursty)](#arrival-rate-patterns-poisson-bursty)
5. [Size distributions](#size-distributions)
6. [Time-of-day shaping](#time-of-day-shaping)
7. [Replaying production traffic](#replaying-production-traffic)
8. [Generator tools](#generator-tools)
9. [Realism checklist](#realism-checklist)

---

## Why synthetic workloads lie

Uniform random is the default, easiest, and worst. Real workloads have:

- **Skewed key distribution** (Zipfian) — hot keys and long tails
- **Bursty arrivals** (Poisson with overdispersion) — not evenly spaced
- **Size distributions** (log-normal, heavy-tailed) — small mean, rare huge
- **Temporal correlation** — users session-cluster
- **Cache warmth** — some keys repeat quickly, others never

A uniform bench will make caches look useless (they can't hit) and rate limits look fair. A Zipfian bench reveals that cache hit rate is 80% on hot 10%, and rate limiters fall over on the hot keys.

**Rule**: your bench's key distribution should match production's key distribution, or you're measuring a fiction.

---

## Distributions you need to know

### Uniform

Each value equally likely. Use only when you know the real distribution IS uniform (rare).

### Zipfian

Power-law distribution where `P(rank=k) ∝ 1/k^α`. α=1 is "classic Zipf" (web page access, word frequency, cache keys).

```python
import numpy as np
N = 10_000          # number of keys
alpha = 1.0         # Zipfian exponent (1.0 = classic)
ranks = np.arange(1, N+1)
probs = 1 / ranks**alpha
probs /= probs.sum()

# Draw M requests
M = 100_000
keys = np.random.choice(N, size=M, p=probs)
```

Effect: top 10 keys account for 30-60% of all requests (depending on α).

Rust (`rand_distr`):
```rust
use rand_distr::{Zipf, Distribution};
let dist = Zipf::new(10_000, 1.0).unwrap();
for _ in 0..100_000 {
    let key_rank = dist.sample(&mut rand::thread_rng()) as usize;
    // ...
}
```

Tune α to production:
- α < 0.5: close to uniform (rare)
- α ~ 0.8-1.2: classic (most web workloads)
- α > 1.5: extreme skew (top-1 dominates)

### Pareto / Power-law

Similar shape, typically for sizes rather than ranks.

`P(X > x) ∝ x^-α`

```python
from scipy.stats import pareto
sizes = pareto(2.62).rvs(100_000)   # shape 2.62 models file sizes
```

Typical shape parameters:
- File sizes: 1.5 - 2.5
- Session lengths: 1.2 - 2.0
- Tweet lengths: 3.0+

### Log-normal

For durations, RPC latencies, request sizes when distributions look bell-curved on log scale.

```python
sizes = np.random.lognormal(mean=np.log(100), sigma=1.0, size=100_000)
# median 100, heavy right tail
```

### Exponential

Times between independent Poisson events (arrival times for a stationary rate).

```python
inter_arrival = np.random.exponential(scale=1.0/rate_per_sec, size=N)
arrival_times = np.cumsum(inter_arrival)
```

---

## Key-access patterns (Zipfian, Pareto)

### Matching production

If you have production logs:

1. Extract the last N hours of key accesses
2. Compute rank-frequency curve: sort keys by count, plot log(count) vs log(rank)
3. Fit a line — slope is -α

Python:
```python
from collections import Counter
counts = Counter(keys_from_log)
sorted_counts = sorted(counts.values(), reverse=True)
ranks = np.arange(1, len(sorted_counts)+1)
log_ranks = np.log(ranks)
log_counts = np.log(sorted_counts)
slope, intercept = np.polyfit(log_ranks[:1000], log_counts[:1000], 1)
print(f"Zipfian alpha = {-slope:.2f}")
```

Use this α in the bench.

### Cache hit rate implications

| Distribution | Top-1% coverage | Typical cache hit rate (1% of keys in cache) |
|--------------|----------------|---------------------------------------------|
| Uniform | 1% of requests | ~1% |
| Zipf α=0.8 | ~25% | ~25% |
| Zipf α=1.0 | ~45% | ~45% |
| Zipf α=1.2 | ~60% | ~60% |

Real-world caches are viable BECAUSE of Zipfian access. Benching uniform hides this entirely.

### Temporal locality

Beyond pure Zipf, many workloads have temporal locality — recently accessed keys more likely to be accessed soon. Model with:
- Zipf for long-tail distribution
- LRU stack model (some fraction of requests re-touch the last N keys)

---

## Arrival-rate patterns (Poisson, bursty)

### Constant rate (baseline)

```
wrk2 -R 1000 ...    # 1000 req/s constant
```

Already far better than wrk (closed-loop). But constant rate hides behavior under bursts.

### Poisson (random arrivals)

Inter-arrival times exponentially distributed. Use `vegeta` with the `-rate` matching Poisson semantics (variable-rate with inter-arrival jitter).

### Bursty / overdispersed

Real traffic is often overdispersed — a few hundred requests arrive in the same millisecond, then quiet. Models:

- **Markov-Modulated Poisson Process** (MMPP): 2-state Markov chain (low/high rate states)
- **Hawkes process**: self-exciting; one request raises the probability of nearby requests

Simpler approximations:
- Scale factor over time: rate(t) = base + amplitude × sin(ωt) + noise
- Production replay (see below)

### Smoothing vs exposing

For SLI/SLO testing, you want realistic bursts. For microbenchmarks, you want clean rates. Know which you're running.

---

## Size distributions

### Request/response sizes

Vary request payload sizes across the distribution you actually expect. A bench with fixed 1-KB payload will not catch:
- JSON parser scaling
- Memory allocator behavior at larger sizes
- Serialization cliffs

```python
# If prod ranges 100 B to 1 MB, roughly log-normal around 5 KB:
sizes = np.random.lognormal(mean=np.log(5000), sigma=1.5, size=N)
sizes = np.clip(sizes, 100, 1_000_000).astype(int)
```

### Batch sizes

For batch APIs, vary batch size. See CASE-STUDIES.md §Case 1 for the scaling law this reveals.

```python
batch_sizes = np.random.choice([1, 10, 100, 1000], size=N,
                               p=[0.5, 0.3, 0.15, 0.05])  # matching prod
```

---

## Time-of-day shaping

### Diurnal

Most user-facing systems see 3-5× swing between off-peak and peak. Bench at peak rates if SLO must hold then:

```python
def hourly_rate(hour):
    # Simple model: low overnight (0-6), ramp (7-9), peak (10-22), taper (22-24)
    if hour < 6: return 0.2
    if hour < 9: return 0.2 + 0.8 * (hour - 6) / 3
    if hour < 22: return 1.0
    return 1.0 - (hour - 22) / 2 * 0.5
```

Run the bench at peak rate to validate SLOs.

### Weekly

Weekend vs weekday for B2C, weekday-only for B2B. Often captured by different peak-hour rates.

---

## Replaying production traffic

The ultimate realistic bench: capture real production requests and replay.

### Capture

Application-level:
```
# Log request metadata (no PII!): timestamp, route, method, size, response code, latency
log.info("req", ts=time.time(), route=request.url.path, method=request.method,
         size=len(request.body), status=response.status, lat_ms=elapsed)
```

Network-level (less common):
```
sudo tcpdump -i any -s0 -w capture.pcap port 8080
# then use goreplay / teeproxy for replay
```

### Scrub

Remove PII before replay fixtures are used in dev/CI:
- Hash user IDs
- Redact query parameters (emails, tokens)
- Truncate bodies to structural dummy

### Replay tools

- **goreplay** (gor) — HTTP capture + replay + rate scaling
- **teeproxy** — tee live traffic to staging (good for canary testing)
- **k6** with scripting — build a replay scenario from captured JSON
- **vegeta** — read targets from file

```bash
# vegeta replay
cat targets.json | jq -r '"@- \(.method) \(.url)\n@body \(.body_b64)\n"' | vegeta attack -rate=1000/s -duration=60s
```

### Scaling captured traffic

Often you want to stress at 10× production rate. vegeta / goreplay have `-rate-multiplier` options.

---

## Generator tools

### `oha`

HTTP load generator with TUI. Good for quick tests.
```bash
oha -n 10000 -c 100 --rand-regex-url 'http://x/items/[0-9]{1,4}' http://x
```

### `k6`

Scriptable, JavaScript-based. Supports stages (ramp up, peak, ramp down).
```js
export let options = {
    stages: [
        { duration: '30s', target: 100 },
        { duration: '2m', target: 100 },
        { duration: '30s', target: 0 },
    ],
};
export default function () {
    // Zipfian key selection
    const key = zipfKey();
    http.get(`http://host/item/${key}`);
    sleep(0.1);
}
```

### `wrk2`

Constant-rate HTTP with Lua scripting.
```lua
-- wrk2 -s zipfian.lua -R 5000 -c 100 http://x/
local keys = {}
for i = 1, 10000 do
    keys[i] = string.format("item_%d", i)
end
request = function()
    local rank = zipf_sample(#keys, 1.0)
    return wrk.format("GET", "/item/" .. keys[rank])
end
```

### `vegeta`

Target file + rate + duration. Open-loop, excellent tail latency accuracy.
```bash
cat <<EOF > targets.txt
GET http://host/api/item/hot_key
GET http://host/api/item/hot_key
GET http://host/api/item/cold_key
...
EOF
vegeta attack -rate=1000/s -duration=30s -targets=targets.txt | vegeta report
```

### YCSB

Yahoo Cloud Serving Benchmark. Standard for KV stores. Has workloads A-F with tuned Zipf parameters.
```bash
ycsb run basic -P workloads/workloada -p recordcount=1000000 -p operationcount=1000000
```

### Stripe / payment-specific

For SaaS with Stripe / PayPal — realistic workloads include webhook retries, subscription lifecycle events, fraud attempts. See `stripe-checkout` skill.

---

## Realism checklist

Before declaring a bench "production-representative":

- [ ] Key distribution matches prod (Zipfian fit within ±20% on α)
- [ ] Arrival rate includes bursts, not just constant
- [ ] Payload sizes match production distribution
- [ ] Time-of-day peak represented if SLO applies at peak
- [ ] Response sizes match (not just request sizes)
- [ ] Tenant / user diversity — not a single user hammering
- [ ] Cache state — cold, warm, or hot as appropriate
- [ ] Error rate matches prod (some requests fail; retries matter)
- [ ] Geographic distribution, if latency is cross-region sensitive
- [ ] Authentication / session overhead included
- [ ] TLS / HTTP/2 / HTTP/3 matching prod
- [ ] Compression behavior (gzip / zstd) matching prod

If you can't check a box, the bench is representative only within that axis. Document in `DEFINE.md §Scope boundary`.

---

## Anti-patterns

- **One hot key, everything uniform else**: real prod isn't two modes
- **100% fresh requests, no cache hits**: a cached service benched cold misses the whole point
- **Single-threaded client doing HTTP**: the client is the bottleneck, not the server
- **Measuring "requests completed" without acknowledging queued**: open-loop vs closed-loop, see STATISTICAL-RIGOR.md
- **Changing the workload mid-bench**: kills comparability across runs
- **Huge client, tiny server (or vice versa)**: mismatched concurrency/IO
- **Skipping auth/TLS "because they're constant"**: they're rarely constant in prod; skew hides there
