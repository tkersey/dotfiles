#!/usr/bin/env -S uv run python

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FEATURE_KEYWORDS = (
    "add",
    "added",
    "support",
    "enable",
    "enabled",
    "introduce",
    "new",
    "allow",
    "expand",
    "promote",
)

NOTABLE_KEYWORDS = (
    "reliability",
    "reliable",
    "stability",
    "stable",
    "performance",
    "latency",
    "throughput",
    "speed",
    "faster",
    "startup",
    "crash",
    "hang",
    "accessibility",
    "usability",
    "ux",
    "harden",
    "sandbox",
    "security",
)

EXCLUDE_PREFIXES = (
    "chore",
    "docs",
    "test",
    "ci",
    "build",
    "style",
    "refactor",
    "nit",
)

PR_NUMBER_RE = re.compile(r"\(#(\d+)\)")
TYPE_PREFIX_RE = re.compile(r"^\s*([a-zA-Z]+)(?:\([^)]*\))?:")

REQUIRED_SOURCE_FILES: list[str] = [
    "codex-rs/core/src/features.rs",
    "codex-rs/tui/src/chatwidget.rs",
    "codex-rs/core/src/codex.rs",
    "codex-rs/app-server/src/codex_message_processor.rs",
    "codex-rs/app-server-protocol/src/protocol/v2.rs",
    "codex-rs/app-server-protocol/schema/json/v2/ExperimentalFeatureListResponse.json",
    "codex-rs/app-server/README.md",
    "codex-rs/tui/src/tooltips.rs",
    "announcement_tip.toml",
]

REQUIRED_SOURCE_MARKERS: dict[str, str] = {
    "codex-rs/core/src/features.rs": "pub const FEATURES",
    "codex-rs/tui/src/chatwidget.rs": "open_experimental_popup",
    "codex-rs/core/src/codex.rs": "build_model_client_beta_features_header",
    "codex-rs/app-server/src/codex_message_processor.rs": "experimental_feature_list",
    "codex-rs/app-server-protocol/src/protocol/v2.rs": "pub enum ExperimentalFeatureStage",
    "codex-rs/app-server-protocol/schema/json/v2/ExperimentalFeatureListResponse.json": "ExperimentalFeatureStage",
    "codex-rs/app-server/README.md": "`experimentalFeature/list`",
    "codex-rs/tui/src/tooltips.rs": "experimental_announcement",
    "announcement_tip.toml": "[[announcements]]",
}


@dataclass
class CommitRef:
    sha: str
    subject: str
    commit_url: str


@dataclass
class CommitItem:
    kind: str
    title: str
    commit_sha: str
    commit_url: str
    pr_number: int | None
    pr_url: str | None


@dataclass
class SourceFeature:
    key: str
    stage: str
    default_enabled: str
    display_name: str | None
    menu_description: str | None
    announcement: str | None
    source_line: int


def fail(message: str, *, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def run_cmd(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        args,
        capture_output=True,
        text=True,
        check=False,
        cwd=str(cwd) if cwd is not None else None,
    )
    if proc.returncode != 0:
        stderr = proc.stderr.strip()
        stdout = proc.stdout.strip()
        detail = stderr or stdout or "unknown error"
        fail(f"{' '.join(args)} failed: {detail}")
    return proc


def run_gh_json(args: list[str]) -> Any:
    proc = run_cmd(["gh", *args])
    raw = proc.stdout.strip()
    if not raw:
        fail(f"gh {' '.join(args)} returned empty output")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"gh {' '.join(args)} returned invalid JSON: {exc}")


def ensure_gh_auth() -> None:
    proc = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        fail("GitHub CLI is not authenticated. Run `gh auth login` first.")


def parse_repo(repo: str) -> tuple[str, str]:
    parts = repo.split("/")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        fail(f"Repo must be in owner/name form, got: {repo}")
    return parts[0], parts[1]


def default_local_repo_path(repo: str) -> Path:
    owner, name = parse_repo(repo)
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
    return codex_home / "repos" / f"{owner}-{name}"


def get_repo_default_branch(repo: str) -> str:
    data = run_gh_json(["api", f"repos/{repo}"])
    branch = data.get("default_branch")
    if not isinstance(branch, str) or not branch:
        fail(f"Could not resolve default branch for {repo}")
    return branch


def get_latest_stable_release(repo: str) -> dict[str, Any]:
    releases = run_gh_json(["api", f"repos/{repo}/releases?per_page=100"])
    if not isinstance(releases, list):
        fail(f"Unexpected releases response for {repo}")

    for release in releases:
        if not isinstance(release, dict):
            continue
        if release.get("draft"):
            continue
        if release.get("prerelease"):
            continue
        tag = release.get("tag_name")
        if isinstance(tag, str) and tag:
            return release

    fail(f"No stable (non-prerelease) release found for {repo}")


def current_origin_url(local_repo: Path) -> str:
    proc = run_cmd(["git", "-C", str(local_repo), "config", "--get", "remote.origin.url"])
    url = proc.stdout.strip()
    if not url:
        fail(f"Local repo {local_repo} is missing remote.origin.url")
    return url


def ensure_local_repo(repo: str, local_repo: Path) -> Path:
    local_repo = local_repo.expanduser()
    remote_https = f"https://github.com/{repo}.git"

    if not local_repo.exists():
        local_repo.parent.mkdir(parents=True, exist_ok=True)
        run_cmd(["git", "clone", remote_https, str(local_repo)])

    git_dir = local_repo / ".git"
    if not git_dir.exists():
        fail(f"Local path exists but is not a git repo: {local_repo}")

    origin = current_origin_url(local_repo)
    expected_suffixes = (f"{repo}.git", repo)
    if not origin.endswith(expected_suffixes):
        fail(
            f"Local repo remote mismatch at {local_repo}. "
            f"Expected origin ending with {repo}(.git), got: {origin}"
        )

    return local_repo.resolve()


def ensure_checkout_branch(local_repo: Path, branch: str) -> None:
    checkout = subprocess.run(
        ["git", "-C", str(local_repo), "checkout", branch],
        capture_output=True,
        text=True,
        check=False,
    )
    if checkout.returncode == 0:
        return

    track = subprocess.run(
        ["git", "-C", str(local_repo), "checkout", "-b", branch, "--track", f"origin/{branch}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if track.returncode != 0:
        detail = (
            track.stderr.strip()
            or checkout.stderr.strip()
            or track.stdout.strip()
            or checkout.stdout.strip()
            or "unknown error"
        )
        fail(f"Could not checkout branch {branch} in {local_repo}: {detail}")


def sync_local_repo(local_repo: Path, branch: str) -> None:
    run_cmd(["git", "-C", str(local_repo), "fetch", "--tags", "--prune", "origin"])
    ensure_checkout_branch(local_repo, branch)
    run_cmd(["git", "-C", str(local_repo), "pull", "--ff-only", "origin", branch])


def ensure_tag_exists(local_repo: Path, tag: str) -> None:
    proc = subprocess.run(
        ["git", "-C", str(local_repo), "rev-parse", "-q", "--verify", f"refs/tags/{tag}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        fail(f"Stable tag {tag} was not found in local repo {local_repo}. Fetch tags and retry.")


def get_repo_head_sha(local_repo: Path) -> str:
    proc = run_cmd(["git", "-C", str(local_repo), "rev-parse", "HEAD"])
    sha = proc.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        fail(f"Could not resolve valid HEAD SHA for {local_repo}, got: {sha!r}")
    return sha


def list_unreleased_commits(repo: str, local_repo: Path, stable_tag: str, branch: str) -> list[CommitRef]:
    range_spec = f"{stable_tag}..origin/{branch}"
    proc = run_cmd(
        [
            "git",
            "-C",
            str(local_repo),
            "log",
            "--reverse",
            "--format=%H%x1f%s",
            range_spec,
        ]
    )
    commits: list[CommitRef] = []
    for line in proc.stdout.splitlines():
        if not line:
            continue
        parts = line.split("\x1f", 1)
        if len(parts) != 2:
            continue
        sha, subject = parts
        sha = sha.strip()
        subject = subject.strip()
        if not sha or not subject:
            continue
        commits.append(
            CommitRef(
                sha=sha,
                subject=subject,
                commit_url=f"https://github.com/{repo}/commit/{sha}",
            )
        )
    return commits


def extract_pr_number(subject: str) -> int | None:
    match = PR_NUMBER_RE.search(subject)
    if not match:
        return None
    return int(match.group(1))


def get_pr(repo: str, pr_number: int, cache: dict[int, dict[str, Any] | None]) -> dict[str, Any] | None:
    if pr_number in cache:
        return cache[pr_number]

    proc = subprocess.run(
        ["gh", "api", f"repos/{repo}/pulls/{pr_number}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        cache[pr_number] = None
        return None
    try:
        pr = json.loads(proc.stdout)
    except json.JSONDecodeError:
        cache[pr_number] = None
        return None

    if not isinstance(pr, dict):
        cache[pr_number] = None
        return None

    cache[pr_number] = pr
    return pr


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def parse_type_prefix(text: str) -> str | None:
    match = TYPE_PREFIX_RE.match(text)
    if not match:
        return None
    return match.group(1).lower()


def has_keyword(text: str, keyword: str) -> bool:
    return re.search(rf"\b{re.escape(keyword)}\b", text) is not None


def starts_with_excluded_prefix(text: str) -> bool:
    text = text.strip().lower()
    return any(text.startswith(prefix + ":") or text.startswith(prefix + "(") for prefix in EXCLUDE_PREFIXES)


def classify_commit(subject: str, pr_title: str | None) -> str | None:
    text = normalize_text(" ".join(part for part in [subject, pr_title or ""] if part))
    subject_type = parse_type_prefix(subject)
    pr_type = parse_type_prefix(pr_title or "") if pr_title else None

    if not text:
        return None

    feature_hit = (
        subject_type == "feat"
        or pr_type == "feat"
        or has_keyword(text, "new feature")
        or has_keyword(text, "new features")
        or any(has_keyword(text, keyword) for keyword in FEATURE_KEYWORDS)
    )
    notable_hit = any(has_keyword(text, keyword) for keyword in NOTABLE_KEYWORDS)

    if starts_with_excluded_prefix(subject) and not (feature_hit or notable_hit):
        return None

    if subject_type == "fix" or pr_type == "fix":
        return "notable_improvement" if notable_hit else None

    if feature_hit:
        return "feature"
    if notable_hit:
        return "notable_improvement"

    return None


def make_commit_item(repo: str, commit: CommitRef, pr_cache: dict[int, dict[str, Any] | None]) -> CommitItem | None:
    subject = commit.subject
    pr_number = extract_pr_number(subject)
    pr_title: str | None = None
    pr_url: str | None = None

    if pr_number is not None:
        pr = get_pr(repo, pr_number, pr_cache)
        if pr:
            title = pr.get("title")
            url = pr.get("html_url")
            merged_at = pr.get("merged_at")
            if isinstance(title, str) and title.strip():
                pr_title = title.strip()
            if isinstance(url, str) and url:
                pr_url = url
            if merged_at is None:
                # Defensive guard: only report merged work.
                return None

    kind = classify_commit(subject, pr_title)
    if kind is None:
        return None

    title = pr_title or subject
    return CommitItem(
        kind=kind,
        title=title,
        commit_sha=commit.sha[:7],
        commit_url=commit.commit_url,
        pr_number=pr_number,
        pr_url=pr_url,
    )


def ensure_required_source_files(local_repo: Path) -> list[str]:
    missing: list[str] = []
    marker_missing: list[str] = []

    for rel in REQUIRED_SOURCE_FILES:
        path = local_repo / rel
        if not path.exists():
            missing.append(rel)
            continue

        marker = REQUIRED_SOURCE_MARKERS.get(rel)
        if marker:
            text = path.read_text(encoding="utf-8", errors="replace")
            if marker not in text:
                marker_missing.append(f"{rel} (expected marker: {marker})")

    if missing:
        fail(
            "Required source files were not found in local repo: "
            + ", ".join(missing)
            + ". Sync to a compatible revision or update REQUIRED_SOURCE_FILES."
        )
    if marker_missing:
        fail(
            "Required source file markers were not found: "
            + ", ".join(marker_missing)
            + ". Update marker expectations or source mining logic."
        )

    return REQUIRED_SOURCE_FILES.copy()


def find_line_number(text: str, needle: str) -> int | None:
    idx = text.find(needle)
    if idx < 0:
        return None
    return text.count("\n", 0, idx) + 1


def extract_rust_fn_block(text: str, fn_name: str) -> tuple[int, str] | None:
    idx = text.find(f"fn {fn_name}(")
    if idx < 0:
        idx = text.find(f"async fn {fn_name}(")
    if idx < 0:
        return None

    brace_start = text.find("{", idx)
    if brace_start < 0:
        return None

    depth = 0
    end = -1
    for pos in range(brace_start, len(text)):
        char = text[pos]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = pos + 1
                break

    if end < 0:
        return None

    start_line = text.count("\n", 0, idx) + 1
    return start_line, text[idx:end]


def parse_chatwidget_experimental_popup(chatwidget_rs: Path) -> dict[str, Any]:
    rel = "codex-rs/tui/src/chatwidget.rs"
    text = chatwidget_rs.read_text(encoding="utf-8", errors="replace")
    fn_data = extract_rust_fn_block(text, "open_experimental_popup")
    if fn_data is None:
        fail(f"Could not parse open_experimental_popup() from {rel}")
    fn_line, fn_block = fn_data

    required_snippets = (
        "FEATURES",
        "experimental_menu_name()",
        "experimental_menu_description()",
        "enabled: self.config.features.enabled(spec.id)",
    )
    missing = [snippet for snippet in required_snippets if snippet not in fn_block]
    if missing:
        fail(
            f"Could not fully mine {rel}: missing expected snippets in open_experimental_popup(): "
            + ", ".join(missing)
        )

    return {
        "source": f"{rel}:{fn_line}",
        "function": "open_experimental_popup",
        "uses_features_registry": "FEATURES" in fn_block and ".iter()" in fn_block,
        "fields_used": ["name", "description", "enabled"],
        "line_name": find_line_number(text, "experimental_menu_name()"),
        "line_description": find_line_number(text, "experimental_menu_description()"),
        "line_enabled": find_line_number(text, "enabled: self.config.features.enabled(spec.id)"),
    }


def parse_codex_beta_header(codex_rs: Path) -> dict[str, Any]:
    rel = "codex-rs/core/src/codex.rs"
    text = codex_rs.read_text(encoding="utf-8", errors="replace")
    fn_data = extract_rust_fn_block(text, "build_model_client_beta_features_header")
    if fn_data is None:
        fail(f"Could not parse build_model_client_beta_features_header() from {rel}")
    fn_line, fn_block = fn_data

    required_snippets = (
        "experimental_menu_description().is_some()",
        "config.features.enabled(spec.id)",
        ".join(\",\")",
    )
    missing = [snippet for snippet in required_snippets if snippet not in fn_block]
    if missing:
        fail(
            f"Could not fully mine {rel}: missing expected snippets in build_model_client_beta_features_header(): "
            + ", ".join(missing)
        )

    return {
        "source": f"{rel}:{fn_line}",
        "function": "build_model_client_beta_features_header",
        "header_name": "x-codex-beta-features",
        "header_comment_line": find_line_number(text, "`x-codex-beta-features`"),
        "filters_enabled_experimental_features": True,
    }


def parse_app_server_experimental_feature_mapping(processor_rs: Path) -> dict[str, Any]:
    rel = "codex-rs/app-server/src/codex_message_processor.rs"
    text = processor_rs.read_text(encoding="utf-8", errors="replace")
    fn_data = extract_rust_fn_block(text, "experimental_feature_list")
    if fn_data is None:
        fail(f"Could not parse experimental_feature_list() from {rel}")
    fn_line, fn_block = fn_data

    stage_mapping = [
        ("Stage::Experimental", "ApiExperimentalFeatureStage::Beta"),
        ("Stage::UnderDevelopment", "ApiExperimentalFeatureStage::UnderDevelopment"),
        ("Stage::Stable", "ApiExperimentalFeatureStage::Stable"),
        ("Stage::Deprecated", "ApiExperimentalFeatureStage::Deprecated"),
        ("Stage::Removed", "ApiExperimentalFeatureStage::Removed"),
    ]
    missing_pairs = [f"{core} -> {api}" for core, api in stage_mapping if core not in fn_block or api not in fn_block]
    if missing_pairs:
        fail(
            f"Could not fully mine {rel}: missing stage mappings in experimental_feature_list(): "
            + ", ".join(missing_pairs)
        )

    api_fields = []
    for field in (
        "name",
        "stage",
        "display_name",
        "description",
        "announcement",
        "enabled",
        "default_enabled",
    ):
        if f"{field}:" in fn_block or f"{field}," in fn_block:
            api_fields.append(field)
    if len(api_fields) != 7:
        fail(f"Could not fully mine {rel}: missing ApiExperimentalFeature fields in mapping block")

    return {
        "source": f"{rel}:{fn_line}",
        "function": "experimental_feature_list",
        "stage_mapping": [{"core": core, "api": api} for core, api in stage_mapping],
        "api_fields": api_fields,
    }


def parse_protocol_v2_feature_types(v2_rs: Path) -> dict[str, Any]:
    rel = "codex-rs/app-server-protocol/src/protocol/v2.rs"
    text = v2_rs.read_text(encoding="utf-8", errors="replace")

    enum_match = re.search(
        r"pub enum ExperimentalFeatureStage\s*\{(?P<body>.*?)\n\}",
        text,
        flags=re.DOTALL,
    )
    if not enum_match:
        fail(f"Could not parse ExperimentalFeatureStage enum from {rel}")
    enum_body = enum_match.group("body")
    enum_variants = re.findall(r"^\s*([A-Z][A-Za-z0-9_]+),\s*$", enum_body, flags=re.MULTILINE)
    if not enum_variants:
        fail(f"Could not mine enum variants for ExperimentalFeatureStage from {rel}")

    struct_match = re.search(
        r"pub struct ExperimentalFeature\s*\{(?P<body>.*?)\n\}",
        text,
        flags=re.DOTALL,
    )
    if not struct_match:
        fail(f"Could not parse ExperimentalFeature struct from {rel}")
    struct_body = struct_match.group("body")
    fields = re.findall(r"^\s*pub\s+([a-z_]+)\s*:\s*[^,]+,\s*$", struct_body, flags=re.MULTILINE)
    if not fields:
        fail(f"Could not mine fields for ExperimentalFeature from {rel}")

    return {
        "source_enum": f"{rel}:{find_line_number(text, 'pub enum ExperimentalFeatureStage')}",
        "source_struct": f"{rel}:{find_line_number(text, 'pub struct ExperimentalFeature')}",
        "stage_variants": enum_variants,
        "feature_fields": fields,
    }


def parse_protocol_schema(schema_json: Path) -> dict[str, Any]:
    rel = "codex-rs/app-server-protocol/schema/json/v2/ExperimentalFeatureListResponse.json"
    text = schema_json.read_text(encoding="utf-8", errors="replace")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        fail(f"Could not parse JSON schema from {rel}: {exc}")

    definitions = payload.get("definitions")
    if not isinstance(definitions, dict):
        fail(f"Schema {rel} is missing definitions object")

    feature_obj = definitions.get("ExperimentalFeature")
    stage_obj = definitions.get("ExperimentalFeatureStage")
    if not isinstance(feature_obj, dict) or not isinstance(stage_obj, dict):
        fail(f"Schema {rel} is missing ExperimentalFeature or ExperimentalFeatureStage definitions")

    one_of = stage_obj.get("oneOf")
    if not isinstance(one_of, list):
        fail(f"Schema {rel} has unexpected ExperimentalFeatureStage shape")
    stage_values: list[str] = []
    for entry in one_of:
        if not isinstance(entry, dict):
            continue
        enum_vals = entry.get("enum")
        if isinstance(enum_vals, list) and enum_vals and isinstance(enum_vals[0], str):
            stage_values.append(enum_vals[0])

    feature_required = feature_obj.get("required")
    if not isinstance(feature_required, list):
        fail(f"Schema {rel} is missing ExperimentalFeature.required")

    top_level_required = payload.get("required")
    if not isinstance(top_level_required, list):
        fail(f"Schema {rel} is missing top-level required fields")

    return {
        "source": f"{rel}:{find_line_number(text, '\"ExperimentalFeatureStage\"')}",
        "stage_values": stage_values,
        "feature_required_fields": feature_required,
        "response_required_fields": top_level_required,
    }


def parse_app_server_readme(readme_md: Path) -> dict[str, Any]:
    rel = "codex-rs/app-server/README.md"
    lines = readme_md.read_text(encoding="utf-8", errors="replace").splitlines()
    for idx, line in enumerate(lines, start=1):
        if "`experimentalFeature/list`" not in line:
            continue
        details = line.split("—", 1)[1].strip() if "—" in line else line.strip()
        return {
            "source": f"{rel}:{idx}",
            "method": "experimentalFeature/list",
            "details": details,
        }
    fail(f"Could not find `experimentalFeature/list` documentation line in {rel}")


def parse_tooltips_announcement_pipeline(tooltips_rs: Path) -> dict[str, Any]:
    rel = "codex-rs/tui/src/tooltips.rs"
    text = tooltips_rs.read_text(encoding="utf-8", errors="replace")

    url_match = re.search(r'ANNOUNCEMENT_TIP_URL:\s*&str\s*=\s*"([^"]+)";', text)
    if not url_match:
        fail(f"Could not parse ANNOUNCEMENT_TIP_URL from {rel}")
    announcement_url = url_match.group(1)

    exp_fn_data = extract_rust_fn_block(text, "experimental_tooltips")
    if exp_fn_data is None:
        fail(f"Could not parse experimental_tooltips() from {rel}")
    exp_line, exp_block = exp_fn_data
    for snippet in ("FEATURES", "experimental_announcement()"):
        if snippet not in exp_block:
            fail(f"Could not fully mine {rel}: missing {snippet} in experimental_tooltips()")

    fetch_line = find_line_number(text, "announcement::fetch_announcement_tip()")
    if fetch_line is None:
        fail(f"Could not fully mine {rel}: missing announcement::fetch_announcement_tip() call")

    return {
        "source_experimental_tooltips": f"{rel}:{exp_line}",
        "source_announcement_fetch": f"{rel}:{fetch_line}",
        "announcement_url": announcement_url,
        "uses_feature_announcements": True,
    }


def parse_announcement_tip_file(announcement_tip_toml: Path) -> dict[str, Any]:
    rel = "announcement_tip.toml"
    text = announcement_tip_toml.read_text(encoding="utf-8", errors="replace")
    try:
        payload = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        fail(f"Could not parse TOML from {rel}: {exc}")

    announcements = payload.get("announcements")
    if not isinstance(announcements, list):
        fail(f"{rel} is missing [[announcements]] list")

    today = datetime.now(timezone.utc).date()
    active_today = 0
    target_apps: set[str] = set()
    entries: list[dict[str, Any]] = []

    for idx, raw in enumerate(announcements, start=1):
        if not isinstance(raw, dict):
            continue

        content_raw = raw.get("content")
        content = content_raw.strip() if isinstance(content_raw, str) else ""
        from_date = raw.get("from_date") if isinstance(raw.get("from_date"), str) else None
        to_date = raw.get("to_date") if isinstance(raw.get("to_date"), str) else None
        version_regex = raw.get("version_regex") if isinstance(raw.get("version_regex"), str) else None
        target_app = raw.get("target_app") if isinstance(raw.get("target_app"), str) else None
        target_app_effective = (target_app or "cli").lower()
        target_apps.add(target_app_effective)

        in_window = True
        if from_date:
            try:
                from_day = datetime.strptime(from_date, "%Y-%m-%d").date()
                in_window = in_window and (today >= from_day)
            except ValueError:
                in_window = False
        if to_date:
            try:
                to_day = datetime.strptime(to_date, "%Y-%m-%d").date()
                in_window = in_window and (today < to_day)
            except ValueError:
                in_window = False
        if in_window:
            active_today += 1

        content_line = find_line_number(text, f'content = "{content}"') if content else None
        entries.append(
            {
                "index": idx,
                "source": f"{rel}:{content_line or 1}",
                "target_app": target_app_effective,
                "from_date": from_date,
                "to_date": to_date,
                "version_regex": version_regex,
                "content_preview": content[:120],
            }
        )

    return {
        "source": f"{rel}:1",
        "entry_count": len(entries),
        "active_today_count": active_today,
        "target_apps": sorted(target_apps),
        "entries": entries[:10],
    }


def parse_features_registry(features_rs: Path) -> list[SourceFeature]:
    text = features_rs.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    in_registry = False
    blocks: list[tuple[int, str]] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not in_registry:
            if "pub const FEATURES" in line and "FeatureSpec" in line:
                in_registry = True
            i += 1
            continue

        if line.strip() == "];":
            break

        if "FeatureSpec {" in line:
            start_line = i + 1
            brace_depth = line.count("{") - line.count("}")
            chunk = [line]
            i += 1
            while i < len(lines):
                cur = lines[i]
                chunk.append(cur)
                brace_depth += cur.count("{") - cur.count("}")
                if brace_depth <= 0 and cur.strip().startswith("},"):
                    break
                i += 1
            blocks.append((start_line, "\n".join(chunk)))

        i += 1

    if not blocks:
        fail(f"Could not parse FeatureSpec registry from {features_rs}")

    features: list[SourceFeature] = []
    for start_line, block in blocks:
        key_match = re.search(r'key:\s*"([^"]+)"', block)
        if not key_match:
            continue
        key = key_match.group(1)

        default_match = re.search(r"default_enabled:\s*([^,\n]+)", block)
        default_enabled = default_match.group(1).strip() if default_match else "unknown"

        has_exp = "Stage::Experimental" in block
        has_under = "Stage::UnderDevelopment" in block
        has_stable = "Stage::Stable" in block
        has_deprecated = "Stage::Deprecated" in block
        has_removed = "Stage::Removed" in block

        stage = "unknown"
        if has_exp and has_under:
            stage = "conditional(beta|underDevelopment)"
        elif has_exp:
            stage = "beta"
        elif has_under:
            stage = "underDevelopment"
        elif has_stable:
            stage = "stable"
        elif has_deprecated:
            stage = "deprecated"
        elif has_removed:
            stage = "removed"

        display_name = None
        menu_description = None
        announcement = None

        name_match = re.search(r'name:\s*"([^"]+)"', block)
        if name_match:
            display_name = name_match.group(1)

        desc_match = re.search(r'menu_description:\s*"([^"]+)"', block)
        if desc_match:
            menu_description = desc_match.group(1)

        ann_match = re.search(r'announcement:\s*"([^"]+)"', block)
        if ann_match:
            announcement = ann_match.group(1)

        features.append(
            SourceFeature(
                key=key,
                stage=stage,
                default_enabled=default_enabled,
                display_name=display_name,
                menu_description=menu_description,
                announcement=announcement,
                source_line=start_line,
            )
        )

    return features


def select_primary_features(features: list[SourceFeature]) -> tuple[list[SourceFeature], list[SourceFeature]]:
    beta: list[SourceFeature] = []
    under_dev: list[SourceFeature] = []

    for feat in features:
        if feat.stage == "beta" or feat.stage == "conditional(beta|underDevelopment)":
            beta.append(feat)
        if feat.stage == "underDevelopment" or feat.stage == "conditional(beta|underDevelopment)":
            under_dev.append(feat)

    return beta, under_dev


def summarize_feature_stage_counts(features: list[SourceFeature]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for feat in features:
        counts[feat.stage] = counts.get(feat.stage, 0) + 1
    return counts


def mine_source_supporting_evidence(local_repo: Path, all_source_features: list[SourceFeature]) -> dict[str, Any]:
    return {
        "features_registry": {
            "source": "codex-rs/core/src/features.rs",
            "total_feature_specs": len(all_source_features),
            "stage_counts": summarize_feature_stage_counts(all_source_features),
        },
        "chatwidget_experimental_popup": parse_chatwidget_experimental_popup(
            local_repo / "codex-rs/tui/src/chatwidget.rs"
        ),
        "beta_header": parse_codex_beta_header(local_repo / "codex-rs/core/src/codex.rs"),
        "app_server_feature_mapping": parse_app_server_experimental_feature_mapping(
            local_repo / "codex-rs/app-server/src/codex_message_processor.rs"
        ),
        "protocol_v2": parse_protocol_v2_feature_types(
            local_repo / "codex-rs/app-server-protocol/src/protocol/v2.rs"
        ),
        "protocol_schema_v2": parse_protocol_schema(
            local_repo
            / "codex-rs/app-server-protocol/schema/json/v2/ExperimentalFeatureListResponse.json"
        ),
        "app_server_readme": parse_app_server_readme(local_repo / "codex-rs/app-server/README.md"),
        "tooltips_announcement_pipeline": parse_tooltips_announcement_pipeline(
            local_repo / "codex-rs/tui/src/tooltips.rs"
        ),
        "announcement_tip_file": parse_announcement_tip_file(local_repo / "announcement_tip.toml"),
    }


def build_markdown(
    *,
    repo: str,
    local_repo: Path,
    as_of_utc: str,
    stable_tag: str,
    stable_release_url: str | None,
    branch: str,
    compare_url: str,
    analyzed_commit_sha: str,
    total_commits: int,
    source_files_mined: list[str],
    beta_features: list[SourceFeature],
    under_dev_features: list[SourceFeature],
    supporting_evidence: dict[str, Any],
    commit_items: list[CommitItem],
) -> str:
    commit_feature_items = [item for item in commit_items if item.kind == "feature"]
    commit_notable_items = [item for item in commit_items if item.kind == "notable_improvement"]

    lines: list[str] = []
    lines.append(f"# Upcoming unreleased changes for `{repo}`")
    lines.append("")
    lines.append(f"- As of (UTC): {as_of_utc}")
    lines.append(f"- Local repo: `{local_repo}`")
    lines.append(f"- Stable baseline: `{stable_tag}`")
    if stable_release_url:
        lines.append(f"- Stable release: {stable_release_url}")
    lines.append(f"- Compared against: `{branch}`")
    lines.append(f"- Analyzed commit: `{analyzed_commit_sha}`")
    lines.append(f"- Compare range: {compare_url}")
    lines.append(f"- Unreleased commits in range: {total_commits}")
    lines.append("")

    lines.append("## Source Files Mined (primary)")
    for rel in source_files_mined:
        lines.append(f"- `{rel}`")
    lines.append("")

    lines.append("## Source-derived upcoming features (primary)")

    lines.append("### Beta / experimental")
    if not beta_features:
        lines.append("None found.")
    else:
        for idx, feat in enumerate(beta_features, start=1):
            label = f"`{feat.key}`"
            if feat.display_name:
                label += f" ({feat.display_name})"
            lines.append(f"{idx}. {label} [default_enabled: {feat.default_enabled}]")
            if feat.menu_description:
                lines.append(f"   - Summary: {feat.menu_description}")
            if feat.announcement:
                lines.append(f"   - Announcement: {feat.announcement}")
            lines.append(f"   - Evidence: `codex-rs/core/src/features.rs:{feat.source_line}`")
    lines.append("")

    lines.append("### Under development")
    if not under_dev_features:
        lines.append("None found.")
    else:
        for idx, feat in enumerate(under_dev_features, start=1):
            lines.append(
                f"{idx}. `{feat.key}` [stage: {feat.stage}; default_enabled: {feat.default_enabled}]"
            )
            if feat.menu_description:
                lines.append(f"   - Summary: {feat.menu_description}")
            lines.append(f"   - Evidence: `codex-rs/core/src/features.rs:{feat.source_line}`")
    lines.append("")

    lines.append("## Cross-file source evidence (primary)")
    registry = supporting_evidence.get("features_registry", {})
    stage_counts = registry.get("stage_counts", {})
    counts_text = ", ".join(f"{k}={v}" for k, v in sorted(stage_counts.items()))
    lines.append(
        "- `codex-rs/core/src/features.rs`: "
        f"{registry.get('total_feature_specs', 0)} feature specs parsed"
        + (f" ({counts_text})" if counts_text else "")
    )

    popup = supporting_evidence.get("chatwidget_experimental_popup", {})
    lines.append(
        "- `codex-rs/tui/src/chatwidget.rs`: `/experimental` popup is built from `FEATURES` using "
        f"{', '.join(popup.get('fields_used', []))} fields ({popup.get('source')})"
    )

    header = supporting_evidence.get("beta_header", {})
    lines.append(
        "- `codex-rs/core/src/codex.rs`: "
        f"`{header.get('header_name', 'x-codex-beta-features')}` header derives enabled experimental keys ({header.get('source')})"
    )

    mapping = supporting_evidence.get("app_server_feature_mapping", {})
    lines.append(
        "- `codex-rs/app-server/src/codex_message_processor.rs`: `experimental_feature_list` maps core stages to API stages "
        f"({mapping.get('source')})"
    )

    protocol = supporting_evidence.get("protocol_v2", {})
    lines.append(
        "- `codex-rs/app-server-protocol/src/protocol/v2.rs`: stage enum values = "
        f"{', '.join(protocol.get('stage_variants', []))}"
    )

    schema = supporting_evidence.get("protocol_schema_v2", {})
    lines.append(
        "- `codex-rs/app-server-protocol/schema/json/v2/ExperimentalFeatureListResponse.json`: schema stage values = "
        f"{', '.join(schema.get('stage_values', []))}"
    )

    readme = supporting_evidence.get("app_server_readme", {})
    lines.append(
        "- `codex-rs/app-server/README.md`: method docs include `experimentalFeature/list` semantics "
        f"({readme.get('source')})"
    )

    tooltips = supporting_evidence.get("tooltips_announcement_pipeline", {})
    lines.append(
        "- `codex-rs/tui/src/tooltips.rs`: combines feature announcements with remote `announcement_tip.toml` "
        f"({tooltips.get('source_experimental_tooltips')})"
    )

    announcements = supporting_evidence.get("announcement_tip_file", {})
    lines.append(
        "- `announcement_tip.toml`: "
        f"{announcements.get('entry_count', 0)} announcements parsed; active today={announcements.get('active_today_count', 0)}"
    )
    lines.append("")

    lines.append("## Commit-derived items (secondary)")
    lines.append(
        f"- Included items: {len(commit_items)} (features: {len(commit_feature_items)}, notable improvements: {len(commit_notable_items)})"
    )
    lines.append("")

    def append_commit_section(title: str, items: list[CommitItem]) -> None:
        lines.append(f"### {title}")
        if not items:
            lines.append("None found.")
            lines.append("")
            return

        for index, item in enumerate(items, start=1):
            primary = item.pr_url or item.commit_url
            lines.append(f"{index}. [{item.title}]({primary})")
            if item.pr_number is not None and item.pr_url:
                lines.append(
                    f"   - Evidence: PR #{item.pr_number} ({item.pr_url}); commit `{item.commit_sha}` ({item.commit_url})"
                )
            else:
                lines.append(f"   - Evidence: commit `{item.commit_sha}` ({item.commit_url})")
        lines.append("")

    append_commit_section("Features", commit_feature_items)
    append_commit_section("Notable Improvements", commit_notable_items)

    return "\n".join(lines).rstrip() + "\n"


def build_json(
    *,
    repo: str,
    local_repo: Path,
    as_of_utc: str,
    stable_tag: str,
    compare_url: str,
    analyzed_commit_sha: str,
    source_files_mined: list[str],
    beta_features: list[SourceFeature],
    under_dev_features: list[SourceFeature],
    supporting_evidence: dict[str, Any],
    commit_items: list[CommitItem],
) -> dict[str, Any]:
    return {
        "as_of_utc": as_of_utc,
        "repo": repo,
        "local_repo": str(local_repo),
        "analyzed_commit_sha": analyzed_commit_sha,
        "analyzed_commit_short": analyzed_commit_sha[:12],
        "stable_tag": stable_tag,
        "compare_url": compare_url,
        "source_files_mined": source_files_mined,
        "source_primary": {
            "beta_features": [
                {
                    "key": feat.key,
                    "stage": feat.stage,
                    "default_enabled": feat.default_enabled,
                    "display_name": feat.display_name,
                    "menu_description": feat.menu_description,
                    "announcement": feat.announcement,
                    "source": f"codex-rs/core/src/features.rs:{feat.source_line}",
                }
                for feat in beta_features
            ],
            "under_development_features": [
                {
                    "key": feat.key,
                    "stage": feat.stage,
                    "default_enabled": feat.default_enabled,
                    "display_name": feat.display_name,
                    "menu_description": feat.menu_description,
                    "announcement": feat.announcement,
                    "source": f"codex-rs/core/src/features.rs:{feat.source_line}",
                }
                for feat in under_dev_features
            ],
            "supporting_evidence": supporting_evidence,
        },
        # Backward-compatible commit output retained as secondary evidence.
        "items": [
            {
                "kind": item.kind,
                "title": item.title,
                "commit_sha": item.commit_sha,
                "commit_url": item.commit_url,
                "pr_number": item.pr_number,
                "pr_url": item.pr_url,
            }
            for item in commit_items
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize upcoming unreleased features/notable improvements "
            "for a GitHub repo since the latest stable release."
        )
    )
    parser.add_argument(
        "--repo",
        default="openai/codex",
        help="GitHub repo in owner/name form (default: openai/codex)",
    )
    parser.add_argument(
        "--base-tag",
        default=None,
        help="Optional stable baseline tag override (default: latest non-prerelease release)",
    )
    parser.add_argument(
        "--local-repo",
        default=None,
        help="Durable local clone path (default: $CODEX_HOME/repos/<owner>-<repo> or ~/.codex/repos/<owner>-<repo>)",
    )
    parser.add_argument(
        "--output",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format (default: markdown)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_gh_auth()

    repo = args.repo
    branch = get_repo_default_branch(repo)
    local_repo = Path(args.local_repo).expanduser() if args.local_repo else default_local_repo_path(repo)
    local_repo = ensure_local_repo(repo, local_repo)
    sync_local_repo(local_repo, branch)
    analyzed_commit_sha = get_repo_head_sha(local_repo)

    stable_release_url: str | None = None
    if args.base_tag:
        stable_tag = args.base_tag
    else:
        stable_release = get_latest_stable_release(repo)
        tag = stable_release.get("tag_name")
        if not isinstance(tag, str) or not tag:
            fail(f"Could not resolve stable release tag for {repo}")
        stable_tag = tag
        stable_release_url_raw = stable_release.get("html_url")
        if isinstance(stable_release_url_raw, str) and stable_release_url_raw:
            stable_release_url = stable_release_url_raw

    ensure_tag_exists(local_repo, stable_tag)

    # Primary feature mining from source files.
    source_files_mined = ensure_required_source_files(local_repo)
    features_registry = local_repo / "codex-rs/core/src/features.rs"
    all_source_features = parse_features_registry(features_registry)
    beta_features, under_dev_features = select_primary_features(all_source_features)
    supporting_evidence = mine_source_supporting_evidence(local_repo, all_source_features)

    # Secondary evidence from commit history.
    commits = list_unreleased_commits(repo, local_repo, stable_tag, branch)
    pr_cache: dict[int, dict[str, Any] | None] = {}
    commit_items: list[CommitItem] = []
    for commit in commits:
        item = make_commit_item(repo, commit, pr_cache)
        if item is not None:
            commit_items.append(item)

    compare_url = f"https://github.com/{repo}/compare/{stable_tag}...{branch}"
    as_of_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    if args.output == "json":
        payload = build_json(
            repo=repo,
            local_repo=local_repo,
            as_of_utc=as_of_utc,
            stable_tag=stable_tag,
            compare_url=compare_url,
            analyzed_commit_sha=analyzed_commit_sha,
            source_files_mined=source_files_mined,
            beta_features=beta_features,
            under_dev_features=under_dev_features,
            supporting_evidence=supporting_evidence,
            commit_items=commit_items,
        )
        print(json.dumps(payload, indent=2, sort_keys=False))
        return

    markdown = build_markdown(
        repo=repo,
        local_repo=local_repo,
        as_of_utc=as_of_utc,
        stable_tag=stable_tag,
        stable_release_url=stable_release_url,
        branch=branch,
        compare_url=compare_url,
        analyzed_commit_sha=analyzed_commit_sha,
        total_commits=len(commits),
        source_files_mined=source_files_mined,
        beta_features=beta_features,
        under_dev_features=under_dev_features,
        supporting_evidence=supporting_evidence,
        commit_items=commit_items,
    )
    print(markdown, end="")


if __name__ == "__main__":
    main()
