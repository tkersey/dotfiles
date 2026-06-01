#!/usr/bin/env python3
"""Mechanical contract checker for Surface-Budgeted Resolution-Warranted v5 review-adjudication outputs.

The checker validates output shape, stale-proofing fields, evidence-reference
obligations, resolve-selection anti-laundering, resolution warrants, surface budgets, and
downstream handoff/diff-surface safety. It cannot prove semantic correctness, but it blocks
unlicensed implementation, validation, or thread resolution before routing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

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
ALLOWED_EVIDENCE_GRADE = {
    "current-artifact",
    "current-test",
    "current-ci",
    "current-session-artifact",
    "prior-session-artifact",
    "memory-only",
    "reviewer-only",
    "none",
}
ACTION_EVIDENCE_GRADES = {
    "current-artifact",
    "current-test",
    "current-ci",
    "current-session-artifact",
}
ALLOWED_HANDOFF = {
    "none",
    "route-to-accretive-implementer",
    "route-to-fixed-point-driver",
    "route-to-logophile",
    "ask-user",
    "draft-reply",
}
IMPLEMENTATION_HANDOFFS = {
    "route-to-accretive-implementer",
    "route-to-fixed-point-driver",
}
ALLOWED_GROUNDED = {"yes", "no", "unknown"}
ALLOWED_MATERIAL = {"yes", "no", "user-requested", "unknown"}
ALLOWED_FRESH = {"current", "stale", "superseded", "unclear"}
ALLOWED_DIAGNOSIS = {"correct", "partially-correct", "misdiagnosed", "unknown"}
ALLOWED_SCOPE_FIT = {"yes", "no", "partial", "unknown"}
ALLOWED_RESOLUTION_VALUE = {
    "merge-blocking",
    "correctness-critical",
    "review-closure",
    "proof-only",
    "validation-needed",
    "low-value",
    "out-of-lane",
    "blocked",
}
ALLOWED_NO_CHANGE_DEFEATED = {"yes", "no", "unresolved"}
ALLOWED_RESOLVE_DECISION = {
    "address",
    "validate-only",
    "resolve-thread-only",
    "do-not-address",
    "blocked",
}
ALLOWED_ROUTE_RATIONALE = {
    "narrow-local",
    "coupled-comments",
    "invariant-level",
    "structural",
    "validation-only",
    "contentious",
    "likely-to-reopen",
    "proof-only-thread",
    "no-change",
    "blocked",
}
FIXED_POINT_RATIONALES = {
    "coupled-comments",
    "invariant-level",
    "structural",
    "validation-only",
    "contentious",
    "likely-to-reopen",
}

ALLOWED_PERMITTED_ACTION = {
    "mutate-code",
    "add-validation-only",
    "resolve-thread",
    "draft-reply",
    "defer",
    "none",
}
ACTION_BY_DECISION = {
    "address": {"mutate-code"},
    "validate-only": {"add-validation-only"},
    "resolve-thread-only": {"resolve-thread"},
    "do-not-address": {"draft-reply", "defer", "none"},
    "blocked": {"none"},
}

ALLOWED_SURFACE_BUDGET_MODE = {
    "subtractive-first",
    "neutral-first",
    "additive-capped",
    "exploratory",
}
ALLOWED_TARGET_NET_LOC = {
    "negative",
    "zero",
    "small-positive",
    "unknown",
    "uncapped-blocked",
}
ALLOWED_EXPANSION_STATUS = {
    "not-needed",
    "needed",
    "granted",
    "blocked",
}
ALLOWED_YES_NO = {"yes", "no"}

REQUIRED_LEDGER_FIELDS = [
    "id",
    "reviewer",
    "location",
    "excerpt",
    "claim",
    "concern",
    "proposed",
    "relevance",
    "disposition",
    "nochange",
    "invariant",
    "evidencegrade",
    "evidenceref",
    "handoff",
]
REQUIRED_DECISION_FIELDS = [
    "id",
    "grounded",
    "material",
    "fresh",
    "diagnosis",
    "scopefit",
    "resolutionvalue",
    "nochangedefeated",
    "minevidence",
]
REQUIRED_RESOLVE_FIELDS = [
    "id",
    "decision",
    "reason",
    "proofref",
    "next",
    "routerationale",
]

REQUIRED_WARRANT_FIELDS = [
    "warrantid",
    "claimid",
    "source",
    "claimexcerpt",
    "decision",
    "concern",
    "proposed",
    "nochange",
    "resolutionvalue",
    "routerationale",
    "permittedaction",
    "permittedscope",
    "forbiddenactions",
    "evidencerefs",
    "countercaseref",
    "proofrequired",
    "expiry",
]

REQUIRED_SURFACE_BUDGET_FIELDS = [
    "warrantid",
    "mode",
    "targetnetloc",
    "maxpositiveloc",
    "maxnewpublicsymbols",
    "maxnewfiles",
    "maxnewhelpers",
    "maxnewflagsorknobs",
    "maxnewstatevariants",
    "maxnewbranches",
    "duplicatepathbudget",
    "subtractiveprobesrequired",
    "expansionwarrantrequired",
    "expansionstatus",
    "proofrequired",
    "notes",
]
REQUIRED_GATE_FIELDS = [
    "artifactstatecoverage",
    "commentinventorycoverage",
    "identitycoverage",
    "decisiontestcoverage",
    "nochangecoverage",
    "dispositioncoverage",
    "proposedfixseparation",
    "evidencerefcoverage",
    "resolveselectioncoverage",
    "resolvecountercasecoverage",
    "resolutionwarrantcoverage",
    "surfacebudgetcoverage",
    "surfacebudgetconsumptionsafety",
    "warrantconsumptionsafety",
    "handoffagendaconsistency",
    "selectionskewaudit",
    "invariantpass",
    "specialistpacketcoverage",
    "acceptanceskewaudit",
    "adjudicationcomplete",
    "implementationhandoffallowed",
    "validationhandoffallowed",
    "replyhandoffallowed",
]
REQUIRED_SECTIONS = [
    "Review Basis",
    "Comment Inventory",
    "PR Why Ledger",
    "Comment Ledger",
    "Decision Tests",
    "No-Change Countercases",
    "Governing Invariant Ledger",
    "Act On",
    "Rebut",
    "Defer / Out of Scope",
    "Need Evidence",
    "Resolve Selection",
    "Resolve Countercases",
    "Resolution Warrants",
    "Surface Budget Ledger",
    "Invariant-Level Handoff",
    "Acceptance Skew Audit",
    "Selection Skew Audit",
    "Adjudication Gate",
    "Handoff Agenda",
    "Adjudication Bottom Line",
]
OPTIONAL_SINGLETON_SECTIONS = {
    "All-Action Justification",
    "All-Selected Justification",
    "Specialist Packet Receipts",
}
ALL_ACTION_CHECKS = {
    "stalesuperseded": "stale/superseded",
    "unsupported": "unsupported",
    "preferenceonly": "preference-only",
    "outofscope": "out-of-scope",
    "misdiagnosis": "misdiagnosis",
    "proposedfixvalidity": "proposed-fix validity",
    "validationonlyalternative": "validation-only alternative",
    "sharedinvariant": "shared-invariant",
}
ALL_SELECTED_CHECKS = {
    "stalealreadyfixedalternative": "stale/already-fixed alternative",
    "proofonlythreadresolutionalternative": "proof-only thread-resolution alternative",
    "donotaddressalternative": "do-not-address alternative",
    "validatebeforemutationalternative": "validate-before-mutation alternative",
    "outofscopedeferalternative": "out-of-scope/defer alternative",
    "fixedpointoverroutingcheck": "fixed-point over-routing check",
}
EMPTY_MARKERS = {"", "-", "—", "n/a", "na", "unknown", "missing", "none", "[]"}
GENERIC_EVIDENCE = {
    "code",
    "code-supports-it",
    "artifact-evidence",
    "current-artifacts",
    "review",
    "reviewer-said-so",
    "looks-right",
    "tests",
}


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
    "excerpt": "excerpt",
    "shortexcerpt": "excerpt",
    "reviewexcerpt": "excerpt",
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
    "evidencegrade": "evidencegrade",
    "evidenceclass": "evidencegrade",
    "evidencelevel": "evidencegrade",
    "evidenceref": "evidenceref",
    "evidencebasis": "evidenceref",
    "evidence": "evidenceref",
    "handoff": "handoff",
    "handoffaction": "handoff",
}

DECISION_ALIASES = {
    "idthread": "id",
    "id": "id",
    "commentid": "id",
    "threadid": "id",
    "grounded": "grounded",
    "grounding": "grounded",
    "material": "material",
    "materiality": "material",
    "fresh": "fresh",
    "freshness": "fresh",
    "diagnosis": "diagnosis",
    "diagnosisquality": "diagnosis",
    "scopefit": "scopefit",
    "scope": "scopefit",
    "resolutionvalue": "resolutionvalue",
    "resolution": "resolutionvalue",
    "value": "resolutionvalue",
    "selectionvalue": "resolutionvalue",
    "nochangedefeated": "nochangedefeated",
    "nochangecountercasedefeated": "nochangedefeated",
    "countercasedefeated": "nochangedefeated",
    "minevidencetochange": "minevidence",
    "minimumevidencetochange": "minevidence",
    "minimumevidencetochangemind": "minevidence",
    "minevidencetochangemind": "minevidence",
}

RESOLVE_ALIASES = {
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
    "proofref": "proofref",
    "proof": "proofref",
    "evidenceref": "proofref",
    "next": "next",
    "nextaction": "next",
    "handoff": "next",
    "routerationale": "routerationale",
    "rationale": "routerationale",
    "route": "routerationale",
}

WARRANT_ALIASES = {
    "warrantid": "warrantid",
    "warrant": "warrantid",
    "claimid": "claimid",
    "commentid": "claimid",
    "threadid": "claimid",
    "source": "source",
    "claimexcerpt": "claimexcerpt",
    "excerpt": "claimexcerpt",
    "decision": "decision",
    "resolvedecision": "decision",
    "concernvalidity": "concern",
    "concern": "concern",
    "proposedfixvalidity": "proposed",
    "proposedfix": "proposed",
    "nochange": "nochange",
    "nochangestatus": "nochange",
    "resolutionvalue": "resolutionvalue",
    "value": "resolutionvalue",
    "routerationale": "routerationale",
    "route": "routerationale",
    "permittedaction": "permittedaction",
    "action": "permittedaction",
    "permission": "permittedaction",
    "permittedscope": "permittedscope",
    "scope": "permittedscope",
    "forbiddenactions": "forbiddenactions",
    "forbidden": "forbiddenactions",
    "evidencerefs": "evidencerefs",
    "evidenceref": "evidencerefs",
    "evidence": "evidencerefs",
    "countercaseref": "countercaseref",
    "countercase": "countercaseref",
    "proofrequired": "proofrequired",
    "proof": "proofrequired",
    "expiry": "expiry",
    "expires": "expiry",
}

SURFACE_BUDGET_ALIASES = {
    "warrantid": "warrantid",
    "warrant": "warrantid",
    "mode": "mode",
    "budgetmode": "mode",
    "surfacebudgetmode": "mode",
    "targetnetloc": "targetnetloc",
    "targetloc": "targetnetloc",
    "targetnetlines": "targetnetloc",
    "maxpositiveloc": "maxpositiveloc",
    "maxpositive": "maxpositiveloc",
    "maxinsertions": "maxpositiveloc",
    "maxnewpublicsymbols": "maxnewpublicsymbols",
    "publicsymbolbudget": "maxnewpublicsymbols",
    "maxnewfiles": "maxnewfiles",
    "newfilebudget": "maxnewfiles",
    "maxnewhelpers": "maxnewhelpers",
    "helperbudget": "maxnewhelpers",
    "maxnewflagsorknobs": "maxnewflagsorknobs",
    "maxnewflags": "maxnewflagsorknobs",
    "maxnewflagsknobs": "maxnewflagsorknobs",
    "flagsorknobs": "maxnewflagsorknobs",
    "flagsknobs": "maxnewflagsorknobs",
    "maxnewstatevariants": "maxnewstatevariants",
    "statevariantbudget": "maxnewstatevariants",
    "maxnewbranches": "maxnewbranches",
    "branchbudget": "maxnewbranches",
    "duplicatepathbudget": "duplicatepathbudget",
    "duplicatepaths": "duplicatepathbudget",
    "subtractiveprobesrequired": "subtractiveprobesrequired",
    "subtractiveprobes": "subtractiveprobesrequired",
    "expansionwarrantrequired": "expansionwarrantrequired",
    "expansionrequired": "expansionwarrantrequired",
    "expansionstatus": "expansionstatus",
    "proofrequired": "proofrequired",
    "proof": "proofrequired",
    "notes": "notes",
}

GATE_ALIASES = {
    "artifactstatecoverage": "artifactstatecoverage",
    "artifactcoverage": "artifactstatecoverage",
    "commentinventorycoverage": "commentinventorycoverage",
    "inventorycoverage": "commentinventorycoverage",
    "identitycoverage": "identitycoverage",
    "decisiontestcoverage": "decisiontestcoverage",
    "decisiontestscoverage": "decisiontestcoverage",
    "nochangecoverage": "nochangecoverage",
    "dispositioncoverage": "dispositioncoverage",
    "proposedfixseparation": "proposedfixseparation",
    "fixseparation": "proposedfixseparation",
    "evidencerefcoverage": "evidencerefcoverage",
    "evidencecoverage": "evidencerefcoverage",
    "resolveselectioncoverage": "resolveselectioncoverage",
    "resolvecoverage": "resolveselectioncoverage",
    "selectioncoverage": "resolveselectioncoverage",
    "resolvecountercasecoverage": "resolvecountercasecoverage",
    "resolvecountercasescoverage": "resolvecountercasecoverage",
    "resolutionwarrantcoverage": "resolutionwarrantcoverage",
    "resolutionwarrantscoverage": "resolutionwarrantcoverage",
    "warrantcoverage": "resolutionwarrantcoverage",
    "surfacebudgetcoverage": "surfacebudgetcoverage",
    "surfacebudgetscoverage": "surfacebudgetcoverage",
    "budgetcoverage": "surfacebudgetcoverage",
    "surfacebudgetconsumptionsafety": "surfacebudgetconsumptionsafety",
    "surfacebudgetconsumption": "surfacebudgetconsumptionsafety",
    "surfacebudgetsafety": "surfacebudgetconsumptionsafety",
    "warrantconsumptionsafety": "warrantconsumptionsafety",
    "warrantconsumption": "warrantconsumptionsafety",
    "consumptionsafety": "warrantconsumptionsafety",
    "handoffagendaconsistency": "handoffagendaconsistency",
    "agendaconsistency": "handoffagendaconsistency",
    "selectionskewaudit": "selectionskewaudit",
    "selectionaudit": "selectionskewaudit",
    "invariantpass": "invariantpass",
    "specialistpacketcoverage": "specialistpacketcoverage",
    "acceptanceskewaudit": "acceptanceskewaudit",
    "adjudicationcomplete": "adjudicationcomplete",
    "implementationhandoffallowed": "implementationhandoffallowed",
    "validationhandoffallowed": "validationhandoffallowed",
    "replyhandoffallowed": "replyhandoffallowed",
    "handoffallowed": "implementationhandoffallowed",
}

INVENTORY_ALIASES = {
    "inputcommentcount": "inputcount",
    "ledgerrowcount": "ledgercount",
    "inputcommentids": "inputids",
    "ledgercommentids": "ledgerids",
    "missingcommentids": "missingids",
    "duplicatecommentids": "duplicateids",
    "synthesizedidsforrealcomments": "synthesized",
}

HANDOFF_ALIASES = {
    "itemsselectedforimplementation": "implementation",
    "implementationitems": "implementation",
    "selectedforimplementation": "implementation",
    "validationonlyitems": "validation",
    "validationitems": "validation",
    "proofonlythreadresolutionitems": "proofonly",
    "proofonlyitems": "proofonly",
    "threadresolutionitems": "proofonly",
    "itemsnotselected": "notselected",
    "notselecteditems": "notselected",
    "blockeditems": "blocked",
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


def section_count(text: str, title: str) -> int:
    pattern = rf"(?im)^\s*#+\s+{re.escape(title)}\s*$"
    return len(re.findall(pattern, text))


def has_section(text: str, title: str) -> bool:
    return section_count(text, title) > 0


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
    return [cell.strip() for cell in line.split("|")]


def is_separator_row(cells: Sequence[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) is not None for cell in cells)


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
    sep = split_md_row(table_lines[1])
    if not is_separator_row(sep):
        return [], []
    rows: List[Dict[str, str]] = []
    for line in table_lines[2:]:
        cells = split_md_row(line)
        if len(cells) < len(headers):
            cells = list(cells) + [""] * (len(headers) - len(cells))
        rows.append({headers[i]: cells[i] for i in range(len(headers))})
    return headers, rows


def normalize_rows(headers: Sequence[str], rows: Sequence[Dict[str, str]], aliases: Dict[str, str]) -> Tuple[Dict[str, str], List[Dict[str, str]]]:
    header_map: Dict[str, str] = {}
    for header in headers:
        canonical = aliases.get(norm_key(header))
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
    field_header: Optional[str] = None
    value_header: Optional[str] = None
    for header in headers:
        key = norm_key(header)
        if key in {"field", "gatefield", "check"}:
            field_header = header
        if key in {"value", "status", "result"}:
            value_header = header
    if field_header is None or value_header is None:
        if len(headers) >= 2:
            field_header, value_header = headers[0], headers[1]
        else:
            return {}
    gate: Dict[str, str] = {}
    for row in rows:
        canonical = GATE_ALIASES.get(norm_key(row.get(field_header, "")))
        if canonical:
            gate[canonical] = norm_value(row.get(value_header, ""))
    return gate


def is_empty(value: str) -> bool:
    return norm_value(value) in EMPTY_MARKERS


def parse_int(value: str) -> Optional[int]:
    match = re.search(r"-?\d+", value or "")
    if not match:
        return None
    try:
        return int(match.group(0))
    except ValueError:
        return None


def parse_nonnegative_int(value: str) -> Optional[int]:
    parsed = parse_int(value)
    if parsed is None or parsed < 0:
        return None
    return parsed


def parse_diffstat(value: str) -> Tuple[int, int]:
    if not value:
        return 0, 0
    insertions = 0
    deletions = 0
    ins_match = re.search(r"(\d+)\s+insertions?\(\+\)", value)
    del_match = re.search(r"(\d+)\s+deletions?\(-\)", value)
    if ins_match:
        insertions = int(ins_match.group(1))
    if del_match:
        deletions = int(del_match.group(1))
    return insertions, deletions


def parse_id_list(value: str) -> List[str]:
    value = value.strip()
    if is_empty(value):
        return []
    if re.search(r"(?i)\ball\b", value):
        return ["__ALL__"]
    value = re.sub(r"^[\[({]", "", value)
    value = re.sub(r"[\])}]$", "", value)
    parts = re.split(r"[,;\s]+", value)
    return [part.strip().strip('"\'`') for part in parts if part.strip().strip('"\'`')]


def parse_inventory(block: str) -> Dict[str, str]:
    inventory: Dict[str, str] = {}
    for line in block.splitlines():
        stripped = re.sub(r"^[-*]\s+", "", line.strip())
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        canonical = INVENTORY_ALIASES.get(norm_key(key))
        if canonical:
            inventory[canonical] = value.strip()
    return inventory


def evidence_ref_is_concrete(value: str, *, allow_missing: bool = False) -> bool:
    if allow_missing and norm_value(value) in {"missing", "blocked", "unknown"}:
        return True
    if is_empty(value):
        return False
    normalized = norm_value(value)
    if normalized in GENERIC_EVIDENCE:
        return False
    if re.search(r"[\w./-]+:\d+", value):
        return True
    if any(token in normalized for token in ["test", "ci", "cmd", "command", "log", "thread", "pr#", "gh-", "github", "diff", "src/", "tests/", "commit"]):
        return True
    if "/" in value or "." in value or "#" in value:
        return True
    return len(value.strip()) >= 16


def rows_by_id(rows: Sequence[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    out: Dict[str, Dict[str, str]] = {}
    for row in rows:
        rid = row.get("id", "").strip()
        if rid:
            out[rid] = row
    return out


def parse_handoff_agenda(block: str, known_ids: Sequence[str], errors: List[str]) -> Dict[str, List[str]]:
    fields: Dict[str, str] = {}
    for line in block.splitlines():
        stripped = re.sub(r"^[-*]\s+", "", line.strip())
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        canonical = HANDOFF_ALIASES.get(norm_key(key))
        if canonical:
            fields[canonical] = value.strip()
    buckets = {"implementation": [], "validation": [], "proofonly": [], "notselected": [], "blocked": []}
    known = set(known_ids)
    for bucket in buckets:
        if bucket not in fields:
            errors.append(f"Handoff Agenda missing `{bucket}` item bucket")
            continue
        raw = fields[bucket]
        if re.search(r"(?i)\ball\b", raw):
            errors.append(f"Handoff Agenda `{bucket}` uses broad `all`; explicit comment ids are required")
            continue
        if is_empty(raw):
            buckets[bucket] = []
            continue
        present = [rid for rid in known_ids if re.search(rf"(?<![A-Za-z0-9_.:-]){re.escape(rid)}(?![A-Za-z0-9_.:-])", raw)]
        if present:
            buckets[bucket] = present
        else:
            buckets[bucket] = parse_id_list(raw)
    return buckets


def validate_structured_table(
    text: str,
    title: str,
    checks: Dict[str, str],
    errors: List[str],
    why_column_name: str,
) -> None:
    if not has_section(text, title):
        errors.append(f"missing required section: {title}")
        return
    headers, raw_rows = extract_first_table(section_text(text, title))
    if not raw_rows:
        errors.append(f"{title} must be a structured table")
        return
    check_header = value_header = evidence_header = why_header = None
    for header in headers:
        key = norm_key(header)
        if key == "check":
            check_header = header
        elif key in {"result", "status", "value"}:
            value_header = header
        elif key in {"evidenceref", "evidence", "evidencebasis"}:
            evidence_header = header
        elif key in {norm_key(why_column_name), "why", "basis"}:
            why_header = header
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


def validate_specialist_receipts(text: str, gate: Dict[str, str], errors: List[str]) -> None:
    coverage = gate.get("specialistpacketcoverage")
    has_receipts = has_section(text, "Specialist Packet Receipts") and bool(section_text(text, "Specialist Packet Receipts").strip())
    if coverage == "not-used":
        if has_receipts:
            errors.append("specialist_packet_coverage is `not-used` but Specialist Packet Receipts is present")
        return
    if coverage == "pass":
        if not has_receipts:
            errors.append("specialist_packet_coverage is `pass` but Specialist Packet Receipts is missing or empty")
            return
        headers, rows = extract_first_table(section_text(text, "Specialist Packet Receipts"))
        header_keys = {norm_key(h) for h in headers}
        required = {"role", "packetstatus", "artifactstatematch", "scopematch", "findingadded", "routechanged", "usedfor", "reason"}
        missing = sorted(required - header_keys)
        if missing:
            errors.append("Specialist Packet Receipts missing required columns: " + ", ".join(missing))
        if not rows:
            errors.append("Specialist Packet Receipts has no data rows")



def extract_refs(value: str) -> List[str]:
    if is_empty(value):
        return []
    parts = re.split(r"[,;\n]+", value)
    return [part.strip().strip('"\'`') for part in parts if part.strip().strip('"\'`')]


def text_mentions_any(value: str, needles: Sequence[str]) -> bool:
    value_norm = value.lower()
    return any(needle and needle.lower() in value_norm for needle in needles)


def validate_resolution_warrants(
    text: str,
    ledger_by_id: Dict[str, Dict[str, str]],
    resolve_by_id: Dict[str, Dict[str, str]],
    handoff_buckets: Dict[str, List[str]],
    errors: List[str],
    warnings: List[str],
    changed_files: Optional[Sequence[str]] = None,
    resolved_threads: Optional[Sequence[str]] = None,
) -> Dict[str, object]:
    headers, raw_rows = extract_first_table(section_text(text, "Resolution Warrants"))
    header_map, rows = normalize_rows(headers, raw_rows, WARRANT_ALIASES)
    missing_columns = [field for field in REQUIRED_WARRANT_FIELDS if field not in header_map]
    if missing_columns:
        errors.append("Resolution Warrants missing required columns: " + ", ".join(missing_columns))
    if not rows:
        errors.append("Resolution Warrants has no data rows")

    warrant_ids: List[str] = []
    by_claim: Dict[str, Dict[str, str]] = {}
    action_buckets = {"mutate-code": [], "add-validation-only": [], "resolve-thread": [], "draft-reply": [], "defer": [], "none": []}
    for idx, row in enumerate(rows, start=1):
        warrant_id = row.get("warrantid", "").strip() or f"warrant row {idx}"
        claim_id = row.get("claimid", "").strip()
        warrant_ids.append(warrant_id)
        if is_empty(warrant_id):
            errors.append(f"{warrant_id}: missing warrant id")
        if claim_id:
            if claim_id in by_claim:
                errors.append(f"{claim_id}: duplicate Resolution Warrant claim id")
            by_claim[claim_id] = row
        else:
            errors.append(f"{warrant_id}: missing claim id")

        decision = norm_value(row.get("decision", ""))
        concern = norm_value(row.get("concern", ""))
        proposed = norm_value(row.get("proposed", ""))
        nochange = norm_value(row.get("nochange", ""))
        resolution_value = norm_value(row.get("resolutionvalue", ""))
        route_rationale = norm_value(row.get("routerationale", ""))
        permitted_action = norm_value(row.get("permittedaction", ""))
        permitted_scope = row.get("permittedscope", "")
        forbidden_actions = row.get("forbiddenactions", "")
        evidence_refs = row.get("evidencerefs", "")
        countercase_ref = row.get("countercaseref", "")
        proof_required = row.get("proofrequired", "")
        expiry = row.get("expiry", "")

        if decision not in ALLOWED_RESOLVE_DECISION:
            errors.append(f"{warrant_id}: invalid warrant decision `{row.get('decision', '')}`")
        if concern not in ALLOWED_CONCERN:
            errors.append(f"{warrant_id}: invalid warrant concern validity `{row.get('concern', '')}`")
        if proposed not in ALLOWED_PROPOSED:
            errors.append(f"{warrant_id}: invalid warrant proposed-fix validity `{row.get('proposed', '')}`")
        if nochange not in ALLOWED_NO_CHANGE:
            errors.append(f"{warrant_id}: invalid warrant no-change status `{row.get('nochange', '')}`")
        if resolution_value not in ALLOWED_RESOLUTION_VALUE:
            errors.append(f"{warrant_id}: invalid warrant resolution value `{row.get('resolutionvalue', '')}`")
        if route_rationale not in ALLOWED_ROUTE_RATIONALE:
            errors.append(f"{warrant_id}: invalid warrant route rationale `{row.get('routerationale', '')}`")
        if permitted_action not in ALLOWED_PERMITTED_ACTION:
            errors.append(f"{warrant_id}: invalid permitted action `{row.get('permittedaction', '')}`")
        elif permitted_action in action_buckets and claim_id:
            action_buckets[permitted_action].append(claim_id)

        if claim_id and claim_id not in ledger_by_id:
            errors.append(f"{warrant_id}: claim id `{claim_id}` does not appear in Comment Ledger")
        resolve_row = resolve_by_id.get(claim_id)
        if resolve_row:
            resolve_decision = norm_value(resolve_row.get("decision", ""))
            resolve_route = norm_value(resolve_row.get("routerationale", ""))
            if decision != resolve_decision:
                errors.append(f"{warrant_id}: warrant decision `{decision}` does not match Resolve Selection `{resolve_decision}`")
            if route_rationale != resolve_route:
                errors.append(f"{warrant_id}: warrant route rationale `{route_rationale}` does not match Resolve Selection `{resolve_route}`")
        elif claim_id:
            errors.append(f"{warrant_id}: no Resolve Selection row for claim `{claim_id}`")

        allowed_actions = ACTION_BY_DECISION.get(decision, set())
        if permitted_action and allowed_actions and permitted_action not in allowed_actions:
            errors.append(f"{warrant_id}: decision `{decision}` cannot issue permitted action `{permitted_action}`")

        if permitted_action == "mutate-code":
            if nochange != "defeated":
                errors.append(f"{warrant_id}: mutate-code warrant requires no-change status defeated")
            if resolution_value not in {"merge-blocking", "correctness-critical", "review-closure"}:
                errors.append(f"{warrant_id}: mutate-code warrant has non-implementation resolution value `{resolution_value}`")
            if is_empty(permitted_scope) or norm_value(permitted_scope) in {"all", "repo", "whole-repo", "everything"}:
                errors.append(f"{warrant_id}: mutate-code warrant requires narrow permitted scope")
            if "mutate" not in norm_value(forbidden_actions) and "outside" not in norm_value(forbidden_actions):
                errors.append(f"{warrant_id}: mutate-code warrant must forbid mutation outside permitted scope")
            if not any(evidence_ref_is_concrete(ref) for ref in extract_refs(evidence_refs)):
                errors.append(f"{warrant_id}: mutate-code warrant requires concrete evidence refs")
        elif permitted_action == "add-validation-only":
            if decision != "validate-only":
                errors.append(f"{warrant_id}: add-validation-only requires decision validate-only")
            if resolution_value != "validation-needed":
                errors.append(f"{warrant_id}: add-validation-only requires resolution value validation-needed")
            forbidden_norm = norm_value(forbidden_actions)
            if "production" not in forbidden_norm and "requested-code-change" not in forbidden_norm and "mutate-code" not in forbidden_norm:
                errors.append(f"{warrant_id}: validation-only warrant must forbid production mutation/requested fix")
        elif permitted_action == "resolve-thread":
            if decision != "resolve-thread-only":
                errors.append(f"{warrant_id}: resolve-thread action requires decision resolve-thread-only")
            if not any(evidence_ref_is_concrete(ref) for ref in extract_refs(evidence_refs)):
                errors.append(f"{warrant_id}: resolve-thread warrant requires proof evidence refs")
        elif permitted_action in {"draft-reply", "defer", "none"}:
            if decision == "address" and permitted_action != "mutate-code":
                errors.append(f"{warrant_id}: address decision must issue mutate-code action")

        if is_empty(countercase_ref):
            errors.append(f"{warrant_id}: missing countercase ref")
        if is_empty(proof_required) and permitted_action != "none":
            errors.append(f"{warrant_id}: non-none warrant requires proof_required")
        expiry_norm = norm_value(expiry)
        if is_empty(expiry) or not any(token in expiry_norm for token in ["head", "base", "artifact", "comment", "claim", "thread", "diff"]):
            errors.append(f"{warrant_id}: expiry must mention artifact/comment invalidation conditions")

    resolve_ids = set(resolve_by_id)
    warrant_claims = set(by_claim)
    if resolve_ids - warrant_claims:
        errors.append("Resolution Warrants missing claims: " + ", ".join(sorted(resolve_ids - warrant_claims)))
    if warrant_claims - resolve_ids:
        errors.append("Resolution Warrants contain claims not in Resolve Selection: " + ", ".join(sorted(warrant_claims - resolve_ids)))

    expected_by_action = {
        "mutate-code": sorted(handoff_buckets.get("implementation", [])),
        "add-validation-only": sorted(handoff_buckets.get("validation", [])),
        "resolve-thread": sorted(handoff_buckets.get("proofonly", [])),
    }
    for action, expected_claims in expected_by_action.items():
        got_claims = sorted(action_buckets.get(action, []))
        if got_claims != expected_claims:
            errors.append(f"Resolution Warrant `{action}` claims mismatch Handoff Agenda: expected {expected_claims}, got {got_claims}")

    if changed_files:
        mutate_warrants = [row for row in rows if norm_value(row.get("permittedaction", "")) == "mutate-code"]
        for changed in changed_files:
            changed = changed.strip()
            if not changed:
                continue
            if not any(changed in row.get("permittedscope", "") for row in mutate_warrants):
                errors.append(f"changed file `{changed}` is not covered by any mutate-code warrant permitted scope")
    if resolved_threads:
        thread_warrants = [row for row in rows if norm_value(row.get("permittedaction", "")) in {"resolve-thread", "mutate-code"}]
        for thread in resolved_threads:
            thread = thread.strip()
            if not thread:
                continue
            if not any(thread in row.get("permittedscope", "") or thread in row.get("claimid", "") for row in thread_warrants):
                errors.append(f"resolved thread `{thread}` is not covered by any resolve-thread/address warrant")

    return {"rows": rows, "by_claim": by_claim, "action_buckets": action_buckets}


def validate_surface_budget_ledger(
    text: str,
    warrant_rows: Sequence[Dict[str, str]],
    errors: List[str],
    warnings: List[str],
    diffstat: str = "",
    new_public_symbols: int = 0,
    new_files: int = 0,
    new_helpers: int = 0,
    new_flags_or_knobs: int = 0,
) -> Dict[str, object]:
    headers, raw_rows = extract_first_table(section_text(text, "Surface Budget Ledger"))
    header_map, rows = normalize_rows(headers, raw_rows, SURFACE_BUDGET_ALIASES)
    missing_columns = [field for field in REQUIRED_SURFACE_BUDGET_FIELDS if field not in header_map]
    if missing_columns:
        errors.append("Surface Budget Ledger missing required columns: " + ", ".join(missing_columns))
    if not rows:
        errors.append("Surface Budget Ledger has no data rows")

    budget_by_warrant: Dict[str, Dict[str, str]] = {}
    for idx, row in enumerate(rows, start=1):
        warrant_id = row.get("warrantid", "").strip() or f"surface budget row {idx}"
        if warrant_id in budget_by_warrant:
            errors.append(f"{warrant_id}: duplicate Surface Budget Ledger row")
        budget_by_warrant[warrant_id] = row
        mode = norm_value(row.get("mode", ""))
        target = norm_value(row.get("targetnetloc", ""))
        subtractive = norm_value(row.get("subtractiveprobesrequired", ""))
        expansion_required = norm_value(row.get("expansionwarrantrequired", ""))
        expansion_status = norm_value(row.get("expansionstatus", ""))
        if mode not in ALLOWED_SURFACE_BUDGET_MODE:
            errors.append(f"{warrant_id}: invalid surface budget mode `{row.get('mode', '')}`")
        if target not in ALLOWED_TARGET_NET_LOC:
            errors.append(f"{warrant_id}: invalid target net LOC `{row.get('targetnetloc', '')}`")
        if subtractive not in ALLOWED_YES_NO:
            errors.append(f"{warrant_id}: subtractive probes required must be yes/no")
        if expansion_required not in ALLOWED_YES_NO:
            errors.append(f"{warrant_id}: expansion warrant required must be yes/no")
        if expansion_status not in ALLOWED_EXPANSION_STATUS:
            errors.append(f"{warrant_id}: invalid expansion status `{row.get('expansionstatus', '')}`")
        for field in [
            "maxpositiveloc",
            "maxnewpublicsymbols",
            "maxnewfiles",
            "maxnewhelpers",
            "maxnewflagsorknobs",
            "maxnewstatevariants",
            "maxnewbranches",
            "duplicatepathbudget",
        ]:
            if parse_nonnegative_int(row.get(field, "")) is None:
                errors.append(f"{warrant_id}: `{field}` must be a non-negative integer")
        if is_empty(row.get("proofrequired", "")):
            errors.append(f"{warrant_id}: Surface Budget Ledger requires proof required")
        if is_empty(row.get("notes", "")):
            errors.append(f"{warrant_id}: Surface Budget Ledger requires notes")

    mutate_warrants = [row for row in warrant_rows if norm_value(row.get("permittedaction", "")) == "mutate-code"]
    mutate_ids = [row.get("warrantid", "").strip() for row in mutate_warrants if row.get("warrantid", "").strip()]
    missing_budgets = sorted(set(mutate_ids) - set(budget_by_warrant))
    if missing_budgets:
        errors.append("Surface Budget Ledger missing mutate-code warrant ids: " + ", ".join(missing_budgets))
    all_warrant_ids = {row.get("warrantid", "").strip() for row in warrant_rows if row.get("warrantid", "").strip()}
    extra_budgets = sorted(set(budget_by_warrant) - all_warrant_ids)
    if extra_budgets:
        errors.append("Surface Budget Ledger contains unknown warrant ids: " + ", ".join(extra_budgets))

    total_max_positive = 0
    total_public_budget = 0
    total_file_budget = 0
    total_helper_budget = 0
    total_flag_budget = 0
    subtractive_first_count = 0
    for warrant in mutate_warrants:
        wid = warrant.get("warrantid", "").strip()
        budget = budget_by_warrant.get(wid)
        if not budget:
            continue
        mode = norm_value(budget.get("mode", ""))
        target = norm_value(budget.get("targetnetloc", ""))
        subtractive = norm_value(budget.get("subtractiveprobesrequired", ""))
        expansion_required = norm_value(budget.get("expansionwarrantrequired", ""))
        max_pos = parse_nonnegative_int(budget.get("maxpositiveloc", "")) or 0
        total_max_positive += max_pos
        total_public_budget += parse_nonnegative_int(budget.get("maxnewpublicsymbols", "")) or 0
        total_file_budget += parse_nonnegative_int(budget.get("maxnewfiles", "")) or 0
        total_helper_budget += parse_nonnegative_int(budget.get("maxnewhelpers", "")) or 0
        total_flag_budget += parse_nonnegative_int(budget.get("maxnewflagsorknobs", "")) or 0
        if mode == "subtractive-first":
            subtractive_first_count += 1
        if subtractive != "yes":
            errors.append(f"{wid}: mutate-code surface budget requires subtractive probes before first production patch")
        if expansion_required != "yes":
            errors.append(f"{wid}: mutate-code surface budget requires expansion warrant for additive escape")
        if mode == "exploratory":
            errors.append(f"{wid}: mutate-code warrant cannot use exploratory surface budget mode")
        if target == "uncapped-blocked":
            errors.append(f"{wid}: mutate-code warrant cannot proceed with uncapped-blocked target net LOC")
        if target in {"negative", "zero"} and max_pos > 0:
            warnings.append(f"{wid}: target net LOC `{target}` has positive LOC allowance {max_pos}; verify expansion constraint")

    insertions, deletions = parse_diffstat(diffstat)
    net = insertions - deletions
    if diffstat and mutate_warrants:
        if net > total_max_positive:
            errors.append(f"diffstat net LOC +{net} exceeds mutate-code surface budget max positive LOC {total_max_positive}")
        if mutate_ids and all(norm_value(budget_by_warrant.get(wid, {}).get("targetnetloc", "")) == "negative" for wid in mutate_ids if wid in budget_by_warrant) and net >= 0:
            errors.append("all mutate-code warrants target negative net LOC, but diffstat is not net-negative")
    if new_public_symbols > total_public_budget:
        errors.append(f"new public symbols {new_public_symbols} exceed surface budget {total_public_budget}")
    if new_files > total_file_budget:
        errors.append(f"new files {new_files} exceed surface budget {total_file_budget}")
    if new_helpers > total_helper_budget:
        errors.append(f"new helpers {new_helpers} exceed surface budget {total_helper_budget}")
    if new_flags_or_knobs > total_flag_budget:
        errors.append(f"new flags/knobs {new_flags_or_knobs} exceed surface budget {total_flag_budget}")

    return {
        "rows": rows,
        "by_warrant": budget_by_warrant,
        "mutate_budget_rows": len(mutate_ids),
        "subtractive_first": subtractive_first_count,
        "total_max_positive_loc": total_max_positive,
        "diffstat_insertions": insertions,
        "diffstat_deletions": deletions,
        "diffstat_net": net,
    }

def check_adjudication(
    text: str,
    changed_files: Optional[Sequence[str]] = None,
    resolved_threads: Optional[Sequence[str]] = None,
    diffstat: str = "",
    new_public_symbols: int = 0,
    new_files: int = 0,
    new_helpers: int = 0,
    new_flags_or_knobs: int = 0,
) -> CheckResult:
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

    review_basis = section_text(text, "Review Basis")
    if "artifact_state_id" not in review_basis:
        errors.append("Review Basis missing artifact_state_id block")
    else:
        for key in ["branch", "head", "diff_digest", "comment_set_digest", "ci_state"]:
            if not re.search(rf"(?im)^\s*{re.escape(key)}\s*:", review_basis):
                errors.append(f"artifact_state_id missing `{key}`")

    inventory = parse_inventory(section_text(text, "Comment Inventory"))
    for key in ["inputcount", "ledgercount", "inputids", "ledgerids", "missingids", "duplicateids", "synthesized"]:
        if key not in inventory:
            errors.append(f"Comment Inventory missing `{key}`")

    ledger_headers, raw_rows = extract_first_table(section_text(text, "Comment Ledger"))
    header_map, rows = normalize_rows(ledger_headers, raw_rows, COLUMN_ALIASES)
    missing_columns = [field for field in REQUIRED_LEDGER_FIELDS if field not in header_map]
    if missing_columns:
        errors.append("Comment Ledger missing required columns: " + ", ".join(missing_columns))
    if not rows:
        errors.append("Comment Ledger has no data rows")

    ledger_ids = [row.get("id", "").strip() for row in rows if row.get("id", "").strip()]
    duplicate_ledger_ids = sorted({rid for rid in ledger_ids if ledger_ids.count(rid) > 1})
    if duplicate_ledger_ids:
        errors.append("Comment Ledger duplicate ids: " + ", ".join(duplicate_ledger_ids))

    input_count = parse_int(inventory.get("inputcount", ""))
    ledger_count = parse_int(inventory.get("ledgercount", ""))
    if input_count is not None and input_count != len(rows):
        errors.append(f"Comment Inventory input_comment_count={input_count} but ledger has {len(rows)} rows")
    if ledger_count is not None and ledger_count != len(rows):
        errors.append(f"Comment Inventory ledger_row_count={ledger_count} but ledger has {len(rows)} rows")

    input_ids = parse_id_list(inventory.get("inputids", ""))
    declared_ledger_ids = parse_id_list(inventory.get("ledgerids", ""))
    missing_ids = parse_id_list(inventory.get("missingids", ""))
    duplicate_ids = parse_id_list(inventory.get("duplicateids", ""))
    synthesized = norm_value(inventory.get("synthesized", ""))
    if input_ids:
        actual_missing = sorted(set(input_ids) - set(ledger_ids))
        if actual_missing:
            errors.append("Comment Inventory omitted input ids from ledger: " + ", ".join(actual_missing))
        actual_extra = sorted(set(ledger_ids) - set(input_ids))
        if actual_extra:
            warnings.append("Comment Ledger has ids not listed in input_comment_ids: " + ", ".join(actual_extra))
    if declared_ledger_ids and set(declared_ledger_ids) != set(ledger_ids):
        errors.append("Comment Inventory ledger_comment_ids does not match actual ledger ids")
    if missing_ids:
        errors.append("Comment Inventory reports missing ids: " + ", ".join(missing_ids))
    if duplicate_ids:
        errors.append("Comment Inventory reports duplicate ids: " + ", ".join(duplicate_ids))
    if synthesized == "yes":
        errors.append("synthesized_ids_for_real_comments is yes; real review identity coverage fails")
    elif synthesized not in {"yes", "no"}:
        errors.append("synthesized_ids_for_real_comments must be yes/no")

    decision_headers, decision_raw_rows = extract_first_table(section_text(text, "Decision Tests"))
    decision_header_map, decision_rows = normalize_rows(decision_headers, decision_raw_rows, DECISION_ALIASES)
    missing_decision_columns = [field for field in REQUIRED_DECISION_FIELDS if field not in decision_header_map]
    if missing_decision_columns:
        errors.append("Decision Tests missing required columns: " + ", ".join(missing_decision_columns))
    if not decision_rows:
        errors.append("Decision Tests has no data rows")
    decisions = rows_by_id(decision_rows)

    act_count = validation_count = reply_count = non_action_count = 0
    ledger_by_id = rows_by_id(rows)
    nochange_section = section_text(text, "No-Change Countercases")
    resolve_countercase_section = section_text(text, "Resolve Countercases")

    for idx, row in enumerate(rows, start=1):
        label = row.get("id", f"row {idx}") or f"row {idx}"
        for field_name in ["id", "reviewer", "location", "excerpt", "claim"]:
            if is_empty(row.get(field_name, "")):
                errors.append(f"{label}: missing raw identity field `{field_name}`")
        if label not in nochange_section:
            errors.append(f"{label}: missing No-Change Countercases entry")
        if label not in resolve_countercase_section:
            errors.append(f"{label}: missing Resolve Countercases entry")

        relevance = norm_value(row.get("relevance", ""))
        disposition = norm_value(row.get("disposition", ""))
        nochange = norm_value(row.get("nochange", ""))
        concern = norm_value(row.get("concern", ""))
        proposed = norm_value(row.get("proposed", ""))
        evidence_grade = norm_value(row.get("evidencegrade", ""))
        evidence_ref = row.get("evidenceref", "")
        handoff = norm_value(row.get("handoff", ""))

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
        if evidence_grade not in ALLOWED_EVIDENCE_GRADE:
            errors.append(f"{label}: invalid evidence grade `{row.get('evidencegrade', '')}`")
        if handoff not in ALLOWED_HANDOFF:
            errors.append(f"{label}: invalid handoff `{row.get('handoff', '')}`")

        decision = decisions.get(label)
        if not decision:
            errors.append(f"{label}: missing Decision Tests row")
        else:
            grounded = norm_value(decision.get("grounded", ""))
            material = norm_value(decision.get("material", ""))
            fresh = norm_value(decision.get("fresh", ""))
            diagnosis = norm_value(decision.get("diagnosis", ""))
            scopefit = norm_value(decision.get("scopefit", ""))
            resolutionvalue = norm_value(decision.get("resolutionvalue", ""))
            nochangedefeated = norm_value(decision.get("nochangedefeated", ""))
            if grounded not in ALLOWED_GROUNDED:
                errors.append(f"{label}: invalid Decision Tests grounded `{grounded}`")
            if material not in ALLOWED_MATERIAL:
                errors.append(f"{label}: invalid Decision Tests material `{material}`")
            if fresh not in ALLOWED_FRESH:
                errors.append(f"{label}: invalid Decision Tests fresh `{fresh}`")
            if diagnosis not in ALLOWED_DIAGNOSIS:
                errors.append(f"{label}: invalid Decision Tests diagnosis `{diagnosis}`")
            if scopefit not in ALLOWED_SCOPE_FIT:
                errors.append(f"{label}: invalid Decision Tests scope-fit `{scopefit}`")
            if resolutionvalue not in ALLOWED_RESOLUTION_VALUE:
                errors.append(f"{label}: invalid Decision Tests resolution value `{resolutionvalue}`")
            if nochangedefeated not in ALLOWED_NO_CHANGE_DEFEATED:
                errors.append(f"{label}: invalid Decision Tests no-change defeated `{nochangedefeated}`")
            if is_empty(decision.get("minevidence", "")):
                errors.append(f"{label}: missing minimum evidence to change mind")

        if disposition == "act":
            act_count += 1
            if nochange != "defeated":
                errors.append(f"{label}: `act` requires no-change status `defeated`")
            if concern not in {"valid", "partial"}:
                errors.append(f"{label}: `act` requires concern validity `valid` or `partial`")
            if relevance in {"stale-or-superseded", "unsupported", "out-of-scope", "preference-only"}:
                errors.append(f"{label}: `act` conflicts with relevance `{relevance}`")
            if evidence_grade not in ACTION_EVIDENCE_GRADES:
                errors.append(f"{label}: `act` requires current evidence grade, got `{evidence_grade}`")
            if not evidence_ref_is_concrete(evidence_ref):
                errors.append(f"{label}: `act` requires concrete evidence ref")
            if proposed == "validation-only":
                errors.append(f"{label}: `act` cannot use proposed-fix validity `validation-only`")
            if decision:
                if norm_value(decision.get("grounded", "")) != "yes":
                    errors.append(f"{label}: `act` requires Decision Tests grounded=yes")
                if norm_value(decision.get("material", "")) not in {"yes", "user-requested"}:
                    errors.append(f"{label}: `act` requires Decision Tests material=yes or user-requested")
                if norm_value(decision.get("fresh", "")) != "current":
                    errors.append(f"{label}: `act` requires Decision Tests fresh=current")
                if norm_value(decision.get("diagnosis", "")) not in {"correct", "partially-correct"}:
                    errors.append(f"{label}: `act` requires diagnosis correct or partially-correct")
                if norm_value(decision.get("scopefit", "")) != "yes":
                    errors.append(f"{label}: `act` requires scope-fit=yes")
                if norm_value(decision.get("resolutionvalue", "")) not in {"merge-blocking", "correctness-critical", "review-closure"}:
                    errors.append(f"{label}: `act` requires resolution value merge-blocking, correctness-critical, or review-closure")
                if norm_value(decision.get("nochangedefeated", "")) != "yes":
                    errors.append(f"{label}: `act` requires no-change defeated=yes")
            if proposed in {"wrong-fix", "overbroad", "under-specified", "not-applicable"}:
                if handoff not in IMPLEMENTATION_HANDOFFS:
                    errors.append(f"{label}: invalid proposed fix requires explicit replacement/invariant handoff")
                warnings.append(f"{label}: proposed fix is `{proposed}`; verify replacement fix shape")
        elif disposition in ALLOWED_DISPOSITION:
            non_action_count += 1

        if proposed == "validation-only":
            validation_count += 1
            if disposition != "need-evidence":
                errors.append(f"{label}: proposed-fix validity `validation-only` requires disposition `need-evidence`")
            if handoff != "route-to-fixed-point-driver":
                errors.append(f"{label}: validation-only requires handoff `route-to-fixed-point-driver`")
        if disposition == "need-evidence":
            validation_count += 1
            if handoff == "route-to-accretive-implementer":
                errors.append(f"{label}: `need-evidence` cannot route directly to accretive-implementer")
            if nochange == "defeated":
                warnings.append(f"{label}: `need-evidence` usually should not have no-change status `defeated`")
        if disposition == "rebut":
            reply_count += 1
            if handoff in IMPLEMENTATION_HANDOFFS:
                errors.append(f"{label}: `rebut` cannot route to implementation handoff `{handoff}`")
        if disposition == "defer":
            reply_count += 1
            if handoff == "route-to-accretive-implementer":
                errors.append(f"{label}: `defer` cannot route directly to accretive-implementer")

    resolve_headers, resolve_raw_rows = extract_first_table(section_text(text, "Resolve Selection"))
    resolve_header_map, resolve_rows = normalize_rows(resolve_headers, resolve_raw_rows, RESOLVE_ALIASES)
    missing_resolve_columns = [field for field in REQUIRED_RESOLVE_FIELDS if field not in resolve_header_map]
    if missing_resolve_columns:
        errors.append("Resolve Selection missing required columns: " + ", ".join(missing_resolve_columns))
    if not resolve_rows:
        errors.append("Resolve Selection has no data rows")
    resolve_by_id = rows_by_id(resolve_rows)
    ledger_id_set = set(ledger_ids)
    resolve_id_set = set(resolve_by_id)
    if sorted(ledger_id_set - resolve_id_set):
        errors.append("Resolve Selection missing comment ids: " + ", ".join(sorted(ledger_id_set - resolve_id_set)))
    if sorted(resolve_id_set - ledger_id_set):
        errors.append("Resolve Selection contains unknown comment ids: " + ", ".join(sorted(resolve_id_set - ledger_id_set)))

    decision_buckets = {"address": [], "validate-only": [], "resolve-thread-only": [], "do-not-address": [], "blocked": []}
    for idx, resolve in enumerate(resolve_rows, start=1):
        label = resolve.get("id", f"resolve row {idx}") or f"resolve row {idx}"
        decision_value = norm_value(resolve.get("decision", ""))
        reason = resolve.get("reason", "")
        proof_ref = resolve.get("proofref", "")
        next_action = resolve.get("next", "")
        route_rationale = norm_value(resolve.get("routerationale", ""))
        if decision_value not in ALLOWED_RESOLVE_DECISION:
            errors.append(f"{label}: invalid resolve decision `{resolve.get('decision', '')}`")
        else:
            decision_buckets[decision_value].append(label)
        if route_rationale not in ALLOWED_ROUTE_RATIONALE:
            errors.append(f"{label}: invalid route rationale `{resolve.get('routerationale', '')}`")
        if is_empty(reason):
            errors.append(f"{label}: Resolve Selection requires non-empty reason")
        if decision_value == "blocked":
            if not evidence_ref_is_concrete(proof_ref, allow_missing=True):
                errors.append(f"{label}: blocked selection requires proof ref or explicit missing marker")
        elif not evidence_ref_is_concrete(proof_ref):
            errors.append(f"{label}: Resolve Selection requires concrete proof ref")
        if is_empty(next_action) and decision_value != "do-not-address":
            errors.append(f"{label}: Resolve Selection requires non-empty next action")
        ledger_row = ledger_by_id.get(label)
        if not ledger_row:
            continue
        disposition = norm_value(ledger_row.get("disposition", ""))
        nochange = norm_value(ledger_row.get("nochange", ""))
        handoff = norm_value(ledger_row.get("handoff", ""))
        if decision_value == "address":
            if disposition != "act":
                errors.append(f"{label}: resolve decision `address` requires disposition `act`")
            if nochange != "defeated":
                errors.append(f"{label}: resolve decision `address` requires defeated no-change case")
            if route_rationale == "narrow-local":
                if handoff == "route-to-fixed-point-driver" or "fixed-point-driver" in norm_value(next_action):
                    errors.append(f"{label}: narrow-local address must not route to fixed-point-driver")
            elif route_rationale not in FIXED_POINT_RATIONALES:
                errors.append(f"{label}: address route rationale must be narrow-local or fixed-point rationale")
        elif decision_value == "validate-only":
            if disposition != "need-evidence":
                errors.append(f"{label}: resolve decision `validate-only` requires disposition `need-evidence`")
            if route_rationale != "validation-only":
                errors.append(f"{label}: validate-only requires route rationale `validation-only`")
            if handoff != "route-to-fixed-point-driver":
                errors.append(f"{label}: validate-only requires route-to-fixed-point-driver handoff")
        elif decision_value == "resolve-thread-only":
            if disposition == "act":
                errors.append(f"{label}: resolve-thread-only conflicts with disposition `act`")
            if route_rationale != "proof-only-thread":
                errors.append(f"{label}: resolve-thread-only requires route rationale `proof-only-thread`")
            if handoff in IMPLEMENTATION_HANDOFFS:
                errors.append(f"{label}: resolve-thread-only cannot use implementation handoff `{handoff}`")
        elif decision_value == "do-not-address":
            if disposition == "act":
                errors.append(f"{label}: do-not-address conflicts with disposition `act`")
            if route_rationale != "no-change":
                errors.append(f"{label}: do-not-address requires route rationale `no-change`")
            if norm_value(next_action) not in {"none", "", "no", "n/a", "na"} and "reply" not in norm_value(next_action):
                warnings.append(f"{label}: do-not-address usually uses next=none or proof/reply-only")
        elif decision_value == "blocked":
            if route_rationale != "blocked":
                errors.append(f"{label}: blocked requires route rationale `blocked`")

    handoff_buckets = parse_handoff_agenda(section_text(text, "Handoff Agenda"), ledger_ids, errors)
    expected = {
        "implementation": sorted(decision_buckets["address"]),
        "validation": sorted(decision_buckets["validate-only"]),
        "proofonly": sorted(decision_buckets["resolve-thread-only"]),
        "notselected": sorted(decision_buckets["do-not-address"]),
        "blocked": sorted(decision_buckets["blocked"]),
    }
    for bucket, expected_ids in expected.items():
        got_ids = sorted(handoff_buckets.get(bucket, []))
        if got_ids != expected_ids:
            errors.append(f"Handoff Agenda `{bucket}` mismatch: expected {expected_ids}, got {got_ids}")

    warrant_result = validate_resolution_warrants(
        text, ledger_by_id, resolve_by_id, handoff_buckets, errors, warnings,
        changed_files=changed_files, resolved_threads=resolved_threads,
    )
    warrant_action_buckets = warrant_result.get("action_buckets", {}) if isinstance(warrant_result, dict) else {}
    surface_budget_result = validate_surface_budget_ledger(
        text,
        warrant_result.get("rows", []) if isinstance(warrant_result, dict) else [],
        errors,
        warnings,
        diffstat=diffstat,
        new_public_symbols=new_public_symbols,
        new_files=new_files,
        new_helpers=new_helpers,
        new_flags_or_knobs=new_flags_or_knobs,
    )

    gate_headers, gate_rows_raw = extract_first_table(section_text(text, "Adjudication Gate"))
    gate = normalize_gate(gate_headers, gate_rows_raw)
    missing_gate = [field for field in REQUIRED_GATE_FIELDS if field not in gate]
    if missing_gate:
        errors.append("Adjudication Gate missing required fields: " + ", ".join(missing_gate))

    for field_name in REQUIRED_GATE_FIELDS:
        if field_name not in gate:
            continue
        value = gate[field_name]
        if field_name in {"implementationhandoffallowed", "validationhandoffallowed", "replyhandoffallowed"}:
            if value not in {"yes", "no"}:
                errors.append(f"{field_name} must be yes/no, got `{value}`")
        elif field_name == "specialistpacketcoverage":
            if value not in {"pass", "fail", "not-used"}:
                errors.append(f"specialist_packet_coverage must be pass/fail/not-used, got `{value}`")
        elif value not in {"pass", "fail"}:
            errors.append(f"{field_name} must be pass/fail, got `{value}`")

    gate_failures = [
        field for field in REQUIRED_GATE_FIELDS
        if field not in {"implementationhandoffallowed", "validationhandoffallowed", "replyhandoffallowed"}
        and gate.get(field) == "fail"
    ]
    if gate_failures and gate.get("adjudicationcomplete") == "pass":
        errors.append("adjudication_complete is pass despite failed gate fields: " + ", ".join(gate_failures))
    if errors and gate.get("adjudicationcomplete") == "pass":
        errors.append("adjudication_complete is pass despite mechanical contract errors")
    if errors and gate.get("implementationhandoffallowed") == "yes":
        errors.append("implementation_handoff_allowed is yes despite mechanical contract errors")
    if gate.get("implementationhandoffallowed") == "yes" and not decision_buckets["address"]:
        errors.append("implementation_handoff_allowed is yes but no Resolve Selection row is `address`")
    if gate.get("implementationhandoffallowed") == "yes" and not warrant_action_buckets.get("mutate-code"):
        errors.append("implementation_handoff_allowed is yes but no mutate-code Resolution Warrant exists")
    if decision_buckets["blocked"] and gate.get("adjudicationcomplete") == "pass":
        errors.append("Resolve Selection has blocked rows but adjudication_complete is pass")
    if decision_buckets["blocked"] and any(gate.get(field) == "yes" for field in ["implementationhandoffallowed", "validationhandoffallowed", "replyhandoffallowed"]):
        errors.append("Resolve Selection has blocked rows but a handoff permission is yes")

    if rows and act_count == len(rows):
        validate_structured_table(text, "All-Action Justification", ALL_ACTION_CHECKS, errors, "why action still warranted")
    if rows and len(decision_buckets["address"]) + len(decision_buckets["validate-only"]) == len(rows):
        validate_structured_table(text, "All-Selected Justification", ALL_SELECTED_CHECKS, errors, "why selected resolution is still warranted")

    validate_specialist_receipts(text, gate, errors)

    if not section_text(text, "Acceptance Skew Audit").strip():
        errors.append("Acceptance Skew Audit is empty")
    if not section_text(text, "Selection Skew Audit").strip():
        errors.append("Selection Skew Audit is empty")

    bottom_line = section_text(text, "Adjudication Bottom Line")
    if (gate_failures or errors) and "blocked" not in bottom_line.lower():
        errors.append("failed gate or mechanical error requires blocked Adjudication Bottom Line")

    stats = {
        "comments": len(rows),
        "act": act_count,
        "non_action": non_action_count,
        "validation_or_need_evidence": validation_count,
        "reply_rows": reply_count,
        "resolve_address": len(decision_buckets["address"]),
        "resolve_validate_only": len(decision_buckets["validate-only"]),
        "resolve_thread_only": len(decision_buckets["resolve-thread-only"]),
        "resolve_do_not_address": len(decision_buckets["do-not-address"]),
        "resolve_blocked": len(decision_buckets["blocked"]),
        "warrants": len(warrant_result.get("rows", [])) if isinstance(warrant_result, dict) else 0,
        "surface_budget_rows": len(surface_budget_result.get("rows", [])) if isinstance(surface_budget_result, dict) else 0,
        "surface_budget_max_positive_loc": int(surface_budget_result.get("total_max_positive_loc", 0)) if isinstance(surface_budget_result, dict) else 0,
        "diffstat_net": int(surface_budget_result.get("diffstat_net", 0)) if isinstance(surface_budget_result, dict) else 0,
        "mutate_warrants": len(warrant_action_buckets.get("mutate-code", [])) if isinstance(warrant_action_buckets, dict) else 0,
        "validation_warrants": len(warrant_action_buckets.get("add-validation-only", [])) if isinstance(warrant_action_buckets, dict) else 0,
        "thread_resolution_warrants": len(warrant_action_buckets.get("resolve-thread", [])) if isinstance(warrant_action_buckets, dict) else 0,
        "duplicate_ledger_ids": len(duplicate_ledger_ids),
        "errors": len(errors),
        "warnings": len(warnings),
    }
    return CheckResult(passed=not errors, errors=errors, warnings=warnings, stats=stats, gate=gate)


def print_human(result: CheckResult) -> None:
    if result.passed:
        print("PASS: Surface-Budgeted v5 adjudication gate contract satisfied")
    else:
        print("FAIL: Surface-Budgeted v5 adjudication gate contract incomplete")
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


def valid_fixture() -> str:
    return """
## Review Basis

artifact_state_id:
  branch: feature/retry
  base: main@abc123
  head: feature@def456
  diff_digest: paths=src/a.py,tests/test_a.py
  comment_set_digest: c1,c2,c3
  ci_state: local tests pass 2026-05-26

- branch / PR: feature/retry
- current artifact evidence: src/a.py and tests/test_a.py
- tests / CI: local pytest pass
- comments adjudicated: 3
- limits / unavailable evidence: none

## Comment Inventory

- input_comment_count: 3
- ledger_row_count: 3
- input_comment_ids: c1,c2,c3
- ledger_comment_ids: c1,c2,c3
- missing_comment_ids: []
- duplicate_comment_ids: []
- synthesized_ids_for_real_comments: no

## PR Why Ledger

- intended_change: make retry idempotent
- explicit_constraints: narrow change
- non_goals: public API rename
- governing_invariants: retry idempotence
- evidence_source: PR body
- rationale_freshness: current
- staleness_source: none
- confidence: high

## Comment Ledger

| id/thread | reviewer | location | excerpt | claim | concern validity | proposed fix validity | relevance | disposition | no-change status | invariant | evidence grade | evidence ref | handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1 | alice | src/a.py:10 | retry writes twice | retry path is not idempotent | valid | valid | material-relevant | act | defeated | retry idempotence | current-artifact | src/a.py:10 | route-to-accretive-implementer |
| c2 | bob | src/a.py:12 | maybe flakes | flake risk needs proof | unknown | validation-only | material-relevant | need-evidence | unresolved | retry idempotence | reviewer-only | thread:c2 | route-to-fixed-point-driver |
| c3 | cara | src/a.py:1 | rename helper | helper name should change | unsupported | not-applicable | preference-only | rebut | not-defeated | none | current-artifact | src/a.py:1 | none |

## Decision Tests

| id/thread | grounded | material | fresh | diagnosis | scope-fit | resolution value | no-change defeated | min evidence to change mind |
|---|---|---|---|---|---|---|---|---|
| c1 | yes | yes | current | correct | yes | correctness-critical | yes | counterexample test showing no duplicate write |
| c2 | unknown | yes | current | unknown | yes | validation-needed | unresolved | repro or failing test for flake |
| c3 | no | no | current | unknown | no | low-value | no | repo naming convention or user goal |

## No-Change Countercases

- c1:
  - strongest no-change case: maybe existing guard handles duplicate writes.
  - status: defeated
  - why defeated / preserved / unresolved: src/a.py:10 lacks guard.
- c2:
  - strongest no-change case: flake is unproven.
  - status: unresolved
  - why defeated / preserved / unresolved: validation needed.
- c3:
  - strongest no-change case: rename is preference-only.
  - status: not-defeated
  - why defeated / preserved / unresolved: no convention supplied.

## Governing Invariant Ledger

| invariant id | invariant | comments | evidence | violated/threatened | minimum fix shape | handoff | why not local fixes |
|---|---|---|---|---|---|---|---|
| inv1 | retry idempotence | c1,c2 | src/a.py:10 | violated | add guard and validation | route-to-fixed-point-driver | coupled proof and implementation |

## Act On

- c1: add the narrow idempotence guard; evidence src/a.py:10.

## Rebut

- c3: rebut as preference-only; no repo convention supplied.

## Defer / Out of Scope

- none.

## Need Evidence

- c2: route validation-only repro/probe to fixed-point-driver.

## Resolve Selection

| id/thread | resolve decision | reason | proof ref | next | route rationale |
|---|---|---|---|---|---|
| c1 | address | act row has defeated no-change case and current artifact evidence | src/a.py:10 | route-to-accretive-implementer | narrow-local |
| c2 | validate-only | reviewer flake claim is unproven and needs validation proof | thread:c2 | route-to-fixed-point-driver | validation-only |
| c3 | do-not-address | preference-only no-change case preserved | src/a.py:1 | none | no-change |

## Resolve Countercases

- c1:
  - proposed resolve decision: address
  - strongest alternative resolve decision: validate-only
  - why alternative is rejected / preserved / unresolved: src/a.py:10 already grounds the defect.
- c2:
  - proposed resolve decision: validate-only
  - strongest alternative resolve decision: address
  - why alternative is rejected / preserved / unresolved: thread:c2 does not prove a failure yet.
- c3:
  - proposed resolve decision: do-not-address
  - strongest alternative resolve decision: address
  - why alternative is rejected / preserved / unresolved: src/a.py:1 shows no convention-backed need.

## Resolution Warrants

| warrant id | claim id | source | claim excerpt | decision | concern validity | proposed fix validity | no-change status | resolution value | route rationale | permitted action | permitted scope | forbidden actions | evidence refs | countercase ref | proof required | expiry |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rw-c1 | c1 | github-review | retry writes twice | address | valid | valid | defeated | correctness-critical | narrow-local | mutate-code | files=src/a.py,tests/test_a.py; symbols=retry guard | mutate outside permitted_scope; resolve unrelated threads | src/a.py:10 | no-change c1 defeated by src/a.py:10 | pytest tests/test_a.py::test_retry_idempotent | invalid when HEAD/base/diff/comment-set changes |
| rw-c2 | c2 | github-review | maybe flakes | validate-only | unknown | validation-only | unresolved | validation-needed | validation-only | add-validation-only | tests/probes for thread:c2 only | production mutation; requested code change | thread:c2 | no-change c2 unresolved pending repro | validation probe for thread:c2 | invalid when HEAD/base/diff/comment-set changes |
| rw-c3 | c3 | github-review | rename helper | do-not-address | unsupported | not-applicable | not-defeated | low-value | no-change | none | none | mutate code; resolve unrelated threads | src/a.py:1 | no-change c3 preserved by missing convention | none | invalid when HEAD/base/diff/comment-set changes |

## Surface Budget Ledger

| warrant id | mode | target net loc | max positive loc | max new public symbols | max new files | max new helpers | max new flags/knobs | max new state variants | max new branches | duplicate path budget | subtractive probes required | expansion warrant required | expansion status | proof required | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rw-c1 | subtractive-first | small-positive | 8 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | yes | yes | not-needed | pytest tests/test_a.py::test_retry_idempotent | try deletion/reuse/refactor first; additive guard is capped |
| rw-c2 | neutral-first | zero | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | no | no | not-needed | validation probe for thread:c2 | validation-only may add tests/probes, not production mutation |
| rw-c3 | neutral-first | zero | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | no | no | not-needed | no proof required | no code surface selected |

## Invariant-Level Handoff

- invariant: retry idempotence
- affected comments: c1,c2
- route: fixed-point-driver only for validation c2 if needed; c1 is narrow-local
- minimum fix shape: guard duplicate write and prove with test
- proof required: pytest tests/test_a.py::test_retry_idempotent

## Acceptance Skew Audit

- disposition distribution: act=1, need-evidence=1, rebut=1
- acceptance pressure checked: mixed dispositions avoid all-action pressure
- stale/superseded possibilities: none current
- unsupported possibilities: c3 unsupported
- preference-only possibilities: c3 preference-only
- out-of-scope possibilities: none
- validation-only alternatives: c2
- shared-invariant pressure: c1/c2 share retry idempotence

## Selection Skew Audit

- resolve decision distribution: address=1, validate-only=1, do-not-address=1
- all-selected pressure checked: not all selected
- address over-selection possibilities: c2 and c3 rejected as address
- validate-only over-routing possibilities: only c2 validation-only
- proof-only thread-resolution alternatives: none already fixed
- do-not-address alternatives: c3
- blocked/ask-user alternatives: none
- fixed-point over-routing pressure: c1 stays narrow-local; c2 validation only

## Adjudication Gate

| field | value | basis |
|---|---|---|
| artifact_state_coverage | pass | artifact_state_id recorded |
| comment_inventory_coverage | pass | all three ids match ledger |
| identity_coverage | pass | all rows have raw identity |
| decision_test_coverage | pass | all rows have decision tests |
| no_change_coverage | pass | all rows have countercases |
| disposition_coverage | pass | all rows have one disposition |
| proposed_fix_separation | pass | concern and fix split |
| evidence_ref_coverage | pass | act has current artifact evidence ref |
| resolve_selection_coverage | pass | every ledger row has valid downstream selection |
| resolve_countercase_coverage | pass | every ledger row has resolve countercase |
| resolution_warrant_coverage | pass | every resolve decision has a matching warrant |
| surface_budget_coverage | pass | every mutate-code warrant has a subtractive-first surface budget |
| surface_budget_consumption_safety | pass | surface budgets constrain downstream diff/symbol growth |
| warrant_consumption_safety | pass | warrant actions match handoff agenda buckets |
| handoff_agenda_consistency | pass | agenda buckets match selection map |
| selection_skew_audit | pass | skew audited |
| invariant_pass | pass | invariant checked and named |
| specialist_packet_coverage | not-used | no specialists used |
| acceptance_skew_audit | pass | skew audited |
| adjudication_complete | pass | all required fields pass |
| implementation_handoff_allowed | yes | c1 is artifact-backed address |
| validation_handoff_allowed | yes | c2 is validation-only |
| reply_handoff_allowed | yes | c3 rebut reply allowed |

## Handoff Agenda

- implementation route: accretive-implementer
- validation route: fixed-point-driver
- proof-only thread-resolution route: none
- reply route: optional logophile
- items selected for implementation: c1
- validation-only items: c2
- proof-only thread-resolution items: none
- items not selected: c3
- proof: pytest tests/test_a.py::test_retry_idempotent
- blocked items: none

## Adjudication Bottom Line

Proceed: one artifact-backed action, one validation-only item, and one rebuttal.
"""


def invalid_fixture() -> str:
    return """
## Review Basis

- branch / PR: feature/retry

## Comment Inventory

- input_comment_count: 2
- ledger_row_count: 1
- input_comment_ids: c1,c2
- ledger_comment_ids: c1
- missing_comment_ids: c2
- duplicate_comment_ids: []
- synthesized_ids_for_real_comments: no

## PR Why Ledger

- intended_change: unknown

## Comment Ledger

| id/thread | reviewer | location | excerpt | claim | concern validity | proposed fix validity | relevance | disposition | no-change status | invariant | evidence grade | evidence ref | handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1 | alice | src/a.py:10 | retry writes twice | retry path is not idempotent | unknown | validation-only | material-relevant | act | unresolved | none | reviewer-only | code | route-to-accretive-implementer |

## Decision Tests

| id/thread | grounded | material | fresh | diagnosis | scope-fit | resolution value | no-change defeated | min evidence to change mind |
|---|---|---|---|---|---|---|---|---|
| c1 | unknown | yes | unclear | unknown | unknown | validation-needed | unresolved | repro |

## No-Change Countercases

- c1: unresolved.

## Governing Invariant Ledger

none.

## Act On

- c1: implement reviewer fix.

## Rebut

none.

## Defer / Out of Scope

none.

## Need Evidence

none.

## Resolve Selection

| id/thread | resolve decision | reason | proof ref | next | route rationale |
|---|---|---|---|---|---|
| c1 | address | all are worth resolving | code | route-to-accretive-implementer | narrow-local |

## Resolve Countercases

- c1: none.

## Invariant-Level Handoff

none.

## Acceptance Skew Audit

all action.

## Selection Skew Audit

all selected.

## Adjudication Gate

| field | value | basis |
|---|---|---|
| artifact_state_coverage | fail | missing |
| comment_inventory_coverage | fail | dropped c2 |
| identity_coverage | pass | c1 only |
| decision_test_coverage | fail | incomplete |
| no_change_coverage | fail | unresolved |
| disposition_coverage | pass | one row |
| proposed_fix_separation | pass | split |
| evidence_ref_coverage | fail | no current evidence |
| resolve_selection_coverage | fail | invalid address |
| resolve_countercase_coverage | fail | generic |
| resolution_warrant_coverage | fail | missing warrants |
| warrant_consumption_safety | fail | no consumption safety |
| handoff_agenda_consistency | fail | missing agenda |
| selection_skew_audit | fail | generic |
| invariant_pass | fail | not checked |
| specialist_packet_coverage | not-used | no specialists |
| acceptance_skew_audit | fail | generic |
| adjudication_complete | fail | incomplete |
| implementation_handoff_allowed | no | blocked |
| validation_handoff_allowed | no | blocked |
| reply_handoff_allowed | no | blocked |

## Handoff Agenda

- items selected for implementation: all
- validation-only items: none
- proof-only thread-resolution items: none
- items not selected: none
- blocked items: none

## Adjudication Bottom Line

Blocked: incomplete adjudication. Do not implement yet.
"""


def run_self_test() -> int:
    good = check_adjudication(valid_fixture())
    bad = check_adjudication(invalid_fixture())
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
    parser.add_argument("--changed-files", help="optional comma-separated changed files to check against mutate-code warrant scope")
    parser.add_argument("--resolved-threads", help="optional comma-separated resolved thread ids to check against thread/action warrants")
    parser.add_argument("--diffstat", default="", help="optional git diff --stat summary for surface budget checking")
    parser.add_argument("--new-public-symbols", type=int, default=0, help="number of new public symbols for surface budget checking")
    parser.add_argument("--new-files", type=int, default=0, help="number of new files for surface budget checking")
    parser.add_argument("--new-helpers", type=int, default=0, help="number of new helpers/functions for surface budget checking")
    parser.add_argument("--new-flags-or-knobs", type=int, default=0, help="number of new flags/config knobs for surface budget checking")
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
    changed_files = parse_id_list(args.changed_files or "")
    resolved_threads = parse_id_list(args.resolved_threads or "")
    result = check_adjudication(
        text,
        changed_files=changed_files,
        resolved_threads=resolved_threads,
        diffstat=args.diffstat,
        new_public_symbols=args.new_public_symbols,
        new_files=args.new_files,
        new_helpers=args.new_helpers,
        new_flags_or_knobs=args.new_flags_or_knobs,
    )
    if args.json:
        print(result.to_json())
    else:
        print_human(result)
    return 0 if result.passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
