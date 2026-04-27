# Container, Kubernetes, and Serverless Profiling

> Profiling changes materially when you go container → Kubernetes → serverless. This reference covers the shared host effects, cgroup limits, and cold-start specifics of each tier.

## Contents

1. [Docker / container profiling](#docker--container-profiling)
2. [Kubernetes pod profiling](#kubernetes-pod-profiling)
3. [Serverless: Lambda / Vercel Functions / Cloud Run](#serverless-lambda--vercel-functions--cloud-run)
4. [Cold-start analysis](#cold-start-analysis)
5. [Edge runtimes](#edge-runtimes)
6. [WebAssembly profiling](#webassembly-profiling)
7. [Noisy-neighbor diagnostics](#noisy-neighbor-diagnostics)
8. [Cloud-specific tools](#cloud-specific-tools)

---

## Docker / container profiling

### What's different from bare metal

1. **cgroup limits** — `cpu.max`, `memory.max`. Your container might be throttled despite the host being idle.
2. **Overlay filesystem** — file I/O goes through an overlay driver (overlay2 default); 5-20% write penalty vs bind mount.
3. **Network namespace** — loopback is real, external involves veth + bridge (negligible but nonzero).
4. **PID namespace** — `/proc/<pid>` inside container shows only in-container processes; outside shows all.
5. **Clock source** — usually fine, but in some VM hosts `vsyscall` fallback adds syscall cost.

### Measuring inside a container

```bash
# Check effective CPU limit
cat /sys/fs/cgroup/cpu.max        # e.g. "200000 100000" = 2 CPUs
# Legacy v1:
cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us
cat /sys/fs/cgroup/cpu/cpu.cfs_period_us

# Check memory limit
cat /sys/fs/cgroup/memory.max     # bytes
cat /sys/fs/cgroup/memory.current # current usage

# Throttling counter
cat /sys/fs/cgroup/cpu.stat       # throttled_usec — if growing, you're throttled
```

If `throttled_usec` is rising, your container is hitting CPU quota — raise `--cpus` or `resources.limits.cpu`.

### Run profilers inside the container

Most profilers work but need:
- **capabilities**: `CAP_SYS_ADMIN` for `perf`, `CAP_PERFMON` (modern kernels)
- **shared PID namespace** with host if attaching to host processes: `docker run --pid=host`
- **debug symbols** in the image (often stripped; use a debug variant)

```bash
# Add needed caps
docker run --cap-add=SYS_ADMIN --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
           -v /proc:/proc:ro \
           myimage profile-cmd

# samply works fine in containers with proper caps
samply record -- ./bin args
```

### Bind-mount host /proc for perf

For `perf record` to resolve kernel symbols:
```bash
docker run -v /proc:/proc:ro -v /sys:/sys:ro --cap-add=SYS_ADMIN ...
```

### Overlay filesystem impact

Build a bench that writes heavily and compare to a tmpfs / bind-mount:
```bash
docker run -v /fast/data:/data ...   # bind-mount to host; bypasses overlay
docker run --tmpfs /data ...          # tmpfs; fastest, not durable
```

If your bench shows 20% slowdown in the container vs bare metal on the same host, overlay is likely the culprit. Mount the data dir as bind or tmpfs.

---

## Kubernetes pod profiling

### Additions over Docker

1. **QoS class** (Guaranteed / Burstable / BestEffort) — affects scheduling
2. **Node-level neighbors** — other pods share CPU, network, storage
3. **Pod disruption / preemption** — profile runs cut short
4. **Init containers** — cold-start penalty
5. **Sidecars** (istio, linkerd) — add ~1-5ms per request

### Diagnostics

```bash
# Per-pod CPU / memory usage
kubectl top pod --containers

# Node-level pressure
kubectl describe node <node> | grep -A5 "Conditions\|Allocated"

# Is the pod being CPU-throttled?
kubectl exec <pod> -- cat /sys/fs/cgroup/cpu.stat | grep throttled

# Events (OOMKilled, preemption, etc.)
kubectl describe pod <pod> | grep -A20 Events
```

### Throttling metrics

Crucial Prometheus metric: `container_cpu_cfs_throttled_seconds_total`.
```promql
rate(container_cpu_cfs_throttled_seconds_total{pod="$pod"}[1m])
```

Non-zero = throttling is happening. Even "plenty of room per kubectl top" can hide throttling if limits are tight.

### Fix strategies

- **Raise limits** (but beware of node overcommit)
- **Switch to Guaranteed QoS** (set requests=limits)
- **Static CPU manager** on the node — pins pods to dedicated cores
- **Remove limits entirely** and rely on requests — better for latency-sensitive apps in some cases

### Profiling tools that work on K8s

- **`parca`** / **Pyroscope** — eBPF continuous profilers, run as DaemonSet; no app changes
- **Datadog Continuous Profiler** — agent DaemonSet
- **`kubectl cp` a profile out** — run profiler in pod, copy the artifact
- **`ephemeral containers`** (kubectl debug) — attach an image with profilers without rebuilding

```bash
kubectl debug -it <pod> --image=nicolaka/netshoot -- bash
# then run tools inside the ephemeral container
```

### Node-tuning matters

K8s inherits cgroup v2 + CPU manager policies. See OS-TUNING.md for host-level knobs; Guaranteed-class pods with static CPU manager get close-to-bare-metal perf.

---

## Serverless: Lambda / Vercel Functions / Cloud Run

### What's different

1. **Cold starts** — container spins up per request when idle; first request is slow
2. **Ephemeral CPU / RAM** — can change between invocations
3. **No persistent state** between invocations (or between regions)
4. **Limited observability hooks** — some can't run `perf`; rely on provider metrics

### AWS Lambda

Metrics:
- `Init Duration` (only on cold start) — init container + imports + handler warmup
- `Billed Duration` — user-visible run time
- `Max Memory Used` — actually used memory
- `Duration` — total execution

Profile via:
- **CloudWatch Lambda Insights** — enable; get per-invocation CPU/memory
- **AWS X-Ray** — tracing; segments per function call
- **Lambda Powertools** — custom metrics, tracer, idempotency

Cold-start mitigations:
- **Provisioned Concurrency** — pre-warmed instances; pay per GB-s whether used or not
- **Smaller deployment** — fewer imports, native compilation
- **Container images** — sometimes slower cold-start than zips; measure
- **SnapStart** (Java) — snapshot of initialized JVM; ~300ms cold → ~50ms
- **Move to Rust / Go** — near-zero cold starts

### Vercel Functions

Similar model; metrics:
- `x-vercel-fn-duration` header (real function time)
- `x-vercel-cache` (HIT/MISS/STALE)
- Vercel Observability dashboard — P50/P95/P99 per function
- Fluid Compute — mitigates cold starts for Node/Python by keeping workers warm

See `vercel:vercel-functions` skill for specifics.

### Google Cloud Run

- `--cpu-boost` — double CPU for first 10s (startup)
- `--min-instances=1` — prevents scale-to-zero cold start
- Request-based concurrency — multiple requests share one instance
- Cloud Profiler integration via agent

---

## Cold-start analysis

### Decompose cold start

```
Total cold start = 
    container pull/start time +
    runtime init (JVM, Python import, Node require) +
    handler cold path (connection pool open, cache prewarm) +
    first request execution
```

Measure each separately:

**Container**: provider-reported `Init Duration` (or time before your handler is entered)
**Runtime init**: wrap handler with `perf_counter()` before and after imports
**Cold handler**: first-request timing separate from subsequent

### Cold-start triage

| Dominant phase | Fix |
|----------------|-----|
| Container pull/start (> 500ms) | Smaller image; provisioned concurrency |
| Runtime init (> 300ms) | Fewer imports; lazy load; smaller dependencies |
| Handler cold path (> 200ms) | Connection pool pre-open; load state on init hook |
| First request itself (> 100ms) | JIT warmup (rarely helps for serverless); move to AOT |

### Python import profiling

```bash
python -X importtime -c 'import mymodule' 2> importtime.log
cat importtime.log | sort -k2 -n | tail -30   # slowest imports
```

### Node startup

```bash
node --inspect-brk=0.0.0.0:9229 app.js   # connect Chrome DevTools, profile the init phase
```

Or:
```bash
node --cpu-prof --cpu-prof-dir=./prof app.js
# look at the flame during the first second
```

---

## Edge runtimes

Vercel Edge, Cloudflare Workers, Deno Deploy — V8 isolates, not containers.

### Characteristics

- Near-zero cold start (ms)
- Limited CPU time per request (10-50ms typical)
- No filesystem
- Limited npm compatibility (Web APIs only, no `node:*`)

### Profiling

Limited; mostly provider-side metrics + structured logging:
- Cloudflare Workers: `cf-ray`, tail workers, Workers Analytics
- Vercel Edge: request logs + Observability tab

The usual `--cpu-prof` / `samply` don't work inside isolates. Instead:
- Log p95 per route
- Instrument with `performance.now()` deltas
- Use provider's trace IDs to correlate across hops

### Optimizations

- Minimize bundle size (ship less JS)
- Avoid expensive imports at module top-level
- Use `KV` / `Durable Objects` / `R2` for state, not filesystem
- Stream responses to improve TTFT

---

## WebAssembly profiling

### In browser

- Chrome DevTools Profiler — shows Wasm frames (with names if `.wasm` has a `names` section)
- Firefox Profiler — same

Emit debug info in build:
```
# Rust → wasm
cargo build --target wasm32-unknown-unknown --release
# then wasm-snip / wasm-opt with names preserved
```

### Outside browser

- **wasmtime** `--profile=perfmap` → perf-compatible output
- **wasmer** `--tracing`

Performance counter access is limited in Wasm; rely on internal instrumentation.

---

## Noisy-neighbor diagnostics

Shared hosts (cloud VMs, K8s nodes, CI runners) have neighbors affecting your measurement.

### Symptoms

- Bench results vary more than CV should allow
- p99 spikes correlate with calendar (cron, backups)
- Performance drops when "nothing changed in our code"

### Diagnostics

```bash
# Steal time (hypervisor stealing cycles from your VM)
top   # look for "st" column in the header, or:
vmstat 1  # "st" column

# If %st > 1-2%, you're sharing a host with noisy tenants
```

### Fixes

- Dedicated instances (EC2 Dedicated Host, bare-metal instance type)
- K8s: static CPU manager + Guaranteed QoS + node-exclusive pods
- Pin bench to off-peak hours (nights, weekends) for statistical work
- Use instance types with SRIOV and dedicated CPUs (`m5d.metal` etc.)

---

## Cloud-specific tools

### AWS

- **CloudWatch Application Signals** — RED metrics (Rate / Errors / Duration) per service
- **AWS X-Ray** — distributed tracing
- **CodeGuru Profiler** — continuous profiler (Java, Python) with recommendations
- **EBS / EFS / FSx metrics** — storage-side latency
- **Compute Optimizer** — recommends instance type based on usage

### GCP

- **Cloud Profiler** — continuous profiler (Java, Go, Node, Python)
- **Cloud Trace** — distributed traces
- **Cloud Monitoring** — metrics, dashboards

### Azure

- **Application Insights** — traces + metrics + profiler
- **Azure Monitor Container Insights** — AKS pod-level

### Vercel

- **Observability** — function duration, cache hit rate, error rate
- **Speed Insights** — Core Web Vitals from real users
- **Analytics** — page-level performance
- **`vercel:deployments-cicd`** skill — deployment-level diagnostics

### Datadog / New Relic / Honeycomb

Third-party APM + continuous profilers. More cross-cloud but cost real money.

---

## What to capture in a container/cloud profile run

```
tests/artifacts/perf/<run-id>/container/
├── cgroup_stats.txt            # cpu.stat, memory.current, memory.max
├── throttled_time.csv          # per-second sampling of throttled_usec
├── pod_describe.txt            # kubectl describe pod output (if K8s)
├── steal_time.csv              # %st from vmstat over run
├── provider_logs.json          # CloudWatch / Vercel / GCP Monitoring snapshot
├── cold_start_breakdown.json   # if measuring serverless cold starts
└── image_size.txt              # deploy artifact size (matters for serverless cold start)
```

Fingerprint.json for containerized runs must include cgroup limits, QoS class, node/instance type.

---

## Cross-references

- **`vercel:vercel-functions`** / `vercel:knowledge-update` — Vercel-specific Function and Edge profiling
- **`supabase`** — when the DB is Supabase-hosted Postgres
- **`gcloud`** — GCP-specific CLI operations
- OS-TUNING.md — host-level tuning (applies to nodes, not pods)
- CI-REGRESSION-GATES.md — runner match concerns intensify when the runner is a cloud VM
