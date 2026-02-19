function extractFenceBody(text, info) {
  if (typeof text !== "string" || !text) return null;
  const marker = `\`\`\`${info}`;
  const fenceIdx = text.indexOf(marker);
  if (fenceIdx === -1) return null;
  const after = text.slice(fenceIdx + marker.length);
  const end = after.indexOf("```");
  if (end === -1) return null;
  const body = after.slice(0, end).replace(/^\n/, "").trim();
  return body || null;
}

export function extractDiff(text) {
  if (typeof text !== "string" || !text) return { diff: null, format: "none" };

  const diffFence = extractFenceBody(text, "diff");
  if (diffFence) return { diff: diffFence, format: "diff_fence" };

  const patchFence = extractFenceBody(text, "patch");
  if (patchFence) return { diff: patchFence, format: "patch_fence" };

  const lines = text.split("\n");
  let start = -1;
  for (let i = 0; i < lines.length; i += 1) {
    if (lines[i].startsWith("diff --git ")) {
      start = i;
      break;
    }
  }
  if (start !== -1) {
    const body = lines.slice(start).join("\n").trim();
    if (body) return { diff: body, format: "git_header" };
  }

  const unifiedStart = lines.findIndex((line) => line.startsWith("--- "));
  if (unifiedStart !== -1) {
    const hasPlusPlus = lines.slice(unifiedStart).some((line) => line.startsWith("+++ "));
    const hasHunk = lines.slice(unifiedStart).some((line) => line.startsWith("@@ "));
    if (hasPlusPlus && hasHunk) {
      const body = lines.slice(unifiedStart).join("\n").trim();
      if (body) return { diff: body, format: "unified_hunk" };
    }
  }

  return { diff: null, format: "none" };
}

export function extractNoDiffReason(text) {
  if (typeof text !== "string" || !text) return null;
  const match = text.match(/NO_DIFF\s*:\s*(.+)/i);
  if (!match || typeof match[1] !== "string") return null;
  const cleaned = match[1].trim();
  return cleaned ? cleaned : null;
}

export function collectPatchCandidateTexts(collected) {
  const out = [];
  const seen = new Set();
  const push = (value) => {
    if (typeof value !== "string") return;
    const trimmed = value.trim();
    if (!trimmed || seen.has(trimmed)) return;
    seen.add(trimmed);
    out.push(trimmed);
  };

  push(collected?.agentMessageText);
  const items = Array.isArray(collected?.items) ? collected.items : [];
  for (const item of items) {
    push(item?.text);
    push(item?.output);
    push(item?.stdout);
    push(item?.stderr);
    push(item?.result?.output);
    push(item?.result?.stdout);
    push(item?.result?.stderr);
    const content = Array.isArray(item?.content) ? item.content : [];
    for (const part of content) {
      push(part?.text);
      push(part?.output);
      push(part?.stdout);
      push(part?.stderr);
    }
  }
  return out;
}

export function parseStrictOutputArtifact(text) {
  if (typeof text !== "string" || !text) {
    return { diff: null, parseFormat: "none", noDiffReason: null, failureCode: "no_diff_parsed" };
  }

  const trimmed = text.trim();
  if (!trimmed) {
    return { diff: null, parseFormat: "none", noDiffReason: null, failureCode: "no_diff_parsed" };
  }

  const diffMatch = trimmed.match(/^```diff\r?\n([\s\S]*?)\r?\n```$/);
  if (diffMatch && typeof diffMatch[1] === "string") {
    const body = diffMatch[1].trim();
    if (body) {
      return { diff: body, parseFormat: "diff_fence", noDiffReason: null, failureCode: null };
    }
  }

  const noDiffMatch = trimmed.match(/^NO_DIFF\s*:\s*([^\r\n].*)$/i);
  if (noDiffMatch && typeof noDiffMatch[1] === "string") {
    const reason = noDiffMatch[1].trim();
    if (reason) {
      return { diff: null, parseFormat: "none", noDiffReason: reason, failureCode: "no_patch_returned" };
    }
  }

  return { diff: null, parseFormat: "none", noDiffReason: null, failureCode: "no_diff_parsed" };
}

export function classifyMeshOutput(collected, opts = {}) {
  const strictOutput = opts.strictOutput === true;
  const statusHint = typeof opts.statusHint === "string" ? opts.statusHint : null;
  const candidates = collectPatchCandidateTexts(collected);

  if (strictOutput) {
    let firstNoDiffReason = null;
    for (const candidateText of candidates) {
      const parsed = parseStrictOutputArtifact(candidateText);
      if (parsed.failureCode === null) {
        return parsed;
      }
      if (!firstNoDiffReason && parsed.failureCode === "no_patch_returned") {
        firstNoDiffReason = parsed.noDiffReason ?? null;
      }
    }

    if (firstNoDiffReason) {
      return {
        diff: null,
        parseFormat: "none",
        noDiffReason: firstNoDiffReason,
        failureCode: "no_patch_returned",
      };
    }

    if (statusHint && statusHint !== "completed") {
      return { diff: null, parseFormat: "none", noDiffReason: null, failureCode: "no_response" };
    }
    return { diff: null, parseFormat: "none", noDiffReason: null, failureCode: "no_diff_parsed" };
  }

  for (const candidateText of candidates) {
    const parsed = extractDiff(candidateText);
    if (parsed.diff) {
      return { diff: parsed.diff, parseFormat: parsed.format, noDiffReason: null, failureCode: null };
    }
  }

  let noDiffReason = null;
  for (const candidateText of candidates) {
    noDiffReason = extractNoDiffReason(candidateText);
    if (noDiffReason) break;
  }
  if (!noDiffReason) {
    noDiffReason = extractNoDiffReason(collected?.agentMessageText ?? "");
  }
  if (noDiffReason) {
    return { diff: null, parseFormat: "none", noDiffReason, failureCode: "no_patch_returned" };
  }

  if (statusHint && statusHint !== "completed") {
    return { diff: null, parseFormat: "none", noDiffReason: null, failureCode: "no_response" };
  }
  return { diff: null, parseFormat: "none", noDiffReason: null, failureCode: "no_diff_parsed" };
}
