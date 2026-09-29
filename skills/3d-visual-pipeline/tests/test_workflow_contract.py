import json
import re
import unittest
from pathlib import Path


class WorkflowContractTests(unittest.TestCase):
    HISTORICAL_NATIVE_CHECK = "Validate repository / validate"
    LEGACY_CUSTOM_STATUS = "3dp/validation"
    RELEASE_URL = "https://github.com/sevranty/3d-visual-pipeline/releases/tag/v1.0.0"

    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[3]
        cls.github_workflow = (root / ".github/workflows/validate.yml").read_text(
            encoding="utf-8"
        )
        cls.woodpecker = (root / ".woodpecker/validate.yml").read_text(
            encoding="utf-8"
        )
        cls.manifest = json.loads(
            (root / "release/1.0.0/validation-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        cls.debt = (root / "docs/debt/3dp-018.md").read_text(encoding="utf-8")

    @staticmethod
    def _github_on_block(text: str) -> str:
        lines = text.splitlines()
        start = next(i for i, line in enumerate(lines) if line == "on:")
        result = []
        for line in lines[start + 1 :]:
            if line and not line.startswith((" ", "\t")):
                break
            result.append(line)
        return "\n".join(result)

    def test_github_actions_is_manual_only_fallback(self):
        on_block = self._github_on_block(self.github_workflow)
        self.assertIn("workflow_dispatch:", on_block)
        self.assertNotRegex(on_block, r"(?m)^\s+pull_request\s*:")
        self.assertNotRegex(on_block, r"(?m)^\s+push\s*:")
        self.assertNotRegex(on_block, r"(?m)^\s+schedule\s*:")
        self.assertRegex(
            self.github_workflow,
            r"(?m)^name: Validate repository \(manual fallback\)$",
        )

    def test_woodpecker_owns_automatic_validation(self):
        self.assertIn("- event: pull_request", self.woodpecker)
        self.assertIn("- event: push", self.woodpecker)
        self.assertIn("branch: ${CI_REPO_DEFAULT_BRANCH}", self.woodpecker)
        self.assertIn(
            "python3 skills/3d-visual-pipeline/scripts/validate_all.py",
            self.woodpecker,
        )
        self.assertIn(
            "validate_pr_governance_woodpecker.py",
            self.woodpecker,
        )
        self.assertIn("git diff --check", self.woodpecker)
        self.assertIn("concurrency: 1", self.woodpecker)

    def test_manual_fallback_keeps_one_read_only_job(self):
        jobs_block = self.github_workflow.split("\njobs:\n", 1)[1]
        job_keys = re.findall(
            r"(?m)^  ([a-zA-Z0-9_-]+):\n    runs-on:", jobs_block
        )
        self.assertEqual(job_keys, ["validate"])
        self.assertIn(
            "permissions:\n  contents: read\n  issues: read\n  pull-requests: read\n",
            self.github_workflow,
        )
        for forbidden in (
            "statuses: write",
            "contents: write",
            "issues: write",
            "pull-requests: write",
        ):
            self.assertNotIn(forbidden, self.github_workflow)

    def test_manual_fallback_checkout_is_read_only(self):
        self.assertIn("cancel-in-progress: true", self.github_workflow)
        self.assertIn("ref: ${{ github.sha }}", self.github_workflow)
        self.assertIn("persist-credentials: false", self.github_workflow)
        self.assertNotIn("Publish success status", self.github_workflow)
        self.assertNotIn("Publish failure status", self.github_workflow)
        self.assertNotIn("gh api --method POST", self.github_workflow)

    def test_release_manifest_preserves_historical_validation_evidence(self):
        self.assertEqual(
            self.manifest.get("validation_check"), self.HISTORICAL_NATIVE_CHECK
        )
        self.assertNotIn("validation_context", self.manifest)
        self.assertNotIn(
            self.LEGACY_CUSTOM_STATUS, json.dumps(self.manifest, sort_keys=True)
        )

    def test_release_state_matches_publication_evidence(self):
        state = self.manifest.get("status")
        self.assertIn(state, {"candidate", "tagged-validated", "published"})

        tag_target = self.manifest.get("tag_target")
        tagged_validation = self.manifest.get("tagged_validation")
        release_url = self.manifest.get("release_url")
        github_release = self.manifest.get("github_release")

        if state == "candidate":
            self.assertIsNone(tag_target)
            self.assertIsNone(tagged_validation)
            self.assertIsNone(release_url)
            self.assertIsNone(github_release)
            return

        self.assertRegex(str(tag_target or ""), r"^[0-9a-f]{40}$")
        self.assertIsInstance(tagged_validation, dict)
        self.assertEqual(tagged_validation.get("status"), "pass")
        self.assertEqual(tagged_validation.get("checkout_sha"), tag_target)
        self.assertEqual(tagged_validation.get("peeled_commit"), tag_target)

        if state == "tagged-validated":
            self.assertIsNone(release_url)
            self.assertIsNone(github_release)
            return

        self.assertEqual(release_url, self.RELEASE_URL)
        self.assertIsInstance(github_release, dict)
        self.assertEqual(github_release.get("url"), self.RELEASE_URL)
        self.assertIs(github_release.get("draft"), False)
        self.assertIs(github_release.get("prerelease"), False)

    def test_ci_identity_history_and_current_owner_are_explicit(self):
        self.assertIn(
            "`3dp/validation` was the custom commit-status context for the 3DP-018 baseline.",
            self.debt,
        )
        self.assertIn(
            "Woodpecker is the current primary automatic validation contour",
            self.debt,
        )
        self.assertIn(
            "GitHub Actions remains manual-only fallback",
            self.debt,
        )

    def test_manual_artifacts_are_failure_or_requested_only(self):
        self.assertIn("default: false", self.github_workflow)
        self.assertIn(
            "if: failure() || inputs.upload_evidence",
            self.github_workflow,
        )
        upload_step = self.github_workflow.split(
            "- name: Upload validation evidence", 1
        )[1]
        self.assertNotIn("if: always()", upload_step)
        self.assertIn("if-no-files-found: warn", upload_step)


if __name__ == "__main__":
    unittest.main()
