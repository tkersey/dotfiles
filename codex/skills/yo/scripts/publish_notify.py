#!/usr/bin/env -S uv run python

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_PARTIAL = 3

GH_API_PAGE_SIZE = 100
TITLE_LIMIT = 80
PREVIEW_LIMIT = 140
SLUG_LIMIT = 48


class YoError(Exception):
    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason
        self.message = message


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish content to a secret gist and notify via macOS.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--text", help="Inline content to publish.")
    source.add_argument("--file", help="Path to content to publish.")
    parser.add_argument("--title", help="Optional notification title override.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve output without side effects.")
    return parser.parse_args()


def gh_bin() -> str:
    return os.environ.get("YO_GH_BIN", "gh")


def notifier_bin() -> str:
    return os.environ.get("YO_TERMINAL_NOTIFIER_BIN", "terminal-notifier")


def emit_result(payload: dict[str, Any], exit_code: int) -> None:
    json.dump(payload, sys.stdout, sort_keys=True)
    sys.stdout.write("\n")
    raise SystemExit(exit_code)


def run_cmd(args: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
    )


def load_source(args: argparse.Namespace) -> tuple[str, str, str | None]:
    if args.text is not None:
        return args.text, "inline", None

    path = Path(args.file).expanduser()
    try:
        body = path.read_text()
    except OSError as exc:
        raise YoError("source_unreadable", f"Could not read source file: {exc}") from exc
    return body, path.name, path.stem


def normalize_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def strip_preview_markup(line: str) -> str:
    cleaned = re.sub(r"^\s*[#>*+\-]+\s*", "", line)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    return normalize_spaces(cleaned)


def normalize_for_compare(value: str) -> str:
    return normalize_spaces(value).casefold()


def first_non_empty_line(text: str) -> str | None:
    for raw in text.splitlines():
        stripped = raw.strip()
        if stripped:
            return stripped
    return None


def first_markdown_h1(text: str) -> str | None:
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            return normalize_spaces(stripped[2:])
        return None
    return None


def infer_title(explicit: str | None, body: str, fallback_stem: str | None) -> str:
    candidates = [
        explicit,
        first_markdown_h1(body),
        strip_preview_markup(first_non_empty_line(body) or ""),
        fallback_stem,
        "YO",
    ]
    for candidate in candidates:
        if candidate:
            title = normalize_spaces(candidate)
            if title:
                return title[:TITLE_LIMIT]
    return "YO"


def derive_preview(body: str) -> str:
    lines: list[str] = []
    for raw in body.splitlines():
        stripped = strip_preview_markup(raw)
        if stripped:
            lines.append(stripped)
        if len(lines) == 2:
            break
    if not lines:
        return "gist ready"

    preview = "\n".join(lines)
    if len(preview) <= PREVIEW_LIMIT:
        return preview

    trimmed = preview[: PREVIEW_LIMIT - 1].rstrip()
    if "\n" in trimmed and trimmed.endswith("\n"):
        trimmed = trimmed.rstrip()
    return f"{trimmed}…"


def source_label(source_name: str) -> str:
    return "inline" if source_name == "inline" else source_name


def render_markdown(title: str, repo_label: str, timestamp: str, src_label: str, body: str) -> str:
    metadata = (
        f"- repo: {repo_label}\n"
        f"- created_at_utc: {timestamp}\n"
        f"- source: {src_label}\n"
        "\n---\n"
    )
    normalized_title = normalize_for_compare(title)
    lines = body.splitlines()

    for index, raw in enumerate(lines):
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("# ") and normalize_for_compare(stripped[2:]) == normalized_title:
            before = "\n".join(lines[: index + 1]).rstrip()
            after = "\n".join(lines[index + 1 :]).lstrip("\n")
            rendered = f"{before}\n\n{metadata}"
            if after:
                rendered += f"\n{after}"
            return rendered.rstrip() + "\n"
        break

    rendered = f"# {title}\n\n{metadata}\n{body.rstrip()}\n"
    return rendered


def run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return run_cmd(["git", *args])


def parse_repo_label(remote_url: str) -> str | None:
    url = remote_url.strip()
    if not url:
        return None

    scp_match = re.match(r"^[^@]+@[^:]+:(.+)$", url)
    if scp_match:
        path = scp_match.group(1)
    else:
        stripped = re.sub(r"^[a-z]+://", "", url)
        slash = stripped.find("/")
        path = stripped[slash + 1 :] if slash >= 0 else ""
    path = path.strip("/").removesuffix(".git")
    parts = [part for part in path.split("/") if part]
    if len(parts) < 2:
        return None
    return f"{parts[-2]}/{parts[-1]}"


def repo_label() -> str:
    inside = run_git(["rev-parse", "--is-inside-work-tree"])
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return "no-repo"

    remotes_proc = run_git(["remote"])
    if remotes_proc.returncode != 0:
        return "no-repo"

    remotes = [line.strip() for line in remotes_proc.stdout.splitlines() if line.strip()]
    if not remotes:
        return "no-repo"

    remote_names = ["origin"] + [name for name in remotes if name != "origin"]
    for name in remote_names:
        proc = run_git(["remote", "get-url", name])
        if proc.returncode != 0:
            continue
        label = parse_repo_label(proc.stdout)
        if label:
            return label
    return "no-repo"


def gh_auth_ok() -> bool:
    proc = run_cmd([gh_bin(), "auth", "status", "--json", "hosts"])
    if proc.returncode != 0:
        return False
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return False

    hosts = payload.get("hosts", {})
    github_hosts = hosts.get("github.com")
    if not isinstance(github_hosts, list):
        return False

    active = None
    for host in github_hosts:
        if isinstance(host, dict) and host.get("active") is True:
            active = host
            break
    if active is None and github_hosts:
        first = github_hosts[0]
        active = first if isinstance(first, dict) else None
    if not isinstance(active, dict):
        return False
    if active.get("state") != "success":
        return False

    scopes = str(active.get("scopes", ""))
    scope_list = {item.strip() for item in scopes.split(",") if item.strip()}
    return "gist" in scope_list


def gh_json(args: list[str]) -> Any:
    proc = run_cmd([gh_bin(), *args])
    if proc.returncode != 0:
        stderr = proc.stderr.strip() or proc.stdout.strip()
        raise YoError("gh_api_failed", stderr or "GitHub CLI command failed")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise YoError("gh_api_failed", f"GitHub CLI returned invalid JSON: {exc}") from exc


def list_matching_gists(description: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    page = 1
    while True:
        page_payload = gh_json([ "api", f"/gists?per_page={GH_API_PAGE_SIZE}&page={page}" ])
        if not isinstance(page_payload, list):
            raise YoError("gh_api_failed", "Unexpected gist list response shape")
        for item in page_payload:
            if not isinstance(item, dict):
                continue
            if item.get("public") is not False:
                continue
            if item.get("description") != description:
                continue
            matches.append(item)
        if len(page_payload) < GH_API_PAGE_SIZE:
            break
        page += 1
    matches.sort(key=lambda item: str(item.get("updated_at", "")), reverse=True)
    return matches


def extract_gist_files(gist: dict[str, Any]) -> set[str]:
    files = gist.get("files", {})
    if not isinstance(files, dict):
        return set()
    return {name for name in files.keys() if isinstance(name, str)}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    if not slug:
        return "yo"
    return slug[:SLUG_LIMIT].rstrip("-") or "yo"


def make_file_name(title: str, existing_files: set[str]) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = slugify(title)
    base = f"{timestamp}-{slug}"
    candidate = f"{base}.md"
    counter = 2
    while candidate in existing_files:
        candidate = f"{base}-{counter}.md"
        counter += 1
    return candidate


def parse_gist_url(raw: str) -> tuple[str, str]:
    url = raw.strip().splitlines()[-1].strip()
    gist_id = url.rstrip("/").split("/")[-1]
    if not gist_id:
        raise YoError("gist_mutation_failed", "Could not parse gist URL from gh output")
    return gist_id, url


def gist_detail(gist_id: str) -> dict[str, Any]:
    payload = gh_json(["api", f"/gists/{gist_id}"])
    if not isinstance(payload, dict):
        raise YoError("gh_api_failed", "Unexpected gist detail response shape")
    return payload


def publish_markdown(description: str, file_name: str, markdown: str) -> tuple[str, str, str, list[str]]:
    warnings: list[str] = []
    matches = list_matching_gists(description)
    chosen = matches[0] if matches else None
    if len(matches) > 1:
        warnings.append("multiple_matching_gists")

    with tempfile.TemporaryDirectory(prefix="yo-gist-") as tmpdir:
        temp_path = Path(tmpdir) / file_name
        temp_path.write_text(markdown)

        if chosen is None:
            proc = run_cmd([gh_bin(), "gist", "create", str(temp_path), "-d", description])
            if proc.returncode != 0:
                stderr = proc.stderr.strip() or proc.stdout.strip()
                raise YoError("gist_mutation_failed", stderr or "gh gist create failed")
            gist_id, gist_url = parse_gist_url(proc.stdout)
            return gist_id, gist_url, "created", warnings

        gist_id = str(chosen.get("id", "")).strip()
        if not gist_id:
            raise YoError("gist_mutation_failed", "Matching gist is missing an id")
        proc = run_cmd([gh_bin(), "gist", "edit", gist_id, "--add", str(temp_path)])
        if proc.returncode != 0:
            stderr = proc.stderr.strip() or proc.stdout.strip()
            raise YoError("gist_mutation_failed", stderr or "gh gist edit --add failed")
        detail = gist_detail(gist_id)
        gist_url = str(detail.get("html_url", "")).strip()
        if not gist_url:
            raise YoError("gist_mutation_failed", "Updated gist is missing html_url")
        return gist_id, gist_url, "reused", warnings


def notifier_available() -> bool:
    return shutil.which(notifier_bin()) is not None


def send_notification(title: str, subtitle: str, body: str, gist_url: str) -> str:
    args = [
        notifier_bin(),
        "-title",
        title,
        "-subtitle",
        subtitle,
        "-message",
        body,
        "-open",
        gist_url,
    ]
    first = run_cmd(args)
    if first.returncode == 0:
        return "sent"
    second = run_cmd(args)
    if second.returncode == 0:
        return "retried_sent"
    return "failed"


def build_base_payload(repo_label_value: str, title: str, preview: str, file_name: str, reason: str | None = None) -> dict[str, Any]:
    return {
        "bucket_action": "skipped",
        "file_name": file_name,
        "gist_id": None,
        "gist_url": None,
        "notification_status": "skipped",
        "preview": preview,
        "reason": reason,
        "repo_label": repo_label_value,
        "status": "failed",
        "title": title,
        "warnings": [],
    }


def main() -> None:
    args = parse_args()
    body, src_label, fallback_stem = load_source(args)

    if sys.platform != "darwin":
        title = infer_title(args.title, body, fallback_stem)
        preview = derive_preview(body)
        payload = build_base_payload("no-repo", title, preview, "", reason="non_macos")
        emit_result(payload, EXIT_FAILED)

    repo_label_value = repo_label()
    title = infer_title(args.title, body, fallback_stem)
    preview = derive_preview(body)
    description = f"yo repo={repo_label_value}"

    existing_matches: list[dict[str, Any]] = []
    warnings: list[str] = []
    existing_files: set[str] = set()
    if gh_auth_ok():
        existing_matches = list_matching_gists(description)
        if len(existing_matches) > 1:
            warnings.append("multiple_matching_gists")
        if existing_matches:
            existing_files = extract_gist_files(existing_matches[0])

    file_name = make_file_name(title, existing_files)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    markdown = render_markdown(title, repo_label_value, timestamp, source_label(src_label), body)

    if args.dry_run:
        emit_result(
            {
                "bucket_action": "planned",
                "file_name": file_name,
                "gist_description": description,
                "gist_id": None,
                "gist_url": None,
                "notification_status": "planned",
                "preview": preview,
                "reason": None,
                "repo_label": repo_label_value,
                "status": "dry_run",
                "title": title,
                "warnings": warnings,
            },
            EXIT_OK,
        )

    if not gh_auth_ok():
        emit_result(
            {
                "bucket_action": "skipped",
                "file_name": file_name,
                "gist_id": None,
                "gist_url": None,
                "notification_status": "skipped",
                "preview": preview,
                "reason": "gh_unavailable",
                "repo_label": repo_label_value,
                "status": "dropped",
                "title": title,
                "warnings": warnings,
            },
            EXIT_OK,
        )

    if not notifier_available():
        payload = build_base_payload(repo_label_value, title, preview, file_name, reason="terminal_notifier_missing")
        emit_result(payload, EXIT_FAILED)

    try:
        gist_id, gist_url, bucket_action, publish_warnings = publish_markdown(description, file_name, markdown)
    except YoError as exc:
        payload = build_base_payload(repo_label_value, title, preview, file_name, reason=exc.reason)
        emit_result(payload, EXIT_FAILED)

    all_warnings = warnings + [item for item in publish_warnings if item not in warnings]
    notification_body = f"{preview}\n{gist_url}"
    notification_status = send_notification(title, repo_label_value, notification_body, gist_url)
    payload = {
        "bucket_action": bucket_action,
        "file_name": file_name,
        "gist_id": gist_id,
        "gist_url": gist_url,
        "notification_status": notification_status,
        "preview": preview,
        "reason": None,
        "repo_label": repo_label_value,
        "status": "delivered",
        "title": title,
        "warnings": all_warnings,
    }
    if notification_status == "failed":
        payload["status"] = "partial"
        payload["reason"] = "notification_failed"
        emit_result(payload, EXIT_PARTIAL)

    emit_result(payload, EXIT_OK)


if __name__ == "__main__":
    try:
        main()
    except YoError as exc:
        emit_result(
            {
                "bucket_action": "skipped",
                "file_name": "",
                "gist_id": None,
                "gist_url": None,
                "notification_status": "skipped",
                "preview": "",
                "reason": exc.reason,
                "repo_label": "no-repo",
                "status": "failed",
                "title": "YO",
                "warnings": [],
            },
            EXIT_FAILED,
        )
