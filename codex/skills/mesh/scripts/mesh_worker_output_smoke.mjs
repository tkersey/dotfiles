#!/usr/bin/env node

import assert from "node:assert/strict";

import { classifyMeshOutput, parseStrictOutputArtifact } from "./mesh_worker_output_parser.mjs";

function wrapCollected(text) {
  return {
    agentMessageText: text,
    items: [{ type: "agentMessage", text }],
  };
}

const strictDiffText = [
  "```diff",
  "diff --git a/a.txt b/a.txt",
  "--- a/a.txt",
  "+++ b/a.txt",
  "@@ -1 +1 @@",
  "-a",
  "+b",
  "```",
].join("\n");

const strictNoDiffText = "NO_DIFF:waiting_on_deps";
const strictWrappedNoDiffText = ["summary:", "NO_DIFF:waiting_on_deps"].join("\n");
const strictPatchFenceText = ["```patch", "--- a/a.txt", "+++ b/a.txt", "@@ -1 +1 @@", "-a", "+b", "```"].join(
  "\n",
);
const relaxedGitHeaderText = ["note", "diff --git a/a.txt b/a.txt", "--- a/a.txt", "+++ b/a.txt"].join("\n");
const relaxedNoDiffText = ["note", "NO_DIFF:not_safe_to_apply"].join("\n");

const strictDiffParsed = parseStrictOutputArtifact(strictDiffText);
assert.equal(strictDiffParsed.failureCode, null);
assert.equal(strictDiffParsed.parseFormat, "diff_fence");
assert.equal(strictDiffParsed.diff?.includes("diff --git a/a.txt b/a.txt"), true);

const strictNoDiffParsed = parseStrictOutputArtifact(strictNoDiffText);
assert.equal(strictNoDiffParsed.failureCode, "no_patch_returned");
assert.equal(strictNoDiffParsed.noDiffReason, "waiting_on_deps");

const strictWrappedParsed = classifyMeshOutput(wrapCollected(strictWrappedNoDiffText), {
  strictOutput: true,
  statusHint: "completed",
});
assert.equal(strictWrappedParsed.failureCode, "no_diff_parsed");
assert.equal(strictWrappedParsed.parseFormat, "none");

const strictPatchFenceParsed = classifyMeshOutput(wrapCollected(strictPatchFenceText), {
  strictOutput: true,
  statusHint: "completed",
});
assert.equal(strictPatchFenceParsed.failureCode, "no_diff_parsed");
assert.equal(strictPatchFenceParsed.parseFormat, "none");

const strictNoResponseParsed = classifyMeshOutput(wrapCollected(""), {
  strictOutput: true,
  statusHint: "failed",
});
assert.equal(strictNoResponseParsed.failureCode, "no_response");

const strictPrefersDiffCollected = {
  agentMessageText: "NO_DIFF:temp",
  items: [{ type: "toolResult", output: strictDiffText }],
};
const strictPrefersDiffParsed = classifyMeshOutput(strictPrefersDiffCollected, {
  strictOutput: true,
  statusHint: "completed",
});
assert.equal(strictPrefersDiffParsed.failureCode, null);
assert.equal(strictPrefersDiffParsed.parseFormat, "diff_fence");
assert.equal(strictPrefersDiffParsed.diff?.includes("diff --git a/a.txt b/a.txt"), true);

const relaxedDiffParsed = classifyMeshOutput(wrapCollected(relaxedGitHeaderText), {
  strictOutput: false,
  statusHint: "completed",
});
assert.equal(relaxedDiffParsed.failureCode, null);
assert.equal(relaxedDiffParsed.parseFormat, "git_header");
assert.equal(relaxedDiffParsed.diff?.startsWith("diff --git "), true);

const relaxedNoDiffParsed = classifyMeshOutput(wrapCollected(relaxedNoDiffText), {
  strictOutput: false,
  statusHint: "completed",
});
assert.equal(relaxedNoDiffParsed.failureCode, "no_patch_returned");
assert.equal(relaxedNoDiffParsed.noDiffReason, "not_safe_to_apply");

process.stdout.write("mesh_worker_output_smoke ok cases=8\n");
