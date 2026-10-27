#!/usr/bin/env python3
"""Optional compile-cost experiment; no claims about runtime or peak memory."""
from __future__ import annotations
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from toolchain import OPTIMIZE_MODES, ZIG_VERSION


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zig", default="zig")
    parser.add_argument("--sizes", type=int, nargs="+", default=[8, 32, 128])
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--optimize", choices=OPTIMIZE_MODES, default="fast")
    parser.add_argument("--target", help="optional Zig target; otherwise native")
    parser.add_argument("--cpu", help="optional explicit CPU/features passed as -mcpu")
    parser.add_argument("--timeout", type=float, default=120)
    args = parser.parse_args(argv)
    if args.samples < 1 or not math.isfinite(args.timeout) or args.timeout <= 0 or any(n < 0 or n > 1024 for n in args.sizes):
        parser.error("positive samples, finite positive timeout and sizes between 0 and 1024 are required")
    rows = []
    try:
        version = subprocess.run([args.zig, "version"], capture_output=True, text=True, check=True, timeout=args.timeout).stdout.strip()
        if version != ZIG_VERSION:
            print(f"VERSION_MISMATCH: expected {ZIG_VERSION}, observed {version}", file=sys.stderr)
            return 2
        for n in args.sizes:
            for sample in range(args.samples):
                strategies = ["direct", "plan", "runtime_table"]
                strategies = strategies[sample % 3:] + strategies[:sample % 3]
                for strategy in strategies:
                    with tempfile.TemporaryDirectory(prefix="zig-scaling-") as temporary:
                        temp = Path(temporary)
                        shutil.copyfile(Path(__file__).resolve().parents[1] / "references" / "comptime_scaling.zig", temp / "comptime_scaling.zig")
                        source = temp / "kernel.zig"
                        source.write_text('const scaling = @import("comptime_scaling.zig");\n'
                                          f'export fn measure(input: *const [{n}]u64) u64 {{\n'
                                          f'    return scaling.checksum(.{strategy}, {n}, input);\n}}\n')
                        output = temp / "kernel.o"
                        command = [args.zig, "build-obj", str(source), "-O", args.optimize,
                                   "--cache-dir", str(temp / "local"), "--global-cache-dir", str(temp / "global"),
                                   "-femit-bin=" + str(output)]
                        if args.target:
                            command += ["-target", args.target]
                        if args.cpu:
                            command += ["-mcpu=" + args.cpu]
                        start = time.perf_counter()
                        result = subprocess.run(command, capture_output=True, text=True, timeout=args.timeout)
                        elapsed = time.perf_counter() - start
                        if result.returncode:
                            print(result.stderr, file=sys.stderr)
                            return 1
                        rows.append({"size": n, "strategy": strategy, "sample": sample,
                                     "compile_seconds": elapsed, "object_bytes": output.stat().st_size,
                                     "command": command, "cache_state": "fresh local and global directories"})
        print(json.dumps({"zig_version": version, "optimize": args.optimize, "target": args.target or "native",
                          "cpu": args.cpu or "compiler default; not explicitly pinned",
                          "host": dict(zip(("sysname", "nodename", "release", "version", "machine"), os.uname())) if hasattr(os, "uname") else sys.platform,
                          "samples": rows, "runtime_latency": None, "compiler_peak_memory": None,
                          "limitations": ["No runtime benchmark or peak-memory measurement.",
                                          "OS page cache is not reset; compiler output may make variants equivalent.",
                                          "This measures direct cold compilation, not configure-cache hits or watch-mode rebuilds.",
                                          "Run check_zig_examples.py for correctness independently."]}, indent=2))
        return 0
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"PROFILE_UNAVAILABLE: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
