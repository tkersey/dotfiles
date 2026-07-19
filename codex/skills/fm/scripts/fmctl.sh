#!/bin/bash
# A local, non-Swift wrapper for Apple's macOS `fm` CLI.
# Bash 3.2 compatible for the system Bash shipped with macOS.

set -euo pipefail

FM_EXECUTABLE="${FM_EXECUTABLE:-/usr/bin/fm}"

usage() {
  cat <<'USAGE'
Usage:
  fmctl.sh check
  fmctl.sh respond [options]
  fmctl.sh schema <fm schema arguments...>
  fmctl.sh raw <noninteractive fm arguments...>

Respond options:
  --model system|pcc            Model to use. Default: system
  --prompt TEXT                 Prompt text
  --prompt-file PATH            Read prompt text from a file
  --stdin                       Read prompt text from standard input
  --instructions TEXT           Model instructions
  --instructions-file PATH      Read instructions from a file
  --image PATH                  Add an image; may be repeated
  --schema PATH                 Guided-generation schema
  --transcript PATH             Existing transcript for --load-transcript
  --greedy                      Request greedy sampling
  -h, --help                    Show this help

Environment variables:
  FM_EXECUTABLE=/path/to/fm     Override /usr/bin/fm
  FM_SKIP_PTY=1                 Invoke fm directly instead of through script(1)
  FM_ALLOW_NON_DARWIN=1         Permit non-macOS execution (intended for tests)
  FM_PRESERVE_TERMINAL=1        Preserve ANSI escapes and carriage returns
USAGE
}

fail() {
  printf 'fmctl: %s\n' "$*" >&2
  exit 64
}

require_value() {
  if [ "$#" -lt 2 ] || [ -z "${2:-}" ]; then
    fail "missing value for $1"
  fi
}

require_readable_file() {
  if [ ! -f "$1" ] || [ ! -r "$1" ]; then
    fail "file is not readable: $1"
  fi
}

preflight() {
  local os_name
  os_name="$(uname -s)"

  if [ "$os_name" != "Darwin" ] && [ "${FM_ALLOW_NON_DARWIN:-0}" != "1" ]; then
    printf 'fmctl: this skill must run locally on macOS; current OS is %s\n' "$os_name" >&2
    exit 69
  fi

  if [ ! -x "$FM_EXECUTABLE" ]; then
    printf 'fmctl: no executable fm tool found at %s\n' "$FM_EXECUTABLE" >&2
    exit 69
  fi

  if [ "${FM_SKIP_PTY:-0}" != "1" ]; then
    if [ ! -x /usr/bin/script ]; then
      printf 'fmctl: /usr/bin/script is required for pseudo-terminal execution\n' >&2
      exit 69
    fi
    if [ ! -x /bin/sh ]; then
      printf 'fmctl: /bin/sh is required for pseudo-terminal execution\n' >&2
      exit 69
    fi
  fi
}

# Run fm in a pseudo-terminal with a nonzero terminal size. The fixed shell code
# receives every fm argument through "$@"; no prompt or path is interpolated into it.
run_fm() (
  preflight

  if [ "${FM_SKIP_PTY:-0}" = "1" ]; then
    exec "$FM_EXECUTABLE" "$@"
  fi

  local temp_dir fifo output_file status
  temp_dir="$(mktemp -d "${TMPDIR:-/tmp}/fm-skill.XXXXXX")"
  fifo="$temp_dir/stdin"
  output_file="$temp_dir/output"

  cleanup() {
    exec 3>&- 2>/dev/null || true
    rm -rf "$temp_dir"
  }
  trap cleanup EXIT HUP INT TERM

  mkfifo "$fifo"

  # Opening the FIFO read/write keeps script(1)'s stdin open until the child exits,
  # avoiding an EOF marker in the terminal capture while requiring no producer.
  exec 3<>"$fifo"
  rm -f "$fifo"

  set +e
  /usr/bin/script -q /dev/null \
    /bin/sh -c 'stty rows 24 cols 80; exec "$@"' \
    fm-skill "$FM_EXECUTABLE" "$@" \
    <&3 >"$output_file" 2>&1
  status=$?
  set -e

  if [ "${FM_PRESERVE_TERMINAL:-0}" = "1" ]; then
    cat "$output_file"
  else
    # Strip common ANSI control sequences and terminal CR characters while
    # preserving the generated text and line structure.
    LC_ALL=C sed $'s/\033\\[[0-?]*[ -\\/]*[@-~]//g; s/\r$//' "$output_file"
  fi

  exit "$status"
)

check_command() {
  preflight

  # Help is a low-risk way to verify that the executable starts successfully.
  if ! "$FM_EXECUTABLE" --help >/dev/null 2>&1; then
    printf 'fmctl: %s exists but did not successfully return help\n' "$FM_EXECUTABLE" >&2
    exit 70
  fi

  printf 'fmctl: ready\n'
  printf 'fmctl: executable=%s\n' "$FM_EXECUTABLE"
  printf 'fmctl: os=%s\n' "$(uname -s)"
  if [ "${FM_SKIP_PTY:-0}" = "1" ]; then
    printf 'fmctl: pty=disabled\n'
  else
    printf 'fmctl: pty=/usr/bin/script (24x80)\n'
  fi
}

respond_command() {
  local model instructions schema transcript prompt prompt_source_count greedy
  local -a images args

  model="system"
  instructions=""
  schema=""
  transcript=""
  prompt=""
  prompt_source_count=0
  greedy=0
  images=()

  while [ "$#" -gt 0 ]; do
    case "$1" in
      --model)
        require_value "$@"
        model="$2"
        shift 2
        ;;
      --prompt)
        require_value "$@"
        prompt="$2"
        prompt_source_count=$((prompt_source_count + 1))
        shift 2
        ;;
      --prompt-file)
        require_value "$@"
        require_readable_file "$2"
        prompt="$(cat "$2")"
        prompt_source_count=$((prompt_source_count + 1))
        shift 2
        ;;
      --stdin)
        prompt="$(cat)"
        prompt_source_count=$((prompt_source_count + 1))
        shift
        ;;
      --instructions)
        require_value "$@"
        instructions="$2"
        shift 2
        ;;
      --instructions-file)
        require_value "$@"
        require_readable_file "$2"
        instructions="$(cat "$2")"
        shift 2
        ;;
      --image)
        require_value "$@"
        require_readable_file "$2"
        images+=("$2")
        shift 2
        ;;
      --schema)
        require_value "$@"
        require_readable_file "$2"
        schema="$2"
        shift 2
        ;;
      --transcript)
        require_value "$@"
        require_readable_file "$2"
        transcript="$2"
        shift 2
        ;;
      --greedy)
        greedy=1
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      --)
        shift
        if [ "$#" -eq 0 ]; then
          fail "missing prompt after --"
        fi
        if [ "$prompt_source_count" -ne 0 ]; then
          fail "provide exactly one prompt source"
        fi
        prompt="$*"
        prompt_source_count=1
        shift "$#"
        ;;
      *)
        fail "unknown respond option: $1"
        ;;
    esac
  done

  case "$model" in
    system|pcc) ;;
    *) fail "model must be 'system' or 'pcc'" ;;
  esac

  if [ "$prompt_source_count" -ne 1 ]; then
    fail "provide exactly one of --prompt, --prompt-file, --stdin, or -- <prompt>"
  fi

  if [ -z "$prompt" ]; then
    fail "prompt is empty"
  fi

  # --text=<value> preserves option-shaped prompts as data. --no-stream keeps
  # output stable even though fm sees a TTY through script(1).
  args=(respond --model "$model" --no-stream)

  if [ -n "$instructions" ]; then
    args+=(--instructions "$instructions")
  fi

  local image
  if [ "${images+present}" = "present" ]; then
    for image in "${images[@]}"; do
      args+=(--image "$image")
    done
  fi

  if [ -n "$schema" ]; then
    args+=(--schema "$schema")
  fi

  if [ -n "$transcript" ]; then
    args+=(--load-transcript "$transcript")
  fi

  if [ "$greedy" -eq 1 ]; then
    args+=(--greedy)
  fi

  args+=("--text=$prompt")
  run_fm "${args[@]}"
}

main() {
  if [ "$#" -lt 1 ]; then
    usage >&2
    exit 64
  fi

  local command_name="$1"
  shift

  case "$command_name" in
    check)
      if [ "$#" -ne 0 ]; then
        fail "check takes no arguments"
      fi
      check_command
      ;;
    respond)
      respond_command "$@"
      ;;
    schema)
      if [ "$#" -eq 0 ]; then
        fail "schema requires fm schema arguments"
      fi
      run_fm schema "$@"
      ;;
    raw)
      if [ "$#" -eq 0 ]; then
        fail "raw requires fm arguments"
      fi
      if [ "$1" = "chat" ]; then
        fail "interactive fm chat is not supported by this noninteractive wrapper"
      fi
      run_fm "$@"
      ;;
    -h|--help|help)
      usage
      ;;
    *)
      fail "unknown command: $command_name"
      ;;
  esac
}

main "$@"
