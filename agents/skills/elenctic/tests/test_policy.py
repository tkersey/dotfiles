"""Executable policy-custody checks, not evidence of model adherence."""
from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('elenctic_policy', SKILL / 'scripts/freeze_policy.py')
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'skills'; self.root.mkdir()
        for path, content in {
            'elenctic/SKILL.md': '# Fixture skill\n',
            'elenctic/references/worker-review.md': '# Fixture worker\n',
            'elenctic/references/campaign.md': '# Fixture campaign\n',
            'elenctic/references/merge-policy.md': '# Fixture merge policy\n',
            'elenctic/references/prior-review-threads.md': '# Fixture discussion contract\n',
            'elenctic/references/campaign-brief.md': '# Fixture preparation\n',
            'elenctic/references/native-forks.md': '# Fixture fork transport\n',
            'elenctic/references/subagents.md': '# Fixture subagent transport\n',
            'elenctic/references/resolution.md': '# Fixture numbering and resolution\n',
            'elenctic/references/construction.md': '# Fixture construction\n',
            'elenctic/references/html-report.md': '# Fixture HTML contract\n',
            'elenctic/scripts/campaign_state.py': 'state = None\n',
            'elenctic/scripts/freeze_policy.py': (SKILL / 'scripts/freeze_policy.py').read_text(),
            'elenctic/scripts/report.py': 'report = None\n',
            'elenctic/assets/report.html': '<html></html>\n',
            'review-fold/references/admission.md': '# Shared admission\nValidate the current witness.\n',
            'review-fold/SKILL.md': '# Full workflow is not a frozen dependency.\n',
            'actuating/references/lenses/example.md': '# Semantic question\nPreserve the accepted law.\n' + policy.OUTPUT_BOUNDARY + '\nReturn native overall_correctness.\n',
            'actuating/references/review-contract.json': json.dumps({'required_lenses':[
                {'name':'standard','role':'standard'},
                {'name':'example','role':'auxiliary','instructions_ref':'agents/skills/actuating/references/lenses/example.md'}]})
        }.items():
            file=self.root/path; file.parent.mkdir(parents=True,exist_ok=True);file.write_text(content)
        self.destination = Path(self.temp.name) / 'snapshot'

    def tearDown(self):
        self.temp.cleanup()

    def test_semantic_projection_retains_source_and_snapshot_digests(self):
        root, identity = policy.freeze(self.root,self.destination)
        manifest = policy.verify(root,identity)
        path='actuating/references/lenses/example.md'
        projected=(root/path).read_text()
        self.assertIn('Preserve the accepted law.',projected)
        self.assertNotIn('overall_correctness',projected)
        self.assertIn('overall_correctness',(self.root/path).read_text())
        binding=next(f for f in manifest['files'] if f['path']==path)
        self.assertNotEqual(binding['source_sha256'],binding['snapshot_sha256'])
        self.assertEqual((root/'policy.json').stat().st_mode & 0o777,0o400)

    def test_installation_update_does_not_change_existing_snapshot(self):
        root, identity=policy.freeze(self.root,self.destination)
        (self.root/'elenctic/references/worker-review.md').write_text('# New installed policy\n')
        policy.verify(root,identity)
        self.assertEqual((root/'elenctic/references/worker-review.md').read_text(),'# Fixture worker\n')
        _, next_manifest=policy.capture(self.root)
        self.assertNotEqual(identity,next_manifest['policy_id'])

    def test_shared_admission_is_exact_and_bound_without_full_workflow(self):
        path = 'review-fold/references/admission.md'
        source = (self.root / path).read_bytes()
        root, identity = policy.freeze(self.root, self.destination)
        manifest = policy.verify(root, identity)
        self.assertEqual((root / path).read_bytes(), source)
        binding = next(f for f in manifest['files'] if f['path'] == path)
        self.assertEqual(binding['source_sha256'], policy.sha(source))
        self.assertEqual(binding['snapshot_sha256'], policy.sha(source))
        self.assertFalse((root / 'review-fold/SKILL.md').exists())
        (self.root / path).write_bytes(source + b'Changed authority.\n')
        policy.verify(root, identity)
        self.assertEqual((root / path).read_bytes(), source)
        _, next_manifest = policy.capture(self.root)
        self.assertNotEqual(identity, next_manifest['policy_id'])

    def test_missing_shared_admission_prevents_publication(self):
        (self.root / 'review-fold/references/admission.md').unlink()
        with self.assertRaises(FileNotFoundError):
            policy.freeze(self.root, self.destination)
        self.assertFalse(self.destination.exists())

    def test_changed_shared_admission_snapshot_is_rejected(self):
        root, identity = policy.freeze(self.root, self.destination)
        path = root / 'review-fold/references/admission.md'
        path.chmod(0o600)
        path.write_text('# Different authority\n')
        with self.assertRaises(ValueError):
            policy.verify(root, identity)

    def test_modified_snapshot_and_wrong_identity_rejected(self):
        root, identity=policy.freeze(self.root,self.destination)
        with self.assertRaises(ValueError):policy.verify(root,'sha256:invented')
        path=root/'elenctic/references/worker-review.md';path.chmod(0o600);path.write_text('changed')
        with self.assertRaises(ValueError):policy.verify(root,identity)

    def test_extra_snapshot_file_and_symlink_are_rejected(self):
        root, identity=policy.freeze(self.root,self.destination)
        extra=root/'injected.md';extra.write_text('not bound')
        with self.assertRaises(ValueError):policy.verify(root,identity)
        extra.unlink();file=root/'elenctic/SKILL.md';file.unlink();file.symlink_to(self.root/'elenctic/SKILL.md')
        with self.assertRaises(ValueError):policy.verify(root,identity)

    def test_ambiguous_or_missing_output_boundary_fails_without_snapshot(self):
        source=self.root/'actuating/references/lenses/example.md'
        for content in ['No boundary', policy.OUTPUT_BOUNDARY * 2]:
            source.write_text(content)
            with self.assertRaises(ValueError):policy.freeze(self.root,self.destination)
            self.assertFalse(self.destination.exists())

    def test_snapshot_is_not_overwritten_and_paths_cannot_escape(self):
        policy.freeze(self.root,self.destination)
        with self.assertRaises(ValueError):policy.freeze(self.root,self.destination)
        for path in ['../outside','/absolute','a/../../b','a\\b']:
            with self.subTest(path=path),self.assertRaises(ValueError):policy.relative(path)

    def test_source_changes_during_capture_are_detected(self):
        actual = Path.read_bytes
        for name in ('worker-review.md', 'admission.md'):
            with self.subTest(source=name):
                calls = {}
                def read(path):
                    value = actual(path)
                    if path.name == name:
                        calls[path] = calls.get(path, 0) + 1
                        if calls[path] > 1:
                            return value + b'changed'
                    return value
                with patch.object(Path, 'read_bytes', read), self.assertRaises(ValueError):
                    policy.freeze(self.root, self.destination)
                self.assertFalse(self.destination.exists())

    def test_installed_skill_symlink_is_copied_as_bytes(self):
        installed=self.root/'elenctic';target=Path(self.temp.name)/'owned-package'
        installed.rename(target);installed.symlink_to(target,target_is_directory=True)
        root,identity=policy.freeze(self.root,self.destination)
        policy.verify(root,identity)
        self.assertFalse((root/'elenctic/SKILL.md').is_symlink())

    def test_missing_adjudication_contract_prevents_publication(self):
        for name in ('elenctic/references/campaign.md', 'elenctic/references/worker-review.md',
                     'elenctic/references/merge-policy.md', 'elenctic/references/prior-review-threads.md',
                     'elenctic/scripts/freeze_policy.py'):
            path = self.root / name
            content = path.read_bytes()
            path.unlink()
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, name):
                policy.freeze(self.root, self.destination)
            self.assertFalse(self.destination.exists())
            path.write_bytes(content)

    def test_worker_dependencies_do_not_prevent_prior_thread_adjudication(self):
        cases = (
            ('elenctic/references/campaign-brief.md', 'fork'),
            ('elenctic/scripts/campaign_state.py', 'subagents'),
            ('elenctic/references/native-forks.md', 'fork'),
            ('elenctic/references/subagents.md', 'subagents'),
        )
        for index, (name, mode) in enumerate(cases):
            path = self.root / name
            content = path.read_bytes()
            path.unlink()
            root, identity = policy.freeze(self.root, self.destination.with_name(f'snapshot-{index}'))
            with self.subTest(name=name):
                policy.verify(root, identity, stage='adjudication')
                with self.assertRaisesRegex(ValueError, name):
                    policy.verify(root, identity, stage='workers', execution_mode=mode)
            path.write_bytes(content)

    def test_only_selected_execution_contract_is_required(self):
        for index, (mode, unused) in enumerate((('fork', 'subagents'), ('subagents', 'native-forks'))):
            path = self.root / f'elenctic/references/{unused}.md'
            content = path.read_bytes()
            path.unlink()
            root, identity = policy.freeze(self.root, self.destination.with_name(f'snapshot-{index}'))
            with self.subTest(mode=mode):
                policy.verify(root, identity, stage='workers', execution_mode=mode)
            path.write_bytes(content)

    def test_authenticated_snapshot_owns_its_readiness_requirements(self):
        root, identity = policy.freeze(self.root, self.destination)
        (self.root / 'elenctic/scripts/freeze_policy.py').write_text('raise RuntimeError("new installation")\n')
        with patch.dict(policy.STAGE_PATHS, workers=policy.STAGE_PATHS['workers'] | {'new-contract.md'}):
            policy.verify(root, identity)
            with self.assertRaisesRegex(ValueError, 'new-contract.md'):
                policy.verify(root, identity, stage='workers', execution_mode='subagents')
            result = subprocess.run([sys.executable, '-B', str(root / 'elenctic/scripts/freeze_policy.py'),
                                     'verify', '--root', str(root), '--policy-id', identity,
                                     '--stage', 'workers', '--execution-mode', 'subagents'],
                                    capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['ready_for'], {'stage': 'workers', 'execution_mode': 'subagents'})

    def test_delivery_requires_only_selected_presentation_inputs(self):
        full, full_identity = policy.freeze(self.root, self.destination.with_name('full'))
        policy.verify(full, full_identity, stage='delivery', workflow='construction', html=True)
        for name in ('elenctic/references/html-report.md', 'elenctic/scripts/report.py',
                     'elenctic/assets/report.html', 'elenctic/references/construction.md'):
            (self.root / name).unlink()
        root, identity = policy.freeze(self.root, self.destination)
        policy.verify(root, identity, stage='workers', execution_mode='subagents')
        for workflow in ('comments', 'resolution'):
            policy.verify(root, identity, stage='delivery', workflow=workflow)
            with self.assertRaisesRegex(ValueError, 'report.html'):
                policy.verify(root, identity, stage='delivery', workflow=workflow, html=True)
        with self.assertRaisesRegex(ValueError, 'construction.md'):
            policy.verify(root, identity, stage='delivery', workflow='construction')

    def test_all_delivery_workflows_require_canonical_numbering(self):
        (self.root / 'elenctic/references/resolution.md').unlink()
        root, identity = policy.freeze(self.root, self.destination)
        for workflow in ('comments', 'resolution', 'construction'):
            with self.subTest(workflow=workflow), self.assertRaisesRegex(ValueError, 'resolution.md'):
                policy.verify(root, identity, stage='delivery', workflow=workflow)

    def test_historical_v1_identity_is_independent_of_current_readiness(self):
        files = {
            'elenctic/SKILL.md': b'# Historical skill\n',
            'elenctic/references/campaign.md': b'# Historical campaign\n',
            'elenctic/references/worker-review.md': b'# Historical worker\n',
            'elenctic/references/resolution.md': b'# Historical numbering\n',
            'actuating/references/lenses/example.md': b'# Historical semantic question\n',
        }
        for path in ('review-fold/references/admission.md', 'actuating/references/review-contract.json'):
            files[path] = (self.root / path).read_bytes()
        digest = lambda value: 'sha256:' + hashlib.sha256(value).hexdigest()
        entries = []
        for name, content in sorted(files.items()):
            path = self.destination / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            entries.append({'path': name, 'source_sha256': digest(content), 'snapshot_sha256': digest(content)})
        body = {'schema': 'elenctic-policy/v1', 'files': entries,
                'lenses': [{'name': 'example', 'path': 'actuating/references/lenses/example.md'}]}
        identity = digest(json.dumps(body, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())
        (self.destination / 'policy.json').write_text(json.dumps({**body, 'policy_id': identity}))
        policy.verify(self.destination, identity)
        policy.verify(self.destination, identity, stage='delivery', workflow='comments')
        with self.assertRaisesRegex(ValueError, 'merge-policy.md'):
            policy.verify(self.destination, identity, stage='adjudication')

    def test_stage_does_not_reinterpret_unspecified_route(self):
        root, identity = policy.freeze(self.root, self.destination)
        cases = (
            {'stage': 'workers'}, {'stage': 'delivery'},
            {'execution_mode': 'fork'}, {'workflow': 'comments'}, {'html': True},
            {'stage': 'adjudication', 'execution_mode': 'fork'},
            {'stage': 'workers', 'execution_mode': 'subagents', 'html': True},
        )
        for options in cases:
            with self.subTest(options=options), self.assertRaises(ValueError):
                policy.verify(root, identity, **options)

    def test_cli_distinguishes_identity_and_selected_readiness(self):
        script = SKILL / 'scripts/freeze_policy.py'
        created = subprocess.run([sys.executable, '-B', str(script), 'create', '--skills-root',
                                  str(self.root), '--output', str(self.destination)], capture_output=True, text=True)
        self.assertEqual(created.returncode, 0, created.stderr)
        receipt = json.loads(created.stdout)
        self.assertEqual(receipt['ready_for'], {'stage': 'adjudication'})
        command = [sys.executable, '-B', str(script), 'verify', '--root', str(self.destination),
                   '--policy-id', receipt['policy_id']]
        checked = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertNotIn('ready_for', json.loads(checked.stdout))
        checked = subprocess.run(command + ['--stage', 'workers', '--execution-mode', 'subagents'],
                                 capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual(json.loads(checked.stdout)['ready_for'], {'stage': 'workers', 'execution_mode': 'subagents'})
        checked = subprocess.run(command + ['--stage', 'delivery', '--workflow', 'comments'],
                                 capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual(json.loads(checked.stdout)['ready_for'],
                         {'stage': 'delivery', 'workflow': 'comments', 'html': False})


if __name__=='__main__':
    unittest.main()
