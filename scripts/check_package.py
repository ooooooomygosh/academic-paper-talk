#!/usr/bin/env python3
"""Validate package metadata, retained assets, links, and Python syntax."""
import ast
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/artifact-template-academic-paper-talk'


def check():
    for rel in ['SKILL.md', 'artifact-template.json', 'agents/openai.yaml', 'assets/reference.pptx', 'assets/preview.png']:
        assert (SKILL / rel).is_file(), f'Missing {rel}'
    manifest = json.loads((SKILL / 'artifact-template.json').read_text(encoding='utf-8'))
    assert manifest['kind'] == 'presentation'
    for key in ['reference', 'preview']:
        target = (SKILL / manifest[key]).resolve()
        assert target.is_relative_to(SKILL.resolve()) and target.is_file(), key
    assert (SKILL / manifest['preview']).read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    with zipfile.ZipFile(SKILL / manifest['reference']) as z:
        assert z.testzip() is None
        assert 'ppt/presentation.xml' in z.namelist()
    front = (SKILL / 'SKILL.md').read_text(encoding='utf-8').split('---', 2)[1]
    assert f'name: {SKILL.name}' in front
    for doc in ROOT.rglob('*.md'):
        if '.git' in doc.parts:
            continue
        content = doc.read_text(encoding='utf-8')
        assert not re.search(r'/Users/[^/\s]+/|thread://|01a0f606-2da6', content), f'Local context in {doc}'
        for target in re.findall(r'\]\(([^)]+)\)', content):
            if '://' not in target and not target.startswith('#'):
                assert (doc.parent / target.split('#')[0]).exists(), f'Broken link in {doc}: {target}'
    for py in ROOT.rglob('*.py'):
        if '.git' not in py.parts:
            ast.parse(py.read_text(encoding='utf-8'), filename=str(py))
    return True


if __name__ == '__main__':
    check()
    print('Package validation passed.')
