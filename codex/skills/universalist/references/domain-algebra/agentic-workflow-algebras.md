# Agentic workflow algebras

Agentic systems are not the center of Universalist, but they are a strong stress test for Track A0.

## Common carriers

```text
Task
Context
Plan
Step
ToolOperation
ToolResult
Observation
EvidenceSet
Claim
Citation
Draft
ValidationResult
Approval
Trace
MemoryUpdate
Artifact
```

## Common operations

```text
plan             : Task × Context -> Plan
sequence         : Plan × Plan -> Plan
selectTool       : Step × Context -> ToolOperation
executeTool      : ToolOperation × Environment -> ToolResult
observe          : ToolResult -> Observation
mergeEvidence    : EvidenceSet × EvidenceSet -> EvidenceSet
extractClaims    : EvidenceSet -> ClaimGraph
validate         : Draft × Criteria -> ValidationResult
repair           : Draft × ValidationResult -> Draft
finalize         : Draft × ValidationResult -> FinalAnswer
```

## Pure/effectful split

```text
Pure:      plan, normalize, rank, validateText, mergeEvidence under fixed observations
Effectful: webSearch, readFile, callAPI, writeFile, sendEmail, deployCode
```

Effectful operations may require Freyd-category, algebraic-effect, handler, trace, approval, or resource mechanics.

## Example laws

```text
emptyPlan then p = p
(p then q) then r = p then (q then r)
mergeEvidence is idempotent/commutative only under source-identity observation
missingApproval ⋅ destructiveAction = blocked
unsupportedClaim blocks finalization
blocked actions have no external effect trace
```
