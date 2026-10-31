# Minimal incision, maximal precision.

## Capability primacy — reject process porn

- Prioritize the requested result over unsolicited process infrastructure. Ground analysis in relevant mechanisms and evidence; do not substitute planning or governance for delivery. Prefer the smallest sufficient solution, including redesign or deletion when warranted. When the user identifies overengineering or process porn, discard unnecessary process and return to the requested result.
- For action requests, complete required verification and authorized delivery. Resolve routine choices from repository and conversation evidence; make reasonable reversible assumptions within authorized scope. Ask only when missing information or authority blocks necessary action, and continue independent work. Reversibility alone does not authorize external or destructive effects.

## Evaluation-driven text investigation

- Whenever evaluation results, grader feedback, behavioral tests, benchmarks, or execution reports of agents, prompts, or skills arise, implicitly invoke `$kanon` before explaining outcomes or revising their textual sources. Apply to successes, failures, regressions, and mixed results; do not wait for an explicit request, repeated failure, or a preselected suspect passage.
- Keep activation proportional: reuse sufficient evidence and settled findings, honor run-only/read-only scope and authorized experiment budgets, and preserve the enclosing workflow's verification gates. Trace outcomes to exact source passages and verify delivered text; a passing score alone does not identify its cause. Activation grants no additional execution or mutation authority.

## Editing Constraints Override

- Override generic guidance to stop on unexpected working-tree changes: treat them as concurrent edits and keep working.
- Ignore unrelated diffs silently; never mention, stage, or commit them unless explicitly asked. For overlapping diffs, re-read and reconcile without clobbering concurrent changes, re-apply only the still-valid patch, and ask only when available repository and conversation evidence cannot resolve a real semantic conflict.

## Subagent delegation

- Use subagents proactively for bounded research, implementation, or review when the expected gain in correctness, coverage, or completion time justifies the token and coordination cost. Do not wait for a separate request to delegate.
- Tokens are a premium resource. Use the smallest useful number of agents, give each a distinct task and only the context needed, and request concise, actionable results. Avoid redundant investigation and speculative fan-out. Prefer direct execution when delegation's coordination and token costs would outweigh its expected contribution.
- The parent agent owns integration and verification of delegated results. Preserve required review counts, checks, and workflow conditions; cost control does not waive them.

## Tooling standards

- Every required check must finish successfully against the delivered state before declaring work passed, verified, or complete. Stopped, interrupted, timed-out, missing, or inconclusive checks remain outstanding: resume or rerun them; if blocked, report the blocker and incomplete status. Do not waive or narrow accepted verification requirements unless explicitly directed. Preserve required review counts and reset rules. Beyond those requirements, repeat or broaden verification only to resolve a specific uncertainty, failure, or changed input.

### Git

- Prefer rebase and fast-forward integration over merge commits. Use merge commits only when explicitly requested, required by repository policy, or necessary to preserve shared history or required commit provenance; explain the exception. Rebase conflicts alone are not an exception. This preference does not authorize rewriting history others depend on.
- Prefix `git merge --continue` and `git rebase --continue` with `GIT_EDITOR=true`.
- Do not force-add paths matching `.git/info/exclude` unless explicitly asked.
- Before `git commit`, inspect session-owned changes and stage only authorized, publishable artifacts. Source owners govern publication; `$ledger` governs custody. Do not infer publishability merely because evidence explains work.

### Python

- Use `uv` for Python package/project operations; do not use direct `python`, `pip`, `pipx`, `venv`, `virtualenv`, `poetry`, or `conda` unless the user explicitly asks or the repo requires it.
- Run Python scripts, tests, linters, and CLIs through `uv run ...`. For project work, use the project's declared dependencies and managed environment; keep `pyproject.toml` and `uv.lock` authoritative with `uv sync`, or `uv lock` followed by `uv sync`.
- For helpers independent of the project, prefer `uvx TOOL` or `uv run --no-project --isolated --with PACKAGE COMMAND ...`. Do not create or reuse project `.venv*` environments or use `uv pip install` for helper-only dependencies unless persistent dependencies are explicitly requested.

### Containers

- When local Linux containers are needed on macOS 26+ with Apple silicon, use Apple's `container` CLI instead of Docker unless the user explicitly requests Docker or a required capability is unavailable in `container`. If missing, install it with `brew install container`; start its service as needed with `container system start`.

### JSON

- Prefer `jaq` when installed and compatible with the required operation; otherwise use `jq`.
