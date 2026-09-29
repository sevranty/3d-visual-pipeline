#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from validate_pr_governance import (
    as_record,
    parse_superseded_numbers,
    parse_task_metadata,
    validate_canonical_issue,
    validate_records,
    write_report,
)

PAGE_SIZE = 100
MAX_PAGES = 100


def request_json(url: str) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "3dp-woodpecker-governance-validator",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {exc.code} for {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"GitHub API unavailable for {url}: {exc.reason}") from exc


def list_open_pull_requests(base_url: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for page in range(1, MAX_PAGES + 1):
        payload = request_json(
            f"{base_url}/pulls?state=open&per_page={PAGE_SIZE}&page={page}"
        )
        if not isinstance(payload, list):
            raise RuntimeError("GitHub open Pull Request response is not a list")
        records.extend(payload)
        if len(payload) < PAGE_SIZE:
            return records
    raise RuntimeError(f"open Pull Request pagination exceeded {MAX_PAGES} pages")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate 3DP Pull Request governance from Woodpecker"
    )
    parser.add_argument("--repository", required=True)
    parser.add_argument("--pr-number", type=int, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    if args.pr_number < 1:
        raise SystemExit("--pr-number must be positive")
    if args.repository != "sevranty/3d-visual-pipeline":
        raise SystemExit("unexpected repository")

    base_url = f"https://api.github.com/repos/{args.repository}"
    current_payload = request_json(f"{base_url}/pulls/{args.pr_number}")
    if not isinstance(current_payload, dict):
        raise RuntimeError("current Pull Request response is not an object")
    current = as_record(current_payload)

    task_id, issue_number, metadata_errors = parse_task_metadata(
        current.body, current.title
    )
    superseded_numbers, _ = parse_superseded_numbers(current.body)
    open_records = [as_record(item) for item in list_open_pull_requests(base_url)]
    all_records = {record.number: record for record in open_records}
    for number in superseded_numbers:
        if number not in all_records:
            payload = request_json(f"{base_url}/pulls/{number}")
            if not isinstance(payload, dict):
                raise RuntimeError(f"superseded Pull Request #{number} is not an object")
            all_records[number] = as_record(payload)

    errors = list(metadata_errors)
    errors.extend(validate_records(current, open_records, all_records))
    issue_payload = None
    if issue_number is not None:
        issue_payload = request_json(f"{base_url}/issues/{issue_number}")
    if issue_number is not None and task_id is not None:
        errors.extend(validate_canonical_issue(issue_payload, issue_number, task_id))
    elif issue_number is not None:
        errors.append("canonical Issue cannot be validated without TASK_ID")

    write_report(
        args.report,
        current,
        task_id,
        issue_number,
        open_records,
        errors,
    )
    print(f"[{'FAIL' if errors else 'PASS'}] pr-governance-woodpecker")
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
