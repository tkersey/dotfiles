# Save the current session transcription

# Role

You are an expert at formatting and saving conversation transcripts in a clear, readable markdown format.

# Goal

Save the current Claude session's transcription to a markdown file at the path specified in $ARGUMENTS.

# Instructions

- Review the entire conversation history from the beginning
- Format the transcription in markdown with clear participant markers:
  - Use `## Human` for user messages
  - Use `## Assistant` for Claude's responses
- Include timestamps if available
- Preserve code blocks with proper markdown syntax highlighting
- Preserve any images or file references mentioned
- Save the formatted transcription to the file path provided in $ARGUMENTS
- If no path is provided, save to `~/transcription-{timestamp}.md`
- Ensure the file uses proper markdown formatting throughout
- Include a header with session metadata (date, duration if available)
- After saving, confirm the file location and provide a brief summary of the transcription (word count, number of exchanges)