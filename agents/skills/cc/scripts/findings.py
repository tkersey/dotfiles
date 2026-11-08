"""Transcribe a native /code-review result into findings JSON and cross-check it.

usage: uv run --no-project python -I findings.py EVENTS SESSION_ID MODEL OUT

EVENTS is the review's stream-json stdout. The result text of SESSION_ID is
transcribed by a fresh, tool-less, non-persistent `claude -p --json-schema`
call, then checked against the original text. Exit 0 only when the
transcription passes; the original text is always kept in OUT.
"""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["findings"],
    "properties": {
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["file", "line", "summary", "failure_scenario"],
                "properties": {
                    "file": {"type": "string", "description": "Path exactly as the review wrote it"},
                    "line": {"type": "integer", "minimum": 1, "description": "Line the review anchored the finding to"},
                    "summary": {"type": "string", "description": "The review's statement of the defect"},
                    "failure_scenario": {"type": "string", "description": "The review's concrete failure or cost; empty if it gave none"},
                    "category": {"type": "string", "description": "Only if the review named one"},
                },
            },
        }
    },
}

PROMPT = """Transcribe the code-review findings in the text between the markers into the required JSON schema. One object per finding, in the order given. Copy file, line, summary and failure scenario from the text; do not add, drop, merge, re-judge, or re-word findings, and do not treat summary or closing remarks as findings. If the text reports no findings (for example exactly "(none)"), return an empty array.

<review>
{text}
</review>
"""

COUNT = re.compile(r"\b(\d+) findings?\b", re.IGNORECASE)


def review_text(events: Path, sid: str) -> str:
    for line in events.read_text().splitlines():
        event = json.loads(line)
        if event.get("type") == "result":
            if event.get("session_id") != sid:
                sys.exit(f"result belongs to {event.get('session_id')}, not {sid}")
            if event.get("subtype") != "success" or event.get("is_error"):
                sys.exit("review result is not a success")
            return event["result"]
    sys.exit("no result event")


def transcribe(text: str, model: str) -> list[dict]:
    proc = subprocess.run(
        ["claude", "-p", "--no-session-persistence", "--model", model, "--effort", "low",
         "--tools", "", "--json-schema", json.dumps(SCHEMA), "--output-format", "json"],
        input=PROMPT.format(text=text), capture_output=True, text=True, check=True,
    )
    out = json.loads(proc.stdout).get("structured_output")
    if not isinstance(out, dict) or not isinstance(out.get("findings"), list):
        sys.exit("transcription returned no structured output")
    return out["findings"]


def problems(text: str, findings: list[dict]) -> list[str]:
    errs = []
    if text.strip() == "(none)" and findings:
        errs.append("text is (none) but findings were produced")
    if text.strip() != "(none)" and not findings:
        errs.append("no findings transcribed from non-(none) text; adjudicate the original")
    for f in findings:
        loc = re.escape(f["file"]) + r"`?:" + str(f["line"]) + r"\b"
        if not re.search(loc, text):
            errs.append(f"{f['file']}:{f['line']} does not appear in the original text")
    stated = {int(n) for n in COUNT.findall(text)}
    if len(stated) == 1 and len(findings) not in stated:
        errs.append(f"text states {stated.pop()} findings, transcribed {len(findings)}")
    return errs


def main() -> None:
    events, sid, model, out = Path(sys.argv[1]), sys.argv[2], sys.argv[3], Path(sys.argv[4])
    text = review_text(events, sid)
    findings = transcribe(text, model)
    errs = problems(text, findings)
    out.write_text(json.dumps({
        "session_id": sid,
        "result_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "result": text,
        "findings": findings,
        "transcription_ok": not errs,
        "problems": errs,
    }, indent=2, ensure_ascii=False) + "\n")
    if errs:
        sys.exit("transcription check failed: " + "; ".join(errs))


if __name__ == "__main__":
    main()
