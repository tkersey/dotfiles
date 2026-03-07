#!/usr/bin/env python3
"""Collect static architecture signals for a local repository."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path


IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".jj",
    ".xit",
    ".idea",
    ".vscode",
    "__pycache__",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "target",
    ".next",
    ".nuxt",
    ".turbo",
    ".zig-cache",
    ".cache",
    "coverage",
    ".venv",
    "venv",
    "tmp",
    "temp",
}

TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".rst",
    ".adoc",
    ".json",
    ".jsonc",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".py",
    ".rb",
    ".go",
    ".rs",
    ".zig",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".java",
    ".kt",
    ".swift",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".php",
    ".sh",
    ".zsh",
}

DOC_SUFFIXES = {".md", ".txt", ".rst", ".adoc"}
LOW_SIGNAL_PARTS = {
    ".github",
    "github",
    "test",
    "tests",
    "spec",
    "specs",
    "fixtures",
    "examples",
    "docs",
    "doc",
    "references",
    "skill",
    "skills",
    "agent",
    "agents",
}

MANIFEST_HINTS = {
    "package.json": "node",
    "pnpm-workspace.yaml": "workspace",
    "turbo.json": "workspace",
    "nx.json": "workspace",
    "pyproject.toml": "python",
    "requirements.txt": "python",
    "go.mod": "go",
    "Cargo.toml": "rust",
    "Gemfile": "ruby",
    "pom.xml": "jvm",
    "build.gradle": "jvm",
    "build.gradle.kts": "jvm",
    "build.zig": "zig",
    "Dockerfile": "container",
    "docker-compose.yml": "container",
    "docker-compose.yaml": "container",
    "flake.nix": "nix",
}

DOC_PATTERNS = [
    re.compile(r"\b(clean architecture|hexagonal|ports and adapters|onion architecture)\b", re.I),
    re.compile(r"\b(layered architecture|n-tier|three-tier)\b", re.I),
    re.compile(r"\b(modular monolith|microservices?|service-oriented)\b", re.I),
    re.compile(r"\b(event-driven|message-driven|event bus|pub/sub)\b", re.I),
    re.compile(r"\b(plugin system|plugin architecture|extension system)\b", re.I),
    re.compile(r"\b(mvc|mvvm)\b", re.I),
]

ARCHITECTURE_MARKERS = {
    "layered": {"controller", "controllers", "service", "services", "repository", "repositories", "model", "models", "handler", "handlers"},
    "component-ui": {"components", "component", "views", "view", "viewmodels", "viewmodel", "screens", "pages"},
    "clean-hexagonal": {"domain", "application", "usecases", "usecase", "ports", "port", "adapters", "adapter", "infrastructure", "delivery"},
    "modular-monolith": {"modules", "module", "packages", "package", "bounded-contexts", "bounded_contexts", "contexts", "apps"},
    "microservice": {"services", "service", "gateway", "gateways"},
    "event-driven": {"events", "event", "consumers", "consumer", "publishers", "publisher", "subscribers", "subscriber", "queues", "queue", "topics"},
    "pipeline": {"pipelines", "pipeline", "jobs", "job", "dags", "dag", "etl", "ingest", "transform", "load"},
    "plugin": {"plugins", "plugin", "extensions", "extension", "hooks", "providers", "adapters"},
}

KEYWORD_PATTERNS = {
    "event-driven": re.compile(r"\b(kafka|rabbitmq|nats|sns|sqs|pubsub|topic|consumer|publisher|subscribe)\b", re.I),
    "pipeline": re.compile(r"\b(airflow|dagster|prefect|etl|workflow|pipeline|cron job|batch job)\b", re.I),
    "plugin": re.compile(r"\b(plugin|hook registry|provider interface|extension point|dynamic load)\b", re.I),
    "microservice": re.compile(r"\b(service boundary|grpc|service-to-service|microservice)\b", re.I),
    "clean-hexagonal": re.compile(r"\b(ports and adapters|use case|usecase|application service|domain layer|infrastructure layer)\b", re.I),
}

REPO_KIND_RULES = [
    ("plugin-extension", lambda counts: counts["plugin"] >= 1),
    ("data-pipeline", lambda counts: counts["pipeline"] >= 3),
    ("monorepo-platform", lambda counts: counts["workspace"] >= 1 or counts["apps_dir"] >= 2),
    ("application-service", lambda counts: counts["service_like"] >= 2),
    ("cli-tooling", lambda counts: counts["cli_like"] >= 2),
    ("infra-ops", lambda counts: counts["infra_like"] >= 2),
    ("library-sdk", lambda counts: counts["library_like"] >= 1),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect static architecture signals for a repository.")
    parser.add_argument("repo_path", help="Path to the repository to inspect")
    return parser.parse_args()


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {"README", "README.md", "ARCHITECTURE.md"}


def should_scan_keywords(path: Path) -> bool:
    if path.suffix.lower() in DOC_SUFFIXES:
        return False
    lowered_parts = {part.lower() for part in path.parts}
    return not (lowered_parts & LOW_SIGNAL_PARTS)


def should_use_path_markers(path: Path) -> bool:
    lowered_parts = {part.lower() for part in path.parts}
    return not (lowered_parts & LOW_SIGNAL_PARTS)


def read_text(path: Path, limit: int = 20000) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            return handle.read(limit)
    except OSError:
        return ""


def trimmed(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def collect_files(root: Path) -> tuple[list[Path], list[Path]]:
    all_files: list[Path] = []
    text_files: list[Path] = []
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d
            for d in dirnames
            if d not in IGNORE_DIRS and not d.startswith(".cache") and not d.startswith(".venv")
        ]
        current_path = Path(current_root)
        for filename in filenames:
            path = current_path / filename
            all_files.append(path)
            if is_text_file(path):
                text_files.append(path)
    return all_files[:4000], text_files[:800]


def collect_manifests(files: list[Path], root: Path) -> tuple[list[dict[str, str]], Counter]:
    manifests: list[dict[str, str]] = []
    counts: Counter = Counter()
    for path in files:
        if path.name in MANIFEST_HINTS:
            manifests.append({"path": trimmed(path, root), "kind": MANIFEST_HINTS[path.name]})
            counts[MANIFEST_HINTS[path.name]] += 1
    return manifests, counts


def collect_top_level_dirs(root: Path) -> list[str]:
    try:
        return sorted(
            entry.name for entry in root.iterdir() if entry.is_dir() and entry.name not in IGNORE_DIRS
        )
    except OSError:
        return []


def collect_docs_claims(text_files: list[Path], root: Path) -> list[dict[str, str]]:
    claims: list[dict[str, str]] = []
    for path in text_files:
        lowered_name = path.name.lower()
        if "readme" not in lowered_name and "architecture" not in lowered_name and "adr" not in lowered_name:
            continue
        text = read_text(path)
        for pattern in DOC_PATTERNS:
            match = pattern.search(text)
            if match:
                claims.append(
                    {
                        "path": trimmed(path, root),
                        "claim": match.group(1),
                    }
                )
    return claims[:50]


def collect_architecture_signals(top_dirs: list[str], text_files: list[Path], root: Path) -> list[dict[str, object]]:
    signal_map: dict[str, dict[str, object]] = {}
    path_hits: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    keyword_hits: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

    def ensure_signal(name: str) -> dict[str, object]:
        if name not in signal_map:
            signal_map[name] = {"name": name, "score": 0, "evidence": []}
        return signal_map[name]

    normalized_dirs = {entry.lower() for entry in top_dirs}
    for signal_name, markers in ARCHITECTURE_MARKERS.items():
        overlap = sorted(normalized_dirs & markers)
        if overlap:
            entry = ensure_signal(signal_name)
            entry["score"] += min(len(overlap), 4)
            entry["evidence"].append(f"top-level dirs: {', '.join(overlap)}")

    for path in text_files:
        rel = trimmed(path, root)
        if should_use_path_markers(path):
            path_parts = {part.lower() for part in Path(rel).parts}
            for signal_name, markers in ARCHITECTURE_MARKERS.items():
                overlap = sorted(path_parts & markers)
                if overlap:
                    marker = overlap[0]
                    if len(path_hits[signal_name][marker]) < 2:
                        path_hits[signal_name][marker].append(rel)

        if not should_scan_keywords(path):
            continue
        text = read_text(path)
        if not text:
            continue
        for signal_name, pattern in KEYWORD_PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                unique_matches = sorted({match.lower() for match in matches})[:4]
                for match in unique_matches:
                    if len(keyword_hits[signal_name][match]) < 2:
                        keyword_hits[signal_name][match].append(rel)

    for signal_name, markers in path_hits.items():
        entry = ensure_signal(signal_name)
        entry["score"] += min(len(markers), 4)
        for marker, paths in list(markers.items())[:4]:
            if len(entry["evidence"]) < 8:
                entry["evidence"].append(f"path marker {marker}: {paths[0]}")

    for signal_name, matches in keyword_hits.items():
        entry = ensure_signal(signal_name)
        entry["score"] += min(len(matches), 4)
        for match, paths in list(matches.items())[:4]:
            if len(entry["evidence"]) < 8:
                entry["evidence"].append(f"{paths[0]}: {match}")

    return sorted(signal_map.values(), key=lambda item: (-int(item["score"]), str(item["name"])))


def collect_subsystem_hints(root: Path, top_dirs: list[str]) -> list[dict[str, str]]:
    hints: list[dict[str, str]] = []
    interesting = {"apps", "services", "packages", "libs", "modules", "plugins", "extensions", "cmd", "internal"}
    for name in top_dirs:
        if name.lower() not in interesting:
            continue
        path = root / name
        try:
            children = [entry.name for entry in path.iterdir() if entry.is_dir() and entry.name not in IGNORE_DIRS][:10]
        except OSError:
            children = []
        hints.append(
            {
                "path": name,
                "hint": "subsystem container",
                "children": ", ".join(children) if children else "none",
            }
        )
    return hints


def infer_repo_kind(manifest_counts: Counter, top_dirs: list[str], signals: list[dict[str, object]]) -> tuple[list[dict[str, str]], list[str]]:
    counts: Counter = Counter(manifest_counts)
    normalized_dirs = {entry.lower() for entry in top_dirs}
    counts["plugin"] = len({"plugins", "extensions", "hooks", "providers"} & normalized_dirs)
    counts["pipeline"] = len({"pipelines", "dags", "jobs", "workflows", "etl"} & normalized_dirs)
    counts["apps_dir"] = len({"apps", "services", "packages"} & normalized_dirs)
    counts["service_like"] = len({"app", "apps", "api", "apis", "service", "services", "worker", "workers"} & normalized_dirs)
    counts["cli_like"] = len({"cmd", "bin", "scripts", "tools"} & normalized_dirs)
    counts["infra_like"] = len({"terraform", "helm", "k8s", "ops", "deploy", "infra"} & normalized_dirs)
    counts["library_like"] = len({"src", "lib", "include", "pkg"} & normalized_dirs)

    hints: list[dict[str, str]] = []
    gaps: list[str] = []
    for repo_kind, rule in REPO_KIND_RULES:
        if rule(counts):
            reason = []
            if repo_kind == "plugin-extension":
                reason.append("plugin or extension directories are present")
            elif repo_kind == "data-pipeline":
                reason.append("pipeline/job-oriented directories dominate the repo")
            elif repo_kind == "monorepo-platform":
                reason.append("workspace manifests or multi-app containers are present")
            elif repo_kind == "application-service":
                reason.append("application or service directories are prominent")
            elif repo_kind == "cli-tooling":
                reason.append("tooling or script entrypoints dominate the repo")
            elif repo_kind == "infra-ops":
                reason.append("infra or deployment directories are prominent")
            elif repo_kind == "library-sdk":
                reason.append("library-style source roots are present")
            hints.append({"repo_kind": repo_kind, "reason": "; ".join(reason)})

    if not hints:
        gaps.append("repo kind is weakly signaled; inspect entrypoints and packaging surfaces manually")

    if not signals:
        gaps.append("architecture signals are sparse; inspect representative modules manually")

    return hints[:3], gaps


def main() -> int:
    args = parse_args()
    root = Path(args.repo_path).expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"repo path does not exist: {root}")
    if not root.is_dir():
        raise SystemExit(f"repo path is not a directory: {root}")

    files, text_files = collect_files(root)
    top_dirs = collect_top_level_dirs(root)
    manifests, manifest_counts = collect_manifests(files, root)
    docs_claims = collect_docs_claims(text_files, root)
    signals = collect_architecture_signals(top_dirs, text_files, root)
    subsystem_hints = collect_subsystem_hints(root, top_dirs)
    repo_kind_hints, confidence_gaps = infer_repo_kind(manifest_counts, top_dirs, signals)

    if not manifests:
        confidence_gaps.append("no common manifest file was detected")
    if not docs_claims:
        confidence_gaps.append("no architecture claim was detected in README/architecture docs")
    if len(top_dirs) < 2:
        confidence_gaps.append("very few top-level directories were available for structural inference")

    payload = {
        "repo_path": str(root),
        "repo_kind_hints": repo_kind_hints,
        "manifests": manifests,
        "top_level_dirs": top_dirs,
        "architecture_signals": signals,
        "subsystem_hints": subsystem_hints,
        "docs_claims": docs_claims,
        "confidence_gaps": sorted(dict.fromkeys(confidence_gaps)),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
