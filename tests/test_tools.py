import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/artifact-template-academic-paper-talk'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit = load('audit', SKILL / 'scripts/audit_pptx.py')
installer = load('installer', ROOT / 'scripts/install.py')


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.reference = SKILL / 'assets/reference.pptx'

    def test_reference_and_notes_roundtrip(self):
        with zipfile.ZipFile(self.reference) as z:
            notes = [audit.speaker_text(z, s)[0] for s in audit.slide_order(z)]
        report = audit.audit(self.reference, notes, True, True)
        self.assertTrue(report['structural_pass'], report['errors'])
        self.assertEqual(report['slide_count'], 17)
        with tempfile.TemporaryDirectory() as d:
            script = Path(d) / 'notes.md'
            script.write_text('\n\n'.join(f'## 第 {i} 页\n\n{n}' for i, n in enumerate(notes, 1)), encoding='utf-8')
            self.assertTrue(audit.audit(self.reference, audit.read_script(script))['structural_pass'])

    def test_mismatched_script(self):
        with zipfile.ZipFile(self.reference) as z:
            notes = [audit.speaker_text(z, s)[0] for s in audit.slide_order(z)]
        notes[2] += 'different narration'
        self.assertTrue(any('Slide 3: notes do not match' in e for e in audit.audit(self.reference, notes)['errors']))

    def test_missing_notes_and_presenter_label(self):
        with zipfile.ZipFile(self.reference) as z, tempfile.TemporaryDirectory() as d:
            part = audit.slide_order(z)[2]
            target = next(t for kind, t in audit.relation_map(z, part).values() if kind == 'notesSlide')
            missing = Path(d) / 'missing.pptx'
            with zipfile.ZipFile(missing, 'w') as out:
                for info in z.infolist():
                    if info.filename != target:
                        out.writestr(copy.copy(info), z.read(info.filename))
            self.assertTrue(any('target is missing' in e for e in audit.audit(missing)['errors']))
            notes = ET.fromstring(z.read(target))
            for shape in notes.findall('.//p:sp', audit.NS):
                ph = shape.find('p:nvSpPr/p:nvPr/p:ph', audit.NS)
                if ph is not None and ph.get('type') == 'body':
                    shape.find('.//a:t', audit.NS).text = '【核心口播】请停顿十秒'
            labeled = Path(d) / 'labeled.pptx'
            with zipfile.ZipFile(labeled, 'w') as out:
                for info in z.infolist():
                    out.writestr(copy.copy(info), ET.tostring(notes) if info.filename == target else z.read(info.filename))
            self.assertTrue(any('presenter labels' in e for e in audit.audit(labeled)['errors']))


class InstallTests(unittest.TestCase):
    def test_install_preserve_and_backup(self):
        with tempfile.TemporaryDirectory() as d:
            dest = Path(d) / 'skills'
            target, backup = installer.install(dest)
            self.assertIsNone(backup)
            self.assertTrue((target / 'SKILL.md').is_file())
            marker = target / 'personal.txt'
            marker.write_text('personal edit', encoding='utf-8')
            with self.assertRaises(FileExistsError):
                installer.install(dest)
            self.assertEqual(marker.read_text(), 'personal edit')
            target, backup = installer.install(dest, force=True)
            self.assertEqual((backup / 'personal.txt').read_text(), 'personal edit')
            self.assertFalse((target / 'personal.txt').exists())


if __name__ == '__main__':
    unittest.main()
