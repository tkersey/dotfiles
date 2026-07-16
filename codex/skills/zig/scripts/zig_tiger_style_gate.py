#!/usr/bin/env python3
"""Validate ZTS-v1 contracts and audit Zig source with a Tiger Style ratchet."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Any, Sequence

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

REPORT_SCHEMA = "zig-tiger-style-report/v1"
STYLE_VERSION = "ZTS-v1"
WORKTREE = "WORKTREE"

LINE_LIMIT = 100
FUNCTION_LIMIT = 70
MAX_FILES = 4096
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_TOTAL_BYTES = 64 * 1024 * 1024
MAX_GIT_OUTPUT_BYTES = 64 * 1024 * 1024
MAX_DIAGNOSTICS = 4096

PRIORITY_ORDER = ["safety", "performance", "developer-experience"]
YES = {"yes", True}
NO = {"no", False}

EXCEPTION_CLASSES = {
    "assertions",
    "best-effort",
    "catch-unreachable",
    "function-lines",
    "implicit-options",
    "loop",
    "recursion",
}
EXCEPTION_RE = re.compile(
    r"//\s*tiger-style:\s*allow\((?P<kind>[^)]+)\)\s+reason=(?P<reason>.+?)\s*$"
)
FUNCTION_RE = re.compile(
    r"\bfn\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\("
)
TEST_RE = re.compile(r"^\s*test(?:\s|\{|$)")
HUNK_RE = re.compile(
    r"^@@\s+-\d+(?:,\d+)?\s+\+(?P<start>\d+)(?:,(?P<count>\d+))?\s+@@"
)
BOUNDARY_NAME_RE = re.compile(
    r"(?:parse|decode|encode|validate|verify|read|write|append|commit|load|store|"
    r"persist|replay|apply|recover|transition|publish|snapshot|fold|open|close)",
    re.IGNORECASE,
)
ASSERT_RE = re.compile(r"(?:\bassert|std\.debug\.assert)\s*\(")
COMPOUND_ASSERT_RE = re.compile(
    r"(?:\bassert|std\.debug\.assert)\s*\([^\n;]*(?:\band\b|\bor\b)"
)
IMPLICIT_OPTIONS_RE = re.compile(
    r"(?:std\.process\.(?:run|spawn)|\.(?:openFile|createFile|openDir|createDir|"
    r"statFile|reader|writer))\s*\([^;\n]*\.\{\s*\}\s*\)"
)


@dataclass(frozen=True)
class Diagnostic:
    path: str
    line: int
    severity: str
    code: str
    message: str


@dataclass(frozen=True)
class ExceptionDirective:
    line: int
    kind: str
    reason: str


@dataclass(frozen=True)
class FunctionSpan:
    name: str
    occurrence: int
    start_line: int
    body_line: int
    end_line: int

    @property
    def length(self) -> int:
        return self.end_line - self.start_line + 1

    @property
    def key(self) -> tuple[str, int]:
        return (self.name, self.occurrence)


@dataclass(frozen=True)
class DiffFile:
    path: str
    base_path: str | None
    changed_lines: frozenset[int]


@dataclass(frozen=True)
class FileSnapshot:
    path: str
    text: str
    base_text: str | None
    changed_lines: frozenset[int]


class AuditFailure(RuntimeError):
    """The gate could not establish a trustworthy result."""


def run_git(root: Path, args: Sequence[str], *, allow_failure: bool = False) -> bytes:
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if len(proc.stdout) > MAX_GIT_OUTPUT_BYTES or len(proc.stderr) > MAX_GIT_OUTPUT_BYTES:
        raise AuditFailure("git output exceeded the 64 MiB gate limit")
    if proc.returncode != 0 and not allow_failure:
        detail = proc.stderr.decode("utf-8", errors="replace").strip()
        raise AuditFailure(detail or f"git {' '.join(args)} failed")
    return proc.stdout


def load_mapping(path: str, wrapper: str) -> dict[str, Any]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    if path.endswith(".json") or path == "-" and text.lstrip().startswith("{"):
        value = json.loads(text)
    else:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML contracts")
        value = yaml.safe_load(text)
    if not isinstance(value, dict):
        raise ValueError("contract must be an object")
    body = value.get(wrapper, value)
    if not isinstance(body, dict):
        raise ValueError(f"{wrapper} must be an object")
    return body


def require_nonempty_string(
    value: Any,
    field: str,
    errors: list[str],
) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field}:missing")
        return ""
    return value.strip()


def require_string_list(
    value: Any,
    field: str,
    errors: list[str],
    *,
    nonempty: bool = False,
) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        errors.append(f"{field}:must-be-string-list")
        return []
    if nonempty and not value:
        errors.append(f"{field}:empty")
    return value


def evidence_or_reason(
    body: dict[str, Any],
    evidence_field: str,
    reason_field: str,
    errors: list[str],
) -> None:
    evidence = body.get(evidence_field)
    reason = body.get(reason_field)
    evidence_present = isinstance(evidence, list) and bool(evidence)
    reason_present = isinstance(reason, str) and bool(reason.strip())
    if evidence is not None and not isinstance(evidence, list):
        errors.append(f"{evidence_field}:must-be-list")
    if not evidence_present and not reason_present:
        errors.append(f"{evidence_field}:evidence-or-reason-required")
    if evidence_present and reason_present:
        errors.append(f"{evidence_field}:evidence-and-reason-conflict")


def validate_zts(contract: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if contract.get("style_version") != STYLE_VERSION:
        errors.append("style_version")

    artifact = contract.get("artifact_state")
    if not isinstance(artifact, dict):
        errors.append("artifact_state:must-be-object")
        artifact = {}
    for field in ("repository_root", "head", "dirty_fingerprint", "zig_version"):
        require_nonempty_string(artifact.get(field), f"artifact_state.{field}", errors)

    material = contract.get("material")
    if material not in YES | NO:
        errors.append("material:expected-yes-or-no")

    priority = require_string_list(
        contract.get("priority_order"),
        "priority_order",
        errors,
        nonempty=True,
    )
    if priority and priority != PRIORITY_ORDER:
        errors.append("priority_order:must-be-safety-performance-developer-experience")

    if material in YES:
        evidence_or_reason(
            contract,
            "bounds",
            "bounds_not_applicable_reason",
            errors,
        )
        evidence_or_reason(
            contract,
            "assertion_pairs",
            "assertions_not_applicable_reason",
            errors,
        )
        performance = contract.get("performance_sketch")
        performance_reason = contract.get("performance_not_applicable_reason")
        performance_present = isinstance(performance, dict) and bool(performance)
        reason_present = isinstance(performance_reason, str) and bool(performance_reason.strip())
        if performance is not None and not isinstance(performance, dict):
            errors.append("performance_sketch:must-be-object")
        if not performance_present and not reason_present:
            errors.append("performance_sketch:evidence-or-reason-required")
        if performance_present and reason_present:
            errors.append("performance_sketch:evidence-and-reason-conflict")
        if performance_present:
            for resource in ("network", "disk", "memory", "cpu"):
                require_nonempty_string(
                    performance.get(resource),
                    f"performance_sketch.{resource}",
                    errors,
                )
    else:
        require_nonempty_string(
            contract.get("nonmaterial_reason"),
            "nonmaterial_reason",
            errors,
        )

    bounds = contract.get("bounds", [])
    if isinstance(bounds, list):
        for index, row in enumerate(bounds):
            if not isinstance(row, dict):
                errors.append(f"bounds[{index}]:must-be-object")
                continue
            for field in ("operation", "resource", "limit", "failure"):
                require_nonempty_string(row.get(field), f"bounds[{index}].{field}", errors)

    pairs = contract.get("assertion_pairs", [])
    if isinstance(pairs, list):
        for index, row in enumerate(pairs):
            if not isinstance(row, dict):
                errors.append(f"assertion_pairs[{index}]:must-be-object")
                continue
            for field in ("invariant", "positive_site", "negative_site"):
                require_nonempty_string(
                    row.get(field),
                    f"assertion_pairs[{index}].{field}",
                    errors,
                )

    control_flow = contract.get("control_flow")
    if material in YES and not isinstance(control_flow, dict):
        errors.append("control_flow:must-be-object")
        control_flow = {}
    if isinstance(control_flow, dict) and material in YES:
        recursion = require_nonempty_string(
            control_flow.get("recursion"),
            "control_flow.recursion",
            errors,
        )
        if recursion not in {"none", "bounded-explicit"}:
            errors.append("control_flow.recursion:invalid")
        if control_flow.get("unbounded_loops") not in NO:
            errors.append("control_flow.unbounded_loops:must-be-no")
        if control_flow.get("function_growth_reviewed") not in YES:
            errors.append("control_flow.function_growth_reviewed:must-be-yes")

    error_contract = contract.get("errors")
    if material in YES and not isinstance(error_contract, dict):
        errors.append("errors:must-be-object")
        error_contract = {}
    if isinstance(error_contract, dict) and material in YES:
        if error_contract.get("operating_errors_handled") not in YES:
            errors.append("errors.operating_errors_handled:must-be-yes")
        if error_contract.get("programmer_errors_asserted") not in YES:
            errors.append("errors.programmer_errors_asserted:must-be-yes")
        best_effort = error_contract.get("best_effort_sites")
        if not isinstance(best_effort, list):
            errors.append("errors.best_effort_sites:must-be-list")

    exceptions = contract.get("exceptions", [])
    if not isinstance(exceptions, list):
        errors.append("exceptions:must-be-list")
        exceptions = []
    for index, row in enumerate(exceptions):
        if not isinstance(row, dict):
            errors.append(f"exceptions[{index}]:must-be-object")
            continue
        kind = require_nonempty_string(row.get("kind"), f"exceptions[{index}].kind", errors)
        if kind and kind not in EXCEPTION_CLASSES:
            errors.append(f"exceptions[{index}].kind:unknown")
        require_nonempty_string(row.get("reason"), f"exceptions[{index}].reason", errors)
        require_nonempty_string(row.get("scope"), f"exceptions[{index}].scope", errors)
        require_nonempty_string(row.get("proof"), f"exceptions[{index}].proof", errors)

    gate = contract.get("gate")
    if not isinstance(gate, dict):
        errors.append("gate:must-be-object")
        gate = {}
    if gate.get("classified_before_first_edit") not in YES:
        errors.append("gate.classified_before_first_edit:not-yes")
    if gate.get("mutation_allowed") not in YES | NO:
        errors.append("gate.mutation_allowed:expected-yes-or-no")
    if errors and gate.get("mutation_allowed") in YES:
        errors.append("gate.mutation_allowed:cannot-be-yes-with-errors")

    if len(exceptions) > 4:
        warnings.append("exceptions:high-count-review-design")

    return {
        "zig_tiger_style_gate": {
            "schema": REPORT_SCHEMA,
            "verdict": "pass" if not errors else "fail",
            "material": material in YES,
            "errors": errors,
            "warnings": warnings,
        }
    }


def is_zig_path(path: str) -> bool:
    posix = PurePosixPath(path)
    return posix.suffix == ".zig" or posix.name == "build.zig"


def normalize_diff_path(raw: str) -> str | None:
    if raw == "/dev/null":
        return None
    if raw.startswith("a/") or raw.startswith("b/"):
        raw = raw[2:]
    return raw


def parse_unified_diff(diff_text: str) -> dict[str, DiffFile]:
    files: dict[str, DiffFile] = {}
    base_path: str | None = None
    current_path: str | None = None
    changed: set[int] = set()

    def flush() -> None:
        nonlocal base_path, current_path, changed
        if current_path is not None and is_zig_path(current_path):
            files[current_path] = DiffFile(
                path=current_path,
                base_path=base_path,
                changed_lines=frozenset(changed),
            )
        base_path = None
        current_path = None
        changed = set()

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            flush()
        elif line.startswith("--- "):
            base_path = normalize_diff_path(line[4:].split("\t", 1)[0])
        elif line.startswith("+++ "):
            current_path = normalize_diff_path(line[4:].split("\t", 1)[0])
        elif line.startswith("@@ ") and current_path is not None:
            match = HUNK_RE.match(line)
            if not match:
                raise AuditFailure(f"unable to parse diff hunk: {line}")
            start = int(match.group("start"))
            count = int(match.group("count") or "1")
            changed.update(range(start, start + count))
    flush()
    return files


def decode_zig_bytes(path: str, data: bytes) -> str:
    if len(data) > MAX_FILE_BYTES:
        raise AuditFailure(f"{path}: file exceeds the 8 MiB gate limit")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AuditFailure(f"{path}: source is not valid UTF-8: {exc}") from exc


def read_worktree_file(root: Path, path: str) -> bytes | None:
    candidate = root / path
    if not candidate.is_file():
        return None
    return candidate.read_bytes()


def read_ref_file(root: Path, ref: str, path: str) -> bytes | None:
    output = run_git(root, ["show", f"{ref}:{path}"], allow_failure=True)
    return output or None


def list_all_files(root: Path) -> list[str]:
    raw = run_git(root, ["ls-files", "-z"])
    return sorted(
        path.decode("utf-8")
        for path in raw.split(b"\0")
        if path and is_zig_path(path.decode("utf-8"))
    )


def changed_snapshots(root: Path, base: str, head: str) -> list[FileSnapshot]:
    if head == WORKTREE:
        diff = run_git(root, ["diff", "--unified=0", "--no-ext-diff", "--find-renames", base, "--"])
    else:
        diff = run_git(
            root,
            ["diff", "--unified=0", "--no-ext-diff", "--find-renames", base, head, "--"],
        )
    files = parse_unified_diff(diff.decode("utf-8", errors="strict"))

    if head == WORKTREE:
        raw_untracked = run_git(root, ["ls-files", "--others", "--exclude-standard", "-z"])
        for item in raw_untracked.split(b"\0"):
            if not item:
                continue
            path = item.decode("utf-8")
            if not is_zig_path(path):
                continue
            data = read_worktree_file(root, path)
            if data is None:
                continue
            line_count = len(decode_zig_bytes(path, data).splitlines())
            files[path] = DiffFile(path, None, frozenset(range(1, line_count + 1)))

    snapshots: list[FileSnapshot] = []
    total_bytes = 0
    for path in sorted(files):
        item = files[path]
        current_data = (
            read_worktree_file(root, path)
            if head == WORKTREE
            else read_ref_file(root, head, path)
        )
        if current_data is None:
            continue
        current_text = decode_zig_bytes(path, current_data)
        total_bytes += len(current_data)
        if total_bytes > MAX_TOTAL_BYTES:
            raise AuditFailure("audited source exceeded the 64 MiB aggregate limit")
        base_text = None
        if item.base_path:
            base_data = read_ref_file(root, base, item.base_path)
            if base_data is not None:
                base_text = decode_zig_bytes(item.base_path, base_data)
        snapshots.append(FileSnapshot(path, current_text, base_text, item.changed_lines))
    return snapshots


def all_snapshots(root: Path, paths: Sequence[str] | None = None) -> list[FileSnapshot]:
    selected = list(paths) if paths else list_all_files(root)
    if len(selected) > MAX_FILES:
        raise AuditFailure(f"file count exceeds the {MAX_FILES} file limit")
    snapshots: list[FileSnapshot] = []
    total_bytes = 0
    for raw_path in sorted(set(selected)):
        path = PurePosixPath(raw_path).as_posix()
        if not is_zig_path(path):
            continue
        data = read_worktree_file(root, path)
        if data is None:
            raise AuditFailure(f"{path}: file not found")
        text = decode_zig_bytes(path, data)
        total_bytes += len(data)
        if total_bytes > MAX_TOTAL_BYTES:
            raise AuditFailure("audited source exceeded the 64 MiB aggregate limit")
        line_count = len(text.splitlines())
        snapshots.append(FileSnapshot(path, text, None, frozenset(range(1, line_count + 1))))
    return snapshots


def mask_code_line(line: str) -> str:
    if line.lstrip().startswith("\\\\"):
        return " " * len(line)
    output = list(line)
    quote: str | None = None
    escaped = False
    index = 0
    while index < len(line):
        char = line[index]
        if quote is not None:
            output[index] = " "
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char == "/" and index + 1 < len(line) and line[index + 1] == "/":
            for rest in range(index, len(line)):
                output[rest] = " "
            break
        if char in {'"', "'"}:
            quote = char
            output[index] = " "
        index += 1
    return "".join(output)


def find_function_spans(text: str) -> list[FunctionSpan]:
    lines = text.splitlines()
    spans: list[FunctionSpan] = []
    occurrences: dict[str, int] = {}
    pending_name: str | None = None
    pending_start = 0
    body_start = 0
    depth = 0

    for line_number, raw in enumerate(lines, 1):
        code = mask_code_line(raw)
        if pending_name is None:
            match = FUNCTION_RE.search(code)
            if match:
                pending_name = match.group("name")
                pending_start = line_number
            elif TEST_RE.match(raw):
                pending_name = f"test@{line_number}"
                pending_start = line_number
            else:
                continue

        if body_start == 0:
            if ";" in code and "{" not in code:
                pending_name = None
                pending_start = 0
                continue
            opening = code.count("{")
            closing = code.count("}")
            if opening == 0:
                continue
            body_start = line_number
            depth = opening - closing
        else:
            depth += code.count("{") - code.count("}")

        if body_start and depth <= 0:
            assert pending_name is not None
            occurrence = occurrences.get(pending_name, 0)
            occurrences[pending_name] = occurrence + 1
            spans.append(
                FunctionSpan(
                    name=pending_name,
                    occurrence=occurrence,
                    start_line=pending_start,
                    body_line=body_start,
                    end_line=line_number,
                )
            )
            pending_name = None
            pending_start = 0
            body_start = 0
            depth = 0
    return spans


def parse_directives(lines: Sequence[str]) -> tuple[list[ExceptionDirective], list[Diagnostic]]:
    directives: list[ExceptionDirective] = []
    diagnostics: list[Diagnostic] = []
    for line_number, line in enumerate(lines, 1):
        if "tiger-style:" not in line:
            continue
        match = EXCEPTION_RE.search(line)
        if not match:
            diagnostics.append(
                Diagnostic("", line_number, "error", "invalid_exception", "malformed tiger-style exception")
            )
            continue
        kind = match.group("kind").strip()
        reason = match.group("reason").strip()
        if kind not in EXCEPTION_CLASSES:
            diagnostics.append(
                Diagnostic("", line_number, "error", "invalid_exception", f"unknown exception class: {kind}")
            )
            continue
        if len(reason) < 12 or reason.lower() in {"todo", "needed", "because", "temporary"}:
            diagnostics.append(
                Diagnostic("", line_number, "error", "invalid_exception", "exception reason is not concrete")
            )
            continue
        directives.append(ExceptionDirective(line_number, kind, reason))
    return directives, diagnostics


def has_exception(
    directives: Sequence[ExceptionDirective],
    line: int,
    kind: str,
    *,
    window: int = 2,
) -> bool:
    return any(
        directive.kind == kind and directive.line <= line <= directive.line + window
        for directive in directives
    )


def line_has_only_url_comment(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("//") and ("https://" in stripped or "http://" in stripped)


def add_diagnostic(
    diagnostics: list[Diagnostic],
    diagnostic: Diagnostic,
) -> None:
    if len(diagnostics) >= MAX_DIAGNOSTICS:
        return
    diagnostics.append(diagnostic)


def audit_lines(
    path: str,
    lines: Sequence[str],
    changed_lines: frozenset[int],
    directives: Sequence[ExceptionDirective],
    diagnostics: list[Diagnostic],
) -> None:
    for line_number in sorted(changed_lines):
        if line_number < 1 or line_number > len(lines):
            continue
        line = lines[line_number - 1]
        code = mask_code_line(line)
        if "\t" in line:
            add_diagnostic(diagnostics, Diagnostic(path, line_number, "error", "tab", "tab character is not permitted"))
        if line.rstrip(" \t") != line:
            add_diagnostic(
                diagnostics,
                Diagnostic(path, line_number, "error", "trailing_whitespace", "trailing whitespace"),
            )
        if any(ord(char) < 0x20 and char != "\t" for char in line):
            add_diagnostic(
                diagnostics,
                Diagnostic(path, line_number, "error", "control_character", "control character in source"),
            )
        if len(line) > LINE_LIMIT and not line_has_only_url_comment(line):
            add_diagnostic(
                diagnostics,
                Diagnostic(
                    path,
                    line_number,
                    "error",
                    "line_too_long",
                    f"line has {len(line)} code points; limit is {LINE_LIMIT}",
                ),
            )
        if re.search(r"\b(?:TODO|FIXME)\b", line):
            add_diagnostic(
                diagnostics,
                Diagnostic(path, line_number, "error", "merge_reminder", "TODO/FIXME must be resolved before closure"),
            )
        if "dbg(" in code and not re.search(r"\bfn\s+dbg\s*\(", code):
            add_diagnostic(
                diagnostics,
                Diagnostic(path, line_number, "error", "debug_call", "dbg() call must be removed before closure"),
            )
        if re.search(r"\bcatch\s+unreachable\b", code) and not has_exception(
            directives, line_number, "catch-unreachable"
        ):
            add_diagnostic(
                diagnostics,
                Diagnostic(
                    path,
                    line_number,
                    "error",
                    "catch_unreachable",
                    "catch unreachable requires a proof-bearing adjacent exception",
                ),
            )
        if re.search(r"\bwhile\s*\(\s*true\s*\)", code) and not has_exception(
            directives, line_number, "loop"
        ):
            add_diagnostic(
                diagnostics,
                Diagnostic(
                    path,
                    line_number,
                    "error",
                    "unbounded_loop",
                    "while (true) requires an adjacent bounded-loop rationale",
                ),
            )
        if re.search(r"\bcatch\s*\{\s*\}", code) and not has_exception(
            directives, line_number, "best-effort"
        ):
            add_diagnostic(
                diagnostics,
                Diagnostic(
                    path,
                    line_number,
                    "warning",
                    "empty_catch",
                    "empty catch needs a best-effort rationale and non-authoritative boundary",
                ),
            )
        if IMPLICIT_OPTIONS_RE.search(code) and not has_exception(
            directives, line_number, "implicit-options"
        ):
            add_diagnostic(
                diagnostics,
                Diagnostic(
                    path,
                    line_number,
                    "warning",
                    "implicit_options",
                    "safety-relevant call relies on empty default options",
                ),
            )
        if COMPOUND_ASSERT_RE.search(code):
            add_diagnostic(
                diagnostics,
                Diagnostic(
                    path,
                    line_number,
                    "warning",
                    "compound_assertion",
                    "split independent invariants into separate assertions",
                ),
            )
        if re.search(r"\bwhile\s*\(", code) and not re.search(
            r"\bwhile\s*\(\s*true\s*\)", code
        ):
            obvious_bound = re.search(
                r"(?:<|>|len|count|remaining|deadline|timeout|limit|max|budget)",
                code,
                re.IGNORECASE,
            )
            if not obvious_bound and not has_exception(directives, line_number, "loop"):
                add_diagnostic(
                    diagnostics,
                    Diagnostic(
                        path,
                        line_number,
                        "warning",
                        "loop_bound_not_obvious",
                        "while-loop bound or progress measure is not obvious at the control site",
                    ),
                )


def function_body_code(lines: Sequence[str], span: FunctionSpan) -> str:
    selected = [mask_code_line(line) for line in lines[span.start_line - 1 : span.end_line]]
    if not selected:
        return ""
    opening = selected[span.body_line - span.start_line].find("{")
    if opening >= 0:
        selected[span.body_line - span.start_line] = selected[span.body_line - span.start_line][opening + 1 :]
    return "\n".join(selected)


def audit_functions(
    path: str,
    lines: Sequence[str],
    changed_lines: frozenset[int],
    base_text: str | None,
    directives: Sequence[ExceptionDirective],
    diagnostics: list[Diagnostic],
) -> int:
    spans = find_function_spans("\n".join(lines))
    base_spans = {
        span.key: span
        for span in find_function_spans(base_text)
    } if base_text is not None else {}

    for span in spans:
        changed = any(span.start_line <= line <= span.end_line for line in changed_lines)
        if not changed:
            continue
        base_span = base_spans.get(span.key)
        exception = has_exception(
            directives,
            span.start_line,
            "function-lines",
            window=3,
        )
        if span.length > FUNCTION_LIMIT:
            if exception:
                severity = "warning"
                code = "allowed_long_function"
                message = f"function is {span.length} lines under an explicit exception"
            elif base_span is None or base_span.length <= FUNCTION_LIMIT:
                severity = "error"
                code = "function_too_long"
                message = f"function is {span.length} lines; limit is {FUNCTION_LIMIT}"
            elif span.length > base_span.length:
                severity = "error"
                code = "function_grew_over_limit"
                message = (
                    f"legacy function grew from {base_span.length} to {span.length} lines "
                    f"above the {FUNCTION_LIMIT}-line limit"
                )
            else:
                severity = "warning"
                code = "legacy_long_function"
                message = f"legacy function remains {span.length} lines; do not grow it"
            add_diagnostic(
                diagnostics,
                Diagnostic(path, span.start_line, severity, code, message),
            )

        body = function_body_code(lines, span)
        if not span.name.startswith("test@"):
            recursive_call = re.search(
                rf"(?<![A-Za-z0-9_.]){re.escape(span.name)}\s*\(",
                body,
            )
            if recursive_call and not has_exception(
                directives,
                span.start_line,
                "recursion",
                window=3,
            ):
                add_diagnostic(
                    diagnostics,
                    Diagnostic(
                        path,
                        span.start_line,
                        "error",
                        "direct_recursion",
                        f"direct recursion in {span.name} requires an explicit bounded-stack design",
                    ),
                )

        if BOUNDARY_NAME_RE.search(span.name):
            assert_count = len(ASSERT_RE.findall(body))
            if assert_count < 2 and not has_exception(
                directives,
                span.start_line,
                "assertions",
                window=3,
            ):
                add_diagnostic(
                    diagnostics,
                    Diagnostic(
                        path,
                        span.start_line,
                        "warning",
                        "paired_assertions_missing",
                        f"boundary function {span.name} has {assert_count} visible assertions; seek an independent pair",
                    ),
                )
    return len(spans)


def audit_snapshots(
    snapshots: Sequence[FileSnapshot],
    *,
    mode: str,
    base: str | None,
    head: str | None,
) -> dict[str, Any]:
    diagnostics: list[Diagnostic] = []
    function_count = 0
    if len(snapshots) > MAX_FILES:
        raise AuditFailure(f"file count exceeds the {MAX_FILES} file limit")

    for snapshot in snapshots:
        lines = snapshot.text.splitlines()
        directives, directive_diagnostics = parse_directives(lines)
        for item in directive_diagnostics:
            add_diagnostic(
                diagnostics,
                Diagnostic(snapshot.path, item.line, item.severity, item.code, item.message),
            )
        audit_lines(
            snapshot.path,
            lines,
            snapshot.changed_lines,
            directives,
            diagnostics,
        )
        function_count += audit_functions(
            snapshot.path,
            lines,
            snapshot.changed_lines,
            snapshot.base_text,
            directives,
            diagnostics,
        )

    errors = sum(item.severity == "error" for item in diagnostics)
    warnings = sum(item.severity == "warning" for item in diagnostics)
    if len(diagnostics) >= MAX_DIAGNOSTICS:
        diagnostics.append(
            Diagnostic(
                "",
                0,
                "error",
                "diagnostic_limit",
                f"diagnostics exceeded the {MAX_DIAGNOSTICS} item limit",
            )
        )
        errors += 1

    return {
        "schema": REPORT_SCHEMA,
        "mode": mode,
        "base": base,
        "head": head,
        "limits": {
            "line_codepoints": LINE_LIMIT,
            "function_lines": FUNCTION_LIMIT,
            "files": MAX_FILES,
            "file_bytes": MAX_FILE_BYTES,
            "total_bytes": MAX_TOTAL_BYTES,
            "diagnostics": MAX_DIAGNOSTICS,
        },
        "summary": {
            "files": len(snapshots),
            "functions": function_count,
            "errors": errors,
            "warnings": warnings,
        },
        "diagnostics": [asdict(item) for item in diagnostics],
    }


def render_audit_text(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "zig_tiger_style_gate",
        f"mode: {report['mode']}",
        f"files: {summary['files']}",
        f"functions: {summary['functions']}",
        f"errors: {summary['errors']}",
        f"warnings: {summary['warnings']}",
    ]
    for item in report["diagnostics"]:
        location = item["path"]
        if item["line"]:
            location = f"{location}:{item['line']}"
        lines.append(
            f"{location}: {item['severity']}: {item['code']}: {item['message']}"
        )
    return "\n".join(lines) + "\n"


def validate_command(args: argparse.Namespace) -> int:
    try:
        contract = load_mapping(args.file, "zig_tiger_style")
        result = validate_zts(contract)
    except Exception as exc:
        result = {
            "zig_tiger_style_gate": {
                "schema": REPORT_SCHEMA,
                "verdict": "fail",
                "material": False,
                "errors": [str(exc)],
                "warnings": [],
            }
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["zig_tiger_style_gate"]["verdict"] == "pass" else 2


def audit_command(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    try:
        if args.all:
            snapshots = all_snapshots(root)
            mode = "all"
            base = None
            head = WORKTREE
        elif args.paths:
            snapshots = all_snapshots(root, args.paths)
            mode = "paths"
            base = None
            head = WORKTREE
        else:
            if not args.base:
                raise AuditFailure("audit requires --base, --all, or explicit paths")
            snapshots = changed_snapshots(root, args.base, args.head)
            mode = "diff"
            base = args.base
            head = args.head
        report = audit_snapshots(snapshots, mode=mode, base=base, head=head)
    except Exception as exc:
        report = {
            "schema": REPORT_SCHEMA,
            "mode": "failed",
            "base": args.base,
            "head": args.head,
            "summary": {"files": 0, "functions": 0, "errors": 1, "warnings": 0},
            "diagnostics": [
                asdict(Diagnostic("", 0, "error", "audit_failed", str(exc)))
            ],
        }
        payload = json.dumps(report, indent=2, sort_keys=True) + "\n" if args.format == "json" else render_audit_text(report)
        sys.stdout.write(payload)
        return 3

    payload = json.dumps(report, indent=2, sort_keys=True) + "\n" if args.format == "json" else render_audit_text(report)
    sys.stdout.write(payload)
    summary = report["summary"]
    if summary["errors"]:
        return 2
    if args.deny_warnings and summary["warnings"]:
        return 2
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate a ZTS-v1 contract")
    validate.add_argument("file", help="JSON/YAML contract path, or - for stdin")
    validate.set_defaults(handler=validate_command)

    audit = subparsers.add_parser("audit", help="Audit Zig source with the changed-code ratchet")
    audit.add_argument("paths", nargs="*", help="Explicit repository-relative Zig paths")
    audit.add_argument("--root", default=".")
    audit.add_argument("--base")
    audit.add_argument("--head", default=WORKTREE)
    audit.add_argument("--all", action="store_true")
    audit.add_argument("--format", choices=("text", "json"), default="text")
    audit.add_argument("--deny-warnings", action="store_true")
    audit.set_defaults(handler=audit_command)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "audit":
        selected_modes = int(bool(args.all)) + int(bool(args.paths)) + int(bool(args.base))
        if selected_modes != 1:
            parser.error("audit requires exactly one of --all, --base, or explicit paths")
        if args.all and args.head != WORKTREE:
            parser.error("--head is only valid with --base")
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
