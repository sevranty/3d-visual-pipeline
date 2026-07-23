#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TASK_ID_RE = re.compile(r"(?m)^- TASK_ID: (3DP-(\d{3}))\s*$")
ISSUE_RE = re.compile(r"(?m)^- Canonical Issue: #(\d+)\s*$")
ISSUE_BODY_TASK_RE = re.compile(r"(?m)^TASK_ID:\s*(3DP-(\d{3}))\s*$")
SUPERSEDES_RE = re.compile(r"(?m)^- Supersedes: (.+?)\s*$")
SUPERSEDED_PR_RE = re.compile(r"PR #(\d+) \(closed\)")
TITLE_TASK_RE = re.compile(r"\b3DP#(\d+)\b")
PAGE_SIZE = 100
MAX_PAGES = 100


@dataclass(frozen=True)
class PullRequestRecord:
    number: int
    title: str
    body: str
    state: str


def canonical_task_id(number: int) -> str:
    return f"3DP-{number:03d}"


def parse_task_metadata(body: str, title: str = "") -> tuple[str | None, int | None, list[str]]:
    errors: list[str] = []
    task_match = TASK_ID_RE.search(body)
    issue_match = ISSUE_RE.search(body)
    title_match = TITLE_TASK_RE.search(title)

    task_id = task_match.group(1) if task_match else None
    task_number = int(task_match.group(2)) if task_match else None
    issue_number = int(issue_match.group(1)) if issue_match else None
    title_number = int(title_match.group(1)) if title_match else None

    if task_id is None:
        errors.append("PR body lacks exact TASK_ID metadata")
    if issue_number is None:
        errors.append("PR body lacks canonical Issue metadata")
    if title_number is None:
        errors.append("PR title lacks 3DP#N task number")
    if task_number is not None and issue_number is not None and task_number != issue_number:
        errors.append("TASK_ID and canonical Issue number differ")
    if title_number is not None and task_number is not None and title_number != task_number:
        errors.append("PR title task number differs from TASK_ID")
    if title_number is not None and issue_number is not None and title_number != issue_number:
        errors.append("PR title task number differs from canonical Issue")
    return task_id, issue_number, errors


def parse_superseded_numbers(body: str) -> tuple[list[int], list[str]]:
    match = SUPERSEDES_RE.search(body)
    if not match:
        return [], ["PR body lacks Supersedes metadata"]
    value = match.group(1).strip()
    if value == "none":
        return [], []
    numbers = [int(number) for number in SUPERSEDED_PR_RE.findall(value)]
    if not numbers:
        return [], ["Supersedes must be none or use PR #N (closed)"]
    reconstructed = ", ".join(f"PR #{number} (closed)" for number in numbers)
    if reconstructed != value:
        return numbers, ["Supersedes metadata is not canonical"]
    if len(numbers) != len(set(numbers)):
        return numbers, ["Supersedes metadata contains duplicate PR numbers"]
    return numbers, []


def task_ids_from_record(record: PullRequestRecord) -> set[str]:
    task_ids: set[str] = set()
    task_match = TASK_ID_RE.search(record.body)
    if task_match:
        task_ids.add(task_match.group(1))
    title_match = TITLE_TASK_RE.search(record.title)
    if title_match:
        task_ids.add(canonical_task_id(int(title_match.group(1))))
    return task_ids


def task_id_from_record(record: PullRequestRecord) -> str | None:
    task_ids = task_ids_from_record(record)
    return next(iter(task_ids)) if len(task_ids) == 1 else None


def validate_canonical_issue(payload: Any, expected_number: int, expected_task_id: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["canonical Issue was not resolved"]
    if int(payload.get("number", -1)) != expected_number:
        errors.append("canonical Issue number differs from PR metadata")
    if "pull_request" in payload:
        errors.append("canonical Issue points to a Pull Request")
    if payload.get("state") != "open":
        errors.append("canonical Issue is not open")

    title = str(payload.get("title") or "")
    title_match = TITLE_TASK_RE.search(title)
    if not title_match or int(title_match.group(1)) != expected_number:
        errors.append("canonical Issue title lacks matching 3DP#N")

    body = str(payload.get("body") or "")
    body_match = ISSUE_BODY_TASK_RE.search(body)
    if not body_match or body_match.group(1) != expected_task_id:
        errors.append("canonical Issue body lacks matching TASK_ID")
    return errors


def validate_records(
    current: PullRequestRecord,
    open_records: list[PullRequestRecord],
    superseded_records: dict[int, PullRequestRecord],
) -> list[str]:
    task_id, _, errors = parse_task_metadata(current.body, current.title)
    superseded_numbers, supersedes_errors = parse_superseded_numbers(current.body)
    errors.extend(supersedes_errors)

    if task_id is not None:
        duplicates = sorted(
            record.number
            for record in open_records
            if record.number != current.number and task_id in task_ids_from_record(record)
        )
        if duplicates:
            joined = ", ".join(f"#{number}" for number in duplicates)
            errors.append(f"parallel active implementation PRs for {task_id}: {joined}")

    for number in superseded_numbers:
        if number == current.number:
            errors.append("PR cannot supersede itself")
            continue
        record = superseded_records.get(number)
        if record is None:
            errors.append(f"superseded PR #{number} was not resolved")
        elif record.state != "closed":
            errors.append(f"superseded PR #{number} is not closed")
    return errors


def request_json(url: str, token: str) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "3dp-governance-validator",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {exc.code} for {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"GitHub API unavailable for {url}: {exc.reason}") from exc


def list_open_pull_requests(base_url: str, token: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for page in range(1, MAX_PAGES + 1):
        payload = request_json(
            f"{base_url}/pulls?state=open&per_page={PAGE_SIZE}&page={page}",
            token,
        )
        if not isinstance(payload, list):
            raise RuntimeError("GitHub open Pull Request response is not a list")
        records.extend(payload)
        if len(payload) < PAGE_SIZE:
            return records
    raise RuntimeError(f"open Pull Request pagination exceeded {MAX_PAGES} pages")


def as_record(payload: dict[str, Any]) -> PullRequestRecord:
    return PullRequestRecord(
        number=int(payload["number"]),
        title=str(payload.get("title") or ""),
        body=str(payload.get("body") or ""),
        state=str(payload.get("state") or ""),
    )


def load_snapshot(
    path: Path,
) -> tuple[list[PullRequestRecord], dict[int, PullRequestRecord], dict[str, Any] | None]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    open_records = [as_record(item) for item in payload.get("open_pull_requests", [])]
    all_records = {record.number: record for record in open_records}
    for item in payload.get("resolved_pull_requests", []):
        record = as_record(item)
        all_records[record.number] = record
    issue_payload = payload.get("canonical_issue")
    return open_records, all_records, issue_payload if isinstance(issue_payload, dict) else None


def write_report(
    path: Path,
    current: PullRequestRecord,
    task_id: str | None,
    issue_number: int | None,
    open_records: list[PullRequestRecord],
    errors: list[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "validator": "pr-governance",
                "status": "fail" if errors else "pass",
                "current_pr": current.number,
                "task_id": task_id,
                "canonical_issue": issue_number,
                "open_pr_count": len(open_records),
                "errors": errors,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate one active implementation PR per 3DP TASK_ID")
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path)
    args = parser.parse_args()

    event = json.loads(args.event.read_text(encoding="utf-8"))
    pull_request = event.get("pull_request")
    if not isinstance(pull_request, dict):
        print("[SKIP] pr-governance: event has no pull_request")
        return 0

    current = as_record(pull_request)
    task_id, issue_number, _ = parse_task_metadata(current.body, current.title)
    superseded_numbers, _ = parse_superseded_numbers(current.body)

    if args.snapshot:
        open_records, all_records, issue_payload = load_snapshot(args.snapshot)
    else:
        token = os.environ.get("GITHUB_TOKEN", "")
        if not token:
            print("[FAIL] pr-governance: GITHUB_TOKEN is required", file=sys.stderr)
            return 1
        base_url = f"https://api.github.com/repos/{args.repository}"
        open_records = [as_record(item) for item in list_open_pull_requests(base_url, token)]
        all_records = {record.number: record for record in open_records}
        for number in superseded_numbers:
            if number not in all_records:
                all_records[number] = as_record(request_json(f"{base_url}/pulls/{number}", token))
        issue_payload = request_json(f"{base_url}/issues/{issue_number}", token) if issue_number else None

    errors = validate_records(current, open_records, all_records)
    if issue_number is not None and task_id is not None:
        errors.extend(validate_canonical_issue(issue_payload, issue_number, task_id))
    elif issue_number is not None:
        errors.append("canonical Issue cannot be validated without TASK_ID")

    write_report(args.report, current, task_id, issue_number, open_records, errors)
    print(f"[{'FAIL' if errors else 'PASS'}] pr-governance")
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
