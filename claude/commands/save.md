# Save your latest learnings

# INSTRUCTIONS

- Look at the files in ~/.learnings
- If there is a file named learnings.md
  - Then looking for a file that starts with learnings then a numeral
  - Increment the numeral by 1, ultrathink and save your learnings to that file
- Else ultrathink and save your learnings to learnings.md
- Extract the title from the learning (first heading after "# " in the new file)
- Update ~/.learnings/index.md by:
  - Adding a new numbered entry with the format: `{number}. [{title}]({filename})`
  - The number should be the next sequential number in the index
  - If no specific title is found, use "Learnings" as the title
- If ~/.learnings is a git repo
  - commit the latest learnings
  - push
