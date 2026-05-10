# Case studies

## Boolean matrix to coproduct

Signal: `isDraft`, `isPublished`, `deletedAt` combinations create impossible states.
Construction: coproduct lifecycle type.
Proof: invalid fixture rejection and exhaustive handling.

## Repeated validation to refined type

Signal: email validation repeated in API, service, and serializer.
Construction: `EmailAddress` refined type with trusted constructor.
Proof: valid/invalid table tests.

## Shared id agreement to pullback

Signal: repeated `customerId` equality checks.
Construction: checked aggregate with agreement witness.
Proof: mismatch rejected; projections preserve ids.

## Callback plugin registry to explicit IR

Signal: plugin callbacks duplicate core semantics.
Construction: free syntax / explicit plugin operation IR.
Proof: `interpret(embed(coreNode)) == coreInterpreter(coreNode)`.
