#!/usr/bin/env python3
"""Validate runtime capability profiles, routing cases, and execution provenance."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


CAPABILITIES = {
    "generate",
    "reference-conditioned",
    "edit",
    "mask-edit",
    "multi-reference",
    "identity-preservation",
    "transparent-output",
    "upscale",
    "exact-dimensions",
    "deliver",
    "seed-control",
}
STATES = {"supported", "unsupported", "unknown"}
MODES = {"generate", "edit", "reference-conditioned", "mask-edit", "upscale"}


def parse_args() -> argparse.Namespace:
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


def validate_profile(profile: Any, errors: list[str]) -> None:
    if not isinstance(profile, dict):
        errors.append("Runtime profile must be an object")
        return
    required = {
        "profile_version",
        "profile_id",
        "adapter_id",
        "tool_family",
        "model_id",
        "observed_at",
        "capabilities",
        "limits",
        "limitations",
        "evidence",
    }
    missing = sorted(required - set(profile))
    if missing:
        errors.append(f"Runtime profile missing fields: {', '.join(missing)}")
    if profile.get("profile_version") != "1.0":
        errors.append("Runtime profile version must be 1.0")
    for key in ("profile_id", "adapter_id"):
        value = profile.get(key)
        if not isinstance(value, str) or re.fullmatch(r"[a-z0-9][a-z0-9-]*@[0-9]+", value) is None:
            errors.append(f"Invalid {key}: {value!r}")
    capabilities = profile.get("capabilities")
    if not isinstance(capabilities, dict):
        errors.append("capabilities must be an object")
    else:
        if set(capabilities) != CAPABILITIES:
            errors.append("capabilities must contain the exact canonical capability set")
        for name, state in capabilities.items():
            if state not in STATES:
                errors.append(f"Invalid capability state {name}={state!r}")
    limits = profile.get("limits")
    if not isinstance(limits, dict):
        errors.append("limits must be an object")
    else:
        for key in ("max_references", "max_width_px", "max_height_px"):
            value = limits.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                errors.append(f"Invalid runtime limit {key}={value!r}")
    if not isinstance(profile.get("limitations"), list):
        errors.append("limitations must be an array")
    evidence = profile.get("evidence")
    if not isinstance(evidence, dict) or not evidence.get("source") or not evidence.get("verified_by"):
        errors.append("evidence.source and evidence.verified_by are required")


def validate_runtime_cases(data: Any, errors: list[str]) -> None:
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        errors.append("runtime-cases.json must contain cases array")
        return
    cases = data["cases"]
    ids: set[str] = set()
    names: set[str] = set()
    profiles: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            errors.append("Runtime case must be an object")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or re.fullmatch(r"RT-[0-9]{3}", case_id) is None:
            errors.append(f"Invalid runtime case ID: {case_id!r}")
            continue
        if case_id in ids:
            errors.append(f"Duplicate runtime case ID: {case_id}")
        ids.add(case_id)
        name = case.get("name")
        if isinstance(name, str):
            names.add(name)
        if case.get("kind") not in {"positive", "negative"}:
            errors.append(f"{case_id}: invalid kind")
        requested = case.get("requested_mode")
        if requested not in MODES:
            errors.append(f"{case_id}: invalid requested_mode {requested!r}")
        required = case.get("required_capabilities")
        if not isinstance(required, list) or not required or any(item not in CAPABILITIES for item in required):
            errors.append(f"{case_id}: invalid required_capabilities")
        expected = case.get("expected")
        if not isinstance(expected, list) or not expected or not all(isinstance(item, str) and item for item in expected):
            errors.append(f"{case_id}: expected must be a non-empty string array")
        profile = case.get("profile")
        if isinstance(profile, str):
            profiles.add(profile)
    for profile in {"chatgpt-image-generation@1", "nano-banana-style@1"}:
        if profile not in profiles:
            errors.append(f"Missing runtime case for {profile}")
    for required_name in {
        "Missing mask edit stops local correction",
        "Delivery capability regression",
        "Hidden route degradation rejected",
    }:
        if required_name not in names:
            errors.append(f"Missing negative runtime case: {required_name}")


def validate_output_manifest(manifest: Any, errors: list[str]) -> None:
    if not isinstance(manifest, dict):
        errors.append("Output manifest must be an object")
        return
    if manifest.get("manifest_version") != "1.1":
        errors.append("Output manifest version must be 1.1")
    execution = manifest.get("execution")
    if not isinstance(execution, dict):
        errors.append("Output manifest execution must be an object")
        return
    required = {
        "runtime_profile_id",
        "adapter_id",
        "tool",
        "model",
        "requested_mode",
        "selected_mode",
        "required_capabilities",
        "iterations",
        "fallback",
        "limitations",
    }
    missing = sorted(required - set(execution))
    if missing:
        errors.append(f"Output manifest execution missing: {', '.join(missing)}")
    requested = execution.get("requested_mode")
    selected = execution.get("selected_mode")
    fallback = execution.get("fallback")
    if requested != selected:
        if not isinstance(fallback, dict) or fallback.get("applied") is not True:
            errors.append("Requested/selected mode mismatch requires fallback.applied=true")
        else:
            for key in ("from_mode", "to_mode", "decision", "reason", "approved_by_user", "risks"):
                if key not in fallback:
                    errors.append(f"Applied fallback missing {key}")
    elif isinstance(fallback, dict) and fallback.get("applied") is not False:
        errors.append("Matching requested/selected modes require fallback.applied=false")
    required_capabilities = execution.get("required_capabilities")
    if not isinstance(required_capabilities, list) or "deliver" not in required_capabilities:
        errors.append("Every completed output manifest must require deliver capability")
    delivery = manifest.get("delivery")
    if not isinstance(delivery, dict) or delivery.get("visible_to_user") is not True or delivery.get("response_non_empty") is not True:
        errors.append("Completed output manifest requires visible, non-empty delivery")


def main() -> int:
    args = parse_args()
    root = args.repo_root.resolve()
    base = root / "skills/finuslugi-3d-visual-pipeline"
    errors: list[str] = []
    checks: list[str] = []

    required_paths = [
        base / "references/runtime-capabilities.md",
        base / "references/runtime-routing.md",
        base / "references/runtime-fallbacks.md",
        base / "assets/schemas/runtime-capabilities.schema.json",
        base / "evals/runtime-cases.json",
        base / "evals/fixtures/valid/runtime-capabilities.json",
        base / "evals/fixtures/invalid/runtime-capabilities-delivery-missing.json",
        base / "evals/fixtures/valid/output-manifest.json",
    ]
    for path in required_paths:
        if not path.exists():
            errors.append(f"Missing runtime contract file: {path.relative_to(root)}")
    checks.append("runtime-required-paths")

    schema = load_json(base / "assets/schemas/runtime-capabilities.schema.json", errors)
    if not isinstance(schema, dict) or schema.get("title") != "Image Runtime Capability Profile":
        errors.append("Runtime capability schema is missing or has an unexpected title")
    checks.append("runtime-schema")

    valid_profile = load_json(base / "evals/fixtures/valid/runtime-capabilities.json", errors)
    validate_profile(valid_profile, errors)
    checks.append("runtime-valid-profile")

    invalid_profile = load_json(base / "evals/fixtures/invalid/runtime-capabilities-delivery-missing.json", errors)
    invalid_errors: list[str] = []
    validate_profile(invalid_profile, invalid_errors)
    if not invalid_errors:
        errors.append("Invalid runtime capability fixture unexpectedly passed")
    checks.append("runtime-invalid-profile")

    cases = load_json(base / "evals/runtime-cases.json", errors)
    validate_runtime_cases(cases, errors)
    checks.append("runtime-cases")

    output_manifest = load_json(base / "evals/fixtures/valid/output-manifest.json", errors)
    validate_output_manifest(output_manifest, errors)
    checks.append("runtime-output-manifest")

    head = git_head(root)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    payload = {
        "report_version": "1.0",
        "run_id": f"{now.strftime('%Y%m%dT%H%M%SZ')}-{head[:8] if head != 'unknown' else 'nogit'}-runtime",
        "timestamp": now.isoformat().replace("+00:00", "Z"),
        "head_sha": head,
        "status": "pass" if not errors else "fail",
        "passed_checks": checks,
        "errors": errors,
    }
    report = args.report or root / "validation" / "runtime" / "runtime-report.json"
    if not report.is_absolute():
        report = root / report
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[{'PASS' if not errors else 'FAIL'}] Runtime contract validation")
    print(f"HEAD: {head}")
    print(f"Checks: {len(checks)}")
    print(f"Errors: {len(errors)}")
    print(f"Report: {report}")
    for error in errors:
        print(f"ERROR: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
