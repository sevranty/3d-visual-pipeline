#!/usr/bin/env python3
"""Validate governed visual assets, rights states, checksums, and history."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

VISUAL_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
ASSET_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
SHA_RE = re.compile(r"^[a-f0-9]{64}$")


def arguments() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=root)
    parser.add_argument("--report", type=Path, default=None)
    return parser.parse_args()


def load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"Missing file: {path}")
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON: {path}: {exc}")
    return None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_head(root: Path) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unknown"


def parse_checksum_file(path: Path, errors: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        errors.append(f"Missing checksum file: {path}")
        return result
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2 or SHA_RE.fullmatch(parts[0]) is None:
            errors.append(f"Invalid checksum line {number}: {line}")
            continue
        asset_path = parts[1].strip()
        if asset_path in result:
            errors.append(f"Duplicate checksum path: {asset_path}")
        result[asset_path] = parts[0]
    return result


def validate_registry(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    checks: list[str] = []
    registry_path = root / "assets/manifest.json"
    registry = load_json(registry_path, errors)
    history = load_json(root / "assets/manifest-history.json", errors)
    checksums = parse_checksum_file(root / "assets/checksums.sha256", errors)

    if not isinstance(registry, dict):
        return checks, errors
    if registry.get("registry_version") != "2.0":
        errors.append("Asset registry version must be 2.0")

    policy = registry.get("policy")
    if not isinstance(policy, dict):
        errors.append("Asset registry policy must be an object")
    else:
        expected_policy = {
            "default_rights_status": "blocked",
            "unregistered_binary_policy": "reject",
            "generated_logo_policy": "reject",
            "exploratory_as_style_source": "reject",
        }
        for key, expected in expected_policy.items():
            if policy.get(key) != expected:
                errors.append(f"Policy {key} must be {expected!r}")
        golden_requirements = policy.get("public_golden_requires")
        if not isinstance(golden_requirements, list) or len(golden_requirements) < 3:
            errors.append("public_golden_requires must define approval, rights, and distribution gates")
    checks.append("asset-policy")

    collections = registry.get("collections")
    collection_map: dict[str, dict[str, Any]] = {}
    if not isinstance(collections, list):
        errors.append("collections must be an array")
    else:
        for collection in collections:
            if not isinstance(collection, dict):
                errors.append("Collection entries must be objects")
                continue
            collection_id = collection.get("collection_id")
            path_value = collection.get("path")
            if not isinstance(collection_id, str) or ASSET_ID_RE.fullmatch(collection_id) is None:
                errors.append(f"Invalid collection_id: {collection_id!r}")
                continue
            if collection_id in collection_map:
                errors.append(f"Duplicate collection_id: {collection_id}")
            collection_map[collection_id] = collection
            if not isinstance(path_value, str) or not path_value.endswith("/"):
                errors.append(f"Collection {collection_id} path must end with /")
            elif not (root / path_value).is_dir():
                errors.append(f"Collection directory does not exist: {path_value}")
        required_collections = {
            "brand-assets", "anchors-modern-flat", "anchors-silver-gold",
            "anchors-obsidian-gold", "anti-patterns", "exploratory",
        }
        missing = sorted(required_collections - set(collection_map))
        if missing:
            errors.append(f"Missing governed collections: {', '.join(missing)}")
    checks.append("asset-collections")

    assets = registry.get("assets")
    asset_paths: set[str] = set()
    asset_ids: set[str] = set()
    if not isinstance(assets, list) or not assets:
        errors.append("assets must be a non-empty array")
    else:
        for entry in assets:
            if not isinstance(entry, dict):
                errors.append("Asset entries must be objects")
                continue
            asset_id = entry.get("asset_id")
            version = entry.get("asset_version")
            path_value = entry.get("path")
            collection_id = entry.get("collection_id")
            if not isinstance(asset_id, str) or ASSET_ID_RE.fullmatch(asset_id) is None:
                errors.append(f"Invalid asset_id: {asset_id!r}")
                continue
            if asset_id in asset_ids:
                errors.append(f"Duplicate asset_id: {asset_id}")
            asset_ids.add(asset_id)
            if not isinstance(version, str) or SEMVER_RE.fullmatch(version) is None:
                errors.append(f"Asset {asset_id} has invalid semantic version")
            if not isinstance(path_value, str) or not path_value.startswith("assets/"):
                errors.append(f"Asset {asset_id} has invalid path")
                continue
            if path_value in asset_paths:
                errors.append(f"Duplicate asset path: {path_value}")
            asset_paths.add(path_value)
            if collection_id not in collection_map:
                errors.append(f"Asset {asset_id} references unknown collection {collection_id!r}")
            file_path = root / path_value
            if not file_path.is_file():
                errors.append(f"Asset file does not exist: {path_value}")
                continue
            declared_sha = entry.get("sha256")
            actual_sha = sha256(file_path)
            if not isinstance(declared_sha, str) or SHA_RE.fullmatch(declared_sha) is None:
                errors.append(f"Asset {asset_id} has invalid sha256")
            elif declared_sha != actual_sha:
                errors.append(f"Asset {asset_id} checksum mismatch")
            if checksums.get(path_value) != actual_sha:
                errors.append(f"Checksum file is missing or stale for {path_value}")

            required_fields = {
                "type", "variant", "lifecycle_status", "approval_status", "rights_status",
                "public_distribution_status", "license_scope", "source", "owner",
                "allowed_backgrounds", "allowed_roles", "prohibited_roles", "source_note",
                "supersedes", "deprecated_at",
            }
            missing_fields = sorted(required_fields - set(entry))
            if missing_fields:
                errors.append(f"Asset {asset_id} missing fields: {', '.join(missing_fields)}")
            if entry.get("lifecycle_status") == "active" and entry.get("deprecated_at") is not None:
                errors.append(f"Active asset {asset_id} cannot have deprecated_at")
            if entry.get("type") == "brand-logo":
                if "generative-reference" not in entry.get("prohibited_roles", []):
                    errors.append(f"Logo {asset_id} must prohibit generative-reference")
                if entry.get("approval_status") != "approved" or entry.get("rights_status") != "cleared":
                    errors.append(f"Canonical logo {asset_id} must be approved and rights-cleared")

            collection = collection_map.get(str(collection_id), {})
            if collection.get("production_eligible") is False and "production" in entry.get("allowed_roles", []):
                errors.append(f"Asset {asset_id} grants production role in a non-production collection")
            if entry.get("public_distribution_status") == "approved":
                if entry.get("approval_status") != "approved" or entry.get("rights_status") != "cleared":
                    errors.append(f"Public asset {asset_id} lacks approval or cleared rights")
    checks.append("asset-entries")

    discovered_visuals = {
        path.relative_to(root).as_posix()
        for path in (root / "assets").rglob("*")
        if path.is_file() and path.suffix.lower() in VISUAL_EXTENSIONS
    }
    unregistered = sorted(discovered_visuals - asset_paths)
    if unregistered:
        errors.append(f"Unregistered visual assets: {', '.join(unregistered)}")
    stale_checksums = sorted(set(checksums) - asset_paths)
    if stale_checksums:
        errors.append(f"Checksum entries without active manifest assets: {', '.join(stale_checksums)}")
    checks.append("asset-inventory")

    base = next((item for item in assets or [] if item.get("asset_id") == "finuslugi-logo-base"), None)
    inverted = next((item for item in assets or [] if item.get("asset_id") == "finuslugi-logo-inverted"), None)
    if not base or set(base.get("allowed_backgrounds", [])) != {"white", "light"}:
        errors.append("Base logo must be restricted to white/light backgrounds")
    if not inverted or set(inverted.get("allowed_backgrounds", [])) != {"red", "dark"}:
        errors.append("Inverted logo must be restricted to red/dark backgrounds")
    checks.append("logo-variants")

    if not isinstance(history, dict) or not isinstance(history.get("events"), list) or not history["events"]:
        errors.append("Asset manifest history must contain at least one event")
    else:
        event_ids: set[str] = set()
        for event in history["events"]:
            event_id = event.get("event_id") if isinstance(event, dict) else None
            if not isinstance(event_id, str) or not event_id:
                errors.append("History event missing event_id")
                continue
            if event_id in event_ids:
                errors.append(f"Duplicate history event_id: {event_id}")
            event_ids.add(event_id)
    checks.append("asset-history")
    return checks, errors


def main() -> int:
    args = arguments()
    root = args.repo_root.resolve()
    checks, errors = validate_registry(root)
    head = git_head(root)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    report = args.report or root / "validation/runtime/asset-report.json"
    if not report.is_absolute():
        report = root / report
    report.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "report_version": "1.0",
        "run_id": f"{now.strftime('%Y%m%dT%H%M%SZ')}-{head[:8] if head != 'unknown' else 'nogit'}-assets",
        "timestamp": now.isoformat().replace("+00:00", "Z"),
        "head_sha": head,
        "status": "pass" if not errors else "fail",
        "passed_checks": checks,
        "errors": errors,
    }
    report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[{'PASS' if not errors else 'FAIL'}] Asset registry validation")
    print(f"HEAD: {head}")
    print(f"Checks: {len(checks)}")
    print(f"Errors: {len(errors)}")
    print(f"Report: {report}")
    for error in errors:
        print(f"ERROR: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
