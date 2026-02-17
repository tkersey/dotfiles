#!/bin/sh
set -eu

LABEL="${MESH_LAUNCHD_LABEL:-com.openai.codex.mesh-autopilot}"
PATH_VALUE="${MESH_LAUNCHD_PATH:-/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin:/usr/sbin:/sbin}}"
UV_CACHE_DIR_VALUE="${MESH_LAUNCHD_UV_CACHE_DIR:-/tmp/uv-cache}"

TARGET_CWD="$(pwd)"
PLAN_FILE_REL=".step/st-plan.jsonl"
POLL_MS="60000"
TURN_TIMEOUT_MS="2700000"
BUDGET_MODE="aware"

usage() {
  echo "Usage: $0 [--label <label>] [--path <path>] [--uv-cache-dir <path>] --cwd <dir> [--plan-file <relpath>] [--poll-ms <n>] [--turn-timeout-ms <n>] [--budget-mode <aware|all_out>]"
  echo "Defaults:"
  echo "  label=$LABEL"
  echo "  plan-file=$PLAN_FILE_REL"
  echo "  poll-ms=$POLL_MS"
  echo "  turn-timeout-ms=$TURN_TIMEOUT_MS"
  echo "  budget-mode=$BUDGET_MODE"
  echo "  uv-cache-dir=$UV_CACHE_DIR_VALUE"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --label)
      LABEL="$2"; shift 2 ;;
    --path)
      PATH_VALUE="$2"; shift 2 ;;
    --uv-cache-dir)
      UV_CACHE_DIR_VALUE="$2"; shift 2 ;;
    --cwd)
      TARGET_CWD="$2"; shift 2 ;;
    --plan-file)
      PLAN_FILE_REL="$2"; shift 2 ;;
    --poll-ms)
      POLL_MS="$2"; shift 2 ;;
    --turn-timeout-ms)
      TURN_TIMEOUT_MS="$2"; shift 2 ;;
    --budget-mode)
      BUDGET_MODE="$2"; shift 2 ;;
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

case "$POLL_MS" in
  ''|*[!0-9]*)
    echo "error: --poll-ms must be a non-negative integer" >&2
    exit 1
    ;;
esac

case "$TURN_TIMEOUT_MS" in
  ''|*[!0-9]*)
    echo "error: --turn-timeout-ms must be a positive integer" >&2
    exit 1
    ;;
esac

case "$BUDGET_MODE" in
  aware|all_out)
    ;;
  *)
    echo "error: --budget-mode must be one of: aware, all_out" >&2
    exit 1
    ;;
esac

NODE_BIN="$(command -v node || true)"
if [ -z "$NODE_BIN" ]; then
  echo "error: node not found on PATH" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$SCRIPT_DIR/mesh_cas_autopilot.mjs"
if [ ! -x "$SCRIPT" ]; then
  echo "error: autopilot script is not executable: $SCRIPT" >&2
  exit 1
fi

PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG_DIR="$HOME/Library/Logs/mesh-cas-autopilot"
UID_VALUE="$(id -u)"
TMP_PLIST="$(mktemp)"

mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR"
mkdir -p "$UV_CACHE_DIR_VALUE"

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
    <string>--poll-ms</string>
    <string>$POLL_MS</string>
    <string>--turn-timeout-ms</string>
    <string>$TURN_TIMEOUT_MS</string>
    <string>--budget-mode</string>
    <string>$BUDGET_MODE</string>
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
    <key>UV_CACHE_DIR</key>
    <string>$UV_CACHE_DIR_VALUE</string>
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
