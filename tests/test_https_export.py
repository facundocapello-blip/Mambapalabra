import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('https_export', ROOT / 'tools/export_https_candidate.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


class HTTPSExportTests(unittest.TestCase):
    def test_offline_export_keeps_all_assets_and_has_no_production_backend(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'site'
            metadata = exporter.export(output, '/candidata/')
            html = (output / 'index.html').read_text()
            self.assertEqual(metadata['mp3'], 188)
            self.assertNotIn(exporter.PRODUCTION_PROJECT, html)
            self.assertIn('/candidata/new-audio/unlock.mp3', html)
            self.assertIn('id="createOnlineBtn" type="button" disabled', html)
            self.assertNotIn('cdn.jsdelivr.net', html)
            assets = json.loads((output / 'ASSETS_SHA256.json').read_text())
            for name in assets:
                self.assertEqual((output / name).read_bytes(), (ROOT / 'game' / name).read_bytes())

    def test_production_and_private_credentials_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                exporter.export(Path(directory) / 'site', '/candidata/',
                                f'https://{exporter.PRODUCTION_PROJECT}.supabase.co', 'sb_publishable_example')
            with self.assertRaises(ValueError):
                exporter.export(Path(directory) / 'site', '/candidata/',
                                'https://abcdefghijklmnopqrst.supabase.co', 'sb_secret_example')

    def test_existing_export_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            exporter.export(directory, '/candidata/')
            with self.assertRaises(ValueError):
                exporter.export(directory, '/candidata/')
