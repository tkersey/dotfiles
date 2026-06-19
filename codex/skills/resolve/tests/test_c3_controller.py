#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "review_compile.py"
GATE = ROOT / "tools" / "mrpc_gate.py"
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

def sh(cwd: Path, *args: str, check: bool = True, stdin: str | None = None):
    proc = subprocess.run(
        list(args), cwd=cwd, input=stdin, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if check and proc.returncode != 0:
        raise AssertionError(f"{args} failed\nstdout={proc.stdout}\nstderr={proc.stderr}")
    return proc

def c3(cwd: Path, *args: str, check: bool = True, stdin: str | None = None):
    return sh(cwd, "python3", str(TOOL), *args, check=check, stdin=stdin)

def dump(path: Path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

def cost(**overrides):
    value = {field: 0 for field in COST_FIELDS}
    value.update(overrides)
    return value

def candidate(cid: str, route_class: str, route_family: str, semantic_cost, valid=True):
    return {
        "candidate_id": cid,
        "route_class": route_class,
        "route_family": route_family,
        "scope_valid": True,
        "semantic_cost": semantic_cost,
        "negative_route": {"status": "allowed", "refs": []},
        "verification": {
            "counterexamples_pass": valid,
            "acceptance_pass": valid,
            "regressions_pass": valid,
            "proof_current": valid,
            "falsified_routes_reused": False,
        },
    }

def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "repo"
        remote = Path(td) / "remote.git"
        root.mkdir()
        sh(root, "git", "init", "-b", "main")
        sh(root, "git", "config", "user.email", "test@example.com")
        sh(root, "git", "config", "user.name", "Test")
        (root / "app.txt").write_text("base\n", encoding="utf-8")
        sh(root, "git", "add", "app.txt")
        sh(root, "git", "commit", "-m", "base")
        sh(Path(td), "git", "init", "--bare", str(remote))
        sh(root, "git", "remote", "add", "origin", str(remote))
        sh(root, "git", "push", "-u", "origin", "main")

        acceptance = Path(td) / "acceptance.json"
        dump(acceptance, {"goal": "repair behavior", "proof_bar": ["test"]})
        lab = Path(td) / "lab"
        result = c3(root, "begin", "--root", ".", "--acceptance", str(acceptance), "--lab", str(lab))
        assert result.returncode == 0

        # Guard blocks direct delivery editing.
        payload = json.dumps({"tool_name": "apply_patch", "tool_input": {"patch": "***"}})
        guard = c3(root, "guard-hook", "--cwd", str(root), stdin=payload)
        assert json.loads(guard.stdout)["status"] == "block"

        finding = root / ".resolve-c3" / "finding.json"
        dump(finding, {
            "id": "F-1",
            "observed_behavior": "bad",
            "required_behavior": "good",
            "liability": "introduced_by_current_diff",
            "reproduction_or_proof": "fixture",
            "source_refs": ["review:1"],
        })
        c3(root, "add-counterexample", "--input", str(finding))

        basis = root / ".resolve-c3" / "basis.json"
        dump(basis, {
            "basis_version": "CEB-v1",
            "branch_liabilities": [{"finding_id": "F-1"}],
            "non_branch_liabilities": [],
            "families": [{
                "family_id": "family-1",
                "governing_rule": "good only",
                "independent_witnesses": ["F-1"],
                "subsumed_findings": [],
                "canonical_owner_candidates": ["app"],
                "proof_obligations": ["test"],
            }],
            "original_acceptance": ["base behavior"],
            "gate": {
                "all_findings_classified": "pass",
                "every_branch_liability_covered": "pass",
                "non_branch_liabilities_excluded": "pass",
            },
        })
        c3(root, "set-basis", "--input", str(basis))

        # Invalid no-change control.
        nochange = root / ".resolve-c3" / "nochange.json"
        dump(nochange, candidate("cand-control", "no-change", "proof-only", cost(), valid=False))
        c3(root, "register-candidate", "--input", str(nochange))

        # Existing-owner candidate.
        c2 = Path(td) / "candidate-existing"
        c3(root, "candidate-worktree", "--candidate-id", "cand-existing", "--path", str(c2))
        (c2 / "app.txt").write_text("base\nextra guard\n", encoding="utf-8")
        c2j = root / ".resolve-c3" / "c2.json"
        dump(c2j, candidate(
            "cand-existing", "existing-owner", "local-guard",
            cost(new_control_flow_branches=1, owners_modified=1, files_modified=1, ast_edit_count=2, production_net_lines=1),
        ))
        c3(root, "register-candidate", "--input", str(c2j), "--worktree", str(c2))
        c2proof = root / ".resolve-c3" / "c2-proof.json"
        dump(c2proof, {"checks": [
            {"kind": "counterexample", "command": "grep -q 'extra guard' app.txt"},
            {"kind": "acceptance", "command": "test -f app.txt"},
            {"kind": "regression", "command": "test $(wc -l < app.txt) -ge 1"}
        ]})
        c3(root, "verify-candidate", "--candidate-id", "cand-existing", "--input", str(c2proof))

        # Lower-cost subtractive/normalizing candidate.
        c3w = Path(td) / "candidate-subtractive"
        c3(root, "candidate-worktree", "--candidate-id", "cand-subtractive", "--path", str(c3w))
        (c3w / "app.txt").write_text("good\nunused\n", encoding="utf-8")
        c3j = root / ".resolve-c3" / "c3.json"
        dump(c3j, candidate(
            "cand-subtractive", "subtractive", "canonicalize",
            cost(owners_modified=1, files_modified=1, ast_edit_count=2, production_net_lines=1),
        ))
        c3(root, "register-candidate", "--input", str(c3j), "--worktree", str(c3w))
        c3proof = root / ".resolve-c3" / "c3-proof.json"
        dump(c3proof, {"checks": [
            {"kind": "counterexample", "command": "grep -qx 'good' app.txt"},
            {"kind": "acceptance", "command": "test -f app.txt"},
            {"kind": "regression", "command": "grep -q '^good$' app.txt"}
        ]})
        c3(root, "verify-candidate", "--candidate-id", "cand-subtractive", "--input", str(c3proof))

        selection = c3(root, "select")
        assert json.loads(selection.stdout)["candidate_tournament"]["selected_candidate"] == "cand-subtractive"

        ablation = root / ".resolve-c3" / "ablation.json"
        dump(ablation, {
            "semantic_cost_after": cost(owners_modified=1, files_modified=1, ast_edit_count=1, production_net_lines=0),
            "checks": [
                {"kind": "counterexample", "command": "grep -qx 'good' app.txt"},
                {"kind": "acceptance", "command": "test -f app.txt"},
                {"kind": "regression", "command": "test $(wc -l < app.txt) -eq 1"}
            ],
            "edit_atoms": [
                {
                    "edit_id": "edit-unused", "kind": "line",
                    "remove_command": "sed -i '/^unused$/d' app.txt",
                    "obligations": []
                },
                {
                    "edit_id": "edit-core", "kind": "replacement",
                    "remove_command": "printf 'base\n' > app.txt",
                    "restore_command": "printf 'good\n' > app.txt",
                    "obligations": ["family-1/test"],
                    "failure_witness": "removal restores bad behavior"
                }
            ]
        })
        c3(root, "ablate", "--candidate-id", "cand-subtractive", "--input", str(ablation))

        candidate_holdout = root / ".resolve-c3" / "candidate-holdout.json"
        dump(candidate_holdout, {
            "verdict": "clean",
            "new_branch_liabilities": [],
            "subsumed_witnesses": [],
            "adjacent_followups": [],
            "preferences_rejected": [],
        })
        c3(root, "record-holdout", "--stage", "candidate", "--input", str(candidate_holdout))
        c3(root, "certify-apply")
        c3(root, "apply")
        assert (root / "app.txt").read_text(encoding="utf-8") == "good\n"

        proof = root / ".resolve-c3" / "proof.json"
        dump(proof, {"checks": [{
            "kind": "proof",
            "command": "test $(cat app.txt) = good",
            "obligations": ["delivery-proof"]
        }]})
        c3(root, "run-proof", "--input", str(proof))

        delivery_holdout = root / ".resolve-c3" / "delivery-holdout.json"
        dump(delivery_holdout, {
            "verdict": "clean",
            "new_branch_liabilities": [],
            "subsumed_witnesses": [],
            "adjacent_followups": [],
            "preferences_rejected": [],
        })
        c3(root, "record-holdout", "--stage", "delivery", "--input", str(delivery_holdout))
        c3(root, "certify-final")
        c3(root, "commit", "--message", "Apply minimal review patch")
        c3(root, "push", "--remote", "origin")

        sweep = root / ".resolve-c3" / "sweep.json"
        dump(sweep, {"unresolved_branch_liabilities": [], "threads": 0, "pr_head_matches": True})
        c3(root, "close", "--input", str(sweep))

        gate = sh(root, "python3", str(GATE), str(root / ".resolve-c3" / "mrpc.json"))
        assert gate.returncode == 0, gate.stdout + gate.stderr
        audit = c3(root, "audit")
        assert json.loads(audit.stdout)["c3_audit"]["ok"] is True
        state = json.loads((root / ".resolve-c3" / "state.json").read_text())
        assert state["phase"] == "closed"
        c3(root, "cleanup-labs", "--confirm")

    print("resolve C³ tests: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
