#!/usr/bin/env python3
"""Run selected positive examples and forced, diagnostic-specific negatives."""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

POSITIVE = ("comptime_patterns.zig", "derive_walk_policy.zig", "comptime_scaling.zig")


def invoke(command: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
    print("$ " + shlex.join(command), flush=True)
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zig", default="zig")
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--optimize", choices=("Debug", "ReleaseSafe", "ReleaseFast", "ReleaseSmall"), default="Debug")
    parser.add_argument("--timeout", type=float, default=120)
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    try:
        version = invoke([args.zig, "version"], args.timeout)
        if version.returncode or version.stdout.strip() != "0.16.0":
            print(f"VERSION_MISMATCH: expected 0.16.0, observed {version.stdout.strip()!r}", file=sys.stderr)
            return 2
        root = args.skill_root.resolve()
        negatives = sorted((root / "tests" / "compile_fail").glob("*.zig"))
        if not negatives:
            raise ValueError("no compile-fail fixtures discovered")
        with tempfile.TemporaryDirectory(prefix="zig-reference-tests-") as temporary:
            temp = Path(temporary)
            flags = ["-O", args.optimize, "--cache-dir", str(temp / "local"), "--global-cache-dir", str(temp / "global")]
            for name in POSITIVE:
                result = invoke([args.zig, "test", str(root / "references" / name), *flags], args.timeout)
                if result.returncode:
                    print(result.stdout + result.stderr, file=sys.stderr)
                    print(f"FAIL positive: {name}", file=sys.stderr)
                    return 1
                print(f"PASS positive: {name}")
            shutil.copyfile(root / "references" / "comptime_patterns.zig", temp / "comptime_patterns.zig")
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
        print(f"PASS: {len(POSITIVE)} positive files and {len(negatives)} forced compile-fail cases ({args.optimize})")
        return 0
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"COMPTIME_PROOF_UNAVAILABLE: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"INVALID_TEST_INPUT: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
