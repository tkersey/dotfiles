#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "review_compile.py"
FIELDS = [
    "new_truth_owners", "new_public_symbols", "new_state_variants",
    "new_fallback_or_compatibility_paths", "new_protocol_cases",
    "new_control_flow_branches", "new_helpers_or_wrappers",
    "new_proof_obligations", "retained_retirable_surfaces",
    "owners_modified", "files_modified", "ast_edit_count",
    "production_net_lines", "test_net_lines",
]

def run(cwd: Path, *args: str, check=True):
    proc = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and proc.returncode != 0:
        raise AssertionError(proc.stdout + proc.stderr)
    return proc

def c3(cwd: Path, *args: str, check=True):
    return run(cwd, "python3", str(TOOL), *args, check=check)

def dump(path: Path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")

def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "repo"
        root.mkdir()
        run(root, "git", "init", "-b", "main")
        run(root, "git", "config", "user.email", "x@y")
        run(root, "git", "config", "user.name", "X")
        (root / "x.txt").write_text("bad\n")
        run(root, "git", "add", "x.txt")
        run(root, "git", "commit", "-m", "base")

        c3(root, "begin", "--goal", "repair x")
        d = root / ".resolve-c3"

        dump(d / "f.json", {
            "id": "F1", "observed_behavior": "bad", "required_behavior": "good",
            "liability": "introduced_by_current_diff", "reproduction_or_proof": "fixture",
        })
        c3(root, "add-counterexample", "--input", str(d / "f.json"))
        dump(d / "b.json", {
            "basis_version": "CEB-v1",
            "branch_liabilities": [{"finding_id": "F1"}],
            "non_branch_liabilities": [],
            "families": [{"family_id": "fam", "governing_rule": "good", "independent_witnesses": ["F1"], "proof_obligations": ["p"]}],
            "original_acceptance": [],
            "gate": {
                "all_findings_classified": "pass",
                "every_branch_liability_covered": "pass",
                "non_branch_liabilities_excluded": "pass",
            },
        })
        c3(root, "set-basis", "--input", str(d / "b.json"))
        c3(root, "tournament-waiver", "--reason", "isolated fixture")

        work = Path(td) / "candidate"
        c3(root, "candidate-worktree", "--candidate-id", "cand", "--path", str(work))
        (work / "x.txt").write_text("good\n")
        cost = {field: 0 for field in FIELDS}
        cost.update({"owners_modified": 1, "files_modified": 1, "ast_edit_count": 1})
        dump(d / "cand.json", {
            "candidate_id": "cand", "route_class": "existing-owner", "route_family": "normalize",
            "scope_valid": True, "semantic_cost": cost,
            "negative_route": {"status": "allowed", "refs": []},
            "verification": {
                "counterexamples_pass": True, "acceptance_pass": True,
                "regressions_pass": True, "proof_current": True,
                "falsified_routes_reused": False,
            },
        })
        c3(root, "register-candidate", "--input", str(d / "cand.json"), "--worktree", str(work))
        dump(d / "cand-proof.json", {"checks": [
            {"kind": "counterexample", "command": "grep -qx good x.txt"},
            {"kind": "acceptance", "command": "test -f x.txt"},
            {"kind": "regression", "command": "test $(wc -l < x.txt) -eq 1"}
        ]})
        c3(root, "verify-candidate", "--candidate-id", "cand", "--input", str(d / "cand-proof.json"))
        c3(root, "select")
        dump(d / "abl.json", {
            "semantic_cost_after": cost,
            "checks": [
                {"kind": "counterexample", "command": "grep -qx good x.txt"},
                {"kind": "acceptance", "command": "test -f x.txt"},
                {"kind": "regression", "command": "test $(wc -l < x.txt) -eq 1"}
            ],
            "edit_atoms": [{
                "edit_id": "e1", "kind": "replacement",
                "remove_command": "printf 'bad\n' > x.txt",
                "restore_command": "printf 'good\n' > x.txt",
                "obligations": ["fam/p"]
            }]
        })
        c3(root, "ablate", "--candidate-id", "cand", "--input", str(d / "abl.json"))
        dump(d / "h1.json", {"verdict": "clean", "new_branch_liabilities": []})
        c3(root, "record-holdout", "--stage", "candidate", "--input", str(d / "h1.json"))
        c3(root, "certify-apply")
        c3(root, "apply")
        assert (root / "x.txt").read_text() == "good\n"

        dump(d / "h2.json", {
            "verdict": "new-counterexample",
            "new_branch_liabilities": [{
                "id": "F2", "observed_behavior": "other bad", "required_behavior": "other good",
                "liability": "introduced_by_current_diff", "reproduction_or_proof": "holdout",
            }],
        })
        result = c3(root, "record-holdout", "--stage", "delivery", "--input", str(d / "h2.json"), check=False)
        assert result.returncode == 2
        state = json.loads((d / "state.json").read_text())
        assert state["phase"] == "invalidated"
        assert state["basis"] is None

        c3(root, "reset-delivery", "--confirm")
        assert (root / "x.txt").read_text() == "bad\n"
        state = json.loads((d / "state.json").read_text())
        assert state["phase"] == "collecting"

    print("resolve C³ invalidation test: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
