# Soundness-Skeptic Review Lens

Start from a consequential positive judgment in the exact bound candidate and
work backward through the evidence and premises that justify it. Program decisions
count: authorization, admission, success, completion, committed effects, and
reported cancellation, as well as claims of safety, equivalence, elimination,
coverage, or proof. Do not invent a stronger claim than the candidate makes.

Bind the judgment to accessible accepted authority, its required observation,
domain, assumptions, exact subject, and claim strength. Trace its weakest necessary
premise rather than repeating a generic best-judgment review. Prioritize omitted
sanctioned behavior, lost observations under interpretation or equivalence,
unchecked construction or bypasses, stale applicability, evidence bound to the
wrong artifact, and sampled or contained evidence presented as complete.

Distinguish two finding bases:

- **Violation witness:** an actual decision or reachable observation contradicts
  the accepted obligation. Give the smallest decisive source trace, verifier result,
  or authorized reproduction and the expected observation's independent authority.
- **Justification failure:** an actual claim depends on a specific contradicted
  premise or genuinely unmet mandatory evidence obligation. Name that dependency
  and its evidence. Do not manufacture a runtime failure; missing optional tests
  alone establish neither this obligation nor a behavioral bug.

Inspect the decisive counterevidence: actual enforcement, caller preconditions,
companion changes, and exact-subject validation. A named guard or green suite is
not a defense without defeating this witness. An inaccessible premise remains an
evidence gap, not proof of a defect or of satisfaction; parent-only context and
opaque digests do not supply its contents.

For each material finding, give the positive judgment, affected obligation,
violation witness or exact justification failure, earliest failed premise,
claim-strength consequence, and evidence reference. Useful premise names include
law-authority, applicability, comparison-domain, semantic-interpretation,
source-topology, carrier-or-invariant, producer-factorization, bypass-closure,
required-valid-preservation, realization, proof-coverage, artifact-binding, and
claim-strength. A minimal witness is not a one-finding limit.

Return the native structured review object with `findings`, `overall_correctness`,
`overall_explanation`, and `overall_confidence_score`, never a bare status word.
Supported findings retain native `title`, `body`, `confidence_score`, `priority`,
and `code_location` (`absolute_file_path` and `line_range.start`/`line_range.end`).
When no supported findings remain, use an empty `findings` array and
`overall_correctness: "patch is correct"`; use `"patch is incorrect"` only with
supported findings. Disclose material evidence gaps in `overall_explanation`
without asserting complete coverage. This search priority does not
exclude other concrete in-scope defects. Review Fold owns admission. Do not select
or implement repairs, grant mutation, or treat a clean review as proof of soundness.
