#!/usr/bin/env node

import puppeteer from "puppeteer-core";

const DEFAULT_PORT = 9222;

function tryParsePort(value) {
  const port = Number.parseInt(String(value), 10);
  if (!Number.isFinite(port) || port <= 0 || port > 65535) return null;
  return port;
}

function printHelp(exitCode = 0) {
  console.log("Usage: eval.js [--port N] [--browser-url URL] [--] 'code'");
  console.log("\nOptions:");
  console.log(`  --port N           CDP port (default: ${DEFAULT_PORT})`);
  console.log("  --browser-url URL  CDP URL (overrides --port)");
  console.log("  -h, --help         Show help");
  console.log("\nEnv:");
  console.log("  CODEX_BROWSER_URL          CDP URL (used when no CLI port/url)");
  console.log("  CODEX_BROWSER_PORT         CDP port (alias: CODEX_CDP_PORT)");
  console.log("\nExamples:");
  console.log("  eval.js 'document.title'");
  console.log("  eval.js --port 9223 'document.title'");
  console.log("  eval.js --browser-url http://localhost:9222 'document.title'");
  console.log("  eval.js -- 'document.querySelectorAll(\"a\").length'");

  process.exit(exitCode);
}

const args = process.argv.slice(2);

let portFromCli;
let browserUrlFromCli;
let codeParts = [];

let parsingOptions = true;
for (let i = 0; i < args.length; i++) {
  const arg = args[i];

  if (parsingOptions && (arg === "-h" || arg === "--help")) {
    printHelp(0);
  } else if (parsingOptions && arg === "--") {
    parsingOptions = false;
  } else if (parsingOptions && arg === "--port") {
    portFromCli = tryParsePort(args[++i]);
    if (!portFromCli) {
      console.error(`✗ Invalid port: ${args[i]}`);
      printHelp(1);
    }
  } else if (parsingOptions && arg.startsWith("--port=")) {
    portFromCli = tryParsePort(arg.slice("--port=".length));
    if (!portFromCli) {
      console.error(`✗ Invalid port: ${arg.slice("--port=".length)}`);
      printHelp(1);
    }
  } else if (parsingOptions && arg === "--browser-url") {
    browserUrlFromCli = args[++i];
    if (!browserUrlFromCli) {
      console.error("✗ Missing value for --browser-url");
      printHelp(1);
    }
  } else if (parsingOptions && arg.startsWith("--browser-url=")) {
    browserUrlFromCli = arg.slice("--browser-url=".length);
  } else if (parsingOptions && arg.startsWith("--")) {
    console.error(`✗ Unknown option: ${arg}`);
    printHelp(1);
  } else {
    codeParts = args.slice(i);
    break;
  }
}

const code = codeParts.join(" ");
if (!code) {
  printHelp(1);
}

const envBrowserURL = process.env["CODEX_BROWSER_URL"] ?? null;
const envPort = tryParsePort(
  process.env["CODEX_BROWSER_PORT"] ?? process.env["CODEX_CDP_PORT"] ?? "",
);

const resolvedPort = portFromCli ?? envPort ?? DEFAULT_PORT;
const browserURL =
  browserUrlFromCli ??
  (portFromCli
    ? `http://localhost:${resolvedPort}`
    : envBrowserURL ?? `http://localhost:${resolvedPort}`);

let browser;
try {
  browser = await puppeteer.connect({
    browserURL,
    defaultViewport: null,
  });
} catch (e) {
  console.error("✗ Failed to connect to Chrome via CDP");
  console.error(`  URL: ${browserURL}`);
  console.error("  Start Chrome via: ./tools/start.js");
  console.error(e);
  process.exit(1);
}

const page = (await browser.pages()).at(-1);

if (!page) {
  console.error("✗ No active tab found");
  console.error("  Open one via: ./tools/nav.js https://example.com --new");
  process.exit(1);
}

let result;

try {
  result = await page.evaluate((c) => {
    const AsyncFunction = (async () => {}).constructor;
    return new AsyncFunction(`return (${c})`)();
  }, code);
} catch (e) {
  console.log("Failed to evaluate expression");
  console.log(`  Expression: ${code}`);
  console.log(e);
  process.exit(1);
}

if (Array.isArray(result)) {
  for (let i = 0; i < result.length; i++) {
    if (i > 0) console.log("");
    for (const [key, value] of Object.entries(result[i])) {
      console.log(`${key}: ${value}`);
    }
  }
} else if (typeof result === "object" && result !== null) {
  for (const [key, value] of Object.entries(result)) {
    console.log(`${key}: ${value}`);
  }
} else {
  console.log(result);
}

await browser.disconnect();
