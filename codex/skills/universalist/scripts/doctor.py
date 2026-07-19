#!/usr/bin/env python3
"""Lightweight integrity and smoke doctor for the Universalist package.

This is intentionally not an architectural correctness test suite. It checks that the
package is internally coherent, the experimental nomination compiler can load its
registry and compile one evidence-bound example, generators fail closed, and the
representative mechanics entrypoints remain reachable.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
sys.dont_write_bytecode = True
import tomllib
from pathlib import Path
from typing import Any, Sequence

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - wrapper supplies dependency
    raise SystemExit("doctor requires PyYAML; use scripts/check_universalist_replacement.sh") from exc

ROOT = Path(__file__).resolve().parents[1]
CODEX_ROOT = ROOT.parent.parent
AGENT_ROOT = CODEX_ROOT / "agents"
COMPILER = ROOT / "scripts" / "compile_universal_problem.py"
REGISTRY = ROOT / "references" / "universal-construction-registry.yaml"
SAMPLE = ROOT / "examples" / "universal-problem.compatibility.json"


def fail(message: str) -> None:
    raise SystemExit(f"universalist doctor: {message}")


def run(command: Sequence[str], *, expect: int = 0, timeout: int = 20) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        list(command),
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )
    if completed.returncode != expect:
        detail = completed.stderr.strip() or completed.stdout.strip()
        fail(f"command failed ({completed.returncode}, expected {expect}): {' '.join(command)}\n{detail}")
    return completed


def load_compiler() -> Any:
    spec = importlib.util.spec_from_file_location("universalist_compiler", COMPILER)
    if spec is None or spec.loader is None:
        fail("cannot load experimental compiler")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def check_core() -> None:
    required = [
        "SKILL.md",
        "README.md",
        "package.json",
        "agents/openai.yaml",
        "references/universal-problem-ir.md",
        "references/universal-construction-registry.yaml",
        "references/decision-contract.yaml",
        "scripts/compile_universal_problem.py",
        "scripts/compile_universal_problem.sh",
        "scripts/emit_boundary_adapter.py",
        "scripts/detect_signals.py",
        "templates/universal-problem-certificate.md",
    ]
    for relative in required:
        if not (ROOT / relative).is_file():
            fail(f"missing required file: {relative}")

    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    expected = {
        "name": "universalist",
        "version": "17.1.0",
        "compiler_status": "experimental",
        "compiler_authority": "nomination_only",
        "universal_problem_ir": "universal-problem/v6",
        "registry_schema": "universal-construction-registry/v6",
        "tests_shipped": False,
        "validation_surface": "single-doctor",
    }
    for key, value in expected.items():
        if package.get(key) != value:
            fail(f"package metadata mismatch for {key}: {package.get(key)!r}")

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    parts = skill.split("---", 2)
    if len(parts) < 3:
        fail("SKILL.md frontmatter is malformed")
    match = re.search(r'^description:\s*["\']?(.*?)["\']?\s*$', parts[1], flags=re.M)
    if not match:
        fail("SKILL.md is missing a description")
    description = match.group(1)
    if len(description) >= 1024:
        fail(f"SKILL.md description is too long: {len(description)}")
    for phrase in (
        "boundary consideration itself is the signal",
        "hidden categorical nomination protocol",
        "root workflow adjudicates",
        "nomination",
    ):
        if phrase.lower() not in skill.lower():
            fail(f"SKILL.md missing governing phrase: {phrase}")

    openai = yaml.safe_load((ROOT / "agents/openai.yaml").read_text(encoding="utf-8"))
    if openai.get("policy", {}).get("allow_implicit_invocation") is not True:
        fail("implicit invocation is not enabled")
    prompt = openai.get("interface", {}).get("default_prompt", "")
    if "ordinary" not in prompt.lower() or "hidden" not in prompt.lower():
        fail("default prompt does not begin from the ordinary candidate and hidden shadow")

    agents = sorted(AGENT_ROOT.glob("universalist-*.toml"))
    if len(agents) != 8:
        fail(f"expected 8 bundled agents, found {len(agents)}")
    for path in agents:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        instructions = data.get("developer_instructions", "")
        if not data.get("name") or not data.get("description") or not instructions:
            fail(f"invalid agent metadata: {path.name}")
        if "Do not spawn subagents" not in instructions:
            fail(f"agent permits recursive delegation: {path.name}")

    for path in sorted((ROOT / "scripts").glob("*.py")):
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except SyntaxError as exc:
            fail(f"Python syntax error in {path.name}: {exc}")
    for path in sorted((ROOT / "scripts").glob("*.sh")):
        run(["bash", "-n", str(path)])


def check_compiler() -> None:
    module = load_compiler()
    registry = module.load_registry(REGISTRY)
    cards = registry.get("constructions", [])
    if len(cards) != 55:
        fail(f"expected 55 theorem cards, found {len(cards)}")
    selectable = [card for card in cards if card.get("selection_mode") == "selectable"]
    support = [card for card in cards if card.get("selection_mode") == "support_only"]
    if len(selectable) != 53 or len(support) != 2:
        fail(f"registry mode counts are wrong: selectable={len(selectable)} support={len(support)}")

    problem = module.load_problem(SAMPLE, registry)
    certificate = module.compile_problem(problem, registry)
    nomination = certificate.get("nomination", {})
    if nomination.get("status") != "nominated":
        fail(f"sample packet was not nominated: {nomination}")
    if nomination.get("construction_key") != "compatibility_object":
        fail(f"sample nominated the wrong card: {nomination}")
    if certificate.get("compiler_authority") != "nomination-only":
        fail("compiler authority is not nomination-only")
    if certificate.get("decision_authority") != "root-workflow":
        fail("root workflow is not the decision authority")
    if certificate.get("root_adjudication_required") is not True:
        fail("sample does not require root adjudication")
    if certificate.get("theory_exposed") is not False:
        fail("plain output unexpectedly exposes theory")

    expert = module.compile_problem(problem, registry, explain_theory=True)
    candidates = expert.get("candidates", [])
    selected = next((item for item in candidates if item.get("construction_key") == "compatibility_object"), None)
    if selected is None or selected.get("expert_name") != "Pullback":
        fail("expert mode does not expose the Pullback derivation")

    output = module.render_markdown(certificate)
    if "Pullback" in output:
        fail("plain compiler output leaked the expert name")
    for phrase in ("root adjudication required", "authority boundary", "nomination"):
        if phrase.lower() not in output.lower():
            fail(f"compiler certificate missing phrase: {phrase}")


def check_generators() -> None:
    decoder = run([sys.executable, "scripts/emit_boundary_adapter.py", "decoder", "typescript"]).stdout
    for forbidden in ("input as CoreShape", "return input", " as Readonly"):
        if forbidden in decoder:
            fail(f"unsafe TypeScript decoder construct returned: {forbidden}")
    if "VALIDATION_NOT_IMPLEMENTED" not in decoder:
        fail("TypeScript decoder does not fail closed")

    py_decoder = run([sys.executable, "scripts/emit_boundary_adapter.py", "decoder", "python"]).stdout
    if "return value" in py_decoder or "typing import Any" in py_decoder:
        fail("Python decoder contains an identity or Any boundary")
    if "VALIDATION_NOT_IMPLEMENTED" not in py_decoder:
        fail("Python decoder does not fail closed")

    run([sys.executable, "scripts/emit_boundary_adapter.py", "typescript", "decoder"], expect=2)
    run([sys.executable, "scripts/detect_signals.py", str(ROOT / "SKILL.md"), "--max-files", "5"])


def check_mechanics(scope: str) -> None:
    commands: dict[str, list[list[str]]] = {
        "pullback-pushout": [
            ["scripts/emit_mechanics_report.sh", "pullback", "agnostic"],
            ["scripts/emit_mechanics_report.sh", "pushout", "agnostic"],
            ["scripts/emit_mechanics_report.sh", "double-pushout", "agnostic"],
        ],
        "spatial": [
            ["scripts/emit_mechanics_report.sh", "comonad-space", "agnostic"],
            ["scripts/emit_mechanics_report.sh", "density-comonad", "agnostic"],
            ["scripts/emit_mechanics_report.sh", "continuous-comonad-map", "agnostic"],
        ],
        "day": [
            ["scripts/emit_mechanics_report.sh", "day-convolution", "agnostic"],
            ["scripts/emit_mechanics_report.sh", "promonoidal-convolution", "agnostic"],
            ["scripts/emit_mechanics_report.sh", "applicative-convolution", "agnostic"],
        ],
        "context": [
            ["scripts/emit_mechanics_report.sh", "tambara-module", "agnostic"],
            ["scripts/emit_mechanics_report.sh", "mixed-optic", "agnostic"],
            ["scripts/emit_mechanics_report.sh", "dependent-tambara", "agnostic"],
        ],
    }
    for command in commands[scope]:
        run(command)
    if scope == "day":
        run(["scripts/emit_mechanics_report.sh", "convolution", "agnostic"], expect=2)
    if scope == "context":
        run(["scripts/emit_mechanics_report.sh", "tambara", "agnostic"], expect=2)


def version_tuple(raw: str) -> tuple[int, int, int]:
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", raw)
    if not match:
        fail(f"cannot parse version from: {raw!r}")
    return tuple(int(part) for part in match.groups())


def check_toolchain() -> None:
    seq_version = run(["seq", "--version"]).stdout or run(["seq", "--version"]).stderr
    if version_tuple(seq_version) < (0, 3, 51):
        fail(f"Skills Seq is too old: {seq_version.strip()}")
    capabilities = json.loads(run(["seq", "capabilities", "--format", "json"]).stdout)
    features = capabilities.get("features", capabilities)
    if features.get("skill_contract_v1") is not True:
        fail("the resolved seq command is not Skills Seq with skill-contract support")
    run(["seq", "skill-contract", "--help"])

    ledger_version = run(["ledger", "--version"]).stdout or run(["ledger", "--version"]).stderr
    if version_tuple(ledger_version) < (0, 10, 4):
        fail(f"Ledger is too old: {ledger_version.strip()}")
    create_help = run(["ledger", "create", "--help"]).stdout
    emit_help = run(["ledger", "emit", "--help"]).stdout
    for token in ("--source", "--repo", "--template"):
        if token not in create_help:
            fail(f"resolved ledger command lacks create {token}")
    for token in ("--contract", "--selected-route", "--write-plan"):
        if token not in emit_help:
            fail(f"resolved ledger command lacks emit {token}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scope",
        choices=("core", "compiler", "pullback-pushout", "spatial", "day", "context"),
        default="core",
    )
    parser.add_argument("--full", action="store_true", help="run all package and mechanics smoke checks")
    parser.add_argument("--toolchain", action="store_true", help="also verify Ledger and Skills Seq identity")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    scopes = [args.scope]
    if args.full:
        scopes = ["core", "compiler", "pullback-pushout", "spatial", "day", "context"]

    for scope in scopes:
        if scope == "core":
            check_core()
            check_generators()
        elif scope == "compiler":
            check_compiler()
        else:
            check_mechanics(scope)
        print(f"doctor: {scope}: ok")

    if args.toolchain:
        check_toolchain()
        print("doctor: toolchain: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
