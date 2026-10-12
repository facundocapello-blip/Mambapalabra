"""Pruebas de ensamblado B1.11; no dependen de infraestructura online."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/"tools"/"build_b111.py"
spec=importlib.util.spec_from_file_location("build_b111",SCRIPT)
builder=importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class B111AssemblerTests(unittest.TestCase):
    def setUp(self):
        self.base=("B1.10-CANDIDATA-TV\n"
                   + "  async function hostSpeak(text,opts={}){\n"
                   + builder.OLD_NO_MP3+"\n"+builder.OLD_MP3_ERROR+"\n"
                   + '  async function primeAV(){')

    def test_consolida_cinco_modificaciones(self):
        compiled=builder.consolidate(self.base)
        for marker in ["B1.11-VOZ-COMPLETA","function deviceSpeak(",
                       "if(!paths.length)return deviceSpeak(text,opts,seq);",
                       "if(result.status===SPEECH_RESULT.FAILED)return deviceSpeak(text,opts,seq);"]:
            self.assertIn(marker,compiled)

    def test_ancla_faltante_falla_sin_producir_codigo(self):
        with self.assertRaises(RuntimeError):
            builder.consolidate(self.base.replace("B1.10-CANDIDATA-TV","OTRO"))

    def test_ancla_duplicada_falla(self):
        with self.assertRaises(RuntimeError):
            builder.consolidate(self.base+builder.OLD_NO_MP3)

    def test_fuente_con_sha_fijo(self):
        source=Path("game/B1_10_ORIGINAL_FLOOT.html")
        if not source.exists(): self.skipTest("Ejecutar primero tools/recuperar_fuente.py")
        from hashlib import sha256
        self.assertEqual(sha256(source.read_bytes()).hexdigest(),builder.EXPECTED_HTML_SHA256)

    def test_b111_compilada_identica(self):
        source=Path("game/B1_10_ORIGINAL_FLOOT.html")
        assembled=Path("game/B1_11_CONSOLIDADA.html")
        if not source.exists() or not assembled.exists():self.skipTest("Ejecutar importador y constructor")
        self.assertEqual(assembled.read_text(),builder.consolidate(source.read_text()))

if __name__=="__main__": unittest.main()
