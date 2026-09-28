"""Executable policy-custody checks, not evidence of model adherence."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
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
            'actuating/references/lenses/example.md': '# Semantic question\nPreserve the accepted law.\n' + policy.OUTPUT_BOUNDARY + '\nReturn native overall_correctness.\n',
            'actuating/references/review-contract.json': json.dumps({'required_lenses':[
                {'name':'standard','role':'standard'},
                {'name':'example','role':'auxiliary','instructions_ref':'codex/skills/actuating/references/lenses/example.md'}]})
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
        actual=Path.read_bytes; calls={}
        def read(path):
            value=actual(path)
            if path.name=='worker-review.md':
                calls[path]=calls.get(path,0)+1
                if calls[path]>1:return value+b'changed'
            return value
        with patch.object(Path,'read_bytes',read),self.assertRaises(ValueError):
            policy.freeze(self.root,self.destination)
        self.assertFalse(self.destination.exists())

    def test_installed_skill_symlink_is_copied_as_bytes(self):
        installed=self.root/'elenctic';target=Path(self.temp.name)/'owned-package'
        installed.rename(target);installed.symlink_to(target,target_is_directory=True)
        root,identity=policy.freeze(self.root,self.destination)
        policy.verify(root,identity)
        self.assertFalse((root/'elenctic/SKILL.md').is_symlink())


if __name__=='__main__':
    unittest.main()
