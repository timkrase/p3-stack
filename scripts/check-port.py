#!/usr/bin/env python3
"""Check skill discovery, local links, T3 tool boundaries, and upstream coverage."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = re.compile(
    r'Cursor|Task tool|subagent_type|run_in_background|cloud agent|\.cursor'
    r'|agent-transcripts|AskQuestion|^icon:|^color:|^reminder:|^mode:'
    r'|claude-|grok-|gpt-|/loop\b|p3-models\.mdc|cursor-team-kit'
    r'|control-ui|control-cli|browser\.preview|/visualize\b'
    r'|poteto-mode|poteto-agent|poteto-help|setup-pstack', re.M,
)


def check(root, upstream=None):
    errors = []
    skills = sorted((root / 'skills').glob('*/SKILL.md'))
    for path in skills:
        text = path.read_text()
        front = re.match(r'\A---\n(.*?)\n---\n', text, re.S)
        if not front:
            errors.append(f'{path.relative_to(root)}: missing frontmatter')
            continue
        names = re.findall(r'^name: (.+)$', front[1], re.M)
        if names != [path.parent.name]:
            errors.append(f'{path.relative_to(root)}: name must match directory')
        if not re.search(r'^description: \S', front[1], re.M):
            errors.append(f'{path.relative_to(root)}: missing description')
    for path in [*(root / 'skills').rglob('*.md'), *(root / 'agents').rglob('*.md')]:
        if 'node_modules' in path.relative_to(root).parts:
            continue
        text = path.read_text()
        for pattern, label in [(FORBIDDEN, 'unported mechanism'),
                               (re.compile(r'^(?:<{7}|={7}|>{7})', re.M), 'merge marker')]:
            for match in pattern.finditer(text):
                line = text.count('\n', 0, match.start()) + 1
                errors.append(f'{path.relative_to(root)}:{line}: {label}: {match[0]}')
        for target in re.findall(r'\[[^\]\n]+\]\(([^)\s]+)\)', text):
            target = target.split('#')[0]
            if not target or re.match(r'[a-z]+:', target) or '<' in target:
                continue
            if not (path.parent / target).exists():
                errors.append(f'{path.relative_to(root)}: broken local link: {target}')
        for line in text.splitlines():
            if ('t3_thread_launch' in line or 'create_threads' in line) and 'explicitly' not in line:
                errors.append(f'{path.relative_to(root)}: top-level threads need explicit user request')
    manifest = json.loads((root / 'UPSTREAM.json').read_text())
    sources = set()
    targets = set()
    for record in manifest['files']:
        source = record['source']
        if source in sources:
            errors.append(f'duplicate source: {source}')
        sources.add(source)
        if ('target' in record) == ('excluded' in record):
            errors.append(f'{source}: specify a target or an exclusion reason')
        if target := record.get('target'):
            if target in targets:
                errors.append(f'duplicate target: {target}')
            targets.add(target)
            if not (root / target).is_file():
                errors.append(f'{source}: missing target: {target}')
        elif not record.get('excluded'):
            errors.append(f'{source}: missing exclusion reason')
        if upstream:
            data = subprocess.check_output(['git', 'show', f"{manifest['commit']}:{source}"], cwd=upstream)
            if hashlib.sha256(data).hexdigest() != record['sha256']:
                errors.append(f'{source}: upstream hash mismatch')
    if upstream:
        paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', manifest['commit'], '--',
                                         *manifest['scope']], cwd=upstream, text=True).splitlines()
        for source in sorted(set(paths) ^ sources):
            errors.append(f'upstream coverage mismatch: {source}')
        plugin = json.loads(subprocess.check_output(['git', 'show',
            f"{manifest['commit']}:pstack/.cursor-plugin/plugin.json"], cwd=upstream))
        if plugin['version'] != manifest['version']:
            errors.append('upstream version does not match the pinned commit')
    return errors, len(skills), len(sources)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', type=Path, help='cursor/plugins checkout containing the pinned commit')
    args = parser.parse_args()
    errors, skills, sources = check(ROOT, args.upstream)
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'Checked {skills} skills and {sources} upstream file records.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
