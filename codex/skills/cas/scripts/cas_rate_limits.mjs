#!/usr/bin/env node
// Read account rate limits via cas (codex app-server) and print a normalized snapshot.

import { createHash } from "node:crypto";
import { homedir } from "node:os";
import { resolve } from "node:path";

import { CasClient } from "./cas_client.mjs";
import { computeBudgetGovernor } from "./budget_governor.mjs";

function usage() {
  return [
    "cas_rate_limits.mjs",
    "",
    "Reads account rate limits via cas (codex app-server) and prints a normalized snapshot.",
    "",
    "Usage:",
    "  node codex/skills/cas/scripts/cas_rate_limits.mjs [options]",
    "",
    "Options:",
    "  --cwd DIR            Workspace to run in (default: current directory)",
    "  --state-file PATH    cas state file path (default: ~/.codex/cas/state/<cwd-hash>.json)",
    "  --json               Emit JSON to stdout",
    "  --help               Show help",
    "",
    "Notes:",
    "  - Requires `codex` on PATH (cas spawns `codex app-server`).",
  ].join("\n");
}

function parseArgs(argv) {
  const opts = {
    cwd: process.cwd(),
    stateFile: null,
    json: false,
  };

  const args = [...argv];
  while (args.length) {
    const a = args.shift();
    if (!a) break;
    if (a === "--help" || a === "-h") return { ok: false, help: true, error: null, opts: null };

    const take = () => {
      const v = args.shift();
      if (!v) throw new Error(`Missing value for ${a}`);
      return v;
    };

    if (a === "--cwd") {
      opts.cwd = take();
      continue;
    }
    if (a === "--state-file") {
      opts.stateFile = take();
      continue;
    }
    if (a === "--json") {
      opts.json = true;
      continue;
    }

    throw new Error(`Unknown arg: ${a}`);
  }

  if (typeof opts.cwd !== "string" || !opts.cwd.trim()) throw new Error("--cwd must be a non-empty string");
  if (opts.stateFile !== null && (typeof opts.stateFile !== "string" || !opts.stateFile.trim())) {
    throw new Error("--state-file must be a non-empty string");
  }

  return { ok: true, help: false, error: null, opts };
}

function defaultStateFileForCwd(cwd) {
  const normalized = resolve(cwd);
  const digest = createHash("sha256").update(normalized).digest("hex").slice(0, 16);
  return resolve(homedir(), ".codex", "cas", "state", `${digest}.json`);
}

function fmtPct(v) {
  if (!Number.isFinite(v)) return "null";
  return `${v.toFixed(1)}%`;
}

function fmtTime(sec) {
  if (!Number.isInteger(sec)) return "null";
  return new Date(sec * 1000).toISOString();
}

async function main() {
  let parsed;
  try {
    parsed = parseArgs(process.argv.slice(2));
  } catch (err) {
    process.stderr.write(`${err instanceof Error ? err.message : String(err)}\n${usage()}\n`);
    return 2;
  }

  if (!parsed.ok) {
    if (parsed.help) {
      process.stderr.write(`${usage()}\n`);
      return 0;
    }
    process.stderr.write(`${parsed.error ?? "invalid args"}\n`);
    return 2;
  }

  const opts = parsed.opts;
  const stateFile = opts.stateFile ?? defaultStateFileForCwd(opts.cwd);
  const client = new CasClient({
    cwd: opts.cwd,
    stateFile,
    clientName: "cas-rate-limits",
    clientTitle: "cas rate limits",
    clientVersion: "0.1.0",
  });

  client.on("cas/error", (ev) => {
    const detail = ev?.error ? ` detail=${JSON.stringify(ev.error)}` : "";
    process.stderr.write(`[cas] error: ${ev?.message ?? "unknown"}${detail}\n`);
  });

  try {
    await client.start();
    const resp = await client.request("account/rateLimits/read", {}, { timeoutMs: 20_000 });
    const gov = computeBudgetGovernor(resp);

    if (opts.json) {
      process.stdout.write(`${JSON.stringify(gov, null, 2)}\n`);
    } else {
      process.stdout.write(
        [
          `tier=${gov.tier} tier_reason=${gov.tierReason}`,
          `used_percent=${gov.usedPercent ?? "null"}`,
          `elapsed_percent=${fmtPct(gov.elapsedPercent)}`,
          `delta_percent=${gov.deltaPercent === null || gov.deltaPercent === undefined ? "null" : gov.deltaPercent.toFixed(1)}`,
          `resets_at=${fmtTime(gov.resetsAt)}`,
          `window_mins=${gov.windowDurationMins ?? "null"}`,
          `bucket_key=${gov.bucketKey ?? "null"}`,
          `limit_id=${gov.limitId ?? "null"}`,
          `limit_name=${gov.limitName ?? "null"}`,
          `plan_type=${gov.planType ?? "null"}`,
        ].join("\n") + "\n",
      );
    }
  } finally {
    try {
      await client.close();
    } catch {
      // ignore
    }
  }

  return 0;
}

main()
  .then((code) => {
    process.exitCode = code;
  })
  .catch((err) => {
    process.stderr.write(`Fatal: ${err instanceof Error ? err.stack ?? err.message : String(err)}\n`);
    process.exitCode = 1;
  });
