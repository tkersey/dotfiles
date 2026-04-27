#!/usr/bin/env bash
# profile_init.sh — User-gated initializer for OS-level profiling accuracy.
#
# WHAT IT DOES: prints the set of sysctl / cpupower / P-state knobs that improve
# profile fidelity on Linux, shows the exact commands, captures the current state
# so it can be reverted, and ONLY applies when the user types APPLY.
#
# Matches the "ask first" policy from references/OS-TUNING.md.
#
# Usage:
#   profile_init.sh           # print plan + current state, prompt for APPLY
#   profile_init.sh --revert  # restore captured state from the most recent snapshot
#   profile_init.sh --dry-run # print plan only, never prompt

set -euo pipefail

state_dir="${XDG_STATE_HOME:-$HOME/.local/state}/profiling-software-performance"
mkdir -p "$state_dir"

mode="prompt"
case "${1:-}" in
  --revert)  mode="revert";;
  --dry-run) mode="dry";;
  "")        mode="prompt";;
  *)         echo "unknown: $1"; exit 2;;
esac

# --- Plan ---------------------------------------------------------------
cat <<'PLAN'
The following changes improve profile accuracy on Linux. They require sudo and
change global machine state. Review each one:

  1. kernel.perf_event_paranoid = -1     (or 1)  — let perf see kernel stacks
  2. kernel.kptr_restrict       =  0              — resolve kernel symbols
  3. kernel.nmi_watchdog        =  0              — free a PMU counter
  4. cpupower frequency-set -g performance        — pin max clock
  5. intel_pstate/no_turbo      =  1              — disable turbo jitter
  6. disable SMT (optional, invasive)             — one logical core per physical

PLAN

# --- Revert mode --------------------------------------------------------
if [[ "$mode" == "revert" ]]; then
  latest=$(ls -1t "$state_dir"/snapshot-*.env 2>/dev/null | head -1)
  [[ -n "$latest" ]] || { echo "no snapshot to revert"; exit 2; }
  echo "Reverting from $latest ..."
  # shellcheck disable=SC1090
  source "$latest"
  _apply() {
    local key="$1" val="$2"
    if [[ "$val" == "unknown" || -z "$val" ]]; then
      echo "  skip $key — no captured value"
      return
    fi
    sudo sysctl -w "$key=$val"
  }
  _apply kernel.perf_event_paranoid "$perf_event_paranoid"
  _apply kernel.kptr_restrict       "$kptr_restrict"
  _apply kernel.nmi_watchdog        "$nmi_watchdog"
  [[ "$governor" != "unknown" && -n "$governor" ]] && (sudo cpupower frequency-set -g "$governor" || true)
  [[ "$no_turbo" != "unknown" && -n "$no_turbo" ]] && (echo "$no_turbo" | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo >/dev/null 2>&1 || true)
  [[ "$smt" != "unknown" && -n "$smt" ]] && (echo "$smt" | sudo tee /sys/devices/system/cpu/smt/control >/dev/null 2>&1 || true)
  echo "Revert complete."
  exit 0
fi

# --- Capture current state ----------------------------------------------
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
snapshot="$state_dir/snapshot-${stamp}.env"
{
  echo "# Captured $stamp"
  echo "perf_event_paranoid=$(sysctl -n kernel.perf_event_paranoid 2>/dev/null || echo unknown)"
  echo "kptr_restrict=$(sysctl -n kernel.kptr_restrict 2>/dev/null || echo unknown)"
  echo "nmi_watchdog=$(sysctl -n kernel.nmi_watchdog 2>/dev/null || echo unknown)"
  echo "governor=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo unknown)"
  echo "no_turbo=$(cat /sys/devices/system/cpu/intel_pstate/no_turbo 2>/dev/null || echo unknown)"
  echo "smt=$(cat /sys/devices/system/cpu/smt/control 2>/dev/null || echo unknown)"
} > "$snapshot"

echo "Captured current state to: $snapshot"
echo

# --- Dry-run ------------------------------------------------------------
if [[ "$mode" == "dry" ]]; then
  echo "Dry-run: no changes applied. Snapshot remains at $snapshot"
  exit 0
fi

# --- Prompt -------------------------------------------------------------
read -r -p "Type APPLY to apply these changes, anything else to cancel: " answer
if [[ "$answer" != "APPLY" ]]; then
  echo "Cancelled. No changes made."
  exit 0
fi

sudo sysctl -w kernel.perf_event_paranoid=-1
sudo sysctl -w kernel.kptr_restrict=0
sudo sysctl -w kernel.nmi_watchdog=0
sudo cpupower frequency-set -g performance || echo "WARN: cpupower not installed"
echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo >/dev/null 2>&1 || true

echo
echo "Applied. Revert any time with: $0 --revert"
echo "Snapshot: $snapshot"
