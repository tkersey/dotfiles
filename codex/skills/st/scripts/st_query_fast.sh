#!/usr/bin/env bash
set -euo pipefail

DEFAULT_FILE=".codex/st-plan.jsonl"

usage() {
  cat >&2 <<'EOF'
usage: st_query_fast.sh [--file PATH] ready|blocked|show [ID]
EOF
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf "error: required command '%s' is not installed or not in PATH\n" "$1" >&2
    exit 127
  fi
}

emit_empty() {
  case "$1" in
    ready|blocked)
      printf '[]\n'
      ;;
    show)
      if [ -n "${2:-}" ]; then
        printf 'null\n'
      else
        printf '{"items":[]}\n'
      fi
      ;;
    *)
      printf '[]\n'
      ;;
  esac
}

plan_file="$DEFAULT_FILE"
query=""
item_id=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --file)
      if [ "$#" -lt 2 ]; then
        printf "error: --file requires a path\n" >&2
        usage
        exit 2
      fi
      plan_file="$2"
      shift 2
      ;;
    ready|blocked|show)
      query="$1"
      shift
      break
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf "error: unknown argument: %s\n" "$1" >&2
      usage
      exit 2
      ;;
  esac
done

if [ -z "$query" ]; then
  printf "error: missing query command\n" >&2
  usage
  exit 2
fi

if [ "$query" = "show" ]; then
  if [ "$#" -gt 1 ]; then
    printf "error: too many arguments for show\n" >&2
    usage
    exit 2
  fi
  if [ "$#" -eq 1 ]; then
    item_id="$1"
  fi
else
  if [ "$#" -ne 0 ]; then
    printf "error: unexpected argument for %s: %s\n" "$query" "$1" >&2
    usage
    exit 2
  fi
fi

require_cmd jq
require_cmd rg

if [ ! -e "$plan_file" ] || [ ! -s "$plan_file" ]; then
  emit_empty "$query" "$item_id"
  exit 0
fi

if [ ! -r "$plan_file" ]; then
  printf "error: cannot read file: %s\n" "$plan_file" >&2
  exit 1
fi

checkpoint_line="$(
  {
    rg -n '"op"[[:space:]]*:[[:space:]]*"(replace|checkpoint|snapshot)"|"items"[[:space:]]*:[[:space:]]*\[' "$plan_file" || true
  } | tail -n 1 | cut -d: -f1
)"

start_line=1
case "$checkpoint_line" in
  ''|*[!0-9]*)
    start_line=1
    ;;
  *)
    start_line="$checkpoint_line"
    if [ "$start_line" -lt 1 ]; then
      start_line=1
    fi
    ;;
esac

tail -n "+$start_line" "$plan_file" | jq -cn --arg query "$query" --arg id "$item_id" '
def trim:
  gsub("^[[:space:]]+|[[:space:]]+$";"");

def status_norm:
  ((. // "pending") | tostring | ascii_downcase | trim) as $s
  | if $s == "open" or $s == "queued" then "pending"
    elif $s == "active" or $s == "doing" or $s == "in-progress" then "in_progress"
    elif $s == "done" or $s == "closed" then "completed"
    elif $s == "cancelled" then "canceled"
    else $s
    end;

def edge_norm:
  if type == "string" then
    (trim) as $id
    | if ($id | length) == 0 then empty else {id: $id, type: "blocks"} end
  elif type == "object" then
    ((.id // "") | tostring | trim) as $id
    | ((.type // "blocks") | tostring | ascii_downcase | trim) as $type
    | if ($id | length) == 0 then empty else {id: $id, type: (if ($type | length) == 0 then "blocks" else $type end)} end
  else
    empty
  end;

def comments_norm:
  if type == "array" then
    [
      .[]?
      | if type == "object" then
          {
            ts: ((.ts // "") | tostring),
            author: ((.author // "") | tostring),
            text: ((.text // "") | tostring)
          }
        else
          empty
        end
    ]
  else
    []
  end;

def deps_norm:
  if type == "array" then
    [ .[]? | edge_norm ] | unique_by(.id)
  else
    []
  end;

def canonical_item:
  {
    id: (.id // "" | tostring | trim),
    step: (.step // "" | tostring),
    status: (.status | status_norm),
    deps: (.deps | deps_norm),
    notes: (.notes // "" | tostring),
    comments: (.comments | comments_norm)
  }
  | select(.id != "");

def op_name:
  (.op // .type // "" | tostring | ascii_downcase | gsub("-"; "_"));

def checkpoint_items:
  if (.items? | type) == "array" then .items
  elif (.snapshot? | type) == "array" then .snapshot
  elif (.snapshot? | type) == "object" and ((.snapshot.items? | type) == "array") then .snapshot.items
  elif (.state? | type) == "object" and ((.state.items? | type) == "array") then .state.items
  elif (.plan? | type) == "object" and ((.plan.items? | type) == "array") then .plan.items
  else []
  end;

def replace_items($items):
  reduce $items[] as $raw (
    [];
    ($raw | canonical_item) as $item
    | if $item then . + [$item] else . end
  );

def upsert_item($state; $item):
  ($state | map(.id) | index($item.id)) as $idx
  | if $idx == null then
      $state + [$item]
    else
      ($state | .[$idx] = $item)
    end;

def apply_event($state; $ev):
  ($ev | op_name) as $op
  | if ($op == "replace" or $op == "checkpoint" or $op == "snapshot") then
      replace_items($ev | checkpoint_items)
    elif ($op == "upsert" or $op == "add") then
      (($ev.item? // $ev.record? // {}) | canonical_item) as $item
      | if $item then upsert_item($state; $item) else $state end
    elif $op == "set_status" then
      (($ev.id // "") | tostring | trim) as $target
      | (($ev.status // "pending") | status_norm) as $status
      | if $target == "" then
          $state
        else
          ($state | map(if .id == $target then .status = $status else . end))
        end
    elif $op == "set_deps" then
      (($ev.id // "") | tostring | trim) as $target
      | (($ev.deps // []) | deps_norm) as $deps
      | if $target == "" then
          $state
        else
          ($state | map(if .id == $target then .deps = $deps else . end))
        end
    elif ($op == "remove" or $op == "delete") then
      (($ev.id // "") | tostring | trim) as $target
      | if $target == "" then
          $state
        else
          ($state | map(select(.id != $target)))
        end
    elif (($ev | checkpoint_items) | length) > 0 then
      replace_items($ev | checkpoint_items)
    else
      $state
    end;

def waiting_on($by_id; $item):
  [
    $item.deps[]? as $dep
    | ($dep.id // "") as $dep_id
    | select(($dep_id | length) > 0)
    | select((($by_id[$dep_id]? | .status?) // "") != "completed")
    | $dep_id
  ] | unique;

def dep_state($item; $waiting):
  if $item.status == "blocked" then
    "blocked_manual"
  elif ($item.status == "completed" or $item.status == "deferred" or $item.status == "canceled") then
    "n/a"
  elif ($waiting | length) > 0 then
    "waiting_on_deps"
  else
    "ready"
  end;

def enrich($items):
  ($items | map({key: .id, value: .}) | from_entries) as $by_id
  | $items
  | map(
      (waiting_on($by_id; .)) as $waiting
      | . + {
          waiting_on: $waiting,
          dep_state: dep_state(.; $waiting)
        }
    );

(reduce (inputs | select(type == "object")) as $ev ([]; apply_event(.; $ev))) as $items
| (enrich($items)) as $enriched
| if $query == "ready" then
    [ $enriched[] | select(.status == "pending" and (.waiting_on | length) == 0) ]
  elif $query == "blocked" then
    [ $enriched[] | select(.status == "blocked" or (.waiting_on | length) > 0) ]
  elif $query == "show" then
    if ($id | length) > 0 then
      ([ $enriched[] | select(.id == $id) ] | if length > 0 then .[0] else null end)
    else
      {items: $enriched}
    end
  else
    error("unsupported query")
  end
'
