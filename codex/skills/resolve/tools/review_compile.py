#!/usr/bin/env python3
"""C³ Counterexample Compression Compiler controller.

Repo-local state lives in .resolve-c3/. The controller is intentionally standard-
library only so it can be dropped into a Codex skill package.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
from typing import Any, Iterator

STATE_DIR = ".resolve-c3"
STATE_FILE = "state.json"
CERT_FILE = "mrpc.json"
EVENT_FILE = "events.jsonl"
LOCK_FILE = "lock"

COST_FIELDS = [
    "new_truth_owners",
    "new_public_symbols",
    "new_state_variants",
    "new_fallback_or_compatibility_paths",
    "new_protocol_cases",
    "new_control_flow_branches",
    "new_helpers_or_wrappers",
    "new_proof_obligations",
    "retained_retirable_surfaces",
    "owners_modified",
    "files_modified",
    "ast_edit_count",
    "production_net_lines",
    "test_net_lines",
]

REQUIRED_VERIFICATION = [
    "counterexamples_pass",
    "acceptance_pass",
    "regressions_pass",
    "proof_current",
]

BRANCH_LIABLE = {
    "introduced_by_current_diff",
    "exposed_and_required_by_current_acceptance",
    "preexisting_but_blocks_current_invariant",
}

TERMINAL_PHASES = {"closed", "aborted"}
ACTIVE_PHASES = {
    "collecting",
    "selected",
    "apply-certified",
    "applied",
    "final-certified",
    "committed",
    "pushed",
    "invalidated",
}


class C3Error(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def emit(payload: dict[str, Any], exit_code: int = 0) -> int:
    print(json.dumps(payload, indent=2, sort_keys=True))
    return exit_code


def run(
    cwd: Path,
    *args: str,
    check: bool = True,
    input_bytes: bytes | None = None,
) -> subprocess.CompletedProcess[bytes]:
    proc = subprocess.run(
        list(args),
        cwd=str(cwd),
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", "replace").strip()
        stdout = proc.stdout.decode("utf-8", "replace").strip()
        raise C3Error(f"command failed ({proc.returncode}): {' '.join(args)}\n{stderr or stdout}")
    return proc


def git(cwd: Path, *args: str, check: bool = True, input_bytes: bytes | None = None) -> bytes:
    return run(cwd, "git", *args, check=check, input_bytes=input_bytes).stdout


def git_text(cwd: Path, *args: str, check: bool = True) -> str:
    return git(cwd, *args, check=check).decode("utf-8", "replace").strip()


def discover_git_root(start: str | Path) -> Path:
    path = Path(start).expanduser().resolve()
    proc = run(path, "git", "rev-parse", "--show-toplevel", check=False)
    if proc.returncode != 0:
        raise C3Error(f"not inside a git repository: {path}")
    return Path(proc.stdout.decode().strip()).resolve()


def find_state_root(start: str | Path) -> Path | None:
    path = Path(start).expanduser().resolve()
    for candidate in [path, *path.parents]:
        if (candidate / STATE_DIR / STATE_FILE).is_file():
            return candidate
    return None


def paths(root: Path) -> dict[str, Path]:
    state_dir = root / STATE_DIR
    return {
        "dir": state_dir,
        "state": state_dir / STATE_FILE,
        "cert": state_dir / CERT_FILE,
        "events": state_dir / EVENT_FILE,
        "lock": state_dir / LOCK_FILE,
        "candidates": state_dir / "candidates",
    }


@contextlib.contextmanager
def state_lock(root: Path) -> Iterator[None]:
    p = paths(root)
    p["dir"].mkdir(parents=True, exist_ok=True)
    with p["lock"].open("a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def append_event(root: Path, event: str, **fields: Any) -> None:
    row = {"timestamp": utc_now(), "event": event, **fields}
    p = paths(root)["events"]
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def load_state(root: Path) -> dict[str, Any]:
    path = paths(root)["state"]
    if not path.is_file():
        raise C3Error(f"C³ state not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(root: Path, state: dict[str, Any], event: str, **event_fields: Any) -> None:
    state["updated_at"] = utc_now()
    atomic_json(paths(root)["state"], state)
    append_event(root, event, phase=state.get("phase"), **event_fields)


def read_json_input(path: str) -> dict[str, Any]:
    if path == "-":
        data = sys.stdin.read()
    else:
        data = Path(path).read_text(encoding="utf-8")
    value = json.loads(data)
    if not isinstance(value, dict):
        raise C3Error("JSON input must be an object")
    return value


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def safe_id(value: str, label: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", value):
        raise C3Error(f"invalid {label}: {value!r}")
    return value


def ensure_local_exclude(root: Path) -> None:
    common_dir_raw = git_text(root, "rev-parse", "--git-common-dir")
    common_dir = Path(common_dir_raw)
    if not common_dir.is_absolute():
        common_dir = (root / common_dir).resolve()
    exclude = common_dir / "info" / "exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    begin = "# BEGIN resolve-c3 local state"
    end = "# END resolve-c3 local state"
    block = f"{begin}\n{STATE_DIR}/\n{end}\n"
    current = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end) + r"\n?", re.S)
    updated = pattern.sub(block, current) if pattern.search(current) else current.rstrip() + ("\n" if current else "") + block
    if updated != current:
        exclude.write_text(updated, encoding="utf-8")


def porcelain(root: Path) -> list[str]:
    output = git_text(root, "status", "--porcelain=v1", "--untracked-files=all")
    return [line for line in output.splitlines() if line and not line[3:].startswith(f"{STATE_DIR}/")]


def require_clean(root: Path) -> None:
    dirty = porcelain(root)
    if dirty:
        raise C3Error("delivery worktree must be clean before this operation:\n" + "\n".join(dirty[:50]))


def current_head(root: Path) -> str:
    return git_text(root, "rev-parse", "HEAD")


def current_branch(root: Path) -> str:
    return git_text(root, "branch", "--show-current") or "(detached)"


def diff_bytes(root: Path, base_sha: str) -> bytes:
    # Intent-to-add makes untracked files visible in diff without staging content.
    run(root, "git", "add", "-N", "--", ".", check=True)
    return git(root, "diff", "--binary", "--full-index", base_sha, "--", ".")


def diff_numstat(root: Path, base_sha: str) -> dict[str, Any]:
    raw = git_text(root, "diff", "--numstat", base_sha, "--", ".")
    rows: list[dict[str, Any]] = []
    insertions = deletions = test_insertions = test_deletions = 0
    for line in raw.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        a, d, path = parts
        ai = int(a) if a.isdigit() else 0
        di = int(d) if d.isdigit() else 0
        is_test = bool(re.search(r"(^|/)(test|tests)(/|$)|_test\.|\.golden($|\.)", path, re.I))
        insertions += ai
        deletions += di
        if is_test:
            test_insertions += ai
            test_deletions += di
        rows.append({"path": path, "insertions": ai, "deletions": di, "test": is_test})
    return {
        "files": rows,
        "insertions": insertions,
        "deletions": deletions,
        "net": insertions - deletions,
        "test_insertions": test_insertions,
        "test_deletions": test_deletions,
        "test_net": test_insertions - test_deletions,
        "production_insertions": insertions - test_insertions,
        "production_deletions": deletions - test_deletions,
        "production_net": (insertions - test_insertions) - (deletions - test_deletions),
    }


def capture_patch(root: Path, base_sha: str) -> tuple[bytes, dict[str, Any]]:
    patch = diff_bytes(root, base_sha)
    return patch, diff_numstat(root, base_sha)


def require_phase(state: dict[str, Any], *allowed: str) -> None:
    if state.get("phase") not in allowed:
        raise C3Error(f"operation requires phase {allowed}; current phase is {state.get('phase')!r}")


def invalidate_compilation(state: dict[str, Any], reason: str) -> None:
    selected_id = state.get("selected_candidate_id")
    if selected_id:
        try:
            state["invalidated_candidate"] = dict(find_candidate(state, selected_id))
        except Exception:
            state["invalidated_candidate"] = {"candidate_id": selected_id}
    state["phase"] = "invalidated"
    state["invalidation_reason"] = reason
    state["selected_candidate_id"] = None
    state["ablation"] = None
    state["holdouts"] = {}
    state["proof"] = None
    state["certificate"] = None



def cost_measurement_errors(cost: dict[str, Any], stats: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not stats:
        return ["diff-stats-missing"]
    measured_files = len(stats.get("files", []))
    expected = {
        "files_modified": measured_files,
        "production_net_lines": stats.get("production_net"),
        "test_net_lines": stats.get("test_net"),
    }
    for field, measured in expected.items():
        if measured is None:
            errors.append(f"unmeasured:{field}")
        elif cost.get(field) != measured:
            errors.append(f"cost-mismatch:{field}:declared={cost.get(field)}:measured={measured}")
    return errors


def candidate_valid(candidate: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    verification = candidate.get("verification", {})
    if verification.get("authority") != "controller":
        reasons.append("verification:not-controller")
    for field in REQUIRED_VERIFICATION:
        if verification.get(field) is not True:
            reasons.append(f"verification:{field}")
    if verification.get("falsified_routes_reused") is True:
        reasons.append("falsified-route-reused")
    negative_status = candidate.get("negative_route", {}).get("status", "unknown")
    if negative_status == "active_exclusion":
        reasons.append("active-negative-route")
    elif negative_status not in {"allowed", "reopened", "stale", "superseded"}:
        reasons.append("negative-route-unresolved")
    if candidate.get("scope_valid") is not True:
        reasons.append("scope-invalid")
    cost = candidate.get("semantic_cost")
    if not isinstance(cost, dict):
        reasons.append("semantic-cost-missing")
    else:
        for field in COST_FIELDS:
            value = cost.get(field)
            if not isinstance(value, int):
                reasons.append(f"semantic-cost:{field}")
        if not any(reason.startswith("semantic-cost:") for reason in reasons):
            reasons.extend(cost_measurement_errors(cost, candidate.get("diff_stats", {})))
    return not reasons, reasons


def cost_tuple(candidate: dict[str, Any]) -> tuple[int, ...]:
    return tuple(int(candidate["semantic_cost"][field]) for field in COST_FIELDS)


def find_candidate(state: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    for candidate in state.get("candidates", []):
        if candidate.get("candidate_id") == candidate_id:
            return candidate
    raise C3Error(f"unknown candidate: {candidate_id}")


def safe_holdout(value: dict[str, Any] | None) -> bool:
    if not value:
        return False
    if value.get("new_branch_liabilities"):
        return False
    return value.get("verdict") in {"clean", "followups-only", "subsumed-only"}


def ablation_summary(value: dict[str, Any] | None) -> tuple[list[Any], list[Any], list[str]]:
    if not value:
        return [], [], ["ablation-missing"]
    removed: list[Any] = []
    survived: list[Any] = []
    orphan: list[str] = []
    for atom in value.get("edit_atoms", []):
        result = atom.get("result")
        if result == "removed":
            removed.append(atom)
        elif result == "survived":
            survived.append(atom)
            if not atom.get("failure_witness") or not atom.get("obligations"):
                orphan.append(str(atom.get("edit_id", "(missing-id)")))
        else:
            orphan.append(str(atom.get("edit_id", "(missing-id)")))
    if value.get("one_minimal") is not True:
        orphan.append("one-minimal-not-proven")
    return removed, survived, orphan


def build_mrpc(state: dict[str, Any], stage: str) -> dict[str, Any]:
    selected = None
    if state.get("selected_candidate_id"):
        selected = find_candidate(state, state["selected_candidate_id"])
    removed, survived, orphan = ablation_summary(state.get("ablation"))
    candidates = []
    for candidate in state.get("candidates", []):
        candidates.append({
            "candidate_id": candidate.get("candidate_id"),
            "route_class": candidate.get("route_class"),
            "route_family": candidate.get("route_family"),
            "valid": candidate.get("valid"),
            "invalid_reasons": candidate.get("invalid_reasons", []),
            "negative_route": candidate.get("negative_route", {}),
            "semantic_cost": candidate.get("semantic_cost", {}),
            "patch_sha": candidate.get("patch_sha"),
            "diff_stats": candidate.get("diff_stats", {}),
        })
    gate = {
        "apply_allowed": stage == "apply-certified",
        "commit_allowed": stage == "final-certified",
        "push_allowed": stage == "committed",
        "closure_allowed": stage in {"pushed", "closed"},
    }
    cert: dict[str, Any] = {
        "minimal_review_patch_certificate": {
            "certificate_version": "MRPC-v1",
            "certificate_id": "",
            "stage": stage,
            "run_id": state["run_id"],
            "immutable_base": {
                "repo_root": state["repo_root"],
                "branch": state["branch"],
                "sha": state["base_sha"],
            },
            "acceptance_contract": state.get("acceptance_contract", {}),
            "counterexample_basis": state.get("basis"),
            "candidate_tournament": candidates,
            "selected_candidate": None if selected is None else {
                "candidate_id": selected.get("candidate_id"),
                "route_class": selected.get("route_class"),
                "route_family": selected.get("route_family"),
                "patch_sha": selected.get("patch_sha"),
                "semantic_cost": selected.get("semantic_cost"),
                "verification": selected.get("verification"),
                "diff_stats": selected.get("diff_stats"),
            },
            "negative_routes": {
                "excluded": [
                    c.get("negative_route") for c in state.get("candidates", [])
                    if c.get("negative_route", {}).get("status") == "active_exclusion"
                ],
                "selected": None if selected is None else selected.get("negative_route", {}),
            },
            "ablation": state.get("ablation"),
            "obligation_to_edit_map": [
                {
                    "edit_id": atom.get("edit_id"),
                    "obligations": atom.get("obligations", []),
                    "failure_witness": atom.get("failure_witness"),
                }
                for atom in survived
            ],
            "proof": state.get("proof"),
            "holdout": state.get("holdouts", {}),
            "delivery": state.get("delivery", {}),
            "metrics": {
                "raw_findings": len(state.get("counterexamples", [])),
                "independent_families": len((state.get("basis") or {}).get("families", [])),
                "candidates_evaluated": len(state.get("candidates", [])),
                "candidates_discarded": len([c for c in state.get("candidates", []) if not c.get("valid") or c.get("candidate_id") != state.get("selected_candidate_id")]),
                "edit_atoms_before_ablation": len((state.get("ablation") or {}).get("edit_atoms", [])),
                "edit_atoms_removed": len(removed),
                "edit_atoms_survived": len(survived),
                "orphan_edit_atoms": orphan,
            },
            "gate": gate,
        }
    }
    body = cert["minimal_review_patch_certificate"]
    identity_payload = dict(body)
    identity_payload["certificate_id"] = ""
    body["certificate_id"] = "MRPC-" + hashlib.sha256(canonical_json_bytes(identity_payload)).hexdigest()[:16]
    return cert


def save_certificate(root: Path, state: dict[str, Any], stage: str) -> dict[str, Any]:
    cert = build_mrpc(state, stage)
    atomic_json(paths(root)["cert"], cert)
    state["certificate"] = {
        "id": cert["minimal_review_patch_certificate"]["certificate_id"],
        "stage": stage,
        "path": str(paths(root)["cert"]),
    }
    return cert



def archive_terminal_run(root: Path, prior: dict[str, Any]) -> None:
    p = paths(root)
    run_id = safe_id(str(prior.get("run_id") or "unknown-run"), "prior run id")
    archive = p["dir"] / "archive" / run_id
    archive.mkdir(parents=True, exist_ok=True)
    for source in [p["state"], p["cert"], p["events"]]:
        if source.exists():
            target = archive / source.name
            if target.exists():
                target.unlink()
            source.replace(target)
    if p["candidates"].exists():
        target = archive / "candidates"
        if target.exists():
            import shutil
            shutil.rmtree(target)
        p["candidates"].replace(target)


def begin(args: argparse.Namespace) -> int:
    root = discover_git_root(args.root)
    p = paths(root)
    parent_run_id = None
    if p["state"].exists():
        prior = json.loads(p["state"].read_text(encoding="utf-8"))
        if prior.get("phase") not in TERMINAL_PHASES:
            raise C3Error(f"active C³ run already exists: {prior.get('run_id')} ({prior.get('phase')}); close or abort it first")
        parent_run_id = prior.get("run_id")
        archive_terminal_run(root, prior)
    require_clean(root)
    acceptance: dict[str, Any]
    if args.acceptance:
        acceptance = read_json_input(args.acceptance)
    elif args.goal:
        acceptance = {"goal": args.goal, "proof_bar": []}
    else:
        raise C3Error("begin requires --acceptance FILE|- or --goal TEXT")
    base_sha = current_head(root)
    run_id = f"C3-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{base_sha[:8]}"
    p["candidates"].mkdir(parents=True, exist_ok=True)
    ensure_local_exclude(root)
    lab_roots: list[str] = []
    lab_worktrees: list[dict[str, str]] = []
    if args.lab:
        lab_path = Path(args.lab).expanduser().resolve()
        if lab_path.exists() and any(lab_path.iterdir()):
            raise C3Error(f"lab path is not empty: {lab_path}")
        lab_path.parent.mkdir(parents=True, exist_ok=True)
        branch_name = f"resolve-c3/{run_id.lower()}"
        run(root, "git", "worktree", "add", "-b", branch_name, str(lab_path), base_sha)
        lab_roots.append(str(lab_path))
        lab_worktrees.append({"path": str(lab_path), "branch": branch_name})
    state = {
        "state_version": 1,
        "run_id": run_id,
        "parent_run_id": parent_run_id,
        "repo_root": str(root),
        "branch": current_branch(root),
        "base_sha": base_sha,
        "phase": "collecting",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "acceptance_contract": acceptance,
        "lab_roots": lab_roots,
        "lab_worktrees": lab_worktrees,
        "counterexamples": [],
        "basis": None,
        "candidates": [],
        "candidate_history": [],
        "tournament_waiver": None,
        "selected_candidate_id": None,
        "ablation": None,
        "holdouts": {},
        "proof": None,
        "delivery": {},
        "certificate": None,
    }
    with state_lock(root):
        atomic_json(p["state"], state)
        append_event(root, "begin", phase="collecting", run_id=run_id, base_sha=base_sha)
    return emit({"c3_receipt": {"command": "begin", "outcome": "success", "run_id": run_id, "root": str(root), "base_sha": base_sha, "lab_roots": lab_roots}})


def root_for(args: argparse.Namespace, require_state: bool = True) -> Path:
    if getattr(args, "root", None):
        root = discover_git_root(args.root)
    else:
        found = find_state_root(Path.cwd())
        if found is None:
            if require_state:
                raise C3Error("no active .resolve-c3 state found")
            return discover_git_root(Path.cwd())
        root = found
    if require_state and not paths(root)["state"].is_file():
        raise C3Error(f"no C³ state under {root}")
    return root



def create_candidate_worktree(args: argparse.Namespace) -> int:
    root = root_for(args)
    candidate_id = safe_id(args.candidate_id, "candidate id")
    with state_lock(root):
        state = load_state(root)
        require_phase(state, "collecting", "selected")
        target = Path(args.path).expanduser().resolve()
        if target.exists() and any(target.iterdir()):
            raise C3Error(f"candidate worktree path is not empty: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        branch = args.branch or f"resolve-c3-candidate/{state['run_id'].lower()}-{candidate_id}"
        run(root, "git", "worktree", "add", "-b", branch, str(target), state["base_sha"])
        state.setdefault("lab_roots", []).append(str(target))
        state.setdefault("lab_worktrees", []).append({"path": str(target), "branch": branch, "candidate_id": candidate_id})
        save_state(root, state, "candidate-worktree-created", candidate_id=candidate_id, path=str(target), branch=branch)
    return emit({"c3_receipt": {"command": "candidate-worktree", "outcome": "success", "candidate_id": candidate_id, "path": str(target), "branch": branch}})


def cleanup_labs(args: argparse.Namespace) -> int:
    if not args.confirm:
        raise C3Error("cleanup-labs requires --confirm")
    root = root_for(args)
    with state_lock(root):
        state = load_state(root)
        if state.get("phase") not in TERMINAL_PHASES:
            raise C3Error("candidate worktrees may be cleaned only after close or abort")
        results = []
        for entry in list(state.get("lab_worktrees", [])):
            target = Path(entry.get("path", ""))
            branch = entry.get("branch", "")
            if target.exists():
                proc = run(root, "git", "worktree", "remove", "--force", str(target), check=False)
                results.append({"path": str(target), "removed": proc.returncode == 0})
            if branch:
                run(root, "git", "branch", "-D", branch, check=False)
        state["lab_roots"] = []
        state["lab_worktrees"] = []
        save_state(root, state, "labs-cleaned")
    return emit({"c3_receipt": {"command": "cleanup-labs", "outcome": "success", "results": results}})


def add_counterexample(args: argparse.Namespace) -> int:
    root = root_for(args)
    item = read_json_input(args.input)
    finding_id = safe_id(str(item.get("id") or item.get("finding_id") or ""), "counterexample id")
    item["id"] = finding_id
    liability = item.get("liability")
    if liability not in BRANCH_LIABLE | {"adjacent_preexisting", "reviewer_preference", "unknown"}:
        raise C3Error(f"invalid liability: {liability!r}")
    with state_lock(root):
        state = load_state(root)
        if state.get("phase") in {"selected", "apply-certified", "applied", "final-certified"} and liability in BRANCH_LIABLE:
            invalidate_compilation(state, f"new branch-liable counterexample: {finding_id}")
        existing = [x for x in state["counterexamples"] if x.get("id") != finding_id]
        existing.append(item)
        state["counterexamples"] = existing
        if liability in BRANCH_LIABLE:
            state["basis"] = None
        save_state(root, state, "counterexample-added", finding_id=finding_id, liability=liability)
    return emit({"c3_receipt": {"command": "add-counterexample", "outcome": "success", "finding_id": finding_id, "liability": liability, "phase": state["phase"]}})


def set_basis(args: argparse.Namespace) -> int:
    root = root_for(args)
    basis = read_json_input(args.input)
    if basis.get("basis_version") != "CEB-v1":
        raise C3Error("basis_version must be CEB-v1")
    gate = basis.get("gate", {})
    required = ["all_findings_classified", "every_branch_liability_covered", "non_branch_liabilities_excluded"]
    if any(gate.get(field) != "pass" for field in required):
        raise C3Error("counterexample basis gate must pass all required fields")
    with state_lock(root):
        state = load_state(root)
        if state.get("phase") == "invalidated" and porcelain(root):
            raise C3Error("reset delivery before installing a new basis")
        if state.get("candidates"):
            state.setdefault("candidate_history", []).extend(state["candidates"])
        state["basis"] = basis
        state["candidates"] = []
        state["phase"] = "collecting"
        state["selected_candidate_id"] = None
        state["invalidated_candidate"] = None
        state["ablation"] = None
        state["holdouts"] = {}
        state["proof"] = None
        state["certificate"] = None
        save_state(root, state, "basis-set", family_count=len(basis.get("families", [])))
    return emit({"c3_receipt": {"command": "set-basis", "outcome": "success", "families": len(basis.get("families", []))}})


def set_tournament_waiver(args: argparse.Namespace) -> int:
    root = root_for(args)
    if not args.reason.strip():
        raise C3Error("waiver reason is required")
    with state_lock(root):
        state = load_state(root)
        state["tournament_waiver"] = {"reason": args.reason.strip(), "created_at": utc_now()}
        save_state(root, state, "tournament-waiver")
    return emit({"c3_receipt": {"command": "tournament-waiver", "outcome": "success", "reason": args.reason.strip()}})


def register_candidate(args: argparse.Namespace) -> int:
    root = root_for(args)
    metadata = read_json_input(args.input)
    candidate_id = safe_id(str(metadata.get("candidate_id") or ""), "candidate id")
    with state_lock(root):
        state = load_state(root)
        require_phase(state, "collecting", "selected", "invalidated")
        if state.get("basis") is None:
            raise C3Error("set a passing CEB-v1 basis before registering candidates")
        patch: bytes
        stats: dict[str, Any]
        worktree: Path | None = None
        if args.worktree:
            worktree = discover_git_root(args.worktree)
            patch, stats = capture_patch(worktree, state["base_sha"])
        elif args.patch:
            patch = Path(args.patch).read_bytes()
            stats = metadata.get("diff_stats", {})
        elif metadata.get("route_class") == "no-change":
            patch = b""
            stats = {
                "files": [], "insertions": 0, "deletions": 0, "net": 0,
                "test_insertions": 0, "test_deletions": 0, "test_net": 0,
                "production_insertions": 0, "production_deletions": 0, "production_net": 0,
            }
        else:
            raise C3Error("register-candidate requires --worktree or --patch, except route_class=no-change")
        candidate_patch = paths(root)["candidates"] / f"{candidate_id}.patch"
        candidate_patch.write_bytes(patch)
        candidate = dict(metadata)
        candidate["candidate_id"] = candidate_id
        if "verification" in candidate:
            candidate["verification_claim"] = candidate.pop("verification")
        candidate["verification"] = {"authority": "unverified"}
        candidate["patch_ref"] = str(candidate_patch)
        candidate["patch_sha"] = sha256_bytes(patch)
        candidate["worktree"] = str(worktree) if worktree else None
        candidate["diff_stats"] = stats
        valid, reasons = candidate_valid(candidate)
        candidate["valid"] = valid
        candidate["invalid_reasons"] = reasons
        state["candidates"] = [c for c in state.get("candidates", []) if c.get("candidate_id") != candidate_id] + [candidate]
        state["phase"] = "collecting"
        state["selected_candidate_id"] = None
        state["invalidated_candidate"] = None
        state["ablation"] = None
        state["holdouts"] = {}
        state["proof"] = None
        state["certificate"] = None
        save_state(root, state, "candidate-registered", candidate_id=candidate_id, valid=valid)
    return emit({"c3_receipt": {"command": "register-candidate", "outcome": "success", "candidate_id": candidate_id, "valid": valid, "invalid_reasons": reasons, "patch_sha": candidate["patch_sha"], "diff_stats": stats}})



def run_check_commands(cwd: Path, checks: list[dict[str, Any]], log_dir: Path, prefix: str) -> list[dict[str, Any]]:
    log_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    for idx, check in enumerate(checks, start=1):
        command = str(check.get("command") or "").strip()
        kind = str(check.get("kind") or "").strip()
        if not command or kind not in {"counterexample", "acceptance", "regression", "proof", "lint", "typecheck", "other"}:
            raise C3Error(f"invalid check at index {idx}")
        proc = subprocess.run(
            command,
            cwd=str(cwd),
            shell=True,
            executable="/bin/sh",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        log_path = log_dir / f"{prefix}-{idx:02d}.log"
        log_path.write_text(
            f"$ {command}\nexit_code={proc.returncode}\n\n{proc.stdout}",
            encoding="utf-8",
        )
        results.append({
            "kind": kind,
            "command": command,
            "result": "pass" if proc.returncode == 0 else "fail",
            "exit_code": proc.returncode,
            "evidence_ref": str(log_path),
            "obligations": check.get("obligations", []),
        })
    return results


def verify_candidate(args: argparse.Namespace) -> int:
    root = root_for(args)
    plan = read_json_input(args.input)
    candidate_id = safe_id(args.candidate_id, "candidate id")
    checks = plan.get("checks", [])
    if not isinstance(checks, list) or not checks:
        raise C3Error("verify-candidate requires a non-empty checks list")
    with state_lock(root):
        state = load_state(root)
        require_phase(state, "collecting", "selected")
        candidate = find_candidate(state, candidate_id)
        worktree = Path(candidate["worktree"]).resolve() if candidate.get("worktree") else root
        before_patch, before_stats = capture_patch(worktree, state["base_sha"])
        before_sha = sha256_bytes(before_patch)
        if before_sha != candidate.get("patch_sha"):
            raise C3Error("candidate patch changed since registration; re-register before verification")
        results = run_check_commands(
            worktree,
            checks,
            paths(root)["candidates"] / f"{candidate_id}-verification",
            "check",
        )
        after_patch, after_stats = capture_patch(worktree, state["base_sha"])
        after_sha = sha256_bytes(after_patch)
        patch_stable = before_sha == after_sha
        by_kind: dict[str, list[dict[str, Any]]] = {}
        for result in results:
            by_kind.setdefault(result["kind"], []).append(result)
        def category_pass(kind: str) -> bool:
            rows = by_kind.get(kind, [])
            return bool(rows) and all(row["result"] == "pass" for row in rows)
        candidate["verification"] = {
            "authority": "controller",
            "counterexamples_pass": category_pass("counterexample"),
            "acceptance_pass": category_pass("acceptance"),
            "regressions_pass": category_pass("regression"),
            "proof_current": patch_stable,
            "falsified_routes_reused": candidate.get("negative_route", {}).get("status") == "active_exclusion",
            "checks": results,
            "patch_stable": patch_stable,
        }
        candidate["diff_stats"] = after_stats
        valid, reasons = candidate_valid(candidate)
        candidate["valid"] = valid
        candidate["invalid_reasons"] = reasons
        save_state(root, state, "candidate-verified", candidate_id=candidate_id, valid=valid)
    return emit({
        "candidate_verification": {
            "candidate_id": candidate_id,
            "valid": valid,
            "invalid_reasons": reasons,
            "checks": results,
            "patch_stable": patch_stable,
        }
    }, exit_code=0 if valid else 2)


def select_candidate(args: argparse.Namespace) -> int:
    root = root_for(args)
    with state_lock(root):
        state = load_state(root)
        require_phase(state, "collecting", "invalidated")
        if state.get("basis") is None:
            raise C3Error("counterexample basis missing")
        candidates = state.get("candidates", [])
        waiver = state.get("tournament_waiver")
        if len(candidates) < 3 and not waiver:
            raise C3Error("material tournament requires at least three candidate records or a tournament waiver")
        route_classes = {str(c.get("route_class")) for c in candidates}
        if len(route_classes) < 2 and not waiver:
            raise C3Error("tournament requires at least two distinct route classes")
        if not ({"no-change", "local-baseline"} & route_classes) and not waiver:
            raise C3Error("tournament requires a no-change or local-baseline control candidate")
        valid = [c for c in candidates if c.get("valid")]
        if not valid:
            raise C3Error("no candidate passes hard constraints")
        valid.sort(key=lambda c: (cost_tuple(c), str(c["candidate_id"])))
        selected = valid[0]
        state["selected_candidate_id"] = selected["candidate_id"]
        state["invalidated_candidate"] = None
        state["phase"] = "selected"
        state["ablation"] = None
        state["holdouts"] = {}
        state["proof"] = None
        state["certificate"] = None
        save_state(root, state, "candidate-selected", candidate_id=selected["candidate_id"])
    return emit({
        "candidate_tournament": {
            "selected_candidate": selected["candidate_id"],
            "selected_semantic_cost": selected["semantic_cost"],
            "optimality": "minimum-among-generated-valid-candidates",
            "global_optimality_claimed": False,
            "ranked_valid_candidates": [
                {"candidate_id": c["candidate_id"], "semantic_cost": c["semantic_cost"]}
                for c in valid
            ],
            "invalid_candidates": [
                {"candidate_id": c.get("candidate_id"), "reasons": c.get("invalid_reasons", [])}
                for c in candidates if not c.get("valid")
            ],
        }
    })



def run_shell_logged(cwd: Path, command: str, log_path: Path) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        command,
        cwd=str(cwd),
        shell=True,
        executable="/bin/sh",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        f"$ {command}\nexit_code={proc.returncode}\n\n{proc.stdout}",
        encoding="utf-8",
    )
    return proc


def ablate_candidate(args: argparse.Namespace) -> int:
    root = root_for(args)
    plan = read_json_input(args.input)
    candidate_id = safe_id(args.candidate_id, "candidate id")
    atoms = plan.get("edit_atoms", [])
    checks = plan.get("checks", [])
    semantic_cost_after = plan.get("semantic_cost_after")
    if not isinstance(atoms, list) or not atoms:
        raise C3Error("ablate requires a non-empty edit_atoms list")
    if not isinstance(checks, list) or not checks:
        raise C3Error("ablate requires a non-empty common checks list")
    if not isinstance(semantic_cost_after, dict) or any(not isinstance(semantic_cost_after.get(field), int) for field in COST_FIELDS):
        raise C3Error("ablate requires a complete integer semantic_cost_after")
    with state_lock(root):
        state = load_state(root)
        require_phase(state, "selected")
        if state.get("selected_candidate_id") != candidate_id:
            raise C3Error("ablate candidate must be the selected candidate")
        candidate = find_candidate(state, candidate_id)
        prior_cost = cost_tuple(candidate)
        if not candidate.get("worktree"):
            raise C3Error("controller-run ablation requires a candidate worktree")
        worktree = Path(candidate["worktree"]).resolve()
        baseline_patch, _ = capture_patch(worktree, state["base_sha"])
        baseline_sha = sha256_bytes(baseline_patch)
        if baseline_sha != candidate.get("patch_sha"):
            raise C3Error("selected candidate changed before ablation")
        results: list[dict[str, Any]] = []
        log_root = paths(root)["candidates"] / f"{candidate_id}-ablation"
        for idx, atom in enumerate(atoms, start=1):
            edit_id = safe_id(str(atom.get("edit_id") or ""), "edit atom id")
            remove_command = str(atom.get("remove_command") or "").strip()
            restore_command = str(atom.get("restore_command") or "").strip()
            obligations = atom.get("obligations", [])
            if not remove_command:
                raise C3Error(f"edit atom {edit_id} is missing remove_command")
            remove_log = log_root / f"{idx:02d}-{edit_id}-remove.log"
            remove_proc = run_shell_logged(worktree, remove_command, remove_log)
            if remove_proc.returncode != 0:
                raise C3Error(f"remove_command failed for {edit_id}; see {remove_log}")
            removed_patch, _ = capture_patch(worktree, state["base_sha"])
            removed_sha = sha256_bytes(removed_patch)
            if removed_sha == baseline_sha:
                raise C3Error(f"remove_command for {edit_id} did not change the candidate patch")
            check_results = run_check_commands(
                worktree,
                checks,
                log_root / f"{idx:02d}-{edit_id}-checks",
                "check",
            )
            all_pass = all(row["result"] == "pass" for row in check_results)
            if all_pass:
                results.append({
                    "edit_id": edit_id,
                    "kind": atom.get("kind", "unknown"),
                    "result": "removed",
                    "obligations": obligations,
                    "remove_command": remove_command,
                    "proof": check_results,
                })
                baseline_patch = removed_patch
                baseline_sha = removed_sha
            else:
                if not restore_command:
                    raise C3Error(f"surviving edit atom {edit_id} requires restore_command")
                restore_log = log_root / f"{idx:02d}-{edit_id}-restore.log"
                restore_proc = run_shell_logged(worktree, restore_command, restore_log)
                if restore_proc.returncode != 0:
                    raise C3Error(f"restore_command failed for {edit_id}; see {restore_log}")
                restored_patch, _ = capture_patch(worktree, state["base_sha"])
                restored_sha = sha256_bytes(restored_patch)
                if restored_sha != baseline_sha:
                    raise C3Error(f"restore_command for {edit_id} did not restore the prior candidate patch")
                failed_checks = [row for row in check_results if row["result"] != "pass"]
                results.append({
                    "edit_id": edit_id,
                    "kind": atom.get("kind", "unknown"),
                    "result": "survived",
                    "obligations": obligations,
                    "remove_command": remove_command,
                    "restore_command": restore_command,
                    "failure_witness": {
                        "failed_checks": failed_checks,
                        "summary": atom.get("failure_witness") or "Removal failed the common proof set.",
                    },
                    "proof_ref": [row["evidence_ref"] for row in failed_checks],
                })
        final_checks = run_check_commands(
            worktree,
            checks,
            log_root / "final-checks",
            "check",
        )
        if any(row["result"] != "pass" for row in final_checks):
            raise C3Error("ablated candidate does not pass the common proof set")
        final_patch, final_stats = capture_patch(worktree, state["base_sha"])
        final_sha = sha256_bytes(final_patch)
        patch_path = Path(candidate["patch_ref"])
        patch_path.write_bytes(final_patch)
        candidate["patch_sha"] = final_sha
        candidate["diff_stats"] = final_stats
        candidate["semantic_cost"] = semantic_cost_after
        if cost_tuple(candidate) > prior_cost:
            raise C3Error("ablation may not increase the selected candidate's semantic cost")
        candidate["verification"] = {
            "authority": "controller",
            "counterexamples_pass": bool([r for r in final_checks if r["kind"] == "counterexample"]) and all(r["result"] == "pass" for r in final_checks if r["kind"] == "counterexample"),
            "acceptance_pass": bool([r for r in final_checks if r["kind"] == "acceptance"]) and all(r["result"] == "pass" for r in final_checks if r["kind"] == "acceptance"),
            "regressions_pass": bool([r for r in final_checks if r["kind"] == "regression"]) and all(r["result"] == "pass" for r in final_checks if r["kind"] == "regression"),
            "proof_current": True,
            "falsified_routes_reused": candidate.get("negative_route", {}).get("status") == "active_exclusion",
            "checks": final_checks,
            "patch_stable": True,
        }
        valid, reasons = candidate_valid(candidate)
        candidate["valid"] = valid
        candidate["invalid_reasons"] = reasons
        if not valid:
            raise C3Error(f"ablated candidate is invalid: {reasons}")
        for other in state.get("candidates", []):
            if other.get("candidate_id") == candidate_id or not other.get("valid"):
                continue
            if cost_tuple(other) < cost_tuple(candidate):
                raise C3Error(f"ablation result is no longer tournament-minimal; {other.get('candidate_id')} is cheaper")
        removed_rows = [row for row in results if row["result"] == "removed"]
        survived_rows = [row for row in results if row["result"] == "survived"]
        ablation = {
            "ablation_version": "ABL-v2",
            "authority": "controller",
            "candidate_id": candidate_id,
            "edit_atoms": results,
            "removed": [row["edit_id"] for row in removed_rows],
            "survived": [row["edit_id"] for row in survived_rows],
            "orphan_edit_atoms": [],
            "one_minimal": True,
            "final_checks": final_checks,
            "post_ablation_patch_sha": final_sha,
            "semantic_cost_after": semantic_cost_after,
        }
        state["ablation"] = ablation
        save_state(root, state, "ablation-run", candidate_id=candidate_id, removed=len(removed_rows), survived=len(survived_rows))
    return emit({"ablation_result": ablation})


def record_ablation(args: argparse.Namespace) -> int:
    root = root_for(args)
    value = read_json_input(args.input)
    value["authority"] = "external"
    with state_lock(root):
        state = load_state(root)
        require_phase(state, "selected")
        selected_id = state.get("selected_candidate_id")
        if value.get("candidate_id") != selected_id:
            raise C3Error("ablation candidate_id must match selected candidate")
        candidate = find_candidate(state, selected_id)
        if args.worktree:
            worktree = discover_git_root(args.worktree)
            patch, stats = capture_patch(worktree, state["base_sha"])
            patch_path = Path(candidate["patch_ref"])
            patch_path.write_bytes(patch)
            candidate["patch_sha"] = sha256_bytes(patch)
            candidate["diff_stats"] = stats
            if "semantic_cost" in value:
                candidate["semantic_cost"] = value["semantic_cost"]
                valid, reasons = candidate_valid(candidate)
                candidate["valid"] = valid
                candidate["invalid_reasons"] = reasons
                if not valid:
                    raise C3Error(f"ablated candidate no longer passes candidate contract: {reasons}")
        removed, survived, orphan = ablation_summary(value)
        if orphan:
            raise C3Error("ablation has orphan/unproven edit atoms: " + ", ".join(orphan))
        state["ablation"] = value
        save_state(root, state, "ablation-recorded", candidate_id=selected_id, removed=len(removed), survived=len(survived))
    return emit({"c3_receipt": {"command": "record-ablation", "outcome": "success", "candidate_id": selected_id, "removed": len(removed), "survived": len(survived), "orphan_edit_atoms": []}})


def record_holdout(args: argparse.Namespace) -> int:
    root = root_for(args)
    value = read_json_input(args.input)
    stage = args.stage
    if stage not in {"candidate", "delivery"}:
        raise C3Error("holdout stage must be candidate or delivery")
    with state_lock(root):
        state = load_state(root)
        if stage == "candidate":
            require_phase(state, "selected")
        else:
            require_phase(state, "applied", "invalidated")
        state.setdefault("holdouts", {})[stage] = value
        new_items = value.get("new_branch_liabilities", [])
        if new_items:
            state["basis"] = None
            for item in new_items:
                if isinstance(item, dict):
                    finding_id = str(item.get("id") or item.get("finding_id") or "")
                    if finding_id:
                        item["id"] = safe_id(finding_id, "counterexample id")
                        state["counterexamples"] = [x for x in state["counterexamples"] if x.get("id") != item["id"]] + [item]
            invalidate_compilation(state, f"{stage} holdout produced branch-liable counterexample")
        save_state(root, state, "holdout-recorded", stage=stage, verdict=value.get("verdict"), invalidated=bool(new_items))
    return emit({"c3_receipt": {"command": "record-holdout", "outcome": "invalidated" if new_items else "success", "stage": stage, "verdict": value.get("verdict"), "phase": state["phase"]}}, exit_code=2 if new_items else 0)


def certify_apply(args: argparse.Namespace) -> int:
    root = root_for(args)
    with state_lock(root):
        state = load_state(root)
        require_phase(state, "selected")
        if state.get("basis") is None:
            raise C3Error("counterexample basis missing")
        selected = find_candidate(state, state["selected_candidate_id"])
        if not selected.get("valid"):
            raise C3Error("selected candidate is invalid")
        if (state.get("ablation") or {}).get("authority") != "controller":
            raise C3Error("apply certification requires controller-run ablation; use ablate")
        _, _, orphan = ablation_summary(state.get("ablation"))
        if orphan:
            raise C3Error("ablation gate failed: " + ", ".join(orphan))
        if not safe_holdout(state.get("holdouts", {}).get("candidate")):
            raise C3Error("candidate holdout is missing or unsafe")
        state["phase"] = "apply-certified"
        cert = save_certificate(root, state, "apply-certified")
        save_state(root, state, "apply-certified", certificate_id=state["certificate"]["id"])
    return emit(cert)


def current_delivery_patch(root: Path, state: dict[str, Any]) -> tuple[bytes, str]:
    patch = diff_bytes(root, state["base_sha"])
    return patch, sha256_bytes(patch)


def apply_selected(args: argparse.Namespace) -> int:
    root = root_for(args)
    with state_lock(root):
        state = load_state(root)
        require_phase(state, "apply-certified")
        if current_head(root) != state["base_sha"]:
            raise C3Error("delivery HEAD moved from immutable base")
        require_clean(root)
        selected = find_candidate(state, state["selected_candidate_id"])
        patch = Path(selected["patch_ref"]).read_bytes()
        if patch:
            run(root, "git", "apply", "--check", "-", input_bytes=patch)
            run(root, "git", "apply", "-", input_bytes=patch)
        current_patch, current_sha = current_delivery_patch(root, state)
        if current_sha != selected["patch_sha"]:
            raise C3Error(f"applied patch fingerprint mismatch: {current_sha} != {selected['patch_sha']}")
        state["delivery"] = {
            "patch_sha": current_sha,
            "diff_stats": diff_numstat(root, state["base_sha"]),
            "applied_at": utc_now(),
            "commit_sha": None,
            "pushed": False,
        }
        state["phase"] = "applied"
        cert = save_certificate(root, state, "applied")
        save_state(root, state, "patch-applied", patch_sha=current_sha)
    return emit(cert)



def run_delivery_proof(args: argparse.Namespace) -> int:
    root = root_for(args)
    plan = read_json_input(args.input)
    checks = plan.get("checks") or plan.get("commands") or []
    if not isinstance(checks, list) or not checks:
        raise C3Error("run-proof requires a non-empty checks list")
    normalized = []
    for check in checks:
        row = dict(check)
        row.setdefault("kind", "proof")
        normalized.append(row)
    with state_lock(root):
        state = load_state(root)
        require_phase(state, "applied")
        _, before_sha = current_delivery_patch(root, state)
        if before_sha != state.get("delivery", {}).get("patch_sha"):
            raise C3Error("delivery patch changed before proof")
        results = run_check_commands(
            root,
            normalized,
            paths(root)["dir"] / "proof",
            "delivery",
        )
        _, after_sha = current_delivery_patch(root, state)
        patch_stable = before_sha == after_sha
        value = {
            "authority": "controller",
            "checks": results,
            "commands": results,
            "patch_sha": after_sha,
            "patch_stable": patch_stable,
            "recorded_at": utc_now(),
        }
        state["proof"] = value
        passed = patch_stable and all(row["result"] == "pass" for row in results)
        save_state(root, state, "proof-run", passed=passed)
    return emit({"delivery_proof": {"passed": passed, "patch_stable": patch_stable, "checks": results}}, exit_code=0 if passed else 2)


def record_proof(args: argparse.Namespace) -> int:
    root = root_for(args)
    value = read_json_input(args.input)
    commands = value.get("commands", [])
    if not isinstance(commands, list) or not commands:
        raise C3Error("proof requires a non-empty commands list")
    with state_lock(root):
        state = load_state(root)
        require_phase(state, "applied")
        _, current_sha = current_delivery_patch(root, state)
        if current_sha != state.get("delivery", {}).get("patch_sha"):
            raise C3Error("delivery patch changed after controller application")
        value["authority"] = value.get("authority", "external")
        value["patch_sha"] = current_sha
        value["recorded_at"] = utc_now()
        state["proof"] = value
        save_state(root, state, "proof-recorded", passed=all(c.get("result") == "pass" for c in commands))
    return emit({"c3_receipt": {"command": "record-proof", "outcome": "success", "all_pass": all(c.get("result") == "pass" for c in commands), "patch_sha": current_sha}})


def certify_final(args: argparse.Namespace) -> int:
    root = root_for(args)
    with state_lock(root):
        state = load_state(root)
        require_phase(state, "applied")
        proof = state.get("proof") or {}
        commands = proof.get("commands", [])
        if proof.get("authority") != "controller":
            raise C3Error("final certification requires controller-run proof; use run-proof")
        if not commands or any(c.get("result") != "pass" for c in commands) or proof.get("patch_stable") is not True:
            raise C3Error("all current delivery proof commands must pass without mutating the patch")
        if not safe_holdout(state.get("holdouts", {}).get("delivery")):
            raise C3Error("delivery holdout is missing or unsafe")
        _, current_sha = current_delivery_patch(root, state)
        selected = find_candidate(state, state["selected_candidate_id"])
        if current_sha != selected["patch_sha"] or current_sha != state.get("delivery", {}).get("patch_sha"):
            raise C3Error("delivery patch is stale or differs from selected candidate")
        _, _, orphan = ablation_summary(state.get("ablation"))
        if orphan:
            raise C3Error("minimality gate failed: " + ", ".join(orphan))
        state["phase"] = "final-certified"
        cert = save_certificate(root, state, "final-certified")
        save_state(root, state, "final-certified", certificate_id=state["certificate"]["id"])
    return emit(cert)


def commit_delivery(args: argparse.Namespace) -> int:
    root = root_for(args)
    with state_lock(root):
        state = load_state(root)
        require_phase(state, "final-certified")
        _, current_sha = current_delivery_patch(root, state)
        selected = find_candidate(state, state["selected_candidate_id"])
        if current_sha != selected["patch_sha"]:
            raise C3Error("delivery patch differs from certified selected candidate")
        if selected["patch_sha"] == sha256_bytes(b""):
            commit_sha = state["base_sha"]
            state["delivery"]["no_commit_required"] = True
        else:
            run(root, "git", "add", "-A", "--", ".")
            run(root, "git", "commit", "-m", args.message)
            commit_sha = current_head(root)
        state["delivery"]["commit_sha"] = commit_sha
        state["delivery"]["committed_at"] = utc_now()
        state["phase"] = "committed"
        cert = save_certificate(root, state, "committed")
        save_state(root, state, "committed", commit_sha=commit_sha)
    return emit(cert)


def push_delivery(args: argparse.Namespace) -> int:
    root = root_for(args)
    with state_lock(root):
        state = load_state(root)
        require_phase(state, "committed")
        if current_head(root) != state.get("delivery", {}).get("commit_sha"):
            raise C3Error("delivery HEAD no longer matches certified commit")
        target = args.branch or "HEAD"
        run(root, "git", "push", args.remote, target)
        state["delivery"]["pushed"] = True
        state["delivery"]["pushed_at"] = utc_now()
        state["delivery"]["remote"] = args.remote
        state["delivery"]["push_target"] = target
        state["phase"] = "pushed"
        cert = save_certificate(root, state, "pushed")
        save_state(root, state, "pushed", remote=args.remote, target=target)
    return emit(cert)


def close_run(args: argparse.Namespace) -> int:
    root = root_for(args)
    sweep = read_json_input(args.input)
    with state_lock(root):
        state = load_state(root)
        require_phase(state, "pushed")
        if sweep.get("unresolved_branch_liabilities"):
            raise C3Error("PR sweep still contains branch-liable findings")
        state["delivery"]["pr_sweep"] = sweep
        state["phase"] = "closed"
        cert = save_certificate(root, state, "closed")
        save_state(root, state, "closed", certificate_id=state["certificate"]["id"])
    return emit(cert)


def reset_delivery(args: argparse.Namespace) -> int:
    if not args.confirm:
        raise C3Error("reset-delivery requires --confirm")
    root = root_for(args)
    with state_lock(root):
        state = load_state(root)
        require_phase(state, "invalidated", "applied", "final-certified")
        if current_head(root) != state["base_sha"]:
            raise C3Error("cannot reset: delivery HEAD moved from immutable base")
        selected_id = state.get("selected_candidate_id")
        patch = b""
        if selected_id:
            patch = Path(find_candidate(state, selected_id)["patch_ref"]).read_bytes()
        elif state.get("invalidated_candidate", {}).get("patch_ref"):
            patch = Path(state["invalidated_candidate"]["patch_ref"]).read_bytes()
        if patch:
            run(root, "git", "apply", "-R", "--check", "-", input_bytes=patch)
            run(root, "git", "apply", "-R", "-", input_bytes=patch)
        if porcelain(root):
            raise C3Error("delivery still has changes after reverse application")
        state["phase"] = "collecting"
        state["selected_candidate_id"] = None
        state["invalidated_candidate"] = None
        state["ablation"] = None
        state["holdouts"] = {}
        state["proof"] = None
        state["delivery"] = {}
        state["certificate"] = None
        save_state(root, state, "delivery-reset")
    return emit({"c3_receipt": {"command": "reset-delivery", "outcome": "success", "phase": "collecting"}})


def abort_run(args: argparse.Namespace) -> int:
    if not args.confirm:
        raise C3Error("abort requires --confirm")
    root = root_for(args)
    with state_lock(root):
        state = load_state(root)
        if state.get("phase") in {"applied", "final-certified", "invalidated"} and porcelain(root):
            raise C3Error("reset delivery before aborting")
        state["phase"] = "aborted"
        state["abort_reason"] = args.reason
        save_state(root, state, "aborted", reason=args.reason)
    return emit({"c3_receipt": {"command": "abort", "outcome": "success", "reason": args.reason}})


def audit_state(args: argparse.Namespace) -> int:
    root = root_for(args)
    state = load_state(root)
    errors: list[str] = []
    warnings: list[str] = []
    if state.get("state_version") != 1:
        errors.append("state-version")
    if not state.get("run_id") or not state.get("base_sha"):
        errors.append("identity")
    if state.get("phase") in {"apply-certified", "applied", "final-certified", "committed", "pushed", "closed"}:
        if not paths(root)["cert"].is_file():
            errors.append("mrpc-missing")
    cert = None
    if paths(root)["cert"].is_file():
        cert = json.loads(paths(root)["cert"].read_text(encoding="utf-8"))
        body = cert.get("minimal_review_patch_certificate", {})
        if body.get("certificate_version") != "MRPC-v1":
            errors.append("mrpc-version")
        if body.get("run_id") != state.get("run_id"):
            errors.append("mrpc-run-id")
        if body.get("stage") != state.get("certificate", {}).get("stage"):
            warnings.append("mrpc-stage-state-mismatch")
    if state.get("phase") in {"applied", "final-certified"}:
        try:
            _, sha = current_delivery_patch(root, state)
            if sha != state.get("delivery", {}).get("patch_sha"):
                errors.append("delivery-patch-stale")
        except Exception as exc:
            errors.append(f"delivery-patch-check:{exc}")
    return emit({"c3_audit": {"ok": not errors, "phase": state.get("phase"), "errors": errors, "warnings": warnings, "certificate": state.get("certificate")}}, exit_code=0 if not errors else 2)


def status(args: argparse.Namespace) -> int:
    root = root_for(args)
    state = load_state(root)
    return emit({"c3_status": state})


def extract_tool(payload: dict[str, Any]) -> tuple[str, str]:
    tool_name = str(payload.get("tool_name") or payload.get("tool") or payload.get("name") or "")
    raw_input = payload.get("tool_input") or payload.get("input") or payload.get("arguments") or {}
    command = ""
    if isinstance(raw_input, dict):
        for key in ("cmd", "command", "script", "code"):
            value = raw_input.get(key)
            if isinstance(value, str):
                command = value
                break
        if not command:
            command = json.dumps(raw_input, sort_keys=True)
    elif isinstance(raw_input, str):
        command = raw_input
    return tool_name.lower(), command


def is_inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def controller_command(command: str) -> bool:
    return "review_compile.py" in command or "resolve-review-compile" in command


def mutating_shell(command: str) -> str | None:
    patterns = [
        (r"\bgit\s+(?:-C\s+\S+\s+)?(?:add|apply|checkout|switch|reset|restore|commit|push|merge|rebase|cherry-pick|stash|clean|worktree)\b", "raw-git-mutation"),
        (r"(^|[;&|]\s*)(?:rm|mv|cp|mkdir|touch|install|truncate)\b", "filesystem-mutation"),
        (r"\bsed\s+-[^\n]*i\b|\bperl\s+-[^\n]*pi\b", "in-place-edit"),
        (r"(^|[^<>])>>?\s*[^\s&]", "shell-redirection"),
        (r"\b(?:apply_patch|write_file|edit_file)\b", "direct-edit-command"),
    ]
    for pattern, reason in patterns:
        if re.search(pattern, command, re.I):
            return reason
    return None


def guard_hook(args: argparse.Namespace) -> int:
    payload = json.loads(sys.stdin.read() or "{}")
    cwd = Path(args.cwd or payload.get("cwd") or os.getcwd()).resolve()
    root = find_state_root(cwd)
    if root is None:
        return emit({"status": "allow", "reason": "no-active-c3"})
    state = load_state(root)
    if state.get("phase") in TERMINAL_PHASES:
        return emit({"status": "allow", "reason": f"c3-{state.get('phase')}"})
    for lab in state.get("lab_roots", []):
        if is_inside(cwd, Path(lab)):
            return emit({"status": "allow", "reason": "c3-lab-context"})
    tool_name, command = extract_tool(payload)
    if controller_command(command):
        return emit({"status": "allow", "reason": "c3-controller-command"})
    if any(token in tool_name for token in ("apply_patch", "write_file", "edit_file", "notebook_edit")):
        return emit({"status": "block", "reason": f"C³ delivery is frozen in phase {state.get('phase')}. Work in the lab or use review_compile.py apply/commit/push."})
    if tool_name in {"exec_command", "shell", "bash", "terminal"} or command:
        reason = mutating_shell(command)
        if reason:
            return emit({"status": "block", "reason": f"C³ blocked {reason} in delivery phase {state.get('phase')}. Use the lab or the C³ controller."})
    return emit({"status": "allow", "reason": "read-only-or-unclassified"})


def hook_context(args: argparse.Namespace) -> int:
    cwd = Path(args.cwd or os.getcwd()).resolve()
    root = find_state_root(cwd)
    if root is None:
        return emit({"active": False})
    state = load_state(root)
    if state.get("phase") in TERMINAL_PHASES:
        return emit({"active": False, "phase": state.get("phase")})
    next_actions = {
        "collecting": "add counterexamples, set CEB-v1, register candidate tournament",
        "selected": "record ablation and candidate holdout, then certify-apply",
        "apply-certified": "use review_compile.py apply",
        "applied": "record current proof and delivery holdout, then certify-final",
        "final-certified": "use review_compile.py commit",
        "committed": "use review_compile.py push",
        "pushed": "record PR sweep with review_compile.py close",
        "invalidated": "reverse the delivery patch with reset-delivery, update the basis, and regenerate candidates",
    }
    context = (
        f"C³ resolve run {state.get('run_id')} is active.\n"
        f"Phase: {state.get('phase')}.\n"
        f"Immutable base: {state.get('base_sha')}.\n"
        f"Delivery is controller-gated. Direct edits, raw commit/amend, and raw push are forbidden.\n"
        f"Next: {next_actions.get(state.get('phase'), 'inspect review_compile.py status')}."
    )
    return emit({"active": True, "phase": state.get("phase"), "run_id": state.get("run_id"), "context": context})


def stop_guard(args: argparse.Namespace) -> int:
    payload = json.loads(sys.stdin.read() or "{}")
    cwd = Path(args.cwd or payload.get("cwd") or os.getcwd()).resolve()
    root = find_state_root(cwd)
    if root is None:
        return emit({"status": "allow", "reason": "no-active-c3"})
    state = load_state(root)
    if state.get("phase") in TERMINAL_PHASES:
        return emit({"status": "allow", "reason": f"c3-{state.get('phase')}"})
    last = str(payload.get("last_assistant_message") or "")
    if re.search(r"\b(done|resolved|complete|completed|ready|shipped|pushed|closed)\b", last, re.I):
        return emit({
            "status": "block",
            "reason": (
                f"C³ run {state.get('run_id')} is still in phase {state.get('phase')}. "
                "Do not claim resolve closure until review_compile.py close emits final MRPC-v1, "
                "or abort the run explicitly."
            ),
        })
    return emit({"status": "allow", "reason": "c3-active-no-wrap-up-claim"})


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="review_compile.py", description="C³ Counterexample Compression Compiler controller")
    sub = p.add_subparsers(dest="command", required=True)

    b = sub.add_parser("begin")
    b.add_argument("--root", default=".")
    b.add_argument("--acceptance")
    b.add_argument("--goal")
    b.add_argument("--lab")
    b.set_defaults(func=begin)

    abl = sub.add_parser("ablate")
    abl.add_argument("--root")
    abl.add_argument("--candidate-id", required=True)
    abl.add_argument("--input", required=True)
    abl.set_defaults(func=ablate_candidate)

    vc = sub.add_parser("verify-candidate")
    vc.add_argument("--root")
    vc.add_argument("--candidate-id", required=True)
    vc.add_argument("--input", required=True)
    vc.set_defaults(func=verify_candidate)

    cw = sub.add_parser("candidate-worktree")
    cw.add_argument("--root")
    cw.add_argument("--candidate-id", required=True)
    cw.add_argument("--path", required=True)
    cw.add_argument("--branch")
    cw.set_defaults(func=create_candidate_worktree)

    for name, func in [
        ("add-counterexample", add_counterexample),
        ("set-basis", set_basis),
        ("register-candidate", register_candidate),
        ("record-ablation", record_ablation),
        ("record-holdout", record_holdout),
        ("record-proof", record_proof),
        ("close", close_run),
    ]:
        sp = sub.add_parser(name)
        sp.add_argument("--root")
        sp.add_argument("--input", required=True)
        if name in {"register-candidate", "record-ablation"}:
            sp.add_argument("--worktree")
        if name == "register-candidate":
            sp.add_argument("--patch")
        if name == "record-holdout":
            sp.add_argument("--stage", choices=["candidate", "delivery"], required=True)
        sp.set_defaults(func=func)

    tw = sub.add_parser("tournament-waiver")
    tw.add_argument("--root")
    tw.add_argument("--reason", required=True)
    tw.set_defaults(func=set_tournament_waiver)

    rp = sub.add_parser("run-proof")
    rp.add_argument("--root")
    rp.add_argument("--input", required=True)
    rp.set_defaults(func=run_delivery_proof)

    for name, func in [
        ("select", select_candidate),
        ("certify-apply", certify_apply),
        ("apply", apply_selected),
        ("certify-final", certify_final),
        ("audit", audit_state),
        ("status", status),
    ]:
        sp = sub.add_parser(name)
        sp.add_argument("--root")
        sp.set_defaults(func=func)

    c = sub.add_parser("commit")
    c.add_argument("--root")
    c.add_argument("--message", required=True)
    c.set_defaults(func=commit_delivery)

    pu = sub.add_parser("push")
    pu.add_argument("--root")
    pu.add_argument("--remote", default="origin")
    pu.add_argument("--branch")
    pu.set_defaults(func=push_delivery)

    rd = sub.add_parser("reset-delivery")
    rd.add_argument("--root")
    rd.add_argument("--confirm", action="store_true")
    rd.set_defaults(func=reset_delivery)

    cl = sub.add_parser("cleanup-labs")
    cl.add_argument("--root")
    cl.add_argument("--confirm", action="store_true")
    cl.set_defaults(func=cleanup_labs)

    ab = sub.add_parser("abort")
    ab.add_argument("--root")
    ab.add_argument("--confirm", action="store_true")
    ab.add_argument("--reason", required=True)
    ab.set_defaults(func=abort_run)

    gh = sub.add_parser("guard-hook")
    gh.add_argument("--cwd")
    gh.set_defaults(func=guard_hook)

    hc = sub.add_parser("hook-context")
    hc.add_argument("--cwd")
    hc.set_defaults(func=hook_context)

    sg = sub.add_parser("stop-guard")
    sg.add_argument("--cwd")
    sg.set_defaults(func=stop_guard)

    return p


def main() -> int:
    try:
        args = parser().parse_args()
        return int(args.func(args))
    except C3Error as exc:
        return emit({"c3_error": {"message": str(exc)}}, exit_code=2)
    except json.JSONDecodeError as exc:
        return emit({"c3_error": {"message": f"invalid JSON: {exc}"}}, exit_code=1)
    except KeyboardInterrupt:
        return emit({"c3_error": {"message": "interrupted"}}, exit_code=130)
    except Exception as exc:
        return emit({"c3_error": {"message": f"unexpected error: {type(exc).__name__}: {exc}"}}, exit_code=1)


if __name__ == "__main__":
    raise SystemExit(main())
