import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('check_port', ROOT / 'scripts/check-port.py')
port = importlib.util.module_from_spec(spec)
spec.loader.exec_module(port)


class PortChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.skill = self.root / 'skills/example/SKILL.md'
        self.skill.parent.mkdir(parents=True)
        self.skill.write_text('---\nname: example\ndescription: Example skill.\n---\n\n# Example\n')
        (self.root / 'UPSTREAM.json').write_text(json.dumps({'files': []}))

    def test_accepts_valid_skill(self):
        self.assertEqual(port.check(self.root)[0], [])

    def test_ignores_installed_test_dependencies(self):
        dependency = self.root / 'skills/example/scripts/node_modules/example/README.md'
        dependency.parent.mkdir(parents=True)
        dependency.write_text('Cursor dependency docs. [Contributing](CONTRIBUTING.md)\n')
        self.assertEqual(port.check(self.root)[0], [])

    def test_rejects_unported_delegation_and_missing_reference(self):
        with self.skill.open('a') as file:
            file.write('\nUse the Task tool.\n[missing](missing.md)\n')
        errors = port.check(self.root)[0]
        self.assertTrue(any('unported mechanism: Task tool' in error for error in errors), errors)
        self.assertTrue(any('broken local link: missing.md' in error for error in errors), errors)

    def test_rejects_mismatched_skill_name_and_merge_markers(self):
        self.skill.write_text(self.skill.read_text().replace('name: example', 'name: wrong') + '\n<<<<<<< ours\n')
        errors = port.check(self.root)[0]
        self.assertTrue(any('name must match directory' in error for error in errors), errors)
        self.assertTrue(any('merge marker' in error for error in errors), errors)

    def test_rejects_implicit_top_level_thread(self):
        with self.skill.open('a') as file:
            file.write('\nUse `t3_thread_launch` for every worker.\n')
        self.assertTrue(any('explicit user request' in error for error in port.check(self.root)[0]))

    def test_rejects_missing_ported_file(self):
        (self.root / 'UPSTREAM.json').write_text(json.dumps({'files': [
            {'source': 'pstack/skills/missing/SKILL.md', 'target': 'skills/missing/SKILL.md'}]}))
        self.assertTrue(any('missing target' in error for error in port.check(self.root)[0]))


class Installer(unittest.TestCase):
    def test_links_every_skill_is_repeatable_and_preserves_user_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            target = home / '.agents/skills'
            target.mkdir(parents=True)
            owned = target / 'bro'
            owned.mkdir()
            (owned / 'mine').write_text('keep me')
            (target / 'how').symlink_to(home / 'missing-old-install')
            env = {**os.environ, 'HOME': str(home)}
            for _ in range(2):
                subprocess.run(['bash', str(ROOT / 'install.sh')], env=env,
                               check=True, capture_output=True, text=True)
                for skill in (ROOT / 'skills').iterdir():
                    if skill.is_dir() and skill.name != 'bro':
                        self.assertTrue((target / skill.name).is_symlink(), skill.name)
                        self.assertEqual((target / skill.name).resolve(), skill.resolve())
                self.assertEqual((owned / 'mine').read_text(), 'keep me')
            project = home / 'project with spaces'
            subprocess.run(['bash', str(ROOT / 'install.sh'), '--project', str(project)],
                           env=env, check=True, capture_output=True, text=True)
            self.assertEqual((project / '.agents/skills/statechart/SKILL.md').read_bytes(),
                             (ROOT / 'skills/statechart/SKILL.md').read_bytes())


if __name__ == '__main__':
    unittest.main()
