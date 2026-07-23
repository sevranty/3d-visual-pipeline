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


def issue_payload(number: int = 27, state: str = "open", task_id: str = "3DP-027"):
    return {
        "number": number,
        "state": state,
        "title": f"🔗 3DP#{number} → governance",
        "body": f"## TASK_CONTEXT\n\n```text\nTASK_ID: {task_id}\n```\n",
    }


class PullRequestGovernanceTests(unittest.TestCase):
    def test_valid_single_pr_passes(self):
        current = record(28, "3DP-027")
        self.assertEqual(mod.validate_records(current, [current], {}), [])

    def test_missing_task_metadata_fails(self):
        current = mod.PullRequestRecord(28, "PR without task", "- Supersedes: none\n", "open")
        errors = mod.validate_records(current, [current], {})
        self.assertIn("PR body lacks exact TASK_ID metadata", errors)
        self.assertIn("PR body lacks canonical Issue metadata", errors)
        self.assertIn("PR title lacks 3DP#N task number", errors)

    def test_task_and_issue_mismatch_fails(self):
        current = mod.PullRequestRecord(
            28,
            "🔗 3DP#27 → PR#28",
            body("3DP-027", 8),
            "open",
        )
        errors = mod.validate_records(current, [current], {})
        self.assertIn("TASK_ID and canonical Issue number differ", errors)
        self.assertIn("PR title task number differs from canonical Issue", errors)

    def test_title_and_task_id_mismatch_fails(self):
        current = mod.PullRequestRecord(
            28,
            "🔗 3DP#8 → PR#28",
            body("3DP-027", 27),
            "open",
        )
        errors = mod.validate_records(current, [current], {})
        self.assertIn("PR title task number differs from TASK_ID", errors)
        self.assertIn("PR title task number differs from canonical Issue", errors)

    def test_parallel_active_pr_for_same_task_fails(self):
        current = record(28, "3DP-027")
        duplicate = record(29, "3DP-027")
        errors = mod.validate_records(current, [current, duplicate], {})
        self.assertIn("parallel active implementation PRs for 3DP-027: #29", errors)

    def test_legacy_title_only_duplicate_is_detected(self):
        current = record(28, "3DP-027")
        duplicate = mod.PullRequestRecord(29, "🔗 3DP#27 → old PR", "", "open")
        errors = mod.validate_records(current, [current, duplicate], {})
        self.assertIn("parallel active implementation PRs for 3DP-027: #29", errors)

    def test_conflicting_duplicate_body_and_matching_title_is_detected(self):
        current = record(28, "3DP-027")
        duplicate = mod.PullRequestRecord(
            29,
            "🔗 3DP#27 → conflicting PR",
            body("3DP-008", 8),
            "open",
        )
        self.assertEqual(mod.task_ids_from_record(duplicate), {"3DP-008", "3DP-027"})
        errors = mod.validate_records(current, [current, duplicate], {})
        self.assertIn("parallel active implementation PRs for 3DP-027: #29", errors)

    def test_conflicting_duplicate_title_and_matching_body_is_detected(self):
        current = record(28, "3DP-027")
        duplicate = mod.PullRequestRecord(
            29,
            "🔗 3DP#8 → conflicting PR",
            body("3DP-027", 27),
            "open",
        )
        self.assertEqual(mod.task_ids_from_record(duplicate), {"3DP-008", "3DP-027"})
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

    def test_canonical_issue_passes(self):
        self.assertEqual(mod.validate_canonical_issue(issue_payload(), 27, "3DP-027"), [])

    def test_closed_canonical_issue_fails(self):
        errors = mod.validate_canonical_issue(issue_payload(state="closed"), 27, "3DP-027")
        self.assertIn("canonical Issue is not open", errors)

    def test_canonical_issue_task_mismatch_fails(self):
        errors = mod.validate_canonical_issue(issue_payload(task_id="3DP-008"), 27, "3DP-027")
        self.assertIn("canonical Issue body lacks matching TASK_ID", errors)

    def test_pull_request_cannot_be_canonical_issue(self):
        payload = issue_payload()
        payload["pull_request"] = {"url": "https://api.github.com/pulls/27"}
        errors = mod.validate_canonical_issue(payload, 27, "3DP-027")
        self.assertIn("canonical Issue points to a Pull Request", errors)


if __name__ == "__main__":
    unittest.main()
