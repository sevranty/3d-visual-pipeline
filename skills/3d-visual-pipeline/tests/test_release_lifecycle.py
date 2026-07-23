import sys
import unittest
from copy import deepcopy
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import validate_release as mod


def candidate_manifest():
    return {
        "version": "1.0.0",
        "intended_tag": "v1.0.0",
        "status": "candidate",
        "hosted_ci": {"status": "not_run", "run_url": None, "commit_sha": None},
        "tag_target": None,
        "tagged_validation": None,
        "release_url": None,
        "github_release": None,
        "legacy_release": {
            "tag": "v0.2.0",
            "target": "3d2cdea9f651f7641ec1f805519a777f013dd6ec",
            "immutable": True,
        },
    }


def tagged_evidence(target: str):
    return {
        "status": "pass",
        "tag": "v1.0.0",
        "tag_object_type": "tag",
        "tag_object_sha": "3" * 40,
        "checkout_sha": target,
        "peeled_commit": target,
        "command": "python3 skills/3d-visual-pipeline/scripts/validate_all.py --report-dir validation/runtime",
        "report": "validation/runtime/summary.json",
        "validated_at": "2026-07-20T12:00:00+00:00",
    }


def published_manifest():
    manifest = candidate_manifest()
    target = "1" * 40
    url = "https://github.com/sevranty/3d-visual-pipeline/releases/tag/v1.0.0"
    manifest.update(
        {
            "status": "published",
            "tag_target": target,
            "tagged_validation": tagged_evidence(target),
            "release_url": url,
            "github_release": {
                "url": url,
                "tag": "v1.0.0",
                "draft": False,
                "prerelease": False,
                "published_at": "2026-07-20T12:30:00Z",
            },
        }
    )
    return manifest


def fake_git(values):
    def reader(root: Path, args: tuple[str, ...]):
        del root
        return values.get(args, (None, f"missing command: {' '.join(args)}"))

    return reader


class ReleaseLifecycleTests(unittest.TestCase):
    def test_candidate_passes(self):
        self.assertEqual(mod.validate_manifest(candidate_manifest()), [])

    def test_pr25_legacy_pass_state_rejected(self):
        manifest = candidate_manifest()
        manifest["status"] = "pass"
        self.assertIn("release status invalid", mod.validate_manifest(manifest))

    def test_candidate_publication_evidence_rejected(self):
        manifest = candidate_manifest()
        manifest["tag_target"] = "1" * 40
        self.assertIn("candidate contains publication evidence", mod.validate_manifest(manifest))

    def test_hosted_not_run_rejects_claimed_run(self):
        manifest = candidate_manifest()
        manifest["hosted_ci"] = {
            "status": "not_run",
            "run_url": "https://github.com/sevranty/3d-visual-pipeline/actions/runs/1",
            "commit_sha": "1" * 40,
        }
        self.assertIn("hosted CI not_run contains run evidence", mod.validate_manifest(manifest))

    def test_hosted_result_requires_url_and_commit(self):
        manifest = candidate_manifest()
        manifest["hosted_ci"] = {"status": "passed", "run_url": None, "commit_sha": None}
        errors = mod.validate_manifest(manifest)
        self.assertIn("hosted CI result lacks canonical run URL", errors)
        self.assertIn("hosted CI result lacks exact commit", errors)

    def test_hosted_result_rejects_other_repository_url(self):
        manifest = candidate_manifest()
        manifest["hosted_ci"] = {
            "status": "passed",
            "run_url": "https://github.com/other/repository/actions/runs/1",
            "commit_sha": "1" * 40,
        }
        self.assertIn("hosted CI result lacks canonical run URL", mod.validate_manifest(manifest))

    def test_tagged_validation_must_bind_to_target(self):
        manifest = candidate_manifest()
        manifest["status"] = "tagged-validated"
        manifest["tag_target"] = "1" * 40
        manifest["tagged_validation"] = tagged_evidence("2" * 40)
        errors = mod.validate_manifest(manifest)
        self.assertIn("tagged validation is not bound to tag target", errors)
        self.assertIn("tagged validation peeled commit differs from tag target", errors)

    def test_tagged_validation_requires_annotated_tag(self):
        manifest = candidate_manifest()
        target = "1" * 40
        evidence = tagged_evidence(target)
        evidence["tag_object_type"] = "commit"
        manifest.update(
            {
                "status": "tagged-validated",
                "tag_target": target,
                "tagged_validation": evidence,
            }
        )
        self.assertIn("tagged validation lacks annotated tag object", mod.validate_manifest(manifest))

    def test_tagged_validation_requires_tag_object_sha(self):
        manifest = candidate_manifest()
        target = "1" * 40
        evidence = tagged_evidence(target)
        evidence["tag_object_sha"] = None
        manifest.update(
            {
                "status": "tagged-validated",
                "tag_target": target,
                "tagged_validation": evidence,
            }
        )
        self.assertIn("tagged validation lacks tag object SHA", mod.validate_manifest(manifest))

    def test_tagged_validation_requires_command_report_and_timestamp(self):
        manifest = candidate_manifest()
        target = "1" * 40
        evidence = tagged_evidence(target)
        evidence["command"] = ""
        evidence["report"] = None
        evidence["validated_at"] = "today"
        manifest.update(
            {
                "status": "tagged-validated",
                "tag_target": target,
                "tagged_validation": evidence,
            }
        )
        errors = mod.validate_manifest(manifest)
        self.assertIn("tagged validation command missing", errors)
        self.assertIn("tagged validation report missing", errors)
        self.assertIn("tagged validation timestamp invalid", errors)

    def test_candidate_skips_git_tag_validation(self):
        def unexpected_reader(root: Path, args: tuple[str, ...]):
            raise AssertionError(f"unexpected Git read: {root} {args}")

        self.assertEqual(mod.validate_git_tag(Path("."), candidate_manifest(), unexpected_reader), [])

    def test_actual_annotated_tag_matches_recorded_evidence(self):
        manifest = published_manifest()
        target = manifest["tag_target"]
        reader = fake_git(
            {
                ("cat-file", "-t", "refs/tags/v1.0.0"): ("tag", None),
                ("rev-parse", "refs/tags/v1.0.0"): ("3" * 40, None),
                ("rev-parse", "refs/tags/v1.0.0^{}"): (target, None),
            }
        )
        self.assertEqual(mod.validate_git_tag(Path("."), manifest, reader), [])

    def test_missing_actual_tag_fails_closed(self):
        manifest = published_manifest()
        reader = fake_git(
            {
                ("cat-file", "-t", "refs/tags/v1.0.0"): (None, "fatal: Not a valid object name v1.0.0"),
            }
        )
        errors = mod.validate_git_tag(Path("."), manifest, reader)
        self.assertTrue(errors[0].startswith("Git release tag v1.0.0 could not be resolved:"))

    def test_actual_lightweight_tag_is_rejected(self):
        manifest = published_manifest()
        target = manifest["tag_target"]
        reader = fake_git(
            {
                ("cat-file", "-t", "refs/tags/v1.0.0"): ("commit", None),
                ("rev-parse", "refs/tags/v1.0.0"): (target, None),
                ("rev-parse", "refs/tags/v1.0.0^{}"): (target, None),
            }
        )
        errors = mod.validate_git_tag(Path("."), manifest, reader)
        self.assertIn("Git release tag v1.0.0 is not annotated", errors)
        self.assertIn("Git tag object SHA differs from recorded evidence", errors)

    def test_actual_tag_object_sha_mismatch_is_rejected(self):
        manifest = published_manifest()
        target = manifest["tag_target"]
        reader = fake_git(
            {
                ("cat-file", "-t", "refs/tags/v1.0.0"): ("tag", None),
                ("rev-parse", "refs/tags/v1.0.0"): ("4" * 40, None),
                ("rev-parse", "refs/tags/v1.0.0^{}"): (target, None),
            }
        )
        self.assertIn(
            "Git tag object SHA differs from recorded evidence",
            mod.validate_git_tag(Path("."), manifest, reader),
        )

    def test_actual_peeled_target_mismatch_is_rejected(self):
        manifest = published_manifest()
        reader = fake_git(
            {
                ("cat-file", "-t", "refs/tags/v1.0.0"): ("tag", None),
                ("rev-parse", "refs/tags/v1.0.0"): ("3" * 40, None),
                ("rev-parse", "refs/tags/v1.0.0^{}"): ("2" * 40, None),
            }
        )
        errors = mod.validate_git_tag(Path("."), manifest, reader)
        self.assertIn("Git peeled release commit differs from tag target", errors)
        self.assertIn("Git peeled release commit differs from recorded evidence", errors)

    def test_published_manifest_passes(self):
        self.assertEqual(mod.validate_manifest(published_manifest()), [])

    def test_published_requires_canonical_release_url(self):
        manifest = published_manifest()
        manifest["release_url"] = "https://example.test/release"
        self.assertIn("published state lacks canonical release URL", mod.validate_manifest(manifest))

    def test_published_requires_public_release_flags(self):
        manifest = published_manifest()
        manifest["github_release"]["draft"] = True
        manifest["github_release"]["prerelease"] = True
        errors = mod.validate_manifest(manifest)
        self.assertIn("GitHub Release must be non-draft", errors)
        self.assertIn("GitHub Release must be non-prerelease", errors)

    def test_legacy_boundary_is_immutable(self):
        manifest = deepcopy(candidate_manifest())
        manifest["legacy_release"]["immutable"] = False
        self.assertIn("legacy release must remain immutable", mod.validate_manifest(manifest))


if __name__ == "__main__":
    unittest.main()
