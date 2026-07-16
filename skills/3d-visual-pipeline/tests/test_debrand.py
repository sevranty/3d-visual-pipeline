import sys, tempfile, unittest
from pathlib import Path
SCRIPTS=Path(__file__).resolve().parents[1]/"scripts"
sys.path.insert(0,str(SCRIPTS))
import validate_debrand as mod
class DebrandTests(unittest.TestCase):
    def test_generic_text_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/"README.md").write_text("generic three-dimensional pipeline")
            self.assertEqual(mod.scan(root),[])
    def test_legacy_text_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); token="".join(["fin","us","lugi"]); (root/"README.md").write_text(token)
            self.assertTrue(mod.scan(root))

    def test_active_short_id_text_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); token="".join(["D","V","P"]); (root/"README.md").write_text(token)
            self.assertTrue(mod.scan(root))
    def test_historical_allowlisted_short_ids_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); path=root/"release"/"1.0.0"; path.mkdir(parents=True)
            (path/"notes.md").write_text("Historical evidence mentions "+"".join(["D","V","P"])+" and "+"".join(["F","3","D"])+" only as closed-era identifiers.")
            self.assertEqual(mod.scan(root),[])
    def test_allowlist_rejects_extra_active_short_id_text(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); path=root/"release"/"1.0.0"; path.mkdir(parents=True)
            (path/"notes.md").write_text("Historical evidence mentions "+"".join(["D","V","P"])+" and "+"".join(["F","3","D"])+" only as closed-era identifiers.\nActive context "+"".join(["D","V","P"]))
            self.assertTrue(mod.scan(root))
    def test_non_allowlisted_historical_text_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); path=root/"release"/"1.0.1"; path.mkdir(parents=True)
            (path/"notes.md").write_text("".join(["D","V","P"]))
            self.assertTrue(mod.scan(root))
    def test_legacy_filename_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); token="".join(["f","3","d"]); (root/(token+".md")).write_text("x")
            self.assertTrue(mod.scan(root))
    def test_legacy_url_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); token="".join(["fin","us","lugi"]); (root/"a.md").write_text("https://example.test/"+token)
            self.assertTrue(mod.scan(root))
    def test_legacy_color_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); color="#"+"".join(["ff","05","08"]); (root/"a.md").write_text(color)
            self.assertTrue(mod.scan(root))
if __name__=="__main__": unittest.main()
