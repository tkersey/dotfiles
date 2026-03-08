#!/usr/bin/env python3
"""Collect static architecture signals for a local repository."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

MAX_FILES = 4000
MAX_TEXT_FILES = 800
DEFAULT_READ_LIMIT = 20000

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
    ".properties",
    ".xml",
    ".proto",
    ".sql",
    ".tf",
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
    ".kts",
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
TEXT_NAMES = {
    "README",
    "README.md",
    "ARCHITECTURE.md",
    "Dockerfile",
    "Makefile",
    "Justfile",
    "Tiltfile",
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
    re.compile(
        r"\b(clean architecture|hexagonal|ports and adapters|onion architecture)\b",
        re.I,
    ),
    re.compile(r"\b(layered architecture|n-tier|three-tier)\b", re.I),
    re.compile(r"\b(modular monolith|microservices?|service-oriented)\b", re.I),
    re.compile(r"\b(event-driven|message-driven|event bus|pub/sub)\b", re.I),
    re.compile(r"\b(plugin system|plugin architecture|extension system)\b", re.I),
    re.compile(r"\b(mvc|mvvm)\b", re.I),
]

ARCHITECTURE_MARKERS = {
    "layered": {
        "controller",
        "controllers",
        "service",
        "services",
        "repository",
        "repositories",
        "model",
        "models",
        "handler",
        "handlers",
    },
    "component-ui": {
        "components",
        "component",
        "views",
        "view",
        "viewmodels",
        "viewmodel",
        "screens",
        "pages",
        "frontend",
        "ui",
    },
    "clean-hexagonal": {
        "domain",
        "application",
        "usecases",
        "usecase",
        "ports",
        "port",
        "adapters",
        "adapter",
        "infrastructure",
        "delivery",
    },
    "modular-monolith": {
        "modules",
        "module",
        "packages",
        "package",
        "bounded-contexts",
        "bounded_contexts",
        "contexts",
        "apps",
    },
    "microservice": {"services", "service", "gateway", "gateways"},
    "event-driven": {
        "events",
        "event",
        "consumers",
        "consumer",
        "publishers",
        "publisher",
        "subscribers",
        "subscriber",
        "queues",
        "queue",
        "topics",
    },
    "pipeline": {
        "pipelines",
        "pipeline",
        "jobs",
        "job",
        "dags",
        "dag",
        "etl",
        "ingest",
        "transform",
        "load",
        "workflow",
        "workflows",
    },
    "plugin": {
        "plugins",
        "plugin",
        "extensions",
        "extension",
        "hooks",
        "providers",
        "adapters",
    },
}

KEYWORD_PATTERNS = {
    "component-ui": re.compile(
        r"\b(component|viewmodel|screen|page|react|vue|svelte|solid)\b", re.I
    ),
    "event-driven": re.compile(
        r"\b(kafka|rabbitmq|nats|sns|sqs|pubsub|topic|consumer|publisher|subscribe|eventbridge)\b",
        re.I,
    ),
    "pipeline": re.compile(
        r"\b(airflow|dagster|prefect|etl|workflow|pipeline|cron job|batch job|dag)\b",
        re.I,
    ),
    "plugin": re.compile(
        r"\b(plugin|hook registry|provider interface|extension point|dynamic load)\b",
        re.I,
    ),
    "microservice": re.compile(
        r"\b(service boundary|grpc|service-to-service|microservice)\b", re.I
    ),
    "clean-hexagonal": re.compile(
        r"\b(ports and adapters|use case|usecase|application service|domain layer|infrastructure layer)\b",
        re.I,
    ),
}

ENTRYPOINT_FILE_NAMES = {
    "main.py",
    "main.go",
    "main.rs",
    "main.ts",
    "main.tsx",
    "main.js",
    "main.jsx",
    "app.py",
    "app.ts",
    "app.tsx",
    "server.py",
    "server.ts",
    "server.js",
    "manage.py",
    "cli.py",
}
ENTRYPOINT_DIR_PARTS = {"cmd", "bin", "api", "server", "web", "app", "apps"}

ZONE_MARKERS = {
    "delivery": {
        "api",
        "http",
        "controller",
        "controllers",
        "handler",
        "handlers",
        "route",
        "routes",
        "gateway",
        "gateways",
        "cli",
        "cmd",
    },
    "domain": {
        "domain",
        "application",
        "usecase",
        "usecases",
        "core",
        "service",
        "services",
        "entity",
        "entities",
        "model",
        "models",
        "ports",
        "port",
    },
    "infrastructure": {
        "repository",
        "repositories",
        "adapter",
        "adapters",
        "infrastructure",
        "infra",
        "db",
        "database",
        "storage",
        "persistence",
    },
    "ui": {
        "component",
        "components",
        "view",
        "views",
        "viewmodel",
        "viewmodels",
        "pages",
        "screens",
        "frontend",
        "ui",
        "web",
    },
}
DOMAIN_IMPORT_TOKENS = {
    "domain",
    "application",
    "usecase",
    "usecases",
    "core",
    "service",
    "services",
    "entity",
    "entities",
    "port",
    "ports",
}
INFRA_IMPORT_TOKENS = {
    "adapter",
    "adapters",
    "repository",
    "repositories",
    "infra",
    "infrastructure",
    "db",
    "database",
    "storage",
    "persistence",
    "gateway",
    "gateways",
}
LAYERED_IMPORT_TOKENS = {
    "service",
    "services",
    "repository",
    "repositories",
    "model",
    "models",
}

IMPORT_PATTERNS = [
    re.compile(r"(?m)^\s*(?:from|import)\s+([A-Za-z0-9_./:-]+)"),
    re.compile(r"(?m)\bfrom\s+[\"']([^\"']+)[\"']"),
    re.compile(r"(?m)\brequire\(\s*[\"']([^\"']+)[\"']\s*\)"),
    re.compile(r"(?m)^\s*use\s+([A-Za-z0-9_:]+)"),
]

REPO_KIND_RULES = [
    ("plugin-extension", lambda counts: counts["plugin"] >= 1),
    ("data-pipeline", lambda counts: counts["pipeline"] >= 3),
    (
        "monorepo-platform",
        lambda counts: counts["workspace"] >= 1 or counts["apps_dir"] >= 2,
    ),
    ("infra-ops", lambda counts: counts["infra_like"] >= 2),
    ("cli-tooling", lambda counts: counts["cli_like"] >= 2),
    (
        "application-service",
        lambda counts: counts["service_like"] >= 2 or counts["frontend_like"] >= 2,
    ),
    ("library-sdk", lambda counts: counts["library_like"] >= 1),
]


@dataclass
class ScanCoverage:
    total_files_seen: int = 0
    total_text_files_seen: int = 0
    files_considered: int = 0
    text_files_considered: int = 0
    truncated_reads: int = 0
    read_errors: int = 0


class SignalEntry(TypedDict):
    name: str
    score: int
    evidence: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect static architecture signals for a repository."
    )
    parser.add_argument("repo_path", help="Path to the repository to inspect")
    parser.add_argument(
        "--focus-path",
        action="append",
        default=[],
        help="Repo-relative file or directory to inspect as a target slice (repeatable)",
    )
    parser.add_argument(
        "--read-limit",
        type=int,
        default=DEFAULT_READ_LIMIT,
        help="Maximum characters to read from each text file",
    )
    return parser.parse_args()


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_NAMES


def should_scan_keywords(path: Path) -> bool:
    if path.suffix.lower() in DOC_SUFFIXES:
        return False
    lowered_parts = {part.lower() for part in path.parts}
    return not (lowered_parts & LOW_SIGNAL_PARTS)


def should_use_path_markers(path: Path) -> bool:
    lowered_parts = {part.lower() for part in path.parts}
    return not (lowered_parts & LOW_SIGNAL_PARTS)


def trimmed(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def read_text(
    path: Path,
    coverage: ScanCoverage,
    read_cache: dict[Path, str],
    limit: int,
) -> str:
    cached = read_cache.get(path)
    if cached is not None:
        return cached
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            text = handle.read(limit + 1)
    except OSError:
        coverage.read_errors += 1
        read_cache[path] = ""
        return ""
    if len(text) > limit:
        coverage.truncated_reads += 1
        text = text[:limit]
    read_cache[path] = text
    return text


def collect_files(root: Path, coverage: ScanCoverage) -> tuple[list[Path], list[Path]]:
    all_files: list[Path] = []
    text_files: list[Path] = []
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d
            for d in dirnames
            if d not in IGNORE_DIRS
            and not d.startswith(".cache")
            and not d.startswith(".venv")
        ]
        current_path = Path(current_root)
        for filename in filenames:
            path = current_path / filename
            all_files.append(path)
            if is_text_file(path):
                text_files.append(path)
    all_files.sort(key=lambda item: str(item))
    text_files.sort(key=lambda item: str(item))
    coverage.total_files_seen = len(all_files)
    coverage.total_text_files_seen = len(text_files)
    limited_files = all_files[:MAX_FILES]
    limited_text_files = text_files[:MAX_TEXT_FILES]
    coverage.files_considered = len(limited_files)
    coverage.text_files_considered = len(limited_text_files)
    return limited_files, limited_text_files


def collect_manifests(
    files: list[Path], root: Path
) -> tuple[list[dict[str, str]], Counter]:
    manifests: list[dict[str, str]] = []
    counts: Counter = Counter()
    for path in files:
        if path.name in MANIFEST_HINTS:
            manifests.append(
                {"path": trimmed(path, root), "kind": MANIFEST_HINTS[path.name]}
            )
            counts[MANIFEST_HINTS[path.name]] += 1
    return manifests, counts


def collect_top_level_dirs(root: Path) -> list[str]:
    try:
        return sorted(
            entry.name
            for entry in root.iterdir()
            if entry.is_dir() and entry.name not in IGNORE_DIRS
        )
    except OSError:
        return []


def collect_docs_claims(
    text_files: list[Path],
    root: Path,
    coverage: ScanCoverage,
    read_cache: dict[Path, str],
    read_limit: int,
) -> list[dict[str, str]]:
    claims: list[dict[str, str]] = []
    for path in text_files:
        lowered_name = path.name.lower()
        if (
            "readme" not in lowered_name
            and "architecture" not in lowered_name
            and "adr" not in lowered_name
        ):
            continue
        text = read_text(path, coverage, read_cache, read_limit)
        for pattern in DOC_PATTERNS:
            match = pattern.search(text)
            if match:
                claims.append({"path": trimmed(path, root), "claim": match.group(1)})
    return claims[:50]


def extract_import_tokens(text: str) -> set[str]:
    tokens: set[str] = set()
    for pattern in IMPORT_PATTERNS:
        for raw in pattern.findall(text):
            normalized = raw.replace("::", "/").replace(".", "/").replace("\\", "/")
            normalized = normalized.strip("./")
            for piece in re.split(r"[^A-Za-z0-9]+", normalized):
                if piece:
                    tokens.add(piece.lower())
    return tokens


def classify_zones(path: Path) -> set[str]:
    lowered_parts = {part.lower() for part in path.parts}
    zones = {name for name, markers in ZONE_MARKERS.items() if lowered_parts & markers}
    return zones


def collect_dependency_direction_hints(
    text_files: list[Path],
    root: Path,
    coverage: ScanCoverage,
    read_cache: dict[Path, str],
    read_limit: int,
) -> list[dict[str, str]]:
    hints: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for path in text_files:
        rel = trimmed(path, root)
        rel_path = Path(rel)
        if not should_scan_keywords(rel_path):
            continue
        zones = classify_zones(rel_path)
        if not zones:
            continue
        tokens = extract_import_tokens(
            read_text(path, coverage, read_cache, read_limit)
        )
        if not tokens:
            continue

        def add_hint(signal: str, effect: str, detail: str) -> None:
            key = (rel, signal, effect)
            if key in seen:
                return
            seen.add(key)
            hints.append(
                {
                    "path": rel,
                    "signal": signal,
                    "effect": effect,
                    "detail": detail,
                }
            )

        if "domain" in zones and tokens & INFRA_IMPORT_TOKENS:
            imports = ", ".join(sorted(tokens & INFRA_IMPORT_TOKENS)[:4])
            add_hint(
                "clean-hexagonal",
                "weakens",
                f"domain-like module imports infrastructure tokens: {imports}",
            )
        if (zones & {"delivery", "ui"}) and tokens & DOMAIN_IMPORT_TOKENS:
            imports = ", ".join(sorted(tokens & DOMAIN_IMPORT_TOKENS)[:4])
            add_hint(
                "clean-hexagonal",
                "supports",
                f"delivery-like module imports domain/application tokens: {imports}",
            )
        if "infrastructure" in zones and tokens & DOMAIN_IMPORT_TOKENS:
            imports = ", ".join(sorted(tokens & DOMAIN_IMPORT_TOKENS)[:4])
            add_hint(
                "clean-hexagonal",
                "supports",
                f"adapter-like module imports domain/application tokens: {imports}",
            )
        if "delivery" in zones and tokens & LAYERED_IMPORT_TOKENS:
            imports = ", ".join(sorted(tokens & LAYERED_IMPORT_TOKENS)[:4])
            add_hint(
                "layered",
                "supports",
                f"delivery-like module imports service/repository tokens: {imports}",
            )
    return hints[:24]


def collect_entrypoint_hints(files: list[Path], root: Path) -> list[dict[str, str]]:
    hints: list[dict[str, str]] = []
    for path in files:
        rel = trimmed(path, root)
        rel_path = Path(rel)
        lowered_parts = [part.lower() for part in rel_path.parts]
        lowered_name = rel_path.name.lower()
        hint: str | None = None
        if lowered_name in ENTRYPOINT_FILE_NAMES:
            hint = "entrypoint candidate"
        elif lowered_parts and lowered_parts[0] in {"cmd", "bin"}:
            hint = "cli entrypoint"
        elif lowered_name in {"index.tsx", "index.jsx", "main.tsx", "app.tsx"}:
            hint = "ui entrypoint"
        elif lowered_parts and lowered_parts[0] in ENTRYPOINT_DIR_PARTS:
            hint = "runnable surface"
        if hint is not None:
            hints.append({"path": rel, "hint": hint})
    return hints[:20]


def collect_runtime_boundary_hints(
    files: list[Path], top_dirs: list[str], root: Path
) -> list[dict[str, str]]:
    hints: list[dict[str, str]] = []
    top_dir_set = {entry.lower() for entry in top_dirs}
    service_units: dict[str, set[str]] = defaultdict(set)
    app_units: dict[str, set[str]] = defaultdict(set)
    for path in files:
        rel_path = Path(trimmed(path, root))
        parts = [part.lower() for part in rel_path.parts]
        if rel_path.name in {"docker-compose.yml", "docker-compose.yaml"}:
            hints.append(
                {
                    "path": trimmed(path, root),
                    "hint": "local orchestration surface",
                    "detail": "compose file suggests multiple runnable units or local service topology",
                }
            )
        if len(parts) >= 2 and parts[0] == "services":
            service_units[parts[1]].add(rel_path.name)
        if len(parts) >= 2 and parts[0] == "apps":
            app_units[parts[1]].add(rel_path.name)

    service_runtime_units = {
        name: markers
        for name, markers in service_units.items()
        if markers
        & {"Dockerfile", "package.json", "pyproject.toml", "go.mod", "Cargo.toml"}
    }
    if len(service_runtime_units) >= 2:
        names = ", ".join(sorted(service_runtime_units)[:4])
        hints.append(
            {
                "path": "services/",
                "hint": "multiple service runtime units",
                "detail": f"multiple service folders have dedicated manifests or container surfaces: {names}",
            }
        )
    if len(app_units) >= 2:
        names = ", ".join(sorted(app_units)[:4])
        hints.append(
            {
                "path": "apps/",
                "hint": "multiple app units",
                "detail": f"multiple app folders are present: {names}",
            }
        )
    if top_dir_set & {"k8s", "helm", "deploy", "terraform", "infra", "ops"}:
        names = ", ".join(
            sorted(top_dir_set & {"k8s", "helm", "deploy", "terraform", "infra", "ops"})
        )
        hints.append(
            {
                "path": names,
                "hint": "deployment topology surface",
                "detail": "infra or deployment directories may reveal runtime boundaries",
            }
        )
    if top_dir_set & {"consumers", "publishers", "queues", "topics"}:
        hints.append(
            {
                "path": ", ".join(
                    sorted(
                        top_dir_set & {"consumers", "publishers", "queues", "topics"}
                    )
                ),
                "hint": "message topology surface",
                "detail": "messaging directories suggest event or queue boundaries are first-class",
            }
        )
    if top_dir_set & {"dags", "workflows", "pipelines", "jobs", "etl"}:
        hints.append(
            {
                "path": ", ".join(
                    sorted(
                        top_dir_set & {"dags", "workflows", "pipelines", "jobs", "etl"}
                    )
                ),
                "hint": "workflow topology surface",
                "detail": "workflow directories suggest stage or job boundaries dominate execution",
            }
        )
    return hints[:12]


def collect_signal_map(
    top_dirs: list[str],
    text_files: list[Path],
    root: Path,
    coverage: ScanCoverage,
    read_cache: dict[Path, str],
    read_limit: int,
    dependency_hints: list[dict[str, str]] | None = None,
    runtime_hints: list[dict[str, str]] | None = None,
    entrypoint_hints: list[dict[str, str]] | None = None,
) -> dict[str, SignalEntry]:
    signal_map: dict[str, SignalEntry] = {}
    path_hits: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    keyword_hits: dict[str, dict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )

    def ensure_signal(name: str) -> SignalEntry:
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
        rel_path = Path(rel)
        if should_use_path_markers(rel_path):
            path_parts = {part.lower() for part in rel_path.parts}
            for signal_name, markers in ARCHITECTURE_MARKERS.items():
                overlap = sorted(path_parts & markers)
                if overlap:
                    marker = overlap[0]
                    if len(path_hits[signal_name][marker]) < 2:
                        path_hits[signal_name][marker].append(rel)

        if not should_scan_keywords(rel_path):
            continue
        text = read_text(path, coverage, read_cache, read_limit)
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
            if len(entry["evidence"]) < 10:
                entry["evidence"].append(f"path marker {marker}: {paths[0]}")

    for signal_name, matches in keyword_hits.items():
        entry = ensure_signal(signal_name)
        entry["score"] += min(len(matches), 4)
        for match, paths in list(matches.items())[:4]:
            if len(entry["evidence"]) < 10:
                entry["evidence"].append(f"{paths[0]}: {match}")

    for hint in dependency_hints or []:
        entry = ensure_signal(hint["signal"])
        if hint["effect"] == "supports":
            entry["score"] += 2
        else:
            entry["score"] -= 2
        if len(entry["evidence"]) < 10:
            entry["evidence"].append(
                f"dependency hint: {hint['path']} ({hint['detail']})"
            )

    for hint in runtime_hints or []:
        detail = hint["detail"]
        if "service runtime units" in hint["hint"]:
            entry = ensure_signal("microservice")
            entry["score"] += 6
            entry["evidence"].append(f"runtime hint: {detail}")
        if "local orchestration surface" in hint["hint"]:
            entry = ensure_signal("microservice")
            entry["score"] += 1
            if len(entry["evidence"]) < 10:
                entry["evidence"].append(f"runtime hint: {detail}")
        if "multiple app units" in hint["hint"]:
            entry = ensure_signal("modular-monolith")
            entry["score"] += 1
            entry["evidence"].append(f"runtime hint: {detail}")
        if "message topology" in hint["hint"]:
            entry = ensure_signal("event-driven")
            entry["score"] += 3
            entry["evidence"].append(f"runtime hint: {detail}")
        if "workflow topology" in hint["hint"]:
            entry = ensure_signal("pipeline")
            entry["score"] += 3
            entry["evidence"].append(f"runtime hint: {detail}")

    for hint in entrypoint_hints or []:
        if hint["hint"] == "ui entrypoint":
            entry = ensure_signal("component-ui")
            entry["score"] += 1
            if len(entry["evidence"]) < 10:
                entry["evidence"].append(f"entrypoint hint: {hint['path']}")
    return signal_map


def sorted_signals(signal_map: dict[str, SignalEntry]) -> list[SignalEntry]:
    values = list(signal_map.values())
    return sorted(values, key=lambda item: (-int(item["score"]), str(item["name"])))


def collect_subsystem_hints(root: Path, top_dirs: list[str]) -> list[dict[str, str]]:
    hints: list[dict[str, str]] = []
    interesting = {
        "apps",
        "services",
        "packages",
        "libs",
        "modules",
        "plugins",
        "extensions",
        "cmd",
        "internal",
    }
    for name in top_dirs:
        if name.lower() not in interesting:
            continue
        path = root / name
        try:
            children = [
                entry.name
                for entry in path.iterdir()
                if entry.is_dir() and entry.name not in IGNORE_DIRS
            ][:10]
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


def infer_repo_kind(
    manifest_counts: Counter,
    top_dirs: list[str],
    signals: list[SignalEntry],
) -> tuple[list[dict[str, str]], list[str]]:
    counts: Counter = Counter(manifest_counts)
    normalized_dirs = {entry.lower() for entry in top_dirs}
    counts["plugin"] = len(
        {"plugins", "extensions", "hooks", "providers"} & normalized_dirs
    )
    counts["pipeline"] = len(
        {"pipelines", "dags", "jobs", "workflows", "etl"} & normalized_dirs
    )
    counts["apps_dir"] = len({"apps", "services", "packages"} & normalized_dirs)
    counts["service_like"] = len(
        {"app", "apps", "api", "apis", "service", "services", "worker", "workers"}
        & normalized_dirs
    )
    counts["frontend_like"] = len(
        {"web", "frontend", "ui", "client", "components", "pages", "views", "screens"}
        & normalized_dirs
    )
    counts["cli_like"] = len({"cmd", "bin", "scripts", "tools"} & normalized_dirs)
    counts["infra_like"] = len(
        {"terraform", "helm", "k8s", "ops", "deploy", "infra"} & normalized_dirs
    )
    counts["library_like"] = len({"src", "lib", "include", "pkg"} & normalized_dirs)

    hints: list[dict[str, str]] = []
    gaps: list[str] = []
    for repo_kind, rule in REPO_KIND_RULES:
        if rule(counts):
            reason = []
            if repo_kind == "plugin-extension":
                reason.append("plugin or extension directories are present")
            elif repo_kind == "data-pipeline":
                reason.append("pipeline and workflow directories dominate the repo")
            elif repo_kind == "monorepo-platform":
                reason.append("workspace manifests or multi-app containers are present")
            elif repo_kind == "infra-ops":
                reason.append("infra or deployment directories are prominent")
            elif repo_kind == "cli-tooling":
                reason.append("tooling entrypoints dominate the repo")
            elif repo_kind == "application-service":
                if counts["frontend_like"] >= 2 and counts["service_like"] < 2:
                    reason.append("frontend or UI app directories dominate the repo")
                else:
                    reason.append("application or service directories are prominent")
            elif repo_kind == "library-sdk":
                reason.append("library-style source roots are present")
            hints.append({"repo_kind": repo_kind, "reason": "; ".join(reason)})

    if not hints:
        gaps.append(
            "repo kind is weakly signaled; inspect entrypoints and packaging surfaces manually"
        )
    if not signals:
        gaps.append(
            "architecture signals are sparse; inspect representative modules manually"
        )
    if signals and int(signals[0]["score"]) <= 2:
        gaps.append("top architecture signal is weak; avoid high-confidence claims")

    return hints[:3], gaps


def collect_focus_path_observations(
    root: Path,
    focus_paths: list[str],
    text_files: list[Path],
    coverage: ScanCoverage,
    read_cache: dict[Path, str],
    read_limit: int,
    repo_signals: list[SignalEntry],
) -> list[dict[str, object]]:
    observations: list[dict[str, object]] = []
    repo_top_signal = str(repo_signals[0]["name"]) if repo_signals else None
    for raw_path in focus_paths:
        candidate = (root / raw_path).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            observations.append(
                {
                    "path": raw_path,
                    "exists": False,
                    "reason": "focus path escapes repo root",
                }
            )
            continue
        if not candidate.exists():
            observations.append(
                {"path": raw_path, "exists": False, "reason": "focus path not found"}
            )
            continue

        selected_text_files: list[Path] = []
        if candidate.is_dir():
            selected_text_files = [
                path for path in text_files if candidate in path.parents
            ]
            try:
                focus_dirs = sorted(
                    entry.name
                    for entry in candidate.iterdir()
                    if entry.is_dir() and entry.name not in IGNORE_DIRS
                )
            except OSError:
                focus_dirs = []
            kind = "dir"
        else:
            selected_text_files = [candidate] if is_text_file(candidate) else []
            focus_dirs = []
            kind = "file"

        focus_signal_map = collect_signal_map(
            top_dirs=focus_dirs,
            text_files=selected_text_files,
            root=root,
            coverage=coverage,
            read_cache=read_cache,
            read_limit=read_limit,
        )
        top_signals = sorted_signals(focus_signal_map)[:3]
        note = "focus slice aligns with repo-wide signal"
        if (
            top_signals
            and repo_top_signal
            and str(top_signals[0]["name"]) != repo_top_signal
        ):
            note = "focus slice differs from repo-wide signal; treat it as a local exception"
        observations.append(
            {
                "path": raw_path,
                "exists": True,
                "kind": kind,
                "top_signals": top_signals,
                "note": note,
            }
        )
    return observations


def main() -> int:
    args = parse_args()
    root = Path(args.repo_path).expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"repo path does not exist: {root}")
    if not root.is_dir():
        raise SystemExit(f"repo path is not a directory: {root}")

    coverage = ScanCoverage()
    read_cache: dict[Path, str] = {}
    files, text_files = collect_files(root, coverage)
    top_dirs = collect_top_level_dirs(root)
    manifests, manifest_counts = collect_manifests(files, root)
    docs_claims = collect_docs_claims(
        text_files, root, coverage, read_cache, args.read_limit
    )
    dependency_hints = collect_dependency_direction_hints(
        text_files,
        root,
        coverage,
        read_cache,
        args.read_limit,
    )
    entrypoint_hints = collect_entrypoint_hints(files, root)
    runtime_hints = collect_runtime_boundary_hints(files, top_dirs, root)
    signal_map = collect_signal_map(
        top_dirs,
        text_files,
        root,
        coverage,
        read_cache,
        args.read_limit,
        dependency_hints=dependency_hints,
        runtime_hints=runtime_hints,
        entrypoint_hints=entrypoint_hints,
    )
    signals = sorted_signals(signal_map)
    subsystem_hints = collect_subsystem_hints(root, top_dirs)
    repo_kind_hints, confidence_gaps = infer_repo_kind(
        manifest_counts, top_dirs, signals
    )
    focus_path_observations = collect_focus_path_observations(
        root,
        args.focus_path,
        text_files,
        coverage,
        read_cache,
        args.read_limit,
        signals,
    )

    if not manifests:
        confidence_gaps.append("no common manifest file was detected")
    if not docs_claims:
        confidence_gaps.append(
            "no architecture claim was detected in README or architecture docs"
        )
    if len(top_dirs) < 2:
        confidence_gaps.append(
            "very few top-level directories were available for structural inference"
        )
    if coverage.total_files_seen > coverage.files_considered:
        confidence_gaps.append(
            f"file scan hit the {MAX_FILES} file cap; large-repo conclusions may be partial"
        )
    if coverage.total_text_files_seen > coverage.text_files_considered:
        confidence_gaps.append(
            f"text scan hit the {MAX_TEXT_FILES} file cap; keyword and dependency evidence may be partial"
        )
    if any(hint["effect"] == "weakens" for hint in dependency_hints):
        confidence_gaps.append(
            "dependency-direction hints contain at least one architecture contradiction"
        )

    payload = {
        "repo_path": str(root),
        "requested_focus_paths": args.focus_path,
        "scan_coverage": {
            "total_files_seen": coverage.total_files_seen,
            "total_text_files_seen": coverage.total_text_files_seen,
            "files_considered": coverage.files_considered,
            "text_files_considered": coverage.text_files_considered,
            "truncated_reads": coverage.truncated_reads,
            "read_errors": coverage.read_errors,
            "read_limit": args.read_limit,
        },
        "evidence_summary": {
            "manifests": len(manifests),
            "entrypoint_hints": len(entrypoint_hints),
            "dependency_direction_hints": len(dependency_hints),
            "runtime_boundary_hints": len(runtime_hints),
            "subsystem_hints": len(subsystem_hints),
            "docs_claims": len(docs_claims),
            "focus_path_observations": len(focus_path_observations),
        },
        "repo_kind_hints": repo_kind_hints,
        "manifests": manifests,
        "top_level_dirs": top_dirs,
        "entrypoint_hints": entrypoint_hints,
        "dependency_direction_hints": dependency_hints,
        "runtime_boundary_hints": runtime_hints,
        "architecture_signals": signals,
        "subsystem_hints": subsystem_hints,
        "focus_path_observations": focus_path_observations,
        "docs_claims": docs_claims,
        "confidence_gaps": sorted(dict.fromkeys(confidence_gaps)),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
