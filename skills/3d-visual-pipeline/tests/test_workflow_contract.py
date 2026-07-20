import json
import re
import unittest
from pathlib import Path


class WorkflowContractTests(unittest.TestCase):
    NATIVE_CHECK = "Validate repository / validate"
    LEGACY_CUSTOM_STATUS = "3dp/validation"

    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[3]
        cls.workflow = (root / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        cls.manifest = json.loads(
            (root / "release/1.0.0/validation-manifest.json").read_text(encoding="utf-8")
        )
        cls.debt = (root / "docs/debt/3dp-018.md").read_text(encoding="utf-8")

    def test_trigger_matrix_has_no_task_branch_push_overlap(self):
        self.assertRegex(
            self.workflow,
            r"(?ms)^  push:\n    branches: \[main\]\n"
            r"  pull_request:\n"
            r"    types: \[opened, synchronize, reopened, ready_for_review\]\n"
            r"  workflow_dispatch:",
        )
        for branch_pattern in ("feat/**", "fix/**", "release/**", "chore/**"):
            self.assertNotIn(branch_pattern, self.workflow)

    def test_workflow_keeps_one_read_only_job(self):
        jobs_block = self.workflow.split("\njobs:\n", 1)[1]
        job_keys = re.findall(r"(?m)^  ([a-zA-Z0-9_-]+):\n    runs-on:", jobs_block)
        self.assertEqual(job_keys, ["validate"])
        self.assertIn("permissions:\n  contents: read\n  issues: read\n  pull-requests: read\n", self.workflow)
        self.assertNotIn("statuses: write", self.workflow)
        self.assertNotIn("contents: write", self.workflow)
        self.assertNotIn("issues: write", self.workflow)
        self.assertNotIn("pull-requests: write", self.workflow)

    def test_checkout_and_concurrency_are_event_safe(self):
        self.assertIn("cancel-in-progress: true", self.workflow)
        self.assertIn("ref: ${{ github.event.pull_request.head.sha || github.sha }}", self.workflow)
        self.assertIn("persist-credentials: false", self.workflow)

    def test_native_job_check_replaces_custom_status(self):
        self.assertRegex(self.workflow, r"(?m)^name: Validate repository$")
        self.assertNotIn("context=3dp/validation", self.workflow)
        self.assertNotIn("Publish success status", self.workflow)
        self.assertNotIn("Publish failure status", self.workflow)
        self.assertNotIn("gh api --method POST", self.workflow)

    def test_release_manifest_matches_native_workflow_check(self):
        self.assertEqual(self.manifest.get("validation_check"), self.NATIVE_CHECK)
        self.assertNotIn("validation_context", self.manifest)
        self.assertNotIn(self.LEGACY_CUSTOM_STATUS, json.dumps(self.manifest, sort_keys=True))

    def test_legacy_custom_status_is_explicitly_historical(self):
        self.assertIn(
            "`3dp/validation` was the custom commit-status context for the 3DP-018 baseline.",
            self.debt,
        )
        self.assertIn(
            "The current canonical CI identity is the native GitHub Actions check "
            "`Validate repository / validate`; the custom status is no longer published.",
            self.debt,
        )

    def test_artifacts_are_failure_or_requested_manual_only(self):
        self.assertIn("default: false", self.workflow)
        self.assertIn(
            "if: failure() || (github.event_name == 'workflow_dispatch' && inputs.upload_evidence)",
            self.workflow,
        )
        upload_step = self.workflow.split("- name: Upload validation evidence", 1)[1]
        self.assertNotIn("if: always()", upload_step)
        self.assertIn("if-no-files-found: warn", upload_step)


if __name__ == "__main__":
    unittest.main()
