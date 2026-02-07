#!/usr/bin/env node

import puppeteer from "puppeteer-core";

const DEFAULT_PORT = 9222;
async function getActivePage(browser) {
  const targets = browser.targets();
  for (let i = targets.length - 1; i >= 0; i--) {
    if (targets[i].type() !== "page") continue;
    const page = await targets[i].page();
    if (page) return page;
  }
  return null;
}

function tryParsePort(value) {
  const port = Number.parseInt(String(value), 10);
  if (!Number.isFinite(port) || port <= 0 || port > 65535) return null;
  return port;
}

function printHelp(exitCode = 0) {
  console.log("Usage: nav.js <url> [--new] [--port N] [--browser-url URL]");
  console.log("\nOptions:");
  console.log("  --new              Open in a new tab");
  console.log(`  --port N           CDP port (default: ${DEFAULT_PORT})`);
  console.log("  --browser-url URL  CDP URL (overrides --port)");
  console.log("  -h, --help         Show help");
  console.log("\nEnv:");
  console.log("  CODEX_BROWSER_URL          CDP URL (used when no CLI port/url)");
  console.log("  CODEX_BROWSER_PORT         CDP port (alias: CODEX_CDP_PORT)");

  process.exit(exitCode);
}

const args = process.argv.slice(2);

let url;
let newTab = false;
let port;
let browserURL;

for (let i = 0; i < args.length; i++) {
  const arg = args[i];

  if (arg === "-h" || arg === "--help") {
    printHelp(0);
  } else if (arg === "--new") {
    newTab = true;
  } else if (arg === "--port") {
    port = tryParsePort(args[++i]);
    if (!port) {
      console.error(`✗ Invalid port: ${args[i]}`);
      printHelp(1);
    }
  } else if (arg.startsWith("--port=")) {
    port = tryParsePort(arg.slice("--port=".length));
    if (!port) {
      console.error(`✗ Invalid port: ${arg.slice("--port=".length)}`);
      printHelp(1);
    }
  } else if (arg === "--browser-url") {
    browserURL = args[++i];
    if (!browserURL) {
      console.error("✗ Missing value for --browser-url");
      printHelp(1);
    }
  } else if (arg.startsWith("--browser-url=")) {
    browserURL = arg.slice("--browser-url=".length);
  } else if (arg.startsWith("--")) {
    console.error(`✗ Unknown option: ${arg}`);
    printHelp(1);
  } else if (!url) {
    url = arg;
  } else {
    console.error(`✗ Unexpected argument: ${arg}`);
    printHelp(1);
  }
}

if (!url) {
  printHelp(1);
}

const envBrowserURL = process.env["CODEX_BROWSER_URL"] ?? null;
const envPort = tryParsePort(
  process.env["CODEX_BROWSER_PORT"] ?? process.env["CODEX_CDP_PORT"] ?? "",
);

const portFromCli = port;
const resolvedPort = portFromCli ?? envPort ?? DEFAULT_PORT;
browserURL =
  browserURL ??
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

if (newTab) {
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: "domcontentloaded" });
  console.log("✓ Opened:", url);
} else {
  const page = await getActivePage(browser);
  if (!page) {
    console.error("✗ No active tab found (try --new)");
    process.exit(1);
  }

  await page.goto(url, { waitUntil: "domcontentloaded" });
  console.log("✓ Navigated to:", url);
}

await browser.disconnect();
