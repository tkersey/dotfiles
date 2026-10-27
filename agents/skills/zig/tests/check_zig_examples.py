#!/usr/bin/env python3
"""Check all reference files and forced, diagnostic-specific negative fixtures."""
from __future__ import annotations
import argparse
import math
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from toolchain import OPTIMIZE_MODES, ZIG_VERSION


def invoke(command: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
    print("$ " + shlex.join(command), flush=True)
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zig", default="zig")
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--optimize", choices=OPTIMIZE_MODES, default="debug")
    parser.add_argument("--compile-only", action="store_true", help="analyze tests without executing them")
    parser.add_argument("--target", help="cross-compilation target; requires --compile-only")
    parser.add_argument("--timeout", type=float, default=120)
    args = parser.parse_args(argv)
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be finite and positive")
    if args.target and not args.compile_only:
        parser.error("--target requires --compile-only; use a project harness for target execution")
    try:
        version = invoke([args.zig, "version"], args.timeout)
        if version.returncode or version.stdout.strip() != ZIG_VERSION:
            print(f"VERSION_MISMATCH: expected {ZIG_VERSION}, observed {version.stdout.strip()!r}", file=sys.stderr)
            return 2
        root = args.skill_root.resolve()
        positives = sorted((root / "references").glob("*.zig"))
        negatives = sorted((root / "tests" / "compile_fail").glob("*.zig"))
        if not positives or not negatives:
            raise ValueError("positive references and compile-fail fixtures must both be present")
        with tempfile.TemporaryDirectory(prefix="zig-reference-tests-") as temporary:
            temp = Path(temporary)
            flags = ["-O", args.optimize, "--cache-dir", str(temp / "local"), "--global-cache-dir", str(temp / "global")]
            if args.compile_only:
                flags += ["--test-no-exec", "-femit-bin=" + str(temp / "test-artifact")]
            if args.target:
                flags += ["-target", args.target]
            for source in positives:
                result = invoke([args.zig, "test", str(source), *flags], args.timeout)
                if result.returncode:
                    print(result.stdout + result.stderr, file=sys.stderr)
                    print(f"FAIL positive: {source.name}", file=sys.stderr)
                    return 1
                action = "compiled (not executed)" if args.compile_only else "executed"
                print(f"PASS positive: {source.name} ({action})")
                shutil.copyfile(source, temp / source.name)
            for fixture in negatives:
                text = fixture.read_text()
                expected = re.findall(r"^// EXPECT: (.+)$", text, re.MULTILINE)
                if len(expected) != 1:
                    raise ValueError(f"{fixture.name}: expected exactly one diagnostic marker")
                target = temp / "negative.zig"
                target.write_text(text)
                result = invoke([args.zig, "test", str(target), *flags], args.timeout)
                diagnostic = re.compile(r"(?:^|\n)[^\n]*\berror: " + re.escape(expected[0]) + r"(?:\r?\n|$)")
                if result.returncode <= 0 or not diagnostic.search(result.stderr):
                    print(result.stdout + result.stderr, file=sys.stderr)
                    print(f"FAIL negative: {fixture.name}: expected intentional diagnostic {expected[0]!r}", file=sys.stderr)
                    return 1
                print(f"PASS negative: {fixture.name}")
        lane = "compile-only; no runtime evidence" if args.compile_only else "native execution"
        print(f"PASS: {len(positives)} positive files and {len(negatives)} forced compile-fail cases ({args.optimize}; {lane})")
        return 0
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"COMPTIME_PROOF_UNAVAILABLE: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"INVALID_TEST_INPUT: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
