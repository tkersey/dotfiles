# GPU and Accelerator Profiling

> CUDA / ROCm / Metal / Vulkan compute. Mostly relevant when profiling ML inference, training, or heavy compute offload. The mental model shifts from "where does time go" (CPU) to "where do GPU SM's stall" and "how do data transfers dominate."

## Contents

1. [GPU perf mental model](#gpu-perf-mental-model)
2. [NVIDIA (CUDA) tools](#nvidia-cuda-tools)
3. [AMD (ROCm) tools](#amd-rocm-tools)
4. [Apple (Metal) tools](#apple-metal-tools)
5. [Common GPU bottlenecks](#common-gpu-bottlenecks)
6. [Profiling ML training](#profiling-ml-training)
7. [Profiling ML inference](#profiling-ml-inference)

---

## GPU perf mental model

GPU performance breaks down along:

- **Compute utilization (SM busy %)** — are the cores doing work?
- **Memory bandwidth** — DRAM is often the ceiling
- **Transfer overhead** — PCIe to/from host
- **Kernel launch overhead** — many tiny kernels add up
- **Synchronization** — `cudaStreamSynchronize` serializes
- **Thermal throttling** — GPU, like CPU, slows under heat

Unlike CPUs, GPUs rarely have the app "CPU bound" — usually either memory-bound, transfer-bound, or underutilized (too small a batch).

---

## NVIDIA (CUDA) tools

### `nvidia-smi` — always start here

```bash
# Snapshot
nvidia-smi

# Continuous
nvidia-smi dmon -s pucvmet -c 100
# p=power u=util c=clock v=voltage m=memory e=encode/decode t=temperature

# Per-process
nvidia-smi pmon -s um -c 30

# Check for errors / ECC
nvidia-smi -q -d ECC
```

Key fields to watch:
- **GPU util** — target > 80% for compute-heavy; < 40% = bottleneck elsewhere
- **Memory util** — target > 80% for memory-bound workloads
- **Power (W)** — near TDP = thermally limited or compute-limited; well below = not saturated
- **Memory used** — how close to VRAM ceiling?

### Nsight Systems

System-wide timeline. Shows CPU + GPU + CUDA API + NVTX ranges.

```bash
nsys profile -o report ./bin args
nsys stats report.nsys-rep
nsys-ui report.nsys-rep    # GUI
```

Find: kernel launches, memory transfers, CPU-GPU synchronization points.

### Nsight Compute

Per-kernel deep dive (roofline, stall reasons).

```bash
ncu --set full -o report ./bin args
ncu-ui report.ncu-rep    # GUI
```

Finds: memory stalls, instruction stalls, occupancy issues. Much deeper than Nsight Systems.

### CUPTI / PyTorch profiler

```python
# PyTorch
import torch.profiler as p
with p.profile(activities=[p.ProfilerActivity.CPU, p.ProfilerActivity.CUDA],
               record_shapes=True, profile_memory=True) as prof:
    model(input)
print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=20))
prof.export_chrome_trace("trace.json")
```

Good enough for most ML work. Chrome trace opens in `chrome://tracing`.

### TensorBoard profiler

```python
with tf.profiler.experimental.Profile('logdir'):
    train_step()
# tensorboard --logdir logdir
```

TF equivalent; similar views.

---

## AMD (ROCm) tools

### `rocm-smi`

```bash
rocm-smi
rocm-smi --showuse --showpower --showtemp --showclocks
rocm-smi --showpids
```

### `rocprof`

```bash
rocprof --stats ./bin args
rocprof --hip-trace --hsa-trace -o trace.json ./bin args   # Chrome trace
```

### Omniperf

```bash
omniperf profile -n workload_name -- ./bin args
omniperf analyze -p workloads/workload_name/mi300x
```

Deep kernel-level analysis, similar to Nsight Compute.

---

## Apple (Metal) tools

### Metal System Trace (Instruments)

```bash
xcrun xctrace record --template 'Metal System Trace' --launch ./app
open *.trace    # Instruments GUI
```

Shows:
- Command buffer submissions
- GPU counters (throughput, memory stalls)
- CPU ↔ GPU sync points

### Metal frame capture

```swift
// Set an env var, then run a frame
// MTL_CAPTURE_ENABLED=1
// Frame capture in Xcode debugger
```

GUI in Xcode with per-command-buffer frame timeline.

### `powermetrics` for M-series

```bash
sudo powermetrics --samplers gpu_power -i 1000
```

Per-sample GPU power, frequency, residency per P-core / E-core / GPU cluster.

---

## Common GPU bottlenecks

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| GPU util < 30% | CPU-side bottleneck (dataloader, host prep) | Increase worker threads, pin memory, prefetch |
| Memory util ~100%, compute low | Memory-bandwidth-bound | Fuse kernels, reduce memory ops, tensor layouts |
| Many tiny kernels | Launch overhead | Kernel fusion (torch.compile, XLA), CUDA Graphs |
| PCIe transfers dominate | CPU ↔ GPU chatter | Pin memory, pipeline transfers, keep tensors on device |
| Occupancy low per Nsight | Register / shared mem too high per block | Reduce per-thread resources, smaller block size |
| Thermal throttle mid-run | Cooling insufficient | Undervolt, better cooling, `nvidia-smi -pl <watts>` |
| OOM (out of memory) | VRAM ceiling | Smaller batch, gradient checkpoint, mixed precision |

---

## Profiling ML training

Key metrics:
- **Tokens/sec throughput** (for LLMs) or **samples/sec** (vision)
- **GPU util over time** — flat ~90% = good; sawtooth = dataloader bottleneck
- **Peak VRAM**
- **Time per step** — median, p95

```python
# PyTorch training loop with profiler
import torch.profiler as p
prof = p.profile(
    schedule=p.schedule(wait=1, warmup=1, active=5, repeat=2),
    on_trace_ready=p.tensorboard_trace_handler('./log'),
    record_shapes=True, profile_memory=True, with_stack=True,
)
prof.start()
for step, batch in enumerate(loader):
    if step >= 20: break
    train_step(batch)
    prof.step()
prof.stop()
```

Then `tensorboard --logdir=./log` — "PyTorch Profiler" tab shows:
- GPU kernel time
- CPU time
- DataLoader time (if this dominates, workers are too few)
- Memory timeline

---

## Profiling ML inference

Different metrics than training:
- **Single-request latency** (TTFT for streaming, total for non-streaming)
- **Throughput under concurrency** (batch size tuning)
- **Memory budget** (can you fit the model + KV cache?)

See LLM-AI-PROFILING.md §"Local inference profiling" for vLLM / llama.cpp specifics.

For a small image model:
```python
# Warmup + timed loop with torch.cuda.Event for GPU timing
import torch
model = model.cuda().eval()
inputs = torch.randn(1, 3, 224, 224).cuda()
start = torch.cuda.Event(enable_timing=True)
end = torch.cuda.Event(enable_timing=True)

# Warmup
for _ in range(10): _ = model(inputs)
torch.cuda.synchronize()

# Measure
times = []
for _ in range(100):
    start.record()
    _ = model(inputs)
    end.record()
    torch.cuda.synchronize()
    times.append(start.elapsed_time(end))

print(f"p50 {sorted(times)[50]:.2f}ms  p95 {sorted(times)[95]:.2f}ms")
```

Note: `torch.cuda.synchronize()` is required for accurate timing; otherwise you're timing kernel launches, not execution.

---

## Artifacts to capture

```
tests/artifacts/perf/<run-id>/gpu/
├── nvidia_smi_over_time.csv       # nvidia-smi dmon output during run
├── nsys_report.nsys-rep
├── torch_profiler_trace.json      # Chrome trace from torch.profiler
├── gpu_utilization.csv            # time-series util%, mem%, power
├── peak_vram.txt
├── kernel_breakdown.csv           # top-N kernels by time
└── thermal_log.csv                # GPU temp over time (watch for throttling)
```

Reference from hotspot_table.md when GPU hotspots dominate.
