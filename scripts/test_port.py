import importlib.util
import json
import os
import re
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

    def test_skill_paths_resolve_from_the_linked_skill_directory(self):
        brief = self.root / 'agents/brief.md'
        brief.parent.mkdir()
        brief.write_text('# Brief\n')
        (self.root / 'skills/other').mkdir()
        (self.root / 'skills/other/SKILL.md').write_text('---\nname: other\ndescription: Other skill.\n---\n')
        (self.root / 'skills/example/references').mkdir()
        (self.root / 'skills/example/references/note.md').write_text('# Note\n')
        playbook = self.root / 'skills/example/playbooks/run.md'
        playbook.parent.mkdir()
        playbook.write_text('Read `playbooks/run.md`, `../references/note.md` and `../other/SKILL.md`.\n')
        with self.skill.open('a') as file:
            file.write('\nRead `agents/brief.md`, then `../../agents/brief.md#top`.\n'
                       'Ignore `../<name>/SKILL.md`, `~/.agents/models.md`, `/tmp/a/b.md`,\n'
                       '`https://example.com/a/b.md`, `.agents/skills/**/*-mode/SKILL.md`,\n'
                       'and `git show origin/main:skills/x/SKILL.md`.\n'
                       '````markdown\nRun `skills/other/SKILL.md` from the target repo.\n````\n')
        errors = port.check(self.root)[0]
        self.assertEqual(sorted(errors), [
            'skills/example/SKILL.md:8: broken skill path: ../../agents/brief.md',
            'skills/example/SKILL.md:8: broken skill path: agents/brief.md',
        ])

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


class InstalledSkillPaths(unittest.TestCase):
    """Installers link each skill directory; agents join paths from the link, not its target."""

    HOMES = ('.claude/skills', '.agents/skills', '.t2-claude-proxy/home/skills')
    BRIEFS = [('p3-mode', 'agents/p3-agent.md'), ('no-comments', 'agents/comment-sicko.md')]
    maxDiff = None

    def test_agent_briefs_and_cross_skill_paths_resolve_in_every_home(self):
        references = list(self.BRIEFS)
        for skill in ('p3-mode', 'no-comments', 'p3-help'):
            for path in (ROOT / 'skills' / skill).rglob('*.md'):
                if path.parent.name == 'agents':
                    continue
                for _, ref in port.skill_paths(path.read_text()):
                    if 'agents/' in ref or re.fullmatch(r'\.\./[\w-]+/SKILL\.md', ref):
                        references.append((skill, ref))
        # A brief declares the skill directory as its base, so every path in it must resolve from there.
        briefs = sorted((ROOT / 'skills').glob('*/agents/*.md'))
        brief_references = [(path.parents[1].name, ref) for path in briefs
                            for _, ref in port.skill_paths(path.read_text())]
        references += brief_references
        with tempfile.TemporaryDirectory() as temporary:
            missing = []
            for home in self.HOMES:
                skills = Path(temporary) / home
                skills.mkdir(parents=True)
                for skill in (ROOT / 'skills').iterdir():
                    if skill.is_dir():
                        subprocess.run(['ln', '-sfn', f'{skill}/', str(skills / skill.name)], check=True)
                for skill, ref in sorted(set(references)):
                    target = skills / skill / ref
                    if not (os.path.isfile(os.path.normpath(target)) and os.path.isfile(target)):
                        missing.append(f'{home}/{skill}: {ref}')
            self.assertEqual(missing, [])
        self.assertIn(('p3-help', '../p3-mode/agents/p3-agent.md'), references)
        self.assertEqual({path.relative_to(ROOT).as_posix() for path in briefs},
                         {f'skills/{skill}/{ref}' for skill, ref in self.BRIEFS})
        self.assertTrue(brief_references)


if __name__ == '__main__':
    unittest.main()
