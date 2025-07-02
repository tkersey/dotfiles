# Generate llms.txt for current repository

# Role

You are an expert at analyzing repositories and creating concise, informative llms.txt files that help LLMs quickly understand project context.

# Goal

Generate an appropriate llms.txt file for the current repository and add it to the current context.

# Instructions

- Analyze the current repository structure and files to understand:
  - Project name (from package.json, Cargo.toml, pyproject.toml, go.mod, or infer from directory name)
  - Project description and purpose
  - Key documentation files (README, docs/, CONTRIBUTING, etc.)
  - Main programming language(s) and frameworks
  - Important configuration files
  - Project structure and organization

- Generate an llms.txt file following the format from llmstxt.org:
  - Start with an H1 containing the project name
  - Include a blockquote with a concise project summary
  - Add relevant context about the project's purpose and architecture
  - Include sections for key resources:
    - ## Docs - Link to main documentation
    - ## Code - Key source directories and their purposes
    - ## Config - Important configuration files
    - ## Getting Started - Quick setup instructions if available

- Format guidelines:
  - Use clear, concise markdown
  - Each linked resource should have a brief description
  - Avoid jargon without explanation
  - Focus on what would help an LLM understand the codebase quickly
  - Keep total length reasonable (aim for under 500 lines)

- After generating the llms.txt content:
  - Display it to the user for review
  - Ask if they want to save it to the repository root
  - If saved, add the file path to .gitignore if appropriate
  - Add the generated content to the current Claude context

- Special considerations:
  - For monorepos, focus on the current working directory
  - Include technology stack and key dependencies
  - Mention testing approach if evident
  - Note any unusual project structures or conventions
  - Include links to external documentation if found