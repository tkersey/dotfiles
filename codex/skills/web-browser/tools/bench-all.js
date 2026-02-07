#!/usr/bin/env node

import { spawnSync } from "node:child_process";

function percentile(sorted, p) {
  if (sorted.length === 0) return NaN;
  if (sorted.length === 1) return sorted[0];
  const k = (sorted.length - 1) * (p / 100);
  const f = Math.floor(k);
  const c = Math.ceil(k);
  if (f === c) return sorted[f];
  return sorted[f] + (sorted[c] - sorted[f]) * (k - f);
}

function parseIntArg(value, name, fallback) {
  if (value == null) return fallback;
  const n = Number.parseInt(value, 10);
  if (!Number.isFinite(n) || n <= 0) {
    console.error(`✗ Invalid value for ${name}: ${value}`);
    process.exit(1);
  }
  return n;
}

function parseFloatArg(value, name, fallback) {
  if (value == null) return fallback;
  const n = Number.parseFloat(value);
  if (!Number.isFinite(n) || n <= 0) {
    console.error(`✗ Invalid value for ${name}: ${value}`);
    process.exit(1);
  }
  return n;
}

function runCommand(cmd, args) {
  const result = spawnSync(cmd, args, { encoding: "utf8" });
  if (result.status !== 0) {
    process.stderr.write(result.stderr ?? "");
    process.stdout.write(result.stdout ?? "");
    process.exit(result.status ?? 1);
  }
}

function benchmarkOne({ label, cmd, args, warmup, samples, budgetP95Ms }) {
  const durationsMs = [];
  for (let i = 0; i < warmup + samples; i++) {
    const t0 = process.hrtime.bigint();
    runCommand(cmd, args);
    const ms = Number(process.hrtime.bigint() - t0) / 1e6;
    if (i >= warmup) durationsMs.push(ms);
  }

  durationsMs.sort((a, b) => a - b);
  const stats = {
    min: durationsMs[0],
    p50: percentile(durationsMs, 50),
    p95: percentile(durationsMs, 95),
    p99: percentile(durationsMs, 99),
    max: durationsMs[durationsMs.length - 1],
  };

  console.log(`${label}: ${stats.min.toFixed(3)} / ${stats.p50.toFixed(3)} / ${stats.p95.toFixed(3)} / ${stats.p99.toFixed(3)} / ${stats.max.toFixed(3)} ms`);

  if (budgetP95Ms != null) {
    if (stats.p95 > budgetP95Ms) {
      console.error(
        `✗ ${label} p95 ${stats.p95.toFixed(3)} ms exceeds budget ${budgetP95Ms.toFixed(3)} ms`,
      );
      process.exit(1);
    }
    console.log(
      `✓ ${label} p95 budget met: ${stats.p95.toFixed(3)} <= ${budgetP95Ms.toFixed(3)} ms`,
    );
  }
}

const args = process.argv.slice(2);

let warmup = 5;
let samples = 30;
let screenshotSamples = 20;
let budgetNavP95Ms = null;
let budgetEvalP95Ms = null;
let budgetScreenshotP95Ms = null;
let budgetStartP95Ms = null;

for (let i = 0; i < args.length; i++) {
  const arg = args[i];

  if (arg === "--warmup") {
    warmup = parseIntArg(args[++i], "--warmup", warmup);
  } else if (arg.startsWith("--warmup=")) {
    warmup = parseIntArg(arg.slice("--warmup=".length), "--warmup", warmup);
  } else if (arg === "--samples") {
    samples = parseIntArg(args[++i], "--samples", samples);
  } else if (arg.startsWith("--samples=")) {
    samples = parseIntArg(arg.slice("--samples=".length), "--samples", samples);
  } else if (arg === "--screenshot-samples") {
    screenshotSamples = parseIntArg(
      args[++i],
      "--screenshot-samples",
      screenshotSamples,
    );
  } else if (arg.startsWith("--screenshot-samples=")) {
    screenshotSamples = parseIntArg(
      arg.slice("--screenshot-samples=".length),
      "--screenshot-samples",
      screenshotSamples,
    );
  } else if (arg === "--budget-nav-p95-ms") {
    budgetNavP95Ms = parseFloatArg(args[++i], "--budget-nav-p95-ms", budgetNavP95Ms);
  } else if (arg.startsWith("--budget-nav-p95-ms=")) {
    budgetNavP95Ms = parseFloatArg(
      arg.slice("--budget-nav-p95-ms=".length),
      "--budget-nav-p95-ms",
      budgetNavP95Ms,
    );
  } else if (arg === "--budget-eval-p95-ms") {
    budgetEvalP95Ms = parseFloatArg(
      args[++i],
      "--budget-eval-p95-ms",
      budgetEvalP95Ms,
    );
  } else if (arg.startsWith("--budget-eval-p95-ms=")) {
    budgetEvalP95Ms = parseFloatArg(
      arg.slice("--budget-eval-p95-ms=".length),
      "--budget-eval-p95-ms",
      budgetEvalP95Ms,
    );
  } else if (arg === "--budget-screenshot-p95-ms") {
    budgetScreenshotP95Ms = parseFloatArg(
      args[++i],
      "--budget-screenshot-p95-ms",
      budgetScreenshotP95Ms,
    );
  } else if (arg.startsWith("--budget-screenshot-p95-ms=")) {
    budgetScreenshotP95Ms = parseFloatArg(
      arg.slice("--budget-screenshot-p95-ms=".length),
      "--budget-screenshot-p95-ms",
      budgetScreenshotP95Ms,
    );
  } else if (arg === "--budget-start-p95-ms") {
    budgetStartP95Ms = parseFloatArg(
      args[++i],
      "--budget-start-p95-ms",
      budgetStartP95Ms,
    );
  } else if (arg.startsWith("--budget-start-p95-ms=")) {
    budgetStartP95Ms = parseFloatArg(
      arg.slice("--budget-start-p95-ms=".length),
      "--budget-start-p95-ms",
      budgetStartP95Ms,
    );
  } else if (arg === "-h" || arg === "--help") {
    console.log(
      "Usage: bench-all.js [--warmup N] [--samples N] [--screenshot-samples N] [--budget-*-p95-ms N]",
    );
    process.exit(0);
  } else {
    console.error(`✗ Unknown option: ${arg}`);
    process.exit(1);
  }
}

// Ensure deterministic active-tab behavior for nav/eval/screenshot loops.
runCommand("./nav.js", ["about:blank", "--new"]);

console.log(
  `samples: nav/eval/start=${samples}, screenshot=${screenshotSamples} (warmup ${warmup})`,
);
console.log("min/p50/p95/p99/max ms per command:");

benchmarkOne({
  label: "nav",
  cmd: "./nav.js",
  args: ["about:blank"],
  warmup,
  samples,
  budgetP95Ms: budgetNavP95Ms,
});
benchmarkOne({
  label: "eval",
  cmd: "./eval.js",
  args: ["1+1"],
  warmup,
  samples,
  budgetP95Ms: budgetEvalP95Ms,
});
benchmarkOne({
  label: "screenshot",
  cmd: "./screenshot.js",
  args: [],
  warmup,
  samples: screenshotSamples,
  budgetP95Ms: budgetScreenshotP95Ms,
});
benchmarkOne({
  label: "start-no-kill",
  cmd: "./start.js",
  args: ["--no-kill"],
  warmup,
  samples,
  budgetP95Ms: budgetStartP95Ms,
});
