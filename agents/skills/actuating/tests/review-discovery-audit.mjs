import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const ordered = values => [...values].sort();
const fail = message => { throw new Error(message); };
const object = (value, path) => {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) fail(`${path} must be an object`);
  return value;
};
const text = (value, path) => {
  if (typeof value !== 'string' || !value.trim()) fail(`${path} must be a nonempty string`);
  return value;
};
const array = (value, path) => {
  if (!Array.isArray(value)) fail(`${path} must be an array`);
  return value;
};
const choice = (value, values, path) => {
  if (!values.includes(value)) fail(`${path} must be one of ${values.join(', ')}`);
  return value;
};
const sha256 = (value, path) => {
  if (typeof value !== 'string' || !/^[a-f0-9]{64}$/.test(value)) fail(`${path} must be a SHA-256`);
  return value;
};
const boundHash = (value, expected, path) => {
  if (sha256(value, path) !== expected) fail(`${path} does not match its subject`);
};
const boundSubject = (value, expected, path) => {
  if (text(value, path) !== expected) fail(`${path} does not match its subject`);
};
const unique = (set, value, path) => {
  if (set.has(value)) fail(`Duplicate ${path}: ${value}`);
  set.add(value);
};

function witnesses(value, path) {
  const ids = new Set();
  return array(value, path).map((item, index) => {
    object(item, `${path}[${index}]`);
    const id = text(item.id, `${path}[${index}].id`);
    unique(ids, id, `${path} witness`);
    return {id, evidence_ref: text(item.evidence_ref, `${path}[${index}].evidence_ref`)};
  });
}

function cost(value, path) {
  if (value === null) return {tokens: null, execution_ms: null};
  object(value, path);
  return Object.fromEntries(['tokens', 'execution_ms'].map(name => {
    const number = value[name];
    if (number !== null && (typeof number !== 'number' || !Number.isFinite(number) || number < 0
      || (name === 'tokens' && !Number.isSafeInteger(number)))) fail(`${path}.${name} must be nonnegative or null`);
    return [name, number];
  }));
}

function sumCosts(values) {
  return Object.fromEntries(['tokens', 'execution_ms'].map(name => {
    const measured_subtotal = values.reduce((total, item) => total + (item[name] ?? 0), 0);
    if (!Number.isFinite(measured_subtotal) || (name === 'tokens' && !Number.isSafeInteger(measured_subtotal)))
      fail(`Measured ${name} subtotal exceeds the numeric range`);
    return [name, {measured_subtotal, unknown_count: values.filter(item => item[name] === null).length}];
  }));
}

function episode(value, subject) {
  if (value === null) return null;
  object(value, 'episode');
  boundSubject(value.subject_id, subject.id, 'episode.subject_id');
  const claim = choice(value.claim, ['complete', 'incomplete'], 'episode.claim');
  const final_sha256 = sha256(value.final_sha256, 'episode.final_sha256');
  const assessment_ref = text(value.assessment_ref, 'episode.assessment_ref');
  const assessment = object(value.assessment, 'episode.assessment');
  boundHash(assessment.candidate_sha256, final_sha256, 'episode.assessment.candidate_sha256');
  boundHash(assessment.goal_sha256, subject.goal_sha256, 'episode.assessment.goal_sha256');
  const execution = choice(assessment.execution, ['complete', 'unavailable'], 'episode.assessment.execution');
  if (typeof assessment.artifact_pass !== 'boolean') fail('episode.assessment.artifact_pass must be boolean');
  if (typeof assessment.candidate_stable !== 'boolean') fail('episode.assessment.candidate_stable must be boolean');
  const protectedChanges = array(assessment.protected_changes, 'episode.assessment.protected_changes');
  protectedChanges.forEach(item => text(item, 'episode.assessment.protected_changes entry'));
  const observations = array(assessment.observations, 'episode.assessment.observations');
  observations.forEach((item, index) => {
    object(item, `episode.assessment.observations[${index}]`);
    if (typeof item.pass !== 'boolean') fail(`episode.assessment.observations[${index}].pass must be boolean`);
  });
  if (execution === 'complete' && !observations.length) fail('Complete assessment has no observations');
  const available = execution === 'complete' && assessment.candidate_stable;
  const supportedPass = available && protectedChanges.length === 0 && observations.every(item => item.pass);
  if (assessment.artifact_pass !== supportedPass) fail('Assessment artifact_pass contradicts execution, stability, protected inputs, or observations');
  const outcome = !available ? 'unavailable' : assessment.artifact_pass ? 'bounded_pass' : 'bounded_fail';
  return {subject_id: subject.id, goal_sha256: subject.goal_sha256, claim, final_sha256, assessment_ref, outcome,
    assessment_execution: execution, candidate_stable: assessment.candidate_stable,
    protected_changes: [...protectedChanges], observation_count: observations.length,
    failed_observation_count: observations.filter(item => !item.pass).length,
    complete_claim_contradiction: claim !== 'complete' ? false : outcome === 'unavailable' ? 'unknown' : outcome === 'bounded_fail',
    cost: sumCosts([cost(value.cost, 'episode.cost')])};
}

export function auditReviewDiscovery(input) {
  object(input, 'input');
  const evidence_kind = choice(input.evidence_kind, ['synthetic', 'observed'], 'evidence_kind');
  const subject = object(input.subject, 'subject');
  const identity = {id: text(subject.id, 'subject.id'), sha256: sha256(subject.sha256, 'subject.sha256'),
    goal_sha256: sha256(subject.goal_sha256, 'subject.goal_sha256'),
    evidence_ref: text(subject.evidence_ref, 'subject.evidence_ref')};
  const audit = input.audit ?? null;
  let auditScope = 'unavailable', auditRef = null, audited = [];
  const applicability = new Map();
  if (audit !== null) {
    object(audit, 'audit');
    boundSubject(audit.subject_id, identity.id, 'audit.subject_id');
    boundHash(audit.subject_sha256, identity.sha256, 'audit.subject_sha256');
    auditScope = choice(audit.scope, ['bounded', 'unknown'], 'audit.scope');
    auditRef = text(audit.evidence_ref, 'audit.evidence_ref');
    audited = witnesses(audit.witnesses, 'audit.witnesses');
    audit.witnesses.forEach((witness, index) => {
      const applicable = new Set();
      array(witness.applies_to, `audit.witnesses[${index}].applies_to`).forEach(id =>
        unique(applicable, text(id, 'applicable attempt identity'), 'applicable attempt identity'));
      applicability.set(witness.id, applicable);
    });
  }
  const seen = new Set(), attemptIds = new Set(), batchIds = new Set(), ordinals = new Set();
  const evidence = new Map(), attempts = [], costs = [];
  const remember = ({id, evidence_ref}) => {
    if (!evidence.has(id)) evidence.set(id, new Set());
    evidence.get(id).add(evidence_ref);
  };
  audited.forEach(remember);
  const batches = array(input.batches, 'batches').map((batch, batchIndex) => {
    object(batch, `batches[${batchIndex}]`);
    const id = text(batch.id, `batches[${batchIndex}].id`);
    unique(batchIds, id, 'batch identity');
    const entries = array(batch.attempts, `batch ${id}.attempts`);
    if (!entries.length) fail(`Batch ${id} has no attempts`);
    const found = new Set();
    const reviewed = entries.map((entry, index) => {
      const path = `batch ${id}.attempts[${index}]`;
      object(entry, path);
      const attemptId = text(entry.id, `${path}.id`);
      unique(attemptIds, attemptId, 'attempt identity');
      boundSubject(entry.subject_id, identity.id, `${path}.subject_id`);
      boundHash(entry.subject_sha256, identity.sha256, `${path}.subject_sha256`);
      const scope = choice(entry.scope, ['changeset', 'file'], `${path}.scope`);
      const focus = scope === 'file' ? text(entry.focus, `${path}.focus`) : entry.focus;
      if (scope === 'changeset' && focus !== null) fail(`${path}.focus must be null for changeset scope`);
      const lens = text(entry.lens, `${path}.lens`);
      const standard_ordinal = entry.standard_ordinal;
      if (scope === 'changeset' && lens === 'standard') {
        if (!Number.isSafeInteger(standard_ordinal) || standard_ordinal < 1) fail(`${path}.standard_ordinal must be positive`);
        unique(ordinals, standard_ordinal, 'changeset standard ordinal');
      } else if (standard_ordinal !== null) fail(`${path}.standard_ordinal must be null outside changeset standard`);
      const execution = choice(entry.execution, ['complete', 'incomplete'], `${path}.execution`);
      const credit = choice(entry.credit, ['credit', 'hold'], `${path}.credit`);
      const inquiry = choice(entry.inquiry, ['adequate', 'incomplete', 'unknown'], `${path}.inquiry`);
      const report_ref = text(entry.report_ref, `${path}.report_ref`);
      const findings = witnesses(entry.findings, `${path}.findings`);
      const credit_issues = credit === 'hold' ? [] : [
        ...(execution !== 'complete' ? ['execution_incomplete'] : []),
        ...(inquiry !== 'adequate' ? [`inquiry_${inquiry}`] : []),
        ...(findings.length ? ['reported_findings'] : [])
      ];
      findings.forEach(item => { remember(item); found.add(item.id); });
      costs.push(cost(entry.cost, `${path}.cost`));
      const reported_witnesses = ordered(findings.map(item => item.id));
      const outcome = findings.length ? 'findings' : execution === 'incomplete' || inquiry === 'incomplete' ? 'incomplete'
        : inquiry === 'unknown' ? 'unknown' : credit === 'hold' ? 'held' : 'clean';
      const result = {id: attemptId, scope, focus, lens, standard_ordinal, execution, credit, credit_issues, inquiry, report_ref, outcome,
        credited_clean: outcome === 'clean', reported_witnesses,
        new_to_prior_batches: reported_witnesses.filter(item => !seen.has(item)),
        repeated_from_prior_batches: reported_witnesses.filter(item => seen.has(item))};
      attempts.push(result);
      return result;
    }).sort((a, b) => a.id.localeCompare(b.id));
    const reportsPerWitness = new Map();
    for (const item of reviewed) for (const witness of item.reported_witnesses)
      reportsPerWitness.set(witness, (reportsPerWitness.get(witness) ?? 0) + 1);
    for (const item of reviewed)
      item.exclusive_in_batch = item.reported_witnesses.filter(witness => reportsPerWitness.get(witness) === 1);
    const new_witnesses = ordered([...found].filter(item => !seen.has(item)));
    const repeated_witnesses = ordered([...found].filter(item => seen.has(item)));
    found.forEach(item => seen.add(item));
    return {id, attempts: reviewed, new_witnesses, repeated_witnesses, cumulative_witnesses: ordered(seen)};
  });
  for (const ids of applicability.values()) for (const id of ids)
    if (!attemptIds.has(id)) fail(`Unknown applicable attempt identity: ${id}`);
  const auditIds = new Set(audited.map(item => item.id));
  const allWitnesses = ordered(evidence.keys()).map(id => {
    const detected_by = [], missed_by = [], unresolved_by = [];
    for (const attempt of attempts) {
      if (attempt.reported_witnesses.includes(id)) detected_by.push(attempt.id);
      else if (attempt.execution === 'complete' && attempt.inquiry === 'adequate' && applicability.get(id)?.has(attempt.id)) missed_by.push(attempt.id);
      else unresolved_by.push(attempt.id);
    }
    return {id, evidence_refs: ordered(evidence.get(id)), audited_present: auditIds.has(id), applies_to: ordered(applicability.get(id) ?? []),
      detected_by: ordered(detected_by), missed_by: ordered(missed_by), unresolved_by: ordered(unresolved_by)};
  });
  const credited_clean_misses = attempts.filter(item => item.credited_clean).map(item => ({
    id: item.id, witnesses: allWitnesses.filter(witness => witness.missed_by.includes(item.id)).map(witness => witness.id)
  })).filter(item => item.witnesses.length).sort((a, b) => a.id.localeCompare(b.id));
  return {evidence_kind, subject: identity, batches, witnesses: allWitnesses,
    residual: {
      status: allWitnesses.length ? 'witnesses_present' : auditScope === 'bounded' ? 'none_in_audited_scope' : 'unknown',
      audit_scope: auditScope, audit_ref: auditRef,
      audited_unreported_witnesses: ordered([...auditIds].filter(id => !seen.has(id))), credited_clean_misses
    },
    review_cost: sumCosts(costs), episode: episode(input.episode ?? null, identity)};
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    if (process.argv.length !== 3) fail('Usage: node review-discovery-audit.mjs INPUT.json');
    console.log(JSON.stringify(auditReviewDiscovery(JSON.parse(readFileSync(process.argv[2], 'utf8'))), null, 2));
  } catch (error) {
    console.error(String(error));
    process.exitCode = 2;
  }
}
