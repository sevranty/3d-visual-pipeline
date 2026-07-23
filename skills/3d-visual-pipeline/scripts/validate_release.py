#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any, Callable

from validation_lib import Result, parse_args, read_json, repo_root, write_report

VERSION = "1.0.0"
TAG = "v1.0.0"
TAG_REF = f"refs/tags/{TAG}"
REPOSITORY_URL = "https://github.com/sevranty/3d-visual-pipeline"
LEGACY_TAG = "v0.2.0"
LEGACY_TARGET = "3d2cdea9f651f7641ec1f805519a777f013dd6ec"
ALLOWED_STATES = {"candidate", "tagged-validated", "published"}
HEX_SHA = re.compile(r"^[0-9a-f]{40}$")
UTC_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)$")
GitReader = Callable[[Path, tuple[str, ...]], tuple[str | None, str | None]]


def has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def read_git_value(root: Path, args: tuple[str, ...]) -> tuple[str | None, str | None]:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}"
        return None, detail
    return completed.stdout.strip(), None


def validate_hosted_ci(hosted: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(hosted, dict):
        return ["hosted CI evidence must be an object"]

    status = hosted.get("status")
    run_url = hosted.get("run_url")
    commit_sha = hosted.get("commit_sha")
    if status not in {"not_run", "passed", "failed"}:
        errors.append("hosted CI status invalid")
        return errors
    if status == "not_run":
        if run_url is not None or commit_sha is not None:
            errors.append("hosted CI not_run contains run evidence")
    else:
        expected_prefix = f"{REPOSITORY_URL}/actions/runs/"
        if not isinstance(run_url, str) or not run_url.startswith(expected_prefix):
            errors.append("hosted CI result lacks canonical run URL")
        if not HEX_SHA.fullmatch(str(commit_sha or "")):
            errors.append("hosted CI result lacks exact commit")
    return errors


def validate_tagged_evidence(tagged: Any, tag_target: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(tagged, dict):
        return ["tagged validation evidence missing"]
    if tagged.get("status") != "pass":
        errors.append("tagged validation is not pass")
    if tagged.get("tag") != TAG:
        errors.append("tagged validation uses wrong tag")
    if tagged.get("tag_object_type") != "tag":
        errors.append("tagged validation lacks annotated tag object")
    if not HEX_SHA.fullmatch(str(tagged.get("tag_object_sha") or "")):
        errors.append("tagged validation lacks tag object SHA")
    if tagged.get("checkout_sha") != tag_target:
        errors.append("tagged validation is not bound to tag target")
    if tagged.get("peeled_commit") != tag_target:
        errors.append("tagged validation peeled commit differs from tag target")
    if not has_text(tagged.get("command")):
        errors.append("tagged validation command missing")
    if not has_text(tagged.get("report")):
        errors.append("tagged validation report missing")
    if not UTC_TIMESTAMP.fullmatch(str(tagged.get("validated_at") or "")):
        errors.append("tagged validation timestamp invalid")
    return errors


def validate_git_tag(
    root: Path,
    manifest: dict[str, Any],
    git_reader: GitReader = read_git_value,
    require_tag: bool = False,
) -> list[str]:
    state = manifest.get("status")
    if state not in {"tagged-validated", "published"}:
        return []

    errors: list[str] = []
    tagged = manifest.get("tagged_validation")
    tag_target = manifest.get("tag_target")
    recorded_object_sha = tagged.get("tag_object_sha") if isinstance(tagged, dict) else None
    recorded_peeled_commit = tagged.get("peeled_commit") if isinstance(tagged, dict) else None

    actual_object_sha, detail = git_reader(root, ("show-ref", "--verify", "--hash", TAG_REF))
    if detail is not None:
        if require_tag:
            return [f"Git release tag {TAG} is required but unavailable: {detail}"]
        return []

    actual_type, detail = git_reader(root, ("cat-file", "-t", TAG_REF))
    if detail is not None:
        errors.append(f"Git release tag type could not be resolved: {detail}")
    elif actual_type != "tag":
        errors.append(f"Git release tag {TAG} is not annotated")

    if actual_object_sha != recorded_object_sha:
        errors.append("Git tag object SHA differs from recorded evidence")

    actual_peeled_commit, detail = git_reader(root, ("rev-parse", f"{TAG_REF}^{{}}"))
    if detail is not None:
        errors.append(f"Git peeled release commit could not be resolved: {detail}")
    else:
        if actual_peeled_commit != tag_target:
            errors.append("Git peeled release commit differs from tag target")
        if actual_peeled_commit != recorded_peeled_commit:
            errors.append("Git peeled release commit differs from recorded evidence")
    return errors


def validate_release_evidence(release: Any, release_url: Any) -> list[str]:
    errors: list[str] = []
    expected_url = f"{REPOSITORY_URL}/releases/tag/{TAG}"
    if release_url != expected_url:
        errors.append("published state lacks canonical release URL")
    if not isinstance(release, dict):
        return errors + ["published state lacks GitHub Release evidence"]
    if release.get("url") != release_url:
        errors.append("GitHub Release evidence URL differs from release_url")
    if release.get("tag") != TAG:
        errors.append("GitHub Release evidence uses wrong tag")
    if release.get("draft") is not False:
        errors.append("GitHub Release must be non-draft")
    if release.get("prerelease") is not False:
        errors.append("GitHub Release must be non-prerelease")
    if not UTC_TIMESTAMP.fullmatch(str(release.get("published_at") or "")):
        errors.append("GitHub Release publication timestamp invalid")
    return errors


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    state = manifest.get("status")

    if manifest.get("version") != VERSION or manifest.get("intended_tag") != TAG:
        errors.append("release manifest not aligned")
    if state not in ALLOWED_STATES:
        errors.append("release status invalid")

    errors.extend(validate_hosted_ci(manifest.get("hosted_ci")))

    tag_target = manifest.get("tag_target")
    release_url = manifest.get("release_url")
    tagged = manifest.get("tagged_validation")
    release = manifest.get("github_release")

    if state == "candidate":
        if tag_target is not None or release_url is not None or tagged is not None or release is not None:
            errors.append("candidate contains publication evidence")

    if state in {"tagged-validated", "published"}:
        if not HEX_SHA.fullmatch(str(tag_target or "")):
            errors.append("tag target missing or invalid")
        errors.extend(validate_tagged_evidence(tagged, tag_target))

    if state == "tagged-validated":
        if release_url is not None or release is not None:
            errors.append("tagged-validated state contains release evidence")
    if state == "published":
        errors.extend(validate_release_evidence(release, release_url))

    legacy = manifest.get("legacy_release", {})
    if legacy.get("tag") != LEGACY_TAG or legacy.get("target") != LEGACY_TARGET:
        errors.append("legacy release boundary changed")
    if legacy.get("immutable") is not True:
        errors.append("legacy release must remain immutable")

    return errors


def main() -> int:
    args = parse_args(__doc__ or "release validator")
    root = repo_root()
    result = Result("release")

    plugin = read_json(root / ".codex-plugin/plugin.json")
    manifest = read_json(root / f"release/{VERSION}/validation-manifest.json")

    if plugin.get("version") != VERSION:
        result.error("plugin version not aligned")
    for error in validate_manifest(manifest):
        result.error(error)
    for error in validate_git_tag(
        root,
        manifest,
        require_tag=os.environ.get("RELEASE_REQUIRE_GIT_TAG") == "1",
    ):
        result.error(error)

    for path in [
        f"release/{VERSION}/RELEASE_NOTES.md",
        "CHANGELOG.md",
        "README.md",
        "RELEASE_CHECKLIST.md",
    ]:
        text = (root / path).read_text(encoding="utf-8")
        if VERSION not in text:
            result.error(f"version absent from {path}")

    result.check("version-and-publication-contract")
    return write_report(root, args, result)


if __name__ == "__main__":
    raise SystemExit(main())
