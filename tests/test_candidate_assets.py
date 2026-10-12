"""Preservation checks for the original bank, baseline and all original assets."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('package_candidate', ROOT / 'tools/package_candidate.py')
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)


class CandidatePreservationTests(unittest.TestCase):
    def test_original_source_and_consolidated_baseline_are_unchanged(self):
        expected = {
            'B1_10_ORIGINAL_FLOOT.html': '1ce6484c1e50355e4f33e4eba28eabff305ce31831272f3e13135ecb4943e6ba',
            'B1_11_CONSOLIDADA.html': '736a580452da46313d09aae29e5394b7632ccdba4e17e462ad97f59a89b9b1c4',
        }
        for name, digest in expected.items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((ROOT / 'game' / name).read_bytes()).hexdigest(), digest)

    def test_all_original_data_and_recording_maps_are_preserved(self):
        baseline = (ROOT / 'game/B1_11_CONSOLIDADA.html').read_text()
        candidate = (ROOT / 'game/index.html').read_text()
        # Covers all original bank/reserve definitions, aliases, text-only rows,
        # historical pool, exact phrases, audio mappings and the whitelist.
        for start, end in [('  const BANK={', '  const $='), ('  const STATIC_AUDIO=', '  const ACTIVE_QUESTION_POOL=')]:
            self.assertEqual(baseline[baseline.index(start):baseline.index(end)],
                             candidate[candidate.index(start):candidate.index(end)])

    def test_package_preserves_every_resource_byte_and_root_audio_paths(self):
        assets = packager.verified_assets()
        self.assertEqual(len([p for p in assets if p.endswith('.mp3')]), 188)
        self.assertIn('new-audio/v33_name_facu.mp3', assets)
        self.assertIn('new-audio/v33w_072.mp3', assets)
        with tempfile.TemporaryDirectory() as directory:
            output = packager.package(Path(directory) / 'candidate.zip')
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(archive.read('index.html'), (ROOT / 'game/index.html').read_bytes())
                for name in assets:
                    with self.subTest(name=name):
                        self.assertEqual(archive.read(name), (ROOT / 'game' / name).read_bytes())
