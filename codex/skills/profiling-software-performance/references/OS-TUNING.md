# OS Tuning for Profiling Accuracy

> Kernel knobs that visibly move benchmark numbers. **All changes require sudo and are global.** Before running anything here, paste the proposed list to the user and ask "apply these?" — changes persist for the machine until reverted.

## Contents

1. [Confirmation script (paste to user first)](#confirmation-script-paste-to-user-first)
2. [Linux — profiling permissions](#linux--profiling-permissions)
3. [Linux — CPU determinism](#linux--cpu-determinism)
4. [Linux — memory / page cache](#linux--memory--page-cache)
5. [Linux — I/O scheduler](#linux--io-scheduler)
6. [Linux — filesystem mount options](#linux--filesystem-mount-options)
7. [macOS](#macos)
8. [Restore / undo block](#restore--undo-block)
9. [Persistence](#persistence)
10. [Verification](#verification)

---

## Confirmation script (paste to user first)

Before running any tuning, present this summary to the user and wait for explicit "yes, apply":

```
About to apply these kernel tuning changes for accurate profiling:

PROFILING PERMISSIONS
  kernel.perf_event_paranoid: 2 → -1         (lets unprivileged users record perf)
  kernel.kptr_restrict: 1 → 0                (resolve kernel symbols in stacks)
  kernel.yama.ptrace_scope: 1 → 0            (optional: lets py-spy/memray attach)

CPU DETERMINISM
  cpu governor: schedutil/powersave → performance
  intel_pstate no_turbo: 0 → 1               (disable Turbo Boost)
  kernel.nmi_watchdog: 1 → 0                 (frees a PMU counter)

None of these changes persist across reboots (unless you opt in to the persistence block).
Reverts are logged at the end.

Apply? [y/N]
```

Document the user's "yes" in the run notes: approver: <name or handle> — approval at <timestamp>.

---

## Linux — profiling permissions

```bash
# Allow unprivileged perf_event_open (samply, perf, eBPF profilers)
sudo sysctl -w kernel.perf_event_paranoid=-1
# Levels:
#   3 = deny all perf_event_open
#   2 = default — no kernel profiling, no tracepoints, no CPU
#   1 = allow CPU/tracepoints, no kernel
#   0 = above + raw tracepoints
#  -1 = no restrictions

# Resolve kernel symbols in flame graphs (else [k] 0xffff... in stacks)
sudo sysctl -w kernel.kptr_restrict=0

# Enable live-attach profilers (py-spy --pid, memray attach, gdb -p)
sudo sysctl -w kernel.yama.ptrace_scope=0       # 0=permissive, 1=same user, 2=capabilities, 3=off

# Raise open-file and memory-lock limits for heavy profiling loads
ulimit -n 1048576
ulimit -l unlimited                             # required for huge-page + some eBPF tools

# Check current state
sudo sysctl kernel.perf_event_paranoid kernel.kptr_restrict kernel.yama.ptrace_scope
```

---

## Linux — CPU determinism

```bash
# Governor: performance (no P-state jitter)
sudo cpupower frequency-set -g performance
# or without cpupower:
for c in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do echo performance | sudo tee "$c"; done

# Disable Turbo Boost (Intel)
echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo
# AMD (amd_pstate) — boost control
echo 0 | sudo tee /sys/devices/system/cpu/cpufreq/boost

# Disable SMT / hyper-threading (removes sibling-thread contention noise)
echo off | sudo tee /sys/devices/system/cpu/smt/control
# Re-enable:
echo on | sudo tee /sys/devices/system/cpu/smt/control

# Disable NMI watchdog (frees one PMU counter)
sudo sysctl -w kernel.nmi_watchdog=0

# CPU isolation (best: boot-time) — requires kernel cmdline changes and reboot
# /etc/default/grub: GRUB_CMDLINE_LINUX="isolcpus=2,3 nohz_full=2,3 rcu_nocbs=2,3"
# sudo update-grub && reboot
# Then pin benchmark:
taskset -c 2,3 chrt -f 50 ./bin args            # SCHED_FIFO priority 50 on cores 2,3

# For a quick session-only approximation without reboot:
# Move all shells to cgroup "background", benchmark to cgroup "foreground" with cpuset
sudo cgcreate -g cpuset:/bench
echo "2,3" | sudo tee /sys/fs/cgroup/cpuset/bench/cpuset.cpus
echo 0     | sudo tee /sys/fs/cgroup/cpuset/bench/cpuset.mems
sudo cgexec -g cpuset:bench ./bin args
```

Show `/proc/$PID/status | grep Cpus_allowed_list` to verify pinning.

---

## Linux — memory / page cache

```bash
# Drop caches before cold-cache runs
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
# Values: 1=pagecache, 2=dentries+inodes, 3=both

# Keep anon pages, aggressively reclaim page cache (workload-owner default)
sudo sysctl -w vm.swappiness=10                # default 60

# Keep dentries/inodes in cache longer (helps small-file workloads)
sudo sysctl -w vm.vfs_cache_pressure=50        # default 100; lower = retain

# Dirty page policy — lower avoids huge fsync spikes
sudo sysctl -w vm.dirty_ratio=10               # default 20 (% of RAM before sync-writes block)
sudo sysctl -w vm.dirty_background_ratio=5     # default 10 (% before async flusher kicks in)
sudo sysctl -w vm.dirty_expire_centisecs=3000  # default 3000 (30s before dirty page must be flushed)

# Transparent huge pages — reduces TLB noise for large working sets
echo madvise | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
# Alternatives: always (aggressive), madvise (opt-in via madvise), never

# Explicit huge pages (for database buffer pools etc.)
sudo sysctl -w vm.nr_hugepages=1024            # reserves 2GiB (1024 × 2MiB)
```

---

## Linux — I/O scheduler

```bash
# List current
for d in /sys/block/nvme*/queue/scheduler /sys/block/sd*/queue/scheduler; do echo "$d:"; cat "$d"; done

# NVMe / ultra-low-latency: none (mq-deadline is also fine)
dev="${PROFILE_BLOCK_DEVICE:?set PROFILE_BLOCK_DEVICE to the benchmark block device name}"
echo none | sudo tee "/sys/block/$dev/queue/scheduler"
# SATA SSD: mq-deadline
echo mq-deadline | sudo tee /sys/block/sda/queue/scheduler
# Rotational: bfq (better for interactive mix) or mq-deadline (throughput)

# Queue depth
cat "/sys/block/$dev/queue/nr_requests"       # raise for heavy-concurrency workloads
echo 1024 | sudo tee "/sys/block/$dev/queue/nr_requests"

# Read-ahead (KiB)
sudo blockdev --getra "/dev/$dev"             # current
sudo blockdev --setra 256 "/dev/$dev"         # lower for random workloads
```

---

## Linux — filesystem mount options

Remount options require FS-specific fields — audit with `findmnt -T $(pwd)` first. Full table in [IO-AND-TRADEOFFS.md](IO-AND-TRADEOFFS.md#filesystem-specific-gotchas).

```bash
# Remount with noatime (stops write-per-read)
sudo mount -o remount,noatime /mount

# ext4 — switch journal mode
sudo mount -o remount,data=ordered /mount      # (default — safe)

# btrfs — enable autodefrag for small-random-write workloads
sudo mount -o remount,autodefrag /mount
# Or for a specific DB file, disable CoW *before first write*:
sudo chattr +C /path/to/db.sqlite

# XFS — prevents sparse-file fragmentation on streaming writes
sudo mount -o remount,allocsize=1m /mount
```

---

## macOS

macOS lacks most Linux knobs. The achievable set:

```bash
# Show power assertions blocking sleep / throttling the CPU
pmset -g assertions

# CPU power budget visualization (Apple Silicon)
sudo powermetrics --samplers cpu_power -i 1000
# → see P-core / E-core frequency, power rails; proves whether thermal/power-cap is active

# Prevent sleep during profile capture
caffeinate -di ./bin args

# SIP status (SIP severely limits dtrace/kernel profiling on Apple Silicon)
csrutil status
# Do NOT disable SIP on a primary machine. If you must use dtrace, boot into recovery.

# Disable Spotlight on the project volume (stops I/O noise)
sudo mdutil -i off /Volumes/BenchData
# Re-enable
sudo mdutil -i on  /Volumes/BenchData

# macOS profilers that don't need SIP off:
sample <pid> 5 -f sample.txt           # 5-second sampling profile (no install)
spindump <pid> 10 -file spindump.txt   # hang / stall analysis
xctrace record --template 'Time Profiler' --launch -- ./bin args --output trace.trace
samply record -- ./bin args            # Firefox Profiler backend, recommended
```

Gotchas specific to macOS:

- SIP on Apple Silicon crippled `dtrace` — use `sample`/`xctrace`/`samply` instead.
- Rosetta processes report x86 stacks only; run native arm64 for correct attribution.
- Fan curves are thermal-aware; a thermally-throttled macOS machine reports lower CPU frequency silently. Always `powermetrics` alongside benchmarks.

---

## Restore / undo block

Keep this block at the bottom of the run notes; **paste and run to revert every change above**.

```bash
# Profiling permissions — Ubuntu defaults
sudo sysctl -w kernel.perf_event_paranoid=2
sudo sysctl -w kernel.kptr_restrict=1
sudo sysctl -w kernel.yama.ptrace_scope=1
sudo sysctl -w kernel.nmi_watchdog=1

# CPU — Ubuntu defaults
sudo cpupower frequency-set -g schedutil        # or powersave
echo 0 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo
echo on | sudo tee /sys/devices/system/cpu/smt/control

# Memory / VM — Ubuntu defaults
sudo sysctl -w vm.swappiness=60
sudo sysctl -w vm.vfs_cache_pressure=100
sudo sysctl -w vm.dirty_ratio=20
sudo sysctl -w vm.dirty_background_ratio=10
echo madvise | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
sudo sysctl -w vm.nr_hugepages=0

# I/O — as previous value
dev="${PROFILE_BLOCK_DEVICE:?set PROFILE_BLOCK_DEVICE to the benchmark block device name}"
echo mq-deadline | sudo tee "/sys/block/$dev/queue/scheduler"
sudo blockdev --setra 128 "/dev/$dev"
```

Record the user-observed defaults *before* applying changes by piping to a file:
```bash
sudo sysctl kernel.perf_event_paranoid kernel.kptr_restrict kernel.yama.ptrace_scope kernel.nmi_watchdog vm.swappiness vm.vfs_cache_pressure vm.dirty_ratio > /tmp/pre-tune.sysctl
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor >> /tmp/pre-tune.sysctl
```

---

## Persistence

Only with explicit user approval — these survive reboot:

```bash
# sysctl
sudo tee /etc/sysctl.d/99-profiling.conf <<'EOF'
kernel.perf_event_paranoid = -1
kernel.kptr_restrict = 0
kernel.nmi_watchdog = 0
vm.swappiness = 10
vm.vfs_cache_pressure = 50
EOF
sudo sysctl --system

# CPU governor on boot
sudo systemctl enable --now cpupower.service
# /etc/default/cpupower → GOVERNOR="performance"

# Kernel cmdline — CPU isolation, no HT
sudoedit /etc/default/grub
# GRUB_CMDLINE_LINUX_DEFAULT="quiet splash isolcpus=2,3 nohz_full=2,3 rcu_nocbs=2,3 nosmt"
sudo update-grub && sudo reboot

# Mount options — edit /etc/fstab or subvolume-level btrfs flags
```

**Default policy: don't persist.** Leave changes session-scoped so a reboot restores normal state. Persist only if the machine is a dedicated bench host.

---

## Verification

After tuning, capture the state and attach to the fingerprint:

```bash
sudo sysctl kernel.perf_event_paranoid kernel.kptr_restrict kernel.yama.ptrace_scope kernel.nmi_watchdog
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
cat /sys/devices/system/cpu/intel_pstate/no_turbo 2>/dev/null
cat /sys/devices/system/cpu/smt/active
cat /sys/kernel/mm/transparent_hugepage/enabled
findmnt -T $(pwd) -o SOURCE,FSTYPE,OPTIONS
grep MemAvailable /proc/meminfo
```

Put the output under `tests/artifacts/perf/<run-id>/tuning.json`. If any future run doesn't match, the comparison is invalid — same-host boundary in fingerprint checks.

---

## Common mistakes

| Mistake | Consequence |
|---------|-------------|
| Forgot governor → performance | p99 varies 5-30% run to run as CPU ramps |
| Left `no_turbo=0` | First samples are cold, later ones are turbo-boosted → fake speedup |
| SMT on, benchmark and noise on sibling threads | Sporadic tail latency from neighbor |
| `drop_caches` only once | First warm run cheats; subsequent cold runs depend on what else loaded |
| Didn't record pre-tune state | Can't undo cleanly |
| Tuned a non-idle machine | Background work contaminates everything |
