#!/usr/bin/env python3
"""Validate Universalist scaffold templates with available local tools.

This script is intentionally opportunistic: it validates Python templates with py_compile and uses language
compilers/typecheckers only when they are installed. Use --require-tools to fail when a tool is missing.
"""
from __future__ import annotations

import argparse
import importlib.util
import py_compile
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
EMIT = SCRIPT_DIR / "emit_scaffold.py"


def load_templates() -> dict[tuple[str, str], str]:
    spec = importlib.util.spec_from_file_location("emit_scaffold", EMIT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {EMIT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["emit_scaffold"] = module
    spec.loader.exec_module(module)
    return module.TEMPLATES


def run(cmd: list[str], cwd: Path) -> tuple[bool, str]:
    proc = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.returncode == 0, proc.stdout.strip()


def validate_python(code: str, tmp: Path) -> tuple[bool, str]:
    path = tmp / "scaffold.py"
    path.write_text(code, encoding="utf-8")
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError as exc:
        return False, str(exc)
    return True, "py_compile ok"


def validate_typescript(code: str, tmp: Path, require_tools: bool) -> tuple[bool, str]:
    tsc = shutil.which("tsc")
    if not tsc:
        return (False, "missing tsc") if require_tools else (True, "skipped: missing tsc")
    path = tmp / "scaffold.ts"
    path.write_text(code, encoding="utf-8")
    return run([tsc, "--noEmit", "--strict", str(path)], tmp)


def validate_go(code: str, tmp: Path, require_tools: bool) -> tuple[bool, str]:
    go = shutil.which("go")
    if not go:
        return (False, "missing go") if require_tools else (True, "skipped: missing go")
    mod = tmp / "go.mod"
    mod.write_text("module scaffold\n\ngo 1.20\n", encoding="utf-8")
    path = tmp / "scaffold.go"
    path.write_text(code, encoding="utf-8")
    return run([go, "test", "./..."], tmp)


def validate_rust(code: str, tmp: Path, require_tools: bool) -> tuple[bool, str]:
    rustc = shutil.which("rustc")
    if not rustc:
        return (False, "missing rustc") if require_tools else (True, "skipped: missing rustc")
    wrapped = f"#![allow(dead_code)]\n{code}\nfn main() {{}}\n"
    path = tmp / "scaffold.rs"
    path.write_text(wrapped, encoding="utf-8")
    return run([rustc, str(path), "-o", str(tmp / "scaffold")], tmp)


def validate(language: str, code: str, require_tools: bool) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        if language == "python":
            return validate_python(code, tmp)
        if language == "typescript":
            return validate_typescript(code, tmp, require_tools)
        if language == "go":
            return validate_go(code, tmp, require_tools)
        if language == "rust":
            return validate_rust(code, tmp, require_tools)
        return True, "skipped: no validator"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-tools", action="store_true", help="fail if optional compilers/typecheckers are missing")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    templates = load_templates()
    failed = False
    for (construction, language), code in sorted(templates.items()):
        ok, message = validate(language, code, args.require_tools)
        status = "ok" if ok else "FAIL"
        print(f"{status}: {construction}/{language}: {message}")
        failed = failed or not ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
