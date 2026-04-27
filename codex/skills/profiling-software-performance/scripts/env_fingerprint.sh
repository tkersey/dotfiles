#!/usr/bin/env bash
# env_fingerprint.sh — capture a machine-readable fingerprint of the host,
# toolchain, and build profile. Emits JSON to stdout.
#
# Usage: ./env_fingerprint.sh [--run-id <id>] [--build-profile <name>] > fingerprint.json
#
# Mirrors the fingerprint.json template in references/ARTIFACTS.md.

set -euo pipefail

RUN_ID="${RUN_ID:-$(date -u '+%s_%6N')}"
BUILD_PROFILE="${BUILD_PROFILE:-release-perf}"

while [ $# -gt 0 ]; do
    case "$1" in
        --run-id) RUN_ID="$2"; shift 2 ;;
        --build-profile) BUILD_PROFILE="$2"; shift 2 ;;
        -h|--help)
            sed -n '2,8p' "$0" | sed 's/^# //'
            exit 0 ;;
        *) echo "unknown arg: $1" >&2; exit 1 ;;
    esac
done

# Helpers
get_or() { local v; v=$(eval "$1" 2>/dev/null || true); [ -n "$v" ] && printf '%s' "$v" || printf '%s' "$2"; }
json_str() { python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))'; }

# Hardware
CPU_MODEL=$(get_or "lscpu | awk -F: '/^Model name:/{sub(/^[ \t]+/,\"\",\$2);print \$2;exit}'" "unknown")
CPU_CORES=$(get_or "lscpu | awk -F: '/^Core\\(s\\) per socket:/{print \$2}' | tr -d ' '" "0")
CPU_SOCKETS=$(get_or "lscpu | awk -F: '/^Socket\\(s\\):/{print \$2}' | tr -d ' '" "1")
CPU_THREADS=$(get_or "nproc" "0")
CPU_MHZ=$(get_or "lscpu | awk -F: '/^CPU MHz:/{print \$2; exit}' | tr -d ' '" "")

RAM_TOTAL=$(get_or "grep MemTotal /proc/meminfo | awk '{print \$2\" \"\$3}'" "unknown")
SWAP_TOTAL=$(get_or "grep SwapTotal /proc/meminfo | awk '{print \$2\" \"\$3}'" "unknown")

# Storage
MNT_POINT="$(pwd)"
MNT_INFO=$(findmnt -T "$MNT_POINT" -o SOURCE,FSTYPE,OPTIONS -n 2>/dev/null || echo "unknown unknown unknown")
MNT_SOURCE=$(echo "$MNT_INFO" | awk '{print $1}')
MNT_FSTYPE=$(echo "$MNT_INFO" | awk '{print $2}')
MNT_OPTIONS=$(echo "$MNT_INFO" | awk '{print $3}')

DEVICE_MODEL="unknown"
if [ -b "$MNT_SOURCE" ]; then
    DEVICE_MODEL=$(get_or "lsblk -ndo MODEL '$MNT_SOURCE' 2>/dev/null" "unknown")
fi

# OS
OS_DISTRO=$(get_or "grep PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '\"'" "$(uname)")
KERNEL=$(uname -r)

# Toolchain (best-effort; report whichever are installed)
RUSTC=$(get_or "rustc --version 2>/dev/null" "")
GO=$(get_or "go version 2>/dev/null" "")
NODE=$(get_or "node --version 2>/dev/null" "")
PYTHON=$(get_or "python3 --version 2>/dev/null" "")
CLANG=$(get_or "clang --version 2>/dev/null | head -1" "")
GCC=$(get_or "gcc --version 2>/dev/null | head -1" "")

# Tuning state
GOVERNOR=$(get_or "cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor" "unknown")
NO_TURBO=$(get_or "cat /sys/devices/system/cpu/intel_pstate/no_turbo" "n/a")
SMT_ACTIVE=$(get_or "cat /sys/devices/system/cpu/smt/active" "n/a")
PARANOID=$(get_or "cat /proc/sys/kernel/perf_event_paranoid" "")
KPTR=$(get_or "cat /proc/sys/kernel/kptr_restrict" "")
NMI_WATCHDOG=$(get_or "cat /proc/sys/kernel/nmi_watchdog" "")
THP=$(get_or "cat /sys/kernel/mm/transparent_hugepage/enabled | grep -oP '\\[\\K[^]]+'" "unknown")

# Git
GIT_SHA=$(get_or "git rev-parse HEAD 2>/dev/null" "unknown")
GIT_DIRTY="false"
if [ -n "$(git status --porcelain 2>/dev/null || true)" ]; then GIT_DIRTY="true"; fi

# Timestamp
NOW_UTC=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

# Emit JSON
cat <<JSON
{
  "run_id": $(printf '%s' "$RUN_ID" | json_str),
  "captured_at_utc": $(printf '%s' "$NOW_UTC" | json_str),
  "git_sha": $(printf '%s' "$GIT_SHA" | json_str),
  "git_dirty": $GIT_DIRTY,
  "hardware": {
    "cpu_model": $(printf '%s' "$CPU_MODEL" | json_str),
    "cpu_cores_per_socket": $CPU_CORES,
    "cpu_sockets": $CPU_SOCKETS,
    "cpu_threads_total": $CPU_THREADS,
    "cpu_mhz_reported": $(printf '%s' "$CPU_MHZ" | json_str),
    "ram_total": $(printf '%s' "$RAM_TOTAL" | json_str),
    "swap_total": $(printf '%s' "$SWAP_TOTAL" | json_str)
  },
  "storage": {
    "device": $(printf '%s' "$MNT_SOURCE" | json_str),
    "model": $(printf '%s' "$DEVICE_MODEL" | json_str),
    "mount_point": $(printf '%s' "$MNT_POINT" | json_str),
    "filesystem": $(printf '%s' "$MNT_FSTYPE" | json_str),
    "mount_options": $(printf '%s' "$MNT_OPTIONS" | json_str)
  },
  "os": {
    "distribution": $(printf '%s' "$OS_DISTRO" | json_str),
    "kernel": $(printf '%s' "$KERNEL" | json_str)
  },
  "toolchain": {
    "rustc": $(printf '%s' "$RUSTC" | json_str),
    "go": $(printf '%s' "$GO" | json_str),
    "node": $(printf '%s' "$NODE" | json_str),
    "python": $(printf '%s' "$PYTHON" | json_str),
    "clang": $(printf '%s' "$CLANG" | json_str),
    "gcc": $(printf '%s' "$GCC" | json_str)
  },
  "build_profile": {
    "name": $(printf '%s' "$BUILD_PROFILE" | json_str)
  },
  "tuning_applied": {
    "governor": $(printf '%s' "$GOVERNOR" | json_str),
    "no_turbo": $(printf '%s' "$NO_TURBO" | json_str),
    "smt_active": $(printf '%s' "$SMT_ACTIVE" | json_str),
    "perf_event_paranoid": $(printf '%s' "$PARANOID" | json_str),
    "kptr_restrict": $(printf '%s' "$KPTR" | json_str),
    "nmi_watchdog": $(printf '%s' "$NMI_WATCHDOG" | json_str),
    "thp": $(printf '%s' "$THP" | json_str)
  }
}
JSON
