#!/usr/bin/env node
// scripts/synthesize_recommendations.mjs — Merge per-surface partial recs into ranked recommendations.jsonl.
//
// Performs deterministic merging on exact-string `diff_sketch` duplicates
// (which are common: e.g. "levenshtein-1 typo correction" appears in 3+
// surface partials independently). Semantic merging — recs that touch the
// same source file in similar ways but with different prose — is the LLM-
// driven `subagents/synthesizer.md`'s job; spawn that subagent when the
// rec set still has obvious duplicates after this script runs.

import { existsSync, readFileSync, readdirSync, writeFileSync, renameSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { randomBytes } from 'node:crypto';

const HELP = `Usage: scripts/synthesize_recommendations.mjs <partial-dir> <output-jsonl>

Reads every partial recommendations file under <partial-dir>
(matching recommendations_*.jsonl), MERGES recs with identical \`diff_sketch\`
(union surface_ids; max per-dim uplift; max-component priority; preserve
first non-empty risk/test_plan/anchors), assigns one sequential R-NNN ID per
final ranked record, defaults applied=false /
applied_at=null / applied_commit_sha=null / deferred_reason=null /
triangulation=null / created_at=now / pass=current_pass, sorts by .priority desc with
.surface_ids length asc as tiebreaker, and writes the result to <output-jsonl>.

Args:
  <partial-dir>     Directory containing per-surface recommendations_*.jsonl
                    files produced by Phase 4 subagents.
  <output-jsonl>    Destination path for the merged file (typically
                    audit/recommendations.jsonl).

Exit codes:
  0  Success.
  2  Missing arguments (this usage printed).

Example:
  scripts/synthesize_recommendations.mjs \\
    audit/partial \\
    audit/recommendations.jsonl

Merging rules (per IO-CONTRACTS § recommendations.jsonl + synthesizer.md):
  - Group by exact \`diff_sketch\` string (case-sensitive, whitespace-trimmed).
  - For each group of size ≥ 2:
      surface_ids               = union (de-duplicated, sorted)
      expected_uplift_per_dim   = max across group, per dim
      expected_uplift_total     = sum of merged per-dim values, capped at 1000
      priority_components       = max across group, per component
      priority                  = recomputed product (frequency × score_gap × blast_radius)
      title                     = the SHORTEST title (most general phrasing)
      summary                   = first non-empty
      risk                      = first non-empty
      test_plan                 = first non-empty
      anchor_quote/_pattern     = first non-empty
      counter_example           = first non-empty
      operators_applied         = union (de-duplicated, preserving order)
      blast_radius_reason       = first non-empty
  - Singletons pass through unchanged.
`;

const [, , partialDir, outPath] = process.argv;

if (partialDir === '-h' || partialDir === '--help') {
  process.stdout.write(HELP);
  process.exit(0);
}

if (!partialDir || !outPath) {
  process.stderr.write(HELP);
  process.exit(2);
}

const manifestPath = join(dirname(outPath), 'manifest.json');
let currentPass = 1;
if (existsSync(manifestPath)) {
  try {
    const manifest = JSON.parse(readFileSync(manifestPath, 'utf-8'));
    if (Number.isInteger(manifest.current_pass) && manifest.current_pass >= 1) {
      currentPass = manifest.current_pass;
    }
  } catch {
    currentPass = 1;
  }
}

let allRecs = [];
const files = readdirSync(partialDir)
  .filter(f => f.startsWith('recommendations_') && f.endsWith('.jsonl'))
  .sort((a, b) => a.localeCompare(b));

for (const f of files) {
  const content = readFileSync(join(partialDir, f), 'utf-8');
  for (const line of content.split('\n')) {
    if (!line.trim()) continue;
    try {
      allRecs.push(JSON.parse(line));
    } catch (e) {
      console.error(`skipping malformed line in ${f}: ${e.message}`);
    }
  }
}

// ---- Deterministic merge step ----
//
// Group recs by exact `diff_sketch` (whitespace-trimmed). Within each group of
// size > 1, fold per the rules documented in HELP. Singletons pass through
// unchanged. Recs with empty/missing diff_sketch are not grouped (each becomes
// its own singleton — we don't pretend they're "the same" without evidence).
const inputCount = allRecs.length;

const groups = new Map();
const singletons = [];
for (const rec of allRecs) {
  const ds = (rec.diff_sketch ?? '').trim();
  if (!ds) {
    singletons.push(rec);
    continue;
  }
  if (!groups.has(ds)) groups.set(ds, []);
  groups.get(ds).push(rec);
}

const firstNonEmpty = (arr, key) => {
  for (const r of arr) {
    const v = r?.[key];
    if (v !== undefined && v !== null && v !== '') return v;
  }
  return undefined;
};

const unionStrings = (arr, key) => {
  const seen = new Set();
  const out = [];
  for (const r of arr) {
    for (const s of (r?.[key] ?? [])) {
      if (!seen.has(s)) { seen.add(s); out.push(s); }
    }
  }
  return out;
};

const maxComponents = (arr) => {
  const out = {};
  for (const r of arr) {
    const c = r?.priority_components ?? {};
    for (const k of Object.keys(c)) {
      if (typeof c[k] === 'number') {
        out[k] = Math.max(out[k] ?? -Infinity, c[k]);
      } else if (out[k] === undefined) {
        out[k] = c[k]; // preserve non-numeric like blast_radius_reason: pick first via firstNonEmpty below
      }
    }
  }
  // For string fields like blast_radius_reason, prefer first-non-empty across the group.
  const reason = firstNonEmpty(arr.map(r => r?.priority_components ?? {}), 'blast_radius_reason');
  if (reason !== undefined) out.blast_radius_reason = reason;
  return out;
};

const maxPerDim = (arr) => {
  const out = {};
  for (const r of arr) {
    const u = r?.expected_uplift_per_dim ?? {};
    for (const k of Object.keys(u)) {
      if (typeof u[k] === 'number') {
        out[k] = Math.max(out[k] ?? 0, u[k]);
      }
    }
  }
  return out;
};

// If a rec has priority_components but no top-level priority, compute it
// from the components per PRIORITY-FORMULA.md (frequency × score_gap ×
// blast_radius). The merge path (group.length > 1) already recomputes from
// max-components; without a matching pass for singletons, a partial that
// emitted components-only landed in the final file with priority=null,
// mis-sorted to the bottom (since `null ?? 0 = 0` < any positive priority),
// and bypassed the "highest priority first" applier ordering.
const fillPriority = (rec) => {
  if (rec.priority !== undefined && rec.priority !== null) return rec;
  const c = rec.priority_components ?? {};
  if (typeof c.frequency === 'number' && typeof c.score_gap === 'number' && typeof c.blast_radius === 'number') {
    rec.priority = c.frequency * c.score_gap * c.blast_radius;
  }
  return rec;
};

const merged = [...singletons.map(fillPriority)];
let mergeCount = 0;

for (const [ds, group] of groups) {
  if (group.length === 1) {
    merged.push(fillPriority(group[0]));
    continue;
  }
  mergeCount += group.length - 1; // count of recs collapsed into the group's representative

  const surface_ids = unionStrings(group, 'surface_ids').sort();
  const expected_uplift_per_dim = maxPerDim(group);
  const expected_uplift_total = Math.min(
    1000,
    Object.values(expected_uplift_per_dim).reduce((s, v) => s + (v ?? 0), 0)
  );
  const priority_components = maxComponents(group);
  const f = priority_components.frequency ?? 0;
  const sg = priority_components.score_gap ?? 0;
  const br = priority_components.blast_radius ?? 0;
  const priority = f * sg * br;
  // Title: shortest (most general) phrasing.
  const title = group
    .map(r => r?.title ?? '')
    .filter(Boolean)
    .sort((a, b) => a.length - b.length)[0] ?? '';
  const operators_applied = unionStrings(group, 'operators_applied');

  // Carry through prior-pass lifecycle fields from input partials. If any
  // input rec already has applied=true / applied_at / applied_commit_sha
  // (e.g. a re-run that re-grouped a previously-applied rec), those must
  // survive the merge. Otherwise the post-merge default-fill below would
  // silently reset applied to false, erasing the pass-N application record.
  // Note: recommendation_id is intentionally NOT carried — the post-merge
  // loop reassigns sequential R-NNN authoritatively (partial agents often
  // emit placeholder template IDs that would collide if preserved).
  const carry = {};
  if (group.some(r => r?.applied === true)) carry.applied = true;
  for (const k of ['applied_at', 'applied_commit_sha', 'deferred_reason', 'triangulation', 'created_at']) {
    const v = firstNonEmpty(group, k);
    if (v !== undefined) carry[k] = v;
  }

  merged.push({
    title,
    summary: firstNonEmpty(group, 'summary') ?? '',
    surface_ids,
    diff_sketch: ds,
    expected_uplift_per_dim,
    expected_uplift_total,
    risk: firstNonEmpty(group, 'risk') ?? '',
    test_plan: firstNonEmpty(group, 'test_plan') ?? '',
    priority,
    priority_components,
    anchor_quote: firstNonEmpty(group, 'anchor_quote') ?? '',
    anchor_pattern: firstNonEmpty(group, 'anchor_pattern') ?? '',
    counter_example: firstNonEmpty(group, 'counter_example') ?? '',
    operators_applied,
    ...(carry.applied !== undefined ? { applied: carry.applied } : {}),
    ...(carry.applied_at !== undefined ? { applied_at: carry.applied_at } : {}),
    ...(carry.applied_commit_sha !== undefined ? { applied_commit_sha: carry.applied_commit_sha } : {}),
    ...(carry.deferred_reason !== undefined ? { deferred_reason: carry.deferred_reason } : {}),
    ...(carry.triangulation !== undefined ? { triangulation: carry.triangulation } : {}),
    ...(carry.created_at !== undefined ? { created_at: carry.created_at } : {}),
  });
}

allRecs = merged;
const outputCount = allRecs.length;

// Sort by priority desc; ties broken by smaller diff (effort heuristic = number of files in surface_ids)
allRecs.sort((a, b) => {
  const pa = a.priority ?? 0;
  const pb = b.priority ?? 0;
  if (pb !== pa) return pb - pa;
  const sa = (a.surface_ids?.length ?? 1);
  const sb = (b.surface_ids?.length ?? 1);
  if (sa !== sb) return sa - sb;
  const da = a.diff_sketch ?? '';
  const db = b.diff_sketch ?? '';
  if (da !== db) return da.localeCompare(db);
  const ta = a.title ?? '';
  const tb = b.title ?? '';
  if (ta !== tb) return ta.localeCompare(tb);
  return JSON.stringify(a.surface_ids ?? []).localeCompare(JSON.stringify(b.surface_ids ?? []));
});

// Assign final sequential IDs after sorting. Partial recommendation files often
// come from separate agents using the same template IDs; preserving those IDs
// would produce duplicate R-NNN keys, ambiguous Phase 5 application, and
// colliding regression-test filenames.
let nextId = 1;
const padId = (n) => `R-${String(n).padStart(3, '0')}`;
for (const rec of allRecs) {
  rec.recommendation_id = padId(nextId);
  nextId++;
  if (!Number.isInteger(rec.pass) || rec.pass < 1) rec.pass = currentPass;
  if (rec.applied === undefined) rec.applied = false;
  if (rec.applied_at === undefined) rec.applied_at = null;
  if (rec.applied_commit_sha === undefined) rec.applied_commit_sha = null;
  if (rec.deferred_reason === undefined) rec.deferred_reason = null;
  // Default the remaining IO-CONTRACTS fields so every emitted record matches
  // the recommendations.jsonl schema even if a partial omitted them.
  if (rec.triangulation === undefined) rec.triangulation = null;
  if (rec.created_at === undefined) rec.created_at = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
}

// Write out via tmp + atomic rename. The previous direct `writeFileSync`
// raced against `tools/flip_applied.sh`: that script does an flock'd
// tmp+rename on the same file. Synthesizer's plain `writeFileSync` is NOT
// atomic (the kernel may flush partial bytes), and the two operations use
// different lock domains — so a re-synthesize kicked off while Phase 5
// appliers were still flipping `applied:true` could:
//   (a) overwrite a fresh applied=true flip that landed between our
//       readdirSync at script start and writeFileSync here, OR
//   (b) leave a partially-written file that flip_applied.sh's jq read
//       chokes on.
// Same-filesystem rename is atomic on POSIX, so a concurrent reader either
// sees the old file in full or the new file in full, never a torn write.
const out = allRecs.map(r => JSON.stringify(r)).join('\n') + '\n';
const tmpPath = `${outPath}.tmp.${process.pid}.${randomBytes(4).toString('hex')}`;
writeFileSync(tmpPath, out);
renameSync(tmpPath, outPath);

console.log(`synthesized ${outputCount} recommendations to ${outPath} (input partials: ${inputCount}; merged: ${mergeCount})`);
if (outputCount > 0) {
  console.log(`top-priority: ${allRecs[0]?.recommendation_id} (priority ${allRecs[0]?.priority?.toFixed(3)})`);
  console.log(`bottom-priority: ${allRecs[allRecs.length - 1]?.recommendation_id} (priority ${allRecs[allRecs.length - 1]?.priority?.toFixed(3)})`);
}
