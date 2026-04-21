# Chronicle Memory Instructions

Chronicle is a memory extension that provides chronological 10minute summaries of the user's recent work context, informed by a passive screen recording process that runs in the background as well as other Codex plugins (e.g., connectors and apps).

When generating phase2 memories, you MUST include memories derived from the resources folder next to this instructions file. The resources folder contains Markdown summaries of what the user was most recently doing on their computer, along with all connectors they have enabled, which is useful for context. Grep over the folder to find useful context to include in your summary.

Key things to include from Chronicle:

- **Chronicle memories' "non-obvious context" sections should go into the "User Profile" section of the memory summary**, because they often include non-obvious backstory or context that is useful for understanding the user (rather than just their current todos, as exposed by memories from codex rollouts alone).
- **All chronological details from Chronicle memories must be included in MEMORY.md** - as new tasks if they aren't already present, or as additional context for existing tasks derived from rollouts. In your answer, list the chronological details you added to MEMORY.md. You should force the creation of synthetic MEMORY.md entries if they don't exist - with thread id None, rollout_path set to the path of the Chronicle memory, and updated_at set to the timestamp of the Chronicle memory.
- **What's in Memory should include details from every relevant task explained in the Chronicle memories** as they are a superset of the rollout memories with more information.

Include the tag "[chronicle memory]" after any information derived from this in your summary.

## Folder structure

- resources/*.md
  - Chronicle memories: markdown summaries of screen recordings, broken up into 10 minute/6h chunks. File format: `YYYY-MM-DDTHH-MM-SS-{4_alpha_chars}-10min-{slug_description}.md` or `YYYY-MM-DDTHH-MM-SS-{4_alpha_chars}-6h-{slug_description}.md`.
