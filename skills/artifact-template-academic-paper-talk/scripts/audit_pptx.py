#!/usr/bin/env python3
"""Read-only structural checks for a paper talk; never a substitute for visual QA."""
import argparse
import json
import posixpath
import re
import sys
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
}
PROMPT_LABEL = re.compile(r'【(?:核心口播|口播约|转场|讲述提示|讲解提示|补充讲解|可能追问|论文定位来源|来源尾注)[^】]*】|(?m:^\s*(?:时长|讲述提示|讲解提示|可能追问|出处与口径)\s*[:：])')


def relation_map(z, part):
    p = posixpath.join(posixpath.dirname(part), '_rels', posixpath.basename(part) + '.rels')
    if p not in z.namelist():
        return {}
    out = {}
    for r in ET.fromstring(z.read(p)):
        if r.get('TargetMode') == 'External':
            continue
        target = r.get('Target', '')
        resolved = target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(part), target))
        out[r.get('Id')] = (r.get('Type', '').rsplit('/', 1)[-1], resolved)
    return out


def slide_order(z):
    p = 'ppt/presentation.xml'
    rels = relation_map(z, p)
    slides = ET.fromstring(z.read(p)).find('p:sldIdLst', NS)
    if slides is None:
        return []
    return [rels[s.get('{' + NS['r'] + '}id')][1] for s in slides]


def speaker_text(z, slide):
    targets = [target for kind, target in relation_map(z, slide).values() if kind == 'notesSlide']
    if len(targets) != 1:
        return '', f'expected 1 notes relation, found {len(targets)}'
    if targets[0] not in z.namelist():
        return '', 'notes relation target is missing'
    root = ET.fromstring(z.read(targets[0]))
    paragraphs = []
    for shape in root.findall('.//p:sp', NS):
        ph = shape.find('p:nvSpPr/p:nvPr/p:ph', NS)
        if ph is not None and ph.get('type') != 'body':
            continue
        for p in shape.findall('p:txBody/a:p', NS):
            paragraphs.append(''.join(t.text or '' for t in p.findall('.//a:t', NS)))
    return '\n\n'.join(paragraphs).strip(), None


def normalized(s):
    # Ignore line wrapping and paragraph whitespace, preserve all nonspace characters.
    return re.sub(r'\s+', '', s)


def read_script(path):
    text = path.read_text(encoding='utf-8')
    headings = list(re.finditer(r'^##\s+[^\n]+\n', text, re.M))
    return [text[m.end():headings[i+1].start() if i+1 < len(headings) else len(text)].strip() for i, m in enumerate(headings)]


def audit(path, expected=None, require_tables=False, require_diagrams=False):
    errors, warnings, rows = [], [], []
    with zipfile.ZipFile(path) as z:
        corrupt = z.testzip()
        if corrupt:
            raise ValueError(f'ZIP CRC failure: {corrupt}')
        parts = slide_order(z)
        if not parts:
            errors.append('No slides in presentation order')
        if expected is not None and len(expected) != len(parts):
            errors.append(f'Expected script has {len(expected)} pages, PPTX has {len(parts)}')
        for i, part in enumerate(parts, 1):
            root = ET.fromstring(z.read(part))
            notes, problem = speaker_text(z, part)
            texts = [t.text or '' for t in root.findall('.//a:t', NS)]
            row = {
                'slide': i, 'part': part, 'notes_chars': len(notes),
                'native_tables': len(root.findall('.//a:tbl', NS)),
                'native_connectors': len(root.findall('.//p:cxnSp', NS)),
                'native_shapes': len(root.findall('.//p:sp', NS)),
                'pictures': len(root.findall('.//p:pic', NS)),
            }
            if problem:
                errors.append(f'Slide {i}: {problem}')
            if not notes.strip():
                errors.append(f'Slide {i}: empty speaker notes')
            elif len(normalized(notes)) < 60:
                warnings.append(f'Slide {i}: short notes; manually check if sufficient for this page')
            if PROMPT_LABEL.search(notes):
                errors.append(f'Slide {i}: presenter labels/instructions remain in speaker notes')
            if re.search(r'https?://', notes):
                warnings.append(f'Slide {i}: URL in spoken notes; move source reference to footer/appendix if not intended speech')
            if any(re.search(r'\b(?:TODO|TBD|PLACEHOLDER)\b|这里放一张图|此处插入', t, re.I) for t in texts):
                warnings.append(f'Slide {i}: possible placeholder text; inspect context')
            if expected is not None and i <= len(expected):
                row['script_matches_ignoring_whitespace'] = normalized(notes) == normalized(expected[i-1])
                if not row['script_matches_ignoring_whitespace']:
                    errors.append(f'Slide {i}: notes do not match the corresponding script page')
            rows.append(row)
    tables = sum(r['native_tables'] for r in rows)
    connectors = sum(r['native_connectors'] for r in rows)
    if require_tables and not tables:
        errors.append('No native table objects found')
    if require_diagrams and not connectors:
        errors.append('No native connector objects found; inspect whether required flows are flattened')
    return {
        'file': str(path.resolve()), 'scope': 'Structural checks only; scientific and visual review are required separately.',
        'structural_pass': not errors, 'slide_count': len(rows), 'native_tables': tables,
        'native_connectors': connectors, 'errors': errors, 'warnings': warnings, 'slides': rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pptx', type=Path)
    check = parser.add_mutually_exclusive_group()
    check.add_argument('--script', type=Path, help='Markdown with one level-2 heading per slide, followed only by spoken text')
    check.add_argument('--expected-notes', type=Path, help='JSON array of strings in slide order')
    parser.add_argument('--out', type=Path)
    parser.add_argument('--require-native-tables', action='store_true')
    parser.add_argument('--require-native-diagrams', action='store_true')
    args = parser.parse_args()
    try:
        expected = None
        if args.expected_notes:
            expected = json.loads(args.expected_notes.read_text(encoding='utf-8'))
            if not isinstance(expected, list) or not all(isinstance(s, str) for s in expected):
                raise ValueError('--expected-notes must be a JSON array of strings')
        elif args.script:
            expected = read_script(args.script)
            if not expected:
                raise ValueError('No level-2 slide headings in script')
        report = audit(args.pptx, expected, args.require_native_tables, args.require_native_diagrams)
    except (OSError, ValueError, KeyError, ET.ParseError, zipfile.BadZipFile) as error:
        report = {'structural_pass': False, 'errors': [str(error)], 'warnings': []}
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output + '\n', encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items() if k != 'slides'}, ensure_ascii=False))
    else:
        print(output)
    return 0 if report['structural_pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
