#!/bin/sh
set -eu

LABEL="${MESH_FLEET_LAUNCHD_LABEL:-com.openai.codex.mesh-fleet-autopilot}"
PATH_VALUE="${MESH_FLEET_LAUNCHD_PATH:-/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin:/usr/sbin:/sbin}}"

TARGET_CWD="$(pwd)"
PLAN_FILE_REL=".step/st-plan.jsonl"
WORKERS="3"
POLL_MS="60000"
WORKER_TURN_TIMEOUT_MS="1800000"
INTEGRATOR_TURN_TIMEOUT_MS="2700000"

usage() {
  echo "Usage: $0 [--label <label>] [--path <path>] --cwd <dir> [--plan-file <relpath>] [--workers <n>] [--poll-ms <n>] [--worker-turn-timeout-ms <n>] [--integrator-turn-timeout-ms <n>]"
  echo "Defaults:"
  echo "  label=$LABEL"
  echo "  plan-file=$PLAN_FILE_REL"
  echo "  workers=$WORKERS"
  echo "  poll-ms=$POLL_MS"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --label)
      LABEL="$2"; shift 2 ;;
    --path)
      PATH_VALUE="$2"; shift 2 ;;
    --cwd)
      TARGET_CWD="$2"; shift 2 ;;
    --plan-file)
      PLAN_FILE_REL="$2"; shift 2 ;;
    --workers)
      WORKERS="$2"; shift 2 ;;
    --poll-ms)
      POLL_MS="$2"; shift 2 ;;
    --worker-turn-timeout-ms)
      WORKER_TURN_TIMEOUT_MS="$2"; shift 2 ;;
    --integrator-turn-timeout-ms)
      INTEGRATOR_TURN_TIMEOUT_MS="$2"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 1 ;;
  esac
done

if [ ! -d "$TARGET_CWD" ]; then
  echo "error: --cwd does not exist or is not a directory: $TARGET_CWD" >&2
  exit 1
fi

case "$WORKERS" in
  ''|*[!0-9]*)
    echo "error: --workers must be an integer >= 0" >&2
    exit 1
    ;;
esac

case "$POLL_MS" in
  ''|*[!0-9]*)
    echo "error: --poll-ms must be a non-negative integer" >&2
    exit 1
    ;;
esac

case "$WORKER_TURN_TIMEOUT_MS" in
  ''|*[!0-9]*)
    echo "error: --worker-turn-timeout-ms must be a positive integer" >&2
    exit 1
    ;;
esac

case "$INTEGRATOR_TURN_TIMEOUT_MS" in
  ''|*[!0-9]*)
    echo "error: --integrator-turn-timeout-ms must be a positive integer" >&2
    exit 1
    ;;
esac

NODE_BIN="$(command -v node || true)"
if [ -z "$NODE_BIN" ]; then
  echo "error: node not found on PATH" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$SCRIPT_DIR/mesh_casp_fleet_autopilot.mjs"
if [ ! -x "$SCRIPT" ]; then
  echo "error: autopilot script is not executable: $SCRIPT" >&2
  exit 1
fi

PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG_DIR="$HOME/Library/Logs/mesh-casp-fleet-autopilot"
UID_VALUE="$(id -u)"
TMP_PLIST="$(mktemp)"

mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR"

cat > "$TMP_PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$NODE_BIN</string>
    <string>$SCRIPT</string>
    <string>--cwd</string>
    <string>$TARGET_CWD</string>
    <string>--plan-file</string>
    <string>$PLAN_FILE_REL</string>
    <string>--workers</string>
    <string>$WORKERS</string>
    <string>--poll-ms</string>
    <string>$POLL_MS</string>
    <string>--worker-turn-timeout-ms</string>
    <string>$WORKER_TURN_TIMEOUT_MS</string>
    <string>--integrator-turn-timeout-ms</string>
    <string>$INTEGRATOR_TURN_TIMEOUT_MS</string>
  </array>
  <key>WorkingDirectory</key>
  <string>$HOME</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <dict>
    <key>SuccessfulExit</key>
    <false/>
  </dict>
  <key>ProcessType</key>
  <string>Background</string>
  <key>ThrottleInterval</key>
  <integer>30</integer>
  <key>StandardOutPath</key>
  <string>$LOG_DIR/out.log</string>
  <key>StandardErrorPath</key>
  <string>$LOG_DIR/err.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>$PATH_VALUE</string>
  </dict>
</dict>
</plist>
EOF

CHANGED=1
if [ -f "$PLIST" ] && cmp -s "$TMP_PLIST" "$PLIST"; then
  CHANGED=0
  rm -f "$TMP_PLIST"
else
  mv "$TMP_PLIST" "$PLIST"
  chmod 0644 "$PLIST"
fi

plutil -lint "$PLIST"

if [ "$CHANGED" -eq 0 ] && launchctl print "gui/$UID_VALUE/$LABEL" >/dev/null 2>&1; then
  echo "already installed and loaded: $LABEL"
  echo "plist: $PLIST"
  echo "logs: $LOG_DIR"
  exit 0
fi

launchctl bootout "gui/$UID_VALUE/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$UID_VALUE" "$PLIST"
launchctl enable "gui/$UID_VALUE/$LABEL" 2>/dev/null || true
launchctl kickstart -k "gui/$UID_VALUE/$LABEL"
launchctl print "gui/$UID_VALUE/$LABEL" >/dev/null

echo "installed and started: $LABEL"
echo "plist: $PLIST"
echo "logs: $LOG_DIR"
