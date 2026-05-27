#!/usr/bin/env python3
"""Mechanical contract checker for Compact-Gated v4 review-adjudication outputs.

The checker validates output shape, stale-proofing fields, direction-state
obligations, P2+ severity anti-laundering, evidence-reference obligations,
resolve-selection anti-laundering, validation-value gating, and downstream
handoff safety. It cannot prove semantic correctness, but it blocks incomplete,
direction-conflicting, severity-laundered, or over-selected adjudications before
implementation routing.
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
    "direction-conflicting",
    "review-closure-only",
}
ALLOWED_DISPOSITION = {"act", "rebut", "defer", "need-evidence", "blocked"}
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
    "direction-critical",
    "review-closure",
    "proof-only",
    "validation-needed",
    "low-value",
    "out-of-lane",
    "blocked",
}
IMPLEMENTATION_RESOLUTION_VALUES = {
    "merge-blocking",
    "correctness-critical",
    "direction-critical",
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
ALLOWED_SEVERITY = {"p0", "p1", "p2", "p3", "p4", "unlabeled", "unknown"}
P2_PLUS = {"p0", "p1", "p2"}
ALLOWED_CRITICALITY = {
    "blocker",
    "security-critical",
    "safety-critical",
    "data-loss-critical",
    "correctness-critical",
    "compatibility-critical",
    "direction-critical",
    "review-closure-only",
    "low-value",
    "out-of-lane",
    "unknown",
}
IMPLEMENTATION_CRITICALITY = {
    "blocker",
    "security-critical",
    "safety-critical",
    "data-loss-critical",
    "correctness-critical",
    "compatibility-critical",
    "direction-critical",
}
ALLOWED_SEVERITY_STATUS = {"accepted", "downgraded", "rejected", "unresolved"}
ALLOWED_DIRECTION_SOURCE = {
    "user-current-instruction",
    "proposed-plan",
    "st-plan",
    "update-plan",
    "pr-body",
    "issue",
    "design-doc",
    "repo-convention",
    "seq-recovered",
    "current-artifact",
    "unknown",
}
ALLOWED_SOURCE_FRESHNESS = {"current", "stale", "off-target", "unknown"}
ALLOWED_SAME_OBJECTIVE = {"yes", "no", "unknown"}
ALLOWED_DIRECTION_FIT = {"aligned", "direction-overriding", "neutral", "conflicting", "unknown"}
ACT_DIRECTION_FIT = {"aligned", "direction-overriding"}
ALLOWED_DIRECTION_OVERRIDE = {"yes", "no", "not-needed", "unknown"}
ALLOWED_MUTATION_VALUE = {
    "codebase-material",
    "validation-material",
    "proof-only",
    "reply-only",
    "no-change",
    "blocked",
}
ALLOWED_P2_ACCEPTED = {"yes", "no", "not-p2plus"}

REQUIRED_LEDGER_FIELDS = [
    "id",
    "reviewer",
    "location",
    "excerpt",
    "claim",
    "severity",
    "criticality",
    "severitystatus",
    "directionfit",
    "directionref",
    "mutationvalue",
    "concern",
    "proposed",
    "relevance",
    "disposition",
    "nochange",
    "invariant",
    "evidencegrade",
    "evidenceref",
    "severityproofref",
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
REQUIRED_DIRECTION_FIELDS = [
    "id",
    "directionsource",
    "sourcefreshness",
    "sameobjective",
    "directionfit",
    "directionref",
    "activefrontier",
    "nongoalconflict",
    "directionoverride",
    "minevidencedirection",
]
REQUIRED_SEVERITY_FIELDS = [
    "id",
    "severity",
    "criticality",
    "severitystatus",
    "severityproofref",
    "downgradereason",
    "p2accepted",
    "minevidenceseverity",
]
REQUIRED_RESOLVE_FIELDS = [
    "id",
    "decision",
    "reason",
    "proofref",
    "next",
    "routerationale",
]
REQUIRED_GATE_FIELDS = [
    "artifactstatecoverage",
    "directioncontextcoverage",
    "commentinventorycoverage",
    "identitycoverage",
    "decisiontestcoverage",
    "directionfitcoverage",
    "severityclaimcoverage",
    "p2plusacceptancecoverage",
    "nochangecoverage",
    "dispositioncoverage",
    "proposedfixseparation",
    "evidencerefcoverage",
    "validationvaluecoverage",
    "resolveselectioncoverage",
    "resolvecountercasecoverage",
    "handoffagendaconsistency",
    "selectionskewaudit",
    "p2plusseverityaudit",
    "directionfitaudit",
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
    "Direction Context Ledger",
    "Comment Inventory",
    "PR Why Ledger",
    "Comment Ledger",
    "Decision Tests",
    "Direction Tests",
    "Severity Tests",
    "No-Change Countercases",
    "Governing Invariant Ledger",
    "Act On",
    "Rebut",
    "Defer / Out of Scope",
    "Need Evidence",
    "Resolve Selection",
    "Resolve Countercases",
    "Invariant-Level Handoff",
    "Acceptance Skew Audit",
    "P2+ Severity Audit",
    "Direction Fit Audit",
    "Selection Skew Audit",
    "Adjudication Gate",
    "Handoff Agenda",
    "Adjudication Bottom Line",
]
OPTIONAL_SINGLETON_SECTIONS = {
    "All-Action Justification",
    "All-Selected Justification",
    "All-P2+ Accepted Justification",
    "Specialist Packet Receipts",
}
ALL_ACTION_CHECKS = {
    "stalesuperseded": "stale/superseded",
    "unsupported": "unsupported",
    "preferenceonly": "preference-only",
    "outofscope": "out-of-scope",
    "directionconflicting": "direction-conflicting",
    "reviewclosureonly": "review-closure-only",
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
    "directionconflictalternative": "direction-conflict alternative",
    "reviewclosureonlyalternative": "review-closure-only alternative",
    "fixedpointoverroutingcheck": "fixed-point over-routing check",
}
ALL_P2_ACCEPTED_CHECKS = {
    "independentartifactproof": "independent artifact proof",
    "implementationgradecriticality": "implementation-grade criticality",
    "directionalignment": "direction alignment",
    "reviewclosureonlyrejection": "review-closure-only rejection",
    "downgradealternative": "downgrade alternative",
    "validationalternative": "validation alternative",
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
    "reviewerseverityclaim": "severity",
    "severityclaim": "severity",
    "severity": "severity",
    "acceptedcriticality": "criticality",
    "criticality": "criticality",
    "severityacceptancestatus": "severitystatus",
    "severitystatus": "severitystatus",
    "directionfit": "directionfit",
    "direction": "directionfit",
    "directionref": "directionref",
    "planref": "directionref",
    "mutationvalue": "mutationvalue",
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
    "severityproofref": "severityproofref",
    "severityproof": "severityproofref",
    "criticalityproofref": "severityproofref",
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

DIRECTION_ALIASES = {
    "idthread": "id",
    "id": "id",
    "commentid": "id",
    "threadid": "id",
    "directionsource": "directionsource",
    "source": "directionsource",
    "sourcefreshness": "sourcefreshness",
    "directionsourcefreshness": "sourcefreshness",
    "sameobjective": "sameobjective",
    "directionfit": "directionfit",
    "direction": "directionfit",
    "directionref": "directionref",
    "source_ref": "directionref",
    "planref": "directionref",
    "activefrontier": "activefrontier",
    "frontier": "activefrontier",
    "nongoalconflict": "nongoalconflict",
    "nongoalsconflict": "nongoalconflict",
    "directionoverride": "directionoverride",
    "override": "directionoverride",
    "minevidencetochangedirection": "minevidencedirection",
    "minimumevidencetochangedirection": "minevidencedirection",
    "minevidencedirection": "minevidencedirection",
}

SEVERITY_ALIASES = {
    "idthread": "id",
    "id": "id",
    "commentid": "id",
    "threadid": "id",
    "reviewerseverityclaim": "severity",
    "severityclaim": "severity",
    "severity": "severity",
    "acceptedcriticality": "criticality",
    "criticality": "criticality",
    "severityacceptancestatus": "severitystatus",
    "severitystatus": "severitystatus",
    "severityproofref": "severityproofref",
    "severityproof": "severityproofref",
    "criticalityproofref": "severityproofref",
    "downgraderejectreason": "downgradereason",
    "downgradereason": "downgradereason",
    "rejectreason": "downgradereason",
    "p2accepted": "p2accepted",
    "p2plusaccepted": "p2accepted",
    "p2acceptedstatus": "p2accepted",
    "minevidencetoacceptseverity": "minevidenceseverity",
    "minimumevidencetoacceptseverity": "minevidenceseverity",
    "minevidenceseverity": "minevidenceseverity",
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

GATE_ALIASES = {
    "artifactstatecoverage": "artifactstatecoverage",
    "artifactcoverage": "artifactstatecoverage",
    "directioncontextcoverage": "directioncontextcoverage",
    "directioncoverage": "directioncontextcoverage",
    "commentinventorycoverage": "commentinventorycoverage",
    "inventorycoverage": "commentinventorycoverage",
    "identitycoverage": "identitycoverage",
    "decisiontestcoverage": "decisiontestcoverage",
    "decisiontestscoverage": "decisiontestcoverage",
    "directionfitcoverage": "directionfitcoverage",
    "directiontestcoverage": "directionfitcoverage",
    "severityclaimcoverage": "severityclaimcoverage",
    "severitycoverage": "severityclaimcoverage",
    "p2plusacceptancecoverage": "p2plusacceptancecoverage",
    "p2acceptancecoverage": "p2plusacceptancecoverage",
    "nochangecoverage": "nochangecoverage",
    "dispositioncoverage": "dispositioncoverage",
    "proposedfixseparation": "proposedfixseparation",
    "fixseparation": "proposedfixseparation",
    "evidencerefcoverage": "evidencerefcoverage",
    "evidencecoverage": "evidencerefcoverage",
    "validationvaluecoverage": "validationvaluecoverage",
    "validationcoverage": "validationvaluecoverage",
    "resolveselectioncoverage": "resolveselectioncoverage",
    "resolvecoverage": "resolveselectioncoverage",
    "selectioncoverage": "resolveselectioncoverage",
    "resolvecountercasecoverage": "resolvecountercasecoverage",
    "resolvecountercasescoverage": "resolvecountercasecoverage",
    "handoffagendaconsistency": "handoffagendaconsistency",
    "agendaconsistency": "handoffagendaconsistency",
    "selectionskewaudit": "selectionskewaudit",
    "selectionaudit": "selectionskewaudit",
    "p2plusseverityaudit": "p2plusseverityaudit",
    "p2severityaudit": "p2plusseverityaudit",
    "directionfitaudit": "directionfitaudit",
    "directionaudit": "directionfitaudit",
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


def parse_kv_block(block: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for line in block.splitlines():
        stripped = re.sub(r"^[-*]\s+", "", line.strip())
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        out[norm_key(key)] = value.strip()
    return out


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
    if any(token in normalized for token in ["test", "ci", "cmd", "command", "log", "thread", "pr#", "gh-", "github", "diff", "src/", "tests/", "commit", "plan", "st-", "issue", "design", "proposed-plan"]):
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
        required = {"role", "packetstatus", "artifactstatematch", "directionstatematch", "scopematch", "findingadded", "routechanged", "usedfor", "reason"}
        missing = sorted(required - header_keys)
        if missing:
            errors.append("Specialist Packet Receipts missing required columns: " + ", ".join(missing))
        if not rows:
            errors.append("Specialist Packet Receipts has no data rows")


def check_adjudication(text: str) -> CheckResult:
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

    direction_context = section_text(text, "Direction Context Ledger")
    if "direction_state_id" not in direction_context:
        errors.append("Direction Context Ledger missing direction_state_id block")
    else:
        for key in ["source", "source_ref", "source_freshness", "same_objective", "active_frontier", "locked_decisions", "non_goals", "compatibility_posture", "ownership_boundaries", "direction_confidence"]:
            if not re.search(rf"(?im)^\s*{re.escape(key)}\s*:", direction_context):
                errors.append(f"direction_state_id missing `{key}`")

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

    direction_headers, direction_raw_rows = extract_first_table(section_text(text, "Direction Tests"))
    direction_header_map, direction_rows = normalize_rows(direction_headers, direction_raw_rows, DIRECTION_ALIASES)
    missing_direction_columns = [field for field in REQUIRED_DIRECTION_FIELDS if field not in direction_header_map]
    if missing_direction_columns:
        errors.append("Direction Tests missing required columns: " + ", ".join(missing_direction_columns))
    if not direction_rows:
        errors.append("Direction Tests has no data rows")
    directions = rows_by_id(direction_rows)

    severity_headers, severity_raw_rows = extract_first_table(section_text(text, "Severity Tests"))
    severity_header_map, severity_rows = normalize_rows(severity_headers, severity_raw_rows, SEVERITY_ALIASES)
    missing_severity_columns = [field for field in REQUIRED_SEVERITY_FIELDS if field not in severity_header_map]
    if missing_severity_columns:
        errors.append("Severity Tests missing required columns: " + ", ".join(missing_severity_columns))
    if not severity_rows:
        errors.append("Severity Tests has no data rows")
    severities = rows_by_id(severity_rows)

    act_count = validation_count = reply_count = blocked_count = p2_count = p2_accepted_count = 0
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
        severity = norm_value(row.get("severity", ""))
        criticality = norm_value(row.get("criticality", ""))
        severity_status = norm_value(row.get("severitystatus", ""))
        severity_proof_ref = row.get("severityproofref", "")
        direction_fit = norm_value(row.get("directionfit", ""))
        direction_ref = row.get("directionref", "")
        mutation_value = norm_value(row.get("mutationvalue", ""))

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
        if severity not in ALLOWED_SEVERITY:
            errors.append(f"{label}: invalid reviewer severity claim `{row.get('severity', '')}`")
        if criticality not in ALLOWED_CRITICALITY:
            errors.append(f"{label}: invalid accepted criticality `{row.get('criticality', '')}`")
        if severity_status not in ALLOWED_SEVERITY_STATUS:
            errors.append(f"{label}: invalid severity acceptance status `{row.get('severitystatus', '')}`")
        if direction_fit not in ALLOWED_DIRECTION_FIT:
            errors.append(f"{label}: invalid direction fit `{row.get('directionfit', '')}`")
        if mutation_value not in ALLOWED_MUTATION_VALUE:
            errors.append(f"{label}: invalid mutation value `{row.get('mutationvalue', '')}`")

        decision = decisions.get(label)
        if not decision:
            errors.append(f"{label}: missing Decision Tests row")
            resolutionvalue = ""
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

        direction = directions.get(label)
        if not direction:
            errors.append(f"{label}: missing Direction Tests row")
        else:
            direction_source = norm_value(direction.get("directionsource", ""))
            source_freshness = norm_value(direction.get("sourcefreshness", ""))
            same_objective = norm_value(direction.get("sameobjective", ""))
            direction_row_fit = norm_value(direction.get("directionfit", ""))
            direction_row_ref = direction.get("directionref", "")
            non_goal_conflict = norm_value(direction.get("nongoalconflict", ""))
            direction_override = norm_value(direction.get("directionoverride", ""))
            if direction_source not in ALLOWED_DIRECTION_SOURCE:
                errors.append(f"{label}: invalid Direction Tests source `{direction_source}`")
            if source_freshness not in ALLOWED_SOURCE_FRESHNESS:
                errors.append(f"{label}: invalid Direction Tests source freshness `{source_freshness}`")
            if same_objective not in ALLOWED_SAME_OBJECTIVE:
                errors.append(f"{label}: invalid Direction Tests same objective `{same_objective}`")
            if direction_row_fit not in ALLOWED_DIRECTION_FIT:
                errors.append(f"{label}: invalid Direction Tests direction fit `{direction_row_fit}`")
            if direction_row_fit != direction_fit:
                errors.append(f"{label}: ledger direction fit `{direction_fit}` does not match Direction Tests `{direction_row_fit}`")
            if direction_row_ref != direction_ref:
                warnings.append(f"{label}: ledger direction ref differs from Direction Tests direction ref")
            if non_goal_conflict not in {"yes", "no", "unknown"}:
                errors.append(f"{label}: invalid Direction Tests non-goal conflict `{non_goal_conflict}`")
            if direction_override not in ALLOWED_DIRECTION_OVERRIDE:
                errors.append(f"{label}: invalid Direction Tests direction override `{direction_override}`")
            if is_empty(direction.get("minevidencedirection", "")):
                errors.append(f"{label}: missing minimum evidence to change direction")
            if direction_fit == "aligned" and (source_freshness != "current" or same_objective != "yes"):
                errors.append(f"{label}: aligned direction requires source_freshness=current and same_objective=yes")
            if direction_fit == "direction-overriding" and direction_override != "yes":
                errors.append(f"{label}: direction-overriding requires direction override=yes")
            if direction_fit == "conflicting" and non_goal_conflict == "no":
                warnings.append(f"{label}: direction-conflicting row has non-goal conflict=no; verify direction conflict basis")

        severity_row = severities.get(label)
        if not severity_row:
            errors.append(f"{label}: missing Severity Tests row")
        else:
            severity_row_claim = norm_value(severity_row.get("severity", ""))
            severity_row_criticality = norm_value(severity_row.get("criticality", ""))
            severity_row_status = norm_value(severity_row.get("severitystatus", ""))
            p2accepted = norm_value(severity_row.get("p2accepted", ""))
            if severity_row_claim not in ALLOWED_SEVERITY:
                errors.append(f"{label}: invalid Severity Tests severity `{severity_row_claim}`")
            if severity_row_criticality not in ALLOWED_CRITICALITY:
                errors.append(f"{label}: invalid Severity Tests criticality `{severity_row_criticality}`")
            if severity_row_status not in ALLOWED_SEVERITY_STATUS:
                errors.append(f"{label}: invalid Severity Tests status `{severity_row_status}`")
            if p2accepted not in ALLOWED_P2_ACCEPTED:
                errors.append(f"{label}: invalid Severity Tests p2+ accepted `{p2accepted}`")
            if severity_row_claim != severity:
                errors.append(f"{label}: ledger severity `{severity}` does not match Severity Tests `{severity_row_claim}`")
            if severity_row_criticality != criticality:
                errors.append(f"{label}: ledger criticality `{criticality}` does not match Severity Tests `{severity_row_criticality}`")
            if severity_row_status != severity_status:
                errors.append(f"{label}: ledger severity status `{severity_status}` does not match Severity Tests `{severity_row_status}`")
            if is_empty(severity_row.get("minevidenceseverity", "")):
                errors.append(f"{label}: missing minimum evidence to accept severity")
            if severity in P2_PLUS and p2accepted == "not-p2plus":
                errors.append(f"{label}: P2+ row cannot use p2+ accepted=not-p2plus")
            if severity not in P2_PLUS and p2accepted != "not-p2plus":
                warnings.append(f"{label}: non-P2+ row usually uses p2+ accepted=not-p2plus")
            if severity in P2_PLUS and severity_status in {"downgraded", "rejected", "unresolved"} and is_empty(severity_row.get("downgradereason", "")):
                errors.append(f"{label}: non-accepted P2+ row requires downgrade/reject reason")

        if severity in P2_PLUS:
            p2_count += 1
            if severity_status == "accepted":
                p2_accepted_count += 1
                if criticality not in IMPLEMENTATION_CRITICALITY:
                    errors.append(f"{label}: accepted P2+ severity requires implementation-grade criticality, got `{criticality}`")
                if not evidence_ref_is_concrete(severity_proof_ref):
                    errors.append(f"{label}: accepted P2+ severity requires concrete severity proof ref")
            if severity_status in {"downgraded", "rejected", "unresolved"} and disposition == "act":
                errors.append(f"{label}: P2+ cannot be `act` unless severity is accepted")

        if disposition == "act":
            act_count += 1
            if nochange != "defeated":
                errors.append(f"{label}: `act` requires no-change status `defeated`")
            if concern not in {"valid", "partial"}:
                errors.append(f"{label}: `act` requires concern validity `valid` or `partial`")
            if relevance in {"stale-or-superseded", "unsupported", "out-of-scope", "preference-only", "direction-conflicting", "review-closure-only"}:
                errors.append(f"{label}: `act` conflicts with relevance `{relevance}`")
            if evidence_grade not in ACTION_EVIDENCE_GRADES:
                errors.append(f"{label}: `act` requires current evidence grade, got `{evidence_grade}`")
            if not evidence_ref_is_concrete(evidence_ref):
                errors.append(f"{label}: `act` requires concrete evidence ref")
            if proposed == "validation-only":
                errors.append(f"{label}: `act` cannot use proposed-fix validity `validation-only`")
            if direction_fit not in ACT_DIRECTION_FIT:
                errors.append(f"{label}: `act` requires direction_fit aligned or direction-overriding")
            if not evidence_ref_is_concrete(direction_ref):
                errors.append(f"{label}: `act` requires concrete direction ref")
            if mutation_value != "codebase-material":
                errors.append(f"{label}: `act` requires mutation_value codebase-material")
            if criticality not in IMPLEMENTATION_CRITICALITY:
                errors.append(f"{label}: `act` requires implementation-grade accepted criticality, got `{criticality}`")
            if criticality == "review-closure-only":
                errors.append(f"{label}: review-closure-only cannot justify `act`")
            if severity in P2_PLUS and severity_status != "accepted":
                errors.append(f"{label}: P2+ `act` requires severity_acceptance_status accepted")
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
                if resolutionvalue not in IMPLEMENTATION_RESOLUTION_VALUES:
                    errors.append(f"{label}: `act` requires implementation-grade resolution value, got `{resolutionvalue}`")
                if norm_value(decision.get("nochangedefeated", "")) != "yes":
                    errors.append(f"{label}: `act` requires no-change defeated=yes")
            if proposed in {"wrong-fix", "overbroad", "under-specified", "not-applicable"}:
                if handoff not in IMPLEMENTATION_HANDOFFS:
                    errors.append(f"{label}: invalid proposed fix requires explicit replacement/invariant handoff")
                warnings.append(f"{label}: proposed fix is `{proposed}`; verify replacement fix shape")
        elif disposition == "blocked":
            blocked_count += 1
        else:
            if disposition in {"rebut", "defer"}:
                reply_count += 1

        if proposed == "validation-only":
            validation_count += 1
            if disposition != "need-evidence":
                errors.append(f"{label}: proposed-fix validity `validation-only` requires disposition `need-evidence`")
            if handoff != "route-to-fixed-point-driver":
                errors.append(f"{label}: validation-only requires handoff `route-to-fixed-point-driver`")
            if mutation_value != "validation-material":
                errors.append(f"{label}: validation-only requires mutation_value validation-material")
        if disposition == "need-evidence":
            validation_count += 1
            if handoff == "route-to-accretive-implementer":
                errors.append(f"{label}: `need-evidence` cannot route directly to accretive-implementer")
            if nochange == "defeated":
                warnings.append(f"{label}: `need-evidence` usually should not have no-change status `defeated`")
        if disposition == "rebut":
            if handoff in IMPLEMENTATION_HANDOFFS:
                errors.append(f"{label}: `rebut` cannot route to implementation handoff `{handoff}`")
        if disposition == "defer":
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
        severity = norm_value(ledger_row.get("severity", ""))
        severity_status = norm_value(ledger_row.get("severitystatus", ""))
        criticality = norm_value(ledger_row.get("criticality", ""))
        direction_fit = norm_value(ledger_row.get("directionfit", ""))
        mutation_value = norm_value(ledger_row.get("mutationvalue", ""))
        if decision_value == "address":
            if disposition != "act":
                errors.append(f"{label}: resolve decision `address` requires disposition `act`")
            if nochange != "defeated":
                errors.append(f"{label}: resolve decision `address` requires defeated no-change case")
            if direction_fit not in ACT_DIRECTION_FIT:
                errors.append(f"{label}: address requires direction_fit aligned or direction-overriding")
            if mutation_value != "codebase-material":
                errors.append(f"{label}: address requires mutation_value codebase-material")
            if criticality not in IMPLEMENTATION_CRITICALITY:
                errors.append(f"{label}: address requires implementation-grade accepted criticality")
            if severity in P2_PLUS and severity_status != "accepted":
                errors.append(f"{label}: P2+ address requires accepted severity")
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
            if mutation_value != "validation-material":
                errors.append(f"{label}: validate-only requires mutation_value validation-material")
            if severity in P2_PLUS and direction_fit in {"conflicting", "neutral"}:
                errors.append(f"{label}: P2+ validate-only requires aligned, direction-overriding, or unknown direction fit")
        elif decision_value == "resolve-thread-only":
            if disposition == "act":
                errors.append(f"{label}: resolve-thread-only conflicts with disposition `act`")
            if route_rationale != "proof-only-thread":
                errors.append(f"{label}: resolve-thread-only requires route rationale `proof-only-thread`")
            if handoff in IMPLEMENTATION_HANDOFFS:
                errors.append(f"{label}: resolve-thread-only cannot use implementation handoff `{handoff}`")
            if mutation_value not in {"proof-only", "reply-only", "no-change"}:
                errors.append(f"{label}: resolve-thread-only requires proof-only, reply-only, or no-change mutation value")
        elif decision_value == "do-not-address":
            if disposition == "act":
                errors.append(f"{label}: do-not-address conflicts with disposition `act`")
            if route_rationale != "no-change":
                errors.append(f"{label}: do-not-address requires route rationale `no-change`")
            if mutation_value not in {"no-change", "reply-only", "proof-only"}:
                warnings.append(f"{label}: do-not-address usually uses mutation_value no-change, reply-only, or proof-only")
            if norm_value(next_action) not in {"none", "", "no", "n/a", "na"} and "reply" not in norm_value(next_action):
                warnings.append(f"{label}: do-not-address usually uses next=none or proof/reply-only")
        elif decision_value == "blocked":
            if route_rationale != "blocked":
                errors.append(f"{label}: blocked requires route rationale `blocked`")
            if disposition != "blocked":
                errors.append(f"{label}: blocked resolve decision requires disposition `blocked`")

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
    if decision_buckets["blocked"] and gate.get("adjudicationcomplete") == "pass":
        errors.append("Resolve Selection has blocked rows but adjudication_complete is pass")
    if decision_buckets["blocked"] and any(gate.get(field) == "yes" for field in ["implementationhandoffallowed", "validationhandoffallowed", "replyhandoffallowed"]):
        errors.append("Resolve Selection has blocked rows but a handoff permission is yes")

    if rows and act_count == len(rows):
        validate_structured_table(text, "All-Action Justification", ALL_ACTION_CHECKS, errors, "why action still warranted")
    if rows and len(decision_buckets["address"]) + len(decision_buckets["validate-only"]) == len(rows):
        validate_structured_table(text, "All-Selected Justification", ALL_SELECTED_CHECKS, errors, "why selected resolution is still warranted")
    if p2_count > 0 and p2_accepted_count == p2_count:
        validate_structured_table(text, "All-P2+ Accepted Justification", ALL_P2_ACCEPTED_CHECKS, errors, "why accepted severity still warranted")

    validate_specialist_receipts(text, gate, errors)

    for section in ["Acceptance Skew Audit", "P2+ Severity Audit", "Direction Fit Audit", "Selection Skew Audit"]:
        if not section_text(text, section).strip():
            errors.append(f"{section} is empty")

    bottom_line = section_text(text, "Adjudication Bottom Line")
    if (gate_failures or errors) and "blocked" not in bottom_line.lower():
        errors.append("failed gate or mechanical error requires blocked Adjudication Bottom Line")

    stats = {
        "comments": len(rows),
        "act": act_count,
        "non_action": max(0, len(rows) - act_count),
        "blocked": blocked_count,
        "p2_plus": p2_count,
        "p2_plus_accepted": p2_accepted_count,
        "validation_or_need_evidence": validation_count,
        "reply_rows": reply_count,
        "resolve_address": len(decision_buckets["address"]),
        "resolve_validate_only": len(decision_buckets["validate-only"]),
        "resolve_thread_only": len(decision_buckets["resolve-thread-only"]),
        "resolve_do_not_address": len(decision_buckets["do-not-address"]),
        "resolve_blocked": len(decision_buckets["blocked"]),
        "duplicate_ledger_ids": len(duplicate_ledger_ids),
        "errors": len(errors),
        "warnings": len(warnings),
    }
    return CheckResult(passed=not errors, errors=errors, warnings=warnings, stats=stats, gate=gate)


def print_human(result: CheckResult) -> None:
    if result.passed:
        print("PASS: Compact-Gated v4 adjudication gate contract satisfied")
    else:
        print("FAIL: Compact-Gated v4 adjudication gate contract incomplete")
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
  comment_set_digest: c1,c2,c3,c4
  ci_state: local tests pass 2026-05-26

- branch / PR: feature/retry
- current artifact evidence: src/a.py and tests/test_a.py
- tests / CI: local pytest pass
- comments adjudicated: 4
- limits / unavailable evidence: none

## Direction Context Ledger

direction_state_id:
  source: proposed-plan
  source_ref: .step/proposed-plan.md:7
  source_freshness: current
  same_objective: yes
  active_frontier: st-101 retry idempotence
  locked_decisions: narrow retry fix, no public API rename
  non_goals: helper rename, broader migration
  compatibility_posture: preserve API
  ownership_boundaries: retry module only
  direction_confidence: high

## Comment Inventory

- input_comment_count: 4
- ledger_row_count: 4
- input_comment_ids: c1,c2,c3,c4
- ledger_comment_ids: c1,c2,c3,c4
- missing_comment_ids: []
- duplicate_comment_ids: []
- synthesized_ids_for_real_comments: no

## PR Why Ledger

- intended_change: make retry idempotent
- explicit_constraints: narrow change
- non_goals: public API rename and broad migration
- governing_invariants: retry idempotence
- evidence_source: .step/proposed-plan.md:7
- rationale_freshness: current
- staleness_source: none
- confidence: high

## Comment Ledger

| id/thread | reviewer | location | excerpt | claim | reviewer severity claim | accepted criticality | severity acceptance status | direction fit | direction ref | mutation value | concern validity | proposed fix validity | relevance | disposition | no-change status | invariant | evidence grade | evidence ref | severity proof ref | handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1 | alice | src/a.py:10 | retry writes twice | retry path is not idempotent | P2 | correctness-critical | accepted | aligned | .step/proposed-plan.md:7 | codebase-material | valid | valid | material-relevant | act | defeated | retry idempotence | current-artifact | src/a.py:10 | tests/test_a.py::test_retry_idempotent | route-to-accretive-implementer |
| c2 | bob | src/a.py:12 | maybe flakes | flake risk needs proof | P2 | unknown | unresolved | aligned | .step/proposed-plan.md:7 | validation-material | unknown | validation-only | material-relevant | need-evidence | unresolved | retry idempotence | reviewer-only | thread:c2 | missing | route-to-fixed-point-driver |
| c3 | cara | src/a.py:1 | rename helper | helper name should change | P2 | review-closure-only | downgraded | neutral | .step/proposed-plan.md:non-goals | no-change | unsupported | not-applicable | review-closure-only | rebut | not-defeated | none | current-artifact | src/a.py:1 | src/a.py:1 | none |
| c4 | dan | src/a.py:99 | migrate all retries | migrate adjacent retry stack | P3 | out-of-lane | rejected | conflicting | .step/proposed-plan.md:non-goals | no-change | partial | overbroad | out-of-scope | defer | not-defeated | migration boundary | current-artifact | src/a.py:99 | src/a.py:99 | none |

## Decision Tests

| id/thread | grounded | material | fresh | diagnosis | scope-fit | resolution value | no-change defeated | min evidence to change mind |
|---|---|---|---|---|---|---|---|---|
| c1 | yes | yes | current | correct | yes | correctness-critical | yes | counterexample test showing no duplicate write |
| c2 | unknown | yes | current | unknown | yes | validation-needed | unresolved | repro or failing test for flake |
| c3 | no | no | current | unknown | no | review-closure | no | repo naming convention or user goal |
| c4 | yes | no | current | partially-correct | no | out-of-lane | no | separate migration plan and user approval |

## Direction Tests

| id/thread | direction source | source freshness | same objective | direction fit | direction ref | active frontier | non-goal conflict | direction override | min evidence to change direction |
|---|---|---|---|---|---|---|---|---|---|
| c1 | proposed-plan | current | yes | aligned | .step/proposed-plan.md:7 | st-101 retry idempotence | no | not-needed | newer plan superseding retry idempotence |
| c2 | proposed-plan | current | yes | aligned | .step/proposed-plan.md:7 | st-101 retry idempotence | no | not-needed | proof that flake is outside retry path |
| c3 | proposed-plan | current | yes | neutral | .step/proposed-plan.md:non-goals | st-101 retry idempotence | no | not-needed | explicit user request for rename |
| c4 | proposed-plan | current | yes | conflicting | .step/proposed-plan.md:non-goals | st-101 retry idempotence | yes | no | new migration plan approved by user |

## Severity Tests

| id/thread | reviewer severity claim | accepted criticality | severity acceptance status | severity proof ref | downgrade/reject reason | p2+ accepted | min evidence to accept severity |
|---|---|---|---|---|---|---|---|
| c1 | P2 | correctness-critical | accepted | tests/test_a.py::test_retry_idempotent | n/a | yes | test proving no duplicate write risk is impossible |
| c2 | P2 | unknown | unresolved | missing | flake severity unproven until repro | no | failing repro or CI log showing flake |
| c3 | P2 | review-closure-only | downgraded | src/a.py:1 | no repo convention or user goal makes rename critical | no | repo naming convention or explicit user goal |
| c4 | P3 | out-of-lane | rejected | src/a.py:99 | broad migration is a non-goal | not-p2plus | separate migration plan |

## No-Change Countercases

- c1:
  - strongest no-change case: maybe existing guard handles duplicate writes.
  - status: defeated
  - why defeated / preserved / unresolved: src/a.py:10 lacks guard.
- c2:
  - strongest no-change case: flake is unproven.
  - status: unresolved
  - why defeated / preserved / unresolved: validation would decide route.
- c3:
  - strongest no-change case: rename is review-closure-only and not a codebase material change.
  - status: not-defeated
  - why defeated / preserved / unresolved: no convention supplied.
- c4:
  - strongest no-change case: migration is outside non-goals.
  - status: not-defeated
  - why defeated / preserved / unresolved: proposed plan locks narrow retry fix.

## Governing Invariant Ledger

| invariant id | invariant | comments | evidence | violated/threatened | minimum fix shape | handoff | why not local fixes |
|---|---|---|---|---|---|---|---|
| inv1 | retry idempotence | c1,c2 | src/a.py:10 | violated/threatened | guard duplicate write and validate flake claim | route-to-fixed-point-driver only for c2 validation | c1 is narrow; c2 is proof-first |

## Act On

- c1: add the narrow idempotence guard; evidence src/a.py:10; direction .step/proposed-plan.md:7; accepted criticality correctness-critical.

## Rebut

- c3: rebut as review-closure-only and severity-downgraded; no repo convention supplied.

## Defer / Out of Scope

- c4: defer broad migration as direction-conflicting non-goal.

## Need Evidence

- c2: route validation-only repro/probe to fixed-point-driver; validation would decide whether the flake is real.

## Resolve Selection

| id/thread | resolve decision | reason | proof ref | next | route rationale |
|---|---|---|---|---|---|
| c1 | address | act row has defeated no-change case, direction fit, and accepted P2 severity | src/a.py:10 | route-to-accretive-implementer | narrow-local |
| c2 | validate-only | reviewer flake claim is unproven and validation would change severity/route | thread:c2 | route-to-fixed-point-driver | validation-only |
| c3 | do-not-address | review-closure-only no-change case preserved | src/a.py:1 | none | no-change |
| c4 | do-not-address | direction-conflicting migration non-goal preserved | .step/proposed-plan.md:non-goals | none | no-change |

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
- c4:
  - proposed resolve decision: do-not-address
  - strongest alternative resolve decision: address
  - why alternative is rejected / preserved / unresolved: .step/proposed-plan.md non-goals reject migration.

## Invariant-Level Handoff

- invariant: retry idempotence
- affected comments: c1,c2
- route: fixed-point-driver only for validation c2 if needed; c1 is narrow-local
- minimum fix shape: guard duplicate write and prove with test
- proof required: pytest tests/test_a.py::test_retry_idempotent

## Acceptance Skew Audit

- disposition distribution: act=1, need-evidence=1, rebut=1, defer=1
- acceptance pressure checked: mixed dispositions avoid all-action pressure
- stale/superseded possibilities: none current
- unsupported possibilities: c3 unsupported
- preference-only possibilities: c3 review-closure-only
- out-of-scope possibilities: c4 out-of-scope
- direction-conflicting possibilities: c4 direction-conflicting
- review-closure-only possibilities: c3 review-closure-only
- validation-only alternatives: c2
- shared-invariant pressure: c1/c2 share retry idempotence

## P2+ Severity Audit

- p2_plus_count: 3
- accepted_count: 1
- downgraded_count: 1
- rejected_count: 0
- unresolved_count: 1
- accepted criticality distribution: correctness-critical=1
- unsupported severity labels: c2 unresolved
- review-closure-only downgrades: c3
- validation-only P2+ rows: c2
- direction-conflicting P2+ rows: none

## Direction Fit Audit

- direction source distribution: proposed-plan=4
- same-objective proof: .step/proposed-plan.md:7 current same objective
- stale/off-target plan pressure: none
- conflicting-direction rows: c4
- direction-overriding rows: none
- rows where `$st`/plan/update-plan changed disposition: c3,c4
- rows where direction was insufficient and blocked/need-evidence was chosen: none

## Selection Skew Audit

- resolve decision distribution: address=1, validate-only=1, do-not-address=2
- all-selected pressure checked: not all selected
- address over-selection possibilities: c2,c3,c4 rejected as address
- validate-only over-routing possibilities: only c2 validation-only
- proof-only thread-resolution alternatives: none already fixed
- do-not-address alternatives: c3,c4
- blocked/ask-user alternatives: none
- direction-conflict alternatives: c4
- review-closure-only alternatives: c3
- fixed-point over-routing pressure: c1 stays narrow-local; c2 validation only

## Adjudication Gate

| field | value | basis |
|---|---|---|
| artifact_state_coverage | pass | artifact_state_id recorded |
| direction_context_coverage | pass | direction_state_id recorded |
| comment_inventory_coverage | pass | all four ids match ledger |
| identity_coverage | pass | all rows have raw identity |
| decision_test_coverage | pass | all rows have decision tests |
| direction_fit_coverage | pass | all rows have direction tests and refs |
| severity_claim_coverage | pass | all rows split severity claim and criticality |
| p2_plus_acceptance_coverage | pass | P2 rows accepted/unresolved/downgraded with proof or reason |
| no_change_coverage | pass | all rows have countercases |
| disposition_coverage | pass | all rows have one disposition |
| proposed_fix_separation | pass | concern and fix split |
| evidence_ref_coverage | pass | act has current artifact evidence ref |
| validation_value_coverage | pass | c2 validate-only has validation-material |
| resolve_selection_coverage | pass | every ledger row has valid downstream selection |
| resolve_countercase_coverage | pass | every ledger row has resolve countercase |
| handoff_agenda_consistency | pass | agenda buckets match selection map |
| selection_skew_audit | pass | skew audited |
| p2_plus_severity_audit | pass | P2+ severity audited |
| direction_fit_audit | pass | direction fit audited |
| invariant_pass | pass | invariant checked and named |
| specialist_packet_coverage | not-used | no specialists used |
| acceptance_skew_audit | pass | skew audited |
| adjudication_complete | pass | all required fields pass |
| implementation_handoff_allowed | yes | c1 is artifact-backed address |
| validation_handoff_allowed | yes | c2 is validation-only |
| reply_handoff_allowed | yes | c3/c4 reply allowed |

## Handoff Agenda

- implementation route: accretive-implementer
- validation route: fixed-point-driver
- proof-only thread-resolution route: none
- reply route: optional logophile
- items selected for implementation: c1
- validation-only items: c2
- proof-only thread-resolution items: none
- items not selected: c3,c4
- proof: pytest tests/test_a.py::test_retry_idempotent
- blocked items: none

## Adjudication Bottom Line

Proceed: one artifact-backed action, one validation-only item, one rebuttal, and one deferred no-change item.
"""


def invalid_fixture() -> str:
    return """
## Review Basis

- branch / PR: feature/retry

## Direction Context Ledger

- source: unknown

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

| id/thread | reviewer | location | excerpt | claim | reviewer severity claim | accepted criticality | severity acceptance status | direction fit | direction ref | mutation value | concern validity | proposed fix validity | relevance | disposition | no-change status | invariant | evidence grade | evidence ref | severity proof ref | handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1 | alice | src/a.py:10 | retry writes twice | retry path is not idempotent | P2 | review-closure-only | accepted | unknown | unknown | no-change | unknown | validation-only | material-relevant | act | unresolved | none | reviewer-only | code | review | route-to-accretive-implementer |

## Decision Tests

| id/thread | grounded | material | fresh | diagnosis | scope-fit | resolution value | no-change defeated | min evidence to change mind |
|---|---|---|---|---|---|---|---|---|
| c1 | unknown | yes | unclear | unknown | unknown | review-closure | unresolved | repro |

## Direction Tests

| id/thread | direction source | source freshness | same objective | direction fit | direction ref | active frontier | non-goal conflict | direction override | min evidence to change direction |
|---|---|---|---|---|---|---|---|---|---|
| c1 | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | plan proof |

## Severity Tests

| id/thread | reviewer severity claim | accepted criticality | severity acceptance status | severity proof ref | downgrade/reject reason | p2+ accepted | min evidence to accept severity |
|---|---|---|---|---|---|---|---|
| c1 | P2 | review-closure-only | accepted | review | n/a | yes | proof |

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

## P2+ Severity Audit

all P2 accepted.

## Direction Fit Audit

unknown.

## Selection Skew Audit

all selected.

## Adjudication Gate

| field | value | basis |
|---|---|---|
| artifact_state_coverage | fail | missing |
| direction_context_coverage | fail | missing |
| comment_inventory_coverage | fail | dropped c2 |
| identity_coverage | pass | c1 only |
| decision_test_coverage | fail | incomplete |
| direction_fit_coverage | fail | incomplete |
| severity_claim_coverage | fail | no severity proof |
| p2_plus_acceptance_coverage | fail | P2 accepted wrongly |
| no_change_coverage | fail | unresolved |
| disposition_coverage | pass | one row |
| proposed_fix_separation | pass | split |
| evidence_ref_coverage | fail | no current evidence |
| validation_value_coverage | fail | validation-only act |
| resolve_selection_coverage | fail | invalid address |
| resolve_countercase_coverage | fail | generic |
| handoff_agenda_consistency | fail | missing agenda |
| selection_skew_audit | fail | generic |
| p2_plus_severity_audit | fail | generic |
| direction_fit_audit | fail | generic |
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
