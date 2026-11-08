"""Offline checks for cc readback and transcription guards; no model is called.

usage: uv run --no-project python -I agents/skills/cc/tests/test_cc.py
"""

import copy
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

scripts = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(scripts))
import findings  # noqa: E402

SID = "11111111-2222-3333-4444-555555555555"
MODEL = "claude-opus-5-5"
BASE = "04c0a84a962c3e637c14614498aa1950a776ba6e"
PROMPT = b"Perform one independent, read-only code review.\n\n{\"lens_name\": \"fresh-eyes\"}"


def standard_events(level="high"):
    return [
        {"type": "system", "subtype": "init", "session_id": SID, "model": MODEL},
        {"type": "user", "message": {"content": [{"type": "text", "text":
            f"Review target: `{BASE}`\n\n`{level} effort → 8 inline angles → ≤10 findings`\n\n## Phase 1"}]}},
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash",
            "input": {"command": f"git diff {BASE[:12]} HEAD"}}]}},
        {"type": "result", "subtype": "success", "is_error": False, "session_id": SID,
         "modelUsage": {MODEL: {}}, "permission_denials": [], "result": "(none)"},
    ]


def custom_events():
    output = {"findings": [], "overall_correctness": "patch is correct",
              "overall_explanation": "Inspected the whole changeset.", "overall_confidence_score": 0.8}
    return [
        {"type": "system", "subtype": "init", "session_id": SID, "model": MODEL},
        {"type": "result", "subtype": "success", "is_error": False, "session_id": SID,
         "modelUsage": {MODEL: {}}, "permission_denials": [], "result": "", "structured_output": output},
    ]


def transcript(prompt=PROMPT):
    return [
        {"type": "queue-operation", "sessionId": SID},
        {"type": "user", "isMeta": True, "sessionId": SID, "message": {"content": "<meta>"}},
        {"type": "user", "sessionId": SID, "message": {"content": prompt.decode()}},
        {"type": "assistant", "sessionId": SID, "message": {"content": []}},
    ]


def readback(base: Path, kind: str, events: list, records=None, prompt=PROMPT, extra_transcript=False):
    tmp = Path(tempfile.mkdtemp(dir=base))
    events_path, out = tmp / "events.jsonl", tmp / "out.json"
    events_path.write_text("".join(json.dumps(e) + "\n" for e in events))
    config = tmp / "config"
    if records is not None:
        project = config / "projects" / "-repo"
        project.mkdir(parents=True, exist_ok=True)
        (project / f"{SID}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
        if extra_transcript:
            other = config / "projects" / "-elsewhere"
            other.mkdir(parents=True, exist_ok=True)
            (other / f"{SID}.jsonl").write_text("")
    prompt_path = tmp / "prompt.txt"
    prompt_path.write_bytes(prompt)
    args = ([kind, str(events_path), SID, MODEL, BASE, "high", str(out)] if kind == "standard"
            else [kind, str(events_path), SID, MODEL, str(prompt_path), str(out)])
    env = {**os.environ, "CLAUDE_CONFIG_DIR": str(config)}
    proc = subprocess.run([sys.executable, "-I", str(scripts / "readback.py"), *args],
                          env=env, capture_output=True, text=True)
    report = json.loads(out.read_text())
    assert (proc.returncode == 0) == report["ok"], proc.stderr
    return report


def expect(report, fragment=None):
    if fragment is None:
        assert report["ok"], report["problems"]
    else:
        assert not report["ok"] and any(fragment in p for p in report["problems"]), (fragment, report["problems"])


def main() -> None:
    checks = 0
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        expect(readback(tmp, "standard", standard_events()))
        report = readback(tmp, "standard", standard_events())
        assert report["observed_level"] == "high" and report["result"] == "(none)"
        expect(readback(tmp, "standard", standard_events(level="medium")), "recipe ran at medium")
        no_diff = standard_events()
        no_diff[2]["message"]["content"][0]["input"]["command"] = "git status"
        expect(readback(tmp, "standard", no_diff), "no reviewer command read")
        fallback = standard_events()
        fallback[3]["modelUsage"] = {MODEL: {}, "claude-sonnet-5-5": {}}
        expect(readback(tmp, "standard", fallback), "models used")
        denied = standard_events()
        denied[3]["permission_denials"] = [{"tool_name": "Bash", "tool_input": {"command": "git diff"}}]
        expect(readback(tmp, "standard", denied), "permission denied")
        foreign = standard_events()
        foreign[3]["session_id"] = "other"
        expect(readback(tmp, "standard", foreign), "result session")
        failed = standard_events()
        failed[3]["subtype"] = "error_during_execution"
        expect(readback(tmp, "standard", failed), "result is error_during_execution")
        expect(readback(tmp, "standard", standard_events()[:3]), "not terminal")
        checks += 9

        expect(readback(tmp, "custom", custom_events(), transcript()))
        expect(readback(tmp, "custom", custom_events(), transcript(PROMPT + b" ")), "delivery unverified")
        missing = copy.deepcopy(custom_events())
        del missing[1]["structured_output"]
        expect(readback(tmp, "custom", missing, transcript()), "no structured_output")
        expect(readback(tmp, "custom", custom_events(), None), "no unique transcript")
        expect(readback(tmp, "custom", custom_events(), transcript(), extra_transcript=True), "no unique transcript")
        mixed = transcript() + [{"type": "user", "sessionId": "other", "message": {"content": "x"}}]
        expect(readback(tmp, "custom", custom_events(), mixed), "mixes sessions")
        checks += 6

    one = [{"file": "calc.py", "line": 3, "summary": "s", "failure_scenario": "f"}]
    assert findings.problems("`calc.py:3` — off by one", one) == []
    assert findings.problems("(none)", []) == []
    assert findings.problems("(none)", one)
    assert findings.problems("Something went wrong at calc.py:3", [])
    assert any("does not appear" in p for p in findings.problems("`calc.py:4` — x", one))
    assert any("states 2 findings" in p for p in findings.problems("2 findings: `calc.py:3` x", one))
    checks += 6
    print(f"cc: {checks} readback and transcription guards passed; no model was called")


if __name__ == "__main__":
    main()
