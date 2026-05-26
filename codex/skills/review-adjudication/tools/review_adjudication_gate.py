#!/usr/bin/env python3
"""Mechanical contract checker for review-adjudication outputs.

This checker is intentionally conservative. It validates the shape of a gated
adjudication before downstream automation routes implementation. It does not
prove semantic correctness.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

ALLOWED_RELEVANCE = {
    "material-relevant",
    "relevant-nonmaterial",
    "partially-relevant",
    "stale-or-superseded",
    "unsupported",
    "out-of-scope",
    "preference-only",
}
ALLOWED_DISPOSITION = {"act", "rebut", "defer", "need-evidence"}
ALLOWED_NO_CHANGE = {"defeated", "not-defeated", "unresolved"}
ALLOWED_CONCERN = {"valid", "partial", "unsupported", "unknown"}
ALLOWED_PROPOSED = {
    "valid",
    "partially-valid",
    "wrong-fix",
    "overbroad",
    "under-specified",
    "not-applicable",
    "validation-only",
}
ALLOWED_RESOLVE_DECISION = {
    "address",
    "validate-only",
    "resolve-thread-only",
    "do-not-address",
    "blocked",
}
IMPLEMENTATION_HANDOFFS = {
    "route-to-accretive-implementer",
    "route-to-fixed-point-driver",
}
REQUIRED_LEDGER_FIELDS = [
    "id",
    "reviewer",
    "location",
    "claim",
    "concern",
    "proposed",
    "relevance",
    "disposition",
    "nochange",
    "invariant",
    "evidence",
    "handoff",
]
REQUIRED_GATE_FIELDS = [
    "identitycoverage",
    "nochangecoverage",
    "dispositioncoverage",
    "proposedfixseparation",
    "evidencecoverage",
    "invariantpass",
    "acceptanceskewaudit",
    "handoffallowed",
]
REQUIRED_SECTIONS = [
    "Comment Ledger",
    "Acceptance Skew Audit",
    "Resolve Selection",
    "Adjudication Gate",
    "Handoff Agenda",
    "Adjudication Bottom Line",
]
ALL_ACTION_TERMS = [
    "stale",
    "unsupported",
    "preference",
    "out-of-scope",
    "misdiagnosis",
    "proposed-fix",
    "validation-only",
    "invariant",
]
EMPTY_MARKERS = {"", "-", "—", "n/a", "na", "unknown", "missing", "none"}


def norm_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.strip().lower())


def norm_value(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[`*_]", "", value)
    value = re.sub(r"\s+", "-", value)
    return value


COLUMN_ALIASES = {
    "idthread": "id",
    "id": "id",
    "commentid": "id",
    "threadid": "id",
    "reviewcommentid": "id",
    "reviewer": "reviewer",
    "author": "reviewer",
    "location": "location",
    "fileorthread": "location",
    "file": "location",
    "thread": "location",
    "pathline": "location",
    "claim": "claim",
    "summary": "claim",
    "reviewclaim": "claim",
    "concernvalidity": "concern",
    "concern": "concern",
    "proposedfixvalidity": "proposed",
    "proposedfix": "proposed",
    "fixvalidity": "proposed",
    "relevance": "relevance",
    "relevanceclass": "relevance",
    "disposition": "disposition",
    "nochangestatus": "nochange",
    "nochangecountercasestatus": "nochange",
    "countercasestatus": "nochange",
    "invariant": "invariant",
    "governinginvariant": "invariant",
    "evidence": "evidence",
    "evidencebasis": "evidence",
    "handoff": "handoff",
    "handoffaction": "handoff",
}

GATE_ALIASES = {
    "identitycoverage": "identitycoverage",
    "nochangecoverage": "nochangecoverage",
    "nochangecoverage": "nochangecoverage",
    "dispositioncoverage": "dispositioncoverage",
    "proposedfixseparation": "proposedfixseparation",
    "fixseparation": "proposedfixseparation",
    "evidencecoverage": "evidencecoverage",
    "invariantpass": "invariantpass",
    "acceptanceskewaudit": "acceptanceskewaudit",
    "handoffallowed": "handoffallowed",
}

RESOLVE_SELECTION_ALIASES = {
    "idthread": "id",
    "id": "id",
    "commentid": "id",
    "threadid": "id",
    "resolvedecision": "decision",
    "decision": "decision",
    "selection": "decision",
    "resolve": "decision",
    "reason": "reason",
    "basis": "reason",
    "next": "next",
    "nextaction": "next",
    "handoff": "next",
}


@dataclass
class CheckResult:
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)
    gate: Dict[str, str] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(
            {
                "passed": self.passed,
                "errors": self.errors,
                "warnings": self.warnings,
                "stats": self.stats,
                "gate": self.gate,
            },
            indent=2,
            sort_keys=True,
        )


def has_section(text: str, title: str) -> bool:
    pattern = rf"(?im)^\s*#+\s+{re.escape(title)}\s*$"
    return re.search(pattern, text) is not None


def section_text(text: str, title: str) -> str:
    pattern = rf"(?im)^\s*#+\s+{re.escape(title)}\s*$"
    match = re.search(pattern, text)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"(?m)^\s*#+\s+", text[start:])
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def split_md_row(line: str) -> List[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    # Simple markdown splitting. Escaped pipes are uncommon in these ledgers; keep
    # the checker dependency-free and conservative.
    return [cell.strip() for cell in line.split("|")]


def is_separator_row(cells: Sequence[str]) -> bool:
    return all(re.fullmatch(r":?-{3,}:?", cell.strip()) is not None for cell in cells)


def extract_first_table(block: str) -> Tuple[List[str], List[Dict[str, str]]]:
    lines = [line.rstrip() for line in block.splitlines()]
    table_lines: List[str] = []
    started = False
    for line in lines:
        if line.strip().startswith("|"):
            table_lines.append(line)
            started = True
        elif started and line.strip() == "":
            break
        elif started:
            break
    if len(table_lines) < 2:
        return [], []
    raw_headers = split_md_row(table_lines[0])
    sep = split_md_row(table_lines[1])
    if not is_separator_row(sep):
        return [], []
    rows: List[Dict[str, str]] = []
    for line in table_lines[2:]:
        cells = split_md_row(line)
        if len(cells) < len(raw_headers):
            cells = list(cells) + [""] * (len(raw_headers) - len(cells))
        row = {raw_headers[i]: cells[i] for i in range(len(raw_headers))}
        rows.append(row)
    return raw_headers, rows


def normalize_ledger_rows(headers: Sequence[str], rows: Sequence[Dict[str, str]]) -> Tuple[Dict[str, str], List[Dict[str, str]]]:
    header_map: Dict[str, str] = {}
    for header in headers:
        key = norm_key(header)
        canonical = COLUMN_ALIASES.get(key)
        if canonical:
            header_map[canonical] = header
    normalized: List[Dict[str, str]] = []
    for row in rows:
        item: Dict[str, str] = {}
        for canonical, original in header_map.items():
            item[canonical] = row.get(original, "").strip()
        normalized.append(item)
    return header_map, normalized


def normalize_gate(headers: Sequence[str], rows: Sequence[Dict[str, str]]) -> Dict[str, str]:
    if not headers:
        return {}
    header_keys = [norm_key(header) for header in headers]
    field_header: Optional[str] = None
    value_header: Optional[str] = None
    for header, key in zip(headers, header_keys):
        if key in {"field", "gatefield", "check"}:
            field_header = header
        if key in {"value", "status", "result"}:
            value_header = header
    if field_header is None or value_header is None:
        # Fallback to first two columns.
        if len(headers) >= 2:
            field_header = headers[0]
            value_header = headers[1]
        else:
            return {}
    gate: Dict[str, str] = {}
    for row in rows:
        raw_field = row.get(field_header, "")
        raw_value = row.get(value_header, "")
        field = GATE_ALIASES.get(norm_key(raw_field))
        if field:
            gate[field] = norm_value(raw_value)
    return gate


def normalize_resolve_selection(
    headers: Sequence[str], rows: Sequence[Dict[str, str]]
) -> Tuple[Dict[str, str], List[Dict[str, str]]]:
    header_map: Dict[str, str] = {}
    for header in headers:
        canonical = RESOLVE_SELECTION_ALIASES.get(norm_key(header))
        if canonical:
            header_map[canonical] = header
    normalized: List[Dict[str, str]] = []
    for row in rows:
        item: Dict[str, str] = {}
        for canonical, original in header_map.items():
            item[canonical] = row.get(original, "").strip()
        normalized.append(item)
    return header_map, normalized


def is_empty(value: str) -> bool:
    return norm_value(value) in EMPTY_MARKERS


def check_adjudication(text: str) -> CheckResult:
    errors: List[str] = []
    warnings: List[str] = []

    for section in REQUIRED_SECTIONS:
        if not has_section(text, section):
            errors.append(f"missing required section: {section}")

    ledger_headers, raw_rows = extract_first_table(section_text(text, "Comment Ledger"))
    header_map, rows = normalize_ledger_rows(ledger_headers, raw_rows)

    missing_columns = [field for field in REQUIRED_LEDGER_FIELDS if field not in header_map]
    if missing_columns:
        errors.append("Comment Ledger missing required columns: " + ", ".join(missing_columns))
    if not rows:
        errors.append("Comment Ledger has no data rows")

    act_count = 0
    non_action_count = 0
    dispositions_by_id: Dict[str, str] = {}
    nochange_by_id: Dict[str, str] = {}
    for idx, row in enumerate(rows, start=1):
        label = row.get("id", f"row {idx}") or f"row {idx}"
        for field_name in ["id", "reviewer", "location", "claim"]:
            if is_empty(row.get(field_name, "")):
                errors.append(f"{label}: missing raw identity field `{field_name}`")
        relevance = norm_value(row.get("relevance", ""))
        disposition = norm_value(row.get("disposition", ""))
        nochange = norm_value(row.get("nochange", ""))
        concern = norm_value(row.get("concern", ""))
        proposed = norm_value(row.get("proposed", ""))
        evidence = row.get("evidence", "")
        handoff = norm_value(row.get("handoff", ""))
        if not is_empty(label):
            dispositions_by_id[label] = disposition
            nochange_by_id[label] = nochange

        if relevance not in ALLOWED_RELEVANCE:
            errors.append(f"{label}: invalid relevance `{row.get('relevance', '')}`")
        if disposition not in ALLOWED_DISPOSITION:
            errors.append(f"{label}: invalid disposition `{row.get('disposition', '')}`")
        if nochange not in ALLOWED_NO_CHANGE:
            errors.append(f"{label}: invalid no-change status `{row.get('nochange', '')}`")
        if concern not in ALLOWED_CONCERN:
            errors.append(f"{label}: invalid concern validity `{row.get('concern', '')}`")
        if proposed not in ALLOWED_PROPOSED:
            errors.append(f"{label}: invalid proposed-fix validity `{row.get('proposed', '')}`")

        if disposition == "act":
            act_count += 1
            if nochange != "defeated":
                errors.append(f"{label}: `act` requires no-change status `defeated`")
            if concern not in {"valid", "partial"}:
                errors.append(f"{label}: `act` requires concern validity `valid` or `partial`")
            if relevance in {"stale-or-superseded", "unsupported", "out-of-scope", "preference-only"}:
                errors.append(f"{label}: `act` conflicts with relevance `{relevance}`")
            if is_empty(evidence):
                errors.append(f"{label}: `act` requires non-empty artifact evidence")
            if proposed in {"wrong-fix", "overbroad", "under-specified", "not-applicable", "validation-only"}:
                if handoff not in IMPLEMENTATION_HANDOFFS and handoff != "none":
                    warnings.append(
                        f"{label}: proposed fix is `{proposed}`; verify handoff `{handoff}` replaces rather than implements reviewer fix"
                    )
                if handoff == "none":
                    errors.append(f"{label}: invalid proposed fix requires an explicit replacement or validation handoff")
        elif disposition in ALLOWED_DISPOSITION:
            non_action_count += 1

    resolve_headers, resolve_rows_raw = extract_first_table(section_text(text, "Resolve Selection"))
    resolve_header_map, resolve_rows = normalize_resolve_selection(resolve_headers, resolve_rows_raw)
    for field in ["id", "decision", "reason", "next"]:
        if field not in resolve_header_map:
            errors.append(f"Resolve Selection missing required column: {field}")
    if not resolve_rows:
        errors.append("Resolve Selection has no data rows")
    ledger_ids = set(dispositions_by_id)
    selection_ids = {row.get("id", "") for row in resolve_rows if row.get("id", "")}
    missing_selection = sorted(ledger_ids - selection_ids)
    if missing_selection:
        errors.append("Resolve Selection missing comment ids: " + ", ".join(missing_selection))
    extra_selection = sorted(selection_ids - ledger_ids)
    if extra_selection:
        errors.append("Resolve Selection contains unknown comment ids: " + ", ".join(extra_selection))
    for idx, row in enumerate(resolve_rows, start=1):
        label = row.get("id", f"selection row {idx}") or f"selection row {idx}"
        decision = norm_value(row.get("decision", ""))
        reason = row.get("reason", "")
        next_action = row.get("next", "")
        if decision not in ALLOWED_RESOLVE_DECISION:
            errors.append(f"{label}: invalid resolve decision `{row.get('decision', '')}`")
        if is_empty(reason):
            errors.append(f"{label}: resolve selection requires non-empty reason")
        empty_next_allowed = decision == "do-not-address" and norm_value(next_action) == "none"
        if is_empty(next_action) and not empty_next_allowed:
            errors.append(f"{label}: resolve selection requires non-empty next action")
        disposition = dispositions_by_id.get(label)
        nochange = nochange_by_id.get(label)
        if decision == "address":
            if disposition != "act":
                errors.append(f"{label}: resolve decision `address` requires disposition `act`")
            if nochange != "defeated":
                errors.append(f"{label}: resolve decision `address` requires defeated no-change case")
        if decision == "validate-only" and disposition != "need-evidence":
            errors.append(f"{label}: resolve decision `validate-only` requires disposition `need-evidence`")
        if decision in {"resolve-thread-only", "do-not-address"} and disposition == "act":
            errors.append(f"{label}: resolve decision `{decision}` conflicts with disposition `act`")

    gate_headers, gate_rows_raw = extract_first_table(section_text(text, "Adjudication Gate"))
    gate = normalize_gate(gate_headers, gate_rows_raw)
    missing_gate = [field for field in REQUIRED_GATE_FIELDS if field not in gate]
    if missing_gate:
        errors.append("Adjudication Gate missing required fields: " + ", ".join(missing_gate))

    for field_name in REQUIRED_GATE_FIELDS:
        if field_name not in gate:
            continue
        value = gate[field_name]
        if field_name == "handoffallowed":
            if value not in {"yes", "no"}:
                errors.append(f"handoff_allowed must be yes/no, got `{value}`")
        elif value not in {"pass", "fail"}:
            errors.append(f"{field_name} must be pass/fail, got `{value}`")

    gate_failures = [field for field in REQUIRED_GATE_FIELDS if field != "handoffallowed" and gate.get(field) == "fail"]
    if gate_failures and gate.get("handoffallowed") == "yes":
        errors.append("handoff_allowed is yes despite failed gate fields: " + ", ".join(gate_failures))
    if errors and gate.get("handoffallowed") == "yes":
        errors.append("handoff_allowed is yes despite mechanical contract errors")

    if rows and act_count == len(rows):
        if not has_section(text, "All-Action Justification"):
            errors.append("all substantive comments are `act`; missing All-Action Justification")
        else:
            all_action = section_text(text, "All-Action Justification").lower()
            missing_terms = [term for term in ALL_ACTION_TERMS if term not in all_action]
            if missing_terms:
                errors.append("All-Action Justification missing checks: " + ", ".join(missing_terms))

    skew_text = section_text(text, "Acceptance Skew Audit")
    if not skew_text.strip():
        errors.append("Acceptance Skew Audit is empty")

    bottom_line = section_text(text, "Adjudication Bottom Line")
    if gate_failures and "blocked" not in bottom_line.lower():
        errors.append("failed gate requires blocked Adjudication Bottom Line")

    stats = {
        "comments": len(rows),
        "act": act_count,
        "non_action": non_action_count,
        "errors": len(errors),
        "warnings": len(warnings),
    }
    return CheckResult(passed=not errors, errors=errors, warnings=warnings, stats=stats, gate=gate)


def print_human(result: CheckResult) -> None:
    if result.passed:
        print("PASS: adjudication gate contract satisfied")
    else:
        print("FAIL: adjudication gate contract incomplete")
    print("stats:", ", ".join(f"{key}={value}" for key, value in result.stats.items()))
    if result.gate:
        print("gate:", ", ".join(f"{key}={value}" for key, value in result.gate.items()))
    if result.errors:
        print("errors:")
        for error in result.errors:
            print(f"- {error}")
    if result.warnings:
        print("warnings:")
        for warning in result.warnings:
            print(f"- {warning}")


def run_self_test() -> int:
    valid = """
## Comment Ledger
| id/thread | reviewer | location | claim | concern validity | proposed fix validity | relevance | disposition | no-change status | invariant | evidence | handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|
| c1 | alice | src/a.py:10 | retry is not idempotent | valid | valid | material-relevant | act | defeated | retry idempotence | src/a.py shows duplicate write | route-to-accretive-implementer |
| c2 | bob | src/a.py:12 | rename helper | unsupported | not-applicable | preference-only | rebut | not-defeated | none | no repo convention supplied | none |

## Acceptance Skew Audit
Mixed dispositions; no all-action pressure.

## Resolve Selection
| id/thread | resolve decision | reason | next |
|---|---|---|---|
| c1 | address | act row has defeated no-change case | route-to-accretive-implementer |
| c2 | do-not-address | preference-only no-change case preserved | none |

## Adjudication Gate
| field | value | basis |
|---|---|---|
| identity_coverage | pass | all rows have identity |
| no_change_coverage | pass | all rows have status |
| disposition_coverage | pass | all rows have disposition |
| proposed_fix_separation | pass | concern and fix split |
| evidence_coverage | pass | action has code evidence |
| invariant_pass | pass | invariant checked |
| acceptance_skew_audit | pass | skew audited |
| handoff_allowed | yes | all pass |

## Handoff Agenda
Route c1 only.

## Adjudication Bottom Line
Proceed: one action, one rebuttal.
"""
    invalid = """
## Comment Ledger
| id/thread | reviewer | location | claim | concern validity | proposed fix validity | relevance | disposition | no-change status | invariant | evidence | handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|
| c1 | alice | src/a.py:10 | retry is not idempotent | unknown | valid | material-relevant | act | unresolved | none |  | route-to-accretive-implementer |

## Acceptance Skew Audit

## Resolve Selection
| id/thread | resolve decision | reason | next |
|---|---|---|---|
| c1 | address |  | route-to-accretive-implementer |

## Adjudication Gate
| field | value | basis |
|---|---|---|
| identity_coverage | pass | all rows have identity |
| no_change_coverage | fail | unresolved |
| disposition_coverage | pass | all rows have disposition |
| proposed_fix_separation | pass | concern and fix split |
| evidence_coverage | fail | missing |
| invariant_pass | pass | invariant checked |
| acceptance_skew_audit | fail | missing |
| handoff_allowed | yes | wrong |

## Handoff Agenda
Route c1.

## Adjudication Bottom Line
Proceed.
"""
    good = check_adjudication(valid)
    bad = check_adjudication(invalid)
    if good.passed and not bad.passed:
        print("self-test passed")
        return 0
    print("self-test failed")
    print("valid result:", good.to_json())
    print("invalid result:", bad.to_json())
    return 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", help="Markdown adjudication output to check")
    parser.add_argument("--json", action="store_true", help="emit JSON result")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()
    if not args.path:
        parser.error("path is required unless --self-test is used")
    path = Path(args.path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error reading {path}: {exc}", file=sys.stderr)
        return 2
    result = check_adjudication(text)
    if args.json:
        print(result.to_json())
    else:
        print_human(result)
    return 0 if result.passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
