#!/usr/bin/env node
// Example orchestration client using CaspClient.
//
// This script is agent-friendly: it prints JSON to stdout and diagnostics to stderr.

import { CaspClient } from "./casp_client.mjs";

function usage() {
  return [
    "casp_example_orchestrator.mjs",
    "",
    "Usage:",
    "  node scripts/casp_example_orchestrator.mjs --cwd DIR --list-threads [N]",
    "  node scripts/casp_example_orchestrator.mjs --cwd DIR --read-thread THREAD_ID [--include-turns]",
    "  node scripts/casp_example_orchestrator.mjs --cwd DIR --compact-thread THREAD_ID",
    "  node scripts/casp_example_orchestrator.mjs --cwd DIR --prompt TEXT [--thread-id THREAD_ID]",
    "",
    "Notes:",
    "  - --cwd controls where codex runs and where .casp/state.json lives.",
    "  - --prompt requires a working Codex login and (usually) network access.",
  ].join("\n");
}

function parseArgs(argv) {
  /** @type {{ cwd: string|null, listThreads: number|null, readThread: string|null, compactThread: string|null, includeTurns: boolean, prompt: string|null, threadId: string|null }} */
  const out = {
    cwd: null,
    listThreads: null,
    readThread: null,
    compactThread: null,
    includeTurns: false,
    prompt: null,
    threadId: null,
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
      out.cwd = take();
      continue;
    }
    if (a === "--list-threads") {
      const maybe = args[0];
      if (maybe && !maybe.startsWith("--")) {
        out.listThreads = Number(take());
      } else {
        out.listThreads = 10;
      }
      continue;
    }
    if (a === "--read-thread") {
      out.readThread = take();
      continue;
    }
    if (a === "--compact-thread") {
      out.compactThread = take();
      continue;
    }
    if (a === "--include-turns") {
      out.includeTurns = true;
      continue;
    }
    if (a === "--prompt") {
      out.prompt = take();
      continue;
    }
    if (a === "--thread-id") {
      out.threadId = take();
      continue;
    }

    throw new Error(`Unknown arg: ${a}`);
  }

  return { ok: true, help: false, error: null, opts: out };
}

function writeJson(obj) {
  process.stdout.write(`${JSON.stringify(obj)}\n`);
}

function logErr(line) {
  process.stderr.write(`${line}\n`);
}

async function main() {
  const parsed = parseArgs(process.argv.slice(2));
  if (!parsed.ok) {
    if (parsed.help) {
      logErr(usage());
      return 0;
    }
    logErr(parsed.error ?? "invalid args");
    return 2;
  }

  const opts = parsed.opts;
  if (!opts.cwd) {
    logErr("Missing --cwd");
    logErr(usage());
    return 2;
  }

  const client = new CaspClient({ cwd: opts.cwd });

  // Print all proxy events to stderr for debugging.
  client.on("casp/error", (ev) => logErr(`casp/error: ${ev.message}`));
  client.on("proxyStderr", (line) => logErr(`proxy stderr: ${line}`));

  // Do not let server-initiated requests stall: respond with an explicit error by default.
  client.on("casp/serverRequest", (ev) => {
    const method = ev.method;
    if (method === "item/tool/call") {
      // Example policy: do not implement tools here; just return a clear error.
      client.respond(ev.id, {
        result: {
          contentItems: [
            { type: "inputText", text: "Tool call not implemented by this example" },
          ],
          success: false,
        },
      });
      return;
    }

    client.respond(ev.id, {
      error: {
        message: `Unhandled server request: ${method}`,
      },
    });
  });

  await client.start();

  if (opts.listThreads !== null) {
    const result = await client.request("thread/list", {
      cursor: null,
      limit: opts.listThreads,
    });
    writeJson({ method: "thread/list", result });
    await client.close();
    return 0;
  }

  if (opts.readThread) {
    const result = await client.request("thread/read", {
      threadId: opts.readThread,
      includeTurns: Boolean(opts.includeTurns),
    });
    writeJson({ method: "thread/read", result });
    await client.close();
    return 0;
  }

  if (opts.compactThread) {
    const result = await client.request("thread/compact/start", {
      threadId: opts.compactThread,
    });
    writeJson({ method: "thread/compact/start", threadId: opts.compactThread, result });
    // Compaction progress streams as standard turn/item notifications.
    await client.close();
    return 0;
  }

  if (opts.prompt) {
    const threadId =
      opts.threadId ??
      (
        /** @type {any} */
        (await client.startThread({ cwd: opts.cwd }))
      )?.thread?.id;

    if (!threadId) {
      throw new Error("Failed to obtain threadId");
    }

    const collected = await client.startTurnAndCollect({
      threadId,
      input: [
        {
          type: "text",
          text: opts.prompt,
          text_elements: [],
        },
      ],
    });

    writeJson({
      method: "turn/start",
      threadId,
      turnId: collected.turnId,
      status: collected.turn?.status ?? null,
      agentMessageText: collected.agentMessageText,
      items: collected.items,
    });
    await client.close();
    return 0;
  }

  logErr("Nothing to do (specify --list-threads, --read-thread, or --prompt)");
  logErr(usage());
  await client.close();
  return 2;
}

main()
  .then((code) => {
    process.exitCode = code;
  })
  .catch((err) => {
    logErr(`Fatal: ${err instanceof Error ? err.stack ?? err.message : String(err)}`);
    process.exitCode = 1;
  });
