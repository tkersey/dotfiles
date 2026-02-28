# cron runtime migration

Runtime logic for the `cron` skill was migrated to the native Zig `cron` binary.

Use:
- `cron <automation command>`
- `cron run-due`
- `cron scheduler install|uninstall|status`

No Python or shell runtime wrappers remain in this skill directory.
