#!/usr/bin/env python3
"""Mechanical contract checker for Surface-Budgeted Resolution-Warranted v6 review-adjudication outputs.

The checker validates output shape, stale-proofing fields, evidence-reference
obligations, resolve-selection anti-laundering, adversarial action coverage,
parallelism calibration, resolution warrants, surface budgets, and downstream
handoff/diff-surface safety. It cannot prove semantic correctness, but it blocks
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
    "material-relevant", "relevant-nonmaterial", "partially-relevant",
    "stale-or-superseded", "unsupported", "out-of-scope", "preference-only",
}
ALLOWED_DISPOSITION = {"act", "rebut", "defer", "need-evidence"}
ALLOWED_NO_CHANGE = {"defeated", "not-defeated", "unresolved"}
ALLOWED_CONCERN = {"valid", "partial", "unsupported", "unknown"}
ALLOWED_PROPOSED = {"valid", "partially-valid", "wrong-fix", "overbroad", "under-specified", "not-applicable", "validation-only"}
ALLOWED_EVIDENCE_GRADE = {"current-artifact", "current-test", "current-ci", "current-session-artifact", "prior-session-artifact", "memory-only", "reviewer-only", "none"}
ACTION_EVIDENCE_GRADES = {"current-artifact", "current-test", "current-ci", "current-session-artifact"}
ALLOWED_HANDOFF = {"none", "route-to-accretive-implementer", "route-to-fixed-point-driver", "route-to-logophile", "ask-user", "draft-reply"}
IMPLEMENTATION_HANDOFFS = {"route-to-accretive-implementer", "route-to-fixed-point-driver"}
ALLOWED_GROUNDED = {"yes", "no", "unknown"}
ALLOWED_MATERIAL = {"yes", "no", "user-requested", "unknown"}
ALLOWED_FRESH = {"current", "stale", "superseded", "unclear"}
ALLOWED_DIAGNOSIS = {"correct", "partially-correct", "misdiagnosed", "unknown"}
ALLOWED_SCOPE_FIT = {"yes", "no", "partial", "unknown"}
ALLOWED_RESOLUTION_VALUE = {"merge-blocking", "correctness-critical", "review-closure", "proof-only", "validation-needed", "low-value", "out-of-lane", "blocked"}
ALLOWED_NO_CHANGE_DEFEATED = {"yes", "no", "unresolved"}
ALLOWED_RESOLVE_DECISION = {"address", "validate-only", "resolve-thread-only", "do-not-address", "blocked"}
ALLOWED_ROUTE_RATIONALE = {"narrow-local", "coupled-comments", "invariant-level", "structural", "validation-only", "contentious", "likely-to-reopen", "proof-only-thread", "no-change", "blocked"}
FIXED_POINT_RATIONALES = {"coupled-comments", "invariant-level", "structural", "validation-only", "contentious", "likely-to-reopen"}
ALLOWED_PERMITTED_ACTION = {"mutate-code", "add-validation-only", "resolve-thread", "draft-reply", "defer", "none"}
ACTION_BY_DECISION = {
    "address": {"mutate-code"},
    "validate-only": {"add-validation-only"},
    "resolve-thread-only": {"resolve-thread"},
    "do-not-address": {"draft-reply", "defer", "none"},
    "blocked": {"none"},
}
ALLOWED_SURFACE_BUDGET_MODE = {"subtractive-first", "neutral-first", "additive-capped", "exploratory"}
ALLOWED_TARGET_NET_LOC = {"negative", "zero", "small-positive", "unknown", "uncapped-blocked"}
ALLOWED_EXPANSION_STATUS = {"not-needed", "needed", "granted", "blocked"}
ALLOWED_YES_NO = {"yes", "no"}
ALLOWED_PARALLELISM_MODE = {"root-equivalent", "targeted-parallel", "full-fanout", "swarm", "not-required"}
ALLOWED_VETO_STATUS = {"cleared", "preserved-no-change", "unresolved", "vetoed", "blocked", "not-required"}
ALLOWED_CLEARANCE = {"cleared", "preserved", "rerouted", "downgraded", "blocked"}

REQUIRED_LEDGER_FIELDS = ["id", "reviewer", "location", "excerpt", "claim", "concern", "proposed", "relevance", "disposition", "nochange", "invariant", "evidencegrade", "evidenceref", "handoff"]
REQUIRED_DECISION_FIELDS = ["id", "grounded", "material", "fresh", "diagnosis", "scopefit", "resolutionvalue", "nochangedefeated", "minevidence"]
REQUIRED_RESOLVE_FIELDS = ["id", "decision", "reason", "proofref", "next", "routerationale"]
REQUIRED_ADVERSARIAL_FIELDS = ["id", "decision", "lanes", "parallelismmode", "response", "vetostatus", "clearance", "proofref", "impact"]
REQUIRED_WARRANT_FIELDS = ["warrantid", "claimid", "source", "claimexcerpt", "decision", "concern", "proposed", "nochange", "resolutionvalue", "routerationale", "permittedaction", "permittedscope", "forbiddenactions", "evidencerefs", "countercaseref", "proofrequired", "expiry"]
REQUIRED_SURFACE_BUDGET_FIELDS = ["warrantid", "mode", "targetnetloc", "maxpositiveloc", "maxnewpublicsymbols", "maxnewfiles", "maxnewhelpers", "maxnewflagsorknobs", "maxnewstatevariants", "maxnewbranches", "duplicatepathbudget", "subtractiveprobesrequired", "expansionwarrantrequired", "expansionstatus", "proofrequired", "notes"]
REQUIRED_GATE_FIELDS = [
    "artifactstatecoverage", "commentinventorycoverage", "identitycoverage",
    "decisiontestcoverage", "nochangecoverage", "dispositioncoverage",
    "proposedfixseparation", "evidencerefcoverage", "resolveselectioncoverage",
    "resolvecountercasecoverage", "adversarialactioncoverage",
    "parallelismcalibration", "resolutionwarrantcoverage", "surfacebudgetcoverage",
    "surfacebudgetconsumptionsafety", "warrantconsumptionsafety",
    "handoffagendaconsistency", "selectionskewaudit", "invariantpass",
    "specialistpacketcoverage", "acceptanceskewaudit", "adjudicationcomplete",
    "implementationhandoffallowed", "validationhandoffallowed", "replyhandoffallowed",
]
REQUIRED_SECTIONS = [
    "Review Basis", "Comment Inventory", "PR Why Ledger", "Comment Ledger",
    "Decision Tests", "No-Change Countercases", "Governing Invariant Ledger",
    "Act On", "Rebut", "Defer / Out of Scope", "Need Evidence",
    "Resolve Selection", "Resolve Countercases", "Adversarial Action Matrix",
    "Resolution Warrants", "Surface Budget Ledger", "Invariant-Level Handoff",
    "Acceptance Skew Audit", "Selection Skew Audit", "Adjudication Gate",
    "Handoff Agenda", "Adjudication Bottom Line",
]
OPTIONAL_SINGLETON_SECTIONS = {"All-Action Justification", "All-Selected Justification", "Specialist Packet Receipts"}
EMPTY_MARKERS = {"", "-", "—", "n/a", "na", "unknown", "missing", "none", "[]"}
GENERIC_EVIDENCE = {"code", "code-supports-it", "artifact-evidence", "current-artifacts", "review", "reviewer-said-so", "looks-right", "tests"}

COLUMN_ALIASES = {
    "idthread": "id", "id": "id", "commentid": "id", "threadid": "id", "reviewcommentid": "id",
    "reviewer": "reviewer", "author": "reviewer", "location": "location", "fileorthread": "location", "file": "location", "thread": "location", "pathline": "location",
    "excerpt": "excerpt", "shortexcerpt": "excerpt", "reviewexcerpt": "excerpt", "claim": "claim", "summary": "claim", "reviewclaim": "claim",
    "concernvalidity": "concern", "concern": "concern", "proposedfixvalidity": "proposed", "proposedfix": "proposed", "fixvalidity": "proposed",
    "relevance": "relevance", "relevanceclass": "relevance", "disposition": "disposition", "nochangestatus": "nochange", "nochangecountercasestatus": "nochange", "countercasestatus": "nochange",
    "invariant": "invariant", "governinginvariant": "invariant", "evidencegrade": "evidencegrade", "evidenceclass": "evidencegrade", "evidencelevel": "evidencegrade", "evidenceref": "evidenceref", "evidencebasis": "evidenceref", "evidence": "evidenceref",
    "handoff": "handoff", "handoffaction": "handoff",
}
DECISION_ALIASES = {
    "idthread": "id", "id": "id", "commentid": "id", "threadid": "id", "grounded": "grounded", "grounding": "grounded",
    "material": "material", "materiality": "material", "fresh": "fresh", "freshness": "fresh", "diagnosis": "diagnosis", "diagnosisquality": "diagnosis",
    "scopefit": "scopefit", "scope": "scopefit", "resolutionvalue": "resolutionvalue", "resolution": "resolutionvalue", "value": "resolutionvalue", "selectionvalue": "resolutionvalue",
    "nochangedefeated": "nochangedefeated", "nochangecountercasedefeated": "nochangedefeated", "countercasedefeated": "nochangedefeated",
    "minevidencetochange": "minevidence", "minimumevidencetochange": "minevidence", "minimumevidencetochangemind": "minevidence", "minevidencetochangemind": "minevidence",
}
RESOLVE_ALIASES = {"idthread": "id", "id": "id", "commentid": "id", "threadid": "id", "resolvedecision": "decision", "decision": "decision", "selection": "decision", "resolve": "decision", "reason": "reason", "basis": "reason", "proofref": "proofref", "proof": "proofref", "evidenceref": "proofref", "next": "next", "nextaction": "next", "handoff": "next", "routerationale": "routerationale", "rationale": "routerationale", "route": "routerationale"}
ADVERSARIAL_ALIASES = {"idthread": "id", "id": "id", "commentid": "id", "threadid": "id", "primaryresolvedecision": "decision", "resolvedecision": "decision", "decision": "decision", "adversariallanes": "lanes", "lanes": "lanes", "challengerlanes": "lanes", "parallelismmode": "parallelismmode", "mode": "parallelismmode", "strongestadversarialresponse": "response", "response": "response", "veto": "vetostatus", "vetostatus": "vetostatus", "clearance": "clearance", "proofref": "proofref", "proof": "proofref", "evidenceref": "proofref", "decisionimpact": "impact", "impact": "impact"}
WARRANT_ALIASES = {"warrantid": "warrantid", "warrant": "warrantid", "claimid": "claimid", "commentid": "claimid", "threadid": "claimid", "source": "source", "claimexcerpt": "claimexcerpt", "excerpt": "claimexcerpt", "decision": "decision", "resolvedecision": "decision", "concernvalidity": "concern", "concern": "concern", "proposedfixvalidity": "proposed", "proposedfix": "proposed", "nochange": "nochange", "nochangestatus": "nochange", "resolutionvalue": "resolutionvalue", "value": "resolutionvalue", "routerationale": "routerationale", "route": "routerationale", "permittedaction": "permittedaction", "action": "permittedaction", "permission": "permittedaction", "permittedscope": "permittedscope", "scope": "permittedscope", "forbiddenactions": "forbiddenactions", "forbidden": "forbiddenactions", "evidencerefs": "evidencerefs", "evidenceref": "evidencerefs", "evidence": "evidencerefs", "countercaseref": "countercaseref", "countercase": "countercaseref", "proofrequired": "proofrequired", "proof": "proofrequired", "expiry": "expiry", "expires": "expiry"}
SURFACE_BUDGET_ALIASES = {"warrantid": "warrantid", "warrant": "warrantid", "mode": "mode", "targetnetloc": "targetnetloc", "targetloc": "targetnetloc", "maxpositiveloc": "maxpositiveloc", "maxpositive": "maxpositiveloc", "maxinsertions": "maxpositiveloc", "maxnewpublicsymbols": "maxnewpublicsymbols", "publicsymbolbudget": "maxnewpublicsymbols", "maxnewfiles": "maxnewfiles", "newfilebudget": "maxnewfiles", "maxnewhelpers": "maxnewhelpers", "helperbudget": "maxnewhelpers", "maxnewflagsorknobs": "maxnewflagsorknobs", "maxnewflags": "maxnewflagsorknobs", "maxnewflagsknobs": "maxnewflagsorknobs", "maxnewstatevariants": "maxnewstatevariants", "statevariantbudget": "maxnewstatevariants", "maxnewbranches": "maxnewbranches", "branchbudget": "maxnewbranches", "duplicatepathbudget": "duplicatepathbudget", "duplicatepaths": "duplicatepathbudget", "subtractiveprobesrequired": "subtractiveprobesrequired", "subtractiveprobes": "subtractiveprobesrequired", "expansionwarrantrequired": "expansionwarrantrequired", "expansionrequired": "expansionwarrantrequired", "expansionstatus": "expansionstatus", "proofrequired": "proofrequired", "proof": "proofrequired", "notes": "notes"}
GATE_ALIASES = {"artifactstatecoverage": "artifactstatecoverage", "artifactcoverage": "artifactstatecoverage", "commentinventorycoverage": "commentinventorycoverage", "inventorycoverage": "commentinventorycoverage", "identitycoverage": "identitycoverage", "decisiontestcoverage": "decisiontestcoverage", "decisiontestscoverage": "decisiontestcoverage", "nochangecoverage": "nochangecoverage", "dispositioncoverage": "dispositioncoverage", "proposedfixseparation": "proposedfixseparation", "fixseparation": "proposedfixseparation", "evidencerefcoverage": "evidencerefcoverage", "evidencecoverage": "evidencerefcoverage", "resolveselectioncoverage": "resolveselectioncoverage", "resolvecoverage": "resolveselectioncoverage", "selectioncoverage": "resolveselectioncoverage", "resolvecountercasecoverage": "resolvecountercasecoverage", "adversarialactioncoverage": "adversarialactioncoverage", "adversarialcoverage": "adversarialactioncoverage", "parallelismcalibration": "parallelismcalibration", "parallelismcoverage": "parallelismcalibration", "resolutionwarrantcoverage": "resolutionwarrantcoverage", "warrantcoverage": "resolutionwarrantcoverage", "surfacebudgetcoverage": "surfacebudgetcoverage", "budgetcoverage": "surfacebudgetcoverage", "surfacebudgetconsumptionsafety": "surfacebudgetconsumptionsafety", "warrantconsumptionsafety": "warrantconsumptionsafety", "handoffagendaconsistency": "handoffagendaconsistency", "agendaconsistency": "handoffagendaconsistency", "selectionskewaudit": "selectionskewaudit", "selectionaudit": "selectionskewaudit", "invariantpass": "invariantpass", "specialistpacketcoverage": "specialistpacketcoverage", "acceptanceskewaudit": "acceptanceskewaudit", "adjudicationcomplete": "adjudicationcomplete", "implementationhandoffallowed": "implementationhandoffallowed", "validationhandoffallowed": "validationhandoffallowed", "replyhandoffallowed": "replyhandoffallowed", "handoffallowed": "implementationhandoffallowed"}
INVENTORY_ALIASES = {"inputcommentcount": "inputcount", "ledgerrowcount": "ledgercount", "inputcommentids": "inputids", "ledgercommentids": "ledgerids", "missingcommentids": "missingids", "duplicatecommentids": "duplicateids", "synthesizedidsforrealcomments": "synthesized"}
HANDOFF_ALIASES = {"itemsselectedforimplementation": "implementation", "implementationitems": "implementation", "selectedforimplementation": "implementation", "validationonlyitems": "validation", "validationitems": "validation", "proofonlythreadresolutionitems": "proofonly", "proofonlyitems": "proofonly", "threadresolutionitems": "proofonly", "itemsnotselected": "notselected", "notselecteditems": "notselected", "blockeditems": "blocked"}

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


def is_empty(value: str) -> bool:
    return norm_value(value) in EMPTY_MARKERS


def section_count(text: str, title: str) -> int:
    return len(re.findall(rf"(?im)^\s*#+\s+{re.escape(title)}\s*$", text))


def has_section(text: str, title: str) -> bool:
    return section_count(text, title) > 0


def section_text(text: str, title: str) -> str:
    m = re.search(rf"(?im)^\s*#+\s+{re.escape(title)}\s*$", text)
    if not m:
        return ""
    start = m.end()
    n = re.search(r"(?m)^\s*#+\s+", text[start:])
    end = start + n.start() if n else len(text)
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
    table_lines: List[str] = []
    started = False
    for line in block.splitlines():
        if line.strip().startswith("|"):
            table_lines.append(line.rstrip())
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
    header_map = {}
    for header in headers:
        canonical = aliases.get(norm_key(header))
        if canonical:
            header_map[canonical] = header
    out = []
    for row in rows:
        out.append({canonical: row.get(original, "").strip() for canonical, original in header_map.items()})
    return header_map, out


def rows_by_id(rows: Sequence[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    out = {}
    for row in rows:
        rid = row.get("id", "").strip()
        if rid:
            out[rid] = row
    return out


def parse_int(value: str) -> Optional[int]:
    m = re.search(r"-?\d+", value or "")
    if not m:
        return None
    try:
        return int(m.group(0))
    except ValueError:
        return None


def parse_nonnegative_int(value: str) -> Optional[int]:
    val = parse_int(value)
    return val if val is not None and val >= 0 else None


def parse_diffstat(value: str) -> Tuple[int, int]:
    insertions = deletions = 0
    mi = re.search(r"(\d+)\s+insertions?\(\+\)", value or "")
    md = re.search(r"(\d+)\s+deletions?\(-\)", value or "")
    if mi:
        insertions = int(mi.group(1))
    if md:
        deletions = int(md.group(1))
    return insertions, deletions


def parse_id_list(value: str) -> List[str]:
    value = (value or "").strip()
    if is_empty(value):
        return []
    if re.search(r"(?i)\ball\b", value):
        return ["__ALL__"]
    value = re.sub(r"^[\[({]", "", value)
    value = re.sub(r"[\])}]$", "", value)
    return [p.strip().strip('"\'`') for p in re.split(r"[,;\s]+", value) if p.strip().strip('"\'`')]


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
    gate = {}
    for row in rows:
        canonical = GATE_ALIASES.get(norm_key(row.get(field_header, "")))
        if canonical:
            gate[canonical] = norm_value(row.get(value_header, ""))
    return gate


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
    if any(tok in normalized for tok in ["test", "ci", "cmd", "command", "log", "thread", "pr#", "gh-", "github", "diff", "src/", "tests/", "commit"]):
        return True
    return "/" in value or "." in value or "#" in value or len(value.strip()) >= 16


def extract_refs(value: str) -> List[str]:
    if is_empty(value):
        return []
    return [p.strip().strip('"\'`') for p in re.split(r"[,;\n]+", value) if p.strip().strip('"\'`')]


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
            continue
        present = [rid for rid in known_ids if re.search(rf"(?<![A-Za-z0-9_.:-]){re.escape(rid)}(?![A-Za-z0-9_.:-])", raw)]
        buckets[bucket] = present if present else parse_id_list(raw)
    return buckets


def validate_adversarial_matrix(text: str, resolve_by_id: Dict[str, Dict[str, str]], ledger_by_id: Dict[str, Dict[str, str]], errors: List[str], warnings: List[str]) -> Tuple[Dict[str, Dict[str, str]], Dict[str, List[str]]]:
    headers, raw = extract_first_table(section_text(text, "Adversarial Action Matrix"))
    header_map, rows = normalize_rows(headers, raw, ADVERSARIAL_ALIASES)
    missing = [f for f in REQUIRED_ADVERSARIAL_FIELDS if f not in header_map]
    if missing:
        errors.append("Adversarial Action Matrix missing required columns: " + ", ".join(missing))
    if not rows:
        errors.append("Adversarial Action Matrix has no data rows")
    by_id = rows_by_id(rows)
    clearance_buckets = {"cleared": [], "preserved": [], "rerouted": [], "downgraded": [], "blocked": []}
    if set(resolve_by_id) - set(by_id):
        errors.append("Adversarial Action Matrix missing comment ids: " + ", ".join(sorted(set(resolve_by_id) - set(by_id))))
    if set(by_id) - set(resolve_by_id):
        errors.append("Adversarial Action Matrix contains unknown comment ids: " + ", ".join(sorted(set(by_id) - set(resolve_by_id))))
    for rid, row in by_id.items():
        decision = norm_value(row.get("decision", ""))
        mode = norm_value(row.get("parallelismmode", ""))
        veto = norm_value(row.get("vetostatus", ""))
        clearance = norm_value(row.get("clearance", ""))
        proof = row.get("proofref", "")
        response = row.get("response", "")
        lanes = row.get("lanes", "")
        if decision not in ALLOWED_RESOLVE_DECISION:
            errors.append(f"{rid}: invalid Adversarial Action Matrix primary resolve decision `{row.get('decision', '')}`")
        if mode not in ALLOWED_PARALLELISM_MODE:
            errors.append(f"{rid}: invalid parallelism mode `{row.get('parallelismmode', '')}`")
        if veto not in ALLOWED_VETO_STATUS:
            errors.append(f"{rid}: invalid veto status `{row.get('vetostatus', '')}`")
        if clearance not in ALLOWED_CLEARANCE:
            errors.append(f"{rid}: invalid clearance `{row.get('clearance', '')}`")
        else:
            clearance_buckets[clearance].append(rid)
        if is_empty(response):
            errors.append(f"{rid}: missing strongest adversarial response")
        if is_empty(lanes):
            errors.append(f"{rid}: missing adversarial lanes")
        resolve = resolve_by_id.get(rid)
        if resolve and decision != norm_value(resolve.get("decision", "")):
            errors.append(f"{rid}: Adversarial Action Matrix decision `{decision}` does not match Resolve Selection `{norm_value(resolve.get('decision', ''))}`")
        if decision == "address":
            if veto != "cleared" or clearance != "cleared":
                errors.append(f"{rid}: address requires adversarial veto status cleared and clearance cleared")
            if not evidence_ref_is_concrete(proof):
                errors.append(f"{rid}: address adversarial clearance requires concrete proof ref")
            if mode == "not-required":
                errors.append(f"{rid}: address cannot use parallelism mode not-required")
        elif decision == "validate-only":
            if veto != "cleared" or clearance not in {"cleared", "downgraded"}:
                errors.append(f"{rid}: validate-only requires cleared veto and cleared/downgraded clearance")
            if not evidence_ref_is_concrete(proof):
                errors.append(f"{rid}: validate-only adversarial row requires concrete proof ref")
        elif decision == "resolve-thread-only":
            if veto not in {"cleared", "preserved-no-change"} or clearance != "preserved":
                errors.append(f"{rid}: resolve-thread-only requires cleared/preserved-no-change veto and preserved clearance")
            if not evidence_ref_is_concrete(proof):
                errors.append(f"{rid}: resolve-thread-only adversarial row requires concrete proof ref")
        elif decision == "do-not-address":
            if veto not in {"cleared", "preserved-no-change"} or clearance != "preserved":
                errors.append(f"{rid}: do-not-address requires cleared/preserved-no-change veto and preserved clearance")
            if not evidence_ref_is_concrete(proof):
                errors.append(f"{rid}: do-not-address adversarial row requires concrete proof/no-change ref")
        elif decision == "blocked":
            if veto not in {"blocked", "unresolved"} or clearance != "blocked":
                errors.append(f"{rid}: blocked requires blocked/unresolved veto and blocked clearance")
            if not evidence_ref_is_concrete(proof, allow_missing=True):
                errors.append(f"{rid}: blocked adversarial row requires proof ref or explicit missing marker")
        if mode == "root-equivalent" and decision == "address" and norm_value(resolve.get("routerationale", "")) in FIXED_POINT_RATIONALES if resolve else False:
            warnings.append(f"{rid}: fixed-point-rationale address used root-equivalent adversarial mode; verify parallelism calibration")
    return by_id, clearance_buckets


def validate_resolution_warrants(text: str, ledger_by_id: Dict[str, Dict[str, str]], resolve_by_id: Dict[str, Dict[str, str]], handoff_buckets: Dict[str, List[str]], errors: List[str], warnings: List[str], changed_files: Optional[Sequence[str]] = None, resolved_threads: Optional[Sequence[str]] = None) -> Dict[str, object]:
    headers, raw = extract_first_table(section_text(text, "Resolution Warrants"))
    header_map, rows = normalize_rows(headers, raw, WARRANT_ALIASES)
    missing = [f for f in REQUIRED_WARRANT_FIELDS if f not in header_map]
    if missing:
        errors.append("Resolution Warrants missing required columns: " + ", ".join(missing))
    if not rows:
        errors.append("Resolution Warrants has no data rows")
    by_claim: Dict[str, Dict[str, str]] = {}
    action_buckets = {"mutate-code": [], "add-validation-only": [], "resolve-thread": [], "draft-reply": [], "defer": [], "none": []}
    for idx, row in enumerate(rows, start=1):
        wid = row.get("warrantid", "").strip() or f"warrant row {idx}"
        cid = row.get("claimid", "").strip()
        if not cid:
            errors.append(f"{wid}: missing claim id")
            continue
        if cid in by_claim:
            errors.append(f"{cid}: duplicate Resolution Warrant claim id")
        by_claim[cid] = row
        decision = norm_value(row.get("decision", ""))
        concern = norm_value(row.get("concern", ""))
        proposed = norm_value(row.get("proposed", ""))
        nochange = norm_value(row.get("nochange", ""))
        resolution_value = norm_value(row.get("resolutionvalue", ""))
        route = norm_value(row.get("routerationale", ""))
        action = norm_value(row.get("permittedaction", ""))
        scope = row.get("permittedscope", "")
        forbidden = row.get("forbiddenactions", "")
        evidence = row.get("evidencerefs", "")
        countercase = row.get("countercaseref", "")
        proof = row.get("proofrequired", "")
        expiry = row.get("expiry", "")
        if decision not in ALLOWED_RESOLVE_DECISION:
            errors.append(f"{wid}: invalid warrant decision `{row.get('decision', '')}`")
        if concern not in ALLOWED_CONCERN:
            errors.append(f"{wid}: invalid warrant concern validity `{row.get('concern', '')}`")
        if proposed not in ALLOWED_PROPOSED:
            errors.append(f"{wid}: invalid warrant proposed-fix validity `{row.get('proposed', '')}`")
        if nochange not in ALLOWED_NO_CHANGE:
            errors.append(f"{wid}: invalid warrant no-change status `{row.get('nochange', '')}`")
        if resolution_value not in ALLOWED_RESOLUTION_VALUE:
            errors.append(f"{wid}: invalid warrant resolution value `{row.get('resolutionvalue', '')}`")
        if route not in ALLOWED_ROUTE_RATIONALE:
            errors.append(f"{wid}: invalid warrant route rationale `{row.get('routerationale', '')}`")
        if action not in ALLOWED_PERMITTED_ACTION:
            errors.append(f"{wid}: invalid permitted action `{row.get('permittedaction', '')}`")
        else:
            action_buckets[action].append(cid)
        if cid not in ledger_by_id:
            errors.append(f"{wid}: claim id `{cid}` does not appear in Comment Ledger")
        resolve = resolve_by_id.get(cid)
        if not resolve:
            errors.append(f"{wid}: no Resolve Selection row for claim `{cid}`")
        else:
            if decision != norm_value(resolve.get("decision", "")):
                errors.append(f"{wid}: warrant decision `{decision}` does not match Resolve Selection `{norm_value(resolve.get('decision', ''))}`")
            if route != norm_value(resolve.get("routerationale", "")):
                errors.append(f"{wid}: warrant route rationale `{route}` does not match Resolve Selection `{norm_value(resolve.get('routerationale', ''))}`")
        if action not in ACTION_BY_DECISION.get(decision, set()):
            errors.append(f"{wid}: decision `{decision}` cannot issue permitted action `{action}`")
        if action == "mutate-code":
            if nochange != "defeated":
                errors.append(f"{wid}: mutate-code warrant requires no-change status defeated")
            if resolution_value not in {"merge-blocking", "correctness-critical", "review-closure"}:
                errors.append(f"{wid}: mutate-code warrant has non-implementation resolution value `{resolution_value}`")
            if is_empty(scope) or norm_value(scope) in {"all", "repo", "whole-repo", "everything"}:
                errors.append(f"{wid}: mutate-code warrant requires narrow permitted scope")
            if "mutate" not in norm_value(forbidden) and "outside" not in norm_value(forbidden):
                errors.append(f"{wid}: mutate-code warrant must forbid mutation outside permitted scope")
            if not any(evidence_ref_is_concrete(ref) for ref in extract_refs(evidence)):
                errors.append(f"{wid}: mutate-code warrant requires concrete evidence refs")
        elif action == "add-validation-only":
            if resolution_value != "validation-needed":
                errors.append(f"{wid}: add-validation-only requires resolution value validation-needed")
            fn = norm_value(forbidden)
            if "production" not in fn and "requested-code-change" not in fn and "mutate-code" not in fn:
                errors.append(f"{wid}: validation-only warrant must forbid production mutation/requested fix")
        elif action == "resolve-thread":
            if not any(evidence_ref_is_concrete(ref) for ref in extract_refs(evidence)):
                errors.append(f"{wid}: resolve-thread warrant requires proof evidence refs")
        if is_empty(countercase):
            errors.append(f"{wid}: missing countercase ref")
        if is_empty(proof) and action != "none":
            errors.append(f"{wid}: non-none warrant requires proof_required")
        expiry_norm = norm_value(expiry)
        if is_empty(expiry) or not any(tok in expiry_norm for tok in ["head", "base", "artifact", "comment", "claim", "thread", "diff"]):
            errors.append(f"{wid}: expiry must mention artifact/comment invalidation conditions")
    if set(resolve_by_id) - set(by_claim):
        errors.append("Resolution Warrants missing claims: " + ", ".join(sorted(set(resolve_by_id) - set(by_claim))))
    expected = {"mutate-code": sorted(handoff_buckets.get("implementation", [])), "add-validation-only": sorted(handoff_buckets.get("validation", [])), "resolve-thread": sorted(handoff_buckets.get("proofonly", []))}
    for action, expected_ids in expected.items():
        got = sorted(action_buckets.get(action, []))
        if got != expected_ids:
            errors.append(f"Resolution Warrant `{action}` claims mismatch Handoff Agenda: expected {expected_ids}, got {got}")
    if changed_files:
        mutate_warrants = [row for row in rows if norm_value(row.get("permittedaction", "")) == "mutate-code"]
        for changed in changed_files:
            if changed and not any(changed in row.get("permittedscope", "") for row in mutate_warrants):
                errors.append(f"changed file `{changed}` is not covered by any mutate-code warrant permitted scope")
    if resolved_threads:
        thread_warrants = [row for row in rows if norm_value(row.get("permittedaction", "")) in {"resolve-thread", "mutate-code"}]
        for thread in resolved_threads:
            if thread and not any(thread in row.get("permittedscope", "") or thread in row.get("claimid", "") for row in thread_warrants):
                errors.append(f"resolved thread `{thread}` is not covered by any resolve-thread/address warrant")
    return {"rows": rows, "by_claim": by_claim, "action_buckets": action_buckets}


def validate_surface_budget_ledger(text: str, warrant_rows: Sequence[Dict[str, str]], errors: List[str], warnings: List[str], diffstat: str = "", new_public_symbols: int = 0, new_files: int = 0, new_helpers: int = 0, new_flags_or_knobs: int = 0) -> Dict[str, object]:
    headers, raw = extract_first_table(section_text(text, "Surface Budget Ledger"))
    header_map, rows = normalize_rows(headers, raw, SURFACE_BUDGET_ALIASES)
    missing = [f for f in REQUIRED_SURFACE_BUDGET_FIELDS if f not in header_map]
    if missing:
        errors.append("Surface Budget Ledger missing required columns: " + ", ".join(missing))
    mutate_warrants = [row for row in warrant_rows if norm_value(row.get("permittedaction", "")) == "mutate-code"]
    if not rows and mutate_warrants:
        errors.append("Surface Budget Ledger has no data rows despite mutate-code warrants")
    budget_by_warrant: Dict[str, Dict[str, str]] = {}
    for idx, row in enumerate(rows, start=1):
        wid = row.get("warrantid", "").strip() or f"surface budget row {idx}"
        budget_by_warrant[wid] = row
        mode = norm_value(row.get("mode", ""))
        target = norm_value(row.get("targetnetloc", ""))
        subtractive = norm_value(row.get("subtractiveprobesrequired", ""))
        expansion = norm_value(row.get("expansionwarrantrequired", ""))
        status = norm_value(row.get("expansionstatus", ""))
        if mode not in ALLOWED_SURFACE_BUDGET_MODE:
            errors.append(f"{wid}: invalid surface budget mode `{row.get('mode', '')}`")
        if target not in ALLOWED_TARGET_NET_LOC:
            errors.append(f"{wid}: invalid target net LOC `{row.get('targetnetloc', '')}`")
        if subtractive not in ALLOWED_YES_NO:
            errors.append(f"{wid}: subtractive probes required must be yes/no")
        if expansion not in ALLOWED_YES_NO:
            errors.append(f"{wid}: expansion warrant required must be yes/no")
        if status not in ALLOWED_EXPANSION_STATUS:
            errors.append(f"{wid}: invalid expansion status `{row.get('expansionstatus', '')}`")
        for f in ["maxpositiveloc", "maxnewpublicsymbols", "maxnewfiles", "maxnewhelpers", "maxnewflagsorknobs", "maxnewstatevariants", "maxnewbranches", "duplicatepathbudget"]:
            if parse_nonnegative_int(row.get(f, "")) is None:
                errors.append(f"{wid}: `{f}` must be a non-negative integer")
        if is_empty(row.get("proofrequired", "")):
            errors.append(f"{wid}: Surface Budget Ledger requires proof required")
        if is_empty(row.get("notes", "")):
            errors.append(f"{wid}: Surface Budget Ledger requires notes")
    mutate_ids = [row.get("warrantid", "").strip() for row in mutate_warrants if row.get("warrantid", "").strip()]
    missing_budgets = sorted(set(mutate_ids) - set(budget_by_warrant))
    if missing_budgets:
        errors.append("Surface Budget Ledger missing mutate-code warrant ids: " + ", ".join(missing_budgets))
    total_max = total_public = total_files = total_helpers = total_flags = 0
    subtractive_first = 0
    for warrant in mutate_warrants:
        wid = warrant.get("warrantid", "").strip()
        budget = budget_by_warrant.get(wid)
        if not budget:
            continue
        mode = norm_value(budget.get("mode", ""))
        target = norm_value(budget.get("targetnetloc", ""))
        subtractive = norm_value(budget.get("subtractiveprobesrequired", ""))
        expansion = norm_value(budget.get("expansionwarrantrequired", ""))
        max_pos = parse_nonnegative_int(budget.get("maxpositiveloc", "")) or 0
        total_max += max_pos
        total_public += parse_nonnegative_int(budget.get("maxnewpublicsymbols", "")) or 0
        total_files += parse_nonnegative_int(budget.get("maxnewfiles", "")) or 0
        total_helpers += parse_nonnegative_int(budget.get("maxnewhelpers", "")) or 0
        total_flags += parse_nonnegative_int(budget.get("maxnewflagsorknobs", "")) or 0
        if mode == "subtractive-first":
            subtractive_first += 1
        if subtractive != "yes":
            errors.append(f"{wid}: mutate-code surface budget requires subtractive probes before first production patch")
        if expansion != "yes":
            errors.append(f"{wid}: mutate-code surface budget requires expansion warrant for additive escape")
        if mode == "exploratory":
            errors.append(f"{wid}: mutate-code warrant cannot use exploratory surface budget mode")
        if target == "uncapped-blocked":
            errors.append(f"{wid}: mutate-code warrant cannot proceed with uncapped-blocked target net LOC")
    ins, dels = parse_diffstat(diffstat)
    net = ins - dels
    if diffstat and mutate_warrants and net > total_max:
        errors.append(f"diffstat net LOC +{net} exceeds mutate-code surface budget max positive LOC {total_max}")
    if new_public_symbols > total_public:
        errors.append(f"new public symbols {new_public_symbols} exceed surface budget {total_public}")
    if new_files > total_files:
        errors.append(f"new files {new_files} exceed surface budget {total_files}")
    if new_helpers > total_helpers:
        errors.append(f"new helpers {new_helpers} exceed surface budget {total_helpers}")
    if new_flags_or_knobs > total_flags:
        errors.append(f"new flags/knobs {new_flags_or_knobs} exceed surface budget {total_flags}")
    return {"rows": rows, "by_warrant": budget_by_warrant, "mutate_budget_rows": len(mutate_ids), "subtractive_first": subtractive_first, "total_max_positive_loc": total_max, "diffstat_insertions": ins, "diffstat_deletions": dels, "diffstat_net": net}


def check_adjudication(text: str, changed_files: Optional[Sequence[str]] = None, resolved_threads: Optional[Sequence[str]] = None, diffstat: str = "", new_public_symbols: int = 0, new_files: int = 0, new_helpers: int = 0, new_flags_or_knobs: int = 0) -> CheckResult:
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
    ledger_headers, ledger_raw = extract_first_table(section_text(text, "Comment Ledger"))
    ledger_map, ledger_rows = normalize_rows(ledger_headers, ledger_raw, COLUMN_ALIASES)
    missing = [f for f in REQUIRED_LEDGER_FIELDS if f not in ledger_map]
    if missing:
        errors.append("Comment Ledger missing required columns: " + ", ".join(missing))
    if not ledger_rows:
        errors.append("Comment Ledger has no data rows")
    ledger_ids = [row.get("id", "").strip() for row in ledger_rows if row.get("id", "").strip()]
    ledger_by_id = rows_by_id(ledger_rows)
    input_count = parse_int(inventory.get("inputcount", ""))
    ledger_count = parse_int(inventory.get("ledgercount", ""))
    if input_count is not None and input_count != len(ledger_rows):
        errors.append(f"Comment Inventory input_comment_count={input_count} but ledger has {len(ledger_rows)} rows")
    if ledger_count is not None and ledger_count != len(ledger_rows):
        errors.append(f"Comment Inventory ledger_row_count={ledger_count} but ledger has {len(ledger_rows)} rows")
    input_ids = parse_id_list(inventory.get("inputids", ""))
    declared_ledger_ids = parse_id_list(inventory.get("ledgerids", ""))
    if input_ids and sorted(set(input_ids) - set(ledger_ids)):
        errors.append("Comment Inventory omitted input ids from ledger: " + ", ".join(sorted(set(input_ids) - set(ledger_ids))))
    if declared_ledger_ids and set(declared_ledger_ids) != set(ledger_ids):
        errors.append("Comment Inventory ledger_comment_ids does not match actual ledger ids")
    if parse_id_list(inventory.get("missingids", "")):
        errors.append("Comment Inventory reports missing ids: " + ", ".join(parse_id_list(inventory.get("missingids", ""))))
    if parse_id_list(inventory.get("duplicateids", "")):
        errors.append("Comment Inventory reports duplicate ids: " + ", ".join(parse_id_list(inventory.get("duplicateids", ""))))
    if norm_value(inventory.get("synthesized", "")) != "no":
        errors.append("synthesized_ids_for_real_comments must be no for implementation handoff")

    decision_headers, decision_raw = extract_first_table(section_text(text, "Decision Tests"))
    decision_map, decision_rows = normalize_rows(decision_headers, decision_raw, DECISION_ALIASES)
    missing_decisions = [f for f in REQUIRED_DECISION_FIELDS if f not in decision_map]
    if missing_decisions:
        errors.append("Decision Tests missing required columns: " + ", ".join(missing_decisions))
    decisions = rows_by_id(decision_rows)
    nochange_text = section_text(text, "No-Change Countercases")
    resolve_counter_text = section_text(text, "Resolve Countercases")
    act_count = validation_count = reply_count = non_action_count = 0
    for idx, row in enumerate(ledger_rows, start=1):
        rid = row.get("id", f"row {idx}") or f"row {idx}"
        for f in ["id", "reviewer", "location", "excerpt", "claim"]:
            if is_empty(row.get(f, "")):
                errors.append(f"{rid}: missing raw identity field `{f}`")
        if rid not in nochange_text:
            errors.append(f"{rid}: missing No-Change Countercases entry")
        if rid not in resolve_counter_text:
            errors.append(f"{rid}: missing Resolve Countercases entry")
        relevance = norm_value(row.get("relevance", ""))
        disposition = norm_value(row.get("disposition", ""))
        nochange = norm_value(row.get("nochange", ""))
        concern = norm_value(row.get("concern", ""))
        proposed = norm_value(row.get("proposed", ""))
        evidence_grade = norm_value(row.get("evidencegrade", ""))
        evidence_ref = row.get("evidenceref", "")
        handoff = norm_value(row.get("handoff", ""))
        if relevance not in ALLOWED_RELEVANCE:
            errors.append(f"{rid}: invalid relevance `{row.get('relevance', '')}`")
        if disposition not in ALLOWED_DISPOSITION:
            errors.append(f"{rid}: invalid disposition `{row.get('disposition', '')}`")
        if nochange not in ALLOWED_NO_CHANGE:
            errors.append(f"{rid}: invalid no-change status `{row.get('nochange', '')}`")
        if concern not in ALLOWED_CONCERN:
            errors.append(f"{rid}: invalid concern validity `{row.get('concern', '')}`")
        if proposed not in ALLOWED_PROPOSED:
            errors.append(f"{rid}: invalid proposed-fix validity `{row.get('proposed', '')}`")
        if evidence_grade not in ALLOWED_EVIDENCE_GRADE:
            errors.append(f"{rid}: invalid evidence grade `{row.get('evidencegrade', '')}`")
        if handoff not in ALLOWED_HANDOFF:
            errors.append(f"{rid}: invalid handoff `{row.get('handoff', '')}`")
        decision = decisions.get(rid)
        if not decision:
            errors.append(f"{rid}: missing Decision Tests row")
        else:
            checks = [("grounded", ALLOWED_GROUNDED), ("material", ALLOWED_MATERIAL), ("fresh", ALLOWED_FRESH), ("diagnosis", ALLOWED_DIAGNOSIS), ("scopefit", ALLOWED_SCOPE_FIT), ("resolutionvalue", ALLOWED_RESOLUTION_VALUE), ("nochangedefeated", ALLOWED_NO_CHANGE_DEFEATED)]
            for f, allowed in checks:
                if norm_value(decision.get(f, "")) not in allowed:
                    errors.append(f"{rid}: invalid Decision Tests {f} `{decision.get(f, '')}`")
            if is_empty(decision.get("minevidence", "")):
                errors.append(f"{rid}: missing minimum evidence to change mind")
        if disposition == "act":
            act_count += 1
            if nochange != "defeated":
                errors.append(f"{rid}: `act` requires no-change status `defeated`")
            if concern not in {"valid", "partial"}:
                errors.append(f"{rid}: `act` requires concern validity valid or partial")
            if evidence_grade not in ACTION_EVIDENCE_GRADES:
                errors.append(f"{rid}: `act` requires current evidence grade")
            if not evidence_ref_is_concrete(evidence_ref):
                errors.append(f"{rid}: `act` requires concrete evidence ref")
        else:
            non_action_count += 1
        if proposed == "validation-only" or disposition == "need-evidence":
            validation_count += 1
            if proposed == "validation-only" and disposition != "need-evidence":
                errors.append(f"{rid}: proposed-fix validity validation-only requires disposition need-evidence")
            if handoff == "route-to-accretive-implementer":
                errors.append(f"{rid}: need-evidence/validation-only cannot route directly to accretive-implementer")
        if disposition in {"rebut", "defer"}:
            reply_count += 1
            if handoff in IMPLEMENTATION_HANDOFFS and disposition == "rebut":
                errors.append(f"{rid}: rebut cannot route to implementation handoff `{handoff}`")
    resolve_headers, resolve_raw = extract_first_table(section_text(text, "Resolve Selection"))
    resolve_map, resolve_rows = normalize_rows(resolve_headers, resolve_raw, RESOLVE_ALIASES)
    missing_resolve = [f for f in REQUIRED_RESOLVE_FIELDS if f not in resolve_map]
    if missing_resolve:
        errors.append("Resolve Selection missing required columns: " + ", ".join(missing_resolve))
    resolve_by_id = rows_by_id(resolve_rows)
    if set(ledger_ids) - set(resolve_by_id):
        errors.append("Resolve Selection missing comment ids: " + ", ".join(sorted(set(ledger_ids) - set(resolve_by_id))))
    if set(resolve_by_id) - set(ledger_ids):
        errors.append("Resolve Selection contains unknown comment ids: " + ", ".join(sorted(set(resolve_by_id) - set(ledger_ids))))
    decision_buckets = {"address": [], "validate-only": [], "resolve-thread-only": [], "do-not-address": [], "blocked": []}
    for idx, row in enumerate(resolve_rows, start=1):
        rid = row.get("id", f"resolve row {idx}") or f"resolve row {idx}"
        decision = norm_value(row.get("decision", ""))
        proof_ref = row.get("proofref", "")
        route = norm_value(row.get("routerationale", ""))
        if decision not in ALLOWED_RESOLVE_DECISION:
            errors.append(f"{rid}: invalid resolve decision `{row.get('decision', '')}`")
        else:
            decision_buckets[decision].append(rid)
        if route not in ALLOWED_ROUTE_RATIONALE:
            errors.append(f"{rid}: invalid route rationale `{row.get('routerationale', '')}`")
        if decision == "blocked":
            if not evidence_ref_is_concrete(proof_ref, allow_missing=True):
                errors.append(f"{rid}: blocked selection requires proof ref or explicit missing marker")
        elif not evidence_ref_is_concrete(proof_ref):
            errors.append(f"{rid}: Resolve Selection requires concrete proof ref")
        ledger = ledger_by_id.get(rid)
        if not ledger:
            continue
        disposition = norm_value(ledger.get("disposition", ""))
        nochange = norm_value(ledger.get("nochange", ""))
        handoff = norm_value(ledger.get("handoff", ""))
        if decision == "address":
            if disposition != "act":
                errors.append(f"{rid}: resolve decision address requires disposition act")
            if nochange != "defeated":
                errors.append(f"{rid}: resolve decision address requires defeated no-change case")
            if route == "narrow-local" and (handoff == "route-to-fixed-point-driver" or "fixed-point-driver" in norm_value(row.get("next", ""))):
                errors.append(f"{rid}: narrow-local address must not route to fixed-point-driver")
            if route != "narrow-local" and route not in FIXED_POINT_RATIONALES:
                errors.append(f"{rid}: address route rationale must be narrow-local or fixed-point rationale")
        elif decision == "validate-only":
            if disposition != "need-evidence":
                errors.append(f"{rid}: validate-only requires disposition need-evidence")
            if route != "validation-only":
                errors.append(f"{rid}: validate-only requires route rationale validation-only")
            if handoff != "route-to-fixed-point-driver":
                errors.append(f"{rid}: validate-only requires route-to-fixed-point-driver handoff")
        elif decision == "resolve-thread-only":
            if disposition == "act":
                errors.append(f"{rid}: resolve-thread-only conflicts with disposition act")
            if route != "proof-only-thread":
                errors.append(f"{rid}: resolve-thread-only requires route rationale proof-only-thread")
        elif decision == "do-not-address":
            if disposition == "act":
                errors.append(f"{rid}: do-not-address conflicts with disposition act")
            if route != "no-change":
                errors.append(f"{rid}: do-not-address requires route rationale no-change")
        elif decision == "blocked" and route != "blocked":
            errors.append(f"{rid}: blocked requires route rationale blocked")

    adversarial_by_id, clearance_buckets = validate_adversarial_matrix(text, resolve_by_id, ledger_by_id, errors, warnings)
    handoff_buckets = parse_handoff_agenda(section_text(text, "Handoff Agenda"), ledger_ids, errors)
    expected_buckets = {"implementation": sorted(decision_buckets["address"]), "validation": sorted(decision_buckets["validate-only"]), "proofonly": sorted(decision_buckets["resolve-thread-only"]), "notselected": sorted(decision_buckets["do-not-address"]), "blocked": sorted(decision_buckets["blocked"])}
    for bucket, expected_ids in expected_buckets.items():
        got = sorted(handoff_buckets.get(bucket, []))
        if got != expected_ids:
            errors.append(f"Handoff Agenda `{bucket}` mismatch: expected {expected_ids}, got {got}")
    warrant_result = validate_resolution_warrants(text, ledger_by_id, resolve_by_id, handoff_buckets, errors, warnings, changed_files, resolved_threads)
    warrant_buckets = warrant_result.get("action_buckets", {}) if isinstance(warrant_result, dict) else {}
    surface_result = validate_surface_budget_ledger(text, warrant_result.get("rows", []) if isinstance(warrant_result, dict) else [], errors, warnings, diffstat, new_public_symbols, new_files, new_helpers, new_flags_or_knobs)

    gate_headers, gate_raw = extract_first_table(section_text(text, "Adjudication Gate"))
    gate = normalize_gate(gate_headers, gate_raw)
    missing_gate = [f for f in REQUIRED_GATE_FIELDS if f not in gate]
    if missing_gate:
        errors.append("Adjudication Gate missing required fields: " + ", ".join(missing_gate))
    for f in REQUIRED_GATE_FIELDS:
        if f not in gate:
            continue
        v = gate[f]
        if f in {"implementationhandoffallowed", "validationhandoffallowed", "replyhandoffallowed"}:
            if v not in {"yes", "no"}:
                errors.append(f"{f} must be yes/no, got `{v}`")
        elif f == "specialistpacketcoverage":
            if v not in {"pass", "fail", "not-used"}:
                errors.append(f"specialist_packet_coverage must be pass/fail/not-used, got `{v}`")
        elif v not in {"pass", "fail"}:
            errors.append(f"{f} must be pass/fail, got `{v}`")
    gate_failures = [f for f in REQUIRED_GATE_FIELDS if f not in {"implementationhandoffallowed", "validationhandoffallowed", "replyhandoffallowed"} and gate.get(f) == "fail"]
    if gate_failures and gate.get("adjudicationcomplete") == "pass":
        errors.append("adjudication_complete is pass despite failed gate fields: " + ", ".join(gate_failures))
    if errors and gate.get("adjudicationcomplete") == "pass":
        errors.append("adjudication_complete is pass despite mechanical contract errors")
    if errors and gate.get("implementationhandoffallowed") == "yes":
        errors.append("implementation_handoff_allowed is yes despite mechanical contract errors")
    if gate.get("implementationhandoffallowed") == "yes" and not decision_buckets["address"]:
        errors.append("implementation_handoff_allowed is yes but no Resolve Selection row is address")
    if gate.get("implementationhandoffallowed") == "yes" and not warrant_buckets.get("mutate-code"):
        errors.append("implementation_handoff_allowed is yes but no mutate-code Resolution Warrant exists")
    for rid in decision_buckets["address"]:
        adv = adversarial_by_id.get(rid, {})
        if norm_value(adv.get("vetostatus", "")) != "cleared" or norm_value(adv.get("clearance", "")) != "cleared":
            errors.append(f"{rid}: implementation handoff requires cleared adversarial action")
    if decision_buckets["blocked"] and gate.get("adjudicationcomplete") == "pass":
        errors.append("Resolve Selection has blocked rows but adjudication_complete is pass")
    if not section_text(text, "Acceptance Skew Audit").strip():
        errors.append("Acceptance Skew Audit is empty")
    if not section_text(text, "Selection Skew Audit").strip():
        errors.append("Selection Skew Audit is empty")
    bottom_line = section_text(text, "Adjudication Bottom Line")
    if (gate_failures or errors) and "blocked" not in bottom_line.lower():
        errors.append("failed gate or mechanical error requires blocked Adjudication Bottom Line")
    stats = {
        "comments": len(ledger_rows),
        "act": act_count,
        "non_action": non_action_count,
        "validation_or_need_evidence": validation_count,
        "reply_rows": reply_count,
        "resolve_address": len(decision_buckets["address"]),
        "resolve_validate_only": len(decision_buckets["validate-only"]),
        "resolve_thread_only": len(decision_buckets["resolve-thread-only"]),
        "resolve_do_not_address": len(decision_buckets["do-not-address"]),
        "resolve_blocked": len(decision_buckets["blocked"]),
        "adversarial_rows": len(adversarial_by_id),
        "adversarial_cleared": len(clearance_buckets.get("cleared", [])),
        "adversarial_preserved": len(clearance_buckets.get("preserved", [])),
        "adversarial_blocked": len(clearance_buckets.get("blocked", [])),
        "warrants": len(warrant_result.get("rows", [])) if isinstance(warrant_result, dict) else 0,
        "surface_budget_rows": len(surface_result.get("rows", [])) if isinstance(surface_result, dict) else 0,
        "surface_budget_max_positive_loc": int(surface_result.get("total_max_positive_loc", 0)) if isinstance(surface_result, dict) else 0,
        "diffstat_net": int(surface_result.get("diffstat_net", 0)) if isinstance(surface_result, dict) else 0,
        "mutate_warrants": len(warrant_buckets.get("mutate-code", [])) if isinstance(warrant_buckets, dict) else 0,
        "validation_warrants": len(warrant_buckets.get("add-validation-only", [])) if isinstance(warrant_buckets, dict) else 0,
        "thread_resolution_warrants": len(warrant_buckets.get("resolve-thread", [])) if isinstance(warrant_buckets, dict) else 0,
        "errors": len(errors),
        "warnings": len(warnings),
    }
    return CheckResult(passed=not errors, errors=errors, warnings=warnings, stats=stats, gate=gate)


def print_human(result: CheckResult) -> None:
    if result.passed:
        print("PASS: Surface-Budgeted v6 adjudication gate contract satisfied")
    else:
        print("FAIL: Surface-Budgeted v6 adjudication gate contract incomplete")
    print("stats:", ", ".join(f"{k}={v}" for k, v in result.stats.items()))
    if result.gate:
        print("gate:", ", ".join(f"{k}={v}" for k, v in result.gate.items()))
    if result.errors:
        print("errors:")
        for e in result.errors:
            print(f"- {e}")
    if result.warnings:
        print("warnings:")
        for w in result.warnings:
            print(f"- {w}")


def valid_fixture() -> str:
    return """
## Review Basis

artifact_state_id:
  branch: feature/retry
  base: main@abc123
  head: feature@def456
  diff_digest: paths=src/a.py,tests/test_a.py
  comment_set_digest: c1,c2,c3
  ci_state: local tests pass 2026-06-03

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

## Adversarial Action Matrix

| id/thread | primary resolve decision | adversarial lanes | parallelism mode | strongest adversarial response | veto status | clearance | proof ref | decision impact |
|---|---|---|---|---|---|---|---|---|
| c1 | address | no-change,validate-first,fix-shape,surface-budget | targeted-parallel | validate-first is weaker because src/a.py:10 already proves duplicate write | cleared | cleared | src/a.py:10 | address retained |
| c2 | validate-only | mutate-now,no-validation-value,probe-shape | targeted-parallel | mutation is not justified until thread:c2 has a repro | cleared | downgraded | thread:c2 | validation retained |
| c3 | do-not-address | materiality,review-closure,no-change | root-equivalent | no convention or user goal makes rename material | preserved-no-change | preserved | src/a.py:1 | no-change retained |

## Resolution Warrants

| warrant id | claim id | source | claim excerpt | decision | concern validity | proposed fix validity | no-change status | resolution value | route rationale | permitted action | permitted scope | forbidden actions | evidence refs | countercase ref | proof required | expiry |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rw-c1 | c1 | github-review | retry writes twice | address | valid | valid | defeated | correctness-critical | narrow-local | mutate-code | files=src/a.py,tests/test_a.py; symbols=retry guard | mutate outside permitted_scope; resolve unrelated threads | src/a.py:10 | no-change c1 defeated by src/a.py:10; adversarial c1 cleared | pytest tests/test_a.py::test_retry_idempotent | invalid when HEAD/base/diff/comment-set changes |
| rw-c2 | c2 | github-review | maybe flakes | validate-only | unknown | validation-only | unresolved | validation-needed | validation-only | add-validation-only | tests/probes for thread:c2 only | production mutation; requested-code-change; mutate-code | thread:c2 | no-change c2 unresolved pending repro; adversarial c2 downgraded | validation probe for thread:c2 | invalid when HEAD/base/diff/comment-set changes |
| rw-c3 | c3 | github-review | rename helper | do-not-address | unsupported | not-applicable | not-defeated | low-value | no-change | none | none | mutate code; resolve unrelated threads | src/a.py:1 | no-change c3 preserved by missing convention; adversarial c3 preserved | none | invalid when HEAD/base/diff/comment-set changes |

## Surface Budget Ledger

| warrant id | mode | target net loc | max positive loc | max new public symbols | max new files | max new helpers | max new flags/knobs | max new state variants | max new branches | duplicate path budget | subtractive probes required | expansion warrant required | expansion status | proof required | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rw-c1 | subtractive-first | small-positive | 8 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | yes | yes | not-needed | pytest tests/test_a.py::test_retry_idempotent | try deletion/reuse/refactor first; additive guard is capped |

## Invariant-Level Handoff

- invariant: retry idempotence
- affected comments: c1,c2
- route: fixed-point-driver only for validation c2 if needed; c1 is narrow-local
- minimum fix shape: guard duplicate write and prove with test
- proof required: pytest tests/test_a.py::test_retry_idempotent
- adversarial clearance: c1 cleared, c2 validation downgraded, c3 preserved

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
- adversarial parallelism pressure: targeted where material; root-equivalent for c3

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
| adversarial_action_coverage | pass | every selected action has adversarial clearance/preservation |
| parallelism_calibration | pass | targeted material rows, root-equivalent no-change row |
| resolution_warrant_coverage | pass | every resolve decision has a matching warrant |
| surface_budget_coverage | pass | mutate-code warrant has a subtractive-first surface budget |
| surface_budget_consumption_safety | pass | surface budgets constrain downstream diff/symbol growth |
| warrant_consumption_safety | pass | warrant actions match handoff agenda buckets |
| handoff_agenda_consistency | pass | agenda buckets match selection map |
| selection_skew_audit | pass | skew audited |
| invariant_pass | pass | invariant checked and named |
| specialist_packet_coverage | not-used | no specialists used |
| acceptance_skew_audit | pass | skew audited |
| adjudication_complete | pass | all required fields pass |
| implementation_handoff_allowed | yes | c1 is artifact-backed address with adversarial clearance |
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

artifact_state_id:
  branch: feature/retry
  base: main@abc123
  head: feature@def456
  diff_digest: paths=src/a.py
  comment_set_digest: c1
  ci_state: not-run

- branch / PR: feature/retry

## Comment Inventory

- input_comment_count: 1
- ledger_row_count: 1
- input_comment_ids: c1
- ledger_comment_ids: c1
- missing_comment_ids: []
- duplicate_comment_ids: []
- synthesized_ids_for_real_comments: no

## PR Why Ledger

- intended_change: unknown

## Comment Ledger

| id/thread | reviewer | location | excerpt | claim | concern validity | proposed fix validity | relevance | disposition | no-change status | invariant | evidence grade | evidence ref | handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1 | alice | src/a.py:10 | retry writes twice | retry path is not idempotent | valid | valid | material-relevant | act | defeated | retry | current-artifact | src/a.py:10 | route-to-accretive-implementer |

## Decision Tests

| id/thread | grounded | material | fresh | diagnosis | scope-fit | resolution value | no-change defeated | min evidence to change mind |
|---|---|---|---|---|---|---|---|---|
| c1 | yes | yes | current | correct | yes | correctness-critical | yes | proof |

## No-Change Countercases

- c1: defeated.

## Governing Invariant Ledger

none.

## Act On

- c1: implement.

## Rebut

none.

## Defer / Out of Scope

none.

## Need Evidence

none.

## Resolve Selection

| id/thread | resolve decision | reason | proof ref | next | route rationale |
|---|---|---|---|---|---|
| c1 | address | current artifact evidence | src/a.py:10 | route-to-accretive-implementer | narrow-local |

## Resolve Countercases

- c1: validate-only rejected by src/a.py:10.

## Adversarial Action Matrix

| id/thread | primary resolve decision | adversarial lanes | parallelism mode | strongest adversarial response | veto status | clearance | proof ref | decision impact |
|---|---|---|---|---|---|---|---|---|

## Resolution Warrants

| warrant id | claim id | source | claim excerpt | decision | concern validity | proposed fix validity | no-change status | resolution value | route rationale | permitted action | permitted scope | forbidden actions | evidence refs | countercase ref | proof required | expiry |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rw-c1 | c1 | github-review | retry writes twice | address | valid | valid | defeated | correctness-critical | narrow-local | mutate-code | files=src/a.py | mutate outside permitted_scope | src/a.py:10 | c1 no-change | pytest | invalid when HEAD/base/diff/comment-set changes |

## Surface Budget Ledger

| warrant id | mode | target net loc | max positive loc | max new public symbols | max new files | max new helpers | max new flags/knobs | max new state variants | max new branches | duplicate path budget | subtractive probes required | expansion warrant required | expansion status | proof required | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rw-c1 | subtractive-first | small-positive | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | yes | yes | not-needed | pytest | narrow |

## Invariant-Level Handoff

none.

## Acceptance Skew Audit

skew checked.

## Selection Skew Audit

skew checked.

## Adjudication Gate

| field | value | basis |
|---|---|---|
| artifact_state_coverage | pass | recorded |
| comment_inventory_coverage | pass | complete |
| identity_coverage | pass | identity |
| decision_test_coverage | pass | tests |
| no_change_coverage | pass | countercase |
| disposition_coverage | pass | disposition |
| proposed_fix_separation | pass | split |
| evidence_ref_coverage | pass | ref |
| resolve_selection_coverage | pass | selection |
| resolve_countercase_coverage | pass | countercase |
| adversarial_action_coverage | fail | missing adversarial row |
| parallelism_calibration | fail | missing |
| resolution_warrant_coverage | pass | warrant |
| surface_budget_coverage | pass | budget |
| surface_budget_consumption_safety | pass | budget |
| warrant_consumption_safety | pass | warrant |
| handoff_agenda_consistency | pass | agenda |
| selection_skew_audit | pass | audited |
| invariant_pass | pass | checked |
| specialist_packet_coverage | not-used | none |
| acceptance_skew_audit | pass | audited |
| adjudication_complete | fail | incomplete |
| implementation_handoff_allowed | no | blocked |
| validation_handoff_allowed | no | blocked |
| reply_handoff_allowed | no | blocked |

## Handoff Agenda

- items selected for implementation: c1
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
    try:
        text = Path(args.path).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error reading {args.path}: {exc}", file=sys.stderr)
        return 2
    result = check_adjudication(
        text,
        changed_files=parse_id_list(args.changed_files or ""),
        resolved_threads=parse_id_list(args.resolved_threads or ""),
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
