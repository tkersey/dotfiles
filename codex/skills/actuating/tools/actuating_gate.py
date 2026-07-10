#!/usr/bin/env python3
"""Validate actuation runs/resolutions and derive live closure decisions."""

from __future__ import annotations

import argparse
import copy
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
SEMANTICS_PATH = ROOT / "references" / "live-semantics.yaml"
OBLIGATION_HANDLERS: dict[str, Any] = {}
REVIEW_FOLD_TOOLS = ROOT.parent / "review-fold" / "tools"
sys.path.insert(0, str(REVIEW_FOLD_TOOLS))

from review_fold_receipt_gate import validate as validate_review_fold_receipt  # noqa: E402


def canonical_json(value: Any) -> str:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as error:
        raise ValueError("input contains non-JSON values") from error


def load_data(path: str) -> dict[str, Any]:
    source = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    value = json.loads(source) if path.endswith(".json") else yaml.safe_load(source)
    if not isinstance(value, dict):
        raise ValueError("input must be an object")
    canonical_json(value)
    return value


def unwrap(value: dict[str, Any], key: str) -> dict[str, Any]:
    candidate = value.get(key, value)
    if not isinstance(candidate, dict):
        raise ValueError(f"{key} must be an object")
    return candidate


def canonical_digest(value: Any) -> str:
    payload = canonical_json(value)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def string_list(value: Any) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        return []
    return value


def has_exact_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def object_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def has_exact_object_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, dict) for item in value)


def git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        message = result.stderr.decode("utf-8", "replace").strip()
        raise ValueError(message or "git command failed")
    return result.stdout


def git_root(repo: Path) -> Path:
    return Path(
        git(repo, "rev-parse", "--show-toplevel")
        .decode("utf-8", "surrogateescape")
        .strip()
    ).resolve()


def json_command(repo: Path, *argv: str) -> dict[str, Any]:
    result = subprocess.run(
        argv,
        cwd=git_root(repo),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        message = result.stderr.decode("utf-8", "replace").strip()
        raise ValueError(message or f"{argv[0]} command failed")
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ValueError(f"{argv[0]} returned invalid JSON") from error
    if not isinstance(value, dict):
        raise ValueError(f"{argv[0]} output must be an object")
    return value


def live_cas_list(repo: Path, base_sha: str, codex_thread_id: str) -> dict[str, Any]:
    return json_command(
        repo,
        "cas",
        "review_session",
        "list",
        "--cwd",
        str(git_root(repo)),
        "--base",
        base_sha,
        "--codex-thread-id",
        codex_thread_id,
        "--json",
    )


def live_pr_metadata(repo: Path, pr_url: str) -> dict[str, Any]:
    repository = json_command(repo, "gh", "repo", "view", "--json", "nameWithOwner,url")
    pull_request = json_command(
        repo,
        "gh",
        "pr",
        "view",
        pr_url,
        "--json",
        "url,baseRefName,baseRefOid,headRefName,headRefOid,headRepository,isDraft,state",
    )
    return {"repository": repository, "pull_request": pull_request}


def append_frame(payload: bytearray, label: bytes, value: bytes) -> None:
    payload.extend(len(label).to_bytes(4, "big"))
    payload.extend(label)
    payload.extend(len(value).to_bytes(8, "big"))
    payload.extend(value)


def entry_map(output: bytes) -> dict[str, bytes]:
    entries: dict[str, bytearray] = {}
    for row in (item for item in output.split(b"\0") if item):
        metadata, separator, raw_path = row.partition(b"\t")
        if not separator:
            continue
        path = raw_path.decode("utf-8", "surrogateescape")
        append_frame(entries.setdefault(path, bytearray()), b"entry", metadata)
    return {path: bytes(payload) for path, payload in entries.items()}


def gitlink_paths(output: bytes) -> set[str]:
    result: set[str] = set()
    for row in (item for item in output.split(b"\0") if item):
        metadata, separator, raw_path = row.partition(b"\t")
        if separator and metadata.startswith(b"160000 "):
            result.add(raw_path.decode("utf-8", "surrogateescape"))
    return result


def gitlink_worktree_entry(repo: Path, path: str) -> bytes:
    source = repo / path
    try:
        mode = source.lstat().st_mode.to_bytes(8, "big")
    except FileNotFoundError:
        return b"missing"
    if not source.is_dir():
        raise ValueError(f"gitlink worktree is not a directory: {path}")
    if not (source / ".git").exists():
        if any(source.iterdir()):
            raise ValueError(f"uninitialized gitlink contains files: {path}")
        return b"uninitialized"

    top = Path(
        git(source, "rev-parse", "--show-toplevel")
        .decode("utf-8", "surrogateescape")
        .strip()
    ).resolve()
    if top != source.resolve():
        raise ValueError(f"gitlink worktree root mismatch: {path}")
    head = git(source, "rev-parse", "HEAD").strip()
    payload = bytearray()
    append_frame(payload, b"gitlink-head", mode + head)
    append_frame(
        payload,
        b"gitlink-status",
        git(
            source,
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
            "--ignore-submodules=none",
        ),
    )
    append_frame(
        payload,
        b"gitlink-diff",
        git(source, "diff", "--binary", "--ignore-submodules=none", "HEAD", "--"),
    )
    append_frame(
        payload,
        b"gitlink-index",
        git(source, "diff", "--cached", "--binary", "HEAD", "--"),
    )
    untracked = git(source, "ls-files", "--others", "--exclude-standard", "-z")
    for raw_path in sorted(item for item in untracked.split(b"\0") if item):
        nested = raw_path.decode("utf-8", "surrogateescape")
        append_frame(payload, raw_path, worktree_entry(source, nested))
    return bytes(payload)


def worktree_entry(repo: Path, path: str) -> bytes:
    source = repo / path
    try:
        mode = source.lstat().st_mode.to_bytes(8, "big")
    except FileNotFoundError:
        return b"missing"
    if source.is_symlink():
        kind = b"symlink"
        content = str(source.readlink()).encode("utf-8", "surrogateescape")
    elif source.is_file():
        kind = b"file"
        content = source.read_bytes()
    else:
        kind = b"nonregular"
        content = b""
    payload = bytearray()
    append_frame(payload, kind, mode + content)
    return bytes(payload)


def live_changed_paths(repo: Path, base_sha: str) -> set[str]:
    repo = git_root(repo)
    outputs = [
        git(
            repo,
            "diff",
            "--no-renames",
            "--ignore-submodules=none",
            "--name-only",
            "-z",
            base_sha,
            "--",
        ),
        git(
            repo,
            "diff",
            "--no-renames",
            "--cached",
            "--ignore-submodules=none",
            "--name-only",
            "-z",
            base_sha,
            "--",
        ),
        git(repo, "ls-files", "--others", "--exclude-standard", "-z"),
    ]
    return {
        item.decode("utf-8", "surrogateescape")
        for output in outputs
        for item in output.split(b"\0")
        if item
    }


def live_path_states(repo: Path, base_sha: str) -> dict[str, str]:
    """Return the live base/HEAD/index/worktree digest for every changed path."""
    repo = git_root(repo)
    paths = live_changed_paths(repo, base_sha)
    base_entries = entry_map(git(repo, "ls-tree", "-r", "-z", base_sha))
    head_entries = entry_map(git(repo, "ls-tree", "-r", "-z", "HEAD"))
    raw_index = git(repo, "ls-files", "--stage", "-z")
    index_entries = entry_map(raw_index)
    index_gitlinks = gitlink_paths(raw_index)
    paths.update(index_gitlinks)
    result: dict[str, str] = {}
    for path in sorted(paths):
        payload = bytearray()
        append_frame(payload, b"base", base_entries.get(path, b"missing"))
        append_frame(payload, b"head", head_entries.get(path, b"missing"))
        append_frame(payload, b"index", index_entries.get(path, b"missing"))
        worktree = (
            gitlink_worktree_entry(repo, path)
            if path in index_gitlinks
            else worktree_entry(repo, path)
        )
        append_frame(payload, b"worktree", worktree)
        result[path] = "sha256:" + hashlib.sha256(payload).hexdigest()
    return result


def state_fingerprint(path_states: dict[str, str]) -> str:
    payload = bytearray()
    for path, digest in sorted(path_states.items()):
        append_frame(
            payload,
            path.encode("utf-8", "surrogateescape"),
            digest.encode("ascii"),
        )
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def diff_hunk_ids(repo: Path, layer: str, *args: str) -> list[str]:
    output = git(
        repo,
        "-c",
        "core.quotePath=false",
        "diff",
        "--no-renames",
        "--unified=0",
        "--no-ext-diff",
        "--no-color",
        "--ignore-submodules=none",
        *args,
        "--",
    ).decode("utf-8", "surrogateescape")
    current = ""
    source = ""
    hunks: dict[str, list[str]] = {}
    for line in output.splitlines():
        if line.startswith("--- "):
            value = line[4:]
            source = value[2:] if value.startswith("a/") else ""
        elif line.startswith("+++ "):
            value = line[4:]
            current = value[2:] if value.startswith("b/") else source
        elif line.startswith("@@ ") and current:
            coordinate = line.split("@@", 2)[1].strip()
            hunks.setdefault(current, []).append(
                f"{current}:{layer}:@@ {coordinate} @@"
            )
    changed = {
        item.decode("utf-8", "surrogateescape")
        for item in git(
            repo,
            "diff",
            "--ignore-submodules=none",
            "--name-only",
            "-z",
            *args,
            "--",
        ).split(b"\0")
        if item
    }
    for path in changed:
        hunks.setdefault(path, [f"{path}:{layer}:metadata"])
    return [hunk for values in hunks.values() for hunk in values]


def live_hunk_ids(repo: Path, base_sha: str) -> list[str]:
    """Return a stable, exhaustive inventory of current diff hunks."""
    repo = git_root(repo)
    hunks = diff_hunk_ids(repo, "index", "--cached", base_sha)
    hunks.extend(diff_hunk_ids(repo, "worktree"))
    untracked = {
        item.decode("utf-8", "surrogateescape")
        for item in git(repo, "ls-files", "--others", "--exclude-standard", "-z").split(
            b"\0"
        )
        if item
    }
    for path in untracked:
        hunks.append(f"{path}:untracked")
    return sorted(hunks)


def live_artifact(repo: Path, base_sha: str) -> dict[str, str]:
    repo = git_root(repo)
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    branch = git(repo, "branch", "--show-current").decode().strip()
    git(repo, "cat-file", "-e", f"{base_sha}^{{commit}}")
    fingerprint = state_fingerprint(live_path_states(repo, base_sha))
    return {
        "repo": str(repo),
        "base_sha": base_sha,
        "branch": branch,
        "head_sha": head,
        "state_fingerprint": fingerprint,
    }


def binding_errors(
    binding: Any, repo: Path, prefix: str
) -> tuple[list[str], dict[str, str]]:
    if not isinstance(binding, dict):
        return [f"{prefix}-missing"], {}
    base = text(binding.get("base_sha"))
    if not base:
        return [f"{prefix}-base-missing"], {}
    try:
        current = live_artifact(repo, base)
    except ValueError:
        return [f"{prefix}-base-invalid"], {}
    errors = artifact_observer_errors(repo)
    errors.extend(
        [
        f"{prefix}-stale:{key}"
        for key in ("repo", "base_sha", "branch", "head_sha", "state_fingerprint")
        if text(binding.get(key)) != current[key]
        ]
    )
    return errors, current


def load_semantics() -> dict[str, Any]:
    return unwrap(load_data(str(SEMANTICS_PATH)), "live_semantics")


def semantic_contract_errors(semantics: dict[str, Any]) -> list[str]:
    isomorphism = semantics.get("isomorphism")
    rows = (
        object_list(isomorphism.get("live_obligations"))
        if isinstance(isomorphism, dict)
        else []
    )
    declared = {
        text(row.get("obligation_id")): text(row.get("handler"))
        for row in rows
        if text(row.get("obligation_id"))
    }
    if set(declared) != set(OBLIGATION_HANDLERS):
        return ["blocked-semantic-contract"]
    if any(
        declared[obligation_id] != handler.__name__
        for obligation_id, handler in OBLIGATION_HANDLERS.items()
    ):
        return ["blocked-semantic-contract"]
    return []


def review_contract_payload(
    change_surfaces: list[str],
    selected_lenses: list[str],
    semantics: dict[str, Any],
) -> dict[str, Any]:
    contracts = semantics.get("lens_contracts", {})
    return {
        "version": "review-contract/v1",
        "change_surfaces": sorted(set(change_surfaces)),
        "selected_lenses": sorted(set(selected_lenses)),
        "lens_contracts": {
            lens: contracts.get(lens)
            for lens in sorted(set(selected_lenses))
            if isinstance(contracts, dict)
        },
        "semantic_non_growth": True,
    }


def expected_review_admission(
    review_resolution: dict[str, Any],
    review_source_refs: list[str],
    changed_paths: list[str],
    hunk_ids: list[str],
    ship_receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "version": "review-admission/v1",
        "review_resolution": copy.deepcopy(review_resolution),
        "observations": {
            "review_source_refs": copy.deepcopy(review_source_refs),
            "changed_paths": copy.deepcopy(changed_paths),
            "hunk_ids": copy.deepcopy(hunk_ids),
        },
        "ship_receipt": copy.deepcopy(ship_receipt),
    }
    return {**payload, "admission_digest": canonical_digest(payload)}


def review_admission_errors(value: Any, step: dict[str, Any]) -> list[str]:
    if not isinstance(value, dict):
        return ["blocked-resolution-binding"]
    review_resolution = value.get("review_resolution")
    observations = value.get("observations")
    review_source_refs = (
        observations.get("review_source_refs")
        if isinstance(observations, dict)
        else None
    )
    changed_paths = (
        observations.get("changed_paths") if isinstance(observations, dict) else None
    )
    hunk_ids = observations.get("hunk_ids") if isinstance(observations, dict) else None
    ship_receipt = value.get("ship_receipt")
    if (
        not isinstance(review_resolution, dict)
        or not isinstance(observations, dict)
        or not has_exact_string_list(review_source_refs)
        or not has_exact_string_list(changed_paths)
        or not has_exact_string_list(hunk_ids)
        or len(review_source_refs) != len(set(review_source_refs))
        or len(changed_paths) != len(set(changed_paths))
        or len(hunk_ids) != len(set(hunk_ids))
        or (ship_receipt is not None and not isinstance(ship_receipt, dict))
    ):
        return ["blocked-resolution-binding"]
    expected = expected_review_admission(
        review_resolution,
        review_source_refs,
        changed_paths,
        hunk_ids,
        ship_receipt,
    )
    historical_run = {
        "run_id": step.get("run_id"),
        "artifact": step.get("state_before"),
    }
    try:
        resolution_problems, _ = _resolution_contract_errors(
            review_resolution,
            _admission_resolution_facts(
                step,
                review_source_refs,
                changed_paths,
                hunk_ids,
            ),
        )
        ship_problems = (
            static_ship_errors(ship_receipt, historical_run)[0]
            if ship_receipt is not None
            else []
        )
    except ValueError:
        return ["blocked-resolution-binding"]
    if value != expected or resolution_problems or ship_problems:
        return ["blocked-resolution-binding"]
    return []


def artifact_observer_errors(repo: Path, *, nested: bool = False) -> list[str]:
    repo = git_root(repo)
    errors: set[str] = set()
    for row in git(repo, "ls-files", "-v", "-z").split(b"\0"):
        tag, separator, _ = row.partition(b" ")
        if separator and (tag == b"S" or tag.islower()):
            errors.add("blocked-index-observer-flags")
    gitlinks = gitlink_paths(git(repo, "ls-files", "--stage", "-z")) | gitlink_paths(
        git(repo, "ls-tree", "-rz", "HEAD", "--")
    )
    for directory, child_dirs, files in os.walk(
        repo,
        onerror=lambda _: errors.add("blocked-nested-gitlink-observer"),
    ):
        current = Path(directory)
        marker_present = ".git" in child_dirs or ".git" in files
        if ".git" in child_dirs:
            child_dirs.remove(".git")
        if current == repo or not marker_present:
            continue
        path = current.relative_to(repo).as_posix()
        if path not in gitlinks:
            errors.add("blocked-nested-gitlink-observer")
    if nested and gitlinks:
        errors.add("blocked-nested-gitlink-observer")
        return sorted(errors)
    for path in gitlinks:
        source = repo / path
        if source.is_dir() and (source / ".git").exists():
            errors.update(artifact_observer_errors(source, nested=True))
    return sorted(errors)


def path_allowed(path: str, allowed: list[str], repo: Path) -> bool:
    parts = Path(path).parts
    if (
        not path
        or Path(path).is_absolute()
        or path.rstrip("/") == "."
        or any(part == ".." or part.casefold() == ".git" for part in parts)
    ):
        return False
    root = repo.resolve()
    candidate = root
    for part in parts:
        candidate /= part
        if candidate.is_symlink():
            return False
    try:
        candidate.resolve(strict=False).relative_to(root)
    except ValueError:
        return False
    normalized = path.rstrip("/")
    return any(
        path_allowed_root(allowed_root, repo)
        and (
            allowed_root.rstrip("/") == "."
            or normalized == allowed_root.rstrip("/")
            or normalized.startswith(allowed_root.rstrip("/") + "/")
        )
        for allowed_root in allowed
    )


def paths_overlap(left: str, right: str, repo: Path) -> bool:
    """Observe symmetric target overlap without reusing mutation admission."""
    left_parts = Path(left).parts
    right_parts = Path(right).parts
    if (
        not left_parts
        or not right_parts
        or Path(left).is_absolute()
        or Path(right).is_absolute()
        or ".." in left_parts
        or ".." in right_parts
    ):
        return False

    def is_prefix(prefix: tuple[str, ...], value: tuple[str, ...]) -> bool:
        return len(prefix) <= len(value) and prefix == value[: len(prefix)]

    if is_prefix(left_parts, right_parts) or is_prefix(right_parts, left_parts):
        return True

    left_folded = tuple(part.casefold() for part in left_parts)
    right_folded = tuple(part.casefold() for part in right_parts)
    if is_prefix(left_folded, right_folded):
        shorter, corresponding = left_parts, right_parts[: len(left_parts)]
    elif is_prefix(right_folded, left_folded):
        shorter, corresponding = right_parts, left_parts[: len(right_parts)]
    else:
        return False

    differing = [
        index
        for index, (first, second) in enumerate(zip(shorter, corresponding))
        if first != second
    ]
    if not differing:
        return False
    required_length = max(differing) + 1
    root = repo.resolve()
    for length in range(len(shorter), required_length - 1, -1):
        try:
            if (root.joinpath(*shorter[:length])).samefile(
                root.joinpath(*corresponding[:length])
            ):
                return True
        except OSError:
            continue
    return False


def path_allowed_root(path: str, repo: Path | None = None) -> bool:
    parts = Path(path).parts
    lexical = (
        bool(path)
        and not Path(path).is_absolute()
        and not any(part == ".." or part.casefold() == ".git" for part in parts)
    )
    if not lexical or repo is None or path.rstrip("/") == ".":
        return lexical
    root = repo.resolve()
    candidate = root
    for part in parts:
        candidate /= part
        if candidate.is_symlink():
            return False
    try:
        candidate.resolve(strict=False).relative_to(root)
    except ValueError:
        return False
    return True


def validate_run(
    run: dict[str, Any],
    repo: Path,
    resolution: dict[str, Any] | None = None,
    evidence_values: list[dict[str, Any]] | None = None,
    *,
    admission_check: bool = True,
) -> tuple[list[str], dict[str, Any]]:
    repo = git_root(repo)
    errors: list[str] = []
    semantics = load_semantics()
    errors.extend(semantic_contract_errors(semantics))
    modes = set((semantics.get("modes") or {}).keys())
    execution_kinds = set(semantics.get("execution_kinds") or [])
    step_effects = set(semantics.get("step_effects") or [])

    if run.get("version") != "actuation-run/v1":
        errors.append("blocked-run-version")
    run_id = text(run.get("run_id"))
    if not run_id:
        errors.append("blocked-run-id-missing")
    mode = text(run.get("mode"))
    if mode not in modes:
        errors.append("blocked-run-mode")
    review_value = run.get("review")
    review_required = (
        isinstance(review_value, dict) and review_value.get("required") is True
    )

    source = run.get("source")
    if not isinstance(source, dict):
        errors.append("blocked-authority-missing")
        source = {}
    source_kind = text(source.get("kind"))
    if source_kind not in set(semantics.get("source_kinds") or []):
        errors.append("blocked-source-kind")
    for key in ("scope_source_ref", "execution_authority_ref"):
        if not text(source.get(key)):
            errors.append(f"blocked-authority-missing:{key}")
    if source.get("current") is not True:
        errors.append("blocked-authority-stale")
    owner = text(source.get("authority_owner"))
    if source_kind == "direct-goal" and owner != "user":
        errors.append("blocked-wrong-authority-owner")
    if source_kind == "accepted-spec":
        if owner != "spec-pipeline":
            errors.append("blocked-wrong-authority-owner")
        if source.get("governance_state") != "complete":
            errors.append("blocked-source-not-executable")

    authority = run.get("authority")
    if not isinstance(authority, dict):
        errors.append("blocked-authority-missing")
        authority = {}
    expected_mutation = mode in {"implement", "review-closeout"}
    if authority.get("mutation_allowed") is not expected_mutation:
        errors.append("blocked-authority-mode-mismatch")
    if authority.get("unsupported_coordination_required") is not False:
        errors.append("blocked-unsupported-controller")
    allowed_paths_raw = authority.get("allowed_paths")
    allowed_paths = string_list(allowed_paths_raw)
    if not has_exact_string_list(allowed_paths_raw):
        errors.append("blocked-authority-paths-invalid")
    if not allowed_paths:
        errors.append("blocked-authority-paths-missing")
    if any(not path_allowed_root(path, repo) for path in allowed_paths):
        errors.append("blocked-authority-paths-invalid")
    public_raw = authority.get("public_effects_allowed")
    public_allowed = string_list(public_raw)
    if not has_exact_string_list(public_raw):
        errors.append("blocked-public-effect-shape")
    if any(effect != "ship-handoff" for effect in public_allowed):
        errors.append("blocked-public-effect-owner")

    binding_problems, current = binding_errors(run.get("artifact"), repo, "blocked-run")
    errors.extend(binding_problems)
    initial = run.get("artifact_initial")
    if not isinstance(initial, dict) or any(
        not text(initial.get(key))
        for key in (
            "repo",
            "base_sha",
            "branch",
            "head_sha",
            "state_fingerprint",
        )
    ):
        errors.append("blocked-run-initial-artifact")
        initial = {}
    initial_path_states = run.get("artifact_initial_path_states")
    if not isinstance(initial_path_states, dict) or any(
        not isinstance(path, str)
        or not path_allowed_root(path)
        or not isinstance(digest, str)
        or len(digest) != 71
        or not digest.startswith("sha256:")
        for path, digest in (
            initial_path_states.items() if isinstance(initial_path_states, dict) else []
        )
    ):
        errors.append("blocked-run-initial-artifact")
        initial_path_states = {}
    if initial and state_fingerprint(initial_path_states) != initial.get(
        "state_fingerprint"
    ):
        errors.append("blocked-run-initial-artifact")
    if initial and current and any(
        initial.get(key) != current.get(key) for key in ("repo", "base_sha", "branch")
    ):
        errors.append("blocked-run-stale")
    current_path_states: dict[str, str] = {}
    live_paths: set[str] = set()
    if current:
        try:
            current_path_states = live_path_states(repo, current["base_sha"])
            live_paths = live_changed_paths(repo, current["base_sha"])
        except ValueError:
            errors.append("blocked-run-initial-artifact")
    if initial == current and current:
        if initial_path_states != current_path_states:
            errors.append("blocked-run-initial-artifact")

    execution = run.get("execution")
    if not isinstance(execution, dict):
        errors.append("blocked-execution-missing")
        execution = {}
    kind = text(execution.get("kind"))
    if kind not in execution_kinds:
        errors.append("blocked-execution-kind")
    if mode in {"triage", "remediation-plan"} and kind != "none":
        errors.append("blocked-no-code-mutation")
    if expected_mutation and kind == "none":
        errors.append("blocked-step-missing")

    steps_raw = execution.get("steps")
    steps = object_list(steps_raw)
    if steps_raw is not None and (
        not isinstance(steps_raw, list) or len(steps) != len(steps_raw)
    ):
        errors.append("blocked-step-shape")
    if kind == "none" and steps:
        errors.append("blocked-no-code-mutation")
    if kind == "direct" and len(steps) > 1:
        errors.append("blocked-direct-step-count")
    if expected_mutation and not steps:
        errors.append("blocked-step-missing")

    selected_id = execution.get("selected_step_id")
    selected = [step for step in steps if step.get("status") == "selected"]
    if selected_id is None and selected:
        errors.append("blocked-step-selection-mismatch")
    if selected_id is not None:
        if len(selected) != 1 or text(selected[0].get("step_id")) != selected_id:
            errors.append("blocked-step-selection-mismatch")
    if len(selected) > 1:
        errors.append("blocked-step-selection-multiple")

    seen_ids: set[str] = set()
    previous_after: dict[str, Any] | None = None
    completed_steps: list[dict[str, Any]] = []
    review_admission_candidate: dict[str, Any] | None = None
    for index, step in enumerate(steps):
        if index > 0:
            prior = steps[index - 1]
            prior_admission = prior.get("review_admission")
            current_ship = (
                review_value.get("ship_receipt")
                if isinstance(review_value, dict)
                else None
            )
            fresh_ship_continuation = bool(
                prior.get("verdict") == "ready-for-closure"
                and isinstance(review_value, dict)
                and review_value.get("publication_requested") is True
                and isinstance(prior_admission, dict)
                and isinstance(prior_admission.get("ship_receipt"), dict)
                and isinstance(current_ship, dict)
                and canonical_digest(current_ship)
                != canonical_digest(prior_admission["ship_receipt"])
                and not ship_epoch_continuity_errors(
                    prior_admission["ship_receipt"], current_ship
                )
            )
            if prior.get("status") != "completed" or not (
                prior.get("verdict") == "continue" or fresh_ship_continuation
            ):
                errors.append("blocked-step-continuation")
        step_id = text(step.get("step_id"))
        if not step_id or step_id in seen_ids:
            errors.append("blocked-step-id")
        seen_ids.add(step_id)
        if text(step.get("run_id")) != run_id:
            errors.append("blocked-step-run-mismatch")
        if step.get("selected_by") != "lead":
            errors.append("blocked-step-owner")
        if not text(step.get("owner_boundary")):
            errors.append("blocked-step-owner-boundary")
        verifier = string_list(step.get("verifier"))
        if not has_exact_string_list(step.get("verifier")) or not verifier:
            errors.append("blocked-step-verifier")
        effect = text(step.get("effect"))
        if effect not in step_effects:
            errors.append("blocked-step-effect")
        review_admission = step.get("review_admission")
        step_paths_raw = step.get("paths")
        changed_paths_raw = step.get("changed_paths")
        step_paths = string_list(step_paths_raw)
        changed_paths = string_list(changed_paths_raw)
        if not has_exact_string_list(step_paths_raw) or not has_exact_string_list(
            changed_paths_raw
        ):
            errors.append("blocked-step-shape")
        if len(changed_paths) != len(set(changed_paths)):
            errors.append("blocked-step-change-mismatch")
        if not step_paths:
            errors.append("blocked-step-paths-missing")
        if any(not path_allowed(path, allowed_paths, repo) for path in step_paths):
            errors.append("blocked-step-out-of-scope")
        if any(not path_allowed(path, allowed_paths, repo) for path in changed_paths):
            errors.append("blocked-step-out-of-scope")
        if any(not path_allowed(path, step_paths, repo) for path in changed_paths):
            errors.append("blocked-step-change-mismatch")
        performed = step.get("performed_public_effects")
        if not has_exact_object_list(performed):
            errors.append("blocked-public-effect-shape")
        elif performed:
            errors.append("blocked-public-effect-owner")
        if step.get("parent_completion_claimed") is not False:
            errors.append("blocked-closure-owner")
        before = step.get("state_before")
        if not isinstance(before, dict):
            errors.append("blocked-step-stale")
            before = {}
        if index == 0 and before != initial:
            errors.append("blocked-step-chain")
        if previous_after is not None and before != previous_after:
            errors.append("blocked-step-chain")
        status = text(step.get("status"))
        if status == "selected":
            if index != len(steps) - 1:
                errors.append("blocked-step-order")
            if current and any(before.get(key) != current[key] for key in current):
                errors.append("blocked-step-stale")
            if changed_paths:
                errors.append("blocked-step-incomplete")
        elif status == "completed":
            if review_required and effect == "edit":
                errors.extend(review_admission_errors(review_admission, step))
            after = step.get("state_after")
            if not isinstance(after, dict):
                errors.append("blocked-step-incomplete")
                after = {}
            previous_after = after
            if effect == "edit" and not changed_paths:
                errors.append("blocked-step-change-mismatch")
            if effect == "edit":
                before_head = text(before.get("head_sha"))
                after_head = text(after.get("head_sha"))
                stable_artifact_keys = ("repo", "base_sha", "branch")
                artifact_transition_valid = not (
                    not before_head
                    or not after_head
                    or any(before.get(key) != after.get(key) for key in stable_artifact_keys)
                )
                commit_transition_valid = False
                if not artifact_transition_valid:
                    errors.append("blocked-step-change-mismatch")
                elif before_head != after_head:
                    try:
                        subprocess.run(
                            [
                                "git",
                                "merge-base",
                                "--is-ancestor",
                                before_head,
                                after_head,
                            ],
                            cwd=repo,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            check=True,
                        )
                        commit_transition_valid = True
                    except subprocess.CalledProcessError:
                        errors.append("blocked-step-change-mismatch")
                if kind == "iterative":
                    if not commit_transition_valid:
                        errors.append("blocked-step-change-mismatch")
                    else:
                        try:
                            observed_paths = {
                                path.decode("utf-8", "surrogateescape")
                                for path in git(
                                    repo,
                                    "diff",
                                    "--ignore-submodules=none",
                                    "--no-renames",
                                    "--name-only",
                                    "-z",
                                    before_head,
                                    after_head,
                                    "--",
                                ).split(b"\0")
                                if path
                            }
                        except ValueError:
                            observed_paths = None
                        if observed_paths != set(changed_paths):
                            errors.append("blocked-step-change-mismatch")
            if effect != "edit" and (changed_paths or after != before):
                errors.append("blocked-step-change-mismatch")
            evidence_ref = text(step.get("evidence_fold_ref"))
            if not evidence_ref:
                errors.append("blocked-evidence-fold-missing")
            else:
                completed_steps.append(
                    {
                        "step_id": step_id,
                        "run_id": text(step.get("run_id")),
                        "evidence_ref": evidence_ref,
                        "artifact": after,
                        "verdict": text(step.get("verdict")),
                        "effect": effect,
                        "changed_paths": changed_paths,
                        "owner_boundary": text(step.get("owner_boundary")),
                        "paths": step_paths,
                        "verifier": verifier,
                        "state_before": before,
                        "review_admission": review_admission,
                    }
                )
            if text(step.get("verdict")) not in {
                "continue",
                "ready-for-closure",
                "blocked",
                "regress",
                "invalid-proof",
            }:
                errors.append("blocked-step-verdict")
        elif status == "blocked":
            previous_after = before
        else:
            errors.append("blocked-step-status")

    if steps and not selected and previous_after is not None and current:
        if any(previous_after.get(key) != current[key] for key in current):
            errors.append("blocked-step-stale")
        claimed_paths = {
            path for step in steps for path in string_list(step.get("changed_paths"))
        }
        newly_changed = {
            path
            for path in set(initial_path_states) | set(current_path_states)
            if initial_path_states.get(path) != current_path_states.get(path)
        }
        if (kind == "direct" and newly_changed != claimed_paths) or (
            kind == "iterative" and not newly_changed.issubset(claimed_paths)
        ):
            errors.append("blocked-step-change-mismatch")
    if not steps and current and initial != current:
        errors.append("blocked-run-initial-artifact")

    review = review_value
    if not isinstance(review, dict):
        errors.append("blocked-review-profile-missing")
        review = {}
    required = review.get("required")
    if not isinstance(required, bool):
        errors.append("blocked-review-required-shape")
    if mode == "review-closeout" and required is not True:
        errors.append("blocked-review-required-shape")
    if mode == "implement" and required is True:
        errors.append("blocked-review-required-shape")
    if required is True and not text(review.get("codex_thread_id")):
        errors.append("blocked-review-source-missing")
    if mode in {"triage", "remediation-plan", "review-closeout"} or required:
        source_refs = review.get("source_refs")
        if not has_exact_string_list(source_refs) or not string_list(source_refs):
            errors.append("blocked-review-source-missing")
    if type(review.get("publication_requested")) is not bool:
        errors.append("blocked-publication-intent")
    if (
        mode in {"triage", "remediation-plan"}
        and review.get("publication_requested") is True
    ):
        errors.append("blocked-publication-intent")
    if (
        review.get("publication_requested") is True
        and "ship-handoff" not in public_allowed
    ):
        errors.append("blocked-publication-intent")
    ship_receipt = review.get("ship_receipt")
    if (
        mode == "review-closeout"
        and review.get("publication_requested") is True
    ):
        if not isinstance(ship_receipt, dict):
            errors.append("blocked-ship-missing")
        elif selected:
            try:
                ship_problems, _ = ship_errors(ship_receipt, run)
            except ValueError:
                ship_problems = ["blocked-ship-binding"]
            errors.extend(ship_problems)
    elif ship_receipt is not None:
        errors.append("blocked-unexpected-input")
    for completed in completed_steps:
        admission = completed.get("review_admission")
        if (
            completed.get("effect") == "edit"
            and isinstance(admission, dict)
            and (admission.get("ship_receipt") is not None)
            is not (review.get("publication_requested") is True)
        ):
            errors.append("blocked-resolution-binding")
    prior_publication = next(
        (
            completed["review_admission"]["ship_receipt"]
            for completed in reversed(completed_steps)
            if completed.get("effect") == "edit"
            and isinstance(completed.get("review_admission"), dict)
            and isinstance(
                completed["review_admission"].get("ship_receipt"), dict
            )
        ),
        None,
    )
    if (
        isinstance(prior_publication, dict)
        and isinstance(ship_receipt, dict)
        and canonical_digest(prior_publication) != canonical_digest(ship_receipt)
    ):
        errors.extend(ship_epoch_continuity_errors(prior_publication, ship_receipt))

    if admission_check and mode == "review-closeout" and selected:
        if resolution is None:
            errors.append("blocked-review-resolution-missing")
        else:
            resolution_errors, resolution_derived = validate_resolution(
                run, resolution, repo
            )
            errors.extend(resolution_errors)
            selected_step = selected[0]
            if not resolution_errors:
                admission = selected_step.get("review_admission")
                expected_admission = expected_review_admission(
                    resolution,
                    string_list(review.get("source_refs")),
                    string_list(resolution_derived.get("live_changed_paths")),
                    string_list(resolution_derived.get("live_hunk_ids")),
                    ship_receipt if isinstance(ship_receipt, dict) else None,
                )
                review_admission_candidate = expected_admission
                if admission is not None and admission != expected_admission:
                    errors.append("blocked-resolution-binding")
    elif admission_check and resolution is not None and mode != "review-closeout":
        errors.append("blocked-unexpected-input")

    if admission_check and selected and completed_steps:
        if not evidence_values:
            errors.append("blocked-evidence-fold-missing")
        else:
            evidence_problems, _ = evidence_errors(
                evidence_values, run, completed_steps
            )
            errors.extend(evidence_problems)
    final_run_errors, _ = binding_errors(run.get("artifact"), repo, "blocked-run")
    errors.extend(final_run_errors)

    derived = {
        "run_digest": canonical_digest(run),
        "current_artifact": current,
        "completed_steps": completed_steps,
        "selected_step_id": selected_id,
        "review_admission": review_admission_candidate if not errors else None,
        "has_blocked_step": any(step.get("status") == "blocked" for step in steps),
        "live_changed_paths": sorted(live_paths),
    }
    return sorted(set(errors)), derived


def resolution_digest_payload(resolution: dict[str, Any]) -> dict[str, Any]:
    outcome = (
        resolution.get("outcome") if isinstance(resolution.get("outcome"), dict) else {}
    )
    balance = (
        outcome.get("semantic_balance")
        if isinstance(outcome.get("semantic_balance"), dict)
        else {}
    )
    return {
        "version": resolution.get("version"),
        "resolution_id": resolution.get("resolution_id"),
        "run_id": resolution.get("run_id"),
        "artifact": resolution.get("artifact"),
        "review_folds": resolution.get("review_folds"),
        "finding_ids": resolution.get("finding_ids"),
        "change_surfaces": resolution.get("change_surfaces"),
        "review_profile": resolution.get("review_profile"),
        "decisions": resolution.get("decisions"),
        "outcome_status": outcome.get("status"),
        "semantic_balance": balance,
    }


def validate_review_folds(
    run: dict[str, Any], value: Any
) -> tuple[list[str], dict[str, dict[str, str]]]:
    errors: list[str] = []
    if not has_exact_object_list(value) or not value:
        return ["blocked-review-fold-missing"], {}
    folds = [unwrap(item, "review_fold") for item in value]
    fold_ids: list[str] = []
    fold_source_refs: list[str] = []
    finding_ids: list[str] = []
    material: dict[str, dict[str, str]] = {}
    artifact = run.get("artifact") if isinstance(run.get("artifact"), dict) else {}
    for fold in folds:
        if validate_review_fold_receipt(fold):
            errors.append("blocked-review-fold-invalid")
        if fold.get("version") != "RF-v2":
            errors.append("blocked-review-fold-version")
        fold_id = text(fold.get("fold_id"))
        fold_ids.append(fold_id)
        if not fold_id or text(fold.get("goal_id")) != text(run.get("run_id")):
            errors.append("blocked-review-fold-binding")
        source = fold.get("source") if isinstance(fold.get("source"), dict) else {}
        fold_source_refs.append(text(source.get("source_ref")))
        source_artifact = (
            source.get("artifact") if isinstance(source.get("artifact"), dict) else {}
        )
        if any(
            source_artifact.get(key) != artifact.get(key)
            for key in ("repo", "base_sha", "branch", "head_sha", "state_fingerprint")
        ):
            errors.append("blocked-review-fold-stale")
        state = text(source.get("source_state"))
        findings_raw = fold.get("findings")
        findings = object_list(findings_raw)
        if not has_exact_object_list(findings_raw):
            errors.append("blocked-review-fold-shape")
        if state == "clean" and findings:
            errors.append("blocked-review-fold-shape")
        if state == "findings" and not findings:
            errors.append("blocked-review-fold-shape")
        if state not in {"clean", "findings"}:
            errors.append("blocked-review-fold-open")
        for finding in findings:
            finding_id = text(finding.get("finding_id"))
            finding_ids.append(finding_id)
            if not finding_id:
                errors.append("blocked-review-fold-finding")
            authority = finding.get("mutation_authority")
            if not isinstance(authority, dict) or authority.get("allowed") is not False:
                errors.append("blocked-review-fold-authority")
            disposition = finding.get("disposition")
            if disposition == "blocked":
                errors.append("blocked-review-fold-open")
            if disposition == "resolution-input":
                owner = text(finding.get("owner_boundary"))
                liability = text(finding.get("liability"))
                if (
                    finding.get("validity") != "valid"
                    or finding.get("intent_relation") not in {"core", "adjacent"}
                    or liability in {"style", "new-requirement", "out-of-scope"}
                    or not owner
                    or not liability
                ):
                    errors.append("blocked-review-fold-finding")
                material[finding_id] = {
                    "owner_boundary": owner,
                    "liability": liability,
                }
    if len(fold_ids) != len(set(fold_ids)) or len(finding_ids) != len(set(finding_ids)):
        errors.append("blocked-review-fold-duplicate")
    review = run.get("review") if isinstance(run.get("review"), dict) else {}
    declared_source_refs = string_list(review.get("source_refs"))
    if len(fold_source_refs) != len(set(fold_source_refs)) or sorted(
        fold_source_refs
    ) != sorted(declared_source_refs):
        errors.append("blocked-review-fold-source")
    return sorted(set(errors)), material


def _resolution_contract_errors(
    resolution: dict[str, Any],
    facts: dict[str, Any],
) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    semantics = facts["semantics"]
    run = {
        "run_id": facts.get("run_id"),
        "artifact": facts.get("artifact"),
        "mode": facts.get("mode"),
        "review": {"source_refs": facts.get("review_source_refs")},
    }
    changed_paths = string_list(facts.get("changed_paths"))
    expected_hunks = string_list(facts.get("hunk_ids"))
    allowed_node_bindings = object_list(facts.get("allowed_node_bindings"))
    admitted_node_binding = facts.get("admitted_node_binding")
    if resolution.get("version") != "review-resolution/v1":
        errors.append("blocked-review-resolution-version")
    if not text(resolution.get("resolution_id")):
        errors.append("blocked-review-resolution-id")
    if text(resolution.get("run_id")) != text(run.get("run_id")):
        errors.append("blocked-review-resolution-run")
    if resolution.get("artifact") != run.get("artifact"):
        errors.append("blocked-review-resolution-stale")

    fold_errors, resolution_inputs = validate_review_folds(
        run, resolution.get("review_folds")
    )
    errors.extend(fold_errors)
    if any(
        finding.get("disposition") == "ask-human"
        for fold in object_list(resolution.get("review_folds"))
        for finding in object_list(unwrap(fold, "review_fold").get("findings"))
    ):
        errors.append("blocked-review-fold-open")
    finding_ids_raw = resolution.get("finding_ids")
    finding_ids = string_list(finding_ids_raw)
    if not has_exact_string_list(finding_ids_raw):
        errors.append("blocked-resolution-finding-shape")
    if len(finding_ids) != len(set(finding_ids)):
        errors.append("blocked-resolution-finding-duplicate")
    if set(finding_ids) != set(resolution_inputs):
        errors.append("blocked-resolution-finding-coverage")

    decisions_raw = resolution.get("decisions")
    decisions = object_list(decisions_raw)
    if not has_exact_object_list(decisions_raw):
        errors.append("blocked-resolution-decisions")
    surfaces_raw = resolution.get("change_surfaces")
    surfaces = string_list(surfaces_raw)
    if not has_exact_string_list(surfaces_raw):
        errors.append("blocked-review-surface")
    known_surfaces = set((semantics.get("change_surfaces") or {}).keys())
    if any(surface not in known_surfaces for surface in surfaces):
        errors.append("blocked-review-surface")
    effective_surfaces = set(surfaces)
    if len(changed_paths) > 1:
        effective_surfaces.add("multi-live-path")
    if any(decision.get("strategy") == "replacement-kernel" for decision in decisions):
        effective_surfaces.add("replacement-kernel")
    expected_surfaces = sorted(effective_surfaces)
    expected_lenses = ["standard"]
    profile = resolution.get("review_profile")
    if not isinstance(profile, dict):
        errors.append("blocked-review-profile-missing")
        profile = {}
    lenses_raw = profile.get("selected_lenses")
    selected_lenses = sorted(set(string_list(lenses_raw)))
    if not has_exact_string_list(lenses_raw):
        errors.append("blocked-review-lens-selection")
    if selected_lenses != expected_lenses:
        errors.append("blocked-review-lens-selection")
    expected_contract = canonical_digest(
        review_contract_payload(expected_surfaces, selected_lenses, semantics)
    )
    if text(profile.get("review_contract_fingerprint")) != expected_contract:
        errors.append("blocked-cas-contract-mismatch")

    outcome = resolution.get("outcome")
    if not isinstance(outcome, dict):
        errors.append("blocked-resolution-outcome")
        outcome = {}
    outcome_status = text(outcome.get("status"))
    if outcome_status not in {"pending", "clean", "resolved", "blocked"}:
        errors.append("blocked-resolution-status")

    covered: list[str] = []
    covered_liabilities: list[str] = []
    decision_ids: list[str] = []
    selected_nodes: list[str] = []
    selected_bindings: list[dict[str, Any]] = []
    retired_abstractions: set[str] = set()
    retained_abstractions: set[str] = set()
    account_owners: dict[tuple[str, str], list[tuple[str, str]]] = {}
    strategies = set(semantics.get("strategies") or [])
    dispositions = set(semantics.get("abstraction_dispositions") or [])
    for decision in decisions:
        decision_id = text(decision.get("decision_id"))
        decision_ids.append(decision_id)
        if not decision_id:
            errors.append("blocked-resolution-decision-id")
        strategy = text(decision.get("strategy"))
        if strategy not in strategies:
            errors.append("blocked-resolution-strategy")
        ids = string_list(decision.get("finding_ids"))
        if not ids:
            errors.append("blocked-resolution-finding-coverage")
        covered.extend(ids)
        liability_classes = string_list(decision.get("liability_classes"))
        if not liability_classes:
            errors.append("blocked-resolution-liability-class")
        covered_liabilities.extend(liability_classes)
        owner_boundary = text(decision.get("owner_boundary"))
        if not owner_boundary:
            errors.append("blocked-resolution-binding")
        source_owners = {
            resolution_inputs[finding_id]["owner_boundary"]
            for finding_id in ids
            if finding_id in resolution_inputs
        }
        source_liabilities = {
            resolution_inputs[finding_id]["liability"]
            for finding_id in ids
            if finding_id in resolution_inputs
        }
        if source_owners != {owner_boundary} or source_liabilities != set(
            liability_classes
        ):
            errors.append("blocked-resolution-binding")
        if not string_list(decision.get("alternatives_considered")):
            errors.append("blocked-resolution-alternatives")
        if not text(decision.get("falsifier")):
            errors.append("blocked-resolution-falsifier")
        account_raw = decision.get("abstraction_account")
        account = object_list(account_raw)
        if not has_exact_object_list(account_raw) or not account:
            errors.append("blocked-abstraction-account")
        for row in account:
            abstraction = text(row.get("abstraction"))
            if not abstraction:
                errors.append("blocked-abstraction-account")
            disposition = text(row.get("disposition"))
            if disposition not in dispositions:
                errors.append("blocked-abstraction-disposition")
            if disposition == "retain" and not text(row.get("obligation_id")):
                errors.append("blocked-abstraction-retain")
            if disposition == "retain" and abstraction:
                retained_abstractions.add(abstraction)
            obligation_id = text(row.get("obligation_id"))
            if abstraction and obligation_id:
                account_owners.setdefault((abstraction, obligation_id), []).append(
                    (strategy, disposition)
                )
            if disposition in {"retire", "collapse", "replace"} and abstraction:
                retired_abstractions.add(abstraction)
        node = decision.get("selected_work_node")
        if strategy in {"local-repair", "replacement-kernel"}:
            if text(run.get("mode")) == "remediation-plan":
                if node not in (None, {}):
                    errors.append("blocked-no-code-mutation")
            elif not isinstance(node, dict) and outcome_status != "pending":
                errors.append("blocked-resolution-node-missing")
            elif isinstance(node, dict):
                if text(node.get("run_id")) != text(run.get("run_id")):
                    errors.append("blocked-resolution-binding")
                if text(node.get("owner_boundary")) != text(
                    decision.get("owner_boundary")
                ):
                    errors.append("blocked-resolution-binding")
                if not string_list(node.get("paths")) or not string_list(
                    node.get("verifier")
                ):
                    errors.append("blocked-resolution-binding")
                node_paths = string_list(node.get("paths"))
                node_id = text(node.get("node_id"))
                if not node_id:
                    errors.append("blocked-resolution-node-id")
                selected_nodes.append(node_id)
                binding = {
                    "node_id": node_id,
                    "owner_boundary": text(node.get("owner_boundary")),
                    "paths": node_paths,
                    "verifier": string_list(node.get("verifier")),
                }
                selected_bindings.append(binding)
                if binding not in allowed_node_bindings:
                    errors.append("blocked-resolution-out-of-scope")
        elif node not in (None, {}):
            errors.append("blocked-resolution-disposition")
        if strategy == "blocked" and not string_list(decision.get("blockers")):
            errors.append("blocked-resolution-blocker-missing")

    if len(decision_ids) != len(set(decision_ids)):
        errors.append("blocked-resolution-decision-id")
    if len(selected_nodes) != len(set(selected_nodes)):
        errors.append("blocked-resolution-node-id")
    if len(selected_nodes) > 1 and outcome_status != "resolved":
        errors.append("blocked-resolution-node-multiple")
    if isinstance(admitted_node_binding, dict):
        if outcome_status != "pending" or selected_bindings != [
            admitted_node_binding
        ]:
            errors.append("blocked-resolution-node-unexecuted")
    if retained_abstractions & retired_abstractions:
        errors.append("blocked-abstraction-disposition")
    if sorted(covered) != sorted(finding_ids) or len(covered) != len(set(covered)):
        errors.append("blocked-resolution-finding-coverage")

    has_blocked_decision = any(
        decision.get("strategy") == "blocked" for decision in decisions
    )
    if has_blocked_decision and selected_nodes:
        errors.append("blocked-resolution-node-under-blocker")
    if has_blocked_decision != (outcome_status == "blocked"):
        errors.append("blocked-resolution-status-inconsistent")
    if finding_ids and outcome_status == "clean":
        errors.append("blocked-resolution-status-inconsistent")
    balance = outcome.get("semantic_balance")
    if not isinstance(balance, dict):
        errors.append("blocked-semantic-balance")
        balance = {}
    for key in (
        "accounted_hunks",
        "unaccounted_hunks",
        "covered_liabilities",
        "uncovered_liabilities",
        "required_retirements",
        "completed_retirements",
        "dominated_remaining",
    ):
        if not isinstance(balance.get(key), list):
            errors.append(f"blocked-semantic-balance:{key}")
    accounted_hunks = string_list(balance.get("accounted_hunks"))
    if len(accounted_hunks) != len(set(accounted_hunks)):
        errors.append("blocked-semantic-hunks")
    if sorted(accounted_hunks) != expected_hunks:
        errors.append("blocked-semantic-hunks")
    if balance.get("unaccounted_hunks"):
        errors.append("blocked-semantic-hunks")
    if balance.get("uncovered_liabilities"):
        errors.append("blocked-semantic-liabilities")
    required_retirements = set(string_list(balance.get("required_retirements")))
    completed_retirements = set(string_list(balance.get("completed_retirements")))
    retirement_debt = required_retirements - completed_retirements
    dominated_remaining = set(string_list(balance.get("dominated_remaining")))
    if completed_retirements - required_retirements:
        errors.append("blocked-semantic-retirements")
    if outcome_status == "pending":
        if dominated_remaining != retirement_debt:
            errors.append("blocked-semantic-dominated")
    elif retirement_debt or dominated_remaining:
        errors.append("blocked-semantic-retirements")
    if retired_abstractions - required_retirements:
        errors.append("blocked-semantic-retirements")
    additions_raw = balance.get("added_constructs")
    additions = object_list(additions_raw)
    if not has_exact_object_list(additions_raw):
        errors.append("blocked-semantic-addition")
    addition_names: list[str] = []
    replaced_constructs: set[str] = set()
    for row in additions:
        if not all(
            text(row.get(key))
            for key in ("name", "obligation_id", "obligation_ref", "replaces")
        ):
            errors.append("blocked-semantic-addition")
        addition_names.append(text(row.get("name")))
        replaces = text(row.get("replaces"))
        obligation_id = text(row.get("obligation_id"))
        replaced_constructs.add(replaces)
        owners = account_owners.get((replaces, obligation_id), [])
        if len(owners) != 1 or owners[0][1] != "replace":
            errors.append("blocked-semantic-addition")
        elif owners[0][0] == "local-repair":
            errors.append("blocked-local-repair-growth")
    if len(addition_names) != len(set(addition_names)):
        errors.append("blocked-semantic-addition")
    if not replaced_constructs.issubset(required_retirements):
        errors.append("blocked-semantic-retirements")
    if required_retirements != retired_abstractions | replaced_constructs:
        errors.append("blocked-semantic-retirements")
    balance_liabilities = string_list(balance.get("covered_liabilities"))
    if len(balance_liabilities) != len(set(balance_liabilities)) or sorted(
        set(balance_liabilities)
    ) != sorted(set(covered_liabilities)):
        errors.append("blocked-semantic-liabilities")
    if (
        any(decision.get("strategy") == "replacement-kernel" for decision in decisions)
        and not required_retirements
    ):
        errors.append("blocked-replacement-retirement")

    expected_digest = canonical_digest(resolution_digest_payload(resolution))
    if text(outcome.get("resolution_digest")) != expected_digest:
        errors.append("blocked-review-resolution-digest")
    return sorted(set(errors)), {
        "resolution_id": text(resolution.get("resolution_id")),
        "review_contract_fingerprint": expected_contract,
        "resolution_digest": expected_digest,
        "change_surfaces": expected_surfaces,
        "selected_lenses": selected_lenses,
        "selected_work_nodes": selected_nodes,
        "selected_work_bindings": selected_bindings,
        "live_changed_paths": changed_paths,
        "live_hunk_ids": expected_hunks,
    }


def _node_binding(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "node_id": text(value.get("node_id", value.get("step_id"))),
        "owner_boundary": text(value.get("owner_boundary")),
        "paths": string_list(value.get("paths")),
        "verifier": string_list(value.get("verifier")),
    }


def _resolution_nodes(resolution: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        node
        for decision in object_list(resolution.get("decisions"))
        if isinstance((node := decision.get("selected_work_node")), dict)
    ]


def _admission_resolution_facts(
    step: dict[str, Any],
    review_source_refs: list[str],
    changed_paths: list[str],
    hunk_ids: list[str],
) -> dict[str, Any]:
    binding = _node_binding(step)
    return {
        "semantics": load_semantics(),
        "run_id": step.get("run_id"),
        "artifact": step.get("state_before"),
        "mode": "review-closeout",
        "review_source_refs": review_source_refs,
        "changed_paths": changed_paths,
        "hunk_ids": hunk_ids,
        "allowed_node_bindings": [binding],
        "admitted_node_binding": binding,
    }


def _live_resolution_facts(
    run: dict[str, Any],
    resolution: dict[str, Any],
    repo: Path,
    run_derived: dict[str, Any],
) -> dict[str, Any]:
    authority = run.get("authority") if isinstance(run.get("authority"), dict) else {}
    allowed_paths = string_list(authority.get("allowed_paths"))
    allowed_node_bindings = [
        _node_binding(node)
        for node in _resolution_nodes(resolution)
        if all(
            path_allowed(path, allowed_paths, repo)
            for path in string_list(node.get("paths"))
        )
    ]
    execution = run.get("execution") if isinstance(run.get("execution"), dict) else {}
    selected = [
        step
        for step in object_list(execution.get("steps"))
        if step.get("status") == "selected"
    ]
    artifact = run.get("artifact") if isinstance(run.get("artifact"), dict) else {}
    try:
        hunk_ids = live_hunk_ids(repo, text(artifact.get("base_sha")))
    except ValueError:
        hunk_ids = []
    review = run.get("review") if isinstance(run.get("review"), dict) else {}
    return {
        "semantics": load_semantics(),
        "run_id": run.get("run_id"),
        "artifact": artifact,
        "mode": run.get("mode"),
        "review_source_refs": string_list(review.get("source_refs")),
        "changed_paths": run_derived.get("live_changed_paths", []),
        "hunk_ids": hunk_ids,
        "allowed_node_bindings": allowed_node_bindings,
        "admitted_node_binding": (
            _node_binding(selected[0])
            if len(selected) == 1 and selected[0].get("effect") == "edit"
            else ({} if selected else None)
        ),
    }


def validate_resolution(
    run: dict[str, Any],
    resolution: dict[str, Any],
    repo: Path,
) -> tuple[list[str], dict[str, Any]]:
    repo = git_root(repo)
    errors, run_derived = validate_run(run, repo, admission_check=False)
    contract_errors, contract_derived = _resolution_contract_errors(
        resolution,
        _live_resolution_facts(run, resolution, repo, run_derived),
    )
    errors.extend(contract_errors)
    outcome = resolution.get("outcome")
    if isinstance(outcome, dict) and outcome.get("status") == "resolved":
        completed_steps = run_derived.get("completed_steps", [])
        for binding in contract_derived.get("selected_work_bindings", []):
            matches = [
                step
                for step in completed_steps
                if step.get("step_id") == binding["node_id"]
                and step.get("effect") == "edit"
                and step.get("owner_boundary") == binding["owner_boundary"]
                and step.get("paths") == binding["paths"]
                and step.get("verifier") == binding["verifier"]
                and not review_admission_errors(
                    step.get("review_admission"), step
                )
            ]
            if len(matches) != 1:
                errors.append("blocked-resolution-node-unexecuted")
    return sorted(set(errors)), {**run_derived, **contract_derived}


def normalize_cas(value: dict[str, Any]) -> dict[str, Any]:
    for key in ("cas_review_evidence_record", "review_evidence_record", "record"):
        if isinstance(value.get(key), dict):
            return value[key]
    return value


def cas_time_key(value: Any) -> int | None:
    if not isinstance(value, str):
        return None
    if value.startswith("unix-ns:"):
        try:
            return int(value.removeprefix("unix-ns:"))
        except ValueError:
            return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return int(parsed.timestamp() * 1_000_000_000)


def cas_errors(
    snapshot: dict[str, Any],
    run: dict[str, Any],
    resolution: dict[str, Any],
    derived: dict[str, Any],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    if (
        snapshot.get("schema") != "CAS-LIST-v1"
        or not has_exact_object_list(snapshot.get("records"))
        or not has_exact_object_list(snapshot.get("recordRefs"))
    ):
        return ["blocked-cas-evidence-set-incomplete"], []
    normalized = [normalize_cas(record) for record in snapshot["records"]]
    ref_rows = snapshot["recordRefs"]
    referenced_ids = {text(row.get("recordId")) for row in ref_rows}
    ref_credit = {
        text(row.get("recordId")): row.get("proofCreditEligible")
        for row in ref_rows
    }
    snapshot_ids = {text(row.get("recordId")) for row in normalized}
    if (
        referenced_ids != snapshot_ids
        or "" in referenced_ids
        or len(ref_rows) != len(referenced_ids)
        or any(type(value) is not bool for value in ref_credit.values())
    ):
        errors.append("blocked-cas-evidence-set-incomplete")
    expected_artifact = (
        run.get("artifact") if isinstance(run.get("artifact"), dict) else {}
    )
    expected_lenses = derived["selected_lenses"]
    expected_contract = derived["review_contract_fingerprint"]
    expected_resolution = derived["resolution_digest"]
    contracts = load_semantics().get("lens_contracts") or {}
    allowed_lanes = set(expected_lenses)
    folds_by_batch: dict[str, list[dict[str, Any]]] = {}
    for value in object_list(resolution.get("review_folds")):
        fold = unwrap(value, "review_fold")
        source = fold.get("source") if isinstance(fold.get("source"), dict) else {}
        source_batch_id = text(source.get("source_batch_id"))
        if source_batch_id:
            folds_by_batch.setdefault(source_batch_id, []).append(fold)
    valid: list[dict[str, Any]] = []
    record_ids: list[str] = []
    native_target_fingerprints: set[str] = set()
    for record in normalized:
        eligible = True

        def reject(code: str) -> None:
            nonlocal eligible
            errors.append(code)
            eligible = False

        if record.get("schema") != "CAS-RER-v1":
            errors.append("blocked-cas-record-version")
            continue
        record_id = text(record.get("recordId"))
        created_at = cas_time_key(record.get("createdAt"))
        tuple_value = (
            record.get("tuple") if isinstance(record.get("tuple"), dict) else {}
        )
        binding = record.get("workflowBinding")
        if (
            isinstance(binding, dict)
            and text(binding.get("actuationRunId"))
            and binding.get("actuationRunId") != run.get("run_id")
        ):
            continue
        command = (
            record.get("command") if isinstance(record.get("command"), dict) else {}
        )
        broker = (
            command.get("brokerDecision")
            if isinstance(command.get("brokerDecision"), dict)
            else {}
        )
        attempt = (
            record.get("attempt") if isinstance(record.get("attempt"), dict) else {}
        )
        verdict = (
            record.get("verdict") if isinstance(record.get("verdict"), dict) else {}
        )
        failure = (
            record.get("failure") if isinstance(record.get("failure"), dict) else {}
        )
        principal = (
            record.get("principal") if isinstance(record.get("principal"), dict) else {}
        )
        if not record_id or not record_id.startswith("rer_"):
            reject("blocked-cas-unit-id")
        if created_at is None:
            reject("blocked-cas-attempt-identity")
        if tuple_value.get("repoRealpath") != expected_artifact.get("repo"):
            reject("blocked-cas-unit-stale")
        for field, artifact_key in (
            ("baseSha", "base_sha"),
            ("headSha", "head_sha"),
        ):
            if tuple_value.get(field) != expected_artifact.get(artifact_key):
                reject("blocked-cas-unit-stale")
        native_target_fingerprint = text(tuple_value.get("targetFingerprint"))
        if not native_target_fingerprint:
            reject("blocked-cas-unit-stale")
        else:
            native_target_fingerprints.add(native_target_fingerprint)
        if tuple_value.get("tupleCurrentAtRecordTime") is not True:
            reject("blocked-cas-unit-stale")
        if not isinstance(binding, dict):
            reject("blocked-cas-workflow-unbound")
            continue
        if binding.get("actuationRunId") != run.get("run_id"):
            reject("blocked-cas-workflow-unbound")
            continue
        current_epoch = all(
            (
                binding.get("reviewContractFingerprint") == expected_contract,
                binding.get("resolutionDigest") == expected_resolution,
                binding.get("artifactStateFingerprint")
                == expected_artifact.get("state_fingerprint"),
            )
        )
        if not current_epoch:
            if verdict.get("status") == "findings":
                producer_findings = object_list(verdict.get("findings"))
                expected_source_refs = [
                    text(finding.get("findingId")) or f"{record_id}#{index}"
                    for index, finding in enumerate(producer_findings, start=1)
                ]
                matching_folds = folds_by_batch.get(record_id, [])
                classified = False
                if len(matching_folds) == 1:
                    fold = matching_folds[0]
                    source = (
                        fold.get("source")
                        if isinstance(fold.get("source"), dict)
                        else {}
                    )
                    fold_findings = object_list(fold.get("findings"))
                    actual_source_refs = [
                        text(finding.get("source_ref")) for finding in fold_findings
                    ]
                    classified = all(
                        (
                            source.get("backend") == "cas",
                            source.get("source_state") == "findings",
                            type(verdict.get("findingCount")) is int,
                            verdict.get("findingCount") == len(producer_findings),
                            len(expected_source_refs) == len(set(expected_source_refs)),
                            len(actual_source_refs) == len(set(actual_source_refs)),
                            sorted(actual_source_refs) == sorted(expected_source_refs),
                        )
                    )
                if not classified:
                    reject("blocked-cas-findings-unresolved")
            continue
        lenses = binding.get("selectedLenses")
        if (
            not isinstance(lenses, list)
            or lenses != sorted(set(string_list(lenses)))
            or lenses != expected_lenses
        ):
            reject("blocked-cas-contract-mismatch")
        lane = text(binding.get("reviewLane"))
        lens_contract = text(binding.get("lensContract"))
        attempt_id = text(attempt.get("attemptId"))
        if (
            not attempt_id
            or attempt.get("exists") is not True
            or text(attempt.get("reviewThreadId")) == ""
            or text(attempt.get("reviewTurnId")) == ""
            or attempt.get("phase") not in {"review_terminal", "normalized_verdict"}
        ):
            reject("blocked-cas-attempt-identity")
        if lane not in allowed_lanes:
            reject("blocked-cas-lane")
        if lens_contract != contracts.get(lane):
            reject("blocked-cas-contract-mismatch")
        findings = verdict.get("findings")
        finding_count = verdict.get("findingCount")
        status = verdict.get("status")
        if (
            verdict.get("tupleVerdictExists") is not True
            or status not in {"clean", "findings"}
            or not isinstance(findings, list)
            or type(finding_count) is not int
            or finding_count != len(findings)
            or verdict.get("clean") is not (status == "clean")
            or (status == "clean" and finding_count != 0)
            or (status == "findings" and finding_count <= 0)
        ):
            reject("blocked-cas-unit-unnormalized")
        elif status == "findings":
            reject("blocked-cas-findings-unresolved")
        if status == "clean" and ref_credit.get(record_id) is not True:
            eligible = False
        if any(
            failure.get(key) is not None
            for key in (
                "failureCode",
                "failureClass",
                "retryableSameTupleNow",
            )
        ):
            reject("blocked-cas-source-invalid")
        if (
            principal.get("kind") != "strong"
            or not text(principal.get("accountFingerprint"))
            or principal.get("proofUsable") is not True
            or principal.get("reduced") is not False
            or principal.get("fallbackUsed") is not False
            or not text(principal.get("source"))
            or principal.get("source") == "cas-native-fallback"
        ):
            reject("blocked-cas-source-invalid")
        fresh = broker.get("freshAttemptRequired")
        if not isinstance(fresh, bool):
            reject("blocked-cas-unit-replayed")
        if eligible:
            valid.append(
                {
                    "record_id": record_id,
                    "attempt_id": attempt_id,
                    "created_at": created_at,
                    "lane": lane,
                    "status": text(verdict.get("status")),
                    "fresh": fresh,
                }
            )
        record_ids.append(record_id)

    if len(record_ids) != len(set(record_ids)):
        errors.append("blocked-cas-unit-duplicate")
    if len(native_target_fingerprints) != 1:
        errors.append("blocked-cas-evidence-set-incomplete")
    attempt_ids = [row["attempt_id"] for row in valid]
    if len(attempt_ids) != len(set(attempt_ids)):
        errors.append("blocked-cas-unit-duplicate")
    created = [row["created_at"] for row in valid]
    if len(created) != len(set(created)):
        errors.append("blocked-cas-attempt-identity")

    ordered = sorted(valid, key=lambda row: (row["created_at"], row["record_id"]))
    if any(row["fresh"] is not True for row in ordered[1:]):
        errors.append("blocked-cas-unit-replayed")
    standard = [row for row in ordered if row["lane"] == "standard"]
    clean_suffix: list[dict[str, Any]] = []
    for row in reversed(standard):
        if row["status"] == "clean":
            clean_suffix.append(row)
        else:
            break
    if len(clean_suffix) < 3:
        errors.append("blocked-cas-clean-streak")

    basis = [row["record_id"] for row in reversed(clean_suffix[:3])]
    return sorted(set(errors)), basis


def normalize_evidence(value: dict[str, Any]) -> dict[str, Any]:
    return unwrap(value, "evidence_fold")


def evidence_errors(
    evidence_values: list[dict[str, Any]],
    run: dict[str, Any],
    completed_steps: list[dict[str, Any]],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    evidence = [normalize_evidence(value) for value in evidence_values]
    evidence_ids = [text(item.get("evidence_id")) for item in evidence]
    if any(not evidence_id for evidence_id in evidence_ids) or len(evidence_ids) != len(
        set(evidence_ids)
    ):
        errors.append("blocked-evidence-fold-identity")
    by_id = {
        text(item.get("evidence_id")): item
        for item in evidence
        if text(item.get("evidence_id"))
    }
    basis: list[str] = []
    expected_references = {
        text(completed.get("evidence_ref")) for completed in completed_steps
    }
    if set(by_id) != expected_references:
        errors.append("blocked-evidence-fold-orphan")
    for completed in completed_steps:
        reference = text(completed.get("evidence_ref"))
        item = by_id.get(reference)
        if item is None:
            errors.append("blocked-evidence-fold-missing")
            continue
        if item.get("version") != "EF-v1":
            errors.append("blocked-evidence-fold-version")
        if text(item.get("run_id")) != text(run.get("run_id")):
            errors.append("blocked-evidence-fold-mismatch")
        if text(item.get("step_id")) != text(completed.get("step_id")):
            errors.append("blocked-evidence-fold-mismatch")
        artifact = item.get("artifact_state")
        if not isinstance(artifact, dict) or any(
            artifact.get(key) != (completed.get("artifact") or {}).get(key)
            for key in (
                "repo",
                "base_sha",
                "branch",
                "head_sha",
                "state_fingerprint",
            )
        ):
            errors.append("blocked-evidence-fold-stale")
            artifact = {}
        observed_paths = string_list(artifact.get("changed_paths"))
        if len(observed_paths) != len(set(observed_paths)) or sorted(
            observed_paths
        ) != sorted(completed.get("changed_paths") or []):
            errors.append("blocked-evidence-fold-change-mismatch")
        evidence = item.get("evidence")
        if not isinstance(evidence, dict):
            errors.append("blocked-evidence-fold-shape")
            evidence = {}
        commands = (
            evidence.get("commands")
            if isinstance(evidence.get("commands"), dict)
            else {}
        )
        if (
            not isinstance(evidence.get("observed"), list)
            or not evidence.get("observed")
            or any(
                not isinstance(commands.get(key), list)
                for key in ("passed", "failed", "unavailable")
            )
            or not isinstance(evidence.get("artifacts_inspected"), list)
            or not evidence.get("artifacts_inspected")
            or not isinstance(evidence.get("review_refs"), list)
        ):
            errors.append("blocked-evidence-fold-shape")
        admission = completed.get("review_admission")
        if isinstance(admission, dict):
            admission_ref = f"review-admission:{text(admission.get('admission_digest'))}"
            if admission_ref not in string_list(evidence.get("review_refs")):
                errors.append("blocked-evidence-fold-mismatch")
        if (
            not string_list(commands.get("passed"))
            or commands.get("failed") != []
            or commands.get("unavailable") != []
        ):
            errors.append("blocked-evidence-fold-incomplete")
        if not set(completed.get("verifier") or []).issubset(
            set(string_list(commands.get("passed")))
        ):
            errors.append("blocked-evidence-fold-incomplete")
        progress = (
            item.get("progress") if isinstance(item.get("progress"), dict) else {}
        )
        recommendation = (
            item.get("recommendation")
            if isinstance(item.get("recommendation"), dict)
            else {}
        )
        if progress.get("status") != "done" or recommendation.get("action") != "stop":
            errors.append("blocked-evidence-fold-incomplete")
        proof = item.get("proof") if isinstance(item.get("proof"), dict) else {}
        if proof.get("supports_done_claim") != "yes" or proof.get("proof_gaps") != []:
            errors.append("blocked-evidence-fold-incomplete")
        if proof.get("stale_or_missing_artifact_binding") != "no":
            errors.append("blocked-evidence-fold-stale")
        anti = (
            item.get("anti_gaming") if isinstance(item.get("anti_gaming"), dict) else {}
        )
        if any(
            anti.get(key) != "no"
            for key in (
                "tests_deleted",
                "assertions_weakened",
                "checks_skipped",
                "coverage_reduced",
                "behavior_outside_goal_changed",
            )
        ):
            errors.append("blocked-evidence-anti-gaming")
        basis.append(reference)
    return sorted(set(errors)), basis


def static_ship_errors(
    ship_value: dict[str, Any],
    run: dict[str, Any],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    record = unwrap(ship_value, "ship_record")
    if record.get("record_version") != "SHIP-v1":
        errors.append("blocked-ship-version")
    artifact = run.get("artifact") if isinstance(run.get("artifact"), dict) else {}
    base_branch = text(record.get("base_branch"))
    if (
        record.get("source") != "actuation"
        or record.get("branch") != artifact.get("branch")
        or record.get("head_sha") != artifact.get("head_sha")
        or not base_branch
    ):
        errors.append("blocked-ship-binding")
    validation = (
        record.get("validation") if isinstance(record.get("validation"), dict) else {}
    )

    if any(
        validation.get(key) != "pass"
        for key in ("build", "lint", "tests", "language_specific", "acceptance")
    ):
        errors.append("blocked-ship-validation")
    readiness = (
        record.get("pr_readiness")
        if isinstance(record.get("pr_readiness"), dict)
        else {}
    )
    if readiness.get("mode") not in {
        "ready",
        "update-existing",
        "promote-draft",
    } or not text(readiness.get("reason")):
        errors.append("blocked-ship-readiness")
    existing = (
        record.get("existing_pr") if isinstance(record.get("existing_pr"), dict) else {}
    )
    if not isinstance(existing.get("exists"), bool):
        errors.append("blocked-ship-result")
    binding = record.get("actuation_binding")
    if not isinstance(binding, dict):
        return ["blocked-ship-binding"], []
    expected = {
        "actuation_run_id": run.get("run_id"),
        "state_fingerprint": artifact.get("state_fingerprint"),
    }
    if binding != expected:
        errors.append("blocked-ship-binding")
    action = record.get("action") if isinstance(record.get("action"), dict) else {}
    if action.get("result") not in {"created", "updated", "promoted"}:
        errors.append("blocked-ship-result")
    expected_readiness = {
        "created": "ready",
        "updated": "update-existing",
        "promoted": "promote-draft",
    }.get(action.get("result"))
    if expected_readiness != readiness.get("mode") or not text(action.get("command")):
        errors.append("blocked-ship-result")
    if action.get("result") == "created" and existing.get("exists") is not False:
        errors.append("blocked-ship-result")
    if action.get("result") in {"updated", "promoted"} and (
        existing.get("exists") is not True
        or not text(existing.get("url"))
        or existing.get("url") != action.get("pr_url")
    ):
        errors.append("blocked-ship-result")
    pr_url = text(action.get("pr_url"))
    if not pr_url:
        errors.append("blocked-ship-result")
    return sorted(set(errors)), [pr_url] if pr_url else []


def ship_epoch_continuity_errors(
    prior_ship: dict[str, Any],
    current_ship: dict[str, Any],
) -> list[str]:
    try:
        prior = unwrap(prior_ship, "ship_record")
        current = unwrap(current_ship, "ship_record")
    except ValueError:
        return ["blocked-ship-pr-continuity"]
    prior_action = (
        prior.get("action") if isinstance(prior.get("action"), dict) else {}
    )
    current_action = (
        current.get("action") if isinstance(current.get("action"), dict) else {}
    )
    readiness = (
        current.get("pr_readiness")
        if isinstance(current.get("pr_readiness"), dict)
        else {}
    )
    existing = (
        current.get("existing_pr")
        if isinstance(current.get("existing_pr"), dict)
        else {}
    )
    prior_url = text(prior_action.get("pr_url"))
    if (
        not prior_url
        or current_action.get("result") != "updated"
        or readiness.get("mode") != "update-existing"
        or existing.get("exists") is not True
        or existing.get("url") != prior_url
        or current_action.get("pr_url") != prior_url
    ):
        return ["blocked-ship-pr-continuity"]
    return []


def ship_errors(
    ship_value: dict[str, Any],
    run: dict[str, Any],
) -> tuple[list[str], list[str]]:
    errors, static_basis = static_ship_errors(ship_value, run)
    record = unwrap(ship_value, "ship_record")
    artifact = run.get("artifact") if isinstance(run.get("artifact"), dict) else {}
    base_branch = text(record.get("base_branch"))
    pr_url = static_basis[0] if static_basis else ""
    live_pr_valid = False
    if pr_url:
        try:
            metadata = live_pr_metadata(Path(text(artifact.get("repo"))), pr_url)
        except ValueError:
            errors.append("blocked-ship-live-pr-unavailable")
        else:
            repository = metadata.get("repository")
            pull_request = metadata.get("pull_request")
            head_repository = (
                pull_request.get("headRepository")
                if isinstance(pull_request, dict)
                and isinstance(pull_request.get("headRepository"), dict)
                else {}
            )
            if not isinstance(repository, dict) or not isinstance(pull_request, dict):
                errors.append("blocked-ship-live-pr-mismatch")
            elif any(
                (
                    pull_request.get("url") != pr_url,
                    not pr_url.startswith(
                        text(repository.get("url")).rstrip("/") + "/pull/"
                    ),
                    head_repository.get("nameWithOwner")
                    != repository.get("nameWithOwner"),
                    pull_request.get("baseRefName") != base_branch,
                    pull_request.get("baseRefOid") != artifact.get("base_sha"),
                    pull_request.get("headRefName") != artifact.get("branch"),
                    pull_request.get("headRefOid") != artifact.get("head_sha"),
                    pull_request.get("state") != "OPEN",
                    pull_request.get("isDraft") is not False,
                )
            ):
                errors.append("blocked-ship-live-pr-mismatch")
            else:
                live_pr_valid = True
    basis = [pr_url] if live_pr_valid else []
    return sorted(set(errors)), basis


def decide(
    run: dict[str, Any],
    resolution: dict[str, Any] | None,
    evidence_values: list[dict[str, Any]],
    cas_values: list[dict[str, Any]],
    ship_value: dict[str, Any] | None,
    repo: Path,
    review_fold_values: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], int]:
    repo = git_root(repo)
    run_errors, run_derived = validate_run(run, repo)
    errors = list(run_errors)
    mode = text(run.get("mode"))
    review = run.get("review") if isinstance(run.get("review"), dict) else {}
    review_required = bool(review.get("required"))
    completed_steps = run_derived.get("completed_steps", [])
    publication_requested = bool(review.get("publication_requested"))
    embedded_ship = review.get("ship_receipt")
    embedded_ship_digest = (
        canonical_digest(embedded_ship) if isinstance(embedded_ship, dict) else ""
    )
    last_published_edit = next(
        (
            step
            for step in reversed(completed_steps)
            if step.get("effect") == "edit"
            and isinstance(step.get("review_admission"), dict)
            and isinstance(step["review_admission"].get("ship_receipt"), dict)
        ),
        None,
    )
    last_publication_admission = (
        last_published_edit.get("review_admission")
        if isinstance(last_published_edit, dict)
        else {}
    )
    needs_reship = bool(
        mode == "review-closeout"
        and publication_requested
        and last_published_edit
        and embedded_ship_digest
        and embedded_ship_digest
        == canonical_digest(last_publication_admission.get("ship_receipt"))
        and (last_published_edit.get("artifact") or {}).get("state_fingerprint")
        != (last_published_edit.get("state_before") or {}).get(
            "state_fingerprint"
        )
    )
    triage_review_basis: list[str] = []
    triage_human = False
    if mode == "triage":
        triage_folds = review_fold_values or []
        fold_errors, _ = validate_review_folds(run, triage_folds)
        errors.extend(fold_errors)
        triage_human = any(
            finding.get("disposition") == "ask-human"
            for fold in triage_folds
            for finding in object_list(unwrap(fold, "review_fold").get("findings"))
        )
        triage_review_basis = [
            canonical_digest(unwrap(value, "review_fold")) for value in triage_folds
        ]
    elif review_fold_values:
        errors.append("blocked-unexpected-input")
    resolution_derived: dict[str, Any] = {}
    resolution_digest: str | None = None
    needs_resolution = review_required or mode == "remediation-plan"
    if needs_resolution:
        if resolution is None:
            errors.append("blocked-review-resolution-missing")
        else:
            resolution_errors, resolution_derived = validate_resolution(
                run, resolution, repo
            )
            errors.extend(resolution_errors)
            resolution_digest = resolution_derived.get("resolution_digest")
    elif resolution is not None:
        errors.append("blocked-unexpected-input")

    if run_derived.get("selected_step_id"):
        errors.append("blocked-step-open")
    if run_derived.get("has_blocked_step"):
        errors.append("blocked-step-open")
    evidence_problems, evidence_basis = evidence_errors(
        evidence_values,
        run,
        run_derived.get("completed_steps", []),
    )
    errors.extend(evidence_problems)
    if review_required or publication_requested or ship_value is not None:
        completed_scope = {
            path
            for step in completed_steps
            for path in string_list(step.get("paths"))
        }
        try:
            uncommitted_paths = live_changed_paths(repo, "HEAD")
        except ValueError:
            errors.append("blocked-artifact-uncommitted")
        else:
            if any(
                paths_overlap(path, scope, repo)
                for path in uncommitted_paths
                for scope in completed_scope
            ):
                errors.append("blocked-artifact-uncommitted")

    cas_ids: list[str] = []
    if review_required and not needs_reship and resolution is not None:
        artifact = run.get("artifact") if isinstance(run.get("artifact"), dict) else {}
        try:
            live_snapshot = live_cas_list(
                repo,
                text(artifact.get("base_sha")),
                text(review.get("codex_thread_id")),
            )
        except ValueError:
            errors.append("blocked-cas-live-list-unavailable")
        else:
            if len(cas_values) > 1 or (
                cas_values
                and canonical_digest(cas_values[0]) != canonical_digest(live_snapshot)
            ):
                errors.append("blocked-cas-evidence-set-incomplete")
            cas_problems, cas_ids = cas_errors(
                live_snapshot, run, resolution, resolution_derived
            )
            errors.extend(cas_problems)
    elif cas_values:
        errors.append("blocked-unexpected-input")
    outcome = (
        (resolution or {}).get("outcome")
        if isinstance((resolution or {}).get("outcome"), dict)
        else {}
    )
    terminal_resolution_statuses = (
        {"pending", "clean", "resolved"}
        if mode == "remediation-plan"
        else {"clean", "resolved"}
    )
    if needs_resolution and outcome.get("status") not in terminal_resolution_statuses:
        errors.append("blocked-review-resolution-open")
    if needs_reship and outcome.get("status") != "resolved":
        errors.append("blocked-review-resolution-open")
    if mode in {"implement", "review-closeout"} and not completed_steps:
        errors.append("blocked-step-not-ready-for-closure")
    if (
        mode in {"implement", "review-closeout"}
        and completed_steps
        and (completed_steps[-1].get("verdict") != "ready-for-closure")
    ):
        errors.append("blocked-step-not-ready-for-closure")
    if ship_value is not None and not publication_requested:
        errors.append("blocked-unexpected-input")
    if mode == "review-closeout" and ship_value is not None:
        errors.append("blocked-unexpected-input")
    effective_ship = embedded_ship if mode == "review-closeout" else ship_value
    ship_basis: list[str] = []
    verdict = "complete"
    goal_outcome = "complete"
    implementation_outcome = (
        "not-applicable" if mode in {"triage", "remediation-plan"} else "complete"
    )
    next_owner = "none"

    if errors:
        verdict = "blocked"
        goal_outcome = "blocked"
        implementation_outcome = (
            "not-applicable" if mode in {"triage", "remediation-plan"} else "incomplete"
        )
        next_owner = "goal-actuating"
    elif triage_human:
        verdict = "continue"
        goal_outcome = "continue"
        next_owner = "human"
    elif needs_reship:
        verdict = "ready-to-ship"
        goal_outcome = "continue"
        next_owner = "ship"
    elif publication_requested:
        if effective_ship is None:
            if mode == "review-closeout":
                errors.append("blocked-ship-missing")
                verdict = "blocked"
                goal_outcome = "blocked"
                next_owner = "goal-actuating"
            else:
                verdict = "ready-to-ship"
                goal_outcome = "continue"
                next_owner = "ship"
        else:
            ship_problems, ship_basis = ship_errors(effective_ship, run)
            errors.extend(ship_problems)
            if ship_problems:
                verdict = "blocked"
                goal_outcome = "blocked"
                next_owner = "ship"
            elif mode == "implement":
                verdict = "continue"
                goal_outcome = "continue"
                next_owner = "goal-actuating"

    final_binding_errors, final_artifact = binding_errors(
        run.get("artifact"), repo, "blocked-run"
    )
    errors.extend(final_binding_errors)
    if final_binding_errors:
        verdict = "blocked"
        goal_outcome = "blocked"
        implementation_outcome = (
            "not-applicable"
            if mode in {"triage", "remediation-plan"}
            else "incomplete"
        )
        next_owner = "goal-actuating"

    decision_core = {
        "version": "closure-decision/v1",
        "run_id": run.get("run_id"),
        "evaluated_artifact": final_artifact,
        "run_digest": run_derived.get("run_digest", ""),
        "resolution_digest": resolution_digest,
        "verdict": verdict,
        "outcomes": {
            "goal_outcome": goal_outcome,
            "implementation_outcome": implementation_outcome,
            "next_owner": next_owner,
        },
        "evidence_basis": evidence_basis,
        "review_basis": triage_review_basis or cas_ids,
        "ship_basis": ship_basis,
        "reasons": sorted(set(errors)),
    }
    decision_core["decision_id"] = canonical_digest(decision_core)
    code = 0 if verdict in {"complete", "ready-to-ship"} else 2
    return {"closure_decision": decision_core}, code


OBLIGATION_HANDLERS.update(
    {
        "source-authority": validate_run,
        "artifact-currentness": binding_errors,
        "mutation-admission": validate_run,
        "continuation-proof": evidence_errors,
        "no-code-separation": validate_run,
        "review-classification": validate_resolution,
        "owner-boundary-repair": validate_resolution,
        "abstraction-account": validate_resolution,
        "semantic-balance": validate_resolution,
        "independent-review-proof": cas_errors,
        "outcome-separation": decide,
        "delivery-boundary": ship_errors,
        "fail-closed-coordination": validate_run,
    }
)


def emit(operation: str, errors: list[str], derived: dict[str, Any]) -> int:
    payload = {
        "actuating_gate": {
            "operation": operation,
            "verdict": "pass" if not errors else "blocked",
            "errors": errors,
            "derived": derived,
        }
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not errors else 2


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="command", required=True)
    run = sub.add_parser("validate-run")
    run.add_argument("--run", required=True)
    run.add_argument("--resolution")
    run.add_argument("--evidence", action="append", default=[])
    run.add_argument("--repo", required=True)
    resolution = sub.add_parser("validate-resolution")
    resolution.add_argument("--run", required=True)
    resolution.add_argument("--resolution", required=True)
    resolution.add_argument("--repo", required=True)
    close = sub.add_parser("decide")
    close.add_argument("--run", required=True)
    close.add_argument("--resolution")
    close.add_argument("--evidence", action="append", default=[])
    close.add_argument("--review-fold", action="append", default=[])
    close.add_argument("--ship-record")
    close.add_argument("--repo", required=True)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        run = unwrap(load_data(args.run), "actuation_run")
        repo = git_root(Path(args.repo).resolve())
        if args.command == "validate-run":
            run_resolution = (
                unwrap(load_data(args.resolution), "review_resolution")
                if args.resolution
                else None
            )
            run_evidence = [load_data(path) for path in args.evidence]
            errors, derived = validate_run(run, repo, run_resolution, run_evidence)
            return emit(args.command, errors, derived)
        resolution = (
            unwrap(load_data(args.resolution), "review_resolution")
            if args.resolution
            else None
        )
        if args.command == "validate-resolution":
            if resolution is None:
                raise ValueError("resolution is required")
            errors, derived = validate_resolution(run, resolution, repo)
            return emit(args.command, errors, derived)
        evidence = [load_data(path) for path in args.evidence]
        review_folds = [load_data(path) for path in args.review_fold]
        ship = load_data(args.ship_record) if args.ship_record else None
        decision, code = decide(
            run,
            resolution,
            evidence,
            [],
            ship,
            repo,
            review_folds,
        )
        print(json.dumps(decision, indent=2, sort_keys=True))
        return code
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        payload = {
            "actuating_gate": {
                "verdict": "blocked",
                "errors": [f"malformed:{exc}"],
            }
        }
        print(json.dumps(payload, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
