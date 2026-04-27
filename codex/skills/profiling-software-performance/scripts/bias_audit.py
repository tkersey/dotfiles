#!/usr/bin/env python3
"""
bias_audit.py — Static scan for known benchmark bias patterns.

Reads a hyperfine/criterion JSON output AND optionally one or more bench source
files (Rust .rs / Python .py / shell .sh / Go _test.go), and emits a markdown
report flagging suspicious patterns. Modeled after the FrankenSQLite benchmark
truthfulness audit — see references/UNBIASED-BENCHMARKING.md.

Usage:
    bias_audit.py [--json bench.json] [--source path ...] [--out report.md]

Exit codes:
    0 — no high-severity issues
    1 — at least one HIGH-severity flag
    2 — usage error
"""

from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional


HIGH = "HIGH"
MED = "MED"
LOW = "LOW"


def flag(severity: str, code: str, message: str, evidence: str = "") -> dict:
    return {"severity": severity, "code": code, "message": message, "evidence": evidence}


# ---- JSON-side checks ---------------------------------------------------

def check_json(path: Path) -> list[dict]:
    flags: list[dict] = []
    try:
        data = json.loads(path.read_text())
    except Exception as e:
        return [flag(HIGH, "json_unreadable", f"could not parse {path}: {e}")]

    results = data.get("results") or []
    for i, r in enumerate(results):
        cmd = r.get("command", f"#{i}")
        times = r.get("times") or []
        n = len(times)
        if n < 5:
            flags.append(flag(HIGH, "tiny_n",
                f"only {n} samples for `{cmd}` — p95 of N<5 is the max, not a percentile",
                evidence=f"results[{i}].times length={n}"))
        elif n < 20:
            flags.append(flag(MED, "small_n",
                f"only {n} samples for `{cmd}` — recommended floor is 20 (FrankenSQLite methodology)",
                evidence=f"results[{i}].times length={n}"))

        mean = r.get("mean", 0.0)
        stddev = r.get("stddev", 0.0)
        if mean > 0 and stddev / mean > 0.10:
            flags.append(flag(MED, "high_cv",
                f"CV (stddev/mean) = {stddev/mean*100:.1f}% > 10% for `{cmd}` — investigate noise",
                evidence=f"mean={mean*1000:.2f}ms stddev={stddev*1000:.2f}ms"))

        # Variation: criterion JSON sometimes uses 'iterations' field
        iters = r.get("iterations")
        if iters is not None and iters < 20:
            flags.append(flag(MED, "small_iter",
                f"`{cmd}` used only {iters} iterations",
                evidence=f"results[{i}].iterations={iters}"))

    if not results:
        flags.append(flag(HIGH, "no_results",
            "JSON has no .results[] array — is this a hyperfine/criterion file?"))

    return flags


# ---- Source-side checks -------------------------------------------------

# Each rule: regex, severity, code, message
SOURCE_RULES = [
    (re.compile(r'format!\s*\(\s*"[^"]*\{[^}]*\}', re.M), MED, "format_in_sql",
     "format!() with interpolated SQL: prevents prepared-statement cache reuse (FrankenSQLite audit)"),
    (re.compile(r'\.execute\s*\(\s*"[^"]*"\s*,\s*params!', re.M), LOW, "ad_hoc_sql_execute",
     "ad-hoc SQL via .execute(): is the comparison side using prepared statements? mismatched API class"),
    (re.compile(r'sleep\s*\(\s*Duration::from_(secs|millis)\s*\(', re.M), MED, "sleep_in_bench",
     "sleep() inside bench: warmup/wait inside the timed region inflates measurements"),
    (re.compile(r'#\[bench\]', re.M), LOW, "old_bench_attr",
     "#[bench] is unstable; prefer criterion 0.5+ for stable percentile reporting"),
    (re.compile(r'measurement_time\s*\(\s*Duration::from_(secs|millis)\s*\(\s*[1-9]\b', re.M), MED, "short_measurement",
     "measurement_time < 10s — Criterion default is fine, but explicit short windows reduce p95 stability"),
    (re.compile(r'sample_size\s*\(\s*([1-9]|1\d)\s*\)', re.M), MED, "small_sample_size",
     "sample_size < 20 in criterion config — fewer samples than the FrankenSQLite minimum of 20"),
    (re.compile(r'PRAGMA\s+(?!journal_mode|synchronous|page_size|temp_store|cache_size|mmap_size|auto_vacuum|locking_mode|busy_timeout)\w+\s*=', re.I | re.M), LOW, "non_canonical_pragma",
     "non-standard PRAGMA in bench setup — verify the comparison side sets the same value"),
    (re.compile(r'rand::random|rand::thread_rng', re.M), MED, "non_deterministic_rng",
     "non-seeded RNG in bench — workload changes between runs, kills reproducibility"),
    (re.compile(r'(println!|eprintln!|print|console\.log)\s*\(', re.M), LOW, "io_in_loop",
     "I/O call in source — verify it's outside the hot loop, otherwise it dominates measurement"),
    (re.compile(r'#\[cfg\s*\(\s*debug_assertions\s*\)\]', re.M), HIGH, "debug_only_path",
     "code path only runs in debug builds — bench should use release-perf profile"),
    (re.compile(r'opt-level\s*=\s*(?:[012]\b|"[012]")', re.M), HIGH, "low_opt_level",
     "opt-level < 3 in build profile — bench would measure unoptimized code"),
    (re.compile(r'lto\s*=\s*false', re.M), MED, "lto_disabled",
     "LTO disabled — FrankenSQLite methodology mandates LTO=true for release-perf"),
    (re.compile(r'\bdebug\s*=\s*true\b', re.M), MED, "debug_true",
     "debug=true in profile — adds frame overhead vs production profile"),
]


def check_source(path: Path) -> list[dict]:
    flags: list[dict] = []
    try:
        text = path.read_text()
    except Exception as e:
        return [flag(MED, "source_unreadable", f"could not read {path}: {e}")]

    for pat, sev, code, msg in SOURCE_RULES:
        for m in pat.finditer(text):
            line_no = text[: m.start()].count("\n") + 1
            flags.append(flag(sev, code, msg, evidence=f"{path.name}:{line_no}"))

    return flags


# ---- Reporter -----------------------------------------------------------

def render_report(json_flags: list[dict], src_flags: list[dict]) -> str:
    out = ["# Bias Audit Report\n"]
    severities = {HIGH: 0, MED: 0, LOW: 0}
    for f in json_flags + src_flags:
        severities[f["severity"]] = severities.get(f["severity"], 0) + 1
    out.append(f"**Counts:** HIGH={severities[HIGH]}  MED={severities[MED]}  LOW={severities[LOW]}\n")

    def section(title: str, flags: list[dict]) -> None:
        if not flags:
            return
        out.append(f"\n## {title}\n")
        out.append("| Severity | Code | Message | Evidence |\n|---|---|---|---|\n")
        for f in flags:
            out.append(f"| {f['severity']} | `{f['code']}` | {f['message']} | {f['evidence'] or '-'} |\n")

    section("JSON / harness output", json_flags)
    section("Bench source", src_flags)

    if not json_flags and not src_flags:
        out.append("\n*No flags raised. Bench appears clean by static rules — still walk the HONEST-GATE-CHECKLIST.*\n")

    out.append("\n---\nSee `references/HONEST-GATE-CHECKLIST.md` for the runtime gate to pair with this static scan.\n")
    return "".join(out)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", type=Path, help="hyperfine / criterion JSON output")
    ap.add_argument("--source", type=Path, action="append", default=[], help="bench source file (repeatable)")
    ap.add_argument("--out", type=Path, help="write markdown report to this file (else stdout)")
    args = ap.parse_args(argv[1:])

    if not args.json and not args.source:
        ap.error("provide at least one of --json or --source")

    json_flags = check_json(args.json) if args.json else []
    src_flags: list[dict] = []
    for s in args.source:
        src_flags.extend(check_source(s))

    report = render_report(json_flags, src_flags)

    if args.out:
        args.out.write_text(report)
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(report)

    high_count = sum(1 for f in json_flags + src_flags if f["severity"] == HIGH)
    return 1 if high_count else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
