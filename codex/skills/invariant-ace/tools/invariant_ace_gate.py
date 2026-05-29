#!/usr/bin/env python3
"""Mechanical contract checker for Authority-Gated v1 invariant-ace outputs.

The checker validates invariant candidate inventory, owner/scope, induction,
enforcement-boundary decisions, authority packet coverage, veto handling,
verification coverage, and change-agenda consistency. It cannot prove semantic
correctness, but it blocks incomplete or permissive invariant outputs before
implementation handoff.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

ALLOWED_STATUS = {"accepted", "candidate", "downgraded", "rejected", "unresolved", "blocked"}
ALLOWED_ROUTE = {"enforce-now", "validate-only", "proof-only", "defer", "no-change", "blocked"}
CLEARANCE_VALUES = {"clear", "veto", "unresolved", "not-needed", "not-in-scope"}
SKEPTIC_VALUES = {"defeated", "veto", "unresolved", "not-needed"}
AUTHORITY_STATUS = {"cleared-for-enforcement", "cleared-for-validation", "proof-only", "defer", "no-change", "blocked"}
PACKET_STATUS = {"accepted", "rejected", "root-equivalent"}
REQUIRED_ROLES = {
    "counterexample-authority",
    "owner-scope-authority",
    "induction-authority",
    "boundary-authority",
    "witness-parity-authority",
    "verification-authority",
    "skeptic-authority",
}
REQUIRED_SECTIONS = [
    "Review Basis",
    "Candidate Invariant Inventory",
    "Counterexample Ledger",
    "Invariant Ledger",
    "Owner and Scope Ledger",
    "Transition / Induction Matrix",
    "Enforcement Boundary Decision",
    "Policy / Exception Ledger",
    "Witness and Fixture Parity Ledger",
    "Verification Plan",
    "Authority Packet Receipts",
    "Authority Clearance Matrix",
    "Authority Veto Ledger",
    "Accepted Invariants",
    "Validate Only",
    "Proof Only",
    "Defer / No Change",
    "Change Agenda",
    "Acceptance Skew Audit",
    "Invariant Gate",
    "Ace Bottom Line",
]
OPTIONAL_SINGLETON_SECTIONS = {"All-Invariant Accepted Justification"}
REQUIRED_GATE_FIELDS = [
    "artifactstatecoverage",
    "candidateinventorycoverage",
    "counterexamplecoverage",
    "ownerscopecoverage",
    "inductioncoverage",
    "boundarydecisioncoverage",
    "policyexceptioncoverage",
    "witnessfixtureparitycoverage",
    "verificationcoverage",
    "authoritypacketcoverage",
    "authorityclearancecoverage",
    "authorityvetocoverage",
    "changeagendaconsistency",
    "acceptanceskewaudit",
    "invariantgatecomplete",
    "implementationhandoffallowed",
    "validationhandoffallowed",
    "proofonlyhandoffallowed",
]
ALL_ACCEPTED_CHECKS = {
    "wrongowneralternative": "wrong-owner alternative",
    "wrongscopealternative": "wrong-scope alternative",
    "notinductivealternative": "not-inductive alternative",
    "validationonlyalternative": "validation-only alternative",
    "proofonlyalternative": "proof-only alternative",
    "duplicateboundaryalternative": "duplicate-boundary alternative",
    "fixturepreconditionalignment": "fixture precondition alignment",
}
EMPTY_MARKERS = {"", "-", "—", "n/a", "na", "unknown", "missing", "none", "[]"}
GENERIC_EVIDENCE = {"code", "tests", "review", "looks-right", "artifact", "current-artifacts", "todo"}

LEDGER_ALIASES = {
    "id": "id", "invariantid": "id", "candidateid": "id",
    "predicate": "predicate", "owner": "owner", "stateowner": "owner",
    "scope": "scope", "holdswhen": "holdswhen", "sourceoftruth": "sourceoftruth",
    "acceptancestatus": "status", "status": "status",
    "enforcementboundary": "boundary", "boundary": "boundary",
    "verificationsignal": "verification", "verification": "verification",
    "evidenceref": "evidenceref", "evidence": "evidenceref",
    "route": "route", "handoff": "route",
}
AUTHORITY_ALIASES = {
    "id": "id", "invariantid": "id", "candidateid": "id",
    "counterexample": "counterexample",
    "ownerscope": "ownerscope", "ownerandscope": "ownerscope",
    "induction": "induction",
    "boundary": "boundary",
    "witnessparity": "witnessparity", "witnessfixtureparity": "witnessparity",
    "verification": "verification",
    "skeptic": "skeptic", "nochange": "skeptic",
    "authoritystatus": "status", "status": "status",
    "packetrefs": "packetrefs", "packets": "packetrefs",
}
RECEIPT_ALIASES = {
    "role": "role",
    "packetstatus": "status", "status": "status",
    "artifactstatematch": "artifactmatch",
    "scopematch": "scopematch",
    "candidatescovered": "covered", "idscovered": "covered",
    "clearancesadded": "clearances",
    "vetoesadded": "vetoes",
    "usedfor": "usedfor",
    "reason": "reason",
}
AGENDA_ALIASES = {
    "id": "id", "invariantid": "id", "candidateid": "id",
    "route": "route",
    "change": "change",
    "prooforvalidationrequired": "proof", "proof": "proof", "validation": "proof",
    "next": "next", "nextaction": "next",
    "owner": "owner",
}
VETO_ALIASES = {
    "id": "id", "invariantid": "id", "candidateid": "id",
    "vetosource": "source", "source": "source",
    "vetoclass": "class", "class": "class",
    "vetoclaim": "claim", "claim": "claim",
    "evidenceref": "evidenceref", "evidence": "evidenceref",
    "requiredtoclear": "required", "clearance": "required",
    "finalroute": "route", "route": "route",
}
GATE_ALIASES = {
    "artifactstatecoverage": "artifactstatecoverage",
    "candidateinventorycoverage": "candidateinventorycoverage",
    "counterexamplecoverage": "counterexamplecoverage",
    "ownerscopecoverage": "ownerscopecoverage",
    "inductioncoverage": "inductioncoverage",
    "boundarydecisioncoverage": "boundarydecisioncoverage",
    "policyexceptioncoverage": "policyexceptioncoverage",
    "witnessfixtureparitycoverage": "witnessfixtureparitycoverage",
    "verificationcoverage": "verificationcoverage",
    "authoritypacketcoverage": "authoritypacketcoverage",
    "authorityclearancecoverage": "authorityclearancecoverage",
    "authorityvetocoverage": "authorityvetocoverage",
    "changeagendaconsistency": "changeagendaconsistency",
    "acceptanceskewaudit": "acceptanceskewaudit",
    "invariantgatecomplete": "invariantgatecomplete",
    "implementationhandoffallowed": "implementationhandoffallowed",
    "validationhandoffallowed": "validationhandoffallowed",
    "proofonlyhandoffallowed": "proofonlyhandoffallowed",
}
INVENTORY_ALIASES = {
    "candidatecount": "candidatecount",
    "acceptedcount": "acceptedcount",
    "validateonlycount": "validationcount",
    "proofonlycount": "proofonlycount",
    "deferornochangecount": "defernochange_count",
    "blockedcount": "blockedcount",
    "candidateids": "candidateids",
    "acceptedids": "acceptedids",
    "validateonlyids": "validationids",
    "proofonlyids": "proofonlyids",
    "deferornochangeids": "defernochangeids",
    "blockedids": "blockedids",
    "missingcandidateids": "missingids",
    "duplicatecandidateids": "duplicateids",
}

@dataclass
class CheckResult:
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stats: Dict[str, int] = field(default_factory=dict)
    gate: Dict[str, str] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({"passed": self.passed, "errors": self.errors, "warnings": self.warnings, "stats": self.stats, "gate": self.gate}, indent=2, sort_keys=True)


def norm_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.strip().lower())


def norm_value(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[`*_]", "", value)
    value = re.sub(r"\s+", "-", value)
    return value


def section_count(text: str, title: str) -> int:
    return len(re.findall(rf"(?im)^\s*#+\s+{re.escape(title)}\s*$", text))


def has_section(text: str, title: str) -> bool:
    return section_count(text, title) > 0


def section_text(text: str, title: str) -> str:
    m = re.search(rf"(?im)^\s*#+\s+{re.escape(title)}\s*$", text)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"(?m)^\s*#+\s+", text[start:])
    end = start + nxt.start() if nxt else len(text)
    return text[start:end].strip()


def split_md_row(line: str) -> List[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def is_separator_row(cells: Sequence[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c.strip()) is not None for c in cells)


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
    headers = split_md_row(table_lines[0])
    if not is_separator_row(split_md_row(table_lines[1])):
        return [], []
    rows = []
    for line in table_lines[2:]:
        cells = split_md_row(line)
        if len(cells) < len(headers):
            cells += [""] * (len(headers) - len(cells))
        rows.append({headers[i]: cells[i] for i in range(len(headers))})
    return headers, rows


def normalize_rows(headers: Sequence[str], rows: Sequence[Dict[str, str]], aliases: Dict[str, str]) -> Tuple[Dict[str, str], List[Dict[str, str]]]:
    header_map: Dict[str, str] = {}
    for h in headers:
        c = aliases.get(norm_key(h))
        if c:
            header_map[c] = h
    out = []
    for row in rows:
        out.append({c: row.get(orig, "").strip() for c, orig in header_map.items()})
    return header_map, out


def is_empty(value: str) -> bool:
    return norm_value(value) in EMPTY_MARKERS


def parse_id_list(value: str) -> List[str]:
    value = value.strip()
    if is_empty(value):
        return []
    if re.search(r"(?i)\ball\b", value):
        return ["__ALL__"]
    value = re.sub(r"^[\[({]", "", value)
    value = re.sub(r"[\])}]$", "", value)
    return [part.strip().strip('"\'`') for part in re.split(r"[,;\s]+", value) if part.strip().strip('"\'`')]


def parse_int(value: str) -> Optional[int]:
    m = re.search(r"-?\d+", value or "")
    return int(m.group(0)) if m else None


def parse_inventory(block: str) -> Dict[str, str]:
    inv: Dict[str, str] = {}
    for line in block.splitlines():
        s = re.sub(r"^[-*]\s+", "", line.strip())
        if ":" not in s:
            continue
        k, v = s.split(":", 1)
        c = INVENTORY_ALIASES.get(norm_key(k))
        if c:
            inv[c] = v.strip()
    return inv


def evidence_ref_is_concrete(value: str, *, allow_missing: bool = False) -> bool:
    if allow_missing and norm_value(value) in {"missing", "blocked", "unknown"}:
        return True
    if is_empty(value):
        return False
    nv = norm_value(value)
    if nv in GENERIC_EVIDENCE:
        return False
    if re.search(r"[\w./-]+:\d+", value):
        return True
    if any(tok in nv for tok in ["test", "ci", "cmd", "command", "log", "thread", "pr#", "github", "diff", "src/", "tests/", "commit", "fixture", "proof"]):
        return True
    if "/" in value or "." in value or "#" in value:
        return True
    return len(value.strip()) >= 16


def rows_by_id(rows: Sequence[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    out: Dict[str, Dict[str, str]] = {}
    for r in rows:
        rid = r.get("id", "").strip()
        if rid:
            out[rid] = r
    return out


def normalize_gate(headers: Sequence[str], rows: Sequence[Dict[str, str]]) -> Dict[str, str]:
    if not headers:
        return {}
    field_header = value_header = None
    for h in headers:
        k = norm_key(h)
        if k in {"field", "gatefield", "check"}:
            field_header = h
        if k in {"value", "status", "result"}:
            value_header = h
    if field_header is None or value_header is None:
        if len(headers) >= 2:
            field_header, value_header = headers[0], headers[1]
        else:
            return {}
    gate: Dict[str, str] = {}
    for row in rows:
        c = GATE_ALIASES.get(norm_key(row.get(field_header, "")))
        if c:
            gate[c] = norm_value(row.get(value_header, ""))
    return gate


def validate_structured_table(text: str, title: str, checks: Dict[str, str], errors: List[str], why_column_name: str) -> None:
    if not has_section(text, title):
        errors.append(f"missing required section: {title}")
        return
    headers, raw_rows = extract_first_table(section_text(text, title))
    if not raw_rows:
        errors.append(f"{title} must be a structured table")
        return
    check_header = value_header = evidence_header = why_header = None
    for h in headers:
        k = norm_key(h)
        if k == "check": check_header = h
        elif k in {"result", "status", "value"}: value_header = h
        elif k in {"evidenceref", "evidence", "evidencebasis"}: evidence_header = h
        elif k in {norm_key(why_column_name), "why", "basis"}: why_header = h
    if not all([check_header, value_header, evidence_header, why_header]):
        errors.append(f"{title} missing required columns: check, result, evidence ref, {why_column_name}")
        return
    seen = {norm_key(row.get(check_header or "", "")): row for row in raw_rows}
    for canonical, label in checks.items():
        if canonical not in seen:
            errors.append(f"{title} missing check `{label}`")
            continue
        row = seen[canonical]
        result = norm_value(row.get(value_header or "", ""))
        if result != "pass":
            errors.append(f"{title} `{label}` must have result `pass`, got `{result}`")
        if not evidence_ref_is_concrete(row.get(evidence_header or "", "")):
            errors.append(f"{title} `{label}` requires concrete evidence ref")
        if is_empty(row.get(why_header or "", "")):
            errors.append(f"{title} `{label}` requires explanation")


def check_invariant_ace(text: str) -> CheckResult:
    errors: List[str] = []
    warnings: List[str] = []

    for section in REQUIRED_SECTIONS:
        count = section_count(text, section)
        if count != 1:
            errors.append(f"{section} must appear exactly once, found {count}")
    for section in OPTIONAL_SINGLETON_SECTIONS:
        count = section_count(text, section)
        if count > 1:
            errors.append(f"{section} must appear at most once, found {count}")

    basis = section_text(text, "Review Basis")
    if "artifact_state_id" not in basis:
        errors.append("Review Basis missing artifact_state_id block")
    else:
        for key in ["branch", "head", "diff_digest", "proof_state"]:
            if not re.search(rf"(?im)^\s*{re.escape(key)}\s*:", basis):
                errors.append(f"artifact_state_id missing `{key}`")

    inventory = parse_inventory(section_text(text, "Candidate Invariant Inventory"))
    for k in ["candidatecount", "acceptedcount", "validationcount", "proofonlycount", "defernochange_count", "blockedcount", "candidateids", "acceptedids", "validationids", "proofonlyids", "defernochangeids", "blockedids", "missingids", "duplicateids"]:
        if k not in inventory:
            errors.append(f"Candidate Invariant Inventory missing `{k}`")

    ledger_headers, ledger_raw = extract_first_table(section_text(text, "Invariant Ledger"))
    ledger_map, ledger_rows = normalize_rows(ledger_headers, ledger_raw, LEDGER_ALIASES)
    missing_cols = [c for c in ["id", "predicate", "owner", "scope", "holdswhen", "sourceoftruth", "status", "boundary", "verification", "evidenceref", "route"] if c not in ledger_map]
    if missing_cols:
        errors.append("Invariant Ledger missing required columns: " + ", ".join(missing_cols))
    if not ledger_rows:
        errors.append("Invariant Ledger has no data rows")
    ids = [r.get("id", "").strip() for r in ledger_rows if r.get("id", "").strip()]
    dup_ids = sorted({rid for rid in ids if ids.count(rid) > 1})
    if dup_ids:
        errors.append("Invariant Ledger duplicate ids: " + ", ".join(dup_ids))

    candidate_ids = parse_id_list(inventory.get("candidateids", ""))
    if candidate_ids:
        missing_actual = sorted(set(candidate_ids) - set(ids))
        if missing_actual:
            errors.append("Candidate Inventory omitted candidate ids from ledger: " + ", ".join(missing_actual))
        extra_actual = sorted(set(ids) - set(candidate_ids))
        if extra_actual:
            warnings.append("Invariant Ledger has ids not listed in candidate_ids: " + ", ".join(extra_actual))
    for key, label in [("missingids", "missing ids"), ("duplicateids", "duplicate ids")]:
        vals = parse_id_list(inventory.get(key, ""))
        if vals:
            errors.append(f"Candidate Inventory reports {label}: " + ", ".join(vals))

    candidate_count = parse_int(inventory.get("candidatecount", ""))
    if candidate_count is not None and candidate_count != len(ledger_rows):
        errors.append(f"candidate_count={candidate_count} but ledger has {len(ledger_rows)} rows")

    auth_headers, auth_raw = extract_first_table(section_text(text, "Authority Clearance Matrix"))
    auth_map, auth_rows = normalize_rows(auth_headers, auth_raw, AUTHORITY_ALIASES)
    missing_auth = [c for c in ["id", "counterexample", "ownerscope", "induction", "boundary", "witnessparity", "verification", "skeptic", "status", "packetrefs"] if c not in auth_map]
    if missing_auth:
        errors.append("Authority Clearance Matrix missing required columns: " + ", ".join(missing_auth))
    auth_by_id = rows_by_id(auth_rows)
    for rid in ids:
        if rid not in auth_by_id:
            errors.append(f"{rid}: missing Authority Clearance Matrix row")

    receipt_headers, receipt_raw = extract_first_table(section_text(text, "Authority Packet Receipts"))
    receipt_map, receipt_rows = normalize_rows(receipt_headers, receipt_raw, RECEIPT_ALIASES)
    missing_receipt = [c for c in ["role", "status", "artifactmatch", "scopematch", "covered", "clearances", "vetoes", "usedfor", "reason"] if c not in receipt_map]
    if missing_receipt:
        errors.append("Authority Packet Receipts missing required columns: " + ", ".join(missing_receipt))
    roles_seen = {norm_value(r.get("role", "")) for r in receipt_rows}
    missing_roles = sorted(REQUIRED_ROLES - roles_seen)
    if missing_roles:
        errors.append("Authority Packet Receipts missing roles: " + ", ".join(missing_roles))
    for r in receipt_rows:
        label = r.get("role", "packet")
        status = norm_value(r.get("status", ""))
        if status not in PACKET_STATUS:
            errors.append(f"{label}: invalid packet status `{r.get('status', '')}`")
        if status in {"accepted", "root-equivalent"}:
            if norm_value(r.get("artifactmatch", "")) != "yes":
                errors.append(f"{label}: accepted/root-equivalent packet requires artifact_state_match=yes")
            if norm_value(r.get("scopematch", "")) != "yes":
                errors.append(f"{label}: accepted/root-equivalent packet requires scope_match=yes")
            if is_empty(r.get("covered", "")):
                errors.append(f"{label}: packet requires candidates_covered")

    agenda_headers, agenda_raw = extract_first_table(section_text(text, "Change Agenda"))
    agenda_map, agenda_rows = normalize_rows(agenda_headers, agenda_raw, AGENDA_ALIASES)
    missing_agenda = [c for c in ["id", "route", "change", "proof", "next", "owner"] if c not in agenda_map]
    if missing_agenda:
        errors.append("Change Agenda missing required columns: " + ", ".join(missing_agenda))
    agenda_by_id = rows_by_id(agenda_rows)
    if "__ALL__" in [v for row in agenda_rows for v in row.values()]:
        errors.append("Change Agenda must not use broad `all`; explicit invariant ids are required")

    veto_headers, veto_raw = extract_first_table(section_text(text, "Authority Veto Ledger"))
    veto_map, veto_rows = normalize_rows(veto_headers, veto_raw, VETO_ALIASES)
    missing_veto = [c for c in ["id", "source", "class", "claim", "evidenceref", "required", "route"] if c not in veto_map]
    if missing_veto:
        errors.append("Authority Veto Ledger missing required columns: " + ", ".join(missing_veto))
    veto_ids = {r.get("id", "").strip() for r in veto_rows if r.get("id", "").strip() and norm_value(r.get("class", "")) not in {"none", "not-needed"}}

    accepted_count = validation_count = proof_count = defer_nochange_count = blocked_count = enforce_count = 0
    ledger_by_id = rows_by_id(ledger_rows)
    for row in ledger_rows:
        rid = row.get("id", "<missing>").strip() or "<missing>"
        status = norm_value(row.get("status", ""))
        route = norm_value(row.get("route", ""))
        if status not in ALLOWED_STATUS:
            errors.append(f"{rid}: invalid acceptance status `{row.get('status','')}`")
        if route not in ALLOWED_ROUTE:
            errors.append(f"{rid}: invalid route `{row.get('route','')}`")
        if is_empty(row.get("predicate", "")):
            errors.append(f"{rid}: missing predicate")
        if status == "accepted":
            accepted_count += 1
        if route == "enforce-now":
            enforce_count += 1
        elif route == "validate-only":
            validation_count += 1
        elif route == "proof-only":
            proof_count += 1
        elif route in {"defer", "no-change"}:
            defer_nochange_count += 1
        elif route == "blocked":
            blocked_count += 1
        auth = auth_by_id.get(rid)
        if route == "enforce-now" or status == "accepted":
            for field in ["owner", "scope", "holdswhen", "sourceoftruth", "boundary", "verification"]:
                if is_empty(row.get(field, "")):
                    errors.append(f"{rid}: accepted/enforce-now invariant missing `{field}`")
            if not evidence_ref_is_concrete(row.get("evidenceref", "")):
                errors.append(f"{rid}: accepted/enforce-now invariant requires concrete evidence ref")
            if auth:
                for field in ["counterexample", "ownerscope", "induction", "boundary", "witnessparity", "verification"]:
                    if norm_value(auth.get(field, "")) != "clear":
                        errors.append(f"{rid}: enforce-now/accepted requires {field}=clear")
                if norm_value(auth.get("skeptic", "")) != "defeated":
                    errors.append(f"{rid}: enforce-now/accepted requires skeptic=defeated")
                if norm_value(auth.get("status", "")) != "cleared-for-enforcement":
                    errors.append(f"{rid}: enforce-now/accepted requires authority status cleared-for-enforcement")
                if not evidence_ref_is_concrete(auth.get("packetrefs", "")):
                    errors.append(f"{rid}: authority clearance requires concrete packet refs")
            if rid in veto_ids:
                errors.append(f"{rid}: enforce-now/accepted conflicts with unresolved veto ledger entry")
        if route == "validate-only":
            if auth and norm_value(auth.get("status", "")) != "cleared-for-validation":
                errors.append(f"{rid}: validate-only requires authority status cleared-for-validation")
        if route == "proof-only":
            if auth and norm_value(auth.get("status", "")) != "proof-only":
                errors.append(f"{rid}: proof-only requires authority status proof-only")
        if route == "blocked":
            if auth and norm_value(auth.get("status", "")) != "blocked":
                warnings.append(f"{rid}: blocked route usually has authority status blocked")
        agenda = agenda_by_id.get(rid)
        if not agenda:
            errors.append(f"{rid}: missing Change Agenda row")
        elif norm_value(agenda.get("route", "")) != route:
            errors.append(f"{rid}: Change Agenda route `{agenda.get('route','')}` does not match Invariant Ledger route `{row.get('route','')}`")
        if rid not in section_text(text, "Counterexample Ledger"):
            errors.append(f"{rid}: missing Counterexample Ledger entry")
        if rid not in section_text(text, "Transition / Induction Matrix"):
            errors.append(f"{rid}: missing Transition / Induction Matrix entry or row")
        if rid not in section_text(text, "Verification Plan"):
            errors.append(f"{rid}: missing Verification Plan entry")

    declared = {
        "acceptedcount": accepted_count,
        "validationcount": validation_count,
        "proofonlycount": proof_count,
        "defernochange_count": defer_nochange_count,
        "blockedcount": blocked_count,
    }
    for key, actual in declared.items():
        parsed = parse_int(inventory.get(key, ""))
        if parsed is not None and parsed != actual:
            errors.append(f"inventory {key}={parsed} but ledger has {actual}")

    gate_headers, gate_raw = extract_first_table(section_text(text, "Invariant Gate"))
    gate = normalize_gate(gate_headers, gate_raw)
    missing_gate = [f for f in REQUIRED_GATE_FIELDS if f not in gate]
    if missing_gate:
        errors.append("Invariant Gate missing required fields: " + ", ".join(missing_gate))
    for field in REQUIRED_GATE_FIELDS:
        if field not in gate:
            continue
        val = gate[field]
        if field in {"implementationhandoffallowed", "validationhandoffallowed", "proofonlyhandoffallowed"}:
            if val not in {"yes", "no"}:
                errors.append(f"{field} must be yes/no, got `{val}`")
        elif val not in {"pass", "fail"}:
            errors.append(f"{field} must be pass/fail, got `{val}`")
    gate_failures = [f for f in REQUIRED_GATE_FIELDS if f not in {"implementationhandoffallowed", "validationhandoffallowed", "proofonlyhandoffallowed"} and gate.get(f) == "fail"]
    if gate_failures and gate.get("invariantgatecomplete") == "pass":
        errors.append("invariant_gate_complete is pass despite failed gate fields: " + ", ".join(gate_failures))
    if errors and gate.get("invariantgatecomplete") == "pass":
        errors.append("invariant_gate_complete is pass despite mechanical contract errors")
    if errors and gate.get("implementationhandoffallowed") == "yes":
        errors.append("implementation_handoff_allowed is yes despite mechanical contract errors")
    if gate.get("implementationhandoffallowed") == "yes" and enforce_count == 0:
        errors.append("implementation_handoff_allowed is yes but no invariant route is enforce-now")
    if blocked_count and any(gate.get(f) == "yes" for f in ["implementationhandoffallowed", "validationhandoffallowed", "proofonlyhandoffallowed"]):
        errors.append("blocked invariant rows exist but a handoff permission is yes")
    if ledger_rows and accepted_count == len(ledger_rows):
        validate_structured_table(text, "All-Invariant Accepted Justification", ALL_ACCEPTED_CHECKS, errors, "why enforcement still warranted")

    for section in ["Acceptance Skew Audit", "Policy / Exception Ledger", "Witness and Fixture Parity Ledger", "Owner and Scope Ledger", "Enforcement Boundary Decision"]:
        if not section_text(text, section).strip():
            errors.append(f"{section} is empty")

    bottom = section_text(text, "Ace Bottom Line")
    if (gate_failures or errors) and "blocked" not in bottom.lower():
        errors.append("failed gate or mechanical error requires blocked Ace Bottom Line")

    stats = {
        "candidates": len(ledger_rows),
        "accepted": accepted_count,
        "enforce_now": enforce_count,
        "validate_only": validation_count,
        "proof_only": proof_count,
        "defer_no_change": defer_nochange_count,
        "blocked": blocked_count,
        "veto_rows": len(veto_ids),
        "errors": len(errors),
        "warnings": len(warnings),
    }
    return CheckResult(passed=not errors, errors=errors, warnings=warnings, stats=stats, gate=gate)


def print_human(result: CheckResult) -> None:
    print("PASS: Authority-Gated v1 invariant-ace contract satisfied" if result.passed else "FAIL: Authority-Gated v1 invariant-ace contract incomplete")
    print("stats:", ", ".join(f"{k}={v}" for k, v in result.stats.items()))
    if result.gate:
        print("gate:", ", ".join(f"{k}={v}" for k, v in result.gate.items()))
    if result.errors:
        print("errors:")
        for e in result.errors: print(f"- {e}")
    if result.warnings:
        print("warnings:")
        for w in result.warnings: print(f"- {w}")


def valid_fixture() -> str:
    return r"""
## Review Basis

artifact_state_id:
  branch: feature/invariant
  base: main@abc123
  head: feature@def456
  diff_digest: paths=src/cert.zig,tests/cert.zig
  proof_state: local tests pass

direction_state_id:
  source: PR-body
  source_ref: PR#7
  same_objective: yes

## Candidate Invariant Inventory

- candidate_count: 3
- accepted_count: 1
- validate_only_count: 1
- proof_only_count: 0
- defer_or_no_change_count: 1
- blocked_count: 0
- candidate_ids: inv1,inv2,inv3
- accepted_ids: inv1
- validate_only_ids: inv2
- proof_only_ids: []
- defer_or_no_change_ids: inv3
- blocked_ids: []
- missing_candidate_ids: []
- duplicate_candidate_ids: []

## Counterexample Ledger

- inv1: malformed certificate can carry matching descriptor ref without route-owned witness; current src/cert.zig:44 accepts it.
- inv2: plausible out-of-order replay trace needs model check before mutation.
- inv3: naming convention property has no counterexample in current artifact state.

## Invariant Ledger

| id | predicate | owner | scope | holds when | source of truth | acceptance status | enforcement boundary | verification signal | evidence ref | route |
|---|---|---|---|---|---|---|---|---|---|---|
| inv1 | selected route witness matches target ref | cert validator | certificate validation | on check | route certificate | accepted | certificate check | tests/cert.zig::route_witness | src/cert.zig:44 | enforce-now |
| inv2 | replay state only advances from frame authority | replay decoder | transcript replay | after frame apply | transcript image | unresolved | validation probe | tests/replay.zig::model | thread:inv2 | validate-only |
| inv3 | helper name follows local preference | helper module | local helper | n/a | convention absent | rejected | none | none | src/helper.zig:1 | no-change |

## Owner and Scope Ledger

| id | owner | scope | source of truth | ownership proof | wrong-owner alternative |
|---|---|---|---|---|---|
| inv1 | cert validator | certificate validation | route certificate | src/cert.zig:44 | generator-only check rejected |
| inv2 | replay decoder | transcript replay | transcript image | tests/replay.zig::model | unknown until probe |
| inv3 | helper module | local helper | none | src/helper.zig:1 | preference only |

## Transition / Induction Matrix

| id | transitions checked | induction status | preservation evidence | gap |
|---|---|---|---|---|
| inv1 | construct, import, check | closed | tests/cert.zig::route_witness | none |
| inv2 | frame_requested, frame_responded | unresolved | thread:inv2 | model check needed |
| inv3 | n/a | not-needed | src/helper.zig:1 | no invariant |

## Enforcement Boundary Decision

| id | chosen boundary | why not weaker | why not stronger | minimum cut |
|---|---|---|---|---|
| inv1 | certificate check | generator self-check misses imported certs | type-level rewrite too broad | compare target witness in check |
| inv2 | validation probe | mutation unproven | redesign too broad | model replay trace |
| inv3 | none | no material invariant | n/a | no change |

## Policy / Exception Ledger

| id | policy owner | exception path | authorized | evidence ref |
|---|---|---|---|---|
| inv1 | route certificate | none | n/a | src/cert.zig:44 |
| inv2 | replay decoder | none | unknown | thread:inv2 |
| inv3 | none | none | no | src/helper.zig:1 |

## Witness and Fixture Parity Ledger

| id | parity surface | fixture preconditions | status | evidence ref |
|---|---|---|---|---|
| inv1 | generator/validator cert witness | fixture uses generator helper | aligned | tests/cert.zig::route_witness |
| inv2 | replay image/model | model fixture needed | unresolved | tests/replay.zig::model |
| inv3 | none | none | not-needed | src/helper.zig:1 |

## Verification Plan

| id | verification signal | command/proof | falsifies what |
|---|---|---|---|
| inv1 | route witness regression | zig build test --summary all | forged cert accepted |
| inv2 | replay model probe | zig build test tests/replay.zig::model | out-of-order state advance |
| inv3 | none | none | no invariant claim |

## Authority Packet Receipts

| role | packet status | artifact state match | scope match | candidates covered | clearances added | vetoes added | used for | reason |
|---|---|---|---|---|---|---|---|---|
| counterexample-authority | root-equivalent | yes | yes | inv1,inv2,inv3 | inv1 | inv2,inv3 | trace | root inspected current artifact |
| owner-scope-authority | root-equivalent | yes | yes | inv1,inv2,inv3 | inv1,inv2 | inv3 | owner | root inspected owners |
| induction-authority | root-equivalent | yes | yes | inv1,inv2,inv3 | inv1 | inv2 | transitions | root transition pass |
| boundary-authority | root-equivalent | yes | yes | inv1,inv2,inv3 | inv1 | inv2,inv3 | boundary | root boundary pass |
| witness-parity-authority | root-equivalent | yes | yes | inv1,inv2,inv3 | inv1 | inv2 | witness | root parity pass |
| verification-authority | root-equivalent | yes | yes | inv1,inv2,inv3 | inv1,inv2 | inv3 | proof | root proof pass |
| skeptic-authority | root-equivalent | yes | yes | inv1,inv2,inv3 | inv1 | inv2,inv3 | veto | root skeptic pass |

## Authority Clearance Matrix

| id | counterexample | owner/scope | induction | boundary | witness/parity | verification | skeptic | authority status | packet refs |
|---|---|---|---|---|---|---|---|---|---|
| inv1 | clear | clear | clear | clear | clear | clear | defeated | cleared-for-enforcement | codex/agents/inv1 |
| inv2 | unresolved | clear | unresolved | unresolved | unresolved | clear | unresolved | cleared-for-validation | codex/agents/inv2 |
| inv3 | veto | veto | not-needed | not-needed | not-needed | not-needed | veto | no-change | codex/agents/inv3 |

## Authority Veto Ledger

| id | veto source | veto class | veto claim | evidence ref | required to clear | final route |
|---|---|---|---|---|---|---|
| inv2 | induction-authority | validation-needed | trace plausible but unproven | thread:inv2 | replay model failure | validate-only |
| inv3 | skeptic-authority | no-counterexample | preference is not an invariant | src/helper.zig:1 | repo convention | no-change |

## Accepted Invariants

- inv1: enforce certificate witness parity at check boundary.

## Validate Only

- inv2: model replay trace before mutation.

## Proof Only

- none.

## Defer / No Change

- inv3: no invariant; no change.

## Change Agenda

| id | route | change | proof or validation required | next | owner |
|---|---|---|---|---|---|
| inv1 | enforce-now | compare selected target witness during certificate check | zig build test --summary all | route to implementation | cert validator |
| inv2 | validate-only | add replay model probe only | replay model test | route validation only | replay decoder |
| inv3 | no-change | none | none | none | none |

## Acceptance Skew Audit

- distribution: accepted=1 validate-only=1 no-change=1
- all-accepted pressure: no
- validation-only alternatives: inv2 preserved
- no-change alternatives: inv3 preserved

## Invariant Gate

| field | value | basis |
|---|---|---|
| artifact_state_coverage | pass | artifact_state_id recorded |
| candidate_inventory_coverage | pass | inventory matches ledger |
| counterexample_coverage | pass | all candidates have trace/veto entry |
| owner_scope_coverage | pass | owners and scopes named |
| induction_coverage | pass | transition matrix present |
| boundary_decision_coverage | pass | boundary decisions present |
| policy_exception_coverage | pass | policy ledger present |
| witness_fixture_parity_coverage | pass | witness ledger present |
| verification_coverage | pass | verification plan present |
| authority_packet_coverage | pass | root-equivalent packets cover all roles |
| authority_clearance_coverage | pass | matrix covers all ids |
| authority_veto_coverage | pass | vetoes preserved and respected |
| change_agenda_consistency | pass | agenda mirrors routes |
| acceptance_skew_audit | pass | skew audited |
| invariant_gate_complete | pass | all required fields pass |
| implementation_handoff_allowed | yes | inv1 cleared-for-enforcement |
| validation_handoff_allowed | yes | inv2 validate-only |
| proof_only_handoff_allowed | no | no proof-only rows |

## Ace Bottom Line

Proceed: inv1 may route to implementation; inv2 is validation-only; inv3 is no-change.
"""


def invalid_fixture() -> str:
    return r"""
## Review Basis

- branch: unknown

## Candidate Invariant Inventory

- candidate_count: 1
- accepted_count: 1
- validate_only_count: 0
- proof_only_count: 0
- defer_or_no_change_count: 0
- blocked_count: 0
- candidate_ids: inv1
- accepted_ids: inv1
- validate_only_ids: []
- proof_only_ids: []
- defer_or_no_change_ids: []
- blocked_ids: []
- missing_candidate_ids: []
- duplicate_candidate_ids: []

## Counterexample Ledger

- inv1: seems bad.

## Invariant Ledger

| id | predicate | owner | scope | holds when | source of truth | acceptance status | enforcement boundary | verification signal | evidence ref | route |
|---|---|---|---|---|---|---|---|---|---|---|
| inv1 | something should match | unknown | unknown | always | unknown | accepted | none | tests | code | enforce-now |

## Owner and Scope Ledger

unknown.

## Transition / Induction Matrix

none.

## Enforcement Boundary Decision

none.

## Policy / Exception Ledger

none.

## Witness and Fixture Parity Ledger

none.

## Verification Plan

none.

## Authority Packet Receipts

| role | packet status | artifact state match | scope match | candidates covered | clearances added | vetoes added | used for | reason |
|---|---|---|---|---|---|---|---|---|
| counterexample-authority | accepted | no | no | inv1 | inv1 | none | trace | generic |

## Authority Clearance Matrix

| id | counterexample | owner/scope | induction | boundary | witness/parity | verification | skeptic | authority status | packet refs |
|---|---|---|---|---|---|---|---|---|---|
| inv1 | clear | unresolved | unresolved | unresolved | unresolved | unresolved | unresolved | cleared-for-enforcement | packets |

## Authority Veto Ledger

| id | veto source | veto class | veto claim | evidence ref | required to clear | final route |
|---|---|---|---|---|---|---|
| inv1 | skeptic-authority | wrong-owner | owner unknown | code | owner proof | enforce-now |

## Accepted Invariants

- inv1

## Validate Only

none.

## Proof Only

none.

## Defer / No Change

none.

## Change Agenda

| id | route | change | proof or validation required | next | owner |
|---|---|---|---|---|---|
| inv1 | enforce-now | fix it | tests | implementation | unknown |

## Acceptance Skew Audit

all accepted.

## Invariant Gate

| field | value | basis |
|---|---|---|
| artifact_state_coverage | fail | missing |
| candidate_inventory_coverage | pass | one |
| counterexample_coverage | fail | generic |
| owner_scope_coverage | fail | unknown |
| induction_coverage | fail | unknown |
| boundary_decision_coverage | fail | none |
| policy_exception_coverage | fail | none |
| witness_fixture_parity_coverage | fail | none |
| verification_coverage | fail | generic |
| authority_packet_coverage | fail | missing roles |
| authority_clearance_coverage | fail | unresolved |
| authority_veto_coverage | fail | unresolved veto |
| change_agenda_consistency | pass | one |
| acceptance_skew_audit | fail | generic |
| invariant_gate_complete | fail | incomplete |
| implementation_handoff_allowed | no | blocked |
| validation_handoff_allowed | no | blocked |
| proof_only_handoff_allowed | no | blocked |

## Ace Bottom Line

Blocked: incomplete invariant gate. Do not implement yet.
"""


def run_self_test() -> int:
    good = check_invariant_ace(valid_fixture())
    bad = check_invariant_ace(invalid_fixture())
    if good.passed and not bad.passed:
        print("self-test passed")
        return 0
    print("self-test failed")
    print("valid result:", good.to_json())
    print("invalid result:", bad.to_json())
    return 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", help="Markdown invariant-ace output to check")
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
    result = check_invariant_ace(text)
    if args.json:
        print(result.to_json())
    else:
        print_human(result)
    return 0 if result.passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
