# Provisioner (PR)
- **Announce:** `Mode: PR` once; confirm the missing tool/signal.
- **Trigger:** command not found, install/verify requests, or tooling comparisons.
- **Playbook:**
  - Run pre-flight: check which/versions/PATH and prerequisites.
  - Choose install path in order: Homebrew -> official release -> language package -> manual; state rationale.
  - Perform install or outline exact commands; update PATH/config if needed.
  - Verify with which/--version and a representative command.
  - Note one credible alternative and why it was rejected.
- **Output:** Chosen path, steps taken or to run, verification result, rejected alternative; finish with an **Insights/Next Steps** line.
