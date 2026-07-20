import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_pr_governance as mod


def body(task_id: str = "3DP-027", issue: int = 27, supersedes: str = "none") -> str:
    return (
        "## Task\n\n"
        f"- TASK_ID: {task_id}\n"
        f"- Canonical Issue: #{issue}\n"
        f"- Supersedes: {supersedes}\n"
    )


def record(number: int, task_id: str, state: str = "open", supersedes: str = "none") -> mod.PullRequestRecord:
    issue = int(task_id.split("-")[1])
    return mod.PullRequestRecord(
        number=number,
        title=f"🔗 3DP#{issue} → PR#{number}",
        body=body(task_id, issue, supersedes),
        state=state,
    )


class PullRequestGovernanceTests(unittest.TestCase):
    def test_valid_single_pr_passes(self):
        current = record(28, "3DP-027")
        self.assertEqual(mod.validate_records(current, [current], {}), [])

    def test_missing_task_metadata_fails(self):
        current = mod.PullRequestRecord(28, "PR without task", "- Supersedes: none\n", "open")
        errors = mod.validate_records(current, [current], {})
        self.assertIn("PR body lacks exact TASK_ID metadata", errors)
        self.assertIn("PR body lacks canonical Issue metadata", errors)

    def test_task_and_issue_mismatch_fails(self):
        current = mod.PullRequestRecord(
            28,
            "🔗 3DP#27 → PR#28",
            body("3DP-027", 8),
            "open",
        )
        self.assertIn("TASK_ID and canonical Issue number differ", mod.validate_records(current, [current], {}))

    def test_parallel_active_pr_for_same_task_fails(self):
        current = record(28, "3DP-027")
        duplicate = record(29, "3DP-027")
        errors = mod.validate_records(current, [current, duplicate], {})
        self.assertIn("parallel active implementation PRs for 3DP-027: #29", errors)

    def test_different_task_pr_does_not_conflict(self):
        current = record(28, "3DP-027")
        other = record(29, "3DP-008")
        self.assertEqual(mod.validate_records(current, [current, other], {}), [])

    def test_superseded_relation_requires_closed_pr(self):
        current = record(28, "3DP-027", supersedes="PR #20 (closed)")
        open_old = record(20, "3DP-018", state="open")
        errors = mod.validate_records(current, [current, open_old], {20: open_old})
        self.assertIn("superseded PR #20 is not closed", errors)

    def test_closed_superseded_relation_passes(self):
        current = record(28, "3DP-027", supersedes="PR #20 (closed), PR #21 (closed)")
        old_20 = record(20, "3DP-018", state="closed")
        old_21 = record(21, "3DP-017", state="closed")
        self.assertEqual(
            mod.validate_records(current, [current], {20: old_20, 21: old_21}),
            [],
        )

    def test_noncanonical_supersedes_metadata_fails(self):
        current = record(28, "3DP-027", supersedes="#20")
        self.assertIn(
            "Supersedes must be none or use PR #N (closed)",
            mod.validate_records(current, [current], {}),
        )

    def test_pr_cannot_supersede_itself(self):
        current = record(28, "3DP-027", supersedes="PR #28 (closed)")
        self.assertIn("PR cannot supersede itself", mod.validate_records(current, [current], {28: current}))


if __name__ == "__main__":
    unittest.main()
