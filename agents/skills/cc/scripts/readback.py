"""Admit or hold one native Claude Code review session from its own evidence.

usage:
  uv run --no-project python -I readback.py standard EVENTS SESSION_ID MODEL TARGET LEVEL OUT
  uv run --no-project python -I readback.py custom   EVENTS SESSION_ID MODEL PROMPT_FILE OUT

EVENTS is the session's captured `--output-format stream-json --verbose` stdout.
MODEL is the full selected model ID. TARGET is the base passed to /code-review,
or "-" when none was passed. Custom delivery is checked against the session
transcript under $CLAUDE_CONFIG_DIR (default ~/.claude)/projects/*/SESSION_ID.jsonl.
OUT always receives the evidence and every problem found; exit 0 only when
there are none. Git subject checks stay with the caller.
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path

LEVEL = re.compile(r"`(\w+) effort\b")
HEX = re.compile(r"\b[0-9a-f]{7,40}\b")


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    return "".join(part.get("text", "") for part in content or [] if part.get("type") == "text")


def load_events(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def common(events: list[dict], sid: str, model: str, problems: list[str]) -> dict:
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), None)
    result = next((e for e in reversed(events) if e.get("type") == "result"), None)
    if init is None:
        problems.append("no init event")
    else:
        if init.get("session_id") != sid:
            problems.append(f"init session {init.get('session_id')} is not {sid}")
        if init.get("model") != model:
            problems.append(f"init model {init.get('model')} is not {model}")
    if result is None:
        problems.append("no result event: not terminal")
        return {}
    if result.get("session_id") != sid:
        problems.append(f"result session {result.get('session_id')} is not {sid}")
    if result.get("subtype") != "success" or result.get("is_error"):
        problems.append(f"result is {result.get('subtype')} (is_error={result.get('is_error')})")
    used = sorted((result.get("modelUsage") or {}).keys())
    if used != [model]:
        problems.append(f"models used {used}, expected only {model}")
    denials = result.get("permission_denials") or []
    for denial in denials:
        problems.append("permission denied: " + json.dumps(denial.get("tool_input"))[:300])
    return result


def standard(events: list[dict], target: str, level: str, problems: list[str]) -> dict:
    recipe = next((text_of(e["message"]["content"]) for e in events
                   if e.get("type") == "user" and "Review target:" in text_of(e.get("message", {}).get("content"))), None)
    if recipe is None:
        problems.append("no expanded /code-review recipe in the session")
        return {}
    observed = LEVEL.search(recipe)
    observed_level = observed.group(1) if observed else None
    if observed_level != level:
        problems.append(f"recipe ran at {observed_level} effort, bound level is {level}")
    if target != "-":
        if f"Review target: `{target}`" not in recipe:
            problems.append(f"recipe target is not {target}")
        commands = [str(part.get("input", {}).get("command", "")) for e in events if e.get("type") == "assistant"
                    for part in e["message"].get("content", []) if part.get("type") == "tool_use"]
        if not any("git diff" in c and any(target.startswith(h) for h in HEX.findall(c)) for c in commands):
            problems.append(f"no reviewer command read `git diff` against {target}")
    return {"observed_level": observed_level, "recipe_header": recipe.split("\n\n", 2)[:2]}


def transcript_path(sid: str) -> Path | None:
    root = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / "projects"
    matches = sorted(root.glob(f"*/{sid}.jsonl"))
    return matches[0] if len(matches) == 1 else None


def custom(result: dict, sid: str, prompt: bytes, problems: list[str]) -> dict:
    evidence = {"prompt_sha256": hashlib.sha256(prompt).hexdigest()}
    path = transcript_path(sid)
    if path is None:
        problems.append(f"no unique transcript for {sid}")
    else:
        evidence["transcript"] = str(path)
        records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        if {r["sessionId"] for r in records if "sessionId" in r} != {sid}:
            problems.append("transcript mixes sessions")
        first = next((r for r in records if r.get("type") == "user" and not r.get("isMeta")), None)
        delivered = text_of(first["message"]["content"]) if first else None
        if delivered is None or delivered.encode() != prompt:
            problems.append("first transcript message is not the exact prompt: delivery unverified")
    output = result.get("structured_output")
    if not isinstance(output, dict):
        problems.append("no structured_output object")
    evidence["structured_output"] = output
    return evidence


def main() -> None:
    kind, args = sys.argv[1], sys.argv[2:]
    if kind == "standard" and len(args) == 6:
        events_path, sid, model, target, level, out = args
    elif kind == "custom" and len(args) == 5:
        events_path, sid, model, prompt_path, out = args
    else:
        sys.exit(__doc__)
    problems: list[str] = []
    events = load_events(Path(events_path))
    result = common(events, sid, model, problems)
    report = {"kind": kind, "session_id": sid, "model": model, "result": result.get("result")}
    if kind == "standard":
        report.update(standard(events, target, level, problems))
    else:
        report.update(custom(result, sid, Path(prompt_path).read_bytes(), problems))
    report.update(ok=not problems, problems=problems)
    Path(out).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    if problems:
        sys.exit("hold: " + "; ".join(problems))


if __name__ == "__main__":
    main()
