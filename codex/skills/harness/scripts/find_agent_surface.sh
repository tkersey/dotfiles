#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"

if [[ ! -d "$ROOT" ]]; then
  echo "Path not found or not a directory: $ROOT" >&2
  exit 1
fi

if command -v rg >/dev/null 2>&1; then
  RG_BASE=(
    rg -n -S --hidden
    --glob '!**/.git/**'
    --glob '!**/node_modules/**'
    --glob '!**/dist/**'
    --glob '!**/build/**'
    --glob '!**/.next/**'
    --glob '!**/coverage/**'
    --glob '!**/.venv/**'
    --glob '!**/venv/**'
  )

  echo "== Candidate files by name =="
  rg --files "$ROOT" | rg '(^|/)(agent|agents|prompt|prompts|system|tool|tools|mcp|guardrail|eval|evals|trace|tracing|workflow|handoff|skill|config|policy|schema|runner|orchestr)' || true
  echo

  echo "== Agent definitions and instructions =="
  "${RG_BASE[@]}" \
    '(Agent\(|new Agent\(|instructions\s*=|instructions:|system_prompt|systemPrompt|messages\s*=|messages:|assistant_instructions|developer_instructions|prompt_template|AGENTS\.md|SKILL\.md)' \
    "$ROOT" || true
  echo

  echo "== Tool definitions and schemas =="
  "${RG_BASE[@]}" \
    '(@function_tool|function_tool|tool\(|tools\s*=|tools:|as_tool|asTool|mcp|server\.tool|Tool\(|toolChoice|tool_choice|output_schema|zod|JSONSchema|json schema|parameters\s*:|strict\s*:)' \
    "$ROOT" || true
  echo

  echo "== Orchestration and run loop =="
  "${RG_BASE[@]}" \
    '(Runner\.run|run\(|while loop|max_turns|maxTurns|exit condition|handoff|delegate|delegation|manager|worker|router|orchestr|retry|backoff)' \
    "$ROOT" || true
  echo

  echo "== Guardrails, approvals, and safety =="
  "${RG_BASE[@]}" \
    '(guardrail|tripwire|approval|approve|human.?in.?the.?loop|confirm|destructive|dangerous|unsafe|moderation|policy)' \
    "$ROOT" || true
  echo

  echo "== Evals, traces, and observability =="
  "${RG_BASE[@]}" \
    '(eval|grader|dataset|trace|tracing|span|telemetry|jsonl|golden|assert|score|rubric|output-schema|output_schema|regression)' \
    "$ROOT" || true
  echo

  echo "== Memory, retrieval, and context =="
  "${RG_BASE[@]}" \
    '(memory|retriev|vector|file_search|web_search|search tool|context window|truncate|pagination|filter|top_k|topK)' \
    "$ROOT" || true
else
  echo "ripgrep (rg) not found. Falling back to grep."
  echo

  echo "== Candidate files by name =="
  find "$ROOT" \
    -path '*/.git' -prune -o \
    -path '*/node_modules' -prune -o \
    -path '*/dist' -prune -o \
    -path '*/build' -prune -o \
    -path '*/.next' -prune -o \
    -path '*/coverage' -prune -o \
    -path '*/.venv' -prune -o \
    -path '*/venv' -prune -o \
    -type f | grep -E '(^|/)(agent|agents|prompt|prompts|system|tool|tools|mcp|guardrail|eval|evals|trace|tracing|workflow|handoff|skill|config|policy|schema|runner|orchestr)' || true
  echo

  echo "== Broad content search =="
  grep -RInE \
    --exclude-dir=.git \
    --exclude-dir=node_modules \
    --exclude-dir=dist \
    --exclude-dir=build \
    --exclude-dir=.next \
    --exclude-dir=coverage \
    --exclude-dir=.venv \
    --exclude-dir=venv \
    'Agent\(|new Agent\(|instructions=|instructions:|system_prompt|tool\(|tools=|tools:|guardrail|handoff|delegate|eval|trace|memory|retriev|mcp' \
    "$ROOT" || true
fi
