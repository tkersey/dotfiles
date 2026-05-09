# Repo audit checklist

1. List architecture worlds: core, API, DB, events, tests, runtime, clients.
2. List boundaries: embeddings `K`, projections `P`, interpreters, serializers, handlers.
3. Classify each pressure: extension, lift, restriction/checking, ordinary adapter.
4. Pick one witness slice.
5. Identify law tests before code movement.
6. Run Yoneda/Coyoneda pass if observations or generated payloads dominate.
7. Run defunctionalization pass if functions cross boundaries.
8. For lifts, run Freyd/AFT diagnostic on `P`.
9. Record no-exact-lift obstructions.
