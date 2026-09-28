#!/usr/bin/env python3
"""Render a private, offline Elenctic findings tracker; no third-party dependencies."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any
from urllib.parse import urlsplit

SCHEMA = "elenctic-report/v1"
KINDS = {"merge-blocker", "risk", "concern"}


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def text(value: Any, name: str, *, empty: bool = False) -> str:
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise ValueError(f"{name} must be {'a' if empty else 'a nonempty'} string")
    return value


def link(value: Any, name: str) -> str:
    value = text(value, name)
    parsed = urlsplit(value)
    if (parsed.scheme not in {"https", "http"} or not parsed.hostname
            or parsed.username is not None or parsed.password is not None
            or any(ord(c) < 32 for c in value)):
        raise ValueError(f"{name} must be an absolute HTTP(S) URL without credentials")
    return value


def prepare(raw: Any) -> dict[str, Any]:
    """Validate the presentation boundary, not the truth/admission of a review."""
    if not isinstance(raw, dict) or raw.get("schema") != SCHEMA:
        raise ValueError(f"expected schema {SCHEMA}")
    identity = raw.get("identity")
    if not isinstance(identity, dict):
        raise ValueError("identity must be the actual campaign identity object")
    identity = dict(identity)
    if identity.get("schema") != "elenctic-review-identity/v1" or identity.get("mode") != "campaign":
        raise ValueError("identity must be an Elenctic v1 campaign identity")
    for field in ("repo", "campaign_id", "base", "candidate", "view"):
        text(identity.get(field), f"identity.{field}")
    if type(identity.get("pr")) is not int or identity["pr"] <= 0:
        raise ValueError("identity.pr must be a positive integer")
    if identity["view"] != "pr-head":
        raise ValueError("identity.view must be pr-head")
    if identity.get("verdict") not in {"BLOCKED", "APPROVE", "INCOMPLETE"}:
        raise ValueError("invalid identity.verdict")
    for field in ("coverage", "selected_scope_coverage"):
        if identity.get(field) not in {"complete", "partial"}:
            raise ValueError(f"invalid identity.{field}")
    if identity.get("whole_pr_coverage") not in {"complete", "partial", "not-established"}:
        raise ValueError("invalid identity.whole_pr_coverage")
    expected = "complete" if identity["whole_pr_coverage"] == "complete" else "partial"
    if identity["coverage"] != expected:
        raise ValueError("coverage must conservatively represent whole-PR coverage")
    # Null is a legitimate absence, never an invented provenance identifier.
    for field in ("campaign_context_id", "campaign_seed_thread_id", "campaign_policy_id"):
        if field not in identity:
            raise ValueError(f"identity.{field} is required; use null only when never created")
        if identity[field] is not None:
            text(identity[field], f"identity.{field}")
    if identity["campaign_seed_thread_id"] is not None and (
            identity["campaign_context_id"] is None or identity["campaign_policy_id"] is None):
        raise ValueError("a seed requires both prepared context and policy identity")

    result: dict[str, Any] = {"schema": SCHEMA, "identity": identity}
    for field in ("title", "generated_at", "summary", "coverage_note", "report_text"):
        result[field] = text(raw.get(field), field)
    result["pr_url"] = link(raw.get("pr_url"), "pr_url")
    findings = raw.get("findings")
    if not isinstance(findings, list):
        raise ValueError("findings must be an array (empty is allowed)")
    seen = set()
    result["findings"] = []
    for index, source in enumerate(findings):
        if not isinstance(source, dict):
            raise ValueError(f"findings[{index}] must be an object")
        finding = {}
        for field in ("id", "title", "location", "detail", "required_outcome"):
            finding[field] = text(source.get(field), f"findings[{index}].{field}")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}", finding["id"]):
            raise ValueError("finding IDs must be opaque ASCII identifiers, not paths or array positions")
        if finding["id"] in seen:
            raise ValueError(f"duplicate finding id: {finding['id']}")
        seen.add(finding["id"])
        finding["disposition"] = source.get("disposition")
        if finding["disposition"] not in KINDS:
            raise ValueError(f"invalid disposition for {finding['id']}")
        finding["draft"] = text(source.get("draft", ""), "draft", empty=True)
        if finding["draft"] and finding["disposition"] != "merge-blocker":
            raise ValueError("only retained merge blockers may contain a draft")
        sources = source.get("sources", [])
        if not isinstance(sources, list):
            raise ValueError("sources must be an array")
        finding["sources"] = [
            {"label": text(s.get("label"), "source.label"), "url": link(s.get("url"), "source.url")}
            for s in sources if isinstance(s, dict)
        ]
        if len(finding["sources"]) != len(sources):
            raise ValueError("each source must be an object")
        # A changed finding conservatively needs handling again; reordering does not.
        finding["fingerprint"] = digest(finding)
        result["findings"].append(finding)
    blockers = any(f["disposition"] == "merge-blocker" for f in result["findings"])
    if blockers != (identity["verdict"] == "BLOCKED"):
        raise ValueError("BLOCKED requires a retained blocker; blockers require BLOCKED")
    if identity["verdict"] == "APPROVE" and identity["selected_scope_coverage"] != "complete":
        raise ValueError("APPROVE requires complete selected-scope coverage")
    result["findings"].sort(key=lambda f: ["merge-blocker", "risk", "concern"].index(f["disposition"]))
    # Stable across regenerations of this campaign; never silently carry checks to a new epoch.
    result["report_key"] = "elenctic:" + digest({
        k: identity[k] for k in ("repo", "pr", "campaign_id", "base", "candidate", "view")
    })
    return result


def script_data(value: Any) -> str:
    return (canonical(value).replace("&", "\\u0026").replace("<", "\\u003c")
            .replace(">", "\\u003e").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def render(raw: Any) -> tuple[str, dict[str, Any]]:
    report = prepare(raw)
    template = (Path(__file__).resolve().parents[1] / "assets" / "report.html").read_text(encoding="utf-8")
    replacements = {"__REPORT_DATA__": script_data(report),
                    "__REPORT_TEXT__": html.escape(report["report_text"]),
                    "__REPORT_TITLE__": html.escape(report["title"])}
    output = re.sub(r"__REPORT_(?:DATA|TEXT|TITLE)__", lambda m: replacements[m[0]], template)
    return output, report


def write_report(raw: Any, output: Path | None = None) -> Path:
    document, report = render(raw)
    if output is None:
        folder = Path(tempfile.mkdtemp(prefix="elenctic-"))
        folder.chmod(0o700)
        output = folder / "report.html"
    output = output.absolute()
    if output.suffix.lower() != ".html" or not output.parent.is_dir():
        raise ValueError("output must be an .html file in an existing private scratch directory")
    if os.name == "posix" and output.parent.stat().st_mode & 0o077:
        raise ValueError("output directory must be private (owner-only permissions)")
    if output.is_symlink():
        raise ValueError("refusing to overwrite a symlink")
    if output.exists():
        old = output.read_text(encoding="utf-8")
        match = re.search(r'<script id="report-data" type="application/json">(.*?)</script>', old, re.S)
        if not match or json.loads(match[1]).get("report_key") != report["report_key"]:
            raise ValueError("output belongs to another report; choose a new private directory")
    fd, temporary = tempfile.mkstemp(prefix=".elenctic-", dir=output.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(document)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="sanitized report JSON")
    parser.add_argument("--output", type=Path, help="reuse the same campaign's report path on regeneration")
    args = parser.parse_args()
    try:
        path = write_report(json.loads(args.input.read_text(encoding="utf-8")), args.output)
    except (ValueError, OSError, TypeError) as error:
        parser.exit(2, f"elenctic report: {error}\n")
    print(canonical({"path": str(path), "url": path.as_uri(), "bytes": path.stat().st_size}))


if __name__ == "__main__":
    main()
