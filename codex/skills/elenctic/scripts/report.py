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


def number_map(value: Any) -> dict[str, int]:
    """Human references are supplied, never manufactured from list positions."""
    if not isinstance(value, dict):
        raise ValueError("finding_numbers must be an object")
    numbers = {}
    for key, number in value.items():
        if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}", key):
            raise ValueError("invalid finding-number identity")
        if type(number) is not int or not 1 <= number <= 2**53 - 1:
            raise ValueError("finding numbers must be positive safe integers")
        if number in numbers.values():
            raise ValueError("a finding number cannot identify two findings")
        numbers[key] = number
    return numbers


def bind_number_history(report: dict[str, Any], previous: dict[str, Any]) -> None:
    """Retain retired references and reject renumbering on same-path regeneration."""
    history = number_map(previous.get("finding_numbers", {}))
    for source in previous.get("findings", []):
        if "number" in source:
            old = number_map({source["id"]: source["number"]})
            if source["id"] in history and history[source["id"]] != source["number"]:
                raise ValueError("previous finding-number history is inconsistent")
            history.update(old)
    for key, number in report["finding_numbers"].items():
        if key in history and history[key] != number:
            raise ValueError(f"cannot renumber finding {key}")
        history[key] = number
    report["finding_numbers"] = number_map(history)
    for finding in report["findings"]:
        if finding["id"] in history:
            finding["number"] = history[finding["id"]]


def prepare_proposal(source: Any, *, blocking: bool) -> dict[str, Any]:
    """A proposal describes future work; its shape cannot certify an elimination."""
    if not isinstance(source, dict):
        raise ValueError("each construction group needs a proposal")
    status = source.get("status")
    if status not in ("proposed", "preserve-incumbent", "unresolved", "obstructed"):
        raise ValueError("invalid proposal status")
    if status != "proposed":
        if source.get("changes"):
            raise ValueError("an unselected construction cannot advertise code changes")
        if status == "preserve-incumbent" and blocking:
            raise ValueError("preserving the incumbent cannot discharge a retained blocker")
        return {"status": status, "reason": text(source.get("reason"), "proposal.reason")}
    proposal = {key: text(source.get(key), f"proposal.{key}") for key in (
        "mechanism", "exclusion_argument", "preserve", "migration", "retirements",
        "verification", "limits")}
    changes = source.get("changes")
    if not isinstance(changes, list) or not changes:
        raise ValueError("a proposed construction needs concrete code changes")
    proposal["status"] = status
    proposal["changes"] = []
    for change in changes:
        if not isinstance(change, dict):
            raise ValueError("each code change must be an object")
        item = {key: text(change.get(key), f"change.{key}") for key in ("path", "symbol", "change")}
        path = item["path"]
        if (path.startswith("/") or re.match(r"^[A-Za-z]:", path) or "\\" in path or ".." in path.split("/")
                or any(ord(c) < 32 for c in path)):
            raise ValueError("change.path must be a repository-relative path")
        proposal["changes"].append(item)
    return proposal


def prepare_adjudications(source: Any, report: dict[str, Any], *, complete: bool) -> list[dict[str, Any]]:
    """Keep rejected/unknown feedback without laundering it into a code finding."""
    if not isinstance(source, list):
        raise ValueError("construction needs an adjudications array")
    known = {f["id"]: f for f in report["findings"]}
    seen, covered = set(), set()
    judgments = []
    for row in source:
        if not isinstance(row, dict):
            raise ValueError("each adjudication must be an object")
        item = {key: text(row.get(key), f"adjudication.{key}") for key in (
            "id", "source", "claim", "basis", "disposition", "law_authority")}
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}", item["id"]) or item["id"] in seen:
            raise ValueError("adjudication IDs must be unique opaque references")
        seen.add(item["id"])
        disposition, law = item["disposition"], item["law_authority"]
        if disposition not in ("accepted", "rejected", "follow-up", "blocked"):
            raise ValueError("invalid adjudication disposition")
        if law not in ("entailed", "strengthening", "preference", "new-requirement", "underdetermined"):
            raise ValueError("invalid law authority")
        refs = row.get("finding_ids")
        if (not isinstance(refs, list) or any(not isinstance(k, str) for k in refs)
                or len(set(refs)) != len(refs) or not set(refs) <= known.keys()):
            raise ValueError("adjudication finding_ids must reference retained findings without duplicates")
        if disposition == "accepted" and (law != "entailed" or not refs):
            raise ValueError("accepted feedback needs an entailed law and a retained finding")
        if disposition == "rejected" and refs:
            raise ValueError("rejected feedback cannot create construction pressure")
        expected = {"strengthening": "follow-up", "new-requirement": "follow-up",
                    "preference": "rejected", "underdetermined": "blocked"}.get(law)
        if expected is not None and disposition not in (expected, "rejected"):
            raise ValueError("adjudication disposition contradicts law authority")
        if (law != "entailed" or disposition in ("follow-up", "blocked")) and any(
                known[k]["disposition"] == "merge-blocker" for k in refs):
            raise ValueError("optional or unresolved feedback cannot become a merge blocker")
        item["finding_ids"] = refs[:]
        if "url" in row:
            item["url"] = link(row["url"], "adjudication.url")
        covered.update(refs)
        judgments.append(item)
    if complete and covered != known.keys():
        raise ValueError("construction adjudications must account for every retained finding")
    return judgments


def prepare_resolution(raw: dict[str, Any], report: dict[str, Any]) -> None:
    """Validate grouping as a lossless presentation, never as review adjudication."""
    workflow = raw.get("workflow", "comments")
    if workflow not in ("comments", "resolution", "construction"):
        raise ValueError("workflow must be comments, resolution or construction")
    report["workflow"] = workflow
    numbers = number_map(raw.get("finding_numbers", {}))
    originals = {f["id"]: f for f in raw["findings"]}
    for finding in report["findings"]:
        source = originals[finding["id"]]
        if "number" in source:
            number = number_map({finding["id"]: source["number"]})[finding["id"]]
            if finding["id"] in numbers and numbers[finding["id"]] != number:
                raise ValueError("finding number disagrees with its recorded identity")
            numbers[finding["id"]] = number
        if finding["id"] in numbers:
            # Numbering and grouping do not change the evidence fingerprint.
            finding["number"] = numbers[finding["id"]]
        elif workflow != "comments":
            raise ValueError(f"{workflow} requires the original number of every finding")
    report["finding_numbers"] = number_map(numbers)
    for key in ("resolution", "construction"):
        if key != workflow and raw.get(key) is not None:
            raise ValueError(f"{key} data requires explicit {key} workflow")
    if workflow == "comments":
        return
    resolution = raw.get(workflow)
    if not isinstance(resolution, dict):
        raise ValueError(f"{workflow} workflow requires a synthesis result")
    extra = {}
    if workflow == "construction":
        extra["adjudications"] = prepare_adjudications(
            resolution.get("adjudications"), report, complete=resolution.get("status") == "complete")
    if resolution.get("status") == "unavailable":
        if resolution.get("groups"):
            raise ValueError("unavailable synthesis cannot advertise complete groups")
        report[workflow] = {"status": "unavailable", "reason": text(resolution.get("reason"), f"{workflow}.reason"), **extra}
        return
    if resolution.get("status") != "complete" or not isinstance(resolution.get("groups"), list):
        raise ValueError("resolution must be complete with groups, or unavailable with a reason")
    known = {f["id"] for f in report["findings"]}
    assigned: set[str] = set()
    groups: dict[str, dict[str, Any]] = {}
    for source in resolution["groups"]:
        if not isinstance(source, dict):
            raise ValueError("each resolution group must be an object")
        group = {key: text(source.get(key), f"group.{key}")
                 for key in ("id", "title", "rationale", "objective")}
        if not re.fullmatch(r"R[1-9][0-9]{0,7}", group["id"]) or group["id"] in groups:
            raise ValueError("group IDs must be unique R1-style references")
        members = source.get("finding_ids")
        if not isinstance(members, list) or not members or any(not isinstance(k, str) for k in members):
            raise ValueError("each group needs a nonempty finding_ids array")
        if len(set(members)) != len(members) or not set(members) <= known or set(members) & assigned:
            raise ValueError("groups must reference each retained finding exactly once")
        group["finding_ids"] = members[:]
        checks = source.get("completion_checks")
        if not isinstance(checks, list):
            raise ValueError("each group needs per-finding completion_checks")
        outcomes = {}
        for check in checks:
            if not isinstance(check, dict):
                raise ValueError("completion checks must be objects")
            key = text(check.get("finding_id"), "completion.finding_id")
            if key in outcomes:
                raise ValueError("duplicate completion check")
            outcomes[key] = text(check.get("evidence"), "completion.evidence")
        if set(outcomes) != set(members):
            raise ValueError("completion checks must cover exactly this group's members")
        group["completion_checks"] = [{"finding_id": k, "evidence": outcomes[k]} for k in members]
        dependencies = source.get("depends_on", [])
        if not isinstance(dependencies, list) or any(not isinstance(k, str) for k in dependencies):
            raise ValueError("depends_on must be an array of group IDs")
        if len(set(dependencies)) != len(dependencies):
            raise ValueError("duplicate group dependency")
        group["depends_on"] = dependencies[:]
        if workflow == "construction":
            blocking = any(f["id"] in members and f["disposition"] == "merge-blocker" for f in report["findings"])
            group["proposal"] = prepare_proposal(source.get("proposal"), blocking=blocking)
        assigned.update(members)
        groups[group["id"]] = group
    if assigned != known:
        raise ValueError("resolution groups must cover every retained finding")
    remaining = {key: set(g["depends_on"]) for key, g in groups.items()}
    if any(not dependencies <= groups.keys() for dependencies in remaining.values()):
        raise ValueError("unknown resolution-group dependency")
    while remaining:
        ready = {key for key, dependencies in remaining.items() if not dependencies}
        if not ready:
            raise ValueError("resolution-group dependencies must be acyclic")
        remaining = {key: dependencies - ready for key, dependencies in remaining.items() if key not in ready}
    if workflow == "construction":
        extra["compatibility"] = text(resolution.get("compatibility"), "construction.compatibility")
    report[workflow] = {"status": "complete", "groups": list(groups.values()), **extra}


def prepare(raw: Any) -> dict[str, Any]:
    """Validate the presentation boundary, not the truth/admission of a review."""
    if not isinstance(raw, dict) or raw.get("schema") != SCHEMA:
        raise ValueError(f"expected schema {SCHEMA}")
    identity = raw.get("identity")
    if not isinstance(identity, dict):
        raise ValueError("identity must be the actual campaign identity object")
    identity = dict(identity)
    analysis = identity.get("schema") == "elenctic-construction-identity/v1"
    if analysis:
        if identity.get("mode") != "analysis" or raw.get("workflow") != "construction":
            raise ValueError("construction analysis identities require construction workflow")
        text(identity.get("analysis_id"), "identity.analysis_id")
        for field in ("verdict", "coverage", "selected_scope_coverage", "whole_pr_coverage",
                      "campaign_id", "campaign_context_id", "campaign_seed_thread_id", "campaign_policy_id"):
            if field in identity:
                raise ValueError("comment analysis cannot claim campaign provenance, review coverage or a verdict")
    elif identity.get("schema") != "elenctic-review-identity/v1" or identity.get("mode") != "campaign":
        raise ValueError("identity must be an Elenctic v1 campaign or construction analysis identity")
    for field in ("repo", "base", "candidate", "view"):
        text(identity.get(field), f"identity.{field}")
    if type(identity.get("pr")) is not int or identity["pr"] <= 0:
        raise ValueError("identity.pr must be a positive integer")
    if identity["view"] != "pr-head":
        raise ValueError("identity.view must be pr-head")
    if not analysis:
        text(identity.get("campaign_id"), "identity.campaign_id")
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
    if not analysis and blockers != (identity["verdict"] == "BLOCKED"):
        raise ValueError("BLOCKED requires a retained blocker; blockers require BLOCKED")
    if not analysis and identity["verdict"] == "APPROVE" and identity["selected_scope_coverage"] != "complete":
        raise ValueError("APPROVE requires complete selected-scope coverage")
    result["findings"].sort(key=lambda f: ["merge-blocker", "risk", "concern"].index(f["disposition"]))
    # Stable across regenerations of this campaign; never silently carry checks to a new epoch.
    instance = "analysis_id" if analysis else "campaign_id"
    result["report_key"] = ("elenctic-analysis:" if analysis else "elenctic:") + digest({
        k: identity[k] for k in ("repo", "pr", instance, "base", "candidate", "view")
    })
    prepare_resolution(raw, result)
    return result


def script_data(value: Any) -> str:
    return (canonical(value).replace("&", "\\u0026").replace("<", "\\u003c")
            .replace(">", "\\u003e").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def render(raw: Any, *, previous: dict[str, Any] | None = None) -> tuple[str, dict[str, Any]]:
    report = prepare(raw)
    if previous is not None:
        if previous.get("report_key") != report["report_key"]:
            raise ValueError("cannot reuse finding numbers from another campaign")
        bind_number_history(report, previous)
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
        document, report = render(raw, previous=json.loads(match[1]))
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
