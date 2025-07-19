# Save your latest learnings

# INSTRUCTIONS

- Look at the files in ~/.learnings/learnings/
- Find the highest numbered file (e.g., 0119.md)
- Increment the number by 1 and zero-pad to 4 digits (e.g., 0120.md)
- Think hard and save your learnings to that new file in ~/.learnings/learnings/
- Extract the title from the learning (first heading after "# " in the new file)
- Extract relevant tags from the learning content by analyzing:
  - Technology/framework names (e.g., typescript, python, react, mcp, hopper-framework)
  - Key concepts (e.g., refactoring, testing, architecture, debugging)
  - Patterns and methodologies (e.g., monoids, agent-architecture, type-safety, functional-programming)
  - Tools and libraries mentioned (e.g., bun, effection, deepeval, playwright)
  - Convert all tags to lowercase and replace spaces with hyphens
  - Include 3-7 most relevant tags
- Update ~/.learnings/README.md by:
  - Adding a new entry AFTER the "## Key Topics" section with the format: `## {number}. [{title}](learnings/{filename}) {tags}`
  - The number should be the next sequential number (previous highest + 1)
  - Entries are in reverse chronological order (newest first)
  - If no specific title is found, use "Learnings" as the title
  - Tags should be formatted as backtick-wrapped hashtags (e.g., `#typescript` `#refactoring`)
  - Analyzing the Key Topics section and updating it if the new learning introduces:
    - A new major theme not yet represented
    - Significant additions to an existing topic (update the session count if applicable)
    - New frameworks, tools, or patterns that warrant inclusion
  - Keep the Key Topics section concise but comprehensive
- If ~/.learnings is a git repo
  - commit the latest learnings
  - push
