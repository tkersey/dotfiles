#!/usr/bin/env python3
"""Mechanical contract checker for Compact-Gated v6 review-adjudication outputs.

The checker validates output shape, stale-proofing fields, direction-state
obligations, P2+ severity anti-laundering, mutation-approval separation,
source-pressure auditing, authority-panel clearance and veto enforcement,
resolve-selection anti-laundering, validation-value gating, and downstream
handoff safety.

It cannot prove semantic correctness. It deliberately blocks incomplete,
direction-conflicting, severity-laundered, validation-laundered,
authority-vetoed, or over-selected adjudications before implementation routing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

ALLOWED_REVIEW_SOURCE = {
    "human",
    "github-review",
    "pr-thread",
    "cas-codex",
    "codex-review",
    "automated-review",
    "root-equivalent",
    "unknown",
}
AUTO_REVIEW_SOURCES = {"cas-codex", "codex-review", "automated-review", "root-equivalent"}

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
IMPLEMENTATION_HANDOFFS = {"route-to-accretive-implementer", "route-to-fixed-point-driver"}

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
IMPLEMENTATION_RESOLUTION_VALUES = {"merge-blocking", "correctness-critical", "direction-critical"}
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
ALLOWED_YES_NO_UNKNOWN = {"yes", "no", "unknown"}

ALLOWED_MUTATION_VALUE = {
    "codebase-material",
    "validation-material",
    "proof-only",
    "reply-only",
    "no-change",
    "blocked",
}
ALLOWED_APPROVAL_CLASS = {
    "A1-current-owned-defect",
    "A2-proof-surface-false-positive",
    "A3-active-direction-mismatch",
    "A4-minimal-illegal-state-removal",
    "B1-plausible-route-changing-validation",
    "B2-valid-already-fixed",
    "B3-valid-not-this-pr",
    "B4-valid-concern-wrong-fix",
    "C1-unsupported",
    "C2-preference-only",
    "C3-review-closure-only",
    "C4-direction-conflicting",
    "blocked",
    "unknown",
}
ADDRESS_APPROVAL_CLASSES = {
    "A1-current-owned-defect",
    "A2-proof-surface-false-positive",
    "A3-active-direction-mismatch",
    "A4-minimal-illegal-state-removal",
}
VALIDATION_APPROVAL_CLASSES = {"B1-plausible-route-changing-validation"}
PROOF_ONLY_APPROVAL_CLASSES = {"B2-valid-already-fixed", "C3-review-closure-only"}
NO_ADDRESS_APPROVAL_CLASSES = {
    "B3-valid-not-this-pr",
    "B4-valid-concern-wrong-fix",
    "C1-unsupported",
    "C2-preference-only",
    "C3-review-closure-only",
    "C4-direction-conflicting",
}
ALLOWED_APPROVAL_BOOL = {"yes", "no", "partial", "unknown", "not-applicable"}
ALLOWED_FIX_APPROVAL = {"yes", "no", "partial", "no-suggested-fix", "unknown", "not-applicable"}
ALLOWED_P2_ACCEPTED = {"yes", "no", "not-p2plus"}

ALLOWED_AUTHORITY_ROLE = {
    "evidence-authority",
    "direction-ownership-authority",
    "criticality-authority",
    "no-change-advocate",
    "validation-value-authority",
    "fix-shape-authority",
}
ALLOWED_PACKET_STATUS = {"accepted", "rejected", "root-equivalent"}
ALLOWED_PACKET_MATCH = {"yes", "no", "not-applicable"}
AUTHORITY_CLEARANCE_VALUES = {"clear", "veto", "unresolved", "not-required"}
NO_CHANGE_CLEARANCE_VALUES = {"defeated", "veto", "unresolved", "not-required"}
VALIDATION_CLEARANCE_VALUES = {"mutate-now", "validate-first", "no-validation-value", "unresolved", "not-required"}
ALLOWED_AUTHORITY_STATUS = {
    "cleared-for-address",
    "cleared-for-validation",
    "proof-only",
    "no-change",
    "defer",
    "blocked",
}
ALLOWED_VETO_CLASS = {
    "ungrounded",
    "unreachable",
    "stale",
    "already-fixed",
    "wrong-owner",
    "out-of-scope",
    "direction-conflicting",
    "review-closure-only",
    "severity-downgraded",
    "validate-first",
    "wrong-fix",
    "overbroad-fix",
    "duplicate-boundary",
    "proof-only",
    "missing-packet",
}
ALLOWED_VETO_FINAL_ROUTE = {"validate-only", "resolve-thread-only", "do-not-address", "blocked", "defer", "rebut"}

REQUIRED_LEDGER_FIELDS = [
    "id",
    "reviewer",
    "reviewsource",
    "location",
    "excerpt",
    "claim",
    "severity",
    "criticality",
    "severitystatus",
    "directionfit",
    "directionref",
    "approvalclass",
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
REQUIRED_MUTATION_FIELDS = [
    "id",
    "concernapproved",
    "fixapproved",
    "mutationapproved",
    "approvalclass",
    "whynow",
    "whynotalternative",
    "proofafterfix",
]
REQUIRED_AUTHORITY_RECEIPT_FIELDS = [
    "role",
    "packetstatus",
    "artifactstatematch",
    "directionstatematch",
    "scopematch",
    "scopedcommentids",
    "clearanceadded",
    "vetoadded",
    "usedfor",
    "reason",
]
REQUIRED_AUTHORITY_FIELDS = [
    "id",
    "evidence",
    "directionownership",
    "criticality",
    "nochange",
    "validationvalue",
    "fixshape",
    "authoritystatus",
    "packetrefs",
]
REQUIRED_VETO_FIELDS = [
    "id",
    "vetosource",
    "vetoclass",
    "vetoclaim",
    "evidenceref",
    "requiredtoclear",
    "finalroute",
]
REQUIRED_RESOLVE_FIELDS = ["id", "decision", "reason", "proofref", "next", "routerationale"]
REQUIRED_GATE_FIELDS = [
    "artifactstatecoverage",
    "directioncontextcoverage",
    "commentinventorycoverage",
    "identitycoverage",
    "decisiontestcoverage",
    "directionfitcoverage",
    "severityclaimcoverage",
    "mutationapprovalcoverage",
    "p2plusacceptancecoverage",
    "nochangecoverage",
    "dispositioncoverage",
    "proposedfixseparation",
    "evidencerefcoverage",
    "validationvaluecoverage",
    "resolveselectioncoverage",
    "resolvecountercasecoverage",
    "handoffagendaconsistency",
    "sourcepressureaudit",
    "selectionskewaudit",
    "p2plusseverityaudit",
    "directionfitaudit",
    "invariantpass",
    "authorityfanoutrequired",
    "authoritypacketcoverage",
    "authorityclearancecoverage",
    "authorityvetocoverage",
    "permissiveoverrideabsent",
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
    "Mutation Approval Tests",
    "No-Change Countercases",
    "Governing Invariant Ledger",
    "Act On",
    "Rebut",
    "Defer / Out of Scope",
    "Need Evidence",
    "Authority Packet Receipts",
    "Authority Clearance Matrix",
    "Authority Veto Ledger",
    "Resolve Selection",
    "Resolve Countercases",
    "Invariant-Level Handoff",
    "Acceptance Skew Audit",
    "P2+ Severity Audit",
    "Direction Fit Audit",
    "Source Pressure Audit",
    "Selection Skew Audit",
    "Adjudication Gate",
    "Handoff Agenda",
    "Adjudication Bottom Line",
]
OPTIONAL_SINGLETON_SECTIONS = {
    "All-Action Justification",
    "All-Selected Justification",
    "All-P2+ Accepted Justification",
    "All-Current-Finding Selected Justification",
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
    "mutationapproval": "mutation approval",
    "validationonlyalternative": "validation-only alternative",
    "sharedinvariant": "shared-invariant",
}
ALL_SELECTED_CHECKS = {
    "stalealreadyfixedalternative": "stale/already-fixed alternative",
    "proofonlythreadresolutionalternative": "proof-only thread-resolution alternative",
    "donotaddressalternative": "do-not-address alternative",
    "validatebeforemutationalternative": "validate-before-mutation alternative",
    "outofscopedeferalternative": "out-of-scope/defer alternative",
    "validbutnotthispralternative": "valid-but-not-this-PR alternative",
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
ALL_CURRENT_FINDING_SELECTED_CHECKS = {
    "artifactreachabilityproof": "artifact/reachability proof",
    "caswronghypothesisalternative": "CAS/Codex wrong-hypothesis alternative",
    "validbutnotthispralternative": "valid-but-not-this-PR alternative",
    "proofonlyalternative": "proof-only alternative",
    "validatebeforemutation": "validate-before-mutation",
    "directionandscopeownership": "direction and scope ownership",
    "mutationbudgetjustification": "mutation budget justification",
}

EMPTY_MARKERS = {"", "-", "—", "n/a", "na", "unknown", "missing", "none", "[]"}
GENERIC_EVIDENCE = {
    "code",
    "code-supports-it",
    "artifact-evidence",
    "current-artifacts",
    "review",
    "reviewer-said-so",
    "cas-said-so",
    "codex-said-so",
    "looks-right",
    "tests",
}

COLUMN_ALIASES = {
    "idthread": "id",
    "id": "id",
    "commentid": "id",
    "threadid": "id",
    "reviewcommentid": "id",
    "reviewer": "reviewer",
    "author": "reviewer",
    "reviewsource": "reviewsource",
    "source": "reviewsource",
    "revieworigin": "reviewsource",
    "origin": "reviewsource",
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
    "approvalclass": "approvalclass",
    "approval": "approvalclass",
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
    "sourceref": "directionref",
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
MUTATION_ALIASES = {
    "idthread": "id",
    "id": "id",
    "commentid": "id",
    "threadid": "id",
    "concernapproved": "concernapproved",
    "concernapproval": "concernapproved",
    "fixapproved": "fixapproved",
    "fixapproval": "fixapproved",
    "mutationapproved": "mutationapproved",
    "mutationapproval": "mutationapproved",
    "approvalclass": "approvalclass",
    "approval": "approvalclass",
    "whynow": "whynow",
    "whymutatenow": "whynow",
    "whynotalternative": "whynotalternative",
    "whynotvalidationdeferproof": "whynotalternative",
    "proofafterfix": "proofafterfix",
    "proof": "proofafterfix",
}
AUTHORITY_RECEIPT_ALIASES = {
    "role": "role",
    "packetstatus": "packetstatus",
    "status": "packetstatus",
    "artifactstatematch": "artifactstatematch",
    "artifactmatch": "artifactstatematch",
    "directionstatematch": "directionstatematch",
    "directionmatch": "directionstatematch",
    "scopematch": "scopematch",
    "scope": "scopematch",
    "scopedcommentids": "scopedcommentids",
    "commentids": "scopedcommentids",
    "clearanceadded": "clearanceadded",
    "clearance": "clearanceadded",
    "vetoadded": "vetoadded",
    "veto": "vetoadded",
    "usedfor": "usedfor",
    "reason": "reason",
}
AUTHORITY_ALIASES = {
    "idthread": "id",
    "id": "id",
    "commentid": "id",
    "threadid": "id",
    "evidence": "evidence",
    "evidenceclearance": "evidence",
    "directionownership": "directionownership",
    "directionownershipclearance": "directionownership",
    "direction": "directionownership",
    "ownership": "directionownership",
    "criticality": "criticality",
    "criticalityclearance": "criticality",
    "nochange": "nochange",
    "nochangeclearance": "nochange",
    "validationvalue": "validationvalue",
    "validation": "validationvalue",
    "validationvalueclearance": "validationvalue",
    "fixshape": "fixshape",
    "fixshapeclearance": "fixshape",
    "authoritystatus": "authoritystatus",
    "status": "authoritystatus",
    "packetrefs": "packetrefs",
    "packets": "packetrefs",
}
VETO_ALIASES = {
    "idthread": "id",
    "id": "id",
    "commentid": "id",
    "threadid": "id",
    "vetosource": "vetosource",
    "source": "vetosource",
    "vetoclass": "vetoclass",
    "class": "vetoclass",
    "vetoclaim": "vetoclaim",
    "claim": "vetoclaim",
    "evidenceref": "evidenceref",
    "evidence": "evidenceref",
    "requiredtoclear": "requiredtoclear",
    "clearancecondition": "requiredtoclear",
    "finalroute": "finalroute",
    "route": "finalroute",
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
    "mutationapprovalcoverage": "mutationapprovalcoverage",
    "mutationcoverage": "mutationapprovalcoverage",
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
    "sourcepressureaudit": "sourcepressureaudit",
    "sourceaudit": "sourcepressureaudit",
    "selectionskewaudit": "selectionskewaudit",
    "selectionaudit": "selectionskewaudit",
    "p2plusseverityaudit": "p2plusseverityaudit",
    "p2severityaudit": "p2plusseverityaudit",
    "directionfitaudit": "directionfitaudit",
    "directionaudit": "directionfitaudit",
    "invariantpass": "invariantpass",
    "authorityfanoutrequired": "authorityfanoutrequired",
    "fanoutrequired": "authorityfanoutrequired",
    "authoritypacketcoverage": "authoritypacketcoverage",
    "authoritypackets": "authoritypacketcoverage",
    "authorityclearancecoverage": "authorityclearancecoverage",
    "authorityclearance": "authorityclearancecoverage",
    "authorityvetocoverage": "authorityvetocoverage",
    "authorityveto": "authorityvetocoverage",
    "permissiveoverrideabsent": "permissiveoverrideabsent",
    "overrideabsent": "permissiveoverrideabsent",
    "specialistpacketcoverage": "authoritypacketcoverage",
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


def norm_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.strip().lower())


def norm_value(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[`*_]", "", value)
    value = re.sub(r"\s+", "-", value)
    return value


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
    if any(token in normalized for token in ["test", "ci", "cmd", "command", "log", "thread", "pr#", "gh-", "github", "diff", "src/", "tests/", "commit", "plan", "st-", "seq", "artifact", "fixture", "sha"]):
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
        buckets[bucket] = present if present else parse_id_list(raw)
    return buckets


def validate_structured_table(text: str, title: str, checks: Dict[str, str], errors: List[str], why_column_name: str) -> None:
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


def validate_authority_receipts(text: str, gate: Dict[str, str], errors: List[str]) -> None:
    coverage = gate.get("authoritypacketcoverage")
    block = section_text(text, "Authority Packet Receipts")
    if coverage == "pass" and not block.strip():
        errors.append("authority_packet_coverage is `pass` but Authority Packet Receipts is missing or empty")
    headers, rows = extract_first_table(block)
    header_map, receipt_rows = normalize_rows(headers, rows, AUTHORITY_RECEIPT_ALIASES)
    require_columns("Authority Packet Receipts", header_map, REQUIRED_AUTHORITY_RECEIPT_FIELDS, errors)
    if not receipt_rows:
        errors.append("Authority Packet Receipts has no data rows")
        return
    required_roles = set(ALLOWED_AUTHORITY_ROLE)
    seen_roles = set()
    for idx, row in enumerate(receipt_rows, start=1):
        label = row.get("role", f"receipt row {idx}") or f"receipt row {idx}"
        role = norm_value(row.get("role", ""))
        status = norm_value(row.get("packetstatus", ""))
        artifact_match = norm_value(row.get("artifactstatematch", ""))
        direction_match = norm_value(row.get("directionstatematch", ""))
        scope_match = norm_value(row.get("scopematch", ""))
        if role not in ALLOWED_AUTHORITY_ROLE:
            errors.append(f"{label}: invalid authority role `{row.get('role', '')}`")
        else:
            seen_roles.add(role)
        if status not in ALLOWED_PACKET_STATUS:
            errors.append(f"{label}: invalid authority packet status `{row.get('packetstatus', '')}`")
        for field_name, value in [
            ("artifact_state_match", artifact_match),
            ("direction_state_match", direction_match),
            ("scope_match", scope_match),
        ]:
            if value not in ALLOWED_PACKET_MATCH:
                errors.append(f"{label}: invalid {field_name} `{value}`")
        if status in {"accepted", "root-equivalent"}:
            if artifact_match == "no" or direction_match == "no" or scope_match == "no":
                errors.append(f"{label}: accepted/root-equivalent authority packet must match artifact, direction, and scope")
            if is_empty(row.get("scopedcommentids", "")):
                errors.append(f"{label}: authority packet requires scoped comment ids")
            if is_empty(row.get("usedfor", "")):
                errors.append(f"{label}: authority packet requires used_for")
        if is_empty(row.get("reason", "")):
            errors.append(f"{label}: authority packet requires reason")
    missing_roles = sorted(required_roles - seen_roles)
    if missing_roles:
        errors.append("Authority Packet Receipts missing required authority roles: " + ", ".join(missing_roles))


def require_columns(name: str, header_map: Dict[str, str], required: Iterable[str], errors: List[str]) -> None:
    missing = [field for field in required if field not in header_map]
    if missing:
        errors.append(f"{name} missing required columns: " + ", ".join(missing))


def validate_adjudication(text: str) -> CheckResult:
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
    ledger_header_map, rows = normalize_rows(ledger_headers, raw_rows, COLUMN_ALIASES)
    require_columns("Comment Ledger", ledger_header_map, REQUIRED_LEDGER_FIELDS, errors)
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
    require_columns("Decision Tests", decision_header_map, REQUIRED_DECISION_FIELDS, errors)
    if not decision_rows:
        errors.append("Decision Tests has no data rows")
    decisions = rows_by_id(decision_rows)

    direction_headers, direction_raw_rows = extract_first_table(section_text(text, "Direction Tests"))
    direction_header_map, direction_rows = normalize_rows(direction_headers, direction_raw_rows, DIRECTION_ALIASES)
    require_columns("Direction Tests", direction_header_map, REQUIRED_DIRECTION_FIELDS, errors)
    if not direction_rows:
        errors.append("Direction Tests has no data rows")
    directions = rows_by_id(direction_rows)

    severity_headers, severity_raw_rows = extract_first_table(section_text(text, "Severity Tests"))
    severity_header_map, severity_rows = normalize_rows(severity_headers, severity_raw_rows, SEVERITY_ALIASES)
    require_columns("Severity Tests", severity_header_map, REQUIRED_SEVERITY_FIELDS, errors)
    if not severity_rows:
        errors.append("Severity Tests has no data rows")
    severities = rows_by_id(severity_rows)

    mutation_headers, mutation_raw_rows = extract_first_table(section_text(text, "Mutation Approval Tests"))
    mutation_header_map, mutation_rows = normalize_rows(mutation_headers, mutation_raw_rows, MUTATION_ALIASES)
    require_columns("Mutation Approval Tests", mutation_header_map, REQUIRED_MUTATION_FIELDS, errors)
    if not mutation_rows:
        errors.append("Mutation Approval Tests has no data rows")
    mutations = rows_by_id(mutation_rows)

    authority_receipt_headers, authority_receipt_raw_rows = extract_first_table(section_text(text, "Authority Packet Receipts"))
    authority_receipt_header_map, authority_receipt_rows = normalize_rows(authority_receipt_headers, authority_receipt_raw_rows, AUTHORITY_RECEIPT_ALIASES)
    require_columns("Authority Packet Receipts", authority_receipt_header_map, REQUIRED_AUTHORITY_RECEIPT_FIELDS, errors)
    if not authority_receipt_rows:
        errors.append("Authority Packet Receipts has no data rows")

    authority_headers, authority_raw_rows = extract_first_table(section_text(text, "Authority Clearance Matrix"))
    authority_header_map, authority_rows = normalize_rows(authority_headers, authority_raw_rows, AUTHORITY_ALIASES)
    require_columns("Authority Clearance Matrix", authority_header_map, REQUIRED_AUTHORITY_FIELDS, errors)
    if not authority_rows:
        errors.append("Authority Clearance Matrix has no data rows")
    authority_by_id = rows_by_id(authority_rows)

    veto_headers, veto_raw_rows = extract_first_table(section_text(text, "Authority Veto Ledger"))
    veto_header_map, veto_rows = normalize_rows(veto_headers, veto_raw_rows, VETO_ALIASES)
    require_columns("Authority Veto Ledger", veto_header_map, REQUIRED_VETO_FIELDS, errors)
    vetoes_by_id: Dict[str, List[Dict[str, str]]] = {}
    if veto_rows:
        for veto in veto_rows:
            vid = veto.get("id", "").strip()
            if vid and vid not in {"none", "n/a", "na"}:
                vetoes_by_id.setdefault(vid, []).append(veto)

    ledger_by_id = rows_by_id(rows)
    nochange_section = section_text(text, "No-Change Countercases")
    resolve_countercase_section = section_text(text, "Resolve Countercases")

    act_count = validation_count = reply_count = non_action_count = blocked_count = 0
    p2_count = p2_accepted = p2_downgraded = p2_rejected = p2_unresolved = 0
    current_auto_review_ids: List[str] = []

    for idx, auth in enumerate(authority_rows, start=1):
        label = auth.get("id", f"authority row {idx}") or f"authority row {idx}"
        if label not in ledger_ids:
            errors.append(f"{label}: Authority Clearance Matrix row has no matching ledger row")
        evidence_clearance = norm_value(auth.get("evidence", ""))
        direction_clearance = norm_value(auth.get("directionownership", ""))
        criticality_clearance = norm_value(auth.get("criticality", ""))
        nochange_clearance = norm_value(auth.get("nochange", ""))
        validation_clearance = norm_value(auth.get("validationvalue", ""))
        fixshape_clearance = norm_value(auth.get("fixshape", ""))
        authority_status = norm_value(auth.get("authoritystatus", ""))
        if evidence_clearance not in AUTHORITY_CLEARANCE_VALUES:
            errors.append(f"{label}: invalid evidence authority clearance `{evidence_clearance}`")
        if direction_clearance not in AUTHORITY_CLEARANCE_VALUES:
            errors.append(f"{label}: invalid direction/ownership authority clearance `{direction_clearance}`")
        if criticality_clearance not in AUTHORITY_CLEARANCE_VALUES:
            errors.append(f"{label}: invalid criticality authority clearance `{criticality_clearance}`")
        if nochange_clearance not in NO_CHANGE_CLEARANCE_VALUES:
            errors.append(f"{label}: invalid no-change authority clearance `{nochange_clearance}`")
        if validation_clearance not in VALIDATION_CLEARANCE_VALUES:
            errors.append(f"{label}: invalid validation-value authority clearance `{validation_clearance}`")
        if fixshape_clearance not in AUTHORITY_CLEARANCE_VALUES:
            errors.append(f"{label}: invalid fix-shape authority clearance `{fixshape_clearance}`")
        if authority_status not in ALLOWED_AUTHORITY_STATUS:
            errors.append(f"{label}: invalid authority status `{authority_status}`")
        if is_empty(auth.get("packetrefs", "")):
            errors.append(f"{label}: Authority Clearance Matrix requires packet refs")

    for idx, veto in enumerate(veto_rows, start=1):
        label = veto.get("id", f"veto row {idx}") or f"veto row {idx}"
        if norm_value(label) in {"none", "n/a", "na"}:
            continue
        if label not in ledger_ids:
            errors.append(f"{label}: Authority Veto Ledger row has no matching ledger row")
        source = norm_value(veto.get("vetosource", ""))
        veto_class = norm_value(veto.get("vetoclass", ""))
        final_route = norm_value(veto.get("finalroute", ""))
        if source not in ALLOWED_AUTHORITY_ROLE and source != "root":
            errors.append(f"{label}: invalid veto source `{veto.get('vetosource', '')}`")
        if veto_class not in ALLOWED_VETO_CLASS:
            errors.append(f"{label}: invalid veto class `{veto.get('vetoclass', '')}`")
        if not evidence_ref_is_concrete(veto.get("evidenceref", ""), allow_missing=True):
            errors.append(f"{label}: veto requires concrete evidence ref or explicit missing marker")
        if is_empty(veto.get("vetoclaim", "")):
            errors.append(f"{label}: veto requires claim")
        if is_empty(veto.get("requiredtoclear", "")):
            errors.append(f"{label}: veto requires required_to_clear")
        if final_route not in ALLOWED_VETO_FINAL_ROUTE:
            errors.append(f"{label}: veto final route must not be address, got `{veto.get('finalroute', '')}`")

    for idx, row in enumerate(rows, start=1):
        label = row.get("id", f"row {idx}") or f"row {idx}"
        for field_name in ["id", "reviewer", "location", "excerpt", "claim"]:
            if is_empty(row.get(field_name, "")):
                errors.append(f"{label}: missing raw identity field `{field_name}`")
        if label not in nochange_section:
            errors.append(f"{label}: missing No-Change Countercases entry")
        if label not in resolve_countercase_section:
            errors.append(f"{label}: missing Resolve Countercases entry")

        review_source = norm_value(row.get("reviewsource", ""))
        severity = norm_value(row.get("severity", ""))
        criticality = norm_value(row.get("criticality", ""))
        severity_status = norm_value(row.get("severitystatus", ""))
        direction_fit = norm_value(row.get("directionfit", ""))
        direction_ref = row.get("directionref", "")
        approval_class = row.get("approvalclass", "").strip()
        approval_class_norm = approval_class
        mutation_value = norm_value(row.get("mutationvalue", ""))
        relevance = norm_value(row.get("relevance", ""))
        disposition = norm_value(row.get("disposition", ""))
        nochange = norm_value(row.get("nochange", ""))
        concern = norm_value(row.get("concern", ""))
        proposed = norm_value(row.get("proposed", ""))
        evidence_grade = norm_value(row.get("evidencegrade", ""))
        evidence_ref = row.get("evidenceref", "")
        severity_proof_ref = row.get("severityproofref", "")
        handoff = norm_value(row.get("handoff", ""))

        if review_source not in ALLOWED_REVIEW_SOURCE:
            errors.append(f"{label}: invalid review source `{row.get('reviewsource', '')}`")
        if severity not in ALLOWED_SEVERITY:
            errors.append(f"{label}: invalid reviewer severity claim `{row.get('severity', '')}`")
        if criticality not in ALLOWED_CRITICALITY:
            errors.append(f"{label}: invalid accepted criticality `{row.get('criticality', '')}`")
        if severity_status not in ALLOWED_SEVERITY_STATUS:
            errors.append(f"{label}: invalid severity acceptance status `{row.get('severitystatus', '')}`")
        if direction_fit not in ALLOWED_DIRECTION_FIT:
            errors.append(f"{label}: invalid direction fit `{row.get('directionfit', '')}`")
        if approval_class_norm not in ALLOWED_APPROVAL_CLASS:
            errors.append(f"{label}: invalid approval class `{approval_class}`")
        if mutation_value not in ALLOWED_MUTATION_VALUE:
            errors.append(f"{label}: invalid mutation value `{row.get('mutationvalue', '')}`")
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
            decision_fresh = ""
            decision_resolution = ""
        else:
            grounded = norm_value(decision.get("grounded", ""))
            material = norm_value(decision.get("material", ""))
            fresh = norm_value(decision.get("fresh", ""))
            diagnosis = norm_value(decision.get("diagnosis", ""))
            scopefit = norm_value(decision.get("scopefit", ""))
            resolutionvalue = norm_value(decision.get("resolutionvalue", ""))
            nochangedefeated = norm_value(decision.get("nochangedefeated", ""))
            decision_fresh = fresh
            decision_resolution = resolutionvalue
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
            if resolutionvalue == "review-closure" and disposition == "act":
                errors.append(f"{label}: review-closure resolution value cannot justify `act`")

        direction = directions.get(label)
        if not direction:
            errors.append(f"{label}: missing Direction Tests row")
        else:
            direction_source = norm_value(direction.get("directionsource", ""))
            source_freshness = norm_value(direction.get("sourcefreshness", ""))
            same_objective = norm_value(direction.get("sameobjective", ""))
            direction_row_fit = norm_value(direction.get("directionfit", ""))
            direction_override = norm_value(direction.get("directionoverride", ""))
            nongoal_conflict = norm_value(direction.get("nongoalconflict", ""))
            if direction_source not in ALLOWED_DIRECTION_SOURCE:
                errors.append(f"{label}: invalid direction source `{direction_source}`")
            if source_freshness not in ALLOWED_SOURCE_FRESHNESS:
                errors.append(f"{label}: invalid source freshness `{source_freshness}`")
            if same_objective not in ALLOWED_SAME_OBJECTIVE:
                errors.append(f"{label}: invalid same objective `{same_objective}`")
            if direction_row_fit not in ALLOWED_DIRECTION_FIT:
                errors.append(f"{label}: invalid Direction Tests direction fit `{direction_row_fit}`")
            if direction_fit and direction_row_fit and direction_fit != direction_row_fit:
                errors.append(f"{label}: Comment Ledger direction fit conflicts with Direction Tests")
            if direction_override not in ALLOWED_DIRECTION_OVERRIDE:
                errors.append(f"{label}: invalid direction override `{direction_override}`")
            if nongoal_conflict not in ALLOWED_YES_NO_UNKNOWN:
                errors.append(f"{label}: invalid non-goal conflict `{nongoal_conflict}`")
            if is_empty(direction.get("minevidencedirection", "")):
                errors.append(f"{label}: missing minimum evidence to change direction")
            if direction_source in {"proposed-plan", "st-plan", "update-plan", "seq-recovered"} and source_freshness != "current" and disposition == "act":
                errors.append(f"{label}: stale/off-target/unknown plan direction cannot justify `act`")
            if same_objective != "yes" and disposition == "act" and direction_fit != "direction-overriding":
                errors.append(f"{label}: `act` needs same-objective direction or direction-overriding proof")

        severity_row = severities.get(label)
        if not severity_row:
            errors.append(f"{label}: missing Severity Tests row")
        else:
            sev = norm_value(severity_row.get("severity", ""))
            crit = norm_value(severity_row.get("criticality", ""))
            status = norm_value(severity_row.get("severitystatus", ""))
            p2accepted = norm_value(severity_row.get("p2accepted", ""))
            if sev not in ALLOWED_SEVERITY:
                errors.append(f"{label}: invalid Severity Tests severity `{sev}`")
            if crit not in ALLOWED_CRITICALITY:
                errors.append(f"{label}: invalid Severity Tests criticality `{crit}`")
            if status not in ALLOWED_SEVERITY_STATUS:
                errors.append(f"{label}: invalid Severity Tests severity status `{status}`")
            if p2accepted not in ALLOWED_P2_ACCEPTED:
                errors.append(f"{label}: invalid p2+ accepted value `{p2accepted}`")
            if severity and sev and severity != sev:
                errors.append(f"{label}: Comment Ledger severity conflicts with Severity Tests")
            if criticality and crit and criticality != crit:
                errors.append(f"{label}: Comment Ledger criticality conflicts with Severity Tests")
            if severity_status and status and severity_status != status:
                errors.append(f"{label}: Comment Ledger severity status conflicts with Severity Tests")
            if is_empty(severity_row.get("minevidenceseverity", "")):
                errors.append(f"{label}: missing minimum evidence to accept severity")
            if severity in P2_PLUS:
                p2_count += 1
                if severity_status == "accepted":
                    p2_accepted += 1
                    if p2accepted != "yes":
                        errors.append(f"{label}: P2+ accepted row must set p2+ accepted=yes")
                    if criticality not in IMPLEMENTATION_CRITICALITY:
                        errors.append(f"{label}: accepted P2+ severity requires implementation-grade criticality")
                    if not evidence_ref_is_concrete(severity_proof_ref):
                        errors.append(f"{label}: accepted P2+ severity requires concrete severity proof ref")
                elif severity_status == "downgraded":
                    p2_downgraded += 1
                    if p2accepted != "no":
                        errors.append(f"{label}: downgraded P2+ row must set p2+ accepted=no")
                    if is_empty(severity_row.get("downgradereason", "")):
                        errors.append(f"{label}: downgraded P2+ row needs downgrade/reject reason")
                elif severity_status == "rejected":
                    p2_rejected += 1
                    if p2accepted != "no":
                        errors.append(f"{label}: rejected P2+ row must set p2+ accepted=no")
                    if is_empty(severity_row.get("downgradereason", "")):
                        errors.append(f"{label}: rejected P2+ row needs downgrade/reject reason")
                elif severity_status == "unresolved":
                    p2_unresolved += 1
            elif p2accepted != "not-p2plus":
                errors.append(f"{label}: non-P2+ row must set p2+ accepted=not-p2plus")

        mutation = mutations.get(label)
        if not mutation:
            errors.append(f"{label}: missing Mutation Approval Tests row")
        else:
            concernapproved = norm_value(mutation.get("concernapproved", ""))
            fixapproved = norm_value(mutation.get("fixapproved", ""))
            mutationapproved = norm_value(mutation.get("mutationapproved", ""))
            mutation_approval_class = mutation.get("approvalclass", "").strip()
            if concernapproved not in ALLOWED_APPROVAL_BOOL:
                errors.append(f"{label}: invalid concern approved value `{concernapproved}`")
            if fixapproved not in ALLOWED_FIX_APPROVAL:
                errors.append(f"{label}: invalid fix approved value `{fixapproved}`")
            if mutationapproved not in {"yes", "no", "unknown"}:
                errors.append(f"{label}: invalid mutation approved value `{mutationapproved}`")
            if mutation_approval_class not in ALLOWED_APPROVAL_CLASS:
                errors.append(f"{label}: invalid Mutation Approval Tests approval class `{mutation_approval_class}`")
            if mutation_approval_class != approval_class_norm:
                errors.append(f"{label}: Comment Ledger approval class conflicts with Mutation Approval Tests")
            for field_name in ["whynow", "whynotalternative"]:
                if is_empty(mutation.get(field_name, "")):
                    errors.append(f"{label}: Mutation Approval Tests missing `{field_name}`")
            if disposition == "act":
                if mutationapproved != "yes":
                    errors.append(f"{label}: `act` requires mutation approved=yes")
                if concernapproved != "yes":
                    errors.append(f"{label}: `act` requires concern approved=yes")
                if fixapproved not in {"yes", "partial", "no-suggested-fix"}:
                    errors.append(f"{label}: `act` requires approved fix or replacement fix shape")
                if not evidence_ref_is_concrete(mutation.get("proofafterfix", "")):
                    errors.append(f"{label}: `act` requires concrete proof after fix")
            else:
                if mutationapproved == "yes":
                    errors.append(f"{label}: mutation approved=yes is legal only for `act` rows")

        if review_source in AUTO_REVIEW_SOURCES and decision_fresh == "current":
            current_auto_review_ids.append(label)

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
            if direction_fit not in ACT_DIRECTION_FIT:
                errors.append(f"{label}: `act` requires direction_fit aligned or direction-overriding")
            if not evidence_ref_is_concrete(direction_ref):
                errors.append(f"{label}: `act` requires concrete direction ref")
            if mutation_value != "codebase-material":
                errors.append(f"{label}: `act` requires mutation_value codebase-material")
            if criticality not in IMPLEMENTATION_CRITICALITY:
                errors.append(f"{label}: `act` requires implementation-grade accepted criticality")
            if approval_class_norm not in ADDRESS_APPROVAL_CLASSES:
                errors.append(f"{label}: `act` requires A-class mutation approval, got `{approval_class_norm}`")
            if proposed == "validation-only":
                errors.append(f"{label}: `act` cannot use proposed-fix validity `validation-only`")
            if severity in P2_PLUS and severity_status != "accepted":
                errors.append(f"{label}: P2+ `act` requires accepted severity")
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
                if norm_value(decision.get("resolutionvalue", "")) not in IMPLEMENTATION_RESOLUTION_VALUES:
                    errors.append(f"{label}: `act` requires implementation-grade resolution value")
                if norm_value(decision.get("nochangedefeated", "")) != "yes":
                    errors.append(f"{label}: `act` requires no-change defeated=yes")
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
            if mutation_value != "validation-material":
                errors.append(f"{label}: `need-evidence` requires mutation_value validation-material")
            if approval_class_norm not in VALIDATION_APPROVAL_CLASSES:
                errors.append(f"{label}: `need-evidence` should use B1 route-changing validation approval class")
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
        if disposition == "blocked":
            blocked_count += 1
            if mutation_value != "blocked" or approval_class_norm != "blocked":
                errors.append(f"{label}: `blocked` requires mutation_value=blocked and approval_class=blocked")

    resolve_headers, resolve_raw_rows = extract_first_table(section_text(text, "Resolve Selection"))
    resolve_header_map, resolve_rows = normalize_rows(resolve_headers, resolve_raw_rows, RESOLVE_ALIASES)
    require_columns("Resolve Selection", resolve_header_map, REQUIRED_RESOLVE_FIELDS, errors)
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
        mutation_row = mutations.get(label)
        if not ledger_row:
            continue
        disposition = norm_value(ledger_row.get("disposition", ""))
        nochange = norm_value(ledger_row.get("nochange", ""))
        handoff = norm_value(ledger_row.get("handoff", ""))
        direction_fit = norm_value(ledger_row.get("directionfit", ""))
        severity = norm_value(ledger_row.get("severity", ""))
        severity_status = norm_value(ledger_row.get("severitystatus", ""))
        criticality = norm_value(ledger_row.get("criticality", ""))
        mutation_value = norm_value(ledger_row.get("mutationvalue", ""))
        approval_class = ledger_row.get("approvalclass", "").strip()
        mutation_approved = norm_value((mutation_row or {}).get("mutationapproved", ""))
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
                errors.append(f"{label}: address requires implementation-grade criticality")
            if approval_class not in ADDRESS_APPROVAL_CLASSES:
                errors.append(f"{label}: address requires A-class approval class")
            if mutation_approved != "yes":
                errors.append(f"{label}: address requires mutation approved=yes")
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
            if approval_class not in VALIDATION_APPROVAL_CLASSES:
                errors.append(f"{label}: validate-only requires B1 route-changing validation approval class")
            if mutation_approved == "yes":
                errors.append(f"{label}: validate-only must not approve mutation yet")
        elif decision_value == "resolve-thread-only":
            if disposition == "act":
                errors.append(f"{label}: resolve-thread-only conflicts with disposition `act`")
            if route_rationale != "proof-only-thread":
                errors.append(f"{label}: resolve-thread-only requires route rationale `proof-only-thread`")
            if handoff in IMPLEMENTATION_HANDOFFS:
                errors.append(f"{label}: resolve-thread-only cannot use implementation handoff `{handoff}`")
            if mutation_value != "proof-only":
                errors.append(f"{label}: resolve-thread-only requires mutation_value proof-only")
            if approval_class not in PROOF_ONLY_APPROVAL_CLASSES:
                warnings.append(f"{label}: resolve-thread-only usually uses B2 or C3 approval class")
        elif decision_value == "do-not-address":
            if disposition == "act":
                errors.append(f"{label}: do-not-address conflicts with disposition `act`")
            if route_rationale != "no-change":
                errors.append(f"{label}: do-not-address requires route rationale `no-change`")
            if mutation_value not in {"no-change", "reply-only"}:
                errors.append(f"{label}: do-not-address requires mutation_value no-change or reply-only")
            if approval_class not in NO_ADDRESS_APPROVAL_CLASSES:
                warnings.append(f"{label}: do-not-address usually uses B3/B4/C-class approval class")
            if norm_value(next_action) not in {"none", "", "no", "n/a", "na"} and "reply" not in norm_value(next_action):
                warnings.append(f"{label}: do-not-address usually uses next=none or proof/reply-only")
        elif decision_value == "blocked":
            if route_rationale != "blocked":
                errors.append(f"{label}: blocked requires route rationale `blocked`")
            if disposition != "blocked":
                errors.append(f"{label}: blocked resolve decision requires disposition blocked")

    for rid in ledger_ids:
        if rid not in authority_by_id:
            errors.append(f"{rid}: missing Authority Clearance Matrix row")
    for rid in sorted(set(authority_by_id) - set(ledger_ids)):
        errors.append(f"{rid}: Authority Clearance Matrix contains unknown comment id")

    for rid, auth in authority_by_id.items():
        if rid not in ledger_by_id:
            continue
        resolve = resolve_by_id.get(rid)
        if not resolve:
            continue
        decision_value = norm_value(resolve.get("decision", ""))
        evidence_clearance = norm_value(auth.get("evidence", ""))
        direction_clearance = norm_value(auth.get("directionownership", ""))
        criticality_clearance = norm_value(auth.get("criticality", ""))
        nochange_clearance = norm_value(auth.get("nochange", ""))
        validation_clearance = norm_value(auth.get("validationvalue", ""))
        fixshape_clearance = norm_value(auth.get("fixshape", ""))
        authority_status = norm_value(auth.get("authoritystatus", ""))
        has_veto = bool(vetoes_by_id.get(rid))
        if decision_value == "address":
            if authority_status != "cleared-for-address":
                errors.append(f"{rid}: address requires authority_status cleared-for-address")
            if evidence_clearance != "clear":
                errors.append(f"{rid}: address requires evidence authority clear")
            if direction_clearance != "clear":
                errors.append(f"{rid}: address requires direction/ownership authority clear")
            if criticality_clearance != "clear":
                errors.append(f"{rid}: address requires criticality authority clear")
            if nochange_clearance != "defeated":
                errors.append(f"{rid}: address requires no-change authority defeated")
            if validation_clearance != "mutate-now":
                errors.append(f"{rid}: address requires validation-value authority mutate-now")
            if fixshape_clearance != "clear":
                errors.append(f"{rid}: address requires fix-shape authority clear")
            if has_veto:
                errors.append(f"{rid}: address is forbidden while Authority Veto Ledger contains a veto")
        elif decision_value == "validate-only":
            if authority_status != "cleared-for-validation":
                errors.append(f"{rid}: validate-only requires authority_status cleared-for-validation")
            if validation_clearance != "validate-first":
                errors.append(f"{rid}: validate-only requires validation-value authority validate-first")
        elif decision_value == "resolve-thread-only":
            if authority_status != "proof-only":
                errors.append(f"{rid}: resolve-thread-only requires authority_status proof-only")
        elif decision_value == "do-not-address":
            if authority_status not in {"no-change", "defer"}:
                errors.append(f"{rid}: do-not-address requires authority_status no-change or defer")
        elif decision_value == "blocked":
            if authority_status != "blocked":
                errors.append(f"{rid}: blocked requires authority_status blocked")

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
    if p2_count > 0 and p2_accepted == p2_count:
        validate_structured_table(text, "All-P2+ Accepted Justification", ALL_P2_ACCEPTED_CHECKS, errors, "why accepted severity still warranted")
    if current_auto_review_ids:
        selected_auto = [rid for rid in current_auto_review_ids if rid in decision_buckets["address"] or rid in decision_buckets["validate-only"]]
        if len(selected_auto) == len(current_auto_review_ids):
            validate_structured_table(text, "All-Current-Finding Selected Justification", ALL_CURRENT_FINDING_SELECTED_CHECKS, errors, "why selected resolution still warranted")

    validate_authority_receipts(text, gate, errors)

    for title in ["Acceptance Skew Audit", "P2+ Severity Audit", "Direction Fit Audit", "Source Pressure Audit", "Selection Skew Audit"]:
        if not section_text(text, title).strip():
            errors.append(f"{title} is empty")

    bottom_line = section_text(text, "Adjudication Bottom Line")
    if (gate_failures or errors) and "blocked" not in bottom_line.lower():
        errors.append("failed gate or mechanical error requires blocked Adjudication Bottom Line")

    stats = {
        "comments": len(rows),
        "act": act_count,
        "non_action": non_action_count,
        "blocked": blocked_count,
        "validation_or_need_evidence": validation_count,
        "reply_rows": reply_count,
        "p2_plus": p2_count,
        "p2_accepted": p2_accepted,
        "p2_downgraded": p2_downgraded,
        "p2_rejected": p2_rejected,
        "p2_unresolved": p2_unresolved,
        "current_auto_review": len(current_auto_review_ids),
        "authority_vetoes": sum(len(v) for v in vetoes_by_id.values()),
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


# Backward-compatible entrypoint name used by older wrappers.
def check_adjudication(text: str) -> CheckResult:
    return validate_adjudication(text)


def print_human(result: CheckResult) -> None:
    if result.passed:
        print("PASS: Compact-Gated v6 adjudication gate contract satisfied")
    else:
        print("FAIL: Compact-Gated v6 adjudication gate contract incomplete")
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
  ci_state: local tests pass 2026-05-28

- branch / PR: feature/retry
- current artifact evidence: src/a.py and tests/test_a.py
- tests / CI: local pytest pass
- comments adjudicated: 4
- limits / unavailable evidence: none

## Direction Context Ledger

direction_state_id:
  source: PR-body
  source_ref: PR#9
  source_freshness: current
  same_objective: yes
  active_frontier: retry idempotence hardening
  locked_decisions: narrow idempotence guard only
  non_goals: public API rename
  compatibility_posture: preserve public API
  ownership_boundaries: retry module owns duplicate-write prevention
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

- intended_change: make retry idempotent without API rename
- explicit_constraints: narrow change
- non_goals: public API rename
- governing_invariants: retry idempotence
- evidence_source: PR body
- rationale_freshness: current
- staleness_source: none
- confidence: high

## Comment Ledger

| id/thread | reviewer | review source | location | excerpt | claim | reviewer severity claim | accepted criticality | severity acceptance status | direction fit | direction ref | approval class | mutation value | concern validity | proposed fix validity | relevance | disposition | no-change status | invariant | evidence grade | evidence ref | severity proof ref | handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1 | alice | github-review | src/a.py:10 | retry writes twice | retry path is not idempotent | P2 | correctness-critical | accepted | aligned | PR#9 retry idempotence | A1-current-owned-defect | codebase-material | valid | valid | material-relevant | act | defeated | retry idempotence | current-artifact | src/a.py:10 | src/a.py:10 duplicate write path | route-to-accretive-implementer |
| c2 | bob | cas-codex | src/a.py:12 | maybe flakes | flake risk needs proof | P3 | unknown | unresolved | aligned | PR#9 retry idempotence | B1-plausible-route-changing-validation | validation-material | unknown | validation-only | material-relevant | need-evidence | unresolved | retry idempotence | reviewer-only | thread:c2 | missing until repro | route-to-fixed-point-driver |
| c3 | cara | pr-thread | src/a.py:1 | already guarded | old duplicate-write comment is fixed | unlabeled | review-closure-only | downgraded | aligned | src/a.py:10 guard | B2-valid-already-fixed | proof-only | valid | not-applicable | stale-or-superseded | rebut | not-defeated | retry idempotence | current-artifact | src/a.py:10 | not-p2plus | none |
| c4 | dan | github-review | src/a.py:1 | rename helper | helper name should change | P2 | low-value | downgraded | conflicting | PR#9 non-goal public API rename | C2-preference-only | no-change | unsupported | not-applicable | preference-only | rebut | not-defeated | none | current-artifact | PR#9 non-goals | PR#9 non-goal public API rename | none |

## Decision Tests

| id/thread | grounded | material | fresh | diagnosis | scope-fit | resolution value | no-change defeated | min evidence to change mind |
|---|---|---|---|---|---|---|---|---|
| c1 | yes | yes | current | correct | yes | correctness-critical | yes | counterexample showing existing guard prevents duplicate write |
| c2 | unknown | yes | current | unknown | yes | validation-needed | unresolved | repro or failing test for flake |
| c3 | yes | no | superseded | correct | no | proof-only | no | latest HEAD lacking guard |
| c4 | no | no | current | unknown | no | low-value | no | repo naming convention or user goal |

## Direction Tests

| id/thread | direction source | source freshness | same objective | direction fit | direction ref | active frontier | non-goal conflict | direction override | min evidence to change direction |
|---|---|---|---|---|---|---|---|---|---|
| c1 | PR-body | current | yes | aligned | PR#9 retry idempotence | retry idempotence | no | not-needed | user expands PR beyond retry guard |
| c2 | PR-body | current | yes | aligned | PR#9 retry idempotence | retry idempotence | no | not-needed | PR says flakes are out of scope |
| c3 | current-artifact | current | yes | aligned | src/a.py:10 guard | retry idempotence | no | not-needed | latest HEAD loses guard |
| c4 | PR-body | current | yes | conflicting | PR#9 non-goal public API rename | retry idempotence | yes | no | user explicitly requests rename |

## Severity Tests

| id/thread | reviewer severity claim | accepted criticality | severity acceptance status | severity proof ref | downgrade/reject reason | p2+ accepted | min evidence to accept severity |
|---|---|---|---|---|---|---|---|
| c1 | P2 | correctness-critical | accepted | src/a.py:10 duplicate write path | n/a | yes | proof duplicate write is impossible |
| c2 | P3 | unknown | unresolved | missing until repro | no P2 label | not-p2plus | failing repro |
| c3 | unlabeled | review-closure-only | downgraded | src/a.py:10 guard | already fixed on HEAD | not-p2plus | not applicable |
| c4 | P2 | low-value | downgraded | PR#9 non-goal public API rename | severity label maps to non-goal preference | no | repo convention or user goal |

## Mutation Approval Tests

| id/thread | concern approved | fix approved | mutation approved | approval class | why now | why not alternative | proof after fix |
|---|---|---|---|---|---|---|---|
| c1 | yes | yes | yes | A1-current-owned-defect | current code admits duplicate write in PR-owned path | validation unnecessary because src/a.py:10 grounds defect | tests/test_a.py::test_retry_idempotent |
| c2 | unknown | not-applicable | no | B1-plausible-route-changing-validation | validation could decide whether flake is real | mutation before repro would be guesswork | tests/test_a.py::test_retry_flake_repro |
| c3 | yes | not-applicable | no | B2-valid-already-fixed | thread can be closed with proof | code already contains guard | src/a.py:10 |
| c4 | no | no | no | C2-preference-only | no mutation warranted | non-goal and no convention support | PR#9 non-goals |

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
  - strongest no-change case: already fixed on latest HEAD.
  - status: not-defeated
  - why defeated / preserved / unresolved: src/a.py:10 proves guard exists.
- c4:
  - strongest no-change case: rename is preference-only and direction-conflicting.
  - status: not-defeated
  - why defeated / preserved / unresolved: PR#9 names public API rename as non-goal.

## Governing Invariant Ledger

| invariant id | invariant | comments | evidence | violated/threatened | minimum fix shape | handoff | why not local fixes |
|---|---|---|---|---|---|---|---|
| inv1 | retry idempotence | c1,c2,c3 | src/a.py:10 | violated by c1, uncertain by c2, satisfied for c3 | add guard and validate flake | route-to-accretive-implementer for c1; validation for c2 | c1 is local, c2 proof-only validation |

## Act On

- c1: add the narrow idempotence guard; evidence src/a.py:10.

## Rebut

- c3: proof-only resolved; already fixed at src/a.py:10.
- c4: rebut as preference-only and direction-conflicting.

## Defer / Out of Scope

- none.

## Need Evidence

- c2: route validation-only repro/probe to fixed-point-driver.

## Authority Packet Receipts

| role | packet status | artifact state match | direction state match | scope match | scoped comment ids | clearance added | veto added | used for | reason |
|---|---|---|---|---|---|---|---|---|---|
| evidence-authority | root-equivalent | yes | yes | yes | c1,c2,c3,c4 | c1,c3 clear; c2 unresolved; c4 veto | c2,c3,c4 | grounding and reachability | root-equivalent current artifact pass covers all rows |
| direction-ownership-authority | root-equivalent | yes | yes | yes | c1,c2,c3,c4 | c1,c2,c3 clear; c4 veto | c4 | direction and PR ownership | PR#9 direction and non-goals are current |
| criticality-authority | root-equivalent | yes | yes | yes | c1,c2,c3,c4 | c1 clear; c2 unresolved; c3/c4 veto | c2,c3,c4 | severity and materiality | P2+ claims independently accepted or downgraded |
| no-change-advocate | root-equivalent | yes | yes | yes | c1,c2,c3,c4 | c1 defeated; c2 unresolved; c3/c4 veto | c2,c3,c4 | no-change pressure | strongest no-change cases preserved unless defeated |
| validation-value-authority | root-equivalent | yes | yes | yes | c1,c2,c3,c4 | c1 mutate-now; c2 validate-first; c3/c4 no-validation-value | c2,c3,c4 | validation gating | validation only chosen when route-changing |
| fix-shape-authority | root-equivalent | yes | yes | yes | c1,c2,c3,c4 | c1 clear; c2 unresolved; c3/c4 not-required | c2,c4 | minimum fix shape | mutation selected only where minimum fix is known |

## Authority Clearance Matrix

| id/thread | evidence | direction/ownership | criticality | no-change | validation-value | fix-shape | authority status | packet refs |
|---|---|---|---|---|---|---|---|---|
| c1 | clear | clear | clear | defeated | mutate-now | clear | cleared-for-address | authority:evidence:c1,authority:direction:c1,authority:criticality:c1,authority:nochange:c1,authority:validation:c1,authority:fix:c1 |
| c2 | unresolved | clear | unresolved | unresolved | validate-first | unresolved | cleared-for-validation | authority:evidence:c2,authority:direction:c2,authority:criticality:c2,authority:nochange:c2,authority:validation:c2,authority:fix:c2 |
| c3 | clear | clear | veto | veto | no-validation-value | not-required | proof-only | authority:evidence:c3,authority:direction:c3,authority:criticality:c3,authority:nochange:c3,authority:validation:c3,authority:fix:c3 |
| c4 | veto | veto | veto | veto | no-validation-value | not-required | no-change | authority:evidence:c4,authority:direction:c4,authority:criticality:c4,authority:nochange:c4,authority:validation:c4,authority:fix:c4 |

## Authority Veto Ledger

| id/thread | veto source | veto class | veto claim | evidence ref | required to clear | final route |
|---|---|---|---|---|---|---|
| c2 | validation-value-authority | validate-first | flake claim is plausible but unproven, so mutation is blocked until validation changes route | thread:c2 | failing repro or artifact proof | validate-only |
| c3 | no-change-advocate | already-fixed | latest HEAD already contains the guard, so mutation is unnecessary | src/a.py:10 | latest HEAD lacking guard | resolve-thread-only |
| c4 | direction-ownership-authority | direction-conflicting | rename conflicts with PR non-goal and lacks convention support | PR#9 non-goals | explicit user instruction or repo convention | do-not-address |

## Resolve Selection

| id/thread | resolve decision | reason | proof ref | next | route rationale |
|---|---|---|---|---|---|
| c1 | address | A1 current owned defect with defeated no-change case | src/a.py:10 | route-to-accretive-implementer | narrow-local |
| c2 | validate-only | B1 plausible failure needs route-changing validation proof | thread:c2 | route-to-fixed-point-driver | validation-only |
| c3 | resolve-thread-only | already fixed on latest HEAD | src/a.py:10 | reply with proof and resolve thread | proof-only-thread |
| c4 | do-not-address | P2 label downgraded to preference/non-goal | PR#9 non-goals | none | no-change |

## Resolve Countercases

- c1:
  - proposed resolve decision: address
  - strongest alternative resolve decision: validate-only
  - why alternative is rejected / preserved / unresolved: src/a.py:10 already grounds the duplicate-write defect.
- c2:
  - proposed resolve decision: validate-only
  - strongest alternative resolve decision: address
  - why alternative is rejected / preserved / unresolved: thread:c2 does not prove a failure yet.
- c3:
  - proposed resolve decision: resolve-thread-only
  - strongest alternative resolve decision: address
  - why alternative is rejected / preserved / unresolved: latest HEAD already has the guard.
- c4:
  - proposed resolve decision: do-not-address
  - strongest alternative resolve decision: address
  - why alternative is rejected / preserved / unresolved: PR#9 makes rename a non-goal.

## Invariant-Level Handoff

- invariant: retry idempotence
- affected comments: c1,c2,c3
- route: c1 narrow implementation, c2 validation-only, c3 proof-only
- minimum fix shape: guard duplicate write and prove with test
- proof required: pytest tests/test_a.py::test_retry_idempotent

## Acceptance Skew Audit

- disposition distribution: act=1, need-evidence=1, rebut=2
- acceptance pressure checked: mixed dispositions avoid all-action pressure
- stale/superseded possibilities: c3 already fixed
- unsupported possibilities: c4 unsupported
- preference-only possibilities: c4 preference-only
- out-of-scope possibilities: c4 direction-conflicting
- validation-only alternatives: c2
- shared-invariant pressure: c1/c2/c3 share retry idempotence

## P2+ Severity Audit

- P2+ count: 2
- accepted count: 1
- downgraded count: 1
- rejected count: 0
- unresolved count: 0
- accepted criticality distribution: correctness-critical=1, low-value=1
- unsupported severity labels: c4
- review-closure-only downgrades: none
- validation-only P2+ rows: none
- direction-conflicting P2+ rows: c4

## Direction Fit Audit

- direction source distribution: PR-body=3, current-artifact=1
- same-objective proof: PR#9 and current HEAD
- stale/off-target plan pressure: none
- conflicting-direction rows: c4
- direction-overriding rows: none
- rows where st/plan/update-plan changed disposition: none
- rows where direction was insufficient and blocked/need-evidence was chosen: none

## Source Pressure Audit

- review source distribution: github-review=2, cas-codex=1, pr-thread=1
- current automated findings: c2 only
- all-current-finding selected pressure: no, validation-only but no mutation
- CAS/Codex wrong-hypothesis alternatives: c2 preserved as validation-only
- current reviewer claim rebutted/deferred: c4

## Selection Skew Audit

- resolve decision distribution: address=1, validate-only=1, resolve-thread-only=1, do-not-address=1
- all-selected pressure checked: not all selected
- address over-selection possibilities: c2/c3/c4 rejected as address
- validate-only over-routing possibilities: only c2 validation-only
- proof-only thread-resolution alternatives: c3
- do-not-address alternatives: c4
- blocked/ask-user alternatives: none
- fixed-point over-routing pressure: c1 stays narrow-local; c2 validation only

## All-Current-Finding Selected Justification

| check | result | evidence ref | why selected resolution still warranted |
|---|---|---|---|
| artifact/reachability proof | pass | thread:c2 | selected as validation-only because artifact reachability is not yet proven |
| CAS wrong-hypothesis alternative | pass | thread:c2 | wrong-hypothesis alternative is preserved by requiring validation before mutation |
| valid-but-not-this-PR alternative | pass | PR#9 retry idempotence | if validated, the flake route belongs to the PR-owned retry invariant |
| proof-only alternative | pass | thread:c2 | no latest-HEAD proof resolves the flake claim yet |
| validate-before-mutation | pass | tests/test_a.py::test_retry_flake_repro | selected path is validation-only, not mutation |
| direction and scope ownership | pass | PR#9 retry idempotence | validation is scoped to retry idempotence and cannot mutate before proof |
| mutation budget justification | pass | thread:c2 | mutation budget is zero for c2 until validation proves the concern |

## Adjudication Gate

| field | value | basis |
|---|---|---|
| artifact_state_coverage | pass | artifact_state_id recorded |
| direction_context_coverage | pass | direction_state_id recorded |
| comment_inventory_coverage | pass | all four ids match ledger |
| identity_coverage | pass | all rows have raw identity |
| decision_test_coverage | pass | all rows have decision tests |
| direction_fit_coverage | pass | all rows have direction tests |
| severity_claim_coverage | pass | all rows have severity tests |
| mutation_approval_coverage | pass | all rows have mutation approval tests |
| p2_plus_acceptance_coverage | pass | P2 rows accepted/downgraded with proof |
| no_change_coverage | pass | all rows have countercases |
| disposition_coverage | pass | all rows have one disposition |
| proposed_fix_separation | pass | concern and fix split |
| evidence_ref_coverage | pass | act has current artifact evidence ref |
| validation_value_coverage | pass | validation-only c2 changes route |
| resolve_selection_coverage | pass | every ledger row has valid downstream selection |
| resolve_countercase_coverage | pass | every ledger row has resolve countercase |
| handoff_agenda_consistency | pass | agenda buckets match selection map |
| source_pressure_audit | pass | source pressure audited |
| selection_skew_audit | pass | skew audited |
| p2_plus_severity_audit | pass | P2+ severity audited |
| direction_fit_audit | pass | direction fit audited |
| invariant_pass | pass | invariant checked and named |
| authority_fanout_required | pass | authority panel considered and root-equivalent packets emitted |
| authority_packet_coverage | pass | all six authority lanes have accepted or root-equivalent packet receipts |
| authority_clearance_coverage | pass | every row has authority clearance matrix entry |
| authority_veto_coverage | pass | every veto is recorded and respected |
| permissive_override_absent | pass | no address row overrides veto or unresolved authority |
| acceptance_skew_audit | pass | skew audited |
| adjudication_complete | pass | all required fields pass |
| implementation_handoff_allowed | yes | c1 is artifact-backed address |
| validation_handoff_allowed | yes | c2 is validation-only |
| reply_handoff_allowed | yes | c3/c4 reply/proof cleanup allowed |

## Handoff Agenda

- implementation route: accretive-implementer
- validation route: fixed-point-driver
- proof-only thread-resolution route: reply/thread cleanup
- reply route: optional logophile
- items selected for implementation: c1
- validation-only items: c2
- proof-only thread-resolution items: c3
- items not selected: c4
- proof: pytest tests/test_a.py::test_retry_idempotent
- blocked items: none

## Adjudication Bottom Line

Proceed: one artifact-backed mutation, one validation-only item, one proof-only resolution, and one no-change rebuttal.
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

## Direction Context Ledger

direction_state_id:
  source: unknown
  source_ref: unknown
  source_freshness: unknown
  same_objective: unknown
  active_frontier: unknown
  locked_decisions: unknown
  non_goals: unknown
  compatibility_posture: unknown
  ownership_boundaries: unknown
  direction_confidence: unknown

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

| id/thread | reviewer | review source | location | excerpt | claim | reviewer severity claim | accepted criticality | severity acceptance status | direction fit | direction ref | approval class | mutation value | concern validity | proposed fix validity | relevance | disposition | no-change status | invariant | evidence grade | evidence ref | severity proof ref | handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1 | cas | cas-codex | src/a.py:10 | maybe unsafe | maybe unsafe | P2 | review-closure-only | accepted | unknown | unknown | C3-review-closure-only | no-change | unknown | validation-only | review-closure-only | act | unresolved | none | reviewer-only | code | review | route-to-accretive-implementer |

## Decision Tests

| id/thread | grounded | material | fresh | diagnosis | scope-fit | resolution value | no-change defeated | min evidence to change mind |
|---|---|---|---|---|---|---|---|---|
| c1 | unknown | unknown | current | unknown | unknown | review-closure | unresolved | repro |

## Direction Tests

| id/thread | direction source | source freshness | same objective | direction fit | direction ref | active frontier | non-goal conflict | direction override | min evidence to change direction |
|---|---|---|---|---|---|---|---|---|---|
| c1 | unknown | unknown | unknown | unknown | unknown | unknown | unknown | unknown | plan |

## Severity Tests

| id/thread | reviewer severity claim | accepted criticality | severity acceptance status | severity proof ref | downgrade/reject reason | p2+ accepted | min evidence to accept severity |
|---|---|---|---|---|---|---|---|
| c1 | P2 | review-closure-only | accepted | review | n/a | yes | proof |

## Mutation Approval Tests

| id/thread | concern approved | fix approved | mutation approved | approval class | why now | why not alternative | proof after fix |
|---|---|---|---|---|---|---|---|
| c1 | unknown | unknown | yes | C3-review-closure-only | reviewer asked | none | tests |

## No-Change Countercases

- c1: none.

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

all accepted.

## Direction Fit Audit

unknown.

## Source Pressure Audit

all current CAS selected.

## Selection Skew Audit

all selected.

## Adjudication Gate

| field | value | basis |
|---|---|---|
| artifact_state_coverage | pass | recorded |
| direction_context_coverage | fail | unknown |
| comment_inventory_coverage | pass | one row |
| identity_coverage | pass | c1 |
| decision_test_coverage | pass | one row |
| direction_fit_coverage | fail | unknown |
| severity_claim_coverage | pass | one row |
| mutation_approval_coverage | fail | bad mutation approval |
| p2_plus_acceptance_coverage | fail | bad severity |
| no_change_coverage | fail | unresolved |
| disposition_coverage | pass | one row |
| proposed_fix_separation | pass | split |
| evidence_ref_coverage | fail | no current evidence |
| validation_value_coverage | fail | none |
| resolve_selection_coverage | fail | invalid address |
| resolve_countercase_coverage | fail | generic |
| handoff_agenda_consistency | fail | missing |
| source_pressure_audit | fail | generic |
| selection_skew_audit | fail | generic |
| p2_plus_severity_audit | fail | generic |
| direction_fit_audit | fail | generic |
| invariant_pass | fail | none |
| authority_fanout_required | fail | missing authority fanout |
| authority_packet_coverage | fail | missing packets |
| authority_clearance_coverage | fail | missing clearance matrix |
| authority_veto_coverage | fail | missing veto ledger |
| permissive_override_absent | fail | attempted address without authority clearance |
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
    good = validate_adjudication(valid_fixture())
    bad = validate_adjudication(invalid_fixture())
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
    result = validate_adjudication(text)
    if args.json:
        print(result.to_json())
    else:
        print_human(result)
    return 0 if result.passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
