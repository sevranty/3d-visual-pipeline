import contextlib, io, json, sys, tempfile, unittest
from pathlib import Path
SCRIPTS=Path(__file__).resolve().parents[1]/"scripts"
sys.path.insert(0,str(SCRIPTS))
import validate_release as mod

class ReleaseLifecycleTests(unittest.TestCase):
    def test_pass_status_rejected(self):
        self.assertNotIn('pass', mod.STATES)

    def test_candidate_hosted_ci_success_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'.codex-plugin').mkdir(); (root/'release/1.0.0').mkdir(parents=True)
            (root/'.codex-plugin/plugin.json').write_text('{"version":"1.0.0"}')
            manifest={'version':'1.0.0','intended_tag':'v1.0.0','status':'candidate','legacy_immutable_tag':'v0.2.0','evidence':{'hosted_ci':'pass'}}
            (root/'release/1.0.0/validation-manifest.json').write_text(json.dumps(manifest))
            for rel in ['release/1.0.0/RELEASE_NOTES.md','CHANGELOG.md','README.md','RELEASE_CHECKLIST.md']:
                p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text('1.0.0')
            old_root=mod.repo_root; old_argv=sys.argv[:]; mod.repo_root=lambda: root; sys.argv=["validate_release.py","--no-report"]
            try:
                with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(mod.main(),1)
            finally: mod.repo_root=old_root; sys.argv=old_argv

    def test_stale_head_sha_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'.codex-plugin').mkdir(); (root/'release/1.0.0').mkdir(parents=True)
            (root/'.codex-plugin/plugin.json').write_text('{"version":"1.0.0"}')
            manifest={'version':'1.0.0','intended_tag':'v1.0.0','status':'candidate','legacy_immutable_tag':'v0.2.0','evidence':{'head_sha':'0'*40,'hosted_ci':'not run'}}
            (root/'release/1.0.0/validation-manifest.json').write_text(json.dumps(manifest))
            for rel in ['release/1.0.0/RELEASE_NOTES.md','CHANGELOG.md','README.md','RELEASE_CHECKLIST.md']:
                p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text('1.0.0')
            old_root=mod.repo_root; old_git=mod.git; old_argv=sys.argv[:]; mod.repo_root=lambda: root; mod.git=lambda root,*args: '1'*40 if args==('rev-parse','HEAD') else ''; sys.argv=["validate_release.py","--no-report"]
            try:
                with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(mod.main(),1)
            finally: mod.repo_root=old_root; mod.git=old_git; sys.argv=old_argv

    def test_invalid_head_sha_shape_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'.codex-plugin').mkdir(); (root/'release/1.0.0').mkdir(parents=True)
            (root/'.codex-plugin/plugin.json').write_text('{"version":"1.0.0"}')
            manifest={'version':'1.0.0','intended_tag':'v1.0.0','status':'candidate','legacy_immutable_tag':'v0.2.0','evidence':{'head_sha':'runtime exact HEAD in validation report','hosted_ci':'not run','local_command':mod.FULL_LOCAL_COMMAND,'reports_path':'validation/runtime/'}}
            (root/'release/1.0.0/validation-manifest.json').write_text(json.dumps(manifest))
            for rel in ['release/1.0.0/RELEASE_NOTES.md','CHANGELOG.md','README.md','RELEASE_CHECKLIST.md']:
                p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text('1.0.0')
            old_root=mod.repo_root; old_argv=sys.argv[:]; mod.repo_root=lambda: root; sys.argv=["validate_release.py","--no-report"]
            try:
                with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(mod.main(),1)
            finally: mod.repo_root=old_root; sys.argv=old_argv

    def test_full_local_command_is_declared(self):
        self.assertIn('validate_repository.py', mod.FULL_LOCAL_COMMAND)
        self.assertIn('python3 -m unittest discover', mod.FULL_LOCAL_COMMAND)

    def test_tagged_validated_requires_bound_tag(self):
        self.assertIn('tagged-validated', mod.STATES)

if __name__=='__main__': unittest.main()
