#!/bin/sh
set -eu

LABEL="${CRON_LAUNCHD_LABEL:-com.openai.codex.automation-runner}"
INTERVAL_SECONDS="${CRON_LAUNCHD_INTERVAL_SECONDS:-60}"
PATH_VALUE="${CRON_LAUNCHD_PATH:-${PATH:-/usr/bin:/bin:/usr/sbin:/sbin}}"

usage() {
  echo "Usage: $0 [--label <label>] [--interval-seconds <n>] [--path <path>]"
  echo "Defaults:"
  echo "  label=$LABEL"
  echo "  interval-seconds=$INTERVAL_SECONDS"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --label)
      if [ "$#" -lt 2 ]; then
        echo "error: --label requires a value" >&2
        exit 1
      fi
      LABEL="$2"
      shift 2
      ;;
    --interval-seconds)
      if [ "$#" -lt 2 ]; then
        echo "error: --interval-seconds requires a value" >&2
        exit 1
      fi
      INTERVAL_SECONDS="$2"
      shift 2
      ;;
    --path)
      if [ "$#" -lt 2 ]; then
        echo "error: --path requires a value" >&2
        exit 1
      fi
      PATH_VALUE="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

case "$INTERVAL_SECONDS" in
  ''|*[!0-9]*)
    echo "error: --interval-seconds must be a positive integer" >&2
    exit 1
    ;;
esac
if [ "$INTERVAL_SECONDS" -lt 1 ]; then
  echo "error: --interval-seconds must be >= 1" >&2
  exit 1
fi

PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG_DIR="$HOME/Library/Logs/codex-automation-runner"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WRAPPER="$SCRIPT_DIR/launchd_wrapper.sh"
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
    <string>/bin/sh</string>
    <string>$WRAPPER</string>
  </array>
  <key>WorkingDirectory</key>
  <string>$HOME</string>
  <key>RunAtLoad</key>
  <true/>
  <key>StartInterval</key>
  <integer>$INTERVAL_SECONDS</integer>
  <key>KeepAlive</key>
  <dict>
    <key>Crashed</key>
    <true/>
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
