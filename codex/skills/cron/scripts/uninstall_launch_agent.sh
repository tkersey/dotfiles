#!/bin/sh
set -eu

LABEL="${CRON_LAUNCHD_LABEL:-com.openai.codex.automation-runner}"

usage() {
  echo "Usage: $0 [--label <label>]"
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

PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
UID_VALUE="$(id -u)"

launchctl disable "gui/$UID_VALUE/$LABEL" 2>/dev/null || true
launchctl bootout "gui/$UID_VALUE/$LABEL" 2>/dev/null || true
if [ -f "$PLIST" ]; then
  rm -f "$PLIST"
  echo "stopped and removed: $LABEL"
else
  echo "already absent: $LABEL"
fi
