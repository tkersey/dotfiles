#!/usr/bin/env -S uv run python
"""Refresh Deckset docs and gist examples with cache fallback."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_DOCS_URL = "https://docs.deckset.com/markdownDocumentation.html"
DEFAULT_GIST_ID = "69c36bcf40e23f7ef5c82a9c63983a13"


@dataclass
class FetchResult:
    source: str
    message: str
    ok: bool


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_url(url: str, timeout_sec: int) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "deckset-skill-refresh/1.0"})
    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:  # nosec B310
        status = getattr(resp, "status", 200)
        if status < 200 or status >= 300:
            raise RuntimeError(f"unexpected status {status} for {url}")
        body = resp.read()
    if not body:
        raise RuntimeError(f"empty response body for {url}")
    return body


def sanitize_filename(name: str) -> str:
    base = name.strip().replace("\\", "/").split("/")[-1]
    base = re.sub(r"[^A-Za-z0-9._-]", "-", base)
    return base or "example.md"


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_bytes(data)
    os.replace(tmp_path, path)


def fetch_docs(
    docs_url: str, docs_path: Path, timeout_sec: int, errors: list[str]
) -> FetchResult:
    try:
        body = read_url(docs_url, timeout_sec)
        atomic_write(docs_path, body)
        return FetchResult(source="network", message=f"fetched {docs_url}", ok=True)
    except Exception as exc:  # noqa: BLE001
        if docs_path.exists() and docs_path.stat().st_size > 0:
            errors.append(f"docs network fetch failed, used cache: {exc}")
            return FetchResult(source="cache", message="used cached docs", ok=True)
        errors.append(f"docs fetch failed with no cache: {exc}")
        return FetchResult(source="none", message="docs unavailable", ok=False)


def fetch_gist_examples(
    gist_id: str, examples_dir: Path, timeout_sec: int, errors: list[str]
) -> FetchResult:
    api_url = f"https://api.github.com/gists/{gist_id}"
    index_path = examples_dir / "_gist-index.json"
    try:
        body = read_url(api_url, timeout_sec)
        payload = json.loads(body.decode("utf-8"))
        files = payload.get("files", {})
        if not isinstance(files, dict) or not files:
            raise RuntimeError("gist files list missing or empty")

        examples_dir.mkdir(parents=True, exist_ok=True)
        written: list[str] = []
        for file_info in files.values():
            if not isinstance(file_info, dict):
                continue
            filename = sanitize_filename(str(file_info.get("filename", "")))
            content = file_info.get("content")
            if not isinstance(content, str):
                continue
            out_path = examples_dir / filename
            atomic_write(out_path, content.encode("utf-8"))
            written.append(filename)

        if not written:
            raise RuntimeError("no gist files with inline content were available")

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
        return FetchResult(source="network", message=f"fetched gist {gist_id}", ok=True)
    except Exception as exc:  # noqa: BLE001
        has_cache = examples_dir.exists() and any(
            p.is_file() and p.name != "_gist-index.json" for p in examples_dir.iterdir()
        )
        if has_cache:
            errors.append(f"gist network fetch failed, used cache: {exc}")
            return FetchResult(source="cache", message="used cached gist examples", ok=True)
        errors.append(f"gist fetch failed with no cache: {exc}")
        return FetchResult(source="none", message="gist examples unavailable", ok=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Refresh Deckset docs and gist examples used by the deckset skill."
    )
    parser.add_argument("--docs-url", default=DEFAULT_DOCS_URL)
    parser.add_argument("--gist-id", default=DEFAULT_GIST_ID)
    parser.add_argument("--timeout-sec", type=int, default=20)
    parser.add_argument("--refs-dir", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_dir = Path(__file__).resolve().parents[1]
    refs_dir = Path(args.refs_dir).resolve() if args.refs_dir else skill_dir / "references"

    docs_path = refs_dir / "deckset-markdownDocumentation.html"
    examples_dir = refs_dir / "examples"
    metadata_path = refs_dir / "refresh-metadata.json"
    errors: list[str] = []

    docs_result = fetch_docs(args.docs_url, docs_path, args.timeout_sec, errors)
    gist_result = fetch_gist_examples(args.gist_id, examples_dir, args.timeout_sec, errors)

    summary: dict[str, Any] = {
        "refreshed_at": now_utc(),
        "docs_url": args.docs_url,
        "gist_id": args.gist_id,
        "docs_source": docs_result.source,
        "gist_source": gist_result.source,
        "used_cache_fallback": docs_result.source == "cache" or gist_result.source == "cache",
        "errors": errors,
    }

    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(metadata_path, json.dumps(summary, indent=2).encode("utf-8"))

    print(
        json.dumps(
            {
                "docs_source": docs_result.source,
                "gist_source": gist_result.source,
                "used_cache_fallback": summary["used_cache_fallback"],
                "metadata": str(metadata_path),
            }
        )
    )

    return 0 if docs_result.ok and gist_result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
