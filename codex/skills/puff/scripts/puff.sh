#!/usr/bin/env bash
set -euo pipefail

PUFF_HOME="${PUFF_HOME:-$HOME/.codex/puff}"
JOBS_DIR="$PUFF_HOME/jobs"
LOGS_DIR="$PUFF_HOME/logs"
RESULTS_DIR="$PUFF_HOME/results"
PROMPTS_DIR="$PUFF_HOME/prompts"
CAS_DIR="$PUFF_HOME/cas"
CAS_PID_FILE="$CAS_DIR/proxy.pid"
CAS_META_FILE="$CAS_DIR/proxy.env"

mkdir -p "$JOBS_DIR" "$LOGS_DIR" "$RESULTS_DIR" "$PROMPTS_DIR" "$CAS_DIR"

err() {
  printf 'puff: %s\n' "$*" >&2
}

die() {
  err "$*"
  exit 1
}

now_utc() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    die "required command not found: $cmd"
  fi
}

parse_task_id() {
  local raw="$1"
  local no_fragment no_query no_trailing id
  no_fragment="${raw%%#*}"
  no_query="${no_fragment%%\?*}"
  no_trailing="${no_query%/}"
  id="${no_trailing##*/}"
  if [[ -z "$id" ]]; then
    return 1
  fi
  printf '%s\n' "$id"
}

field_from_text() {
  local text="$1"
  local key="$2"
  printf '%s\n' "$text" | sed -n "s/^${key}=//p" | head -n1
}

field_from_file() {
  local file="$1"
  local key="$2"
  sed -n "s/^${key}=//p" "$file" | head -n1
}

validate_attempts() {
  local attempts="$1"
  if ! [[ "$attempts" =~ ^[0-9]+$ ]]; then
    die "attempts must be an integer (1-4)"
  fi
  if (( attempts < 1 || attempts > 4 )); then
    die "attempts must be between 1 and 4"
  fi
}

validate_interval() {
  local interval="$1"
  if ! [[ "$interval" =~ ^[0-9]+$ ]]; then
    die "interval must be an integer in seconds"
  fi
  if (( interval < 1 )); then
    die "interval must be at least 1 second"
  fi
}

validate_timeout() {
  local timeout="$1"
  if ! [[ "$timeout" =~ ^[0-9]+$ ]]; then
    die "timeout must be an integer in seconds"
  fi
}

validate_timeout_ms() {
  local timeout_ms="$1"
  if ! [[ "$timeout_ms" =~ ^[0-9]+$ ]]; then
    die "server-request timeout must be an integer in milliseconds"
  fi
}

run_doctor_checks() {
  local env_id="${1:-}"
  local quiet="${2:-0}"

  require_cmd codex

  local cmd=(codex cloud list --limit 1 --json)
  if [[ -n "$env_id" ]]; then
    cmd+=(--env "$env_id")
  fi

  local output=""
  if ! output="$("${cmd[@]}" 2>&1)"; then
    if [[ "$quiet" != "1" ]]; then
      printf 'DOCTOR_STATUS=FAIL\n'
      printf 'CHECK=codex_cloud_access RESULT=fail\n'
    fi
    printf '%s\n' "$output" >&2
    return 1
  fi

  if [[ "$quiet" != "1" ]]; then
    printf 'DOCTOR_STATUS=OK\n'
    printf 'CHECK=codex_command RESULT=ok\n'
    printf 'CHECK=cloud_access RESULT=ok\n'
    if [[ -n "$env_id" ]]; then
      printf 'CHECK=environment RESULT=ok VALUE=%s\n' "$env_id"
    fi
  fi

  return 0
}

read_prompt() {
  local prompt="$1"
  if [[ -n "$prompt" ]]; then
    printf '%s' "$prompt"
    return
  fi
  if [[ -t 0 ]]; then
    die "prompt is required; pass --prompt or pipe via stdin"
  fi
  cat
}

submit_task() {
  local env_id="$1"
  local prompt="$2"
  local attempts="$3"
  local branch="$4"

  require_cmd codex

  local cmd=(codex cloud exec --env "$env_id" --attempts "$attempts")
  if [[ -n "$branch" ]]; then
    cmd+=(--branch "$branch")
  fi
  cmd+=("$prompt")

  local output=""
  if ! output="$("${cmd[@]}" 2>&1)"; then
    printf '%s\n' "$output" >&2
    return 1
  fi

  local task_url=""
  task_url="$(printf '%s\n' "$output" | awk 'NF { line=$0 } END { print line }')"
  if [[ -z "$task_url" ]]; then
    printf '%s\n' "$output" >&2
    die "failed to parse task url from codex cloud exec output"
  fi

  local task_id=""
  if ! task_id="$(parse_task_id "$task_url")"; then
    printf '%s\n' "$output" >&2
    die "failed to parse task id from url: $task_url"
  fi

  printf 'TASK_ID=%s\n' "$task_id"
  printf 'TASK_URL=%s\n' "$task_url"
}

write_result_file() {
  local result_file="$1"
  local task_id="$2"
  local task_url="$3"
  local terminal_state="$4"
  local exit_code="$5"

  mkdir -p "$(dirname "$result_file")"
  cat >"$result_file" <<RESULT
TASK_ID=$task_id
TASK_URL=$task_url
FINAL_STATE=$terminal_state
EXIT_CODE=$exit_code
ENDED_AT=$(now_utc)
RESULT
}

cmd_submit() {
  local env_id=""
  local prompt=""
  local attempts="1"
  local branch=""

  while (( $# > 0 )); do
    case "$1" in
      --env)
        [[ $# -ge 2 ]] || die "--env requires a value"
        env_id="$2"
        shift 2
        ;;
      --prompt)
        [[ $# -ge 2 ]] || die "--prompt requires a value"
        prompt="$2"
        shift 2
        ;;
      --attempts)
        [[ $# -ge 2 ]] || die "--attempts requires a value"
        attempts="$2"
        shift 2
        ;;
      --branch)
        [[ $# -ge 2 ]] || die "--branch requires a value"
        branch="$2"
        shift 2
        ;;
      -h|--help)
        usage_submit
        return 0
        ;;
      *)
        die "unknown submit option: $1"
        ;;
    esac
  done

  [[ -n "$env_id" ]] || die "--env is required"
  validate_attempts "$attempts"
  prompt="$(read_prompt "$prompt")"
  if [[ -z "${prompt//[[:space:]]/}" ]]; then
    die "prompt must not be empty"
  fi

  submit_task "$env_id" "$prompt" "$attempts" "$branch"
}

cmd_doctor() {
  local env_id=""
  local quiet="0"

  while (( $# > 0 )); do
    case "$1" in
      --env)
        [[ $# -ge 2 ]] || die "--env requires a value"
        env_id="$2"
        shift 2
        ;;
      --quiet)
        quiet="1"
        shift
        ;;
      -h|--help)
        usage_doctor
        return 0
        ;;
      *)
        die "unknown doctor option: $1"
        ;;
    esac
  done

  run_doctor_checks "$env_id" "$quiet"
}

cmd_watch() {
  local task_ref=""
  local task_url=""
  local interval="15"
  local timeout="0"
  local result_file=""

  while (( $# > 0 )); do
    case "$1" in
      --task)
        [[ $# -ge 2 ]] || die "--task requires a value"
        task_ref="$2"
        shift 2
        ;;
      --task-url)
        [[ $# -ge 2 ]] || die "--task-url requires a value"
        task_url="$2"
        shift 2
        ;;
      --interval)
        [[ $# -ge 2 ]] || die "--interval requires a value"
        interval="$2"
        shift 2
        ;;
      --timeout)
        [[ $# -ge 2 ]] || die "--timeout requires a value"
        timeout="$2"
        shift 2
        ;;
      --result-file)
        [[ $# -ge 2 ]] || die "--result-file requires a value"
        result_file="$2"
        shift 2
        ;;
      -h|--help)
        usage_watch
        return 0
        ;;
      *)
        die "unknown watch option: $1"
        ;;
    esac
  done

  [[ -n "$task_ref" ]] || die "--task is required"
  validate_interval "$interval"
  validate_timeout "$timeout"

  local task_id=""
  if ! task_id="$(parse_task_id "$task_ref")"; then
    die "invalid task reference: $task_ref"
  fi
  if [[ -z "$task_url" ]]; then
    task_url="$task_ref"
  fi

  require_cmd codex

  local start_epoch=""
  start_epoch="$(date +%s)"

  printf '[%s] watch_start task=%s interval=%ss timeout=%ss\n' "$(now_utc)" "$task_id" "$interval" "$timeout"

  local terminal_state=""
  local exit_code="0"

  while true; do
    local status_output=""
    local rc="0"
    if status_output="$(codex cloud status "$task_id" 2>&1)"; then
      rc=0
    else
      rc=$?
    fi

    local status=""
    status="$(printf '%s\n' "$status_output" | sed -n 's/^\[\([A-Z][A-Z]*\)\].*/\1/p' | head -n1)"
    if [[ -z "$status" ]]; then
      status="UNKNOWN"
    fi

    local headline=""
    headline="$(printf '%s\n' "$status_output" | awk 'NF { print; exit }')"
    if [[ -z "$headline" ]]; then
      headline="(no status output)"
    fi

    printf '[%s] status=%s rc=%s %s\n' "$(now_utc)" "$status" "$rc" "$headline"

    case "$status" in
      READY|APPLIED)
        terminal_state="success"
        exit_code=0
        break
        ;;
      ERROR)
        terminal_state="error"
        exit_code=2
        break
        ;;
      *)
        ;;
    esac

    if (( timeout > 0 )); then
      local now_epoch=""
      now_epoch="$(date +%s)"
      local elapsed=""
      elapsed=$((now_epoch - start_epoch))
      if (( elapsed >= timeout )); then
        terminal_state="timeout"
        exit_code=124
        break
      fi
    fi

    sleep "$interval"
  done

  printf '[%s] watch_end task=%s final=%s exit=%s\n' "$(now_utc)" "$task_id" "$terminal_state" "$exit_code"

  if [[ -n "$result_file" ]]; then
    write_result_file "$result_file" "$task_id" "$task_url" "$terminal_state" "$exit_code"
  fi

  return "$exit_code"
}

cmd_launch() {
  local env_id=""
  local prompt=""
  local attempts="1"
  local branch=""
  local interval="15"
  local timeout="0"
  local run_doctor="1"

  while (( $# > 0 )); do
    case "$1" in
      --env)
        [[ $# -ge 2 ]] || die "--env requires a value"
        env_id="$2"
        shift 2
        ;;
      --prompt)
        [[ $# -ge 2 ]] || die "--prompt requires a value"
        prompt="$2"
        shift 2
        ;;
      --attempts)
        [[ $# -ge 2 ]] || die "--attempts requires a value"
        attempts="$2"
        shift 2
        ;;
      --branch)
        [[ $# -ge 2 ]] || die "--branch requires a value"
        branch="$2"
        shift 2
        ;;
      --interval)
        [[ $# -ge 2 ]] || die "--interval requires a value"
        interval="$2"
        shift 2
        ;;
      --timeout)
        [[ $# -ge 2 ]] || die "--timeout requires a value"
        timeout="$2"
        shift 2
        ;;
      --skip-doctor)
        run_doctor="0"
        shift
        ;;
      -h|--help)
        usage_launch
        return 0
        ;;
      *)
        die "unknown launch option: $1"
        ;;
    esac
  done

  [[ -n "$env_id" ]] || die "--env is required"
  validate_attempts "$attempts"
  validate_interval "$interval"
  validate_timeout "$timeout"

  if [[ "$run_doctor" == "1" ]]; then
    run_doctor_checks "$env_id" "0"
  fi

  prompt="$(read_prompt "$prompt")"
  if [[ -z "${prompt//[[:space:]]/}" ]]; then
    die "prompt must not be empty"
  fi

  local submit_output=""
  submit_output="$(submit_task "$env_id" "$prompt" "$attempts" "$branch")"

  local task_id=""
  local task_url=""
  task_id="$(field_from_text "$submit_output" TASK_ID)"
  task_url="$(field_from_text "$submit_output" TASK_URL)"

  if [[ -z "$task_id" || -z "$task_url" ]]; then
    die "failed to parse submit output"
  fi

  local job_id=""
  job_id="$(date -u +%Y%m%dT%H%M%SZ)-$RANDOM"
  local job_file="$JOBS_DIR/$job_id.env"
  local log_file="$LOGS_DIR/$job_id.log"
  local result_file="$RESULTS_DIR/$job_id.result"
  local prompt_file="$PROMPTS_DIR/$job_id.prompt"

  printf '%s' "$prompt" >"$prompt_file"

  local self_script=""
  self_script="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/$(basename -- "${BASH_SOURCE[0]}")"

  nohup "$self_script" watch \
    --task "$task_id" \
    --task-url "$task_url" \
    --interval "$interval" \
    --timeout "$timeout" \
    --result-file "$result_file" \
    >"$log_file" 2>&1 < /dev/null &
  local pid="$!"

  cat >"$job_file" <<JOB
JOB_ID=$job_id
PID=$pid
TASK_ID=$task_id
TASK_URL=$task_url
LOG_PATH=$log_file
RESULT_PATH=$result_file
PROMPT_FILE=$prompt_file
ENV_ID=$env_id
ATTEMPTS=$attempts
BRANCH=$branch
WATCH_INTERVAL=$interval
WATCH_TIMEOUT=$timeout
STARTED_AT=$(now_utc)
JOB

  printf 'JOB_ID=%s\n' "$job_id"
  printf 'PID=%s\n' "$pid"
  printf 'TASK_ID=%s\n' "$task_id"
  printf 'TASK_URL=%s\n' "$task_url"
  printf 'LOG_PATH=%s\n' "$log_file"
  printf 'RESULT_PATH=%s\n' "$result_file"
}

cmd_jobs() {
  shopt -s nullglob
  local files=("$JOBS_DIR"/*.env)
  shopt -u nullglob

  if (( ${#files[@]} == 0 )); then
    printf 'No puff jobs found.\n'
    return 0
  fi

  local file
  for file in "${files[@]}"; do
    local job_id pid task_id task_url log_path result_path started_at
    job_id="$(field_from_file "$file" JOB_ID)"
    pid="$(field_from_file "$file" PID)"
    task_id="$(field_from_file "$file" TASK_ID)"
    task_url="$(field_from_file "$file" TASK_URL)"
    log_path="$(field_from_file "$file" LOG_PATH)"
    result_path="$(field_from_file "$file" RESULT_PATH)"
    started_at="$(field_from_file "$file" STARTED_AT)"

    local process_state="stopped"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      process_state="running"
    fi

    local final_state="in_progress"
    local ended_at=""
    if [[ -f "$result_path" ]]; then
      final_state="$(field_from_file "$result_path" FINAL_STATE)"
      ended_at="$(field_from_file "$result_path" ENDED_AT)"
    elif [[ "$process_state" != "running" ]]; then
      final_state="unknown"
    fi

    printf 'JOB_ID=%s TASK_ID=%s PROCESS=%s FINAL=%s PID=%s STARTED_AT=%s\n' \
      "$job_id" "$task_id" "$process_state" "$final_state" "$pid" "$started_at"
    if [[ -n "$ended_at" ]]; then
      printf 'ENDED_AT=%s\n' "$ended_at"
    fi
    printf 'TASK_URL=%s\n' "$task_url"
    printf 'LOG_PATH=%s\n' "$log_path"
    printf '\n'
  done
}

cmd_stop() {
  local job_id=""

  while (( $# > 0 )); do
    case "$1" in
      --job)
        [[ $# -ge 2 ]] || die "--job requires a value"
        job_id="$2"
        shift 2
        ;;
      -h|--help)
        usage_stop
        return 0
        ;;
      *)
        die "unknown stop option: $1"
        ;;
    esac
  done

  [[ -n "$job_id" ]] || die "--job is required"

  local job_file="$JOBS_DIR/$job_id.env"
  if [[ ! -f "$job_file" ]]; then
    die "job not found: $job_id"
  fi

  local pid=""
  local task_id=""
  local task_url=""
  local result_file=""
  pid="$(field_from_file "$job_file" PID)"
  task_id="$(field_from_file "$job_file" TASK_ID)"
  task_url="$(field_from_file "$job_file" TASK_URL)"
  result_file="$(field_from_file "$job_file" RESULT_PATH)"

  if [[ -z "$pid" ]]; then
    die "job has no PID: $job_id"
  fi

  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid" >/dev/null 2>&1 || true
    local i
    for i in {1..25}; do
      if ! kill -0 "$pid" 2>/dev/null; then
        break
      fi
      sleep 0.2
    done
    if kill -0 "$pid" 2>/dev/null; then
      kill -9 "$pid" >/dev/null 2>&1 || true
    fi
    printf 'Stopped job %s (pid=%s).\n' "$job_id" "$pid"
  else
    printf 'Job %s is not running (pid=%s).\n' "$job_id" "$pid"
  fi

  if [[ -n "$result_file" && ! -f "$result_file" ]]; then
    write_result_file "$result_file" "$task_id" "$task_url" "stopped" "130"
  fi
}

cmd_cas_start() {
  local proxy_script="${PUFF_CAS_PROXY_SCRIPT:-$HOME/.dotfiles/codex/skills/cas/scripts/cas_proxy.mjs}"
  local cwd=""
  local state_file=""
  local timeout_ms=""
  local log_file=""
  local -a opt_out_methods=()

  while (( $# > 0 )); do
    case "$1" in
      --proxy-script)
        [[ $# -ge 2 ]] || die "--proxy-script requires a value"
        proxy_script="$2"
        shift 2
        ;;
      --cwd)
        [[ $# -ge 2 ]] || die "--cwd requires a value"
        cwd="$2"
        shift 2
        ;;
      --state-file)
        [[ $# -ge 2 ]] || die "--state-file requires a value"
        state_file="$2"
        shift 2
        ;;
      --server-request-timeout-ms)
        [[ $# -ge 2 ]] || die "--server-request-timeout-ms requires a value"
        timeout_ms="$2"
        shift 2
        ;;
      --opt-out-notification-method)
        [[ $# -ge 2 ]] || die "--opt-out-notification-method requires a value"
        opt_out_methods+=("$2")
        shift 2
        ;;
      --log-file)
        [[ $# -ge 2 ]] || die "--log-file requires a value"
        log_file="$2"
        shift 2
        ;;
      -h|--help)
        usage_cas_start
        return 0
        ;;
      *)
        die "unknown cas-start option: $1"
        ;;
    esac
  done

  require_cmd node
  [[ -f "$proxy_script" ]] || die "cas proxy script not found: $proxy_script"
  if [[ -n "$timeout_ms" ]]; then
    validate_timeout_ms "$timeout_ms"
  fi

  local current_pid=""
  if [[ -f "$CAS_PID_FILE" ]]; then
    current_pid="$(cat "$CAS_PID_FILE" 2>/dev/null || true)"
  fi
  if [[ -z "$current_pid" && -f "$CAS_META_FILE" ]]; then
    current_pid="$(field_from_file "$CAS_META_FILE" PID)"
  fi

  if [[ -n "$current_pid" ]] && kill -0 "$current_pid" 2>/dev/null; then
    local existing_log=""
    if [[ -f "$CAS_META_FILE" ]]; then
      existing_log="$(field_from_file "$CAS_META_FILE" LOG_PATH)"
    fi
    printf 'CAS_STATUS=already_running\n'
    printf 'PID=%s\n' "$current_pid"
    if [[ -n "$existing_log" ]]; then
      printf 'LOG_PATH=%s\n' "$existing_log"
    fi
    return 0
  fi

  if [[ -z "$log_file" ]]; then
    log_file="$CAS_DIR/proxy-$(date -u +%Y%m%dT%H%M%SZ).log"
  fi

  local cmd=(node "$proxy_script")
  if [[ -n "$cwd" ]]; then
    cmd+=(--cwd "$cwd")
  fi
  if [[ -n "$state_file" ]]; then
    cmd+=(--state-file "$state_file")
  fi
  if [[ -n "$timeout_ms" ]]; then
    cmd+=(--server-request-timeout-ms "$timeout_ms")
  fi
  if (( ${#opt_out_methods[@]} > 0 )); then
    local method
    for method in "${opt_out_methods[@]}"; do
      cmd+=(--opt-out-notification-method "$method")
    done
  fi

  nohup "${cmd[@]}" >"$log_file" 2>&1 < /dev/null &
  local pid="$!"
  sleep 0.2

  if ! kill -0 "$pid" 2>/dev/null; then
    printf 'CAS_STATUS=failed_to_start\n'
    printf 'LOG_PATH=%s\n' "$log_file"
    return 1
  fi

  printf '%s\n' "$pid" >"$CAS_PID_FILE"
  cat >"$CAS_META_FILE" <<META
PID=$pid
LOG_PATH=$log_file
PROXY_SCRIPT=$proxy_script
CWD=$cwd
STATE_FILE=$state_file
SERVER_REQUEST_TIMEOUT_MS=$timeout_ms
STARTED_AT=$(now_utc)
META

  printf 'CAS_STATUS=started\n'
  printf 'PID=%s\n' "$pid"
  printf 'LOG_PATH=%s\n' "$log_file"
}

cmd_cas_stop() {
  local force="0"

  while (( $# > 0 )); do
    case "$1" in
      --force)
        force="1"
        shift
        ;;
      -h|--help)
        usage_cas_stop
        return 0
        ;;
      *)
        die "unknown cas-stop option: $1"
        ;;
    esac
  done

  local pid=""
  if [[ -f "$CAS_PID_FILE" ]]; then
    pid="$(cat "$CAS_PID_FILE" 2>/dev/null || true)"
  fi
  if [[ -z "$pid" && -f "$CAS_META_FILE" ]]; then
    pid="$(field_from_file "$CAS_META_FILE" PID)"
  fi

  if [[ -z "$pid" ]]; then
    printf 'CAS_STATUS=not_running\n'
    return 0
  fi

  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid" >/dev/null 2>&1 || true
    local i
    for i in {1..25}; do
      if ! kill -0 "$pid" 2>/dev/null; then
        break
      fi
      sleep 0.2
    done
    if [[ "$force" == "1" ]] && kill -0 "$pid" 2>/dev/null; then
      kill -9 "$pid" >/dev/null 2>&1 || true
    fi
  fi

  if kill -0 "$pid" 2>/dev/null; then
    printf 'CAS_STATUS=still_running\n'
    printf 'PID=%s\n' "$pid"
    return 1
  fi

  rm -f "$CAS_PID_FILE"
  printf 'CAS_STATUS=stopped\n'
  printf 'PID=%s\n' "$pid"
}

usage_submit() {
  cat <<USAGE
Usage: puff.sh submit --env <env-id-or-label> [--prompt <text>] [--attempts <1-4>] [--branch <branch>]

Submit a Codex Cloud task and print TASK_ID/TASK_URL.
When --prompt is omitted, the prompt is read from stdin.
USAGE
}

usage_doctor() {
  cat <<USAGE
Usage: puff.sh doctor [--env <env-id-or-label>] [--quiet]

Run readiness checks for codex cloud access.
When --env is provided, validates that the environment selector resolves.
USAGE
}

usage_watch() {
  cat <<USAGE
Usage: puff.sh watch --task <task-id-or-url> [--interval <seconds>] [--timeout <seconds>] [--result-file <path>]

Poll codex cloud status until terminal state.
Successful terminal states: READY, APPLIED.
Failure terminal state: ERROR.
Timeout 0 means no timeout.
USAGE
}

usage_launch() {
  cat <<USAGE
Usage: puff.sh launch --env <env-id-or-label> [--prompt <text>] [--attempts <1-4>] [--branch <branch>] [--interval <seconds>] [--timeout <seconds>] [--skip-doctor]

Submit a Codex Cloud task and start a detached watcher.
Prints JOB_ID, PID, TASK_ID, TASK_URL, LOG_PATH, RESULT_PATH.
USAGE
}

usage_jobs() {
  cat <<USAGE
Usage: puff.sh jobs

List detached watcher jobs.
USAGE
}

usage_stop() {
  cat <<USAGE
Usage: puff.sh stop --job <job-id>

Stop a detached watcher job started by launch.
USAGE
}

usage_cas_start() {
  cat <<USAGE
Usage: puff.sh cas-start [--cwd <path>] [--state-file <path>] [--server-request-timeout-ms <ms>] [--opt-out-notification-method <method>]... [--proxy-script <path>] [--log-file <path>]

Start the \$cas proxy as a detached background process.
Prints CAS_STATUS, PID, and LOG_PATH.
USAGE
}

usage_cas_stop() {
  cat <<USAGE
Usage: puff.sh cas-stop [--force]

Stop the detached \$cas proxy process started via cas-start.
USAGE
}

usage_main() {
  cat <<USAGE
Usage: puff.sh <command> [options]

Commands:
  submit   Submit a Codex Cloud task.
  doctor   Check codex cloud readiness (login/env resolution).
  watch    Poll status for a task until terminal state.
  launch   Submit task + start detached watcher.
  jobs     List detached watcher jobs.
  stop     Stop a detached watcher job.
  cas-start  Start \$cas proxy in background.
  cas-stop   Stop background \$cas proxy.
  help     Show this message.

Run "puff.sh <command> --help" for command-specific options.
USAGE
}

main() {
  local command="${1:-help}"
  if (( $# > 0 )); then
    shift
  fi

  case "$command" in
    submit)
      cmd_submit "$@"
      ;;
    doctor)
      cmd_doctor "$@"
      ;;
    watch)
      cmd_watch "$@"
      ;;
    launch)
      cmd_launch "$@"
      ;;
    jobs)
      cmd_jobs "$@"
      ;;
    stop)
      cmd_stop "$@"
      ;;
    cas-start)
      cmd_cas_start "$@"
      ;;
    cas-stop)
      cmd_cas_stop "$@"
      ;;
    help|-h|--help)
      usage_main
      ;;
    *)
      die "unknown command: $command"
      ;;
  esac
}

main "$@"
