#!/usr/bin/env -S uv run python
"""Refresh Deckset docs and gist examples with cache fallback.

Also generates a small Deckset markdown cheatsheet (`references/deckset-cheatsheet.md`)
intended for LLM consumption.

Features:
- GitHub auth (avoids rate limits): set `GH_TOKEN` or `GITHUB_TOKEN`
- Conditional requests: uses ETag/Last-Modified from `references/refresh-metadata.json`
- Optional TTL: `--max-age-sec N` skips network refresh when the last refresh is recent
- Avoids leaving `__pycache__` artifacts in skill directories
"""

from __future__ import annotations

import sys

# Avoid leaving __pycache__ artifacts in skill directories.
sys.dont_write_bytecode = True

import argparse
import html
import json
import os
import re
import uuid
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_DOCS_URL = "https://docs.deckset.com/markdownDocumentation.html"
DEFAULT_GIST_ID = "69c36bcf40e23f7ef5c82a9c63983a13"

DOCS_CACHE_FILENAME = "deckset-markdownDocumentation.html"
CHEATSHEET_FILENAME = "deckset-cheatsheet.md"
METADATA_FILENAME = "refresh-metadata.json"

USER_AGENT = "deckset-skill-refresh/1.1"
GITHUB_ACCEPT = "application/vnd.github+json"
GITHUB_TOKEN_ENV_VARS = ("GH_TOKEN", "GITHUB_TOKEN")


@dataclass
class FetchResult:
    source: str
    message: str
    ok: bool


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json_dict(path: Path) -> dict[str, Any]:
    try:
        if not path.exists():
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


def parse_iso_datetime(value: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(value)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:  # noqa: BLE001
        return None


def within_max_age(prior: dict[str, Any], max_age_sec: int) -> bool:
    if max_age_sec <= 0:
        return False
    refreshed_at = prior.get("refreshed_at")
    if not isinstance(refreshed_at, str):
        return False
    prior_dt = parse_iso_datetime(refreshed_at)
    if prior_dt is None:
        return False
    age = (
        datetime.now(timezone.utc) - prior_dt.astimezone(timezone.utc)
    ).total_seconds()
    return 0 <= age <= max_age_sec


def header_get(headers: dict[str, str], name: str) -> str | None:
    needle = name.lower()
    for k, v in headers.items():
        if k.lower() == needle:
            return v
    return None


def http_get(
    url: str, timeout_sec: int, headers: dict[str, str]
) -> tuple[int, bytes, dict[str, str]]:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:  # nosec B310
            status = int(getattr(resp, "status", 200))
            body = resp.read()
            resp_headers = {k: v for k, v in resp.headers.items()}
            return status, body, resp_headers
    except urllib.error.HTTPError as exc:
        if exc.code == 304:
            resp_headers = {k: v for k, v in exc.headers.items()}
            return 304, b"", resp_headers
        raise


def sanitize_filename(name: str) -> str:
    base = name.strip().replace("\\", "/").split("/")[-1]
    base = re.sub(r"[^A-Za-z0-9._-]", "-", base)
    return base or "example.md"


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.tmp.{uuid.uuid4().hex}")
    try:
        tmp_path.write_bytes(data)
        os.replace(tmp_path, path)
    finally:
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except Exception:  # noqa: BLE001
            pass


def nonempty_file(path: Path) -> bool:
    return path.exists() and path.is_file() and path.stat().st_size > 0


def has_examples_cache(examples_dir: Path) -> bool:
    if not examples_dir.exists() or not examples_dir.is_dir():
        return False
    for p in examples_dir.iterdir():
        if p.is_file() and p.name != "_gist-index.json":
            return True
    return False


def get_github_token() -> str | None:
    for key in GITHUB_TOKEN_ENV_VARS:
        value = os.environ.get(key)
        if value:
            return value
    return None


def make_headers(
    *,
    accept: str | None = None,
    token: str | None = None,
    conditional: dict[str, str] | None = None,
) -> dict[str, str]:
    headers: dict[str, str] = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if conditional:
        headers.update(conditional)
    return headers


def fetch_docs(
    docs_url: str,
    docs_path: Path,
    timeout_sec: int,
    errors: list[str],
    prior: dict[str, Any],
    max_age_sec: int,
) -> tuple[FetchResult, dict[str, Any]]:
    meta: dict[str, Any] = {
        "http_status": None,
        "etag": prior.get("docs_etag")
        if isinstance(prior.get("docs_etag"), str)
        else None,
        "last_modified": (
            prior.get("docs_last_modified")
            if isinstance(prior.get("docs_last_modified"), str)
            else None
        ),
    }

    if within_max_age(prior, max_age_sec) and nonempty_file(docs_path):
        return (
            FetchResult(
                source="cache_ttl",
                message=f"skipped docs fetch (max_age_sec={max_age_sec})",
                ok=True,
            ),
            meta,
        )

    conditional: dict[str, str] = {}
    if isinstance(meta["etag"], str):
        conditional["If-None-Match"] = meta["etag"]
    if isinstance(meta["last_modified"], str):
        conditional["If-Modified-Since"] = meta["last_modified"]

    try:
        status, body, hdrs = http_get(
            docs_url, timeout_sec, make_headers(conditional=conditional)
        )
        meta["http_status"] = status
        meta["etag"] = header_get(hdrs, "ETag") or meta["etag"]
        meta["last_modified"] = (
            header_get(hdrs, "Last-Modified") or meta["last_modified"]
        )

        if status == 304:
            if nonempty_file(docs_path):
                return (
                    FetchResult(
                        source="cache_not_modified",
                        message="docs not modified (304)",
                        ok=True,
                    ),
                    meta,
                )
            errors.append("docs returned 304 but cache is missing")
            return FetchResult(
                source="none", message="docs unavailable", ok=False
            ), meta

        if status < 200 or status >= 300:
            raise RuntimeError(f"unexpected status {status} for {docs_url}")
        if not body:
            raise RuntimeError(f"empty response body for {docs_url}")

        atomic_write(docs_path, body)
        return FetchResult(
            source="network", message=f"fetched {docs_url}", ok=True
        ), meta
    except Exception as exc:  # noqa: BLE001
        meta["http_status"] = None
        if nonempty_file(docs_path):
            errors.append(f"docs network fetch failed, used cache: {exc}")
            return FetchResult(
                source="cache_fallback", message="used cached docs", ok=True
            ), meta
        errors.append(f"docs fetch failed with no cache: {exc}")
        return FetchResult(source="none", message="docs unavailable", ok=False), meta


def fetch_gist_examples(
    gist_id: str,
    examples_dir: Path,
    timeout_sec: int,
    errors: list[str],
    prior: dict[str, Any],
    max_age_sec: int,
    github_token: str | None,
) -> tuple[FetchResult, dict[str, Any]]:
    api_url = f"https://api.github.com/gists/{gist_id}"
    index_path = examples_dir / "_gist-index.json"
    meta: dict[str, Any] = {
        "http_status": None,
        "etag": prior.get("gist_etag")
        if isinstance(prior.get("gist_etag"), str)
        else None,
        "last_modified": (
            prior.get("gist_last_modified")
            if isinstance(prior.get("gist_last_modified"), str)
            else None
        ),
    }

    if within_max_age(prior, max_age_sec) and has_examples_cache(examples_dir):
        return (
            FetchResult(
                source="cache_ttl",
                message=f"skipped gist fetch (max_age_sec={max_age_sec})",
                ok=True,
            ),
            meta,
        )

    conditional: dict[str, str] = {}
    if isinstance(meta["etag"], str):
        conditional["If-None-Match"] = meta["etag"]
    if isinstance(meta["last_modified"], str):
        conditional["If-Modified-Since"] = meta["last_modified"]

    try:
        status, body, hdrs = http_get(
            api_url,
            timeout_sec,
            make_headers(
                accept=GITHUB_ACCEPT, token=github_token, conditional=conditional
            ),
        )
        meta["http_status"] = status
        meta["etag"] = header_get(hdrs, "ETag") or meta["etag"]
        meta["last_modified"] = (
            header_get(hdrs, "Last-Modified") or meta["last_modified"]
        )

        if status == 304:
            if has_examples_cache(examples_dir):
                return (
                    FetchResult(
                        source="cache_not_modified",
                        message="gist not modified (304)",
                        ok=True,
                    ),
                    meta,
                )
            errors.append("gist returned 304 but examples cache is missing")
            return (
                FetchResult(
                    source="none", message="gist examples unavailable", ok=False
                ),
                meta,
            )

        if status < 200 or status >= 300:
            raise RuntimeError(f"unexpected status {status} for {api_url}")
        if not body:
            raise RuntimeError(f"empty response body for {api_url}")

        payload = json.loads(body.decode("utf-8"))
        files = payload.get("files", {})
        if not isinstance(files, dict) or not files:
            raise RuntimeError("gist files list missing or empty")

        examples_dir.mkdir(parents=True, exist_ok=True)
        written: list[str] = []
        raw_headers = make_headers(token=github_token)

        for file_info in files.values():
            if not isinstance(file_info, dict):
                continue
            filename = sanitize_filename(str(file_info.get("filename", "")))
            out_path = examples_dir / filename

            truncated = file_info.get("truncated") is True
            content = file_info.get("content")
            if isinstance(content, str) and not truncated:
                data = content.encode("utf-8")
            else:
                raw_url = file_info.get("raw_url")
                if not isinstance(raw_url, str) or not raw_url:
                    continue
                raw_status, raw_body, _ = http_get(raw_url, timeout_sec, raw_headers)
                if raw_status < 200 or raw_status >= 300:
                    raise RuntimeError(f"unexpected status {raw_status} for {raw_url}")
                if not raw_body:
                    raise RuntimeError(f"empty response body for {raw_url}")
                data = raw_body

            atomic_write(out_path, data)
            written.append(filename)

        if not written:
            raise RuntimeError("no gist files with content were available")

        # Remove stale files from previous refreshes.
        keep = set(written) | {"_gist-index.json"}
        for path in examples_dir.iterdir():
            if path.is_file() and path.name not in keep:
                path.unlink()

        index_payload = {
            "gist_id": gist_id,
            "refreshed_at": now_utc(),
            "files": sorted(written),
            "source": api_url,
        }
        atomic_write(index_path, json.dumps(index_payload, indent=2).encode("utf-8"))
        return FetchResult(
            source="network", message=f"fetched gist {gist_id}", ok=True
        ), meta
    except Exception as exc:  # noqa: BLE001
        meta["http_status"] = None
        if has_examples_cache(examples_dir):
            errors.append(f"gist network fetch failed, used cache: {exc}")
            return (
                FetchResult(
                    source="cache_fallback",
                    message="used cached gist examples",
                    ok=True,
                ),
                meta,
            )
        errors.append(f"gist fetch failed with no cache: {exc}")
        return (
            FetchResult(source="none", message="gist examples unavailable", ok=False),
            meta,
        )


def extract_code_lines_from_html(html_text: str) -> list[str]:
    code_tag_re = re.compile(r"<code[^>]*>(.*?)</code>", re.IGNORECASE | re.DOTALL)
    strip_tags_re = re.compile(r"<[^>]+>")
    candidates: list[str] = []

    for raw in code_tag_re.findall(html_text):
        text = html.unescape(raw)
        text = strip_tags_re.sub("", text)
        text = text.replace("\r\n", "\n")
        for line in text.split("\n"):
            line = line.strip()
            if line:
                candidates.append(line)

    seen: set[str] = set()
    out: list[str] = []
    for line in candidates:
        if line not in seen:
            seen.add(line)
            out.append(line)
    return out


def build_cheatsheet(docs_url: str, generated_at: str, docs_path: Path | None) -> str:
    docs_lines: list[str] = []
    if docs_path and nonempty_file(docs_path):
        try:
            docs_text = docs_path.read_text(encoding="utf-8", errors="replace")
            docs_lines = extract_code_lines_from_html(docs_text)
        except Exception:  # noqa: BLE001
            docs_lines = []

    def pick(prefix: str, fallback: str) -> str:
        for line in docs_lines:
            if line.startswith(prefix):
                return line
        return fallback

    theme_line = pick("theme:", "theme: Fira")
    footer_line = pick("footer:", "footer: Your footer goes here")
    slidenumbers_line = pick("slidenumbers:", "slidenumbers: true")
    autoscale_line = pick("autoscale:", "autoscale: true")
    background_image_line = pick("background-image:", "background-image: image.jpg")
    build_lists_line = pick("build-lists:", "build-lists: notFirst")
    fit_header_line = pick("fit-header:", "fit-header: #, ##")
    paragraphs_notes_line = pick(
        "paragraphs-as-presenter-notes:", "paragraphs-as-presenter-notes: true"
    )
    slide_transition_line = pick("slide-transition:", "slide-transition: fade(0.3)")

    per_text = pick("[.text:", "[.text: alignment(center)]")
    per_bg = pick("[.background-color:", "[.background-color: #FF0000]")
    per_build = pick("[.build-lists:", "[.build-lists: true]")
    per_footer = pick("[.footer:", "[.footer: A different footer]")
    per_presenter_notes = pick(
        "[.presenter-notes:",
        "[.presenter-notes: #333333, alignment(left), text-scale(0.9), Helvetica]",
    )
    per_slide_transition = pick("[.slide-transition:", "[.slide-transition: false]")
    code_highlight = pick("[.code-highlight:", "[.code-highlight: 2, 6-8]")

    lines: list[str] = [
        f"<!-- Generated by scripts/refresh_sources.py; generated_at={generated_at}; docs_url={docs_url} -->",
        "# Deckset Cheatsheet (for LLMs)",
        "",
        "Prefer this file over the HTML docs cache when authoring Deckset markdown.",
        "",
        "## Core",
        "- Slide separator: `---`",
        "- Presenter notes: prefix paragraphs with `^`",
        "",
        "## Global metadata (top of file, no blank lines between commands)",
        "```md",
        theme_line,
        footer_line,
        slidenumbers_line,
        autoscale_line,
        "```",
        "",
        "## Common global commands",
        "```md",
        background_image_line,
        build_lists_line,
        fit_header_line,
        paragraphs_notes_line,
        slide_transition_line,
        "```",
        "",
        "## Per-slide commands",
        "```md",
        per_text,
        per_bg,
        per_build,
        per_footer,
        per_presenter_notes,
        per_slide_transition,
        code_highlight,
        "```",
        "",
        "## Columns",
        "```md",
        "[.column]",
        "Left",
        "[.column]",
        "Right",
        "[.end-columns]",
        "```",
        "",
        "## [fit] titles",
        "```md",
        "# [fit] Title that must fit",
        "```",
        "",
        "## Gotchas",
        "- Global commands must be the first lines; no blank lines between them.",
        "- If you enable `paragraphs-as-presenter-notes: true`, normal paragraphs disappear from slides.",
        "- Always close columns with `[.end-columns]`.",
        "",
    ]
    return "\n".join(lines)


def write_cheatsheet(
    cheatsheet_path: Path, docs_url: str, docs_path: Path, errors: list[str]
) -> FetchResult:
    try:
        content = build_cheatsheet(
            docs_url=docs_url,
            generated_at=now_utc(),
            docs_path=docs_path if nonempty_file(docs_path) else None,
        )
        atomic_write(cheatsheet_path, content.encode("utf-8"))
        return FetchResult(source="generated", message="generated cheatsheet", ok=True)
    except Exception as exc:  # noqa: BLE001
        if nonempty_file(cheatsheet_path):
            errors.append(f"cheatsheet generation failed, used cache: {exc}")
            return FetchResult(
                source="cache_fallback", message="used cached cheatsheet", ok=True
            )
        errors.append(f"cheatsheet generation failed with no cache: {exc}")
        return FetchResult(source="none", message="cheatsheet unavailable", ok=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Refresh Deckset docs and gist examples used by the deckset skill."
    )
    parser.add_argument("--docs-url", default=DEFAULT_DOCS_URL)
    parser.add_argument("--gist-id", default=DEFAULT_GIST_ID)
    parser.add_argument("--timeout-sec", type=int, default=20)
    parser.add_argument(
        "--max-age-sec",
        type=int,
        default=0,
        help="Skip network refresh if refreshed_at is within this many seconds.",
    )
    parser.add_argument("--refs-dir", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_dir = Path(__file__).resolve().parents[1]
    refs_dir = (
        Path(args.refs_dir).resolve() if args.refs_dir else skill_dir / "references"
    )

    docs_path = refs_dir / DOCS_CACHE_FILENAME
    cheatsheet_path = refs_dir / CHEATSHEET_FILENAME
    examples_dir = refs_dir / "examples"
    metadata_path = refs_dir / METADATA_FILENAME

    prior = load_json_dict(metadata_path)
    errors: list[str] = []
    github_token = get_github_token()

    docs_result, docs_meta = fetch_docs(
        args.docs_url, docs_path, args.timeout_sec, errors, prior, args.max_age_sec
    )
    gist_result, gist_meta = fetch_gist_examples(
        args.gist_id,
        examples_dir,
        args.timeout_sec,
        errors,
        prior,
        args.max_age_sec,
        github_token,
    )
    cheatsheet_result = write_cheatsheet(
        cheatsheet_path, args.docs_url, docs_path, errors
    )

    used_cache_fallback = (
        docs_result.source == "cache_fallback" or gist_result.source == "cache_fallback"
    )

    summary: dict[str, Any] = {
        "refreshed_at": now_utc(),
        "docs_url": args.docs_url,
        "gist_id": args.gist_id,
        "docs_source": docs_result.source,
        "gist_source": gist_result.source,
        "cheatsheet_source": cheatsheet_result.source,
        "used_cache_fallback": used_cache_fallback,
        "max_age_sec": args.max_age_sec,
        "docs_http_status": docs_meta.get("http_status"),
        "gist_http_status": gist_meta.get("http_status"),
        "docs_etag": docs_meta.get("etag"),
        "docs_last_modified": docs_meta.get("last_modified"),
        "gist_etag": gist_meta.get("etag"),
        "gist_last_modified": gist_meta.get("last_modified"),
        "errors": errors,
    }

    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(metadata_path, json.dumps(summary, indent=2).encode("utf-8"))

    print(
        json.dumps(
            {
                "docs_source": docs_result.source,
                "gist_source": gist_result.source,
                "cheatsheet_source": cheatsheet_result.source,
                "used_cache_fallback": used_cache_fallback,
                "metadata": str(metadata_path),
                "cheatsheet": str(cheatsheet_path),
            }
        )
    )

    ok = docs_result.ok and gist_result.ok and cheatsheet_result.ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
