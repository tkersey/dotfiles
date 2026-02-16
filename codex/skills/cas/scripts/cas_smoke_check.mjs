#!/usr/bin/env node
// Smoke-check cas support for key app-server APIs.
//
// Validates:
// - experimentalFeature/list
// - thread/resume
// - turn/steer method availability (accepts precondition failures)

import { randomUUID } from "node:crypto";
import { CasClient } from "./cas_client.mjs";

function usage() {
  return [
    "cas_smoke_check.mjs",
    "",
    "Usage:",
    "  node scripts/cas_smoke_check.mjs --cwd DIR [options]",
    "",
    "Required:",
    "  --cwd DIR                        Workspace for cas/app-server.",
    "",
    "Options:",
    "  --thread-id THREAD_ID            Existing thread id to reuse (optional).",
    "  --request-timeout-ms N           Timeout per request (default: 15000).",
    "  --opt-out-notification-method M  Suppress notification method (repeatable).",
    "  --json                           Emit machine-readable JSON report.",
    "  --help                           Show this help.",
  ].join("\n");
}

function parseArgs(argv) {
  const opts = {
    cwd: null,
    threadId: null,
    requestTimeoutMs: 15_000,
    optOutNotificationMethods: [],
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
    if (a === "--thread-id") {
      opts.threadId = take();
      continue;
    }
    if (a === "--request-timeout-ms") {
      opts.requestTimeoutMs = Number(take());
      continue;
    }
    if (a === "--opt-out-notification-method") {
      opts.optOutNotificationMethods.push(take());
      continue;
    }
    if (a === "--json") {
      opts.json = true;
      continue;
    }

    throw new Error(`Unknown arg: ${a}`);
  }

  if (!opts.cwd) throw new Error("Missing --cwd");
  if (!Number.isInteger(opts.requestTimeoutMs) || opts.requestTimeoutMs <= 0) {
    throw new Error("--request-timeout-ms must be a positive integer");
  }

  return { ok: true, help: false, error: null, opts };
}

function parseRpcError(err) {
  if (!(err instanceof Error)) return null;
  if (!err.message) return null;
  try {
    const parsed = JSON.parse(err.message);
    if (parsed && typeof parsed === "object") return parsed;
  } catch {
    // ignore non-JSON error
  }
  return null;
}

function isMethodUnavailableError(err) {
  const parsed = parseRpcError(err);
  if (parsed && parsed.code === -32601) return true;

  const msg = err instanceof Error ? err.message : String(err);
  return /method not found|unknown method|unrecognized method/i.test(msg);
}

function errorSummary(err) {
  if (err instanceof Error) return err.message;
  return String(err);
}

function writeReport(opts, report) {
  if (opts.json) {
    process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
    return;
  }

  const lines = [];
  lines.push("cas smoke-check");
  lines.push(`cwd: ${report.cwd}`);
  lines.push(`threadId: ${report.threadId ?? "n/a"}`);
  lines.push(`overall: ${report.ok ? "pass" : "fail"}`);
  for (const check of report.checks) {
    lines.push(`- ${check.name}: ${check.ok ? "pass" : "fail"} (${check.detail})`);
  }
  process.stdout.write(`${lines.join("\n")}\n`);
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
  const checks = [];
  let threadId = opts.threadId;

  const client = new CasClient({
    cwd: opts.cwd,
    optOutNotificationMethods: opts.optOutNotificationMethods,
  });

  try {
    await client.start();

    // Check 1: experimental feature listing request succeeds.
    try {
      const res = await client.listExperimentalFeatures(
        { cursor: null, limit: 1 },
        { timeoutMs: opts.requestTimeoutMs },
      );
      const rows = Array.isArray(res?.data) ? res.data.length : null;
      checks.push({
        name: "experimentalFeature/list",
        ok: true,
        detail: `ok (rows=${rows ?? "unknown"})`,
      });
    } catch (err) {
      checks.push({
        name: "experimentalFeature/list",
        ok: false,
        detail: errorSummary(err),
      });
    }

    // Check 2: thread/resume method is wired.
    // New thread ids may not always have persisted rollouts yet, so non-method
    // server errors are treated as "method available".
    try {
      if (!threadId) {
        const startRes = await client.startThread({ cwd: opts.cwd }, { timeoutMs: opts.requestTimeoutMs });
        threadId = startRes?.thread?.id ?? null;
      }
      if (!threadId) {
        throw new Error("thread/start did not return thread.id");
      }
      const resumeRes = await client.resumeThread(
        { threadId },
        { timeoutMs: opts.requestTimeoutMs },
      );
      const resumedId = resumeRes?.thread?.id ?? null;
      if (resumedId !== threadId) {
        throw new Error(
          `thread/resume returned unexpected thread id: ${resumedId ?? "null"}`,
        );
      }
      checks.push({
        name: "thread/resume",
        ok: true,
        detail: "ok",
      });
    } catch (err) {
      if (isMethodUnavailableError(err)) {
        checks.push({
          name: "thread/resume",
          ok: false,
          detail: `method unavailable: ${errorSummary(err)}`,
        });
      } else {
        checks.push({
          name: "thread/resume",
          ok: true,
          detail: `method reached server: ${errorSummary(err)}`,
        });
      }
    }

    // Check 3: turn/steer method is wired; precondition failures are acceptable.
    try {
      if (!threadId) {
        throw new Error("no threadId available for turn/steer check");
      }
      await client.steerTurn(
        {
          threadId,
          expectedTurnId: `cas-smoke-${randomUUID()}`,
          input: [
            {
              type: "text",
              text: "cas smoke-check turn steer",
            },
          ],
        },
        { timeoutMs: opts.requestTimeoutMs },
      );
      checks.push({
        name: "turn/steer",
        ok: true,
        detail: "ok",
      });
    } catch (err) {
      if (isMethodUnavailableError(err)) {
        checks.push({
          name: "turn/steer",
          ok: false,
          detail: `method unavailable: ${errorSummary(err)}`,
        });
      } else {
        checks.push({
          name: "turn/steer",
          ok: true,
          detail: `method reached server (expected precondition rejection): ${errorSummary(err)}`,
        });
      }
    }
  } finally {
    await client.close().catch(() => {});
  }

  const ok = checks.every((c) => c.ok);
  const report = {
    check: "cas-smoke-check",
    cwd: opts.cwd,
    threadId,
    ok,
    checks,
  };
  writeReport(opts, report);
  return ok ? 0 : 1;
}

main()
  .then((code) => {
    process.exitCode = code;
  })
  .catch((err) => {
    process.stderr.write(
      `Fatal: ${err instanceof Error ? err.stack ?? err.message : String(err)}\n`,
    );
    process.exitCode = 1;
  });
